"""
XGBoost Multiclass Direction Classifier.

Classes:
0 = BEAR
1 = NEUTRAL
2 = BULL
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np
import xgboost as xgb

LABEL_MAP = {"BEAR": 0, "NEUTRAL": 1, "BULL": 2}
REVERSE_LABEL_MAP = {0: "BEAR", 1: "NEUTRAL", 2: "BULL"}


class XGBDirectionModel:
    """XGBoost multiclass classification wrapper."""

    def __init__(self, params: Optional[dict[str, Any]] = None):
        self.params = params or {
            "objective": "multi:softprob",
            "num_class": 3,
            "max_depth": 4,
            "learning_rate": 0.03,
            "n_estimators": 300,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_weight": 15,
            "gamma": 0.1,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "random_state": 42,
            "n_jobs": -1,
        }
        self.model: Optional[xgb.XGBClassifier] = None

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        early_stopping_rounds: int = 30,
    ) -> XGBDirectionModel:
        # Convert string labels if needed
        if isinstance(y[0], str):
            y = np.array([LABEL_MAP[val] for val in y])
        if y_val is not None and isinstance(y_val[0], str):
            y_val = np.array([LABEL_MAP[val] for val in y_val])

        self.model = xgb.XGBClassifier(**self.params)

        if X_val is not None and y_val is not None:
            self.model.fit(
                X,
                y,
                eval_set=[(X_val, y_val)],
                verbose=False,
            )
        else:
            self.model.fit(X, y)

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return raw uncalibrated probabilities array of shape (N, 3)."""
        if self.model is None:
            raise RuntimeError("Model has not been trained yet.")
        return self.model.predict_proba(X)

    def predict(self, X: np.ndarray) -> list[str]:
        """Return class predictions as strings ['BEAR', 'NEUTRAL', 'BULL']."""
        probs = self.predict_proba(X)
        class_idxs = np.argmax(probs, axis=1)
        return [REVERSE_LABEL_MAP[idx] for idx in class_idxs]

    def get_feature_importance(self, feature_names: list[str]) -> dict[str, float]:
        """Get XGBoost gain feature importances."""
        if self.model is None:
            return {}
        importances = self.model.feature_importances_
        res = {name: float(imp) for name, imp in zip(feature_names, importances)}
        # Sort descending
        return dict(sorted(res.items(), key=lambda item: item[1], reverse=True))
