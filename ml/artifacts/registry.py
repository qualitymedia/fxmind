"""
Model Registry State Machine.

Lifecycle states:
TRAINING → CANDIDATE → VALIDATED → PRODUCTION → RETIRED
                                               → FAILED

Only VALIDATED models can be promoted to PRODUCTION.
Model versions are never overwritten.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


class ModelLifecycleState(str, Enum):
    TRAINING = "TRAINING"
    CANDIDATE = "CANDIDATE"
    VALIDATED = "VALIDATED"
    PRODUCTION = "PRODUCTION"
    RETIRED = "RETIRED"
    FAILED = "FAILED"


VALID_TRANSITIONS = {
    ModelLifecycleState.TRAINING: [ModelLifecycleState.CANDIDATE, ModelLifecycleState.FAILED],
    ModelLifecycleState.CANDIDATE: [ModelLifecycleState.VALIDATED, ModelLifecycleState.FAILED],
    ModelLifecycleState.VALIDATED: [ModelLifecycleState.PRODUCTION, ModelLifecycleState.FAILED],
    ModelLifecycleState.PRODUCTION: [ModelLifecycleState.RETIRED, ModelLifecycleState.FAILED],
    ModelLifecycleState.RETIRED: [],
    ModelLifecycleState.FAILED: [],
}


def can_transition(current_state: str, new_state: str) -> bool:
    """Validate state transition logic."""
    try:
        curr_enum = ModelLifecycleState(current_state)
        new_enum = ModelLifecycleState(new_state)
        return new_enum in VALID_TRANSITIONS[curr_enum]
    except ValueError:
        return False
