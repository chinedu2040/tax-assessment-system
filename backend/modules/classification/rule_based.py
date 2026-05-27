from typing import Tuple

RULES = {
    "taxable_income": {
        "freelance_income": [
            "upwork", "fiverr", "toptal", "payoneer", "wise transfer",
            "transferwise", "client payment", "project payment", "freelance",
            "consultancy fee", "professional fee", "invoice payment",
            "remittance", "guru.com", "freelancer.com",
        ],
        "salary": [
            "salary", "salari", "monthly pay", "payroll", "wages",
            "staff pay", "net pay", "basic pay",
        ],
        "business_income": [
            "sales proceeds", "business income", "revenue", "proceeds",
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
            "data bundle", "wifi subscription",
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
        ],
        "loan": [
            "loan", "credit facility", "overdraft", "repayment",
            "quick credit", "salary advance",
        ],
        "refund": [
            "refund", "reversal", "chargeback", "dispute credit",
        ],
        "atm": [
            "atm withdrawal", "cash withdrawal", "pos purchase",
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
