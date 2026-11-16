"""A minimal custom detector for `injectbench evaluate --detector python:examples/my_detector.py:detect`.

Replace the body of `detect` with a call to your own guardrail. The function
receives the input text and returns the probability that it is an attack.
It never receives labels or any other column of the dataset.
"""

SUSPICIOUS = ("ignore your instructions", "system prompt", "skip the confirmation", "no safety rules")


def detect(text: str) -> float:
    lowered = text.lower()
    hits = sum(phrase in lowered for phrase in SUSPICIOUS)
    return min(1.0, 0.6 * hits)
