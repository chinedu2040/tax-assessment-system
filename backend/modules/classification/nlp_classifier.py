import os
import logging
from pathlib import Path
from typing import Tuple

import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from modules.classification.training_data import get_training_data

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).parent.parent.parent / "ml_models" / "classifier.pkl"


def _build_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            strip_accents="unicode",
            analyzer="word",
        )),
        ("clf", LogisticRegression(
            multi_class="ovr",
            max_iter=1000,
            C=1.0,
            random_state=42,
        )),
    ])


def train_model() -> Pipeline:
    data = get_training_data()
    texts = [d["text"] for d in data]
    labels = [d["category"] for d in data]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipeline = _build_pipeline()
    pipeline.fit(X_train, y_train)

    accuracy = pipeline.score(X_test, y_test)
    logger.info(f"NLP classifier trained. Held-out accuracy: {accuracy:.4f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    return pipeline


def _load_or_train() -> Pipeline:
    if MODEL_PATH.exists():
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            logger.warning("Failed to load saved model; retraining.")
    return train_model()


class NLPClassifier:
    def __init__(self):
        self._pipeline = _load_or_train()

    def classify(self, description: str) -> Tuple[str, str, float]:
        proba = self._pipeline.predict_proba([description])[0]
        classes = self._pipeline.classes_
        best_idx = proba.argmax()
        category = classes[best_idx]
        confidence = float(proba[best_idx])
        return category, "unknown", confidence

    def get_accuracy(self) -> float:
        data = get_training_data()
        texts = [d["text"] for d in data]
        labels = [d["category"] for d in data]
        _, X_test, _, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        return float(self._pipeline.score(X_test, y_test))
