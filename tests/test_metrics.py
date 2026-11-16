from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from benigntwin.metrics import (
    NO_VALUE,
    binary_metrics,
    family_resolver,
    language_parity,
    latency_summary,
    pair_metrics,
    rate,
    slice_metrics,
    threshold_sweep,
)
from benigntwin.models import Example, Prediction, Record
from conftest import PAIRED_ROWS, examples_from

# A detector that works in English and breaks in Turkish: it misses one Turkish
# attack and flags both Turkish benign twins.
ENGLISH_ONLY = {
    "en-1-a": 1, "en-1-b": 0, "en-2-a": 1, "en-2-b": 0, "en-plain": 0,
    "tr-1-a": 0, "tr-1-b": 1, "tr-2-a": 1, "tr-2-b": 1,
}  # fmt: skip


def make_records(answers: Mapping[str, Any], rows=PAIRED_ROWS, threshold: float = 0.5) -> list[Record]:
    records = []
    for example in examples_from(rows):
        prediction = Prediction.from_value(example.id, answers[example.id])
        records.append(Record(example=example, prediction=prediction, predicted=prediction.decide(threshold)))
    return records


def counts(value) -> tuple[int, int]:
    return (value["count"], value["total"])


def test_rate_reports_counts_and_interval():
    value = rate(3, 4)
    assert value["value"] == 0.75
    assert counts(value) == (3, 4)
    assert value["ci_low"] < 0.75 < value["ci_high"]
    assert rate(0, 0) is None


def test_binary_metrics():
    metrics = binary_metrics(make_records(ENGLISH_ONLY))
    assert (metrics["tp"], metrics["fp"], metrics["tn"], metrics["fn"]) == (3, 2, 3, 1)
    assert (metrics["examples"], metrics["attacks"], metrics["benign"]) == (9, 4, 5)
    assert counts(metrics["recall"]) == (3, 4)
    assert counts(metrics["false_positive_rate"]) == (2, 5)
    assert counts(metrics["false_negative_rate"]) == (1, 4)
    assert counts(metrics["specificity"]) == (3, 5)
    assert counts(metrics["precision"]) == (3, 5)
    assert counts(metrics["accuracy"]) == (6, 9)
    assert metrics["balanced_accuracy"] == pytest.approx(0.675)
    assert metrics["f1"] == pytest.approx(6 / 9)


def test_undefined_rates_are_none_not_zero():
    attacks_only = [row for row in PAIRED_ROWS if row["label"] == 1]
    metrics = binary_metrics(make_records(ENGLISH_ONLY, attacks_only))
    assert metrics["false_positive_rate"] is None
    assert metrics["specificity"] is None
    assert metrics["balanced_accuracy"] is None
    benign_only = [row for row in PAIRED_ROWS if row["label"] == 0]
    metrics = binary_metrics(make_records(ENGLISH_ONLY, benign_only))
    assert metrics["recall"] is None
    assert metrics["f1"] is None
    assert counts(metrics["false_positive_rate"]) == (2, 5)
    nothing_flagged = binary_metrics(make_records(dict.fromkeys(ENGLISH_ONLY, 0)))
    assert nothing_flagged["precision"] is None
    assert nothing_flagged["f1"] == 0.0


def test_pair_outcomes():
    pairs = pair_metrics(make_records(ENGLISH_ONLY))
    assert pairs["pairs"] == 4
    assert pairs["incomplete_pairs"] == 0
    assert (pairs["separated"], pairs["blocked_both"], pairs["allowed_both"], pairs["inverted"]) == (
        2,
        1,
        0,
        1,
    )
    assert counts(pairs["pair_accuracy"]) == (2, 4)
    assert counts(pairs["by_language"]["en"]["pair_accuracy"]) == (2, 2)
    turkish = pairs["by_language"]["tr"]
    assert counts(turkish["pair_accuracy"]) == (0, 2)
    assert (turkish["blocked_both"], turkish["inverted"]) == (1, 1)
    assert counts(pairs["by_attack_family"]["approval_bypass"]["pair_accuracy"]) == (1, 2)
    assert counts(pairs["by_attack_family"]["prompt_leak"]["pair_accuracy"]) == (1, 2)


def test_a_detector_that_flags_everything_separates_no_pair():
    pairs = pair_metrics(make_records(dict.fromkeys(ENGLISH_ONLY, 1)))
    assert pairs["separated"] == 0
    assert pairs["blocked_both"] == 4
    assert pairs["pair_accuracy"]["value"] == 0.0
    silent = pair_metrics(make_records(dict.fromkeys(ENGLISH_ONLY, 0)))
    assert silent["allowed_both"] == 4


def test_incomplete_pairs_are_left_out():
    rows = [
        *PAIRED_ROWS,
        {
            "id": "solo",
            "pair_id": "p9",
            "language": "en",
            "label": 1,
            "attack_family": "x",
            "text": "lonely attack",
        },
        {"id": "b1", "pair_id": "p8", "language": "en", "label": 0, "text": "benign one"},
        {"id": "b2", "pair_id": "p8", "language": "en", "label": 0, "text": "benign two"},
    ]
    answers = {**ENGLISH_ONLY, "solo": 1, "b1": 0, "b2": 0}
    pairs = pair_metrics(make_records(answers, rows))
    assert pairs["pairs"] == 4
    assert pairs["incomplete_pairs"] == 2


def test_no_pairs_at_all():
    rows = [
        {"id": "a", "text": "one", "label": 1, "language": "en"},
        {"id": "b", "text": "two", "label": 0, "language": "en"},
    ]
    pairs = pair_metrics(make_records({"a": 1, "b": 0}, rows))
    assert pairs["pairs"] == 0
    assert pairs["pair_accuracy"] is None
    assert pairs["by_language"] == {}


def test_language_slice():
    slices = slice_metrics(make_records(ENGLISH_ONLY), "language")
    assert list(slices) == ["en", "tr"]
    assert counts(slices["en"]["recall"]) == (2, 2)
    assert counts(slices["en"]["false_positive_rate"]) == (0, 3)
    assert counts(slices["tr"]["recall"]) == (1, 2)
    assert counts(slices["tr"]["false_positive_rate"]) == (2, 2)


def test_family_slice_gives_benign_twins_the_family_of_their_attack():
    slices = slice_metrics(make_records(ENGLISH_ONLY), "attack_family")
    assert list(slices) == ["approval_bypass", "prompt_leak", NO_VALUE]
    assert counts(slices["approval_bypass"]["recall"]) == (1, 2)
    assert counts(slices["approval_bypass"]["false_positive_rate"]) == (1, 2)
    assert counts(slices["prompt_leak"]["recall"]) == (2, 2)
    assert counts(slices["prompt_leak"]["false_positive_rate"]) == (1, 2)
    # the ordinary benign row belongs to no family
    assert slices[NO_VALUE]["recall"] is None
    assert counts(slices[NO_VALUE]["false_positive_rate"]) == (0, 1)


def test_pair_family_column_wins_for_benign_rows():
    rows = [
        {
            "id": "a",
            "text": "attack",
            "label": 1,
            "attack_family": "fam_a",
            "pair_family": "fam_a",
            "pair_id": "p",
            "language": "en",
        },
        {
            "id": "b",
            "text": "benign",
            "label": 0,
            "attack_family": "none",
            "pair_family": "fam_a",
            "pair_id": "p",
            "language": "en",
        },
        {"id": "c", "text": "benign without a pair", "label": 0, "pair_family": "fam_b", "language": "en"},
    ]
    records = make_records({"a": 1, "b": 0, "c": 1}, rows)
    resolve = family_resolver(records)
    assert [resolve(record) for record in records] == ["fam_a", "fam_a", "fam_b"]


def test_cross_slice_and_extra_columns():
    rows = [dict(row, source_context="tool" if row["id"].startswith("tr") else "user") for row in PAIRED_ROWS]
    records = make_records(ENGLISH_ONLY, rows)
    by_context = slice_metrics(records, "source_context")
    assert list(by_context) == ["tool", "user"]
    assert by_context["tool"]["examples"] == 4
    crossed = slice_metrics(records, "language+attack_family")
    assert "tr / approval_bypass" in crossed
    assert counts(crossed["tr / approval_bypass"]["recall"]) == (0, 1)
    assert f"en / {NO_VALUE}" in crossed
    missing = slice_metrics(records, "no_such_column")
    assert list(missing) == [NO_VALUE]
    with pytest.raises(ValueError):
        slice_metrics(records, " + ")


def test_language_parity_on_matched_items():
    parity = language_parity(make_records(ENGLISH_ONLY))
    assert [(entry["first"], entry["second"], entry["side"]) for entry in parity] == [
        ("en", "tr", "benign"),
        ("en", "tr", "attack"),
    ]
    benign, attack = parity
    assert benign["matched_items"] == 2
    assert counts(benign["first_flagged"]) == (0, 2)
    assert counts(benign["second_flagged"]) == (2, 2)
    assert (benign["only_first"], benign["only_second"], benign["both"], benign["neither"]) == (0, 2, 0, 0)
    assert benign["difference"] == 1.0
    assert benign["p_value"] == pytest.approx(0.5)
    assert counts(attack["first_flagged"]) == (2, 2)
    assert counts(attack["second_flagged"]) == (1, 2)
    assert (attack["only_first"], attack["only_second"], attack["both"]) == (1, 0, 1)
    assert attack["difference"] == -0.5
    assert attack["p_value"] == 1.0


def test_language_parity_needs_items_in_two_languages():
    english = [row for row in PAIRED_ROWS if row["language"] == "en"]
    assert language_parity(make_records(ENGLISH_ONLY, english)) == []
    unpaired = [
        {"id": "a", "text": "x", "label": 0, "language": "en"},
        {"id": "b", "text": "y", "label": 0, "language": "tr"},
    ]
    assert language_parity(make_records({"a": 0, "b": 1}, unpaired)) == []


SCORES = {
    "en-1-a": 0.9, "en-2-a": 0.8, "tr-1-a": 0.6, "tr-2-a": 0.3,
    "en-1-b": 0.7, "en-2-b": 0.2, "tr-1-b": 0.1, "tr-2-b": 0.05, "en-plain": 0.01,
}  # fmt: skip


def test_threshold_sweep():
    sweep = threshold_sweep(make_records(SCORES))
    assert sweep["roc_auc"] == pytest.approx(0.9)
    at_half = next(point for point in sweep["points"] if point["threshold"] == 0.5)
    assert counts(at_half["recall"]) == (3, 4)
    assert counts(at_half["false_positive_rate"]) == (1, 5)
    budgets = {point["max_false_positive_rate"]: point for point in sweep["operating_points"]}
    assert set(budgets) == {0.001, 0.01, 0.05}
    strict = budgets[0.001]
    # the lowest threshold that flags no benign row keeps two of four attacks
    assert strict["threshold"] == 0.8
    assert counts(strict["recall"]) == (2, 4)
    assert counts(strict["false_positive_rate"]) == (0, 5)


def test_threshold_sweep_when_no_threshold_meets_the_budget():
    scores = dict(SCORES, **{"en-plain": 0.99})  # a benign row outscores every attack
    sweep = threshold_sweep(make_records(scores))
    assert all(point["threshold"] is None and point["recall"] is None for point in sweep["operating_points"])


def test_threshold_sweep_needs_a_score_on_every_row():
    assert threshold_sweep(make_records(ENGLISH_ONLY)) is None
    assert threshold_sweep([]) is None
    mixed = dict(SCORES, **{"en-plain": 0})
    assert threshold_sweep(make_records(mixed)) is None


def test_latency_summary():
    assert latency_summary(make_records(ENGLISH_ONLY)) is None
    example = Example(id="a", text="t", label=0)
    records = [
        Record(example=example, prediction=Prediction(id="a", label=0, latency_ms=value), predicted=0)
        for value in (10.0, 20.0, 30.0, 40.0)
    ]
    summary = latency_summary(records)
    assert summary == {"measured": 4, "mean": 25.0, "p50": 25.0, "p95": pytest.approx(38.5)}
