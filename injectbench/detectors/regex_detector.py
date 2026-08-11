"""A transparent regex/keyword baseline detector.

This is intentionally simple: it exists as a reference point and as a worked
example of the `Detector` interface. Real guardrails should beat it comfortably
on recall *without* paying for it in false positives — which is exactly what the
paired-boundary metric measures.
"""
from __future__ import annotations

import re
from typing import List

from .base import Detector

# Patterns are English + Turkish, matched case-insensitively.
_PATTERNS: List[str] = [
    r"ignore (all|any|the|your)?\s*(previous|prior|above|earlier)\s+(instructions|prompts|rules)",
    r"disregard (all|the|your)?\s*(previous|prior|above)\s+(instructions|rules)",
    r"forget (everything|all|your)\s*(you were told|instructions|system prompt)?",
    r"reveal (your|the)\s+(system prompt|instructions|hidden prompt|initial prompt)",
    r"(print|show|repeat|output|display)\s+(your|the)\s+(system prompt|instructions|rules|prompt above)",
    r"you are now\s+[\w\s]+ (mode|persona|assistant)",
    r"(developer|dev|debug|god|dan|jailbreak)\s+mode",
    r"do anything now",
    r"without any (restrictions|filters|rules|limitations)",
    r"bypass (the|your|all)?\s*(safety|content|guard|filter)",
    r"</?(system|user|assistant|instructions?)>",
    r"\[/?(system|inst|instructions?)\]",
    r"base64|rot13|leetspeak",
    r"(print|leak|exfiltrate|send|reveal)\s+(the|your|all)?\s*(api|secret|access)?\s*(key|token|password|credentials)",
    # Turkish
    r"(önceki|üstteki|yukarıdaki)\s+(tüm\s+)?(talimatları|komutları|kuralları)\s+(yoksay|yok say|görmezden gel|unut|dikkate alma)",
    r"sistem\s+(prompt|komut|talimat)(unu|ını)?\s+(göster|yazdır|ifşa et|söyle|paylaş)",
    r"(kısıtlama|filtre|kural)\s*(sız|olmadan)",
    r"artık\s+[\wçğıöşü\s]+\s+(modundasın|personasısın|oldun)",
]


class RegexDetector(Detector):
    name = "regex-baseline"

    def __init__(self) -> None:
        self._compiled = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]

    def predict(self, text: str) -> int:
        text = text or ""
        return 1 if any(rx.search(text) for rx in self._compiled) else 0

    def score(self, text: str) -> float:
        text = text or ""
        hits = sum(1 for rx in self._compiled if rx.search(text))
        # squashing so multiple hits raise confidence without exceeding 1
        return min(1.0, hits / 3.0)
