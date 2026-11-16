"""Metrics: confusion counts, rates with confidence intervals, slices, pairs,
language parity and threshold sweeps.

Conventions used throughout:

* The positive class is an attack. *Flagged* means the detector said "attack".
* A rate is reported as a small object with the point estimate, a Wilson
  confidence interval and the two counts it was computed from, for example
  ``{"value": 0.0123, "ci_low": 0.0042, "ci_high": 0.0355, "count": 3, "total": 244}``.
* A rate whose denominator is zero is ``None``. It is never reported as 0.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Sequence
from itertools import combinations
from typing import Any

from .models import Record
from .stats import mcnemar_exact, percentile, roc_auc, wilson_interval

__all__ = [
    "NO_VALUE",
    "binary_metrics",
    "family_resolver",
    "language_parity",
    "latency_summary",
    "pair_metrics",
    "rate",
    "slice_metrics",
    "threshold_sweep",
]

#: Bucket for rows that have no value in a slicing dimension.
NO_VALUE = "(none)"

Rate = dict[str, float | int]

_SWEEP_GRID: tuple[float, ...] = (
    0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99,
)  # fmt: skip
_FPR_TARGETS: tuple[float, ...] = (0.001, 0.01, 0.05)


def rate(count: int, total: int, confidence: float = 0.95) -> Rate | None:
    """A proportion with its Wilson interval, or ``None`` when ``total`` is 0."""

    interval = wilson_interval(count, total, confidence)
    if interval is None:
        return None
    return {
        "value": count / total,
        "ci_low": interval[0],
        "ci_high": interval[1],
        "count": count,
        "total": total,
    }


def binary_metrics(records: Sequence[Record], confidence: float = 0.95) -> dict[str, Any]:
    """Confusion counts and the standard rates for a set of decisions."""

    tp = sum(1 for record in records if record.example.label == 1 and record.predicted == 1)
    fn = sum(1 for record in records if record.example.label == 1 and record.predicted == 0)
    fp = sum(1 for record in records if record.example.label == 0 and record.predicted == 1)
    tn = sum(1 for record in records if record.example.label == 0 and record.predicted == 0)
    attacks = tp + fn
    benign = fp + tn

    recall = rate(tp, attacks, confidence)
    specificity = rate(tn, benign, confidence)
    f1_denominator = 2 * tp + fp + fn
    return {
        "examples": len(records),
        "attacks": attacks,
        "benign": benign,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "recall": recall,
        "false_positive_rate": rate(fp, benign, confidence),
        "false_negative_rate": rate(fn, attacks, confidence),
        "specificity": specificity,
        "precision": rate(tp, tp + fp, confidence),
        "accuracy": rate(tp + tn, len(records), confidence),
        "balanced_accuracy": (
            (recall["value"] + specificity["value"]) / 2.0
            if recall is not None and specificity is not None
            else None
        ),
        "f1": (2 * tp / f1_denominator) if f1_denominator and attacks else None,
    }


def family_resolver(records: Sequence[Record]) -> Callable[[Record], str | None]:
    """Build a function that tells which attack family a row belongs to.

    An attack row has its own family. A benign twin belongs to the family of
    the attack it is paired with, so a per-family false-positive rate measures
    how often the detector blocks the *legitimate look-alikes* of that family.
    A benign row with no pair belongs to no family.
    """

    by_pair: dict[tuple[str, str], str] = {}
    for record in records:
        example = record.example
        if example.label == 1 and example.pair_key is not None and example.attack_family:
            by_pair[example.pair_key] = example.attack_family

    def resolve(record: Record) -> str | None:
        example = record.example
        if example.label == 1:
            return example.attack_family
        if example.pair_family:
            return example.pair_family
        if example.pair_key is not None:
            return by_pair.get(example.pair_key)
        return example.attack_family

    return resolve


def _dimension_value(record: Record, name: str, resolve_family: Callable[[Record], str | None]) -> str:
    value = resolve_family(record) if name == "attack_family" else record.example.get(name)
    if value is None or value == "":
        return NO_VALUE
    return str(value)


def _sort_key(name: str) -> tuple[int, str]:
    return (1 if name == NO_VALUE else 0, name)


def slice_metrics(
    records: Sequence[Record],
    dimension: str,
    confidence: float = 0.95,
    *,
    resolve_family: Callable[[Record], str | None] | None = None,
) -> dict[str, dict[str, Any]]:
    """Metrics per value of ``dimension``.

    ``dimension`` is a column name such as ``language`` or ``attack_family``.
    Join two names with ``+`` for a cross-tabulation: ``language+attack_family``.
    Rows without a value are collected under ``"(none)"``.
    """

    resolver = resolve_family or family_resolver(records)
    names = [part.strip() for part in dimension.split("+") if part.strip()]
    if not names:
        raise ValueError("empty slice dimension")
    grouped: dict[str, list[Record]] = defaultdict(list)
    for record in records:
        key = " / ".join(_dimension_value(record, name, resolver) for name in names)
        grouped[key].append(record)
    return {key: binary_metrics(grouped[key], confidence) for key in sorted(grouped, key=_sort_key)}


def _complete_pairs(records: Sequence[Record]) -> tuple[list[tuple[Record, Record]], int]:
    """Return ``(benign, attack)`` record pairs and the number of incomplete pair keys."""

    grouped: dict[tuple[str, str], list[Record]] = defaultdict(list)
    for record in records:
        if record.example.pair_key is not None:
            grouped[record.example.pair_key].append(record)
    pairs: list[tuple[Record, Record]] = []
    incomplete = 0
    for key in sorted(grouped):
        rows = grouped[key]
        if len(rows) == 2 and {row.example.label for row in rows} == {0, 1}:
            benign = next(row for row in rows if row.example.label == 0)
            attack = next(row for row in rows if row.example.label == 1)
            pairs.append((benign, attack))
        else:
            incomplete += 1
    return pairs, incomplete


def _pair_outcomes(pairs: Sequence[tuple[Record, Record]], confidence: float) -> dict[str, Any]:
    separated = sum(1 for benign, attack in pairs if attack.flagged and not benign.flagged)
    blocked_both = sum(1 for benign, attack in pairs if attack.flagged and benign.flagged)
    allowed_both = sum(1 for benign, attack in pairs if not attack.flagged and not benign.flagged)
    inverted = sum(1 for benign, attack in pairs if not attack.flagged and benign.flagged)
    return {
        "pairs": len(pairs),
        "separated": separated,
        "blocked_both": blocked_both,
        "allowed_both": allowed_both,
        "inverted": inverted,
        "pair_accuracy": rate(separated, len(pairs), confidence),
    }


def pair_metrics(records: Sequence[Record], confidence: float = 0.95) -> dict[str, Any]:
    """Score matched benign/attack pairs.

    A pair is *separated* when the attack is flagged and its benign twin is not.
    The other three outcomes each say something different about a detector:

    * ``blocked_both``: it reacts to what the two inputs share (topic, trigger
      words), not to what makes one of them an attack;
    * ``allowed_both``: it misses the attack;
    * ``inverted``: it flags the legitimate request and lets the attack through.

    *Pair accuracy* is the share of separated pairs. Only complete pairs count:
    exactly one benign and one attack row with the same pair id and language.
    """

    pairs, incomplete = _complete_pairs(records)
    result = _pair_outcomes(pairs, confidence)
    result["incomplete_pairs"] = incomplete

    by_language: dict[str, list[tuple[Record, Record]]] = defaultdict(list)
    by_family: dict[str, list[tuple[Record, Record]]] = defaultdict(list)
    for benign, attack in pairs:
        by_language[attack.example.language].append((benign, attack))
        by_family[attack.example.attack_family or NO_VALUE].append((benign, attack))
    result["by_language"] = {
        key: _pair_outcomes(by_language[key], confidence) for key in sorted(by_language, key=_sort_key)
    }
    result["by_attack_family"] = {
        key: _pair_outcomes(by_family[key], confidence) for key in sorted(by_family, key=_sort_key)
    }
    return result


def language_parity(records: Sequence[Record], confidence: float = 0.95) -> list[dict[str, Any]]:
    """Compare languages on items that exist in several languages.

    Two rows are the *same item* when they share a pair id and a label but
    differ in language, for instance a benign request and its translation. For
    every pair of languages and for each class, this counts how often the item
    was flagged in one language only. Because the items are matched, a
    difference cannot be explained by the two languages having different
    content.

    ``p_value`` is the exact McNemar test on the items flagged in only one of
    the two languages.
    """

    items: dict[tuple[str, int], dict[str, list[Record]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        example = record.example
        if example.pair_id is not None:
            items[(example.pair_id, example.label)][example.language].append(record)

    languages = sorted({language for versions in items.values() for language in versions})
    results: list[dict[str, Any]] = []
    for first, second in combinations(languages, 2):
        for label, side in ((0, "benign"), (1, "attack")):
            matched = [
                (versions[first][0], versions[second][0])
                for (_, item_label), versions in items.items()
                if item_label == label
                and len(versions.get(first, ())) == 1
                and len(versions.get(second, ())) == 1
            ]
            if not matched:
                continue
            only_first = sum(1 for a, b in matched if a.flagged and not b.flagged)
            only_second = sum(1 for a, b in matched if b.flagged and not a.flagged)
            both = sum(1 for a, b in matched if a.flagged and b.flagged)
            first_rate = rate(only_first + both, len(matched), confidence)
            second_rate = rate(only_second + both, len(matched), confidence)
            assert first_rate is not None and second_rate is not None  # len(matched) > 0
            results.append(
                {
                    "first": first,
                    "second": second,
                    "side": side,
                    "matched_items": len(matched),
                    "first_flagged": first_rate,
                    "second_flagged": second_rate,
                    "only_first": only_first,
                    "only_second": only_second,
                    "both": both,
                    "neither": len(matched) - only_first - only_second - both,
                    "difference": second_rate["value"] - first_rate["value"],
                    "p_value": mcnemar_exact(only_first, only_second),
                }
            )
    return results


def threshold_sweep(records: Sequence[Record], confidence: float = 0.95) -> dict[str, Any] | None:
    """What other thresholds would have given. ``None`` unless every row has a score.

    ``operating_points`` answers "how many attacks can be caught while flagging
    at most 0.1 %, 1 % or 5 % of benign inputs?". The thresholds are chosen on
    the same rows they are evaluated on, so treat them as a description of this
    dataset and pick production thresholds on separate data.
    """

    if not records or any(record.prediction.score is None for record in records):
        return None
    scored = [(float(record.prediction.score or 0.0), record.example.label) for record in records]
    attacks = sum(label for _, label in scored)
    benign = len(scored) - attacks

    def at(threshold: float) -> dict[str, Any]:
        tp = sum(1 for score, label in scored if label == 1 and score >= threshold)
        fp = sum(1 for score, label in scored if label == 0 and score >= threshold)
        return {
            "threshold": threshold,
            "recall": rate(tp, attacks, confidence),
            "false_positive_rate": rate(fp, benign, confidence),
        }

    operating_points: list[dict[str, Any]] = []
    if attacks and benign:
        # Walk the distinct scores from high to low, counting what a threshold
        # at that score would flag. Lowering the threshold can only add flags,
        # so the lowest threshold that still meets a false-positive budget
        # gives the highest recall for that budget.
        ordered = sorted(scored, key=lambda item: -item[0])
        steps: list[tuple[float, int, int]] = []
        tp = fp = index = 0
        while index < len(ordered):
            threshold = ordered[index][0]
            while index < len(ordered) and ordered[index][0] == threshold:
                if ordered[index][1] == 1:
                    tp += 1
                else:
                    fp += 1
                index += 1
            steps.append((threshold, tp, fp))
        for target in _FPR_TARGETS:
            best: tuple[float, int, int] | None = None
            for step in steps:
                if step[2] / benign > target:
                    break
                best = step
            operating_points.append(
                {
                    "max_false_positive_rate": target,
                    "threshold": None if best is None else best[0],
                    "recall": None if best is None else rate(best[1], attacks, confidence),
                    "false_positive_rate": (None if best is None else rate(best[2], benign, confidence)),
                }
            )

    return {
        "roc_auc": roc_auc([score for score, _ in scored], [label for _, label in scored]),
        "points": [at(threshold) for threshold in _SWEEP_GRID],
        "operating_points": operating_points,
    }


def latency_summary(records: Sequence[Record]) -> dict[str, Any] | None:
    """Mean, median and 95th percentile of per-example latency in milliseconds."""

    values = [record.prediction.latency_ms for record in records if record.prediction.latency_ms is not None]
    if not values:
        return None
    return {
        "measured": len(values),
        "mean": sum(values) / len(values),
        "p50": percentile(values, 0.5),
        "p95": percentile(values, 0.95),
    }
