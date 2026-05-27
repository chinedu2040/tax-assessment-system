from typing import Optional, List, Any, Dict
from pydantic import BaseModel

from schemas.transaction import TransactionUpdate


class BandBreakdown(BaseModel):
    rate: float
    taxable_amount: float
    tax_amount: float


class TaxComputation(BaseModel):
    user_id: str
    tax_year: int
    gross_income: float
    cra_fixed: float
    cra_percentage: float
    total_cra: float
    pension_relief: float
    nhf_relief: float
    nhis_relief: float
    other_deductions: float
    taxable_income: float
    tax_liability: float
    effective_rate: float
    band_breakdown: List[BandBreakdown]


class ConfirmRequest(BaseModel):
    document_id: str
    transactions: List[TransactionUpdate]
    user_id: str
    tax_year: int


class ConfirmResponse(BaseModel):
    report_id: str
    computation: TaxComputation
    download_url: str


class UserCreate(BaseModel):
    email: str
    full_name: Optional[str] = None
    tin: Optional[str] = None


class UserOut(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str] = None
    tin: Optional[str] = None
