import os
import uuid
import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from config import get_settings
from models import Document, Transaction, AuditLog, User
from modules.ingestion.document_parser import parse_document
from modules.classification.hybrid_engine import classify_transaction
from schemas.transaction import UploadResponse, UploadSummary, TransactionOut

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".pdf"}
MAX_SIZE_BYTES = settings.max_upload_size_mb * 1024 * 1024


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload a bank statement",
    description="Upload a CSV, Excel, or PDF bank statement. Transactions are parsed, normalised, and classified automatically.",
    tags=["Documents"],
    status_code=200,
)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    bank_name: str = Form(default=""),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE_BYTES:
        raise HTTPException(413, f"File exceeds {settings.max_upload_size_mb}MB limit")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_filename = f"{uuid.uuid4()}{ext}"
    upload_path = upload_dir / saved_filename
    upload_path.write_bytes(file_bytes)

    doc = Document(
        user_id=user_id,
        file_name=file.filename,
        file_type=ext.lstrip("."),
        upload_path=str(upload_path),
        status="uploaded",
        bank_name=bank_name or None,
    )
    db.add(doc)
    db.flush()

    db.add(AuditLog(
        user_id=user_id,
        action="file_uploaded",
        details={"document_id": doc.document_id, "file_name": file.filename, "size_bytes": len(file_bytes)},
    ))

    try:
        raw_transactions = parse_document(file_bytes, file.filename)
    except Exception as e:
        logger.error(f"Parse error: {e}")
        raise HTTPException(422, f"Could not parse file: {e}")

    # Cap at 2000 transactions to prevent timeout; prioritise by date desc
    MAX_TXN = 2000
    if len(raw_transactions) > MAX_TXN:
        logger.warning(f"Capping {len(raw_transactions)} → {MAX_TXN} transactions")
        raw_transactions = raw_transactions[:MAX_TXN]

    saved_txns = []
    txn_objects = []
    for raw in raw_transactions:
        result = classify_transaction(raw.get("description", ""))
        txn = Transaction(
            document_id=doc.document_id,
            user_id=user_id,
            date=raw.get("date") or None,
            description=raw.get("description"),
            amount=raw.get("amount"),
            direction=raw.get("direction"),
            category=result["category"],
            sub_category=result["sub_category"],
            classification_method=result["classification_method"],
            confidence_score=result["confidence_score"],
            user_corrected=False,
        )
        txn_objects.append(txn)

    # Bulk insert for speed (handles hundreds/thousands without timeout)
    db.bulk_save_objects(txn_objects, return_defaults=True)

    db.add(AuditLog(
        user_id=user_id,
        action="classified",
        details={"document_id": doc.document_id, "transaction_count": len(txn_objects)},
    ))

    doc.status = "classified"
    db.commit()

    # Re-query transactions for response (bulk_save_objects doesn't auto-refresh)
    saved_txns = db.query(Transaction).filter(
        Transaction.document_id == doc.document_id
    ).all()

    def _txn_out(t: Transaction) -> TransactionOut:
        return TransactionOut(
            transaction_id=str(t.transaction_id),
            document_id=str(t.document_id),
            user_id=str(t.user_id) if t.user_id else None,
            date=str(t.date) if t.date else None,
            description=t.description,
            amount=float(t.amount) if t.amount is not None else None,
            direction=t.direction,
            category=t.category,
            sub_category=t.sub_category,
            classification_method=t.classification_method,
            confidence_score=float(t.confidence_score) if t.confidence_score is not None else None,
            user_corrected=t.user_corrected,
        )

    txn_outs = [_txn_out(t) for t in saved_txns]

    summary = UploadSummary(
        total=len(txn_outs),
        taxable_income_count=sum(1 for t in txn_outs if t.category == "taxable_income"),
        deductible_count=sum(1 for t in txn_outs if t.category == "deductible_expense"),
        non_taxable_count=sum(1 for t in txn_outs if t.category == "non_taxable"),
        needs_review_count=sum(1 for t in txn_outs if t.category == "needs_review"),
    )

    return UploadResponse(
        document_id=str(doc.document_id),
        transactions=txn_outs,
        summary=summary,
    )
