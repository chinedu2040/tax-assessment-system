import io
import re
import logging
import zipfile
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from modules.ingestion.normaliser import normalise

logger = logging.getLogger(__name__)

DATE_COLS = ["Trans. Date", "Transaction Date", "Posting Date", "Date", "Txn Date", "BookingDate", "date", "Trans Date", "POSTING DATE", "Value Date"]
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


# ═══════════════════════════════════════════════════════════════════════════
# PDF PARSING — four-strategy pipeline
# ═══════════════════════════════════════════════════════════════════════════

_PDF_HEADER_TOKENS = frozenset({
    'date', 'trans', 'posting', 'value', 'transaction', 'txn',
    'narration', 'description', 'details', 'particulars', 'remarks', 'memo',
    'debit', 'credit', 'withdrawal', 'deposit', 'withdrawals', 'deposits',
    'amount', 'balance', 'dr', 'cr', 'ref', 'reference', 'channel', 'type',
})

_PDF_AMOUNT_RE = re.compile(r'\b[\d,]+\.\d{2}\b')
_PDF_DATE_RE   = re.compile(
    r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}'
    r'|\d{1,2}\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}'
    r'|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{1,2},?\s*\d{4})\b',
    re.IGNORECASE,
)
_PDF_CRDR_RE   = re.compile(r'\b(CR|DR|Cr|Dr)\b')
_PDF_LONGREF   = re.compile(r'\b\d{10,}\b')        # strip 10+ digit reference codes


def _pdf_words_to_rows(words: list, y_tol: float = 4.0) -> list:
    """Group pdfplumber word-objects into rows by Y-coordinate."""
    buckets: Dict[int, list] = {}
    for w in words:
        key = round(w['top'] / y_tol)
        buckets.setdefault(key, []).append(w)
    return [sorted(v, key=lambda w: w['x0']) for _, v in sorted(buckets.items())]


def _pdf_header_score_words(row_words: list) -> int:
    return sum(
        1 for w in row_words
        if re.sub(r'[^a-z]', '', w['text'].lower()) in _PDF_HEADER_TOKENS
    )


def _pdf_header_score_strings(cells: list) -> int:
    return sum(
        1 for c in cells
        if re.sub(r'[^a-z]', '', str(c).lower()) in _PDF_HEADER_TOKENS
    )


def _pdf_build_col_map(header_words: list, merge_gap: float = 20.0) -> dict:
    """
    Build {anchor_x: column_name} merging adjacent words (handles 'Trans. Date').
    """
    if not header_words:
        return {}
    groups, cur = [], [header_words[0]]
    for w in header_words[1:]:
        if w['x0'] - cur[-1]['x1'] <= merge_gap:
            cur.append(w)
        else:
            groups.append(cur)
            cur = [w]
    groups.append(cur)
    return {
        grp[0]['x0']: ' '.join(w['text'] for w in grp).lower().strip('()./\\-:, ')
        for grp in groups
    }


def _pdf_snap(x: float, col_xs: list, tol: float = 45.0):
    if not col_xs:
        return None
    best = min(col_xs, key=lambda cx: abs(cx - x))
    return best if abs(best - x) <= tol else None


def _pdf_norm_row(rec: dict) -> dict:
    """Apply _find_col mapping to a raw row-dict from PDF extraction."""
    cols = list(rec.keys())
    date_col   = _find_col(cols, DATE_COLS)
    desc_col   = _find_col(cols, DESC_COLS)
    debit_col  = _find_col(cols, DEBIT_COLS)
    credit_col = _find_col(cols, CREDIT_COLS)
    amount_col = _find_col(cols, AMOUNT_COLS)

    norm: Dict[str, Any] = {}
    norm['date'] = rec.get(date_col, '') if date_col else ''
    raw_desc = str(rec.get(desc_col, '')).strip() if desc_col else ''
    norm['description'] = raw_desc if raw_desc.lower() not in ('', 'nan', 'none') else ''

    if debit_col or credit_col:
        norm['_debit']  = rec.get(debit_col) if debit_col else None
        norm['_credit'] = rec.get(credit_col) if credit_col else None
    elif amount_col:
        amt_val = rec.get(amount_col, '0')
        # Look for a DR/CR indicator column to determine direction
        crdr_col = next(
            (c for c in cols if c.lower().strip('()/ ') in
             ('dr/cr', 'cr/dr', 'd/c', 'c/d', 'dr', 'cr', 'type', 'indicator', 'flag')),
            None,
        )
        if crdr_col:
            ind = str(rec.get(crdr_col, '')).strip().upper()
            if ind in ('DR', 'D', 'DEBIT', 'WD', 'W/D'):
                norm['_debit'], norm['_credit'] = amt_val, None
            elif ind in ('CR', 'C', 'CREDIT', 'DEP'):
                norm['_debit'], norm['_credit'] = None, amt_val
            else:
                norm['_signed_amount'] = amt_val
        else:
            norm['_signed_amount'] = amt_val
    else:
        norm['amount'] = 0

    return norm


# ── Strategy 1 ─ Table extraction (grid PDFs: Zenith, Access, First Bank) ─

def _parse_pdf_tables(pdf) -> List[Dict[str, Any]]:
    header: list = []
    raw_rows: list = []

    for page in pdf.pages:
        for table in page.extract_tables():
            if not table or len(table) < 2:
                continue
            first_row = [str(c).strip() if c else '' for c in table[0]]
            if not header:
                header   = first_row
                data_rows = table[1:]
            elif _pdf_header_score_strings(first_row) >= 2:
                data_rows = table[1:]           # repeated header on new page — skip it
            else:
                data_rows = table               # no repeated header

            for row in data_rows:
                if not row:
                    continue
                rec = {header[i]: (row[i] or '') for i in range(min(len(header), len(row)))}
                raw_rows.append(rec)

    if not raw_rows:
        return []
    return normalise([_pdf_norm_row(r) for r in raw_rows], 'pdf')


# ── Strategy 2 ─ Coordinate-based word extraction (text PDFs: GTBank pdfkit) ─

def _parse_pdf_by_words(pdf) -> List[Dict[str, Any]]:
    """
    Uses bounding-box word positions to reconstruct columns without needing
    grid lines. Works for GTBank, UBA, FCMB, and most digitally-generated PDFs.
    """
    col_map:     dict = {}
    col_xs:      list = []
    found_header = False
    raw_rows:    list = []

    for page in pdf.pages:
        words = page.extract_words(x_tolerance=3, y_tolerance=3, keep_blank_chars=False)
        if not words:
            continue
        rows = _pdf_words_to_rows(words)

        if not found_header:
            best_score, best_idx = 0, -1
            for i, row in enumerate(rows[:30]):
                s = _pdf_header_score_words(row)
                if s > best_score:
                    best_score, best_idx = s, i
            if best_score < 2 or best_idx < 0:
                continue
            col_map  = _pdf_build_col_map(rows[best_idx])
            col_xs   = sorted(col_map.keys())
            found_header = True
            data_rows = rows[best_idx + 1:]
        else:
            # On subsequent pages, check if the first row is a repeated header
            if rows and _pdf_header_score_words(rows[0]) >= 2:
                data_rows = rows[1:]
            else:
                data_rows = rows

        for row_words in data_rows:
            if len(row_words) < 2:
                continue
            cells: dict = {}
            for w in row_words:
                snap = _pdf_snap(w['x0'], col_xs)
                if snap is not None:
                    cells.setdefault(snap, []).append(w['text'])
            if len(cells) < 2:
                continue
            raw_rows.append({col_map[cx]: ' '.join(ws) for cx, ws in cells.items()})

    if not raw_rows:
        return []
    return normalise([_pdf_norm_row(r) for r in raw_rows], 'pdf')


# ── Strategy 3 ─ Line-by-line text with CR/DR detection ───────────────────

def _parse_pdf_text_lines(pdf) -> List[Dict[str, Any]]:
    """
    Simple line-by-line fallback that detects CR/DR direction markers and
    strips the running balance (last amount on each line) from the transaction
    amount. Works for many Nigerian bank PDF text formats.
    """
    records = []
    for page in pdf.pages:
        text = page.extract_text() or ""
        for line in text.splitlines():
            line = line.strip()
            if not line or len(line) < 8:
                continue
            date_m  = _PDF_DATE_RE.search(line)
            amounts = _PDF_AMOUNT_RE.findall(line)
            if not date_m or not amounts:
                continue

            date_str = date_m.group()
            # Use second-to-last amount (last is usually the running balance)
            txn_amt  = amounts[-2] if len(amounts) >= 2 else amounts[-1]

            # CR/DR direction marker
            crdr_m    = _PDF_CRDR_RE.search(line)
            direction = None
            if crdr_m:
                direction = 'credit' if crdr_m.group().upper() == 'CR' else 'debit'

            # Description = text between date end and first amount
            after_date  = line[date_m.end():]
            first_amt_m = _PDF_AMOUNT_RE.search(after_date)
            desc = (after_date[:first_amt_m.start()] if first_amt_m else after_date).strip()
            desc = _PDF_CRDR_RE.sub('', desc)           # remove CR/DR tokens
            desc = _PDF_LONGREF.sub('', desc)            # remove long ref numbers
            desc = re.sub(r'\s{2,}', ' ', desc).strip()
            if not desc:
                desc = line[:date_m.start()].strip() or line

            rec: Dict[str, Any] = {'date': date_str, 'description': desc}
            if direction == 'debit':
                rec['_debit'], rec['_credit'] = txn_amt, None
            elif direction == 'credit':
                rec['_debit'], rec['_credit'] = None, txn_amt
            else:
                rec['_signed_amount'] = txn_amt

            records.append(rec)

    return normalise(records, 'pdf') if records else []


# ── Strategy 4 ─ Memory-safe OCR (one page at a time) ─────────────────────

def _parse_scanned_pdf_memory_safe(
    file_bytes: bytes, max_pages: int = 20, dpi: int = 150
) -> List[Dict[str, Any]]:
    """
    OCR fallback for scanned/image PDFs. Processes one page at a time and
    limits DPI to stay within Railway free-tier memory (~512 MB).
    200 DPI full-PDF loading is replaced with 150 DPI single-page loop.
    """
    try:
        from pdf2image import convert_from_bytes
        import pytesseract
        import gc

        all_text: list = []
        page_num = 1
        while page_num <= max_pages:
            try:
                images = convert_from_bytes(
                    file_bytes, dpi=dpi,
                    first_page=page_num, last_page=page_num,
                    thread_count=1,
                )
            except Exception:
                break
            if not images:
                break
            all_text.append(pytesseract.image_to_string(images[0]))
            del images
            gc.collect()
            page_num += 1

        if not all_text:
            return []
        records = _parse_ocr_text('\n'.join(all_text))
        return normalise(records, 'scanned')

    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return []


def _parse_ocr_text(text: str) -> List[Dict[str, Any]]:
    date_pat   = re.compile(r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{1,2}\s+\w{3}\s+\d{4})')
    amount_pat = re.compile(r'[\d,]+\.\d{2}')
    records = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        dm = date_pat.search(line)
        am = amount_pat.search(line)
        if dm and am:
            desc = (line[:dm.start()] or line[dm.end():am.start()]).strip() or line
            records.append({'date': dm.group(), 'description': desc, '_signed_amount': am.group()})
    return records


# ── Main PDF entry point ───────────────────────────────────────────────────

def parse_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Multi-strategy PDF parser for Nigerian bank statements.

    1. pdfplumber table extraction — grid PDFs (Zenith Bank, Access Bank, First Bank)
    2. Coordinate word extraction  — text PDFs (GTBank pdfkit, UBA, FCMB, Stanbic)
    3. Line-by-line + CR/DR       — simple text PDFs
    4. Memory-safe OCR (150 DPI, 1 page/loop) — scanned/image PDFs only
    """
    import pdfplumber

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        logger.info(f"PDF parser: {len(pdf.pages)} pages")

        result = _parse_pdf_tables(pdf)
        if result:
            logger.info(f"PDF strategy-1 (tables): {len(result)} transactions")
            return result

        result = _parse_pdf_by_words(pdf)
        if result:
            logger.info(f"PDF strategy-2 (word-coords): {len(result)} transactions")
            return result

        result = _parse_pdf_text_lines(pdf)
        if result:
            logger.info(f"PDF strategy-3 (text-lines): {len(result)} transactions")
            return result

    logger.info("PDF: all pdfplumber strategies empty, trying OCR")
    return _parse_scanned_pdf_memory_safe(file_bytes)


# Keep old name as alias so any external callers still work
parse_scanned_pdf = _parse_scanned_pdf_memory_safe


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
