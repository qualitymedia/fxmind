"""
Walk-Forward Chronological Cross-Validation.

Strictly chronological rolling/expanding window cross-validation
with purging and embargo.
"""

from __future__ import annotations

from typing import Generator
import numpy as np

from ml.validation.purge import purge_and_embargo_splits


class PurgedWalkForwardCV:
    """
    Chronological Walk-Forward Cross-Validator with Purging & Embargo.
    
    Ensures zero forward-looking data leakage.
    """

    def __init__(
        self,
        n_splits: int = 5,
        train_ratio: float = 0.6,
        embargo_bars: int = 4,
    ):
        self.n_splits = n_splits
        self.train_ratio = train_ratio
        self.embargo_bars = embargo_bars

    def split(
        self,
        X: np.ndarray,
        label_end_indices: list[int] | None = None,
    ) -> Generator[tuple[list[int], list[int]], None, None]:
        n_samples = len(X)
        indices = list(range(n_samples))

        if label_end_indices is None:
            label_end_indices = indices

        # Size of total walk-forward window
        val_size = int(n_samples * (1.0 - self.train_ratio) / self.n_splits)

        for i in range(self.n_splits):
            train_end = int(n_samples * self.train_ratio) + (i * val_size)
            val_start = train_end
            val_end = min(val_start + val_size, n_samples)

            train_idx = list(range(0, train_end))
            val_idx = list(range(val_start, val_end))

            if not val_idx:
                break

            # Purge & Embargo
            purged_train_idx, clean_val_idx = purge_and_embargo_splits(
                train_idx,
                val_idx,
                label_end_indices,
                embargo_bars=self.embargo_bars,
            )

            yield purged_train_idx, clean_val_idx
