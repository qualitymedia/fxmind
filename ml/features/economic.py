"""
Economic Calendar features (~8 features).

Minutes to next event, minutes since previous event,
flags for next 15m, 30m, 60m events, event importance.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_economic_features(
    main_m15_df: pd.DataFrame,
    events_df: pd.DataFrame | None,
) -> pd.DataFrame:
    """Compute economic calendar event distance and risk window features."""
    res = pd.DataFrame(index=main_m15_df.index)

    if events_df is None or events_df.empty:
        res["mins_to_econ_event"] = 999.0
        res["mins_since_econ_event"] = 999.0
        res["event_next_15m"] = 0.0
        res["event_next_30m"] = 0.0
        res["event_next_60m"] = 0.0
        res["high_impact_event_near"] = 0.0
        return res

    ts = pd.to_datetime(main_m15_df["timestamp"], utc=True)
    events = events_df.copy()
    events["timestamp"] = pd.to_datetime(events["timestamp"], utc=True)

    # For each M15 timestamp, calculate distance to nearest upcoming/past high impact event
    high_impact = events[events["importance"].str.upper() == "HIGH"]

    mins_to_event = []
    mins_since_event = []

    for t in ts:
        if high_impact.empty:
            mins_to_event.append(999.0)
            mins_since_event.append(999.0)
            continue

        future_events = high_impact[high_impact["timestamp"] >= t]
        past_events = high_impact[high_impact["timestamp"] <= t]

        if not future_events.empty:
            m_to = (future_events["timestamp"].min() - t).total_seconds() / 60.0
        else:
            m_to = 999.0

        if not past_events.empty:
            m_since = (t - past_events["timestamp"].max()).total_seconds() / 60.0
        else:
            m_since = 999.0

        mins_to_event.append(m_to)
        mins_since_event.append(m_since)

    res["mins_to_econ_event"] = mins_to_event
    res["mins_since_econ_event"] = mins_since_event
    res["event_next_15m"] = (np.array(mins_to_event) <= 15).astype(float)
    res["event_next_30m"] = (np.array(mins_to_event) <= 30).astype(float)
    res["event_next_60m"] = (np.array(mins_to_event) <= 60).astype(float)
    res["high_impact_event_near"] = (
        (np.array(mins_to_event) <= 30) | (np.array(mins_since_event) <= 30)
    ).astype(float)

    return res
