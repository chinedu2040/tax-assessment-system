from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from modules.tax_engine.statutory_rules import load_parameters, DEFAULT_PARAMS
from modules.tax_engine.state_rates import get_state_info


def compute_tax(
    transactions: List[Dict[str, Any]],
    user_id: str,
    tax_year: int,
    db: Optional[Session] = None,
    state_of_residence: Optional[str] = None,
    annual_rent: float = 0.0,
) -> Dict[str, Any]:
    """
    Compute personal income tax under the Nigeria Tax Act 2025 (effective 1 Jan 2026).

    Key changes from the repealed PITA:
    - Consolidated Relief Allowance (CRA) abolished; replaced by Rent Relief.
    - Rent Relief = lower of NGN 500,000 or 20% of annual rent paid.
    - First NGN 800,000 of taxable income is exempt (0% band).
    - Minimum tax (1% of gross) no longer applies.
    - Pension, NHF and NHIS reliefs are deductible only when actually paid;
      they are captured through deductible_expense -> pension transaction classification.
    """
    try:
        params = load_parameters(db) if db else DEFAULT_PARAMS
    except Exception:
        params = DEFAULT_PARAMS

    # ── Income ────────────────────────────────────────────────────────────────
    gross_income = sum(
        float(t.get("amount", 0))
        for t in transactions
        if t.get("category") == "taxable_income"
        and t.get("direction", "credit") == "credit"
    )

    # Allowable business deductions (equipment, software, internet, etc.)
    # Pension / NHF / NHIS are included here IF they appear as paid transactions.
    total_deductions = sum(
        float(t.get("amount", 0))
        for t in transactions
        if t.get("category") == "deductible_expense"
        and t.get("direction", "debit") == "debit"
    )

    # ── Rent Relief (NTA 2025 — replaces CRA) ────────────────────────────────
    rent_relief_cap = float(params.get("rent_relief_cap", 500_000))
    rent_relief_pct = float(params.get("rent_relief_pct", 0.20))
    rent_relief = min(rent_relief_cap, rent_relief_pct * annual_rent) if annual_rent > 0 else 0.0

    # Pension / NHF / NHIS are not auto-applied; set to zero here.
    pension_relief = 0.0
    nhf_relief = 0.0
    nhis_relief = 0.0

    # ── Taxable Income ────────────────────────────────────────────────────────
    taxable_income = max(0.0, gross_income - rent_relief - total_deductions)

    # ── NTA 2025 Progressive Bands ────────────────────────────────────────────
    band1_upper = float(params.get("band1_upper", 800_000))
    band2_upper = float(params.get("band2_upper", 3_000_000))
    band3_upper = float(params.get("band3_upper", 12_000_000))
    band4_upper = float(params.get("band4_upper", 25_000_000))
    band5_upper = float(params.get("band5_upper", 50_000_000))

    bands = [
        (band1_upper,                  float(params.get("band1_rate", 0.00))),
        (band2_upper - band1_upper,    float(params.get("band2_rate", 0.15))),
        (band3_upper - band2_upper,    float(params.get("band3_rate", 0.18))),
        (band4_upper - band3_upper,    float(params.get("band4_rate", 0.21))),
        (band5_upper - band4_upper,    float(params.get("band5_rate", 0.23))),
        (float("inf"),                 float(params.get("band6_rate", 0.25))),
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

    # NTA 2025: Minimum tax (1% rule) is abolished; replaced by the 0% band.

    # ── State Development Levy ────────────────────────────────────────────────
    state_info = get_state_info(state_of_residence or "")
    development_levy = float(state_info["development_levy"])
    total_tax_payable = tax_liability + development_levy

    effective_rate = (tax_liability / gross_income * 100) if gross_income > 0 else 0.0

    return {
        "user_id": user_id,
        "tax_year": tax_year,
        "gross_income": round(gross_income, 2),
        "rent_relief": round(rent_relief, 2),
        # DB-compatible aliases: cra columns repurposed to store rent relief
        "cra_fixed": 0.0,
        "cra_percentage": round(rent_relief, 2),
        "total_cra": round(rent_relief, 2),
        "pension_relief": pension_relief,
        "nhf_relief": nhf_relief,
        "nhis_relief": nhis_relief,
        "other_deductions": round(total_deductions, 2),
        "taxable_income": round(taxable_income, 2),
        "tax_liability": round(tax_liability, 2),
        "development_levy": round(development_levy, 2),
        "total_tax_payable": round(total_tax_payable, 2),
        "effective_rate": round(effective_rate, 4),
        "band_breakdown": band_breakdown,
        "state_of_residence": state_of_residence or "Not specified",
        "state_irs": state_info["irs"],
    }
