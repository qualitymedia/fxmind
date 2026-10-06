"""
Baseline Benchmarks for ML Comparison.

Models:
1. Random Classifier
2. Previous Direction (Persistence)
3. Logistic Regression
4. Random Forest
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


class RandomBaseline:
    """Random baseline classifier."""
    def fit(self, X, y): pass
    def predict_proba(self, X):
        n = len(X)
        return np.ones((n, 3)) / 3.0
    def predict(self, X):
        return ["NEUTRAL"] * len(X)


class PreviousDirectionBaseline:
    """Previous direction persistence baseline."""
    def fit(self, X, y): pass
    def predict_proba(self, X):
        n = len(X)
        return np.ones((n, 3)) / 3.0
    def predict(self, X):
        # Predicts NEUTRAL by default
        return ["NEUTRAL"] * len(X)


class LogisticRegressionBaseline:
    """Logistic Regression baseline."""
    def __init__(self):
        self.model = LogisticRegression(max_iter=500, multi_class="multinomial")
    def fit(self, X, y):
        self.model.fit(X, y)
        return self
    def predict_proba(self, X):
        return self.model.predict_proba(X)
    def predict(self, X):
        return self.model.predict(X)


class RandomForestBaseline:
    """Random Forest baseline."""
    def __init__(self, n_estimators=100):
        self.model = RandomForestClassifier(n_estimators=n_estimators, max_depth=5, random_state=42)
    def fit(self, X, y):
        self.model.fit(X, y)
        return self
    def predict_proba(self, X):
        return self.model.predict_proba(X)
    def predict(self, X):
        return self.model.predict(X)
