import re
from datetime import datetime
from typing import List, Dict, Any


DATE_FORMATS = [
    "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d",
    "%d-%m-%Y", "%Y/%m/%d",
    "%d %b %Y", "%d-%b-%Y", "%d-%b-%y",
    "%d.%m.%Y", "%Y.%m.%d",
    "%b %d, %Y", "%d %B %Y",
]


def _parse_date(raw: str) -> str:
    if not raw:
        return ""
    raw = str(raw).strip()
    # Handle pandas Timestamp
    if hasattr(raw, "strftime"):
        return raw.strftime("%Y-%m-%d")
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # Try ISO-style truncation
    try:
        return datetime.fromisoformat(raw[:10]).strftime("%Y-%m-%d")
    except Exception:
        return raw


def _clean_amount(raw: Any) -> float:
    if raw is None or (isinstance(raw, float) and str(raw) == "nan"):
        return 0.0
    s = str(raw).strip()
    s = re.sub(r"[₦NGN\$,\s]", "", s)
    s = re.sub(r"[^\d.\-]", "", s)
    if not s or s in (".", "-"):
        return 0.0
    try:
        return abs(float(s))
    except ValueError:
        return 0.0


def _clean_description(raw: str) -> str:
    if not raw:
        return ""
    cleaned = str(raw).strip()
    cleaned = re.sub(r"[^\w\s\-/]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _derive_direction(row: Dict[str, Any]) -> str:
    if row.get("_debit") and _clean_amount(row["_debit"]) > 0:
        return "debit"
    if row.get("_credit") and _clean_amount(row["_credit"]) > 0:
        return "credit"
    if row.get("_signed_amount") is not None:
        try:
            val = float(str(row["_signed_amount"]).replace(",", ""))
            return "debit" if val < 0 else "credit"
        except ValueError:
            pass
    desc = str(row.get("description", "")).lower()
    debit_keywords = ["withdrawal", "debit", "pos", "payment", "transfer to", "trf to"]
    if any(kw in desc for kw in debit_keywords):
        return "debit"
    return "credit"


def normalise(raw_records: List[Dict[str, Any]], source_format: str) -> List[Dict[str, Any]]:
    seen = set()
    result = []

    for rec in raw_records:
        date_str = _parse_date(rec.get("date", ""))
        raw_desc = str(rec.get("description", "")).strip()
        description = _clean_description(raw_desc)

        if rec.get("_signed_amount") is not None:
            amount = _clean_amount(rec["_signed_amount"])
        elif rec.get("_debit") and _clean_amount(rec["_debit"]) > 0:
            amount = _clean_amount(rec["_debit"])
        elif rec.get("_credit") and _clean_amount(rec["_credit"]) > 0:
            amount = _clean_amount(rec["_credit"])
        else:
            amount = _clean_amount(rec.get("amount", 0))

        if amount == 0:
            continue

        direction = _derive_direction(rec)

        dedup_key = (date_str, description.lower(), amount)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        result.append({
            "date": date_str,
            "description": description,
            "amount": amount,
            "direction": direction,
            "raw_description": raw_desc,
            "source_format": source_format,
        })

    return result
