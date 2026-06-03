# CLAUDE.md — Complete Build Instructions
# Secure Automated Tax Self-Assessment System for Nigerian Freelancers

> READ THIS ENTIRE FILE BEFORE WRITING A SINGLE LINE OF CODE.
>
> The person who owns this project does NOT write code.
> You are responsible for 100% of everything:
> frontend, backend, database, ML pipeline, Docker setup, GitHub push,
> live deployment, API documentation, and tests.
>
> Do not ask the user to copy-paste anything, run commands manually,
> configure anything by hand, or make any decisions about the code.
> You decide everything. You build everything. You fix everything.
> When something fails, fix it yourself without asking.

---

## SECTION 1 — PROJECT IDENTITY

Title:      Design and Implementation of a Secure Automated Tax
            Self-Assessment System for Freelancers

Author:     Udeze Chinedu Chinagorom
Student ID: CSC/2018/169
Department: Computer Science with Economics
Supervisor: Dr. H. O. Odukoya
Submitted:  22/05/26

This is an undergraduate final-year thesis project. The system must be
fully functional, production-grade, and match the architecture in the
thesis (Chapters 1–3) exactly. Nothing should be mocked or faked —
everything must work end-to-end.

---

## SECTION 2 — THE PROBLEM THIS SYSTEM SOLVES

Nigerian freelancers (tech workers, designers, writers, crypto traders,
consultants) face two simultaneous tax compliance failures:

OVER-TAXATION:
  Registered freelancers overpay because they don't know about the
  Consolidated Relief Allowance (CRA) and other deductions they are
  legally entitled to claim.

UNDER-TAXATION:
  Unregistered freelancers earning through Upwork, Fiverr, Payoneer,
  crypto wallets, etc. are completely invisible to the tax system.
  They have no accessible, guided entry point into formal compliance.

Existing tools (FIRS e-filing portal, spreadsheets, accounting software)
all require pre-organised structured data. None can ingest raw bank
statements, classify transactions intelligently, or automatically apply
Nigerian statutory tax rules.

This system fixes all of that.

---

## SECTION 3 — TECHNOLOGY STACK (NON-NEGOTIABLE)

Do not substitute any technology. Use exactly these:

  Layer                   Technology
  ----------------------  ------------------------------------------
  Frontend                React + Tailwind CSS
  Backend                 Python FastAPI
  Database                PostgreSQL 15
  CSV/Excel parsing       pandas
  PDF parsing             pdfplumber + tabula-py
  OCR (scanned docs)      pytesseract + pdf2image + Tesseract
  NLP/ML classifier       scikit-learn + TF-IDF via NLTK
  PDF report generation   ReportLab
  Containerisation        Docker + docker-compose
  API style               RESTful
  Version control         Git + GitHub

---

## SECTION 4 — COMPLETE FILE STRUCTURE

Create exactly this structure. Every file listed must exist and work.

  tax-assessment-system/
  ├── CLAUDE.md
  ├── README.md
  ├── docker-compose.yml
  ├── .env.example
  ├── .gitignore
  │
  ├── frontend/
  │   ├── Dockerfile
  │   ├── package.json
  │   ├── tailwind.config.js
  │   ├── vite.config.js
  │   ├── index.html
  │   ├── public/
  │   └── src/
  │       ├── App.jsx
  │       ├── main.jsx
  │       ├── index.css
  │       ├── components/
  │       │   ├── UploadStep.jsx
  │       │   ├── ReviewStep.jsx
  │       │   ├── ReportStep.jsx
  │       │   ├── TaxSummaryCard.jsx
  │       │   ├── TransactionTable.jsx
  │       │   ├── ProgressBar.jsx
  │       │   └── Navbar.jsx
  │       └── services/
  │           └── api.js
  │
  ├── backend/
  │   ├── Dockerfile
  │   ├── requirements.txt
  │   ├── main.py
  │   ├── config.py
  │   ├── database.py
  │   ├── models.py
  │   ├── modules/
  │   │   ├── __init__.py
  │   │   ├── ingestion/
  │   │   │   ├── __init__.py
  │   │   │   ├── document_parser.py
  │   │   │   └── normaliser.py
  │   │   ├── classification/
  │   │   │   ├── __init__.py
  │   │   │   ├── rule_based.py
  │   │   │   ├── nlp_classifier.py
  │   │   │   ├── hybrid_engine.py
  │   │   │   └── training_data.py
  │   │   ├── tax_engine/
  │   │   │   ├── __init__.py
  │   │   │   ├── tax_computation.py
  │   │   │   └── statutory_rules.py
  │   │   └── reporting/
  │   │       ├── __init__.py
  │   │       └── report_generator.py
  │   ├── routers/
  │   │   ├── __init__.py
  │   │   ├── upload.py
  │   │   ├── confirm.py
  │   │   └── report.py
  │   ├── schemas/
  │   │   ├── __init__.py
  │   │   ├── transaction.py
  │   │   └── tax_report.py
  │   ├── ml_models/
  │   │   └── .gitkeep
  │   └── tests/
  │       ├── __init__.py
  │       ├── test_parser.py
  │       ├── test_classifier.py
  │       ├── test_tax_engine.py
  │       └── test_e2e.py
  │
  └── database/
      └── init.sql

---

## SECTION 5 — DATABASE SCHEMA (PostgreSQL)

File: database/init.sql
Create all tables and seed all data on first run.

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
    user_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) UNIQUE NOT NULL,
    full_name   VARCHAR(255),
    tin         VARCHAR(50),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE documents (
    document_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES users(user_id),
    file_name     VARCHAR(255),
    file_type     VARCHAR(20),
    upload_path   TEXT,
    status        VARCHAR(50) DEFAULT 'uploaded',
    uploaded_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE transactions (
    transaction_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id           UUID REFERENCES documents(document_id),
    user_id               UUID REFERENCES users(user_id),
    date                  DATE,
    description           TEXT,
    amount                NUMERIC(15,2),
    direction             VARCHAR(10),
    category              VARCHAR(50),
    sub_category          VARCHAR(100),
    classification_method VARCHAR(20),
    confidence_score      NUMERIC(5,4),
    user_corrected        BOOLEAN DEFAULT FALSE,
    created_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tax_computations (
    computation_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES users(user_id),
    tax_year          INTEGER,
    gross_income      NUMERIC(15,2),
    cra_fixed         NUMERIC(15,2),
    cra_percentage    NUMERIC(15,2),
    total_cra         NUMERIC(15,2),
    pension_relief    NUMERIC(15,2),
    nhf_relief        NUMERIC(15,2),
    nhis_relief       NUMERIC(15,2),
    other_deductions  NUMERIC(15,2),
    taxable_income    NUMERIC(15,2),
    tax_liability     NUMERIC(15,2),
    effective_rate    NUMERIC(6,4),
    band_breakdown    JSONB,
    computed_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tax_reports (
    report_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(user_id),
    computation_id  UUID REFERENCES tax_computations(computation_id),
    report_path     TEXT,
    generated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE audit_logs (
    log_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID,
    action      VARCHAR(100),
    details     JSONB,
    timestamp   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE statutory_parameters (
    param_id        SERIAL PRIMARY KEY,
    param_key       VARCHAR(100) UNIQUE NOT NULL,
    param_value     NUMERIC(15,4),
    description     TEXT,
    effective_year  INTEGER DEFAULT 2024
);

INSERT INTO statutory_parameters
  (param_key, param_value, description, effective_year)
VALUES
  ('cra_fixed_amount',    200000.00, 'Fixed CRA component (NGN)',                2024),
  ('cra_percentage',           0.20, '20% of gross income CRA component',        2024),
  ('minimum_cra_trigger',      0.01, '1% of gross — CRA fixed floor trigger',    2024),
  ('band1_upper',         300000.00, 'First band upper limit (NGN)',              2024),
  ('band1_rate',               0.07, 'First band tax rate 7%',                   2024),
  ('band2_upper',         600000.00, 'Second band upper limit (NGN)',             2024),
  ('band2_rate',               0.11, 'Second band tax rate 11%',                 2024),
  ('band3_upper',        1100000.00, 'Third band upper limit (NGN)',              2024),
  ('band3_rate',               0.15, 'Third band tax rate 15%',                  2024),
  ('band4_upper',        1600000.00, 'Fourth band upper limit (NGN)',             2024),
  ('band4_rate',               0.19, 'Fourth band tax rate 19%',                 2024),
  ('band5_upper',        3200000.00, 'Fifth band upper limit (NGN)',              2024),
  ('band5_rate',               0.21, 'Fifth band tax rate 21%',                  2024),
  ('band6_rate',               0.24, 'Top band rate above 3.2M NGN 24%',         2024),
  ('minimum_tax_rate',         0.01, 'Minimum tax 1% of gross income',           2024),
  ('pension_employee_rate',    0.08, 'Employee pension contribution 8%',         2024),
  ('nhf_rate',                0.025, 'National Housing Fund 2.5%',               2024),
  ('nhis_rate',                0.05, 'National Health Insurance 5%',             2024);
```

---

## SECTION 6 — MODULE IMPLEMENTATION DETAILS

### 6.1 Document Parser (backend/modules/ingestion/document_parser.py)

Handle all four input types:

CSV:
  Use pandas.read_csv() with encoding fallback (UTF-8 then latin-1).
  Handle these column name variations from Nigerian banks:
    Date columns:   "Trans. Date", "Transaction Date", "Value Date",
                    "Date", "Txn Date", "BookingDate"
    Description:    "Narration", "Description", "Details", "Remarks",
                    "Transaction Details", "Particulars"
    Debit:          "Debit", "Withdrawals", "Dr", "Debit Amount"
    Credit:         "Credit", "Deposits", "Cr", "Credit Amount"
    Amount:         "Amount" (signed — negative = debit, positive = credit)
    Balance:        "Balance", "Running Balance", "Ledger Balance"

Excel:
  Use pandas.read_excel() for .xlsx and .xls.
  Same flexible column mapping as CSV above.
  Try sheet index 0 first, then search all sheets for the one with
  the most transaction-looking rows.

PDF (digital/text-based):
  Use pdfplumber to extract tables from each page.
  Handle multi-page statements by concatenating all pages.
  Use spatial alignment to detect table boundaries.
  Supported banks: GTBank, Access Bank, Zenith Bank, UBA, First Bank,
  Kuda, OPay, PalmPay, Sterling Bank, Stanbic IBTC.

Scanned PDF / Image:
  Use pdf2image to convert pages to images.
  Use pytesseract to extract text from each image.
  Parse the OCR text output into structured rows.
  Flag all OCR-extracted records with source_format = 'scanned'
  and lower confidence scores.

All parsers must pass raw records to the Normaliser before returning.
Never return un-normalised data from a parser.

### 6.2 Normaliser (backend/modules/ingestion/normaliser.py)

Convert all raw extracted data into this canonical schema:

  {
    "date":            "YYYY-MM-DD",
    "description":     "cleaned string",
    "amount":          float (always positive),
    "direction":       "credit" or "debit",
    "raw_description": "original string before cleaning",
    "source_format":   "csv" | "excel" | "pdf" | "scanned"
  }

Operations to perform:
  - Strip all leading/trailing whitespace from all fields
  - Remove special characters from descriptions except letters, numbers,
    spaces, hyphens, forward slashes
  - Parse all date formats:
      DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD,
      "14 Jan 2024", "14-Jan-24", "14.01.2024"
  - Normalise amounts: remove commas, currency symbols (NGN, ₦, N, $)
  - Derive direction:
      If separate Debit/Credit columns exist: non-empty debit = debit
      If signed amount: negative = debit, positive = credit
      If keywords in description: "withdrawal", "debit", "POS" = debit
  - Remove rows where amount is zero or null
  - Remove duplicate rows (same date + description + amount)

### 6.3 Rule-Based Classifier (backend/modules/classification/rule_based.py)

Match transaction descriptions against keyword patterns.
Return (category, sub_category, confidence) tuple.
Confidence for a rule match = 0.90.
Confidence for no match = 0.00.

RULES = {
  "taxable_income": {
    "freelance_income": [
      "upwork", "fiverr", "toptal", "payoneer", "wise transfer",
      "transferwise", "client payment", "project payment", "freelance",
      "consultancy fee", "professional fee", "invoice payment",
      "remittance", "toptal", "guru.com", "freelancer.com"
    ],
    "salary": [
      "salary", "salari", "monthly pay", "payroll", "wages",
      "staff pay", "net pay", "basic pay"
    ],
    "business_income": [
      "sales proceeds", "business income", "revenue", "proceeds"
    ],
    "crypto_income": [
      "binance", "coinbase", "crypto", "bitcoin", "ethereum",
      "usdt", "blockchain", "p2p transfer", "bybit", "kucoin",
      "luno", "quidax", "buycoin"
    ],
    "foreign_income": [
      "swift", "foreign currency", "domiciliary", "dom account",
      "international transfer", "wire transfer", "dollar credit"
    ]
  },
  "deductible_expense": {
    "equipment": [
      "laptop", "computer", "monitor", "keyboard", "phone purchase",
      "gadget", "hardware", "iphone", "macbook", "dell", "hp laptop"
    ],
    "software": [
      "adobe", "github", "notion", "figma", "canva", "zoom", "slack",
      "microsoft 365", "office 365", "jetbrains", "digitalocean",
      "aws", "google workspace", "gsuite", "netlify", "vercel",
      "heroku", "namecheap", "godaddy"
    ],
    "internet": [
      "mtn", "airtel", "glo", "9mobile", "spectranet", "swift",
      "smile", "internet", "data subscription", "broadband",
      "data bundle", "wifi subscription"
    ],
    "utilities": [
      "nepa", "disco", "electricity", "ikedc", "ekedc", "bedc",
      "phcn", "token", "dstv", "showmax", "netflix", "water bill"
    ],
    "professional_development": [
      "udemy", "coursera", "pluralsight", "training", "workshop",
      "certification", "book purchase", "conference", "seminar",
      "linkedin learning", "skillshare"
    ],
    "pension": [
      "pension", "pfa", "retirement", "nhf", "nhis",
      "stanbic ibtc pensions", "arm pensions", "aiico pension"
    ],
    "transport": [
      "uber", "bolt", "indriver", "taxify", "fuel", "transport",
      "logistics", "delivery"
    ]
  },
  "non_taxable": {
    "transfer": [
      "transfer to", "transfer from", "trf", "intra-bank",
      "between accounts", "own account", "inter-account"
    ],
    "loan": [
      "loan", "credit facility", "overdraft", "repayment",
      "quick credit", "salary advance"
    ],
    "refund": [
      "refund", "reversal", "chargeback", "dispute credit"
    ],
    "atm": [
      "atm withdrawal", "cash withdrawal", "pos purchase"
    ]
  }
}

### 6.4 NLP Classifier (backend/modules/classification/nlp_classifier.py)

Uses scikit-learn with TF-IDF for ambiguous transactions.

Model pipeline:
  from sklearn.pipeline import Pipeline
  from sklearn.feature_extraction.text import TfidfVectorizer
  from sklearn.linear_model import LogisticRegression

  pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,
        strip_accents='unicode',
        analyzer='word'
    )),
    ('clf', LogisticRegression(
        multi_class='ovr',
        max_iter=1000,
        C=1.0,
        random_state=42
    ))
  ])

Training:
  - Load training data from training_data.py on startup
  - Train the model if no saved model exists at ml_models/classifier.pkl
  - Save the trained model to ml_models/classifier.pkl using joblib
  - Each prediction returns (category, sub_category, confidence_score)
  - Target accuracy: >= 85% on held-out 20% test split

### 6.5 Hybrid Engine (backend/modules/classification/hybrid_engine.py)

Orchestrate rule-based + NLP in sequence:

  1. Run RuleBasedClassifier on transaction description
  2. If rule confidence >= 0.85 → use rule result, method = 'rule'
  3. If rule confidence < 0.85 → run NLPClassifier
  4. If NLP confidence >= 0.70 → use NLP result, method = 'nlp'
  5. If both below threshold → category = 'needs_review', method = 'flagged'
  6. User corrections → save with method = 'user_correction'
  7. All corrections are logged to audit_logs for future retraining

### 6.6 Tax Computation Engine (backend/modules/tax_engine/tax_computation.py)

Implement FIRS 2024 Nigerian Personal Income Tax Act exactly:

  def compute_tax(transactions, user_id, tax_year):

    # Step 1: Gross Income
    gross_income = sum of all transactions where category == 'taxable_income'

    # Step 2: Allowable deductions
    total_deductions = sum of all transactions where category == 'deductible_expense'

    # Step 3: Consolidated Relief Allowance (CRA)
    # CRA = higher of (200,000 OR 1% of gross) PLUS 20% of gross
    cra_fixed = max(200_000, 0.01 * gross_income)
    cra_percentage = 0.20 * gross_income
    total_cra = cra_fixed + cra_percentage

    # Step 4: Statutory reliefs
    pension_relief = 0.08 * gross_income
    nhf_relief     = 0.025 * gross_income
    nhis_relief    = 0.05 * gross_income

    # Step 5: Taxable Income
    taxable_income = gross_income
                   - total_cra
                   - pension_relief
                   - nhf_relief
                   - nhis_relief
                   - total_deductions
    taxable_income = max(0, taxable_income)

    # Step 6: Progressive Tax Bands (FIRS 2024)
    bands = [
      (300_000,      0.07),   # 7%  on first 300k
      (300_000,      0.11),   # 11% on next 300k
      (500_000,      0.15),   # 15% on next 500k
      (500_000,      0.19),   # 19% on next 500k
      (1_600_000,    0.21),   # 21% on next 1.6M
      (float('inf'), 0.24),   # 24% on remainder
    ]

    tax_liability = 0
    band_breakdown = []
    remaining = taxable_income

    for limit, rate in bands:
      if remaining <= 0: break
      taxable_in_band = min(remaining, limit)
      tax_in_band = taxable_in_band * rate
      tax_liability += tax_in_band
      band_breakdown.append({
        "rate": rate,
        "taxable_amount": taxable_in_band,
        "tax_amount": tax_in_band
      })
      remaining -= taxable_in_band

    # Step 7: Minimum tax check
    minimum_tax = 0.01 * gross_income
    if tax_liability < minimum_tax:
      tax_liability = minimum_tax

    # Step 8: Effective rate
    effective_rate = (tax_liability / gross_income * 100) if gross_income > 0 else 0

    return all values as a dict

Tax parameters must be read from the statutory_parameters table in
PostgreSQL, not hardcoded — this allows rule updates without code changes.

### 6.7 Report Generator (backend/modules/reporting/report_generator.py)

Use ReportLab to produce a professional downloadable PDF report.

Report must contain these sections in order:

  1. Header
     - System name: "Secure Tax Self-Assessment System"
     - User full name and TIN
     - Tax year
     - Date generated
     - "NDPR Compliant | FIRS 2024"

  2. Tax Summary Table
     - Gross Income
     - Consolidated Relief Allowance (CRA)
     - Pension Relief (8%)
     - NHF Relief (2.5%)
     - NHIS Relief (5%)
     - Other Allowable Deductions
     - Taxable Income
     - Tax Liability
     - Effective Tax Rate

  3. Progressive Band Breakdown Table
     - One row per band: Band, Rate, Taxable Amount, Tax Amount

  4. Full Transaction Ledger
     - Every transaction with: Date, Description, Amount, Direction,
       Category, Sub-Category, Classification Method, Confidence Score
     - Totals row at the bottom

  5. Footer
     - "Generated by Secure Tax Self-Assessment System"
     - "In compliance with the Nigeria Data Protection Regulation (NDPR)"
     - "Tax rules sourced from FIRS 2024 guidelines"

Styling:
  - Accent colour: Nigerian green #008751
  - Currency format: ₦1,234,567.00 (with ₦ symbol and comma separators)
  - Page size: A4
  - Professional, clean layout suitable for submission to tax authorities

---

## SECTION 7 — API ENDPOINTS

Implement all of these in FastAPI. Enable CORS for http://localhost:3000.

  POST   /api/upload
    Accepts:  multipart/form-data with fields: file, user_id
    Actions:  validate format and size (max 10MB)
              parse document
              normalise transactions
              classify all transactions
              save document + transactions to database
              log 'file_uploaded' to audit_logs
    Returns:  {
                document_id: uuid,
                transactions: [...],
                summary: {
                  total: int,
                  taxable_income_count: int,
                  deductible_count: int,
                  non_taxable_count: int,
                  needs_review_count: int
                }
              }

  POST   /api/confirm
    Accepts:  {
                document_id: uuid,
                transactions: [...with any user corrections...],
                user_id: uuid,
                tax_year: int
              }
    Actions:  save any user corrections to database
              log corrections to audit_logs
              run tax computation engine
              generate PDF report
              save computation + report to database
              SECURELY DELETE the uploaded source file from disk
              log 'file_deleted' to audit_logs
    Returns:  {
                report_id: uuid,
                computation: { all tax values },
                download_url: "/api/report/{report_id}"
              }

  GET    /api/report/{report_id}
    Returns:  PDF file (Content-Type: application/pdf)

  GET    /api/transactions/{document_id}
    Returns:  all classified transactions for a document

  POST   /api/users
    Accepts:  { email, full_name, tin }
    Returns:  { user_id }

  GET    /api/health
    Returns:  { status: "ok", timestamp: "..." }

Add proper OpenAPI metadata to every endpoint:
  - title, description, tags, response_model, status_code
  - This ensures /docs and /redoc are fully documented automatically

---

## SECTION 8 — API DOCUMENTATION (AUTOMATIC — NO EXTRA WORK NEEDED)

FastAPI generates full interactive API documentation automatically.
Configure the FastAPI app with proper metadata so the docs look professional:

  app = FastAPI(
    title="Secure Tax Self-Assessment API",
    description="Automated tax computation for Nigerian freelancers. "
                "Supports CSV, Excel, and PDF bank statements. "
                "FIRS 2024 compliant. NDPR compliant.",
    version="1.0.0",
    contact={
      "name": "Udeze Chinedu Chinagorom",
      "email": "your-email@example.com"
    },
    license_info={
      "name": "Academic Project — CSC/2018/169"
    }
  )

After the backend is running, documentation is live at:
  http://localhost:8000/docs       (Swagger UI — interactive, test endpoints here)
  http://localhost:8000/redoc      (ReDoc — clean reading format)
  http://localhost:8000/openapi.json  (raw JSON — import into Postman if needed)

No Postman setup required. Swagger UI at /docs allows uploading files,
confirming transactions, and downloading reports directly in the browser.

---

## SECTION 9 — FRONTEND (REACT + TAILWIND)

3-step wizard. Clean, professional, mobile-responsive UI.

Step 1 — Upload:
  - Nigerian green (#008751) navbar with system name
  - Drag-and-drop upload zone (also clickable)
  - Accepted: .csv, .xlsx, .xls, .pdf
  - Show file name + size after selection
  - Animated progress bar during processing
  - Format tips: "Supports GTBank, Access, Zenith, UBA, Kuda, OPay and more"
  - Step indicator at the top (Step 1 of 3)

Step 2 — Review & Correct:
  - Full transaction table with columns:
    Date | Description | Amount | Direction | Category | Sub-category |
    Method | Confidence
  - Category column is an editable dropdown:
    "Taxable Income" | "Deductible Expense" | "Non-Taxable"
  - Rows with method = 'flagged' highlighted in amber background
  - Rows with user_corrected = true highlighted in blue background
  - Live tax summary sidebar that recalculates as user edits categories:
    Shows: Gross Income, Estimated CRA, Estimated Tax Liability
  - "Confirm & Generate Report" button at the bottom
  - Step indicator at the top (Step 2 of 3)

Step 3 — Download Report:
  - Summary cards in a 2x2 grid:
    Gross Income | Total Relief | Taxable Income | Tax Liability
  - Effective tax rate displayed prominently
  - Bar chart showing band-by-band tax breakdown (use recharts or Chart.js)
  - "Download PDF Report" large green button
  - Privacy notice in a green info box:
    "Your uploaded bank statement has been permanently deleted from our
     server in compliance with the Nigeria Data Protection Regulation (NDPR)."
  - Step indicator at the top (Step 3 of 3)

---

## SECTION 10 — PRIVACY & SECURITY (NDPR — NON-NEGOTIABLE)

1. SECURE DELETION
   After generating the report, delete the uploaded source file from disk.
   Use os.unlink() or pathlib Path.unlink().
   Immediately log the deletion to audit_logs with action = 'file_deleted'.
   If deletion fails, log the error and raise an alert — do not silently fail.

2. AUDIT TRAIL
   Every action must be logged to audit_logs:
     'file_uploaded'       — when a file is received
     'classified'          — when classification is complete
     'user_correction'     — when user edits a category
     'tax_computed'        — when tax engine runs
     'report_generated'    — when PDF is created
     'file_deleted'        — when source file is deleted
   Include user_id, timestamp, and a details JSONB with relevant metadata.

3. INPUT VALIDATION
   Validate every uploaded file:
     - File extension must be .csv, .xlsx, .xls, or .pdf
     - File size must not exceed 10MB
     - File must parse without critical errors
   Return clear error messages for invalid files.

4. LOCAL OCR ONLY
   Tesseract runs locally. Never send document data to any external API.

5. DATA MINIMISATION
   Store only canonical transaction records.
   Never persist raw file bytes in the database.

6. CORS
   Allow http://localhost:3000 in development.
   Allow the Railway frontend URL in production.

---

## SECTION 11 — DOCKER SETUP

File: docker-compose.yml

  version: "3.9"

  services:
    db:
      image: postgres:15
      environment:
        POSTGRES_DB: taxdb
        POSTGRES_USER: taxuser
        POSTGRES_PASSWORD: taxpass
      volumes:
        - postgres_data:/var/lib/postgresql/data
        - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
      ports:
        - "5432:5432"
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U taxuser -d taxdb"]
        interval: 5s
        timeout: 5s
        retries: 5

    backend:
      build: ./backend
      environment:
        DATABASE_URL: postgresql://taxuser:taxpass@db:5432/taxdb
        UPLOAD_DIR: /app/uploads
        REPORT_DIR: /app/reports
        SECRET_KEY: change-this-in-production
        ENV: development
      ports:
        - "8000:8000"
      depends_on:
        db:
          condition: service_healthy
      volumes:
        - ./backend:/app
        - uploads_data:/app/uploads
        - reports_data:/app/reports

    frontend:
      build: ./frontend
      environment:
        VITE_API_URL: http://localhost:8000
      ports:
        - "3000:3000"
      depends_on:
        - backend

  volumes:
    postgres_data:
    uploads_data:
    reports_data:

File: .env.example

  DATABASE_URL=postgresql://taxuser:taxpass@db:5432/taxdb
  UPLOAD_DIR=/app/uploads
  REPORT_DIR=/app/reports
  SECRET_KEY=change-this-in-production
  ENV=development
  FRONTEND_URL=http://localhost:3000

File: .gitignore

  .env
  __pycache__/
  *.pyc
  *.pyo
  node_modules/
  dist/
  build/
  .DS_Store
  *.pkl
  uploads/
  reports/
  postgres_data/

---

## SECTION 12 — SYNTHETIC TRAINING DATA

File: backend/modules/classification/training_data.py

Generate at least 600 labelled examples. Must include realistic
Nigerian bank transaction narrations from these categories:

TAXABLE INCOME examples (at least 150):
  - "UPWORK PAYMENT - PROJECT COMPLETION INV#2341"
  - "PAYONEER TRANSFER USD 850.00 REF:PAY2024"
  - "FIVERR WITHDRAWAL TO BANK ACCOUNT"
  - "CLIENT PAYMENT WEB DESIGN PROJECT CHIDINMA OKONKWO"
  - "WISE TRANSFER GBP 400 FREELANCE WRITING"
  - "CONSULTANCY FEE ADAEZE SOLUTIONS LTD"
  - "TOPTAL PAYMENT Q3 2024 INVOICE"
  - "SALARY PAYMENT NOVEMBER 2024"
  - "MONTHLY PAYROLL CREDIT TECHCORP LTD"
  - "BINANCE P2P TRANSFER USDT SALE"
  - "CRYPTO WITHDRAWAL QUIDAX.COM"
  - "SWIFT CREDIT USD 1200 INTERNATIONAL CLIENT"
  - "FREELANCE WRITING FEE GUARDIAN NEWSPAPERS"
  - "GRAPHIC DESIGN PROJECT PAYMENT FINAL"
  - "PROFESSIONAL FEE INVOICE 45 SETTLEMENT"

DEDUCTIBLE EXPENSE examples (at least 150):
  - "MTN DATA SUBSCRIPTION 10GB MONTHLY"
  - "SPECTRANET INTERNET SUBSCRIPTION AUG2024"
  - "ADOBE CREATIVE CLOUD MONTHLY SUBSCRIPTION"
  - "GITHUB PRO ANNUAL SUBSCRIPTION"
  - "UDEMY COURSE PAYMENT REACT DEVELOPMENT"
  - "LAPTOP PURCHASE COMPUTER VILLAGE IKEJA"
  - "IKEDC ELECTRICITY TOKEN PURCHASE 5000"
  - "DSTV SUBSCRIPTION PREMIUM PACKAGE"
  - "AIRTEL BROADBAND MONTHLY PLAN"
  - "FIGMA PROFESSIONAL PLAN ANNUAL"
  - "AWS MONTHLY USAGE INVOICE"
  - "NOTION TEAM PLAN SUBSCRIPTION"
  - "PENSION CONTRIBUTION ARM PENSIONS OCTOBER"
  - "NHF DEDUCTION FEDERAL MORTGAGE BANK"
  - "UBER TRIP LAGOS ISLAND TO MAINLAND"
  - "BOLT RIDE SHARE VICTORIA ISLAND"
  - "FUEL PURCHASE TOTAL FILLING STATION"

NON-TAXABLE examples (at least 150):
  - "TRF TO OWN ACCOUNT SAVINGS ZENITH"
  - "INTERBANK TRANSFER PERSONAL USE"
  - "ATM WITHDRAWAL LAGOS ISLAND BRANCH"
  - "POS PURCHASE SHOPRITE IKEJA CITY MALL"
  - "LOAN REPAYMENT ZENITH BANK CREDIT"
  - "QUICK CREDIT REPAYMENT OCTOBER"
  - "REVERSAL DUPLICATE TRANSACTION"
  - "CHARGEBACK DISPUTED TRANSACTION"
  - "FAMILY SUPPORT TRANSFER"
  - "RENT PAYMENT VICTORIA GARDEN CITY"
  - "CASH DEPOSIT OVER THE COUNTER"

NEEDS REVIEW examples (ambiguous — at least 150):
  - "INFLOW FROM JOHN"
  - "PAYMENT RECEIVED"
  - "CREDIT ALERT"
  - "TRANSFER FROM EMEKA NWOSU"
  - "ONLINE PAYMENT"
  - "DEBIT ORDER"
  - "TRF 2024001234"
  - "STANDING ORDER"
  - "MANDATE DEDUCTION"

Return as a list of dicts:
  [{"text": "UPWORK PAYMENT...", "category": "taxable_income",
    "sub_category": "freelance_income"}, ...]

---

## SECTION 13 — TESTS

File: backend/tests/test_tax_engine.py

These three scenarios MUST pass with exact values:

  Scenario 1: Gross Income = ₦2,400,000/year
    gross_income        = 2_400_000
    cra_fixed           = 200_000   (200k > 1% of 2.4M = 24k)
    cra_percentage      = 480_000   (20% of 2.4M)
    total_cra           = 680_000
    pension_relief      = 192_000   (8% of 2.4M)
    nhf_relief          =  60_000   (2.5% of 2.4M)
    nhis_relief         = 120_000   (5% of 2.4M)
    taxable_income      = 1_348_000 (2.4M - 680k - 192k - 60k - 120k)
    Band 1: 300k @ 7%  =  21_000
    Band 2: 300k @ 11% =  33_000
    Band 3: 500k @ 15% =  75_000
    Band 4: 248k @ 19% =  47_120
    tax_liability       = 176_120
    effective_rate      ≈ 7.34%

  Scenario 2: Gross Income = ₦600,000/year
    total_cra           = 320_000   (200k + 20% of 600k)
    pension_relief      =  48_000
    nhf_relief          =  15_000
    nhis_relief         =  30_000
    taxable_income      = 187_000
    Band 1: 187k @ 7%  =  13_090
    minimum_tax         =   6_000   (1% of 600k — does NOT apply here)
    tax_liability       =  13_090

  Scenario 3: Gross Income = ₦10,000,000/year (top band)
    Must correctly apply 24% to income above ₦3,200,000
    Verify band_breakdown has exactly 6 entries
    Verify tax_liability > 0 and effective_rate > 20%

File: backend/tests/test_classifier.py
  - Rule-based classifier returns 'taxable_income' for "UPWORK PAYMENT"
  - Rule-based classifier returns 'deductible_expense' for "MTN DATA SUBSCRIPTION"
  - Rule-based classifier returns 'non_taxable' for "ATM WITHDRAWAL"
  - NLP classifier achieves >= 85% accuracy on 20% held-out test split
  - Hybrid engine uses method='rule' when rule confidence >= 0.85
  - Hybrid engine uses method='nlp' when rule confidence < 0.85

File: backend/tests/test_parser.py
  - CSV parser handles GTBank-style export (Date, Narration, Debit, Credit)
  - CSV parser handles Kuda-style export (Transaction Date, Description, Amount)
  - Normaliser converts all date formats to YYYY-MM-DD
  - Normaliser removes ₦ and commas from amounts
  - Normaliser correctly derives direction from signed amounts

File: backend/tests/test_e2e.py
  - Full pipeline: upload CSV → classify → confirm → report downloads
  - Audit log has entries for all 5 actions after a full run
  - Source file is deleted after confirm step
  - Report PDF file is non-empty and valid

---

## SECTION 14 — GITHUB SETUP AND PUSH

After building and testing everything locally, do all of this automatically:

  1. Initialise git repo (if not already):
       git init
       git branch -M main

  2. Create .gitignore (already in file structure above)

  3. Stage and commit all files:
       git add .
       git commit -m "Initial commit: Secure Tax Self-Assessment System

       Full-stack Nigerian freelancer tax system with:
       - FastAPI backend with 6 processing modules
       - React + Tailwind frontend (3-step wizard)
       - PostgreSQL database with FIRS 2024 tax parameters
       - Hybrid rule-based + NLP transaction classifier
       - ReportLab audit-ready PDF report generation
       - NDPR-compliant privacy-by-design architecture
       - Docker + docker-compose setup
       - Full pytest test suite

       Thesis: CSC/2018/169 — Udeze Chinedu Chinagorom"

  4. Add remote and push:
       git remote add origin https://github.com/YOUR_USERNAME/tax-assessment-system.git
       git push -u origin main

  NOTE: Ask the user for their GitHub username before running step 4.
  Do not guess or hardcode the username.

---

## SECTION 15 — LIVE DEPLOYMENT TO RAILWAY

After the GitHub push is confirmed, deploy to Railway automatically.

Railway is the recommended platform — it supports FastAPI + PostgreSQL +
React together natively, has a free starter tier, and has official
Claude Code integration.

Prerequisites (confirm these before deploying):
  - User has a Railway account (railway.app — free to create)
  - Railway CLI is installed: npm install -g @railway/cli
  - User is logged in: railway login

Deployment steps:
  1. Create Railway project:
       railway init

  2. Provision PostgreSQL database on Railway:
       railway add --plugin postgresql

  3. Set environment variables on Railway:
       railway variables set SECRET_KEY=<generate-strong-random-string>
       railway variables set ENV=production
       railway variables set UPLOAD_DIR=/app/uploads
       railway variables set REPORT_DIR=/app/reports

  4. Deploy:
       railway up

  5. After deployment, run the database init:
       railway run python -c "from database import init_db; init_db()"

  6. Get the live URL:
       railway domain

After deployment the system will be live at:
  https://your-project.railway.app          (Frontend)
  https://your-project.railway.app/docs     (Swagger UI — API documentation)
  https://your-project.railway.app/redoc    (ReDoc — API documentation)

NOTE: Ask the user if they are ready to deploy before running these steps.
Do not deploy automatically without asking.

---

## SECTION 16 — README.md TO GENERATE

Generate a README.md at the project root with these sections:
  1. Project title and one-line description
  2. Quick Start (3 commands: git clone, cd, docker-compose up --build)
  3. URLs table (Frontend, API, Swagger docs, ReDoc docs)
  4. What this system does (brief, from thesis)
  5. Tech stack table
  6. How to use the app (3 steps)
  7. API Documentation (explain /docs and /redoc)
  8. Running tests
  9. Deploying to Railway
  10. Project structure tree
  11. Nigerian tax computation formula
  12. Data privacy (NDPR compliance)
  13. Thesis details (author, supervisor, student ID)

---

## SECTION 17 — BUILD ORDER

Follow this exact sequence. Do not skip steps or build out of order.

  1.  database/init.sql            — schema + seeded tax parameters
  2.  backend/config.py            — environment variable loading
  3.  backend/database.py          — SQLAlchemy engine + session
  4.  backend/models.py            — ORM models matching schema exactly
  5.  backend/modules/ingestion/   — document_parser.py then normaliser.py
  6.  training_data.py             — 600+ synthetic Nigerian transactions
  7.  backend/modules/classification/ — rule_based, nlp_classifier, hybrid
  8.  backend/modules/tax_engine/  — statutory_rules.py then tax_computation.py
  9.  backend/modules/reporting/   — report_generator.py
  10. backend/schemas/             — Pydantic schemas
  11. backend/routers/             — upload.py, confirm.py, report.py
  12. backend/main.py              — wire up FastAPI, register routers, CORS
  13. backend/tests/               — all 4 test files
  14. Run: docker-compose up --build
  15. Run: docker-compose exec backend pytest
  16. Fix any failures before proceeding to frontend
  17. frontend/ (all components)   — build after backend is confirmed working
  18. Verify full flow in browser: upload → review → download
  19. docker-compose.yml + .env.example + .gitignore
  20. README.md
  21. GitHub push (ask user for username first)
  22. Railway deployment (ask user if ready first)

---

## SECTION 18 — FINAL CHECKLIST

Do not mark the project complete until every item is checked:

  [ ] docker-compose up --build starts all 3 services with zero errors
  [ ] Frontend loads at http://localhost:3000 without console errors
  [ ] CSV upload works and extracts transactions correctly
  [ ] Excel upload works and extracts transactions correctly
  [ ] PDF upload works and extracts transactions correctly
  [ ] All transactions have category + confidence_score populated
  [ ] Needs-review rows are highlighted amber in the UI
  [ ] User can edit any category in the review table
  [ ] Tax summary updates live as user edits categories
  [ ] Tax computation is correct for all 3 test scenarios
  [ ] PDF report downloads and opens without errors
  [ ] PDF report contains all 5 required sections
  [ ] Uploaded source file is deleted after confirm step
  [ ] All 5 action types appear in audit_logs after a full run
  [ ] All pytest tests pass with zero failures
  [ ] GET /api/health returns 200
  [ ] /docs loads with all endpoints documented
  [ ] /redoc loads with clean documentation
  [ ] GitHub repo has all files committed and pushed
  [ ] Railway deployment is live (if user confirmed ready)

---

## SECTION 19 — IF ANYTHING FAILS

Do not ask the user for help with technical errors. Fix them yourself.
Common issues and how to handle them:

  "Module not found" errors:
    Check requirements.txt — add the missing package and rebuild.

  Database connection errors:
    Check that docker-compose db healthcheck passes before backend starts.
    Verify DATABASE_URL format is correct.

  Tesseract not found:
    Add to backend Dockerfile: RUN apt-get install -y tesseract-ocr

  PDF parsing returns empty:
    Try tabula-py as fallback when pdfplumber returns no tables.
    For scanned PDFs, ensure pdf2image + poppler is installed in Dockerfile.

  NLP model accuracy below 85%:
    Add more training examples to training_data.py.
    Adjust TfidfVectorizer max_features or ngram_range.

  CORS errors in browser:
    Verify FastAPI CORS middleware allows http://localhost:3000.

  Port already in use:
    Change port mapping in docker-compose.yml.

---

*This file was prepared from Chapters 1–3 of the thesis and the presentation slides.*
*Author: Udeze Chinedu Chinagorom | CSC/2018/169*
*Do not modify the architecture, tech stack, or tax computation logic.*
*Build everything. Test everything. The user does not write code.*
