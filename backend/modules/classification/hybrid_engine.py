from typing import Dict, Any

from modules.classification.rule_based import RuleBasedClassifier
from modules.classification.nlp_classifier import NLPClassifier

_rule_clf = None
_nlp_clf = None


def _get_classifiers():
    global _rule_clf, _nlp_clf
    if _rule_clf is None:
        _rule_clf = RuleBasedClassifier()
    if _nlp_clf is None:
        _nlp_clf = NLPClassifier()
    return _rule_clf, _nlp_clf


def classify_transaction(description: str) -> Dict[str, Any]:
    rule_clf, nlp_clf = _get_classifiers()

    r_cat, r_sub, r_conf = rule_clf.classify(description)

    if r_conf >= 0.85:
        return {
            "category": r_cat,
            "sub_category": r_sub,
            "confidence_score": r_conf,
            "classification_method": "rule",
        }

    n_cat, n_sub, n_conf = nlp_clf.classify(description)

    if n_conf >= 0.70:
        return {
            "category": n_cat,
            "sub_category": n_sub,
            "confidence_score": n_conf,
            "classification_method": "nlp",
        }

    return {
        "category": "needs_review",
        "sub_category": "unknown",
        "confidence_score": max(r_conf, n_conf),
        "classification_method": "flagged",
    }
