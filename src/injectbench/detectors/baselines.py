"""Two transparent reference detectors.

They exist so that every report has a floor to compare against, and as worked
examples of the :class:`~injectbench.detectors.base.Detector` interface. They
are keyword matchers, not guardrails: do not deploy them.
"""

from __future__ import annotations

import re

from .base import Detector

__all__ = ["HeuristicDetector", "RegexDetector"]

# English and Turkish patterns, matched case-insensitively.
_REGEX_PATTERNS: tuple[str, ...] = (
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
    r"(önceki|üstteki|yukarıdaki)\s+(tüm\s+)?(talimatları|komutları|kuralları)\s+(yoksay|yok say|görmezden gel|unut|dikkate alma)",
    r"sistem\s+(prompt|komut|talimat)(unu|ını)?\s+(göster|yazdır|ifşa et|söyle|paylaş)",
    r"(kısıtlama|filtre|kural)\s*(sız|olmadan)",
    r"artık\s+[\wçğıöşü\s]+\s+(modundasın|personasısın|oldun)",
)

_HEURISTIC_SIGNALS: tuple[tuple[str, float], ...] = (
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
)

_IMPERATIVE = re.compile(
    r"^\s*(please\s+)?(ignore|forget|disregard|reveal|print|show|repeat|act|pretend|bypass)\b",
    re.IGNORECASE,
)


class RegexDetector(Detector):
    """Flags an input when any known attack phrase matches."""

    name = "regex-baseline"

    def __init__(self) -> None:
        self._compiled = [re.compile(pattern, re.IGNORECASE) for pattern in _REGEX_PATTERNS]

    def predict(self, text: str) -> int:
        return int(any(pattern.search(text) for pattern in self._compiled))


class HeuristicDetector(Detector):
    """Adds up weighted keyword signals into a score between 0 and 1.

    It returns a score and no decision of its own, so the evaluation threshold
    applies and a threshold sweep is possible.
    """

    name = "heuristic"

    def __init__(self) -> None:
        self._signals = [
            (re.compile(pattern, re.IGNORECASE), weight) for pattern, weight in _HEURISTIC_SIGNALS
        ]

    def score(self, text: str) -> float:
        total = sum(weight for pattern, weight in self._signals if pattern.search(text))
        if _IMPERATIVE.search(text):
            total += 0.2
        return min(1.0, total)
