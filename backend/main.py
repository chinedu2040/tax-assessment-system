from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routers import upload, confirm, report

settings = get_settings()

app = FastAPI(
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
        settings.frontend_url,
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
