"""
Purging & Embargo for Financial Time Series Cross-Validation.

Prevents leakage caused by overlapping triple-barrier label horizons.
"""

from __future__ import annotations

import pandas as pd


def purge_and_embargo_splits(
    train_indices: list[int],
    val_indices: list[int],
    label_end_indices: list[int],
    embargo_bars: int = 4,
) -> tuple[list[int], list[int]]:
    """
    Purge training samples whose triple-barrier label evaluation period overlaps
    with validation samples, and apply an embargo period after validation set.
    """
    if not train_indices or not val_indices:
        return train_indices, val_indices

    val_start = min(val_indices)
    val_end = max(val_indices)

    # Embargo limit
    embargo_limit = val_end + embargo_bars

    purged_train = []
    for idx in train_indices:
        lbl_end = label_end_indices[idx]
        
        # 1. Purge: If training sample's label evaluation period extends into validation period
        if idx < val_start and lbl_end >= val_start:
            continue
        
        # 2. Embargo: If training sample is immediately after validation period within embargo window
        if val_end < idx <= embargo_limit:
            continue

        purged_train.append(idx)

    return purged_train, val_indices
