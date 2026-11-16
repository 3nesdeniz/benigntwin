"""The detector interface.

A detector decides whether an input is an attack. To measure your own
guardrail, subclass :class:`Detector` and implement :meth:`Detector.predict`,
:meth:`Detector.score`, or both::

    from benigntwin import Detector

    class MyGuardrail(Detector):
        name = "my-guardrail"

        def score(self, text: str) -> float:
            return my_model.attack_probability(text)

Detectors only ever receive the identifier and the text of an example. Labels,
attack families and other columns never leave the benchmark.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from typing import Any

from ..models import BenignTwinError, Example, Prediction, normalize_label

__all__ = ["Detector", "DetectorError", "run_per_example"]


class DetectorError(BenignTwinError):
    """A detector cannot be created or configured."""


def run_per_example(
    examples: Sequence[Example],
    function: Callable[[Example], Prediction],
    *,
    workers: int = 1,
) -> dict[str, Prediction]:
    """Call ``function`` once per example, timing each call.

    An exception inside ``function`` becomes a prediction with ``error`` set,
    so one bad input cannot hide the results for the others. The evaluation
    decides what to do with failed rows.
    """

    if workers < 1:
        raise DetectorError("workers must be at least 1")

    def guarded(example: Example) -> Prediction:
        started = time.perf_counter()
        try:
            prediction = function(example)
        except Exception as exc:  # noqa: BLE001 - boundary around third-party code
            return Prediction(id=example.id, error=f"{type(exc).__name__}: {exc}")
        if prediction.error is None and prediction.latency_ms is None:
            elapsed = (time.perf_counter() - started) * 1000.0
            prediction = replace(prediction, latency_ms=elapsed)
        return prediction

    if workers == 1:
        return {example.id: guarded(example) for example in examples}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(guarded, examples))
    return {example.id: prediction for example, prediction in zip(examples, results, strict=True)}


class Detector:
    """Base class for everything BenignTwin can evaluate."""

    #: Shown in reports. Give every detector a distinct, stable name.
    name: str = "detector"

    def predict(self, text: str) -> int | bool | str | None:
        """Return the detector's own decision: ``1`` for an attack, ``0`` for benign."""

        return None

    def score(self, text: str) -> float | None:
        """Return an attack score between 0 and 1, if the detector has one."""

        return None

    def describe(self) -> dict[str, Any]:
        """Configuration recorded in reports. Never put secrets here."""

        return {"name": self.name, "type": type(self).__name__}

    def predict_one(self, example: Example) -> Prediction:
        label = self.predict(example.text)
        score = self.score(example.text)
        if label is None and score is None:
            raise DetectorError(f"{type(self).__name__} must implement predict() or score()")
        return Prediction(
            id=example.id,
            label=None if label is None else normalize_label(label),
            score=None if score is None else float(score),
        )

    def predict_many(
        self,
        examples: Sequence[Example],
        *,
        workers: int = 1,
    ) -> dict[str, Prediction]:
        """Predict for many examples. Override this to batch requests."""

        return run_per_example(examples, self.predict_one, workers=workers)

    def close(self) -> None:
        """Release resources. Called once after an evaluation."""
