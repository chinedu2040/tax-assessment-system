# Secure Automated Tax Self-Assessment System for Nigerian Freelancers

A production-grade, full-stack web application that automatically classifies bank statement transactions and computes Nigerian personal income tax for freelancers, in strict compliance with FIRS 2024 guidelines and the Nigeria Data Protection Regulation (NDPR).

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/tax-assessment-system.git
cd tax-assessment-system
docker-compose up --build
```

---

## URLs

| Service | URL |
|---|---|
| Frontend (3-step wizard) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger UI (interactive docs) | http://localhost:8000/docs |
| ReDoc (clean docs) | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |

---

## What This System Does

Nigerian freelancers (tech workers, designers, writers, crypto traders) face two simultaneous tax compliance failures:

- **Over-taxation**: Registered freelancers overpay because they don't know about the Consolidated Relief Allowance (CRA) and other statutory deductions.
- **Under-taxation**: Unregistered freelancers earning through Upwork, Fiverr, Payoneer, crypto wallets, etc. are invisible to the tax system.

This system fixes both by:
1. Ingesting raw bank statements (CSV, Excel, PDF — including scanned/OCR)
2. Classifying every transaction using a hybrid rule-based + NLP engine
3. Automatically applying FIRS 2024 Nigerian tax rules (CRA, progressive bands, minimum tax)
4. Generating a professional, audit-ready PDF tax assessment report
5. Securely deleting the uploaded source file after processing (NDPR compliance)

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Tailwind CSS |
| Backend | Python FastAPI |
| Database | PostgreSQL 15 |
| CSV/Excel parsing | pandas |
| PDF parsing | pdfplumber + tabula-py |
| OCR (scanned docs) | pytesseract + pdf2image + Tesseract |
| NLP/ML classifier | scikit-learn + TF-IDF |
| PDF report generation | ReportLab |
| Containerisation | Docker + docker-compose |
| API style | RESTful (OpenAPI 3.0) |

---

## How to Use the App

**Step 1 — Upload**
- Drag and drop (or click to browse) your bank statement
- Supported formats: `.csv`, `.xlsx`, `.xls`, `.pdf`
- Supported banks: GTBank, Access Bank, Zenith, UBA, First Bank, Kuda, OPay, PalmPay, Sterling, Stanbic IBTC

**Step 2 — Review & Correct**
- Review all classified transactions in a full table
- Amber rows = needs your attention (low-confidence classification)
- Edit any category using the dropdown: Taxable Income / Deductible Expense / Non-Taxable
- Live tax estimate updates as you make corrections

**Step 3 — Download Report**
- View your tax summary: Gross Income, CRA, Taxable Income, Tax Liability
- See the progressive band breakdown in a bar chart
- Download the full PDF report (suitable for submission to tax authorities)

---

## API Documentation

FastAPI generates full interactive documentation automatically.

- **Swagger UI** at `/docs` — test every endpoint directly in the browser, including file uploads
- **ReDoc** at `/redoc` — clean, readable reference documentation
- **OpenAPI JSON** at `/openapi.json` — import into Postman if needed

No manual Postman setup required. You can upload files, confirm transactions, and download reports entirely through `/docs`.

---

## Running Tests

```bash
# Run all tests inside the running backend container
docker-compose exec backend pytest

# Run specific test files
docker-compose exec backend pytest tests/test_tax_engine.py -v
docker-compose exec backend pytest tests/test_classifier.py -v
docker-compose exec backend pytest tests/test_parser.py -v
docker-compose exec backend pytest tests/test_e2e.py -v
```

---

## Deploying to Railway

Prerequisites:
- Railway account at [railway.app](https://railway.app)
- Railway CLI: `npm install -g @railway/cli`
- Log in: `railway login`

```bash
railway init
railway add --plugin postgresql
railway variables set SECRET_KEY=your-strong-random-key
railway variables set ENV=production
railway variables set UPLOAD_DIR=/app/uploads
railway variables set REPORT_DIR=/app/reports
railway up
railway domain
```

---

## Project Structure

```
tax-assessment-system/
├── docker-compose.yml
├── .env.example
├── database/
│   └── init.sql                  # PostgreSQL schema + FIRS 2024 tax parameters
├── backend/
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Environment variable loading
│   ├── database.py               # SQLAlchemy engine + session
│   ├── models.py                 # ORM models
│   ├── modules/
│   │   ├── ingestion/            # CSV, Excel, PDF, OCR parsers
│   │   ├── classification/       # Rule-based + NLP + hybrid engine
│   │   ├── tax_engine/           # FIRS 2024 tax computation
│   │   └── reporting/            # ReportLab PDF generator
│   ├── routers/                  # FastAPI route handlers
│   ├── schemas/                  # Pydantic request/response models
│   └── tests/                   # Full pytest suite
└── frontend/
    └── src/
        ├── App.jsx               # 3-step wizard shell
        ├── components/           # Upload, Review, Report, Navbar, etc.
        └── services/api.js       # Axios API client
```

---

## Nigerian Tax Computation Formula (FIRS 2024)

```
Gross Income  =  Sum of all taxable income credits

CRA           =  MAX(₦200,000, 1% × Gross) + 20% × Gross
Pension       =  8% × Gross
NHF           =  2.5% × Gross
NHIS          =  5% × Gross

Taxable Income = Gross − CRA − Pension − NHF − NHIS − Deductible Expenses

Progressive Tax Bands:
  First ₦300,000     → 7%
  Next  ₦300,000     → 11%
  Next  ₦500,000     → 15%
  Next  ₦500,000     → 19%
  Next  ₦1,600,000   → 21%
  Above ₦3,200,000   → 24%

Minimum Tax = 1% of Gross Income (applies if computed tax < minimum)
```

---

## Data Privacy (NDPR Compliance)

- Uploaded bank statement files are **permanently deleted** from the server immediately after the tax report is generated
- Only canonical (normalised) transaction records are stored in the database
- All OCR processing is done locally — no data is sent to external APIs
- Every action is logged to an audit trail (`audit_logs` table) with timestamps
- Deletion is verified and logged; failure raises an alert rather than silently failing

---

## Thesis Details

| Field | Detail |
|---|---|
| Title | Design and Implementation of a Secure Automated Tax Self-Assessment System for Freelancers |
| Author | Udeze Chinedu Chinagorom |
| Student ID | CSC/2018/169 |
| Department | Computer Science with Economics |
| Supervisor | Dr. H. O. Odukoya |
| Submitted | 22 May 2026 |
