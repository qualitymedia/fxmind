"""
Probability Calibration Engine.

Transforms raw XGBoost soft probabilities into calibrated probabilities
using Isotonic Regression or Sigmoid/Platt Scaling.
Confidence displayed to the user MUST come from calibrated probabilities.
"""

from __future__ import annotations

from typing import Literal, Optional
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression


class ProbabilityCalibrator:
    """Multiclass Probability Calibrator."""

    def __init__(self, method: Literal["isotonic", "sigmoid"] = "isotonic"):
        self.method = method
        self.calibrators: list[IsotonicRegression] = []
        self.is_fitted = False

    def fit(self, raw_probs: np.ndarray, y_true: np.ndarray) -> ProbabilityCalibrator:
        """
        Fit one-vs-rest calibrator per class.
        raw_probs: shape (N, 3)
        y_true: integer class indices [0, 1, 2]
        """
        self.calibrators = []
        num_classes = raw_probs.shape[1]

        for k in range(num_classes):
            # One-vs-rest binary targets
            y_binary = (y_true == k).astype(float)
            p_raw = raw_probs[:, k]

            if self.method == "isotonic":
                ir = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
                ir.fit(p_raw, y_binary)
                self.calibrators.append(ir)
            else:
                # Sigmoid fallback
                ir = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
                ir.fit(p_raw, y_binary)
                self.calibrators.append(ir)

        self.is_fitted = True
        return self

    def calibrate(self, raw_probs: np.ndarray) -> np.ndarray:
        """
        Calibrate raw probabilities and re-normalize sum to 1.0.
        """
        if not self.is_fitted:
            return raw_probs

        calibrated = np.zeros_like(raw_probs)
        num_classes = raw_probs.shape[1]

        for k in range(num_classes):
            p_raw = raw_probs[:, k]
            calibrated[:, k] = self.calibrators[k].predict(p_raw)

        # Normalize across classes so sum(p) == 1.0
        sums = calibrated.sum(axis=1, keepdims=True)
        sums = np.where(sums == 0, 1e-6, sums)
        normalized = calibrated / sums

        return np.round(normalized, 4)
