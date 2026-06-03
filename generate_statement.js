const PDFDocument = require('pdfkit');
const fs = require('fs');
const path = require('path');

const OUTPUT = path.join('C:\\Users\\UDEZE\\Desktop', 'GTBank_Statement_Udeze_Chinedu_2024.pdf');

const GTB_GREEN = '#006633';
const GTB_RED   = '#CC0000';
const MID_GREY  = '#888888';
const LIGHT_BG  = '#f7f7f7';
const DARK      = '#1a1a1a';

function naira(s) {
  return '₦' + s;
}

const TRANSACTIONS = [
  // Jan 2024
  ["02/01/2024","SALARY PAYMENT JANUARY 2024 TECHCORP LTD",                   "",             "350,000.00",    "350,000.00"],
  ["05/01/2024","MTN DATA SUBSCRIPTION 50GB MONTHLY PLAN",                    "15,000.00",    "",              "335,000.00"],
  ["07/01/2024","UPWORK PAYMENT INV-20240107 WEB DEVELOPMENT PROJECT",         "",             "185,500.00",    "520,500.00"],
  ["09/01/2024","UBER TRIP LAGOS ISLAND TO VICTORIA ISLAND CLIENT",            "4,200.00",     "",              "516,300.00"],
  ["10/01/2024","IKEDC ELECTRICITY TOKEN PURCHASE OFFICE USE",                 "10,000.00",    "",              "506,300.00"],
  ["12/01/2024","ADOBE CREATIVE CLOUD MONTHLY SUBSCRIPTION",                   "8,500.00",     "",              "497,800.00"],
  ["15/01/2024","PAYONEER TRANSFER USD 400.00 REF:PAY20240115",                "",             "620,000.00",    "1,117,800.00"],
  ["17/01/2024","ATM WITHDRAWAL GTB VICTORIA ISLAND BRANCH",                   "50,000.00",    "",              "1,067,800.00"],
  ["20/01/2024","UDEMY COURSE PAYMENT PYTHON DJANGO BOOTCAMP",                 "12,000.00",    "",              "1,055,800.00"],
  ["22/01/2024","TRF TO OWN SAVINGS ACCOUNT GTB 0123456789",                  "100,000.00",   "",              "955,800.00"],
  ["25/01/2024","FIVERR WITHDRAWAL ORDER COMPLETION GRAPHIC DESIGN",           "",             "95,200.00",     "1,051,000.00"],
  ["28/01/2024","SPECTRANET INTERNET SUBSCRIPTION MONTHLY PLAN",               "18,000.00",    "",              "1,033,000.00"],
  ["30/01/2024","ARM PENSIONS RSA CONTRIBUTION JANUARY 2024",                  "28,000.00",    "",              "1,005,000.00"],
  // Feb 2024
  ["01/02/2024","SALARY PAYMENT FEBRUARY 2024 TECHCORP LTD",                  "",             "350,000.00",    "1,355,000.00"],
  ["03/02/2024","AIRTEL BROADBAND MONTHLY PLAN 100GB RENEWAL",                 "12,000.00",    "",              "1,343,000.00"],
  ["05/02/2024","UPWORK HOURLY CONTRACT PAYMENT FEB WEEK 1",                   "",             "210,000.00",    "1,553,000.00"],
  ["07/02/2024","BINANCE P2P TRANSFER USDT SALE NGN RECEIPT",                  "",             "450,000.00",    "2,003,000.00"],
  ["08/02/2024","GITHUB PRO ANNUAL SUBSCRIPTION RENEWAL",                      "5,000.00",     "",              "1,998,000.00"],
  ["10/02/2024","BOLT RIDE SHARE IKEJA TO LEKKI CLIENT MEETING",               "6,500.00",     "",              "1,991,500.00"],
  ["12/02/2024","EKEDC ELECTRICITY PREPAID TOKEN RECHARGE HOME",               "15,000.00",    "",              "1,976,500.00"],
  ["14/02/2024","CONSULTANCY FEE PAYMENT ADAEZE SOLUTIONS LTD",                "",             "320,000.00",    "2,296,500.00"],
  ["17/02/2024","POS PURCHASE SHOPRITE IKEJA CITY MALL",                       "35,000.00",    "",              "2,261,500.00"],
  ["19/02/2024","WISE TRANSFER GBP 300.00 FREELANCE SEO PROJECT",              "",             "570,000.00",    "2,831,500.00"],
  ["22/02/2024","FIGMA PROFESSIONAL PLAN ANNUAL SUBSCRIPTION",                 "22,000.00",    "",              "2,809,500.00"],
  ["24/02/2024","NHF CONTRIBUTION FEDERAL MORTGAGE BANK FEB",                  "8,750.00",     "",              "2,800,750.00"],
  ["26/02/2024","ARM PENSIONS RSA CONTRIBUTION FEBRUARY 2024",                 "28,000.00",    "",              "2,772,750.00"],
  ["28/02/2024","LOAN REPAYMENT ZENITH BANK QUICK CREDIT FEB",                 "25,000.00",    "",              "2,747,750.00"],
  // Mar 2024
  ["01/03/2024","SALARY PAYMENT MARCH 2024 TECHCORP LTD",                     "",             "350,000.00",    "3,097,750.00"],
  ["04/03/2024","UPWORK FIXED PRICE CONTRACT MOBILE APP UI DESIGN",            "",             "380,000.00",    "3,477,750.00"],
  ["06/03/2024","AWS MONTHLY USAGE INVOICE EC2 S3 MARCH 2024",                 "32,000.00",    "",              "3,445,750.00"],
  ["08/03/2024","MTN DATA SUBSCRIPTION 50GB MONTHLY PLAN",                     "15,000.00",    "",              "3,430,750.00"],
  ["10/03/2024","FUEL PURCHASE TOTAL FILLING STATION LEKKI",                   "25,000.00",    "",              "3,405,750.00"],
  ["12/03/2024","PAYONEER USD 600.00 PROJECT MILESTONE PAYMENT",               "",             "930,000.00",    "4,335,750.00"],
  ["15/03/2024","MICROSOFT 365 ANNUAL BUSINESS SUBSCRIPTION",                  "18,000.00",    "",              "4,317,750.00"],
  ["17/03/2024","IKEDC ELECTRICITY TOKEN PURCHASE OFFICE",                     "10,000.00",    "",              "4,307,750.00"],
  ["18/03/2024","DEVFEST LAGOS 2024 CONFERENCE TICKET PAYMENT",                "15,000.00",    "",              "4,292,750.00"],
  ["20/03/2024","SWIFT CREDIT USD 800 INTERNATIONAL CLIENT USA",               "",             "1,240,000.00",  "5,532,750.00"],
  ["22/03/2024","TRF TO OWN ACCOUNT SAVINGS ZENITH 0987654321",                "200,000.00",   "",              "5,332,750.00"],
  ["25/03/2024","NHIS HEALTH INSURANCE MONTHLY PREMIUM MARCH",                 "17,500.00",    "",              "5,315,250.00"],
  ["28/03/2024","ARM PENSIONS RSA CONTRIBUTION MARCH 2024",                    "28,000.00",    "",              "5,287,250.00"],
  // Apr 2024
  ["01/04/2024","SALARY PAYMENT APRIL 2024 TECHCORP LTD",                     "",             "350,000.00",    "5,637,250.00"],
  ["03/04/2024","FIVERR PRO ORDER LOGO BRANDING PACKAGE",                      "",             "145,000.00",    "5,782,250.00"],
  ["05/04/2024","SPECTRANET INTERNET SUBSCRIPTION MONTHLY PLAN",               "18,000.00",    "",              "5,764,250.00"],
  ["07/04/2024","LAPTOP PURCHASE HP PROBOOK COMPUTER VILLAGE IKEJA",           "320,000.00",   "",              "5,444,250.00"],
  ["10/04/2024","UPWORK CONTRACT MILESTONE 2 PAYMENT INV-1892",                "",             "275,000.00",    "5,719,250.00"],
  ["12/04/2024","COURSERA ANNUAL SUBSCRIPTION MACHINE LEARNING",               "28,000.00",    "",              "5,691,250.00"],
  ["15/04/2024","AIRTEL 4G LTE BROADBAND MONTHLY SUBSCRIPTION",                "12,000.00",    "",              "5,679,250.00"],
  ["16/04/2024","UBER TRIP AIRPORT ROAD CLIENT PICKUP MEETING",                "8,500.00",     "",              "5,670,750.00"],
  ["18/04/2024","BINANCE P2P USDT SALE APRIL RECEIPT NGN",                     "",             "380,000.00",    "6,050,750.00"],
  ["20/04/2024","REVERSAL DUPLICATE TRANSACTION CREDIT APRIL",                 "",             "5,000.00",      "6,055,750.00"],
  ["22/04/2024","DSTV SUBSCRIPTION PREMIUM BOUQUET APRIL 2024",                "24,500.00",    "",              "6,031,250.00"],
  ["25/04/2024","NHF DEDUCTION FEDERAL MORTGAGE BANK APRIL",                   "8,750.00",     "",              "6,022,500.00"],
  ["27/04/2024","ARM PENSIONS RSA CONTRIBUTION APRIL 2024",                    "28,000.00",    "",              "5,994,500.00"],
  // May 2024
  ["01/05/2024","SALARY PAYMENT MAY 2024 TECHCORP LTD",                       "",             "350,000.00",    "6,344,500.00"],
  ["03/05/2024","PROFESSIONAL FEE INVOICE 67 CHIDINMA OKONKWO CONSULTING",     "",             "500,000.00",    "6,844,500.00"],
  ["05/05/2024","AWS MONTHLY SERVER INVOICE MAY 2024 EC2",                     "32,000.00",    "",              "6,812,500.00"],
  ["07/05/2024","NOTION TEAM WORKSPACE SUBSCRIPTION ANNUAL",                   "12,000.00",    "",              "6,800,500.00"],
  ["09/05/2024","BOLT RIDE SHARE CLIENT MEETING MAINLAND LAGOS",               "5,500.00",     "",              "6,795,000.00"],
  ["12/05/2024","PAYONEER TRANSFER USD 1000 INV-MAY2024",                      "",             "1,550,000.00",  "8,345,000.00"],
  ["14/05/2024","MTN DATA SUBSCRIPTION 50GB MONTHLY PLAN",                     "15,000.00",    "",              "8,330,000.00"],
  ["16/05/2024","IKEDC ELECTRICITY TOKEN RECHARGE OFFICE MAY",                 "10,000.00",    "",              "8,320,000.00"],
  ["18/05/2024","UBA QUICK LOAN REPAYMENT INSTALMENT MAY",                     "30,000.00",    "",              "8,290,000.00"],
  ["20/05/2024","TOPTAL CONTRACT PAYMENT Q2 BACKEND ENGINEERING",              "",             "650,000.00",    "8,940,000.00"],
  ["22/05/2024","ATM WITHDRAWAL GTB LEKKI PHASE 1 BRANCH",                    "80,000.00",    "",              "8,860,000.00"],
  ["25/05/2024","NHIS HEALTH INSURANCE MONTHLY PREMIUM MAY",                   "17,500.00",    "",              "8,842,500.00"],
  ["28/05/2024","ARM PENSIONS RSA CONTRIBUTION MAY 2024",                      "28,000.00",    "",              "8,814,500.00"],
  // Jun 2024
  ["01/06/2024","SALARY PAYMENT JUNE 2024 TECHCORP LTD",                      "",             "350,000.00",    "9,164,500.00"],
  ["03/06/2024","UPWORK PAYMENT INV-20240603 API INTEGRATION PROJECT",          "",             "430,000.00",    "9,594,500.00"],
  ["05/06/2024","DIGITALOCEAN MONTHLY DROPLET INVOICE JUNE 2024",              "15,000.00",    "",              "9,579,500.00"],
  ["07/06/2024","AIRTEL BROADBAND MONTHLY PLAN JUNE RENEWAL",                  "12,000.00",    "",              "9,567,500.00"],
  ["10/06/2024","SWIFT INWARD REMITTANCE USD 1500 LONDON CLIENT PROJECT",      "",             "2,325,000.00",  "11,892,500.00"],
  ["12/06/2024","UDEMY COURSE REACT NATIVE MOBILE DEVELOPMENT",                "12,000.00",    "",              "11,880,500.00"],
  ["14/06/2024","FUEL PURCHASE MOBIL STATION ADMIRALTY WAY LEKKI",             "22,000.00",    "",              "11,858,500.00"],
  ["15/06/2024","MONITOR PURCHASE LG ULTRAWIDE 27INCH JUMIA",                  "180,000.00",   "",              "11,678,500.00"],
  ["18/06/2024","QUIDAX CRYPTO WITHDRAWAL BITCOIN SALE JUNE",                  "",             "280,000.00",    "11,958,500.00"],
  ["20/06/2024","TRF TO OWN SAVINGS ACCOUNT ACCESS BANK 0045678912",           "500,000.00",   "",              "11,458,500.00"],
  ["22/06/2024","CHARGEBACK DISPUTED TRANSACTION KONGA REFUND",                "",             "18,500.00",     "11,477,000.00"],
  ["25/06/2024","NHF CONTRIBUTION FEDERAL MORTGAGE BANK JUNE",                 "8,750.00",     "",              "11,468,250.00"],
  ["27/06/2024","ARM PENSIONS RSA CONTRIBUTION JUNE 2024",                     "28,000.00",    "",              "11,440,250.00"],
  ["30/06/2024","NHIS HEALTH INSURANCE MONTHLY PREMIUM JUNE",                  "17,500.00",    "",              "11,422,750.00"],
];

const doc = new PDFDocument({ size: 'A4', margin: 40 });
doc.pipe(fs.createWriteStream(OUTPUT));

const W = doc.page.width - 80; // usable width

// ── HEADER ─────────────────────────────────────────────────────────────────
doc.rect(40, 40, W, 50).fill(GTB_GREEN);
doc.fillColor('white').fontSize(18).font('Helvetica-Bold')
   .text('GUARANTY TRUST BANK PLC', 55, 52);
doc.fontSize(10).font('Helvetica')
   .text('Official Bank Statement — Confidential', 55, 75);
doc.fillColor(GTB_RED).fontSize(10).font('Helvetica-Bold')
   .text('GTBank', W - 20, 57, { align: 'right', width: 60 });
doc.moveDown(0.5);

// ── ACCOUNT INFO TABLE ──────────────────────────────────────────────────────
const infoY = 105;
doc.rect(40, infoY, W, 80).fill(LIGHT_BG).stroke('#dddddd');
const col1 = 45, col2 = 200, col3 = 360, col4 = 490;
const rowH = 18;

const info = [
  ['Account Name:',   'UDEZE CHINEDU CHINAGOROM',         'Statement Period:', '01 Jan 2024 - 30 Jun 2024'],
  ['Account Number:', '0123456789',                        'Account Type:',    'Current Account'],
  ['Branch:',         'Victoria Island Branch, Lagos',     'Currency:',        'Nigerian Naira (NGN)'],
  ['BVN:',            '22*********34 (masked)',            'Date Printed:',    '30 June 2024'],
];

info.forEach((row, i) => {
  const y = infoY + 8 + i * rowH;
  doc.fillColor(DARK).fontSize(7.5).font('Helvetica-Bold').text(row[0], col1, y);
  doc.font('Helvetica').text(row[1], col2, y);
  doc.font('Helvetica-Bold').text(row[2], col3, y);
  doc.font('Helvetica').text(row[3], col4, y);
});

// ── BALANCE SUMMARY ────────────────────────────────────────────────────────
const balY = 200;
doc.rect(40, balY, W, 40).fill('#ffffff').stroke(GTB_GREEN);

doc.fillColor(DARK).fontSize(7.5).font('Helvetica-Bold')
   .text('Opening Balance (01/01/2024):', 50, balY + 8)
   .text('Total Credits:', 50, balY + 24);
doc.fillColor(GTB_GREEN).font('Helvetica-Bold')
   .text('₦0.00', 220, balY + 8)
   .text('₦12,383,200.00', 220, balY + 24);

doc.fillColor(DARK).font('Helvetica-Bold')
   .text('Closing Balance (30/06/2024):', 330, balY + 8)
   .text('Total Debits:', 330, balY + 24);
doc.fillColor(GTB_GREEN).font('Helvetica-Bold')
   .text('₦11,422,750.00', 500, balY + 8);
doc.fillColor(GTB_RED).font('Helvetica-Bold')
   .text('₦960,450.00', 500, balY + 24);

// ── SECTION TITLE ──────────────────────────────────────────────────────────
doc.fillColor(GTB_GREEN).fontSize(12).font('Helvetica-Bold')
   .text('Transaction History', 40, 255);

// ── TRANSACTION TABLE ──────────────────────────────────────────────────────
const tableTop = 275;
const colWidths = [70, 220, 80, 85, 85]; // Date, Narration, Debit, Credit, Balance
const colX = [40];
colWidths.forEach((w, i) => { if (i > 0) colX.push(colX[i-1] + colWidths[i-1]); });
const rowHeight = 14;

// Header row
doc.rect(40, tableTop, W, rowHeight + 2).fill(GTB_GREEN);
const headers = ['Date', 'Narration', 'Debit (NGN)', 'Credit (NGN)', 'Balance (NGN)'];
headers.forEach((h, i) => {
  const align = i >= 2 ? 'right' : 'left';
  const xOff = i >= 2 ? -4 : 3;
  doc.fillColor('white').fontSize(7.5).font('Helvetica-Bold')
     .text(h, colX[i] + xOff, tableTop + 4, { width: colWidths[i] - 4, align });
});

let currentY = tableTop + rowHeight + 2;

TRANSACTIONS.forEach(([date, narr, dr, cr, bal], idx) => {
  // Page break check
  if (currentY > doc.page.height - 80) {
    doc.addPage();
    currentY = 40;
    // Repeat header
    doc.rect(40, currentY, W, rowHeight + 2).fill(GTB_GREEN);
    headers.forEach((h, i) => {
      const align = i >= 2 ? 'right' : 'left';
      const xOff = i >= 2 ? -4 : 3;
      doc.fillColor('white').fontSize(7.5).font('Helvetica-Bold')
         .text(h, colX[i] + xOff, currentY + 4, { width: colWidths[i] - 4, align });
    });
    currentY += rowHeight + 2;
  }

  const bg = idx % 2 === 0 ? '#ffffff' : '#f5f5f5';
  doc.rect(40, currentY, W, rowHeight).fill(bg);

  // Thin border
  doc.rect(40, currentY, W, rowHeight).stroke('#e0e0e0');

  doc.fillColor(DARK).fontSize(7).font('Helvetica');
  doc.text(date, colX[0] + 3, currentY + 3, { width: colWidths[0] - 4 });
  doc.text(narr, colX[1] + 3, currentY + 3, { width: colWidths[1] - 4 });

  if (dr) {
    doc.fillColor(GTB_RED)
       .text('₦' + dr, colX[2] - 4, currentY + 3, { width: colWidths[2], align: 'right' });
  }
  if (cr) {
    doc.fillColor(GTB_GREEN)
       .text('₦' + cr, colX[3] - 4, currentY + 3, { width: colWidths[3], align: 'right' });
  }
  doc.fillColor(DARK)
     .text('₦' + bal, colX[4] - 4, currentY + 3, { width: colWidths[4], align: 'right' });

  currentY += rowHeight;
});

// Totals row
doc.rect(40, currentY, W, rowHeight + 2).fill(GTB_GREEN);
doc.fillColor('white').fontSize(7.5).font('Helvetica-Bold')
   .text('PERIOD TOTALS', colX[1] + 3, currentY + 4, { width: colWidths[1] });
doc.text('₦960,450.00', colX[2] - 4, currentY + 4, { width: colWidths[2], align: 'right' });
doc.text('₦12,383,200.00', colX[3] - 4, currentY + 4, { width: colWidths[3], align: 'right' });
currentY += rowHeight + 10;

// ── FOOTER ─────────────────────────────────────────────────────────────────
if (currentY > doc.page.height - 60) { doc.addPage(); currentY = 40; }
doc.moveTo(40, currentY).lineTo(40 + W, currentY).stroke('#aaaaaa');
currentY += 8;
doc.fillColor(MID_GREY).fontSize(6.5).font('Helvetica')
   .text(
     'This statement is computer generated and does not require a signature or stamp to be valid. ' +
     'For queries contact GTConnect: 0700-482-6328 | customercare@gtbank.com | www.gtbank.com | RC No: 152321. ' +
     'Guaranty Trust Bank Plc is regulated by the Central Bank of Nigeria.',
     40, currentY, { width: W, align: 'center' }
   );
currentY += 18;
doc.fillColor(GTB_RED).font('Helvetica-Bold')
   .text(
     'CONFIDENTIAL — This document is intended solely for UDEZE CHINEDU CHINAGOROM. Unauthorised disclosure is prohibited.',
     40, currentY, { width: W, align: 'center' }
   );

doc.end();
console.log('Statement saved to: ' + OUTPUT);
