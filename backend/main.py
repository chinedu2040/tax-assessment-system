from contextlib import asynccontextmanager
from datetime import datetime
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routers import upload, confirm, report

settings = get_settings()
logger = logging.getLogger(__name__)


def _seed_statutory_parameters(db):
    """Seed FIRS 2024 statutory parameters if the table is empty."""
    from models import StatutoryParameter
    if db.query(StatutoryParameter).count() > 0:
        return
    defaults = {
        "cra_fixed_amount": 200_000,
        "cra_percentage": 0.20,
        "minimum_cra_trigger": 0.01,
        "pension_employee_rate": 0.08,
        "nhf_rate": 0.025,
        "nhis_rate": 0.05,
        "band1_upper": 300_000,
        "band2_upper": 600_000,
        "band3_upper": 1_100_000,
        "band4_upper": 1_600_000,
        "band5_upper": 3_200_000,
        "band1_rate": 0.07,
        "band2_rate": 0.11,
        "band3_rate": 0.15,
        "band4_rate": 0.19,
        "band5_rate": 0.21,
        "band6_rate": 0.24,
        "minimum_tax_rate": 0.01,
        "tax_year": 2024,
    }
    for key, value in defaults.items():
        db.add(StatutoryParameter(
            param_key=key,
            param_value=float(value),
            effective_year=2024,
            description=f"FIRS 2024 — {key}",
        ))
    db.commit()
    logger.info("Statutory parameters seeded.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure upload/report directories exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.report_dir, exist_ok=True)

    # Create all DB tables
    from database import init_db, SessionLocal
    try:
        init_db()
        logger.info("Database tables created/verified.")
        db = SessionLocal()
        try:
            _seed_statutory_parameters(db)
        finally:
            db.close()
    except Exception as exc:
        logger.warning(f"DB init skipped (will use defaults): {exc}")
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Secure Tax Self-Assessment API",
    description=(
        "Automated tax computation for Nigerian freelancers. "
        "Supports CSV, Excel, and PDF bank statements. "
        "FIRS 2024 compliant. NDPR compliant."
    ),
    version="1.0.0",
    contact={
        "name": "Udeze Chinedu Chinagorom",
        "email": "your-email@example.com",
    },
    license_info={
        "name": "Academic Project — CSC/2018/169",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        settings.frontend_url,
        "https://*.up.railway.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(confirm.router, prefix="/api")
app.include_router(report.router, prefix="/api")


@app.get(
    "/api/health",
    summary="Health check",
    description="Returns system status and current timestamp.",
    tags=["System"],
)
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
