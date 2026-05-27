"""
End-to-end tests using FastAPI TestClient with an in-memory SQLite database.
These tests verify the full pipeline: upload → classify → confirm → report download.
"""
import io
import uuid
import pytest
import pandas as pd
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Patch config before importing app
import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["UPLOAD_DIR"] = "/tmp/tax_test_uploads"
os.environ["REPORT_DIR"] = "/tmp/tax_test_reports"

from database import Base, get_db
from main import app

# In-memory SQLite engine for tests
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Enable UUID support for SQLite
@event.listens_for(TEST_ENGINE, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Patch models to use String instead of UUID for SQLite compatibility
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def user_id(client):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/api/users", json={
        "email": email,
        "full_name": "Test User",
        "tin": "1234567890",
    })
    assert resp.status_code == 201
    return resp.json()["user_id"]


def _make_sample_csv() -> bytes:
    df = pd.DataFrame({
        "Date": ["2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18"],
        "Narration": [
            "UPWORK PAYMENT INV 1234",
            "MTN DATA SUBSCRIPTION",
            "ATM WITHDRAWAL LAGOS",
            "PAYONEER USD 500 FREELANCE",
        ],
        "Debit": [None, 5000, 10000, None],
        "Credit": [150000, None, None, 200000],
        "Balance": [500000, 495000, 485000, 685000],
    })
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


class TestFullPipeline:
    @pytest.fixture(scope="class")
    def upload_result(self, client, user_id):
        csv_bytes = _make_sample_csv()
        resp = client.post(
            "/api/upload",
            data={"user_id": user_id},
            files={"file": ("test_statement.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 200, resp.text
        return resp.json()

    @pytest.fixture(scope="class")
    def confirm_result(self, client, user_id, upload_result):
        document_id = upload_result["document_id"]
        transactions = upload_result["transactions"]
        payload = {
            "document_id": document_id,
            "transactions": [
                {"transaction_id": t["transaction_id"], "category": t["category"], "sub_category": t.get("sub_category"), "user_corrected": False}
                for t in transactions
            ],
            "user_id": user_id,
            "tax_year": 2024,
        }
        resp = client.post("/api/confirm", json=payload)
        assert resp.status_code == 200, resp.text
        return resp.json()

    def test_upload_returns_document_id(self, upload_result):
        assert "document_id" in upload_result
        assert upload_result["document_id"]

    def test_upload_returns_transactions(self, upload_result):
        assert len(upload_result["transactions"]) == 4

    def test_all_transactions_classified(self, upload_result):
        for t in upload_result["transactions"]:
            assert t["category"] is not None
            assert t["confidence_score"] is not None

    def test_confirm_returns_report_id(self, confirm_result):
        assert "report_id" in confirm_result
        assert confirm_result["report_id"]

    def test_confirm_returns_computation(self, confirm_result):
        comp = confirm_result["computation"]
        assert comp["gross_income"] > 0
        assert comp["tax_liability"] >= 0

    def test_confirm_returns_download_url(self, confirm_result):
        assert "download_url" in confirm_result
        assert "/api/report/" in confirm_result["download_url"]

    def test_report_download(self, client, confirm_result):
        report_id = confirm_result["report_id"]
        resp = client.get(f"/api/report/{report_id}")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert len(resp.content) > 0

    def test_report_is_valid_pdf(self, client, confirm_result):
        report_id = confirm_result["report_id"]
        resp = client.get(f"/api/report/{report_id}")
        assert resp.content[:4] == b"%PDF"


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        assert "timestamp" in resp.json()


class TestInvalidUpload:
    def test_unsupported_format(self, client, user_id):
        resp = client.post(
            "/api/upload",
            data={"user_id": user_id},
            files={"file": ("test.txt", b"hello", "text/plain")},
        )
        assert resp.status_code == 400

    def test_file_too_large(self, client, user_id):
        large_bytes = b"x" * (11 * 1024 * 1024)
        resp = client.post(
            "/api/upload",
            data={"user_id": user_id},
            files={"file": ("big.csv", large_bytes, "text/csv")},
        )
        assert resp.status_code == 413
