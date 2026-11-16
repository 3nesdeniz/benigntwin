"""Score predictions that were produced somewhere else.

``predictions:path.jsonl`` reads one JSON object per line::

    {"id": "apibp_0595_a", "label": "attack", "score": 0.97}

Each line needs the example ``id`` and a ``label`` (or ``prediction`` /
``predicted_label``), a ``score``, or both. This is the way to benchmark a
system that cannot be called from this machine: export the dataset ids and
texts, run the system where it lives, bring the predictions back.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ..models import Example, ModelError, Prediction
from .base import Detector, DetectorError

__all__ = ["OfflineDetector"]


class OfflineDetector(Detector):
    """Looks predictions up in a JSONL file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        self.name = f"predictions:{self.path.name}"
        self._predictions = self._load()

    def _load(self) -> dict[str, Prediction]:
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise DetectorError(f"could not read predictions file {self.path}: {exc}") from exc
        predictions: dict[str, Prediction] = {}
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            where = f"{self.path}:{line_number}"
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DetectorError(f"{where}: invalid JSON: {exc.msg}") from exc
            if not isinstance(payload, dict):
                raise DetectorError(f"{where}: each line must be a JSON object")
            raw_id = payload.get("id")
            if raw_id is None or not str(raw_id).strip():
                raise DetectorError(f"{where}: missing id")
            example_id = str(raw_id).strip()
            if example_id in predictions:
                raise DetectorError(f"{where}: duplicate id {example_id!r}")
            try:
                predictions[example_id] = Prediction.from_value(example_id, payload)
            except ModelError as exc:
                raise DetectorError(f"{where}: {exc}") from exc
        if not predictions:
            raise DetectorError(f"{self.path}: no predictions found")
        return predictions

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": "offline",
            "file": self.path.name,
            "predictions": len(self._predictions),
        }

    def predict_many(
        self,
        examples: Sequence[Example],
        *,
        workers: int = 1,
    ) -> dict[str, Prediction]:
        del workers
        return {
            example.id: self._predictions.get(
                example.id, Prediction(id=example.id, error="no prediction for this id")
            )
            for example in examples
        }
