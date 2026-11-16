"""Small, dependency-free statistics used by the reports.

Everything here is exact or closed-form, so two runs on the same predictions
always print the same numbers.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from statistics import NormalDist

__all__ = [
    "mcnemar_exact",
    "percentile",
    "roc_auc",
    "wilson_interval",
]


def wilson_interval(successes: int, total: int, confidence: float = 0.95) -> tuple[float, float] | None:
    """Wilson score interval for a binomial proportion.

    Returns ``None`` when ``total`` is zero. Unlike the textbook ``p ± z·se``
    interval, the Wilson interval stays inside ``[0, 1]`` and is still
    informative when the observed rate is 0 % or 100 %: 0 errors in 60 trials
    gives an upper bound of about 6 %, not "0 %".
    """

    if total < 0 or successes < 0 or successes > total:
        raise ValueError("need 0 <= successes <= total")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between 0 and 1")
    if total == 0:
        return None
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    p = successes / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    centre = (p + z2 / (2.0 * total)) / denominator
    margin = (z * math.sqrt(p * (1.0 - p) / total + z2 / (4.0 * total * total))) / denominator
    low = 0.0 if successes == 0 else max(0.0, centre - margin)
    high = 1.0 if successes == total else min(1.0, centre + margin)
    return (low, high)


def mcnemar_exact(only_first: int, only_second: int) -> float | None:
    """Two-sided exact McNemar test on the discordant counts of matched items.

    ``only_first`` is the number of matched items flagged only under the first
    condition, ``only_second`` only under the second. The return value is the
    probability of a split at least this uneven if both conditions flagged
    items equally often. ``None`` when there are no discordant items.
    """

    if only_first < 0 or only_second < 0:
        raise ValueError("counts cannot be negative")
    discordant = only_first + only_second
    if discordant == 0:
        return None
    smaller = min(only_first, only_second)
    tail = sum(math.comb(discordant, i) for i in range(smaller + 1)) / (2.0**discordant)
    return min(1.0, 2.0 * tail)


def roc_auc(scores: Sequence[float], labels: Sequence[int]) -> float | None:
    """Area under the ROC curve from attack scores, with ties given half credit.

    Equals the probability that a randomly chosen attack scores higher than a
    randomly chosen benign input. ``None`` when either class is missing.
    """

    if len(scores) != len(labels):
        raise ValueError("scores and labels must have the same length")
    positives = sum(1 for label in labels if label == 1)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        return None
    ordered = sorted(zip(scores, labels, strict=True), key=lambda item: item[0])
    rank_sum = 0.0
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][0] == ordered[index][0]:
            end += 1
        average_rank = (index + 1 + end) / 2.0
        rank_sum += average_rank * sum(1 for _, label in ordered[index:end] if label == 1)
        index = end
    return (rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


def percentile(values: Sequence[float], fraction: float) -> float | None:
    """Linear-interpolated percentile (``fraction`` in ``[0, 1]``)."""

    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be between 0 and 1")
    if not values:
        return None
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight
