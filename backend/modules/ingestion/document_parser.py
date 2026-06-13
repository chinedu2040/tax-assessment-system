import io
import re
import logging
import zipfile
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from modules.ingestion.normaliser import normalise

logger = logging.getLogger(__name__)

DATE_COLS = ["Trans. Date", "Transaction Date", "Value Date", "Date", "Txn Date", "BookingDate", "date", "Trans Date"]
DESC_COLS = ["Narration", "Description", "Details", "Remarks", "Transaction Details", "Particulars", "description", "Memo"]
DEBIT_COLS  = ["Debit", "Withdrawals", "Dr", "Debit Amount", "Debit(", "Settlement Debit"]
CREDIT_COLS = ["Credit", "Deposits", "Cr", "Credit Amount", "Credit(", "Settlement Credit"]
AMOUNT_COLS = ["Amount", "amount", "Transaction Amount"]
BALANCE_COLS = ["Balance", "Running Balance", "Ledger Balance", "Balance After"]

# Supplementary columns used for description enrichment when primary narration is blank
_REF_COLS  = ["Transaction Ref", "Reference", "Transaction Reference", "Ref"]
_TYPE_COLS = ["Transaction Type", "Type"]
_BEN_COLS  = ["Beneficiary", "Beneficiary Name"]

ALL_HEADER_CANDIDATES = DATE_COLS + DESC_COLS + DEBIT_COLS + CREDIT_COLS + AMOUNT_COLS


def _repair_xlsx(file_bytes: bytes) -> bytes:
    """Fix xlsx files that have invalid stylesheet XML (e.g. Moniepoint exports).
    Removes the offending vertical-alignment attribute so openpyxl can open them."""
    buf = io.BytesIO()
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes), "r") as zin:
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
                for name in zin.namelist():
                    data = zin.read(name)
                    if name == "xl/styles.xml":
                        xml = data.decode("utf-8", errors="replace")
                        xml = re.sub(r'\bvertical="[^"]*"', "", xml)
                        data = xml.encode("utf-8")
                    zout.writestr(name, data)
    except Exception as e:
        logger.warning(f"xlsx repair failed: {e}")
        return file_bytes
    return buf.getvalue()


def _find_col(df_cols, candidates):
    """Find column by exact match first, then prefix match (handles 'Debit(₦)', 'Settlement Debit (NGN)' etc)."""
    for c in candidates:
        c_lower = c.lower()
        for col in df_cols:
            col_lower = col.strip().lower()
            if col_lower == c_lower or col_lower.startswith(c_lower):
                return col
    return None


def _enrich_description(row, cols: list) -> str:
    """Build a fallback description from supplementary columns when the primary narration is blank."""
    # Check Transaction Ref for known Moniepoint system patterns
    ref_col = _find_col(cols, _REF_COLS)
    if ref_col:
        ref = str(row.get(ref_col, "")).upper()
        if "_EMTL_DC" in ref or ref.startswith("EMTL"):
            return "electronic money transfer levy"
        if "INTR" in ref and "INTEREST" in ref:
            return "savings account interest"
    # Try Beneficiary name
    ben_col = _find_col(cols, _BEN_COLS)
    if ben_col:
        val = str(row.get(ben_col, "")).strip()
        if val and val.lower() not in ("nan", "none", ""):
            return val
    # Try Transaction Type
    type_col = _find_col(cols, _TYPE_COLS)
    if type_col:
        val = str(row.get(type_col, "")).strip()
        if val and val.lower() not in ("nan", "none", ""):
            return val
    return ""


def _find_header_row(df_raw) -> int:
    """Scan first 20 rows to find the actual header row (handles OPay metadata rows)."""
    candidates_lower = [c.lower() for c in ALL_HEADER_CANDIDATES]
    best_row, best_score = 0, 0
    for idx, row in df_raw.iterrows():
        if idx > 20:
            break
        score = 0
        for val in row:
            v = str(val).strip().lower()
            if any(v == c or v.startswith(c) for c in candidates_lower):
                score += 1
        if score > best_score:
            best_score = score
            best_row = idx
    return best_row if best_score >= 2 else 0


def _df_to_raw(df: pd.DataFrame, source_format: str) -> List[Dict[str, Any]]:
    cols = list(df.columns)
    date_col = _find_col(cols, DATE_COLS)
    desc_col = _find_col(cols, DESC_COLS)
    debit_col = _find_col(cols, DEBIT_COLS)
    credit_col = _find_col(cols, CREDIT_COLS)
    amount_col = _find_col(cols, AMOUNT_COLS)

    records = []
    for _, row in df.iterrows():
        rec: Dict[str, Any] = {}
        rec["date"] = row[date_col] if date_col else ""

        raw_desc = str(row[desc_col]).strip() if desc_col else ""
        if raw_desc.lower() in ("", "nan", "none"):
            raw_desc = _enrich_description(row, cols)
        rec["description"] = raw_desc

        if debit_col or credit_col:
            rec["_debit"] = row[debit_col] if debit_col else None
            rec["_credit"] = row[credit_col] if credit_col else None
        elif amount_col:
            rec["_signed_amount"] = row[amount_col]
        else:
            rec["amount"] = 0

        records.append(rec)

    return normalise(records, source_format)


def parse_csv(file_bytes: bytes) -> List[Dict[str, Any]]:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc)
            df.columns = [str(c).strip() for c in df.columns]
            return _df_to_raw(df, "csv")
        except Exception:
            continue
    raise ValueError("Could not parse CSV with any supported encoding")


def _parse_sheet(xf, sheet) -> List[Dict[str, Any]]:
    """Parse a single Excel sheet with smart header row detection."""
    try:
        raw = xf.parse(sheet, header=None)
        header_row = _find_header_row(raw)
        df = xf.parse(sheet, header=header_row)
        df.columns = [str(c).strip() for c in df.columns]
        # Drop rows that are all NaN or all "--"
        df = df.dropna(how="all")
        return _df_to_raw(df, "excel")
    except Exception as e:
        logger.warning(f"Sheet '{sheet}' parse failed: {e}")
        return []


def parse_excel(file_bytes: bytes) -> List[Dict[str, Any]]:
    def _try_parse(data: bytes) -> List[Dict[str, Any]]:
        xf = pd.ExcelFile(io.BytesIO(data))
        all_records: List[Dict[str, Any]] = []
        for sheet in xf.sheet_names:
            records = _parse_sheet(xf, sheet)
            all_records.extend(records)
        return all_records

    try:
        all_records = _try_parse(file_bytes)
    except Exception as e:
        logger.warning(f"Excel parse failed ({e}), attempting stylesheet repair…")
        repaired = _repair_xlsx(file_bytes)
        try:
            all_records = _try_parse(repaired)
        except Exception as e2:
            raise ValueError(f"Could not parse Excel file after repair: {e2}") from e2

    if not all_records:
        raise ValueError("Could not find any transactions in Excel file")
    return all_records


def _pdf_text_fallback(file_bytes: bytes) -> List[Dict[str, Any]]:
    """Extract transactions from PDFs with no grid lines (e.g. pdfkit output)."""
    import pdfplumber
    date_re = re.compile(
        r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}"
        r"|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}"
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b",
        re.IGNORECASE,
    )
    amount_re = re.compile(r"[\d,]+\.\d{2}")
    records = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                d = date_re.search(line)
                amounts = amount_re.findall(line)
                if d and amounts:
                    date_str = d.group()
                    desc_part = line[d.end():].strip()
                    # Remove all amounts from description
                    for a in amounts:
                        desc_part = desc_part.replace(a, "").strip()
                    desc_part = re.sub(r"\s{2,}", " ", desc_part).strip() or line
                    records.append({
                        "date": date_str,
                        "description": desc_part,
                        "_signed_amount": amounts[0],
                    })
    return records


def parse_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    import pdfplumber

    records = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                header = [str(c).strip() if c else "" for c in table[0]]
                for row in table[1:]:
                    if not row:
                        continue
                    rec = {}
                    for i, val in enumerate(row):
                        if i < len(header):
                            rec[header[i]] = val
                    records.append(rec)

    if not records:
        # Try line-by-line text extraction before OCR (handles pdfkit/non-grid PDFs)
        text_records = _pdf_text_fallback(file_bytes)
        if text_records:
            return normalise(text_records, "pdf")
        return parse_scanned_pdf(file_bytes)

    normalized_records = []
    for rec in records:
        cols = list(rec.keys())
        date_col = _find_col(cols, DATE_COLS)
        desc_col = _find_col(cols, DESC_COLS)
        debit_col = _find_col(cols, DEBIT_COLS)
        credit_col = _find_col(cols, CREDIT_COLS)
        amount_col = _find_col(cols, AMOUNT_COLS)

        norm_rec: Dict[str, Any] = {}
        norm_rec["date"] = rec.get(date_col, "") if date_col else ""
        norm_rec["description"] = rec.get(desc_col, "") if desc_col else ""

        if debit_col or credit_col:
            norm_rec["_debit"] = rec.get(debit_col) if debit_col else None
            norm_rec["_credit"] = rec.get(credit_col) if credit_col else None
        elif amount_col:
            norm_rec["_signed_amount"] = rec.get(amount_col)
        else:
            norm_rec["amount"] = 0

        normalized_records.append(norm_rec)

    return normalise(normalized_records, "pdf")


def parse_scanned_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    try:
        from pdf2image import convert_from_bytes
        import pytesseract

        images = convert_from_bytes(file_bytes, dpi=200)
        all_text = []
        for img in images:
            text = pytesseract.image_to_string(img)
            all_text.append(text)

        full_text = "\n".join(all_text)
        records = _parse_ocr_text(full_text)
        return normalise(records, "scanned")
    except Exception as e:
        logger.error(f"OCR parsing failed: {e}")
        return []


def _parse_ocr_text(text: str) -> List[Dict[str, Any]]:
    date_pattern = re.compile(
        r"(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{1,2}\s+\w{3}\s+\d{4})"
    )
    amount_pattern = re.compile(r"[\d,]+\.\d{2}")

    lines = text.split("\n")
    records = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        date_match = date_pattern.search(line)
        amount_match = amount_pattern.search(line)
        if date_match and amount_match:
            date_str = date_match.group()
            amount_str = amount_match.group()
            desc = line[:date_match.start()].strip() or line[date_match.end():amount_match.start()].strip()
            if not desc:
                desc = line
            records.append({
                "date": date_str,
                "description": desc,
                "_signed_amount": amount_str,
            })
    return records


def parse_document(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    ext = Path(filename).suffix.lower()
    if ext == ".csv":
        return parse_csv(file_bytes)
    elif ext in (".xlsx", ".xls"):
        return parse_excel(file_bytes)
    elif ext == ".pdf":
        return parse_pdf(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
