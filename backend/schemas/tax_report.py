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
    development_levy: float = 0.0
    total_tax_payable: float = 0.0
    effective_rate: float
    band_breakdown: List[BandBreakdown]
    state_of_residence: Optional[str] = None
    state_irs: Optional[str] = None


class ConfirmRequest(BaseModel):
    document_id: str
    transactions: List[TransactionUpdate]
    user_id: str
    tax_year: int
    state_of_residence: Optional[str] = None
    bank_name: Optional[str] = None


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
