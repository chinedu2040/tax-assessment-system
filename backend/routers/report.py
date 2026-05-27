from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from models import TaxReport, Transaction, User
from schemas.tax_report import UserCreate, UserOut
from schemas.transaction import TransactionOut

router = APIRouter()


@router.get(
    "/report/{report_id}",
    summary="Download tax report PDF",
    description="Download the generated PDF tax assessment report.",
    tags=["Reports"],
)
def download_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(TaxReport).filter(TaxReport.report_id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    path = Path(report.report_path)
    if not path.exists():
        raise HTTPException(404, "Report file not found on disk")
    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=path.name,
    )


@router.get(
    "/transactions/{document_id}",
    response_model=list[TransactionOut],
    summary="Get transactions for a document",
    description="Retrieve all classified transactions for a given document ID.",
    tags=["Documents"],
)
def get_transactions(document_id: str, db: Session = Depends(get_db)):
    txns = db.query(Transaction).filter(Transaction.document_id == document_id).all()
    return [
        TransactionOut(
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
        for t in txns
    ]


@router.post(
    "/users",
    response_model=UserOut,
    summary="Create a user",
    description="Register a new user (freelancer) in the system.",
    tags=["Users"],
    status_code=201,
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        return UserOut(
            user_id=str(existing.user_id),
            email=existing.email,
            full_name=existing.full_name,
            tin=existing.tin,
        )
    user = User(email=payload.email, full_name=payload.full_name, tin=payload.tin)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(
        user_id=str(user.user_id),
        email=user.email,
        full_name=user.full_name,
        tin=user.tin,
    )
