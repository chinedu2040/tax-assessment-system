from typing import Tuple

RULES = {
    "taxable_income": {
        "freelance_income": [
            "upwork", "fiverr", "toptal", "payoneer", "wise transfer",
            "transferwise", "client payment", "client retainer", "client advance",
            "project payment", "freelance", "consultancy fee", "consulting fee",
            "professional fee", "invoice payment", "retainer fee",
            "design fee", "development fee", "service fee", "service payment",
            "web design", "logo design", "brand", "ui/ux", "motion graphics",
            "photography", "seo", "content writing", "graphic design",
            "remittance", "guru.com", "freelancer.com",
            "physiotherapy", "physio", "therapy session", "therapy fee",
            "medical session", "clinic", "treatment fee",
            "rehab", "rehabilitation", "home care", "health care service",
        ],
        "salary": [
            "salary", "salari", "monthly pay", "payroll", "wages",
            "staff pay", "net pay", "basic pay",
        ],
        "business_income": [
            "sales proceeds", "business income", "business revenue",
            "media house income", "company payment",
        ],
        "interest_income": [
            "owealth interest", "interest earned", "investment income",
            "dividend", "piggyvest interest", "cowrywise return",
            "savings account interest", "pb_sav_acct_interest",
            "interest credit", "acct interest",
            "capitalized interest",
        ],
        "crypto_income": [
            "binance", "coinbase", "crypto", "bitcoin", "ethereum",
            "usdt", "blockchain", "p2p transfer", "bybit", "kucoin",
            "luno", "quidax", "buycoin",
        ],
        "foreign_income": [
            "swift", "foreign currency", "domiciliary", "dom account",
            "international transfer", "wire transfer", "dollar credit",
        ],
    },
    "deductible_expense": {
        "equipment": [
            "laptop", "computer", "monitor", "keyboard", "phone purchase",
            "gadget", "hardware", "iphone", "macbook", "dell", "hp laptop",
        ],
        "software": [
            "adobe", "github", "notion", "figma", "canva", "zoom", "slack",
            "microsoft 365", "office 365", "jetbrains", "digitalocean",
            "aws", "google workspace", "gsuite", "netlify", "vercel",
            "heroku", "namecheap", "godaddy",
        ],
        "internet": [
            "mtn", "airtel", "glo", "9mobile", "spectranet", "swift",
            "smile", "internet", "data subscription", "broadband",
            "data bundle", "wifi subscription", "mobile data |",
            "data purchase", "data purchase to",
        ],
        "utilities": [
            "nepa", "disco", "electricity", "ikedc", "ekedc", "bedc",
            "phcn", "token", "dstv", "showmax", "netflix", "water bill",
        ],
        "professional_development": [
            "udemy", "coursera", "pluralsight", "training", "workshop",
            "certification", "book purchase", "conference", "seminar",
            "linkedin learning", "skillshare",
        ],
        "pension": [
            "pension", "pfa", "retirement", "nhf", "nhis",
            "stanbic ibtc pensions", "arm pensions", "aiico pension",
        ],
        "transport": [
            "uber", "bolt", "indriver", "taxify", "fuel", "transport",
            "logistics", "delivery",
        ],
    },
    "non_taxable": {
        "transfer": [
            "transfer to", "transfer from", "trf", "intra-bank",
            "between accounts", "own account", "inter-account",
            "nip transfer", "alat nip", "onebank transfer", "mob/uto/",
            "personal transfer", "own transfer",
            "nip cr/mob", "cip/cr", "online transfer",
        ],
        "loan": [
            "loan", "credit facility", "overdraft", "repayment",
            "quick credit", "salary advance",
        ],
        "refund": [
            "refund", "reversal", "chargeback", "dispute credit",
            "pay back", "payback", "failed transfer reversal", "rev-nip-fee", "rev-vat-fee",
        ],
        "atm": [
            "atm withdrawal", "cash withdrawal", "pos purchase",
            "pos transfer", "transfer to pos transfer",
            "mc loc", "mc pos pyt", "mc agency",
        ],
        "savings": [
            "owealth withdrawal", "auto-save", "owealth balance",
            "savings deposit", "fixed deposit", "target savings",
            "piggybank", "cowrywise", "risevest", "bamboo",
            "flexible savings", "auto save", "one year plan",
            "money market", "uba nominee", "stanbic ibtc money",
            "mutual fund", "treasury bill", "t-bill",
        ],
        "bank_charge": [
            "electronic money transfer levy", "stamp duty", "sms alert",
            "maintenance fee", "card maintenance", "vat on ", "commission on",
            "bank charge", "service charge",
            "emtl", "_emtl_dc", "value added tax", "transfer levy",
            "electroniclevy", "cbn electroniclevy", "nip-fee", "vat-fee",
            "alert charge", "quarterly debit", "card issuance fee",
            "witholding tax", "withholding tax", "nip charge", "sms charge",
            "charge + vat", "charge vat",
        ],
        "airtime_data": [
            "airtime recharge", "airtime |", "vtu airtime",
            "airtime to", "airtime purchase", "/atp|",
            "airtime//", "bundle//",
        ],
    },
}


class RuleBasedClassifier:
    def __init__(self):
        self._rules = RULES

    def classify(self, description: str) -> Tuple[str, str, float]:
        lower = description.lower()
        for category, sub_cats in self._rules.items():
            for sub_category, keywords in sub_cats.items():
                for kw in keywords:
                    if kw in lower:
                        return category, sub_category, 0.90
        return "needs_review", "unknown", 0.00
