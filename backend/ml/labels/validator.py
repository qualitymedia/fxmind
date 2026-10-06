"""
Label distribution validation.
"""

from __future__ import annotations

import pandas as pd


def validate_label_distribution(labels: pd.Series) -> dict[str, float]:
    """Calculate class proportions for BULL, BEAR, and NEUTRAL labels."""
    counts = labels.value_counts(normalize=True).to_dict()
    return {
        "BULL": round(counts.get("BULL", 0.0), 4),
        "BEAR": round(counts.get("BEAR", 0.0), 4),
        "NEUTRAL": round(counts.get("NEUTRAL", 0.0), 4),
    }
