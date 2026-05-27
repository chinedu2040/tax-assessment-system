from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from modules.tax_engine.statutory_rules import load_parameters, DEFAULT_PARAMS


def compute_tax(
    transactions: List[Dict[str, Any]],
    user_id: str,
    tax_year: int,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    try:
        params = load_parameters(db) if db else DEFAULT_PARAMS
    except Exception:
        params = DEFAULT_PARAMS

    gross_income = sum(
        float(t.get("amount", 0))
        for t in transactions
        if t.get("category") == "taxable_income"
        and t.get("direction", "credit") == "credit"
    )

    total_deductions = sum(
        float(t.get("amount", 0))
        for t in transactions
        if t.get("category") == "deductible_expense"
        and t.get("direction", "debit") == "debit"
    )

    cra_fixed_base = float(params.get("cra_fixed_amount", 200_000))
    cra_pct_rate = float(params.get("cra_percentage", 0.20))
    min_trigger = float(params.get("minimum_cra_trigger", 0.01))

    cra_fixed = max(cra_fixed_base, min_trigger * gross_income)
    cra_percentage = cra_pct_rate * gross_income
    total_cra = cra_fixed + cra_percentage

    pension_rate = float(params.get("pension_employee_rate", 0.08))
    nhf_rate = float(params.get("nhf_rate", 0.025))
    nhis_rate = float(params.get("nhis_rate", 0.05))

    pension_relief = pension_rate * gross_income
    nhf_relief = nhf_rate * gross_income
    nhis_relief = nhis_rate * gross_income

    taxable_income = max(
        0,
        gross_income - total_cra - pension_relief - nhf_relief - nhis_relief - total_deductions,
    )

    band1_upper = float(params.get("band1_upper", 300_000))
    band2_upper = float(params.get("band2_upper", 600_000))
    band3_upper = float(params.get("band3_upper", 1_100_000))
    band4_upper = float(params.get("band4_upper", 1_600_000))
    band5_upper = float(params.get("band5_upper", 3_200_000))

    bands = [
        (band1_upper, float(params.get("band1_rate", 0.07))),
        (band2_upper - band1_upper, float(params.get("band2_rate", 0.11))),
        (band3_upper - band2_upper, float(params.get("band3_rate", 0.15))),
        (band4_upper - band3_upper, float(params.get("band4_rate", 0.19))),
        (band5_upper - band4_upper, float(params.get("band5_rate", 0.21))),
        (float("inf"), float(params.get("band6_rate", 0.24))),
    ]

    tax_liability = 0.0
    band_breakdown = []
    remaining = taxable_income

    for limit, rate in bands:
        if remaining <= 0:
            break
        taxable_in_band = min(remaining, limit)
        tax_in_band = taxable_in_band * rate
        tax_liability += tax_in_band
        band_breakdown.append({
            "rate": rate,
            "taxable_amount": round(taxable_in_band, 2),
            "tax_amount": round(tax_in_band, 2),
        })
        remaining -= taxable_in_band

    min_tax_rate = float(params.get("minimum_tax_rate", 0.01))
    minimum_tax = min_tax_rate * gross_income
    if tax_liability < minimum_tax:
        tax_liability = minimum_tax

    effective_rate = (tax_liability / gross_income * 100) if gross_income > 0 else 0.0

    return {
        "user_id": user_id,
        "tax_year": tax_year,
        "gross_income": round(gross_income, 2),
        "cra_fixed": round(cra_fixed, 2),
        "cra_percentage": round(cra_percentage, 2),
        "total_cra": round(total_cra, 2),
        "pension_relief": round(pension_relief, 2),
        "nhf_relief": round(nhf_relief, 2),
        "nhis_relief": round(nhis_relief, 2),
        "other_deductions": round(total_deductions, 2),
        "taxable_income": round(taxable_income, 2),
        "tax_liability": round(tax_liability, 2),
        "effective_rate": round(effective_rate, 4),
        "band_breakdown": band_breakdown,
    }
