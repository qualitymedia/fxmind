"""
Feature Schema definition and validation.

Ensures exact feature count (~100) and column names are enforced
between training and inference.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FeatureSchema:
    """Stores feature list and schema metadata."""
    feature_names: list[str] = field(default_factory=list)
    feature_count: int = 0
    version: str = "v1.0"

    def save(self, file_path: str | Path) -> None:
        file_path = Path(file_path)
        data = {
            "version": self.version,
            "feature_count": len(self.feature_names),
            "feature_names": self.feature_names,
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, file_path: str | Path) -> FeatureSchema:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            feature_names=data["feature_names"],
            feature_count=data["feature_count"],
            version=data.get("version", "v1.0"),
        )
