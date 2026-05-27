from typing import Optional, List
from datetime import date
from pydantic import BaseModel


class TransactionBase(BaseModel):
    date: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    direction: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    classification_method: Optional[str] = None
    confidence_score: Optional[float] = None
    user_corrected: Optional[bool] = False


class TransactionOut(TransactionBase):
    transaction_id: str
    document_id: Optional[str] = None
    user_id: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionUpdate(BaseModel):
    transaction_id: str
    category: str
    sub_category: Optional[str] = None
    user_corrected: bool = True


class UploadSummary(BaseModel):
    total: int
    taxable_income_count: int
    deductible_count: int
    non_taxable_count: int
    needs_review_count: int


class UploadResponse(BaseModel):
    document_id: str
    transactions: List[TransactionOut]
    summary: UploadSummary
