from typing import Dict
from sqlalchemy.orm import Session
from models import StatutoryParameter


def load_parameters(db: Session) -> Dict[str, float]:
    rows = db.query(StatutoryParameter).all()
    return {row.param_key: float(row.param_value) for row in rows}


# Nigeria Tax Act 2025 - effective 1 January 2026
# Source: PwC Worldwide Tax Summaries, reviewed 29 May 2026
DEFAULT_PARAMS = {
    # Rent Relief (replaces the abolished Consolidated Relief Allowance)
    # Relief = lower of NGN 500,000 or 20% of annual rent paid
    "rent_relief_cap": 500_000.0,
    "rent_relief_pct": 0.20,

    # Progressive Tax Bands — Schedule 6, NTA 2025
    "band1_upper": 800_000.0,     # 0%  — tax-free threshold
    "band1_rate":  0.00,
    "band2_upper": 3_000_000.0,   # 15% — next NGN 2,200,000
    "band2_rate":  0.15,
    "band3_upper": 12_000_000.0,  # 18% — next NGN 9,000,000
    "band3_rate":  0.18,
    "band4_upper": 25_000_000.0,  # 21% — next NGN 13,000,000
    "band4_rate":  0.21,
    "band5_upper": 50_000_000.0,  # 23% — next NGN 25,000,000
    "band5_rate":  0.23,
    "band6_rate":  0.25,          # 25% — above NGN 50,000,000

    # Statutory contributions — deductible only when actually paid
    # (captured via deductible_expense -> pension classification in transactions)
    "pension_employee_rate": 0.08,
    "nhf_rate": 0.025,
    "nhis_rate": 0.05,
}
