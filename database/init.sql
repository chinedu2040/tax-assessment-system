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
