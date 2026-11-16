"""Put several JSON reports side by side.

``injectbench compare a.json b.json`` prints one row per detector. Reports are
only comparable when they were computed on the same data, so the comparison
says so when the dataset fingerprints differ.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .models import InjectBenchError
from .report import format_rate

__all__ = ["CompareError", "compare_reports", "load_report", "render_comparison"]

_SORT_KEYS = ("pair_accuracy", "false_positive_rate", "recall", "detector")


class CompareError(InjectBenchError):
    """Reports cannot be loaded or compared."""


def load_report(path: str | Path) -> dict[str, Any]:
    """Read a JSON report written by ``injectbench evaluate --format json``."""

    source = Path(path).expanduser()
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CompareError(f"could not read {source}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CompareError(f"{source}: invalid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict) or "metrics" not in payload or "detector" not in payload:
        raise CompareError(f"{source}: not an InjectBench report")
    major = str(payload.get("schema_version", "")).split(".")[0]
    if major != "2":
        raise CompareError(
            f"{source}: report schema {payload.get('schema_version')!r} is not supported; "
            "re-run the evaluation with this version"
        )
    return payload


def _fingerprint(report: Mapping[str, Any]) -> tuple[Any, ...]:
    dataset = report["dataset"]
    hashes = tuple(sorted(entry["sha256"] for entry in dataset.get("files", [])))
    return (dataset["source"], dataset["split"], hashes or dataset.get("examples"))


def _value(entry: Mapping[str, Any] | None) -> float | None:
    return None if entry is None else float(entry["value"])


def compare_reports(
    reports: Sequence[Mapping[str, Any]],
    *,
    sort_by: str = "pair_accuracy",
) -> dict[str, Any]:
    """Build a comparison: one row per report plus a same-data check."""

    if not reports:
        raise CompareError("nothing to compare")
    if sort_by not in _SORT_KEYS:
        raise CompareError(f"sort key must be one of: {', '.join(_SORT_KEYS)}")
    rows = []
    for report in reports:
        metrics = report["metrics"]
        pairs = report["pairs"]
        rows.append(
            {
                "detector": report["detector"]["name"],
                "revision": report["detector"].get("commit"),
                "threshold": report["run"]["threshold"],
                "examples": metrics["examples"],
                "recall": metrics["recall"],
                "false_positive_rate": metrics["false_positive_rate"],
                "pair_accuracy": pairs["pair_accuracy"] if pairs["pairs"] else None,
                "balanced_accuracy": metrics["balanced_accuracy"],
                "roc_auc": (report.get("sweep") or {}).get("roc_auc"),
            }
        )

    def key(row: Mapping[str, Any]) -> tuple[Any, ...]:
        if sort_by == "detector":
            return (0, str(row["detector"]))
        value = _value(row[sort_by])
        if value is None:
            return (1, 0.0, str(row["detector"]))
        # Lower is better for false positives, higher for everything else.
        return (0, value if sort_by == "false_positive_rate" else -value, str(row["detector"]))

    rows.sort(key=key)
    fingerprints = {_fingerprint(report) for report in reports}
    first = reports[0]["dataset"]
    return {
        "dataset": {"source": first["source"], "split": first["split"]},
        "same_dataset": len(fingerprints) == 1,
        "sorted_by": sort_by,
        "rows": rows,
    }


def render_comparison(comparison: Mapping[str, Any], fmt: str = "markdown") -> str:
    """Render a comparison as Markdown or JSON."""

    if fmt.lower() == "json":
        return json.dumps(comparison, ensure_ascii=False, indent=2) + "\n"
    if fmt.lower() not in ("markdown", "md"):
        raise CompareError(f"unknown comparison format {fmt!r}; choose markdown or json")
    dataset = comparison["dataset"]
    lines = [
        f"# InjectBench comparison on `{dataset['source']}` ({dataset['split']})",
        "",
    ]
    if not comparison["same_dataset"]:
        lines.extend(
            [
                "> **These reports were not computed on the same data.** "
                "Differences between rows may come from the data, not from the detectors.",
                "",
            ]
        )
    lines.extend(
        [
            "| Detector | Recall | False-positive rate | Pair accuracy | Balanced accuracy | ROC AUC |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in comparison["rows"]:
        balanced = row["balanced_accuracy"]
        auc = row["roc_auc"]
        lines.append(
            f"| `{row['detector']}` | {format_rate(row['recall'])} | "
            f"{format_rate(row['false_positive_rate'])} | {format_rate(row['pair_accuracy'])} | "
            f"{'n/a' if balanced is None else f'{balanced:.3f}'} | "
            f"{'n/a' if auc is None else f'{auc:.3f}'} |"
        )
    lines.extend(
        [
            "",
            "Brackets are Wilson confidence intervals; the fraction is the count behind each rate. "
            "Rows whose intervals overlap are not clearly different.",
            "",
        ]
    )
    return "\n".join(lines)
