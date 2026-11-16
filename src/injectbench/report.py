"""Render a report as Markdown, JSON or SARIF.

Reports never contain input text, only identifiers and counts, so they are
safe to publish even when the dataset holds attack payloads.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .metrics import NO_VALUE
from .models import InjectBenchError, Record

__all__ = [
    "FORMATS",
    "format_rate",
    "predictions_jsonl",
    "render",
    "to_json",
    "to_markdown",
    "to_sarif",
    "write_text",
]

FORMATS: tuple[str, ...] = ("markdown", "json", "sarif")
_HOMEPAGE = "https://github.com/3nesdeniz/injectbench"


class ReportError(InjectBenchError):
    """A report cannot be rendered or written."""


def _percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_rate(value: Mapping[str, Any] | None, *, interval: bool = True) -> str:
    """``12.5% (8.1–18.7%) 15/120`` or ``n/a``."""

    if value is None:
        return "n/a"
    text = _percent(value["value"])
    if interval:
        text += f" ({_percent(value['ci_low'])[:-1]}–{_percent(value['ci_high'])})"
    return f"{text} {value['count']}/{value['total']}"


def _number(value: Any, digits: int = 3) -> str:
    return "n/a" if value is None else f"{float(value):.{digits}f}"


def _table(headers: Sequence[str], rows: Sequence[Sequence[str]], *, numeric_from: int = 1) -> list[str]:
    alignment = ["---" if index < numeric_from else "---:" for index in range(len(headers))]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(alignment) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def _code(value: Any) -> str:
    text = str(value)
    return text if text == NO_VALUE else f"`{text}`"


def _dataset_lines(report: Mapping[str, Any]) -> list[str]:
    dataset = report["dataset"]
    revision = dataset.get("resolved_revision") or dataset.get("revision")
    lines = [
        f"- **Dataset:** `{dataset['source']}`"
        + (f" at `{revision}`" if revision else "")
        + f", split `{dataset['split']}`",
        f"- **Examples:** {dataset['examples']} ({dataset['attacks']} attacks, {dataset['benign']} benign)",
    ]
    pairs = dataset.get("pairs") or {}
    if pairs.get("complete"):
        lines.append(f"- **Matched pairs:** {pairs['complete']}")
    return lines


def _detector_lines(report: Mapping[str, Any]) -> list[str]:
    detector = report["detector"]
    run = report["run"]
    lines = [f"- **Detector:** `{detector['name']}`"]
    if detector.get("commit"):
        lines[-1] += f" at `{detector['commit']}`"
    if run["decisions_from_score"]:
        lines.append(f"- **Threshold:** {run['threshold']:g} (flag when score >= threshold)")
    if run["decisions_from_label"]:
        lines.append(f"- **Decisions taken from the detector's own label:** {run['decisions_from_label']}")
    if detector.get("truncated_inputs"):
        lines.append(
            f"- **Inputs truncated to {detector['max_length']} tokens:** {detector['truncated_inputs']}"
        )
    if detector.get("attack_labels_assumed"):
        lines.append(
            "- **Note:** the model only names its outputs `LABEL_0`/`LABEL_1`; "
            "`LABEL_1` was assumed to mean attack"
        )
    coverage = report["coverage"]
    lines.append(
        f"- **Coverage:** {coverage['evaluated']}/{coverage['evaluated'] + coverage['failed']} rows"
        + (f" ({coverage['failed']} failed)" if coverage["failed"] else "")
    )
    lines.append(
        f"- **Run:** {run['created_at']}, InjectBench {report['tool']['version']}, "
        f"{run['confidence'] * 100:g}% Wilson confidence intervals"
    )
    return lines


def _headline(report: Mapping[str, Any]) -> list[str]:
    metrics = report["metrics"]
    pairs = report["pairs"]
    rows = [
        ["Attacks caught (recall)", format_rate(metrics["recall"])],
        ["Benign inputs flagged (false-positive rate)", format_rate(metrics["false_positive_rate"])],
    ]
    if pairs["pairs"]:
        rows.append(["Pairs separated (pair accuracy)", format_rate(pairs["pair_accuracy"])])
    rows.extend(
        [
            ["Precision", format_rate(metrics["precision"])],
            ["Balanced accuracy", _number(metrics["balanced_accuracy"])],
            ["F1", _number(metrics["f1"])],
            ["TP / FP / TN / FN", f"{metrics['tp']} / {metrics['fp']} / {metrics['tn']} / {metrics['fn']}"],
        ]
    )
    sweep = report.get("sweep")
    if sweep and sweep.get("roc_auc") is not None:
        rows.append(["ROC AUC", _number(sweep["roc_auc"])])
    return _table(["Metric", "Value"], rows)


def _pairs_section(report: Mapping[str, Any]) -> list[str]:
    pairs = report["pairs"]
    if not pairs["pairs"]:
        return []
    lines = [
        "## Matched pairs",
        "",
        "Each attack has a benign twin with the same topic and vocabulary. "
        "A pair counts only when the attack is flagged and the twin is not.",
        "",
        *_table(
            ["Outcome", "Pairs"],
            [
                ["Separated: attack flagged, twin cleared", str(pairs["separated"])],
                ["Blocked both: reacts to the shared wording", str(pairs["blocked_both"])],
                ["Allowed both: attack missed", str(pairs["allowed_both"])],
                ["Inverted: twin flagged, attack missed", str(pairs["inverted"])],
            ],
        ),
    ]
    if pairs.get("incomplete_pairs"):
        lines.extend(["", f"{pairs['incomplete_pairs']} incomplete pair ids were left out."])
    for title, key in (("language", "by_language"), ("attack family", "by_attack_family")):
        groups = pairs.get(key) or {}
        if len(groups) > 1:
            lines.extend(
                [
                    "",
                    f"### Pair accuracy by {title}",
                    "",
                    *_table(
                        [
                            title.capitalize(),
                            "Pairs",
                            "Pair accuracy",
                            "Blocked both",
                            "Allowed both",
                            "Inverted",
                        ],
                        [
                            [
                                _code(name),
                                str(group["pairs"]),
                                format_rate(group["pair_accuracy"]),
                                str(group["blocked_both"]),
                                str(group["allowed_both"]),
                                str(group["inverted"]),
                            ]
                            for name, group in groups.items()
                        ],
                    ),
                ]
            )
    return [*lines, ""]


def _slices_section(report: Mapping[str, Any]) -> list[str]:
    lines: list[str] = []
    for dimension, groups in report["slices"].items():
        if len(groups) < 2:
            continue  # a single group repeats the summary
        title = dimension.replace("+", " and ").replace("_", " ")
        lines.extend(
            [
                f"## By {title}",
                "",
                *_table(
                    [title.capitalize(), "Rows", "Recall", "False-positive rate"],
                    [
                        [
                            _code(name),
                            str(group["examples"]),
                            format_rate(group["recall"]),
                            format_rate(group["false_positive_rate"]),
                        ]
                        for name, group in groups.items()
                    ],
                ),
                "",
            ]
        )
    return lines


def _parity_section(report: Mapping[str, Any]) -> list[str]:
    parity = report.get("language_parity") or []
    if not parity:
        return []
    rows = []
    for entry in parity:
        p_value = entry["p_value"]
        rows.append(
            [
                f"{entry['side']} inputs, `{entry['first']}` vs `{entry['second']}`",
                str(entry["matched_items"]),
                format_rate(entry["first_flagged"]),
                format_rate(entry["second_flagged"]),
                f"{entry['only_first']} / {entry['only_second']}",
                "n/a" if p_value is None else (f"{p_value:.4f}" if p_value >= 0.0001 else "<0.0001"),
            ]
        )
    return [
        "## Language parity on matched items",
        "",
        "The same item in two languages. For benign inputs a flag is a false positive; "
        "for attacks a flag is a catch.",
        "",
        *_table(
            [
                "Comparison",
                "Items",
                "Flagged in first",
                "Flagged in second",
                "Only first / only second",
                "p (McNemar)",
            ],
            rows,
        ),
        "",
    ]


def _sweep_section(report: Mapping[str, Any]) -> list[str]:
    sweep = report.get("sweep")
    if not sweep or not sweep.get("operating_points"):
        return []
    rows = []
    for point in sweep["operating_points"]:
        rows.append(
            [
                f"at most {_percent(point['max_false_positive_rate'])} of benign inputs flagged",
                "n/a" if point["threshold"] is None else f"{point['threshold']:.4f}",
                format_rate(point["recall"]),
                format_rate(point["false_positive_rate"]),
            ]
        )
    return [
        "## Other thresholds",
        "",
        "The best recall this detector reaches on this dataset under a false-positive budget. "
        "The thresholds are fitted to these rows; choose production thresholds on separate data.",
        "",
        *_table(["Budget", "Threshold", "Recall", "False-positive rate"], rows),
        "",
    ]


def _gates_section(report: Mapping[str, Any]) -> list[str]:
    gates = report.get("gates") or []
    if not gates:
        return []
    rows = [
        [
            f"`{gate['name']}`",
            f"{gate['limit']:.4f}",
            "n/a" if gate["observed"] is None else f"{gate['observed']:.4f}",
            gate["basis"],
            "pass" if gate["passed"] else "**FAIL**",
        ]
        for gate in gates
    ]
    return ["## Gates", "", *_table(["Gate", "Limit", "Observed", "Basis", "Result"], rows), ""]


def to_markdown(report: Mapping[str, Any]) -> str:
    """Render a human-readable Markdown report."""

    lines = [
        f"# InjectBench report: `{report['detector']['name']}`",
        "",
        *_dataset_lines(report),
        *_detector_lines(report),
        "",
        "## Summary",
        "",
        *_headline(report),
        "",
        *_gates_section(report),
        *_pairs_section(report),
        *_slices_section(report),
        *_parity_section(report),
        *_sweep_section(report),
    ]
    latency = report.get("latency_ms")
    if latency:
        lines.extend(
            [
                "## Latency",
                "",
                f"Mean {latency['mean']:.1f} ms, median {latency['p50']:.1f} ms, "
                f"95th percentile {latency['p95']:.1f} ms per input ({latency['measured']} measured).",
                "",
            ]
        )
    warnings = report["dataset"].get("warnings") or []
    if warnings:
        lines.extend(["## Dataset notes", "", *[f"- {warning}" for warning in warnings], ""])
    if report.get("errors"):
        lines.extend(
            [
                "## Failed rows",
                "",
                f"{len(report['errors'])} rows got no prediction and are not part of the numbers above. "
                "Their ids are in the JSON report.",
                "",
            ]
        )
    lines.extend(
        [
            "## How to read this",
            "",
            "These numbers describe one detector on one dataset. The ranges in brackets are "
            "Wilson confidence intervals at the level stated above: with few rows they are wide, "
            "and a rate of 0% still has an upper bound above zero. A good result here is evidence "
            "about these inputs, not proof that a system is secure against attacks it has not seen.",
            "",
        ]
    )
    return "\n".join(lines)


def to_json(report: Mapping[str, Any]) -> str:
    """Render the machine-readable report."""

    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def to_sarif(report: Mapping[str, Any]) -> str:
    """Render SARIF 2.1.0 so results can appear in code-scanning dashboards.

    Every gate becomes a result (``error`` when it failed). Without gates the
    headline metrics are attached as notes.
    """

    metrics = report["metrics"]
    pairs = report["pairs"]
    rules = [
        {
            "id": "false-positive-rate",
            "name": "BenignFalsePositiveRate",
            "shortDescription": {"text": "Share of benign inputs flagged as attacks."},
            "helpUri": _HOMEPAGE,
        },
        {
            "id": "recall",
            "name": "AttackRecall",
            "shortDescription": {"text": "Share of attacks flagged."},
            "helpUri": _HOMEPAGE,
        },
        {
            "id": "pair-accuracy",
            "name": "PairAccuracy",
            "shortDescription": {
                "text": "Share of matched pairs where the attack is flagged and its benign twin is not."
            },
            "helpUri": _HOMEPAGE,
        },
    ]
    values = {
        "false-positive-rate": metrics["false_positive_rate"],
        "recall": metrics["recall"],
        "pair-accuracy": pairs["pair_accuracy"],
    }
    gate_by_metric = {
        {"false_positive_rate": "false-positive-rate", "recall": "recall", "pair_accuracy": "pair-accuracy"}[
            gate["metric"]
        ]: gate
        for gate in report.get("gates") or []
    }
    results = []
    for rule_id, value in values.items():
        gate = gate_by_metric.get(rule_id)
        text = f"{rule_id}: {format_rate(value)}"
        level = "note"
        if gate is not None:
            verdict = "passed" if gate["passed"] else "failed"
            text += f". Gate {gate['name']} {gate['limit']:g} {verdict} ({gate['basis']})."
            level = "note" if gate["passed"] else "error"
        elif value is None:
            continue
        results.append({"ruleId": rule_id, "level": level, "message": {"text": text}})
    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "InjectBench",
                        "version": report["tool"]["version"],
                        "informationUri": _HOMEPAGE,
                        "rules": rules,
                    }
                },
                "properties": {
                    "detector": report["detector"]["name"],
                    "dataset": report["dataset"]["source"],
                    "split": report["dataset"]["split"],
                    "threshold": report["run"]["threshold"],
                },
                "results": results,
            }
        ],
    }
    return json.dumps(sarif, ensure_ascii=False, indent=2) + "\n"


def render(report: Mapping[str, Any], fmt: str) -> str:
    """Render ``report`` in one of :data:`FORMATS` (``md`` is accepted for Markdown)."""

    name = fmt.lower()
    if name in ("markdown", "md"):
        return to_markdown(report)
    if name == "json":
        return to_json(report)
    if name == "sarif":
        return to_sarif(report)
    raise ReportError(f"unknown report format {fmt!r}; choose from: {', '.join(FORMATS)}")


def predictions_jsonl(records: Sequence[Record]) -> str:
    """Row-level decisions, without the input text."""

    lines = []
    for record in records:
        example = record.example
        lines.append(
            json.dumps(
                {
                    "id": example.id,
                    "label": example.label,
                    "prediction": record.predicted,
                    "score": record.prediction.score,
                    "correct": record.correct,
                    "language": example.language,
                    "attack_family": example.attack_family,
                    "pair_id": example.pair_id,
                    "latency_ms": record.prediction.latency_ms,
                },
                ensure_ascii=False,
            )
        )
    return "\n".join(lines) + "\n"


def write_text(path: str | Path, content: str) -> Path:
    """Write a file atomically, creating parent directories."""

    target = Path(path).expanduser()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".part")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)
    except OSError as exc:
        raise ReportError(f"could not write {target}: {exc}") from exc
    return target
