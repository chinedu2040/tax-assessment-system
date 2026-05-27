import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register DejaVu fonts (include Naira sign U+20A6 and full Unicode)
_DEJAVU_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]
_DEJAVU_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
]

BODY_FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"

for _p in _DEJAVU_PATHS:
    if Path(_p).exists():
        try:
            pdfmetrics.registerFont(TTFont("DejaVuSans", _p))
            BODY_FONT = "DejaVuSans"
        except Exception:
            pass
        break

for _p in _DEJAVU_BOLD_PATHS:
    if Path(_p).exists():
        try:
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", _p))
            BOLD_FONT = "DejaVuSans-Bold"
        except Exception:
            pass
        break

NIGERIAN_GREEN = colors.HexColor("#008751")
LIGHT_GREEN = colors.HexColor("#e8f5e9")
AMBER = colors.HexColor("#fff8e1")
WHITE = colors.white
DARK_GREY = colors.HexColor("#212121")
MID_GREY = colors.HexColor("#757575")


def _fmt_naira(amount: float) -> str:
    # Use ₦ only when a Unicode font is loaded; fall back to NGN to avoid
    # UnicodeEncodeError with Helvetica (Latin-1 encoding).
    symbol = "₦" if BODY_FONT not in ("Helvetica", "Helvetica-Bold") else "NGN "
    return f"{symbol}{amount:,.2f}"


def _fmt_pct(rate: float) -> str:
    return f"{rate:.2f}%"


def generate_report(
    computation: Dict[str, Any],
    transactions: List[Dict[str, Any]],
    user_info: Dict[str, str],
    report_path: str,
) -> str:
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"],
        textColor=WHITE, fontSize=18, alignment=TA_CENTER,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        textColor=WHITE, fontSize=10, alignment=TA_CENTER,
    )
    section_heading = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"],
        textColor=NIGERIAN_GREEN, fontSize=13, spaceBefore=16, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        textColor=DARK_GREY, fontSize=9,
    )
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"],
        textColor=MID_GREY, fontSize=7, alignment=TA_CENTER,
    )

    story = []

    # ── HEADER ──────────────────────────────────────────────────────────────
    header_table = Table(
        [[Paragraph("Secure Tax Self-Assessment System", title_style)],
         [Paragraph("NDPR Compliant | FIRS 2024", subtitle_style)]],
        colWidths=[doc.width],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NIGERIAN_GREEN),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [NIGERIAN_GREEN]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4 * cm))

    meta_data = [
        ["Taxpayer:", user_info.get("full_name", "N/A"),
         "Tax Year:", str(computation.get("tax_year", "N/A"))],
        ["TIN:", user_info.get("tin", "Not Provided"),
         "Generated:", datetime.now().strftime("%d %B %Y")],
    ]
    meta_table = Table(meta_data, colWidths=[3 * cm, 7 * cm, 3 * cm, 4 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), BOLD_FONT),
        ("FONTNAME", (2, 0), (2, -1), BOLD_FONT),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK_GREY),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(HRFlowable(width="100%", thickness=1, color=NIGERIAN_GREEN))
    story.append(Spacer(1, 0.3 * cm))

    # ── TAX SUMMARY TABLE ────────────────────────────────────────────────────
    story.append(Paragraph("Tax Summary", section_heading))

    summary_rows = [
        ["Description", "Amount"],
        ["Gross Income", _fmt_naira(computation["gross_income"])],
        ["Consolidated Relief Allowance (CRA)", _fmt_naira(computation["total_cra"])],
        ["  — CRA Fixed Component", _fmt_naira(computation["cra_fixed"])],
        ["  — CRA 20% of Gross Income", _fmt_naira(computation["cra_percentage"])],
        ["Pension Relief (8%)", _fmt_naira(computation["pension_relief"])],
        ["NHF Relief (2.5%)", _fmt_naira(computation["nhf_relief"])],
        ["NHIS Relief (5%)", _fmt_naira(computation["nhis_relief"])],
        ["Other Allowable Deductions", _fmt_naira(computation["other_deductions"])],
        ["Taxable Income", _fmt_naira(computation["taxable_income"])],
        ["Tax Liability", _fmt_naira(computation["tax_liability"])],
        ["Effective Tax Rate", _fmt_pct(computation["effective_rate"])],
    ]

    summary_table = Table(summary_rows, colWidths=[12 * cm, 5 * cm])
    summary_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NIGERIAN_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREEN]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTNAME", (0, len(summary_rows) - 3), (-1, len(summary_rows) - 1), BOLD_FONT),
        ("BACKGROUND", (0, len(summary_rows) - 2), (-1, len(summary_rows) - 1), LIGHT_GREEN),
    ])
    summary_table.setStyle(summary_style)
    story.append(summary_table)
    story.append(Spacer(1, 0.4 * cm))

    # ── BAND BREAKDOWN TABLE ─────────────────────────────────────────────────
    story.append(Paragraph("Progressive Tax Band Breakdown", section_heading))

    band_rows = [["Band", "Rate", "Taxable Amount", "Tax Amount"]]
    for i, band in enumerate(computation.get("band_breakdown", []), start=1):
        band_rows.append([
            f"Band {i}",
            _fmt_pct(band["rate"] * 100),
            _fmt_naira(band["taxable_amount"]),
            _fmt_naira(band["tax_amount"]),
        ])
    total_tax = sum(b["tax_amount"] for b in computation.get("band_breakdown", []))
    band_rows.append(["TOTAL", "", "", _fmt_naira(total_tax)])

    band_table = Table(band_rows, colWidths=[4 * cm, 3 * cm, 5 * cm, 5 * cm])
    band_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NIGERIAN_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [WHITE, LIGHT_GREEN]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("FONTNAME", (0, -1), (-1, -1), BOLD_FONT),
        ("BACKGROUND", (0, -1), (-1, -1), NIGERIAN_GREEN),
        ("TEXTCOLOR", (0, -1), (-1, -1), WHITE),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(band_table)
    story.append(Spacer(1, 0.4 * cm))

    # ── TRANSACTION LEDGER ───────────────────────────────────────────────────
    story.append(Paragraph("Full Transaction Ledger", section_heading))

    txn_rows = [["Date", "Description", "Amount", "Dir", "Category", "Method", "Conf"]]
    total_credits = 0.0
    total_debits = 0.0

    for t in transactions:
        amt = float(t.get("amount", 0))
        direction = t.get("direction", "")
        if direction == "credit":
            total_credits += amt
        else:
            total_debits += amt
        desc = str(t.get("description", ""))[:40]
        txn_rows.append([
            str(t.get("date", "")),
            desc,
            _fmt_naira(amt),
            direction[:1].upper(),
            str(t.get("category", ""))[:20],
            str(t.get("classification_method", ""))[:6],
            f"{float(t.get('confidence_score', 0)):.2f}",
        ])

    txn_rows.append([
        "TOTALS", "",
        f"C:{_fmt_naira(total_credits)} D:{_fmt_naira(total_debits)}",
        "", "", "", "",
    ])

    col_widths = [2.2 * cm, 5.5 * cm, 3.5 * cm, 1 * cm, 3 * cm, 1.5 * cm, 1.3 * cm]
    txn_table = Table(txn_rows, colWidths=col_widths, repeatRows=1)
    txn_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NIGERIAN_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [WHITE, LIGHT_GREEN]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("FONTNAME", (0, -1), (-1, -1), BOLD_FONT),
        ("BACKGROUND", (0, -1), (-1, -1), NIGERIAN_GREEN),
        ("TEXTCOLOR", (0, -1), (-1, -1), WHITE),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("WORDWRAP", (1, 1), (1, -1), True),
    ]))
    story.append(txn_table)
    story.append(Spacer(1, 0.6 * cm))

    # ── FOOTER ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Generated by Secure Tax Self-Assessment System", footer_style))
    story.append(Paragraph(
        "In compliance with the Nigeria Data Protection Regulation (NDPR)", footer_style
    ))
    story.append(Paragraph("Tax rules sourced from FIRS 2024 guidelines", footer_style))

    doc.build(story)
    return report_path
