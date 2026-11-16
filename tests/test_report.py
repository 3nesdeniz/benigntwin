from __future__ import annotations

import json

import pytest

from benigntwin.evaluate import evaluate
from benigntwin.gates import check_gates
from benigntwin.models import BenignTwinError
from benigntwin.report import (
    format_rate,
    predictions_jsonl,
    render,
    to_json,
    to_markdown,
    to_sarif,
    write_text,
)
from conftest import PAIRED_ROWS, ScriptedDetector, examples_from
from test_metrics import ENGLISH_ONLY, SCORES


@pytest.fixture
def result(paired_examples):
    return evaluate(paired_examples, ScriptedDetector(ENGLISH_ONLY))


def test_format_rate():
    assert format_rate(None) == "n/a"
    value = {"value": 0.125, "ci_low": 0.0812, "ci_high": 0.1871, "count": 15, "total": 120}
    assert format_rate(value) == "12.5% (8.1–18.7%) 15/120"
    assert format_rate(value, interval=False) == "12.5% 15/120"


def test_markdown_report(result):
    text = to_markdown(result.report)
    assert text.startswith("# BenignTwin report: `scripted`\n")
    assert "- **Examples:** 9 (4 attacks, 5 benign)" in text
    assert "- **Matched pairs:** 4" in text
    assert "| Attacks caught (recall) | 75.0% (" in text and " 3/4 |" in text
    assert "| Benign inputs flagged (false-positive rate) | 40.0% (" in text
    assert "| Pairs separated (pair accuracy) | 50.0% (" in text
    assert "| Separated: attack flagged, twin cleared | 2 |" in text
    assert "| Inverted: twin flagged, attack missed | 1 |" in text
    assert "### Pair accuracy by language" in text
    assert "## By language" in text and "## By attack family" in text
    assert "| `tr` | 4 |" in text
    assert "## Language parity on matched items" in text
    assert "benign inputs, `en` vs `tr`" in text
    assert "## How to read this" in text
    assert "## Other thresholds" not in text  # label-only detector
    assert "## Gates" not in text


def test_markdown_shows_thresholds_gates_notes_and_failures(paired_examples):
    scored = evaluate(paired_examples, ScriptedDetector(SCORES))
    scored.report["gates"] = [gate.as_dict() for gate in check_gates(scored.report, max_fpr=0.1)]
    text = to_markdown(scored.report)
    assert "- **Threshold:** 0.5 (flag when score >= threshold)" in text
    assert "## Other thresholds" in text
    assert "at most 1.0% of benign inputs flagged" in text
    assert "| ROC AUC | 0.900 |" in text
    assert "## Gates" in text and "| `max-fpr` | 0.1000 | 0.2000 | point estimate | **FAIL** |" in text

    rows = [{"id": "a", "text": "an attack", "label": 1}, {"id": "b", "text": "a question", "label": 0}]
    answers = {"a": RuntimeError("down"), "b": 0}
    partial = evaluate(examples_from(rows), ScriptedDetector(answers), allow_errors=True)
    text = to_markdown(partial.report)
    assert "## Dataset notes" in text and "no language tag" in text
    assert "## Failed rows" in text and "1 rows got no prediction" in text
    assert "(1 failed)" in text
    assert "| Attacks caught (recall) | n/a |" in text


def test_no_report_format_contains_input_text(result):
    texts = [row["text"] for row in PAIRED_ROWS]
    outputs = [
        to_markdown(result.report),
        to_json(result.report),
        to_sarif(result.report),
        predictions_jsonl(result.records),
    ]
    for output in outputs:
        assert not any(text in output for text in texts)


def test_json_round_trip(result):
    assert json.loads(to_json(result.report)) == result.report


def test_sarif_structure(result):
    sarif = json.loads(to_sarif(result.report))
    assert sarif["version"] == "2.1.0"
    run = sarif["runs"][0]
    assert run["tool"]["driver"]["name"] == "BenignTwin"
    assert [rule["id"] for rule in run["tool"]["driver"]["rules"]] == [
        "false-positive-rate",
        "recall",
        "pair-accuracy",
    ]
    assert [item["ruleId"] for item in run["results"]] == ["false-positive-rate", "recall", "pair-accuracy"]
    assert {item["level"] for item in run["results"]} == {"note"}
    assert run["properties"]["detector"] == "scripted"


def test_sarif_marks_failed_gates_as_errors(result):
    gates = check_gates(result.report, max_fpr=0.05, min_recall=0.5)
    result.report["gates"] = [gate.as_dict() for gate in gates]
    results = {item["ruleId"]: item for item in json.loads(to_sarif(result.report))["runs"][0]["results"]}
    assert results["false-positive-rate"]["level"] == "error"
    assert "Gate max-fpr 0.05 failed" in results["false-positive-rate"]["message"]["text"]
    assert results["recall"]["level"] == "note"
    assert "Gate min-recall 0.5 passed" in results["recall"]["message"]["text"]


def test_sarif_skips_metrics_that_do_not_exist():
    rows = [{"id": "a", "text": "an attack", "label": 1, "language": "en"}]
    report = evaluate(examples_from(rows), ScriptedDetector({"a": 1})).report
    results = json.loads(to_sarif(report))["runs"][0]["results"]
    assert [item["ruleId"] for item in results] == ["recall"]


def test_render_dispatch(result):
    assert render(result.report, "md") == to_markdown(result.report)
    assert render(result.report, "JSON") == to_json(result.report)
    assert render(result.report, "sarif") == to_sarif(result.report)
    with pytest.raises(BenignTwinError, match="unknown report format 'pdf'"):
        render(result.report, "pdf")


def test_predictions_jsonl_can_be_scored_again(result):
    lines = [json.loads(line) for line in predictions_jsonl(result.records).splitlines()]
    assert len(lines) == 9
    first = lines[0]
    assert set(first) == {
        "id", "label", "prediction", "score", "correct", "language", "attack_family", "pair_id", "latency_ms",
    }  # fmt: skip
    assert (first["id"], first["label"], first["prediction"], first["correct"]) == ("en-1-a", 1, 1, True)


def test_write_text_creates_directories(tmp_path):
    target = write_text(tmp_path / "reports" / "nested" / "report.md", "hello\n")
    assert target.read_text(encoding="utf-8") == "hello\n"
    assert not list(target.parent.glob("*.part"))
    blocker = tmp_path / "file"
    blocker.write_text("x", encoding="utf-8")
    with pytest.raises(BenignTwinError, match="could not write"):
        write_text(blocker / "child" / "report.md", "nope")
