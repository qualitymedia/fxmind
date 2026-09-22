"""
Master Feature Pipeline Orchestrator.

Combines price, MA, momentum, volatility, market structure, volume,
session, cross-market, H1 context, and economic calendar features
into a unified feature matrix (~100 features).
"""

from __future__ import annotations

import pandas as pd

from ml.features.cross_market import compute_cross_market_features
from ml.features.economic import compute_economic_features
from ml.features.h1_context import compute_h1_context_features
from ml.features.market_structure import compute_market_structure_features
from ml.features.momentum import compute_momentum_features
from ml.features.moving_averages import compute_ma_features
from ml.features.price import compute_price_features
from ml.features.schema import FeatureSchema
from ml.features.volatility import compute_volatility_features
from ml.features.volume import compute_volume_features
from ml.features.session import compute_session_features
from ml.features.vwap import compute_session_vwap_features
from ml.features.patterns import compute_pattern_features


class FeaturePipeline:
    """Orchestrates all feature modules into a single DataFrame."""

    def __init__(self, schema: FeatureSchema | None = None):
        self.schema = schema

    def compute_features(
        self,
        main_m15_df: pd.DataFrame,
        context_dfs: dict[str, pd.DataFrame] | None = None,
        h1_df: pd.DataFrame | None = None,
        events_df: pd.DataFrame | None = None,
    ) -> pd.DataFrame:
        """Compute full feature matrix."""
        if main_m15_df.empty:
            return pd.DataFrame()

        context_dfs = context_dfs or {}

        # 1. Individual feature blocks
        f_price = compute_price_features(main_m15_df)
        f_ma = compute_ma_features(main_m15_df)
        f_mom = compute_momentum_features(main_m15_df)
        f_vol = compute_volatility_features(main_m15_df)
        f_struct = compute_market_structure_features(main_m15_df)
        f_volume = compute_volume_features(main_m15_df)
        f_session = compute_session_features(main_m15_df)
        f_vwap = compute_session_vwap_features(main_m15_df)
        f_patterns = compute_pattern_features(main_m15_df)
        f_cross = compute_cross_market_features(main_m15_df, context_dfs)
        f_h1 = compute_h1_context_features(main_m15_df, h1_df)
        f_econ = compute_economic_features(main_m15_df, events_df)

        # 2. Concatenate all feature blocks
        feature_matrix = pd.concat(
            [
                f_price,
                f_ma,
                f_mom,
                f_vol,
                f_struct,
                f_volume,
                f_session,
                f_vwap,
                f_patterns,
                f_cross,
                f_h1,
                f_econ,
            ],
            axis=1,
        )

        # 3. Fill NaN values from rolling calculations with forward-fill then median
        feature_matrix = feature_matrix.ffill().fillna(0.0)

        # If schema is provided, align columns exactly
        if self.schema and self.schema.feature_names:
            # Missing columns fill 0.0
            for col in self.schema.feature_names:
                if col not in feature_matrix.columns:
                    feature_matrix[col] = 0.0
            feature_matrix = feature_matrix[self.schema.feature_names]

        return feature_matrix
