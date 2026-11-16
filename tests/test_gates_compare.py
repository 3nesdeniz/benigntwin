from __future__ import annotations

import json

import pytest

from conftest import PAIRED_ROWS, ScriptedDetector, examples_from
from injectbench.compare import CompareError, compare_reports, load_report, render_comparison
from injectbench.evaluate import evaluate
from injectbench.gates import EXIT_FPR, EXIT_OK, EXIT_PAIR, EXIT_RECALL, check_gates, exit_code
from injectbench.report import to_json
from test_metrics import ENGLISH_ONLY, SCORES


@pytest.fixture
def report(paired_examples):
    # recall 3/4, false-positive rate 2/5, pair accuracy 2/4
    return evaluate(paired_examples, ScriptedDetector(ENGLISH_ONLY)).report


def test_no_gates_requested(report):
    assert check_gates(report) == []
    assert exit_code([]) == EXIT_OK


def test_gates_on_point_estimates(report):
    passing = check_gates(report, max_fpr=0.4, min_recall=0.75, min_pair_accuracy=0.5)
    assert [gate.passed for gate in passing] == [True, True, True]
    assert exit_code(passing) == EXIT_OK
    assert passing[0].message == "max-fpr: 0.4000 (point estimate) must be <= 0.4000: ok"

    assert exit_code(check_gates(report, max_fpr=0.39)) == EXIT_FPR
    assert exit_code(check_gates(report, min_recall=0.76)) == EXIT_RECALL
    assert exit_code(check_gates(report, min_pair_accuracy=0.51)) == EXIT_PAIR
    # the first failing gate decides the exit status
    several = check_gates(report, max_fpr=0.1, min_recall=0.9, min_pair_accuracy=0.9)
    assert exit_code(several) == EXIT_FPR
    assert "FAILED" in several[0].message


def test_conservative_gates_use_the_unfavourable_bound(report):
    relaxed = check_gates(report, max_fpr=0.45, min_recall=0.7)
    assert all(gate.passed for gate in relaxed)
    strict = check_gates(report, max_fpr=0.45, min_recall=0.7, conservative=True)
    assert [gate.passed for gate in strict] == [False, False]
    assert strict[0].basis == "confidence bound"
    assert strict[0].observed == report["metrics"]["false_positive_rate"]["ci_high"]
    assert strict[1].observed == report["metrics"]["recall"]["ci_low"]


def test_zero_false_positives_do_not_pass_a_conservative_gate_on_a_tiny_set():
    rows = [
        {"id": f"b{index}", "text": f"benign question {index}", "label": 0, "language": "en"}
        for index in range(40)
    ]
    clean = evaluate(examples_from(rows), ScriptedDetector({}, default=0)).report
    assert clean["metrics"]["false_positive_rate"]["value"] == 0.0
    assert exit_code(check_gates(clean, max_fpr=0.05)) == EXIT_OK
    conservative = check_gates(clean, max_fpr=0.05, conservative=True)
    assert conservative[0].observed == pytest.approx(0.0876, abs=1e-3)
    assert exit_code(conservative) == EXIT_FPR


def test_a_gate_on_a_metric_that_cannot_be_measured_fails():
    attacks = [row for row in PAIRED_ROWS if row["label"] == 1]
    answers = {row["id"]: 1 for row in attacks}
    report = evaluate(examples_from(attacks), ScriptedDetector(answers)).report
    gates = check_gates(report, max_fpr=0.5, min_pair_accuracy=0.1, min_recall=0.5)
    assert [(gate.name, gate.passed, gate.observed) for gate in gates] == [
        ("max-fpr", False, None),
        ("min-recall", True, 1.0),
        ("min-pair-accuracy", False, None),
    ]
    assert "cannot be measured" in gates[0].message
    assert gates[0].as_dict() == {
        "name": "max-fpr",
        "metric": "false_positive_rate",
        "limit": 0.5,
        "observed": None,
        "basis": "point estimate",
        "passed": False,
    }


# ---------------------------------------------------------------- compare


def _save(tmp_path, name, report):
    path = tmp_path / name
    path.write_text(to_json(report), encoding="utf-8")
    return path


def test_compare_sorts_and_checks_the_data(tmp_path, write_jsonl, paired_examples):
    from injectbench.datasets import load_dataset

    dataset = load_dataset(write_jsonl(PAIRED_ROWS))
    weak = evaluate(dataset, ScriptedDetector(ENGLISH_ONLY)).report
    weak["detector"]["name"] = "english-only"
    perfect_answers = {row["id"]: row["label"] for row in PAIRED_ROWS}
    strong = evaluate(dataset, ScriptedDetector(perfect_answers)).report
    strong["detector"]["name"] = "oracle"
    scored = evaluate(dataset, ScriptedDetector(SCORES)).report
    scored["detector"]["name"] = "scored"

    loaded = [
        load_report(_save(tmp_path, f"{index}.json", item))
        for index, item in enumerate((weak, strong, scored))
    ]
    comparison = compare_reports(loaded)
    assert comparison["same_dataset"] is True
    assert [row["detector"] for row in comparison["rows"]] == ["oracle", "english-only", "scored"]
    assert comparison["rows"][0]["pair_accuracy"]["value"] == 1.0
    assert comparison["rows"][2]["roc_auc"] == pytest.approx(0.9)

    by_fpr = compare_reports(loaded, sort_by="false_positive_rate")
    assert [row["detector"] for row in by_fpr["rows"]] == ["oracle", "scored", "english-only"]
    by_name = compare_reports(loaded, sort_by="detector")
    assert [row["detector"] for row in by_name["rows"]] == ["english-only", "oracle", "scored"]

    text = render_comparison(comparison)
    assert text.startswith("# InjectBench comparison on `")
    assert "| `oracle` | 100.0% (" in text
    assert "not computed on the same data" not in text
    assert json.loads(render_comparison(comparison, "json"))["sorted_by"] == "pair_accuracy"

    other = evaluate(paired_examples[:4], ScriptedDetector(ENGLISH_ONLY)).report
    mixed = compare_reports([weak, other])
    assert mixed["same_dataset"] is False
    assert "not computed on the same data" in render_comparison(mixed)


def test_reports_without_pairs_sort_last():
    rows = [
        {"id": "a", "text": "an attack", "label": 1, "language": "en"},
        {"id": "b", "text": "a question", "label": 0, "language": "en"},
    ]
    unpaired = evaluate(examples_from(rows), ScriptedDetector({"a": 1, "b": 0})).report
    unpaired["detector"]["name"] = "unpaired"
    paired = evaluate(examples_from(PAIRED_ROWS), ScriptedDetector(ENGLISH_ONLY)).report
    comparison = compare_reports([unpaired, paired])
    assert [row["detector"] for row in comparison["rows"]] == ["scripted", "unpaired"]
    assert comparison["rows"][1]["pair_accuracy"] is None
    assert "| `unpaired` | 100.0% (" in render_comparison(comparison)


def test_compare_errors(tmp_path, report):
    with pytest.raises(CompareError, match="nothing to compare"):
        compare_reports([])
    with pytest.raises(CompareError, match="sort key must be one of"):
        compare_reports([report], sort_by="stars")
    with pytest.raises(CompareError, match="unknown comparison format"):
        render_comparison(compare_reports([report]), "html")
    with pytest.raises(CompareError, match="could not read"):
        load_report(tmp_path / "absent.json")
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    with pytest.raises(CompareError, match="invalid JSON"):
        load_report(broken)
    other = tmp_path / "other.json"
    other.write_text('{"hello": "world"}', encoding="utf-8")
    with pytest.raises(CompareError, match="not an InjectBench report"):
        load_report(other)
    old = dict(report, schema_version="1.0")
    with pytest.raises(CompareError, match=r"schema '1\.0' is not supported"):
        load_report(_save(tmp_path, "old.json", old))
