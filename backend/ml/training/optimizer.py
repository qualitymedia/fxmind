"""
Optuna Hyperparameter Optimization Engine.

Searches:
- max_depth (3..6)
- learning_rate (0.01..0.10)
- n_estimators (200..1000)
- subsample (0.6..1.0)
- colsample_bytree (0.6..1.0)
- min_child_weight (5..50)
- gamma
- reg_alpha
- reg_lambda
"""

from __future__ import annotations

import numpy as np
import xgboost as xgb
from sklearn.metrics import log_loss

from ml.models.direction import LABEL_MAP
from ml.validation.walk_forward import PurgedWalkForwardCV

try:
    import optuna
    HAS_OPTUNA = True
except ImportError:
    HAS_OPTUNA = False


class OptunaOptimizer:
    """Hyperparameter search for XGBoost using Purged Walk-Forward CV."""

    def __init__(self, n_trials: int = 30):
        self.n_trials = n_trials

    def optimize(self, X: np.ndarray, y: np.ndarray, label_ends: list[int]) -> dict:
        """Run Optuna study."""
        if not HAS_OPTUNA:
            print("  [WARN] Optuna not installed. Using default hyperparameter grid.")
            return {
                "objective": "multi:softprob",
                "num_class": 3,
                "max_depth": 4,
                "learning_rate": 0.03,
                "n_estimators": 250,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "min_child_weight": 15,
                "random_state": 42,
                "n_jobs": -1,
            }

        # Convert y to integer classes
        y_int = np.array([LABEL_MAP[val] if isinstance(val, str) else val for val in y])

        cv = PurgedWalkForwardCV(n_splits=3, embargo_bars=4)

        def objective(trial: optuna.Trial) -> float:
            params = {
                "objective": "multi:softprob",
                "num_class": 3,
                "max_depth": trial.suggest_int("max_depth", 3, 6),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.10, log=True),
                "n_estimators": trial.suggest_int("n_estimators", 200, 500),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
                "min_child_weight": trial.suggest_int("min_child_weight", 5, 50),
                "gamma": trial.suggest_float("gamma", 0.0, 0.5),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
                "random_state": 42,
                "n_jobs": -1,
            }

            losses = []

            for train_idx, val_idx in cv.split(X, label_ends):
                X_tr, y_tr = X[train_idx], y_int[train_idx]
                X_va, y_va = X[val_idx], y_int[val_idx]

                clf = xgb.XGBClassifier(**params)
                clf.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], verbose=False)

                probs = clf.predict_proba(X_va)
                loss = log_loss(y_va, probs)
                losses.append(loss)

            return float(np.mean(losses))

        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=self.n_trials)

        best = study.best_params
        best.update({"objective": "multi:softprob", "num_class": 3, "random_state": 42, "n_jobs": -1})
        return best
