"""Detector interface. Implement `predict` (and optionally `score`) to plug a
new guardrail / prompt-injection detector into the benchmark."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence


class Detector(ABC):
    """A detector maps input text to a binary decision: 1 = injection, 0 = benign."""

    name: str = "detector"

    @abstractmethod
    def predict(self, text: str) -> int:
        """Return 1 if `text` is judged a prompt-injection attempt, else 0."""

    def score(self, text: str) -> float:
        """Optional continuous risk score in [0, 1]. Defaults to the hard label."""
        return float(self.predict(text))

    def predict_batch(self, texts: Sequence[str]) -> List[int]:
        return [self.predict(t) for t in texts]
