"""A multi-signal heuristic detector.

Unlike the pure regex baseline, this one accumulates weighted signals and
thresholds a continuous risk score. It is a slightly stronger reference and
demonstrates how `score()` enables threshold sweeps / ROC-style analysis.
"""
from __future__ import annotations

import re
from typing import List, Tuple

from .base import Detector

_SIGNALS: List[Tuple[str, float]] = [
    (r"ignore\s+(all|previous|prior|the above)", 0.55),
    (r"disregard\s+(all|previous|the above)", 0.55),
    (r"forget\s+(everything|your instructions|the system)", 0.5),
    (r"(reveal|show|print|repeat|leak)\s+(your|the)\s+(system prompt|instructions|rules)", 0.6),
    (r"you are now|from now on you (are|will)", 0.4),
    (r"(developer|debug|god|dan|jailbreak|unrestricted)\s*mode", 0.6),
    (r"do anything now", 0.6),
    (r"without\s+(any\s+)?(restrictions|filters|rules|safety)", 0.5),
    (r"bypass\s+(the\s+)?(safety|content|guard|filter)", 0.55),
    (r"</?(system|assistant|instructions?)>|\[/?(system|inst)\]", 0.55),
    (r"(api|secret|access)\s*(key|token|password|credential)", 0.5),
    (r"base64|rot13|\\x[0-9a-f]{2}", 0.3),
    (r"(yoksay|yok say|görmezden gel|dikkate alma)", 0.55),
    (r"sistem\s+(prompt|talimat|komut)", 0.45),
    (r"(kısıtlama|filtre|kural)\s*(sız|olmadan)", 0.5),
]

_IMPERATIVE = re.compile(r"^\s*(please\s+)?(ignore|forget|disregard|reveal|print|show|repeat|act|pretend|bypass)\b", re.I)


class HeuristicDetector(Detector):
    name = "heuristic"

    def __init__(self, threshold: float = 0.5) -> None:
        self.threshold = threshold
        self._signals = [(re.compile(p, re.IGNORECASE), w) for p, w in _SIGNALS]

    def score(self, text: str) -> float:
        text = text or ""
        s = 0.0
        for rx, w in self._signals:
            if rx.search(text):
                s += w
        if _IMPERATIVE.search(text):
            s += 0.2
        return min(1.0, s)

    def predict(self, text: str) -> int:
        return 1 if self.score(text) >= self.threshold else 0
