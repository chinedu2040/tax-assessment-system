import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from config import get_settings
from models import Transaction, TaxComputation, TaxReport, AuditLog, User, Document
from modules.tax_engine.tax_computation import compute_tax
from modules.reporting.report_generator import generate_report
from schemas.tax_report import ConfirmRequest, ConfirmResponse, TaxComputation as TaxComputationSchema, BandBreakdown

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.post(
    "/confirm",
    response_model=ConfirmResponse,
    summary="Confirm transactions and generate tax report",
    description="Apply user corrections, run tax computation, generate PDF report, and securely delete the uploaded source file.",
    tags=["Tax"],
    status_code=200,
)
def confirm_and_compute(payload: ConfirmRequest, db: Session = Depends(get_db)):
    for correction in payload.transactions:
        txn = db.query(Transaction).filter(
            Transaction.transaction_id == correction.transaction_id
        ).first()
        if txn and txn.category != correction.category:
            txn.category = correction.category
            if correction.sub_category:
                txn.sub_category = correction.sub_category
            txn.user_corrected = True
            txn.classification_method = "user_correction"
            db.add(AuditLog(
                user_id=payload.user_id,
                action="user_correction",
                details={
                    "transaction_id": correction.transaction_id,
                    "new_category": correction.category,
                },
            ))

    db.flush()

    all_txns = db.query(Transaction).filter(
        Transaction.document_id == payload.document_id
    ).all()

    txn_dicts = [
        {
            "transaction_id": str(t.transaction_id),
            "amount": float(t.amount) if t.amount else 0,
            "direction": t.direction,
            "category": t.category,
            "description": t.description,
        }
        for t in all_txns
    ]

    result = compute_tax(txn_dicts, payload.user_id, payload.tax_year, db)

    db.add(AuditLog(
        user_id=payload.user_id,
        action="tax_computed",
        details={"tax_year": payload.tax_year, "tax_liability": result["tax_liability"]},
    ))

    comp = TaxComputation(
        user_id=payload.user_id,
        tax_year=payload.tax_year,
        gross_income=result["gross_income"],
        cra_fixed=result["cra_fixed"],
        cra_percentage=result["cra_percentage"],
        total_cra=result["total_cra"],
        pension_relief=result["pension_relief"],
        nhf_relief=result["nhf_relief"],
        nhis_relief=result["nhis_relief"],
        other_deductions=result["other_deductions"],
        taxable_income=result["taxable_income"],
        tax_liability=result["tax_liability"],
        effective_rate=result["effective_rate"],
        band_breakdown=result["band_breakdown"],
    )
    db.add(comp)
    db.flush()

    user = db.query(User).filter(User.user_id == payload.user_id).first()
    user_info = {
        "full_name": user.full_name if user else "Unknown",
        "tin": user.tin if user else "N/A",
    }

    report_dir = Path(settings.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_filename = f"tax_report_{comp.computation_id}.pdf"
    report_path = str(report_dir / report_filename)

    try:
        generate_report(result, txn_dicts, user_info, report_path)
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    db.add(AuditLog(
        user_id=payload.user_id,
        action="report_generated",
        details={"report_path": report_path, "computation_id": str(comp.computation_id)},
    ))

    tax_report = TaxReport(
        user_id=payload.user_id,
        computation_id=comp.computation_id,
        report_path=report_path,
    )
    db.add(tax_report)
    db.flush()

    doc = db.query(Document).filter(Document.document_id == payload.document_id).first()
    if doc and doc.upload_path:
        upload_path = Path(doc.upload_path)
        try:
            upload_path.unlink(missing_ok=True)
            doc.status = "deleted"
            db.add(AuditLog(
                user_id=payload.user_id,
                action="file_deleted",
                details={"document_id": payload.document_id, "file_path": str(upload_path)},
            ))
        except Exception as e:
            # Log deletion failure but don't abort — report is already generated
            logger.error(f"Failed to delete source file {upload_path}: {e}")
            db.add(AuditLog(
                user_id=payload.user_id,
                action="file_delete_failed",
                details={"error": str(e), "file_path": str(upload_path)},
            ))

    db.commit()
    db.refresh(tax_report)

    comp_schema = TaxComputationSchema(
        user_id=payload.user_id,
        tax_year=payload.tax_year,
        gross_income=result["gross_income"],
        cra_fixed=result["cra_fixed"],
        cra_percentage=result["cra_percentage"],
        total_cra=result["total_cra"],
        pension_relief=result["pension_relief"],
        nhf_relief=result["nhf_relief"],
        nhis_relief=result["nhis_relief"],
        other_deductions=result["other_deductions"],
        taxable_income=result["taxable_income"],
        tax_liability=result["tax_liability"],
        effective_rate=result["effective_rate"],
        band_breakdown=[BandBreakdown(**b) for b in result["band_breakdown"]],
    )

    return ConfirmResponse(
        report_id=str(tax_report.report_id),
        computation=comp_schema,
        download_url=f"/api/report/{tax_report.report_id}",
    )
