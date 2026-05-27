from typing import Dict
from sqlalchemy.orm import Session
from models import StatutoryParameter


def load_parameters(db: Session) -> Dict[str, float]:
    rows = db.query(StatutoryParameter).all()
    return {row.param_key: float(row.param_value) for row in rows}


DEFAULT_PARAMS = {
    "cra_fixed_amount": 200_000.0,
    "cra_percentage": 0.20,
    "minimum_cra_trigger": 0.01,
    "band1_upper": 300_000.0,
    "band1_rate": 0.07,
    "band2_upper": 600_000.0,
    "band2_rate": 0.11,
    "band3_upper": 1_100_000.0,
    "band3_rate": 0.15,
    "band4_upper": 1_600_000.0,
    "band4_rate": 0.19,
    "band5_upper": 3_200_000.0,
    "band5_rate": 0.21,
    "band6_rate": 0.24,
    "minimum_tax_rate": 0.01,
    "pension_employee_rate": 0.08,
    "nhf_rate": 0.025,
    "nhis_rate": 0.05,
}
