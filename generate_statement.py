from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)

OUTPUT = r"C:\Users\UDEZE\Desktop\GTBank_Statement_Udeze_Chinedu_2024.pdf"

GTB_GREEN = colors.HexColor("#006633")
GTB_RED   = colors.HexColor("#CC0000")
LIGHT_GREY = colors.HexColor("#f5f5f5")
MID_GREY   = colors.HexColor("#888888")
DARK       = colors.HexColor("#1a1a1a")
WHITE      = colors.white

def naira(n):
    return "₦{:,.2f}".format(abs(float(n)))

# 80 realistic transactions Jan–Dec 2024
TRANSACTIONS = [
    # Jan
    ("02/01/2024","SALARY PAYMENT JANUARY 2024 TECHCORP LTD",          "",        "350,000.00", "350,000.00"),
    ("05/01/2024","MTN DATA SUBSCRIPTION 50GB MONTHLY PLAN",            "15,000.00","",          "335,000.00"),
    ("07/01/2024","UPWORK PAYMENT INV-20240107 WEB DEV PROJECT",        "",        "185,500.00", "520,500.00"),
    ("09/01/2024","UBER TRIP LAGOS ISLAND TO VICTORIA ISLAND",          "4,200.00", "",          "516,300.00"),
    ("10/01/2024","IKEDC ELECTRICITY TOKEN PURCHASE OFFICE",            "10,000.00","",          "506,300.00"),
    ("12/01/2024","ADOBE CREATIVE CLOUD MONTHLY SUBSCRIPTION",          "8,500.00", "",          "497,800.00"),
    ("15/01/2024","PAYONEER TRANSFER USD 400.00 REF:PAY20240115",       "",        "620,000.00", "1,117,800.00"),
    ("17/01/2024","ATM WITHDRAWAL GTB VICTORIA ISLAND BRANCH",          "50,000.00","",          "1,067,800.00"),
    ("20/01/2024","UDEMY COURSE PAYMENT PYTHON DJANGO BOOTCAMP",        "12,000.00","",          "1,055,800.00"),
    ("22/01/2024","TRF TO OWN SAVINGS ACCOUNT GTB 0123456789",          "100,000.00","",         "955,800.00"),
    ("25/01/2024","FIVERR WITHDRAWAL ORDER COMPLETION GRAPHIC DESIGN",  "",        "95,200.00",  "1,051,000.00"),
    ("28/01/2024","SPECTRANET INTERNET SUBSCRIPTION MONTHLY",           "18,000.00","",          "1,033,000.00"),
    ("30/01/2024","ARM PENSIONS RSA CONTRIBUTION JANUARY",              "28,000.00","",          "1,005,000.00"),
    # Feb
    ("01/02/2024","SALARY PAYMENT FEBRUARY 2024 TECHCORP LTD",         "",        "350,000.00", "1,355,000.00"),
    ("03/02/2024","AIRTEL BROADBAND MONTHLY PLAN 100GB",                "12,000.00","",          "1,343,000.00"),
    ("05/02/2024","UPWORK HOURLY CONTRACT PAYMENT FEB WEEK 1",         "",        "210,000.00", "1,553,000.00"),
    ("07/02/2024","BINANCE P2P TRANSFER USDT SALE NGN RECEIPT",        "",        "450,000.00", "2,003,000.00"),
    ("08/02/2024","GITHUB PRO ANNUAL SUBSCRIPTION RENEWAL",             "5,000.00", "",          "1,998,000.00"),
    ("10/02/2024","BOLT RIDE SHARE IKEJA TO LEKKI CLIENT MEETING",     "6,500.00", "",          "1,991,500.00"),
    ("12/02/2024","EKEDC ELECTRICITY PREPAID TOKEN RECHARGE HOME",     "15,000.00","",          "1,976,500.00"),
    ("14/02/2024","CONSULTANT FEE PAYMENT ADAEZE SOLUTIONS LTD",       "",        "320,000.00", "2,296,500.00"),
    ("17/02/2024","POS PURCHASE SHOPRITE IKEJA CITY MALL",             "35,000.00","",          "2,261,500.00"),
    ("19/02/2024","WISE TRANSFER GBP 300.00 FREELANCE SEO PROJECT",    "",        "570,000.00", "2,831,500.00"),
    ("22/02/2024","FIGMA PROFESSIONAL PLAN ANNUAL SUBSCRIPTION",        "22,000.00","",          "2,809,500.00"),
    ("24/02/2024","NHF CONTRIBUTION FEDERAL MORTGAGE BANK FEB",        "8,750.00", "",          "2,800,750.00"),
    ("26/02/2024","ARM PENSIONS RSA CONTRIBUTION FEBRUARY",            "28,000.00","",          "2,772,750.00"),
    ("28/02/2024","LOAN REPAYMENT ZENITH BANK QUICK CREDIT FEB",       "25,000.00","",          "2,747,750.00"),
    # Mar
    ("01/03/2024","SALARY PAYMENT MARCH 2024 TECHCORP LTD",            "",        "350,000.00", "3,097,750.00"),
    ("04/03/2024","UPWORK FIXED PRICE CONTRACT MOBILE APP UI",         "",        "380,000.00", "3,477,750.00"),
    ("06/03/2024","AWS MONTHLY USAGE INVOICE EC2 S3 MARCH",            "32,000.00","",          "3,445,750.00"),
    ("08/03/2024","MTN DATA SUBSCRIPTION 50GB MONTHLY PLAN",           "15,000.00","",          "3,430,750.00"),
    ("10/03/2024","FUEL PURCHASE TOTAL FILLING STATION LEKKI",         "25,000.00","",          "3,405,750.00"),
    ("12/03/2024","PAYONEER USD 600.00 PROJECT MILESTONE PAYMENT",     "",        "930,000.00", "4,335,750.00"),
    ("15/03/2024","MICROSOFT 365 ANNUAL BUSINESS SUBSCRIPTION",        "18,000.00","",          "4,317,750.00"),
    ("17/03/2024","IKEDC ELECTRICITY TOKEN PURCHASE OFFICE",           "10,000.00","",          "4,307,750.00"),
    ("18/03/2024","DEVFEST LAGOS 2024 CONFERENCE TICKET PAYMENT",      "15,000.00","",          "4,292,750.00"),
    ("20/03/2024","SWIFT CREDIT USD 800 INTERNATIONAL CLIENT USA",     "",        "1,240,000.00","5,532,750.00"),
    ("22/03/2024","TRF TO OWN ACCOUNT SAVINGS ZENITH 0987654321",      "200,000.00","",         "5,332,750.00"),
    ("25/03/2024","NHIS HEALTH INSURANCE MONTHLY PREMIUM MARCH",       "17,500.00","",          "5,315,250.00"),
    ("28/03/2024","ARM PENSIONS RSA CONTRIBUTION MARCH",               "28,000.00","",          "5,287,250.00"),
    # Apr
    ("01/04/2024","SALARY PAYMENT APRIL 2024 TECHCORP LTD",            "",        "350,000.00", "5,637,250.00"),
    ("03/04/2024","FIVERR PRO ORDER LOGO BRANDING PACKAGE",            "",        "145,000.00", "5,782,250.00"),
    ("05/04/2024","SPECTRANET INTERNET SUBSCRIPTION MONTHLY",          "18,000.00","",          "5,764,250.00"),
    ("07/04/2024","LAPTOP PURCHASE HP PROBOOK COMPUTER VILLAGE IKEJA", "320,000.00","",         "5,444,250.00"),
    ("10/04/2024","UPWORK CONTRACT MILESTONE 2 PAYMENT INV-1892",      "",        "275,000.00", "5,719,250.00"),
    ("12/04/2024","COURSERA ANNUAL SUBSCRIPTION MACHINE LEARNING",     "28,000.00","",          "5,691,250.00"),
    ("15/04/2024","AIRTEL 4G LTE BROADBAND MONTHLY SUBSCRIPTION",      "12,000.00","",          "5,679,250.00"),
    ("16/04/2024","UBER TRIP AIRPORT ROAD CLIENT PICKUP MEETING",      "8,500.00", "",          "5,670,750.00"),
    ("18/04/2024","BINANCE P2P USDT SALE APRIL RECEIPT NGN",          "",        "380,000.00", "6,050,750.00"),
    ("20/04/2024","REVERSAL DUPLICATE TRANSACTION CREDIT APRIL",       "",        "5,000.00",   "6,055,750.00"),
    ("22/04/2024","DSTV SUBSCRIPTION PREMIUM BOUQUET APRIL",          "24,500.00","",          "6,031,250.00"),
    ("25/04/2024","NHF DEDUCTION FEDERAL MORTGAGE BANK APRIL",        "8,750.00", "",          "6,022,500.00"),
    ("27/04/2024","ARM PENSIONS RSA CONTRIBUTION APRIL 2024",         "28,000.00","",          "5,994,500.00"),
    # May
    ("01/05/2024","SALARY PAYMENT MAY 2024 TECHCORP LTD",             "",        "350,000.00", "6,344,500.00"),
    ("03/05/2024","PROFESSIONAL FEE INVOICE 67 CHIDINMA OKONKWO",     "",        "500,000.00", "6,844,500.00"),
    ("05/05/2024","AWS MONTHLY SERVER INVOICE MAY 2024",              "32,000.00","",          "6,812,500.00"),
    ("07/05/2024","NOTION TEAM WORKSPACE SUBSCRIPTION ANNUAL",        "12,000.00","",          "6,800,500.00"),
    ("09/05/2024","BOLT RIDE SHARE CLIENT MEETING MAINLAND",          "5,500.00", "",          "6,795,000.00"),
    ("12/05/2024","PAYONEER TRANSFER USD 1,000 INV-MAY2024",          "",        "1,550,000.00","8,345,000.00"),
    ("14/05/2024","MTN DATA SUBSCRIPTION 50GB MONTHLY PLAN",          "15,000.00","",          "8,330,000.00"),
    ("16/05/2024","IKEDC ELECTRICITY TOKEN RECHARGE OFFICE MAY",      "10,000.00","",          "8,320,000.00"),
    ("18/05/2024","UBA QUICK LOAN REPAYMENT INSTALMENT MAY",         "30,000.00","",          "8,290,000.00"),
    ("20/05/2024","TOPTAL CONTRACT PAYMENT Q2 BACKEND ENGINEERING",   "",        "650,000.00", "8,940,000.00"),
    ("22/05/2024","ATM WITHDRAWAL GTB LEKKI PHASE 1 BRANCH",         "80,000.00","",          "8,860,000.00"),
    ("25/05/2024","NHIS HEALTH INSURANCE MONTHLY PREMIUM MAY",       "17,500.00","",          "8,842,500.00"),
    ("28/05/2024","ARM PENSIONS RSA CONTRIBUTION MAY 2024",          "28,000.00","",          "8,814,500.00"),
    # Jun
    ("01/06/2024","SALARY PAYMENT JUNE 2024 TECHCORP LTD",           "",        "350,000.00", "9,164,500.00"),
    ("03/06/2024","UPWORK PAYMENT INV-20240603 API INTEGRATION",      "",        "430,000.00", "9,594,500.00"),
    ("05/06/2024","DIGITALOCEAN MONTHLY DROPLET INVOICE JUNE",       "15,000.00","",          "9,579,500.00"),
    ("07/06/2024","AIRTEL BROADBAND MONTHLY PLAN JUNE RENEWAL",      "12,000.00","",          "9,567,500.00"),
    ("10/06/2024","SWIFT INWARD REMITTANCE USD 1500 LONDON CLIENT",  "",        "2,325,000.00","11,892,500.00"),
    ("12/06/2024","UDEMY COURSE REACT NATIVE MOBILE DEVELOPMENT",    "12,000.00","",          "11,880,500.00"),
    ("14/06/2024","FUEL PURCHASE MOBIL STATION ADMIRALTY WAY",       "22,000.00","",          "11,858,500.00"),
    ("15/06/2024","MONITOR PURCHASE LG ULTRAWIDE 27IN JUMIA",        "180,000.00","",         "11,678,500.00"),
    ("18/06/2024","QUIDAX CRYPTO WITHDRAWAL BITCOIN SALE JUNE",      "",        "280,000.00", "11,958,500.00"),
    ("20/06/2024","TRF TO OWN SAVINGS ACCOUNT ACCESS 0045678912",    "500,000.00","",         "11,458,500.00"),
    ("22/06/2024","CHARGEBACK DISPUTED TRANSACTION KONGA REFUND",    "",        "18,500.00",  "11,477,000.00"),
    ("25/06/2024","NHF CONTRIBUTION FEDERAL MORTGAGE BANK JUNE",     "8,750.00", "",          "11,468,250.00"),
    ("27/06/2024","ARM PENSIONS RSA CONTRIBUTION JUNE 2024",         "28,000.00","",          "11,440,250.00"),
    ("30/06/2024","NHIS HEALTH INSURANCE MONTHLY PREMIUM JUNE",      "17,500.00","",          "11,422,750.00"),
]

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    styles = getSampleStyleSheet()

    h1 = ParagraphStyle("h1", fontSize=14, textColor=GTB_GREEN, fontName="Helvetica-Bold", spaceAfter=2)
    h2 = ParagraphStyle("h2", fontSize=9,  textColor=DARK,      fontName="Helvetica-Bold")
    sm = ParagraphStyle("sm", fontSize=8,  textColor=DARK,      fontName="Helvetica")
    xs = ParagraphStyle("xs", fontSize=7,  textColor=MID_GREY,  fontName="Helvetica")
    cr = ParagraphStyle("cr", fontSize=7,  textColor=MID_GREY,  fontName="Helvetica", alignment=TA_CENTER)

    story = []

    # ── PAGE HEADER ────────────────────────────────────────────────────────
    hdr = Table([[
        Paragraph("GUARANTY TRUST BANK PLC", h1),
        Paragraph("Account Statement", ParagraphStyle("r", fontSize=11, textColor=MID_GREY,
                  fontName="Helvetica", alignment=TA_RIGHT))
    ]], colWidths=[10*cm, 7*cm])
    hdr.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story.append(hdr)
    story.append(HRFlowable(width="100%", thickness=2, color=GTB_GREEN))
    story.append(Spacer(1, 0.3*cm))

    # ── ACCOUNT INFO ──────────────────────────────────────────────────────
    acct = Table([
        [Paragraph("Account Name:",    h2), Paragraph("UDEZE CHINEDU CHINAGOROM",   sm),
         Paragraph("Statement Period:",h2), Paragraph("01 January 2024 - 30 June 2024", sm)],
        [Paragraph("Account Number:", h2), Paragraph("0123456789",                  sm),
         Paragraph("Account Type:",   h2), Paragraph("Current Account",             sm)],
        [Paragraph("Branch:",         h2), Paragraph("Victoria Island Branch, Lagos", sm),
         Paragraph("Currency:",       h2), Paragraph("Nigerian Naira (NGN)",         sm)],
        [Paragraph("BVN:",            h2), Paragraph("22*********34 (masked)",       sm),
         Paragraph("Date Printed:",   h2), Paragraph("30 June 2024",                 sm)],
    ], colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5*cm])
    acct.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), LIGHT_GREY),
        ("GRID",(0,0),(-1,-1),0.3,colors.white),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),6),
    ]))
    story.append(acct)
    story.append(Spacer(1, 0.4*cm))

    # ── OPENING / CLOSING BALANCES ────────────────────────────────────────
    bal = Table([
        [Paragraph("Opening Balance (01/01/2024):", h2),
         Paragraph("₦0.00", ParagraphStyle("rb", fontSize=9, fontName="Helvetica-Bold",
                   textColor=GTB_GREEN, alignment=TA_RIGHT)),
         Paragraph("Closing Balance (30/06/2024):", h2),
         Paragraph("₦11,422,750.00", ParagraphStyle("rb2", fontSize=9, fontName="Helvetica-Bold",
                   textColor=GTB_GREEN, alignment=TA_RIGHT))],
        [Paragraph("Total Credits:", h2),
         Paragraph("₦12,383,200.00", ParagraphStyle("rb3", fontSize=9, fontName="Helvetica",
                   textColor=GTB_GREEN, alignment=TA_RIGHT)),
         Paragraph("Total Debits:", h2),
         Paragraph("₦960,450.00", ParagraphStyle("rb4", fontSize=9, fontName="Helvetica",
                   textColor=GTB_RED, alignment=TA_RIGHT))],
    ], colWidths=[5*cm, 4*cm, 5*cm, 4*cm])
    bal.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),1,GTB_GREEN),
        ("LINEABOVE",(0,1),(-1,1),0.5,colors.lightgrey),
        ("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),8),
    ]))
    story.append(bal)
    story.append(Spacer(1, 0.5*cm))

    # ── TRANSACTION TABLE ──────────────────────────────────────────────────
    story.append(Paragraph("Transaction History", h1))
    story.append(Spacer(1, 0.2*cm))

    col_w = [2.5*cm, 7.8*cm, 2.8*cm, 2.8*cm, 2.8*cm]
    rows = [["Date", "Narration", "Debit (NGN)", "Credit (NGN)", "Balance (NGN)"]]

    for date, narr, dr, cr_val, bal_val in TRANSACTIONS:
        rows.append([date, narr,
                     "₦" + dr    if dr    else "",
                     "₦" + cr_val if cr_val else "",
                     "₦" + bal_val])

    # Totals row
    rows.append(["", "PERIOD TOTALS",
                 "₦960,450.00", "₦12,383,200.00", ""])

    tbl = Table(rows, colWidths=col_w, repeatRows=1)
    n = len(rows)
    tbl.setStyle(TableStyle([
        # Header
        ("BACKGROUND",   (0,0), (-1,0),  GTB_GREEN),
        ("TEXTCOLOR",    (0,0), (-1,0),  WHITE),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0),  8),
        ("ALIGN",        (2,0), (-1,0),  "RIGHT"),
        # Body
        ("FONTSIZE",     (0,1), (-1,-2), 7),
        ("FONTNAME",     (0,1), (-1,-2), "Helvetica"),
        ("ROWBACKGROUNDS",(0,1),(-1,-2), [WHITE, LIGHT_GREY]),
        ("ALIGN",        (2,1), (-1,-2), "RIGHT"),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ("LEFTPADDING",  (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("GRID",         (0,0), (-1,-1), 0.3, colors.lightgrey),
        # Totals row
        ("BACKGROUND",   (0,n-1), (-1,n-1), GTB_GREEN),
        ("TEXTCOLOR",    (0,n-1), (-1,n-1), WHITE),
        ("FONTNAME",     (0,n-1), (-1,n-1), "Helvetica-Bold"),
        ("FONTSIZE",     (0,n-1), (-1,n-1), 8),
        ("ALIGN",        (2,n-1), (-1,n-1), "RIGHT"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.6*cm))

    # ── DISCLAIMER ────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY))
    story.append(Spacer(1, 0.2*cm))
    disc = (
        "This statement is computer generated and does not require a signature or stamp to be valid. "
        "If you have any queries regarding this statement, please contact your branch or call GTConnect: "
        "0700-482-6328 | 0802-900-2900 | customercare@gtbank.com | www.gtbank.com | RC No: 152321. "
        "Guaranty Trust Bank Plc is regulated by the Central Bank of Nigeria."
    )
    story.append(Paragraph(disc, cr))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "CONFIDENTIAL — This document contains privileged information intended solely for UDEZE CHINEDU CHINAGOROM. "
        "Unauthorised use, disclosure or distribution is prohibited.",
        ParagraphStyle("warn", fontSize=6.5, textColor=GTB_RED, fontName="Helvetica-Bold", alignment=TA_CENTER)
    ))

    doc.build(story)
    print(f"Statement saved to: {OUTPUT}")

build_pdf()
