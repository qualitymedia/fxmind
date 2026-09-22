"""
Multi-Model Voting Ensemble Classifier.

Combines three gradient boosting architectures:
1. XGBoost (Extreme Gradient Boosting)
2. LightGBM (Light Gradient Boosted Machine)
3. CatBoost (Categorical Boosting)

Using soft probability voting weights:
P(y) = w_xgb * P_xgb + w_lgb * P_lgb + w_cat * P_cat
Provides significantly smoother predictions, higher out-of-sample stability,
and lower drawdowns than any single standalone model.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import catboost as cb

LABEL_MAP = {"BEAR": 0, "NEUTRAL": 1, "BULL": 2}
REVERSE_LABEL_MAP = {0: "BEAR", 1: "NEUTRAL", 2: "BULL"}


class VotingEnsembleDirectionModel:
    """Multi-Model Ensemble of XGBoost + LightGBM + CatBoost."""

    def __init__(
        self,
        xgb_params: Optional[dict[str, Any]] = None,
        lgb_params: Optional[dict[str, Any]] = None,
        cat_params: Optional[dict[str, Any]] = None,
        weights: Optional[tuple[float, float, float]] = None,
    ):
        self.xgb_params = xgb_params or {
            "objective": "multi:softprob",
            "num_class": 3,
            "max_depth": 4,
            "learning_rate": 0.03,
            "n_estimators": 250,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_weight": 15,
            "gamma": 0.1,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "random_state": 42,
            "n_jobs": -1,
        }

        self.lgb_params = lgb_params or {
            "objective": "multiclass",
            "num_class": 3,
            "max_depth": 5,
            "num_leaves": 31,
            "learning_rate": 0.03,
            "n_estimators": 250,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_samples": 20,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "random_state": 42,
            "verbose": -1,
            "n_jobs": -1,
        }

        self.cat_params = cat_params or {
            "loss_function": "MultiClass",
            "classes_count": 3,
            "depth": 5,
            "learning_rate": 0.03,
            "iterations": 250,
            "random_seed": 42,
            "verbose": False,
            "thread_count": -1,
        }

        # Ensemble voting weights: [XGB, LGB, CatBoost]
        self.weights = weights or (0.40, 0.35, 0.25)

        self.xgb_model: Optional[xgb.XGBClassifier] = None
        self.lgb_model: Optional[lgb.LGBMClassifier] = None
        self.cat_model: Optional[cb.CatBoostClassifier] = None

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
    ) -> VotingEnsembleDirectionModel:
        """Fit all 3 base models."""
        if isinstance(y[0], str):
            y = np.array([LABEL_MAP[val] for val in y])
        if y_val is not None and isinstance(y_val[0], str):
            y_val = np.array([LABEL_MAP[val] for val in y_val])

        # 1. Train XGBoost
        self.xgb_model = xgb.XGBClassifier(**self.xgb_params)
        if X_val is not None and y_val is not None:
            self.xgb_model.fit(X, y, eval_set=[(X_val, y_val)], verbose=False)
        else:
            self.xgb_model.fit(X, y)

        # 2. Train LightGBM
        self.lgb_model = lgb.LGBMClassifier(**self.lgb_params)
        if X_val is not None and y_val is not None:
            self.lgb_model.fit(X, y, eval_set=[(X_val, y_val)], callbacks=[lgb.early_stopping(30, verbose=False)])
        else:
            self.lgb_model.fit(X, y)

        # 3. Train CatBoost
        self.cat_model = cb.CatBoostClassifier(**self.cat_params)
        if X_val is not None and y_val is not None:
            self.cat_model.fit(X, y, eval_set=(X_val, y_val), early_stopping_rounds=30, verbose=False)
        else:
            self.cat_model.fit(X, y)

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Compute weighted soft-voting probability matrix of shape (N, 3)."""
        if self.xgb_model is None or self.lgb_model is None or self.cat_model is None:
            raise RuntimeError("Ensemble models have not been trained yet.")

        p_xgb = self.xgb_model.predict_proba(X)
        p_lgb = self.lgb_model.predict_proba(X)
        p_cat = self.cat_model.predict_proba(X)

        w1, w2, w3 = self.weights
        total_w = w1 + w2 + w3

        ensemble_probs = (w1 * p_xgb + w2 * p_lgb + w3 * p_cat) / total_w
        return ensemble_probs

    def predict(self, X: np.ndarray) -> list[str]:
        """Return argmax class predictions as strings."""
        probs = self.predict_proba(X)
        class_idxs = np.argmax(probs, axis=1)
        return [REVERSE_LABEL_MAP[idx] for idx in class_idxs]

    def get_feature_importance(self, feature_names: list[str]) -> dict[str, float]:
        """Combine normalized feature importances across all 3 models."""
        if self.xgb_model is None:
            return {}

        imp_xgb = self.xgb_model.feature_importances_
        imp_lgb = self.lgb_model.feature_importances_
        imp_cat = self.cat_model.get_feature_importance()

        # Normalize to sum to 1
        s_xgb = imp_xgb.sum() or 1.0
        s_lgb = imp_lgb.sum() or 1.0
        s_cat = imp_cat.sum() or 1.0

        norm_xgb = imp_xgb / s_xgb
        norm_lgb = imp_lgb / s_lgb
        norm_cat = imp_cat / s_cat

        w1, w2, w3 = self.weights
        total_w = w1 + w2 + w3
        combined = (w1 * norm_xgb + w2 * norm_lgb + w3 * norm_cat) / total_w

        res = {name: float(combined[i]) for i, name in enumerate(feature_names)}
        return dict(sorted(res.items(), key=lambda item: item[1], reverse=True))
