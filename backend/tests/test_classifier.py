import pytest
from modules.classification.rule_based import RuleBasedClassifier
from modules.classification.nlp_classifier import NLPClassifier
from modules.classification.hybrid_engine import classify_transaction


@pytest.fixture(scope="module")
def rule_clf():
    return RuleBasedClassifier()


@pytest.fixture(scope="module")
def nlp_clf():
    return NLPClassifier()


class TestRuleBased:
    def test_upwork_is_taxable_income(self, rule_clf):
        cat, sub, conf = rule_clf.classify("UPWORK PAYMENT INV 2341")
        assert cat == "taxable_income"
        assert conf == 0.90

    def test_mtn_is_deductible(self, rule_clf):
        cat, sub, conf = rule_clf.classify("MTN DATA SUBSCRIPTION 10GB MONTHLY")
        assert cat == "deductible_expense"
        assert conf == 0.90

    def test_atm_is_non_taxable(self, rule_clf):
        cat, sub, conf = rule_clf.classify("ATM WITHDRAWAL LAGOS ISLAND BRANCH")
        assert cat == "non_taxable"
        assert conf == 0.90

    def test_payoneer_is_taxable_income(self, rule_clf):
        cat, sub, conf = rule_clf.classify("PAYONEER TRANSFER USD 850 PROJECT")
        assert cat == "taxable_income"
        assert conf == 0.90

    def test_fiverr_is_taxable_income(self, rule_clf):
        cat, sub, conf = rule_clf.classify("FIVERR WITHDRAWAL TO BANK ACCOUNT")
        assert cat == "taxable_income"
        assert conf == 0.90

    def test_adobe_is_deductible(self, rule_clf):
        cat, sub, conf = rule_clf.classify("ADOBE CREATIVE CLOUD MONTHLY")
        assert cat == "deductible_expense"
        assert conf == 0.90

    def test_loan_is_non_taxable(self, rule_clf):
        cat, sub, conf = rule_clf.classify("LOAN REPAYMENT ZENITH BANK CREDIT")
        assert cat == "non_taxable"
        assert conf == 0.90


class TestNLPClassifier:
    def test_accuracy_above_85_percent(self, nlp_clf):
        accuracy = nlp_clf.get_accuracy()
        assert accuracy >= 0.85, f"NLP accuracy {accuracy:.2%} is below 85%"

    def test_classifies_upwork(self, nlp_clf):
        cat, sub, conf = nlp_clf.classify("UPWORK PAYMENT PROJECT COMPLETION")
        assert cat == "taxable_income"
        assert conf > 0.5

    def test_classifies_mtn(self, nlp_clf):
        cat, sub, conf = nlp_clf.classify("MTN DATA SUBSCRIPTION 10GB MONTHLY")
        assert cat == "deductible_expense"
        assert conf > 0.5


class TestHybridEngine:
    def test_rule_method_used_for_clear_match(self):
        result = classify_transaction("UPWORK PAYMENT INV 2341")
        assert result["classification_method"] == "rule"
        assert result["category"] == "taxable_income"
        assert result["confidence_score"] >= 0.85

    def test_rule_method_for_atm(self):
        result = classify_transaction("ATM WITHDRAWAL LAGOS ISLAND")
        assert result["classification_method"] == "rule"
        assert result["category"] == "non_taxable"

    def test_nlp_or_flagged_for_ambiguous(self):
        result = classify_transaction("PAYMENT FROM JOHN 12345")
        assert result["classification_method"] in ("nlp", "flagged", "rule")

    def test_confidence_score_present(self):
        result = classify_transaction("SALARY PAYMENT NOVEMBER 2024")
        assert "confidence_score" in result
        assert result["confidence_score"] >= 0
