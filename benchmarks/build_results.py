"""Turn the raw reports of a suite run into the published results.

    python benchmarks/build_results.py

Reads ``results/raw/<dataset key>/<detector key>.json`` and writes:

* ``results/README.md``    the tables people read
* ``results/results.csv``  one row per dataset and detector
* ``results/results.json`` the same numbers with intervals and counts

Nothing here computes a metric: every number is copied from the reports that
``benchmarks/run_suite.py`` wrote.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
from typing import Any

from benigntwin import load_report
from benigntwin.report import format_rate, write_text

ROOT = Path(__file__).resolve().parents[1]
#: Wider category tables stay in the per-detector reports.
MAX_CATEGORY_COLUMNS = 5


def _value(entry: dict[str, Any] | None) -> float | None:
    return None if entry is None else entry["value"]


def _sort_key(report: dict[str, Any]) -> tuple[Any, ...]:
    pair = _value(report["pairs"]["pair_accuracy"]) if report["pairs"]["pairs"] else None
    fpr = _value(report["metrics"]["false_positive_rate"])
    recall = _value(report["metrics"]["recall"])
    if pair is not None:
        return (0, -pair, fpr if fpr is not None else 1.0)
    if recall is not None:
        return (1, -recall, fpr if fpr is not None else 1.0)
    return (2, fpr if fpr is not None else 1.0, 0.0)


def _table(headers: list[str], rows: list[list[str]], *, text: bool = False) -> list[str]:
    """A Markdown table. Number columns are right-aligned unless ``text`` is set."""

    rule = " --- |" if text else " ---: |"
    lines = ["| " + " | ".join(headers) + " |", "| --- |" + rule * (len(headers) - 1)]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def _name(report: dict[str, Any], titles: dict[str, str]) -> str:
    key = report["suite"]["detector_key"]
    mark = " †" if report["suite"].get("trained_on_this_dataset") else ""
    return f"`{titles.get(key, key)}`{mark}"


def _p_value(value: float | None) -> str:
    if value is None:
        return "n/a"
    return "<0.0001" if value < 0.0001 else f"{value:.4f}"


def dataset_section(
    entry: dict[str, Any], reports: list[dict[str, Any]], titles: dict[str, str]
) -> list[str]:
    reports = sorted(reports, key=_sort_key)
    first = reports[0]
    dataset = first["dataset"]
    has_pairs = any(report["pairs"]["pairs"] for report in reports)
    has_attacks = dataset["attacks"] > 0
    revision = dataset.get("resolved_revision") or dataset.get("revision") or ""
    lines = [
        f"## {entry['title']}",
        "",
        entry["note"],
        "",
        f"- Source: `{dataset['source']}`"
        + (f" at `{revision[:12]}`" if revision else "")
        + (f", file `{entry['hf_file']}`" if entry.get("hf_file") else f", split `{dataset['split']}`")
        + (
            f", rows where {', '.join(f'{k}={v}' for k, v in dataset['filters'].items())}"
            if dataset.get("filters")
            else ""
        ),
        f"- Rows: {dataset['examples']} ({dataset['attacks']} attacks, {dataset['benign']} benign)"
        + (f", {dataset['pairs']['complete']} matched pairs" if dataset["pairs"]["complete"] else ""),
        f"- Licence of the data: {entry.get('license', 'see the dataset card')}",
        "",
    ]

    headers = ["Detector"]
    if has_attacks:
        headers.append("Attacks caught")
    headers.append("Benign flagged")
    if has_pairs:
        headers.append("Pairs separated")
    if has_attacks:
        headers.append("ROC AUC")
    rows = []
    for report in reports:
        row = [_name(report, titles)]
        if has_attacks:
            row.append(format_rate(report["metrics"]["recall"]))
        row.append(format_rate(report["metrics"]["false_positive_rate"]))
        if has_pairs:
            row.append(format_rate(report["pairs"]["pair_accuracy"]))
        if has_attacks:
            auc = (report.get("sweep") or {}).get("roc_auc")
            row.append("n/a" if auc is None else f"{auc:.3f}")
        rows.append(row)
    lines.extend(_table(headers, rows))
    if any(report["suite"].get("trained_on_this_dataset") for report in reports):
        lines.extend(["", "† The developers of this model list the train split of this dataset as training data."])
    lines.append("")

    # False positives per category, for datasets that tag their benign rows.
    categories = first["slices"].get("category")
    if categories:
        benign_categories = [
            name for name, group in categories.items() if group["attacks"] == 0 and group["benign"] > 0
        ]
        if 1 < len(benign_categories) <= MAX_CATEGORY_COLUMNS:
            lines.extend(
                [
                    "Benign inputs flagged, by kind of benign input:",
                    "",
                    *_table(
                        ["Detector", *[f"`{name}`" for name in benign_categories]],
                        [
                            [
                                _name(report, titles),
                                *[
                                    format_rate(report["slices"]["category"][name]["false_positive_rate"])
                                    for name in benign_categories
                                ],
                            ]
                            for report in reports
                        ],
                    ),
                    "",
                ]
            )

    # The same items in two languages.
    if first.get("language_parity"):
        rows = []
        for report in reports:
            for item in report["language_parity"]:
                if item["side"] != "benign" and dataset["attacks"] == 0:
                    continue
                rows.append(
                    [
                        _name(report, titles),
                        f"{item['side']}, `{item['first']}` vs `{item['second']}`",
                        format_rate(item["first_flagged"]),
                        format_rate(item["second_flagged"]),
                        f"{item['only_first']} / {item['only_second']}",
                        _p_value(item["p_value"]),
                    ]
                )
        lines.extend(
            [
                "The same items in two languages (a flag on a benign item is a false positive):",
                "",
                *_table(
                    [
                        "Detector",
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
        )
    return lines


def flat_rows(reports: list[dict[str, Any]], titles: dict[str, str]) -> list[dict[str, Any]]:
    rows = []
    for report in reports:
        metrics, pairs = report["metrics"], report["pairs"]
        recall, fpr, pair = metrics["recall"], metrics["false_positive_rate"], pairs["pair_accuracy"]
        key = report["suite"]["detector_key"]
        rows.append(
            {
                "dataset": report["suite"]["dataset_key"],
                "detector": key,
                "model": titles.get(key, key),
                "model_commit": report["detector"].get("commit") or "",
                "dataset_revision": report["dataset"].get("resolved_revision") or "",
                "threshold": report["run"]["threshold"],
                "attacks": metrics["attacks"],
                "benign": metrics["benign"],
                "pairs": pairs["pairs"],
                "recall": _value(recall),
                "recall_ci_low": None if recall is None else recall["ci_low"],
                "recall_ci_high": None if recall is None else recall["ci_high"],
                "false_positive_rate": _value(fpr),
                "fpr_ci_low": None if fpr is None else fpr["ci_low"],
                "fpr_ci_high": None if fpr is None else fpr["ci_high"],
                "pair_accuracy": _value(pair),
                "pair_ci_low": None if pair is None else pair["ci_low"],
                "pair_ci_high": None if pair is None else pair["ci_high"],
                "roc_auc": (report.get("sweep") or {}).get("roc_auc"),
                "truncated_inputs": report["detector"].get("truncated_inputs", 0),
                "trained_on_this_dataset": bool(report["suite"].get("trained_on_this_dataset")),
                "tool_version": report["tool"]["version"],
                "created_at": report["run"]["created_at"],
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--suite", type=Path, default=ROOT / "benchmarks" / "suite.json")
    parser.add_argument("--raw", type=Path, default=ROOT / "results" / "raw")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args(argv)

    suite = json.loads(args.suite.read_text(encoding="utf-8"))
    titles = {entry["key"]: entry["title"].replace(" (built in)", "") for entry in suite["detectors"]}
    order = {entry["key"]: index for index, entry in enumerate(suite["detectors"])}
    everything: list[dict[str, Any]] = []
    sections: list[str] = []
    for entry in suite["datasets"]:
        directory = args.raw / entry["key"]
        reports = (
            [load_report(path) for path in sorted(directory.glob("*.json"))] if directory.is_dir() else []
        )
        reports = [report for report in reports if report.get("suite", {}).get("detector_key") in order]
        if not reports:
            continue
        everything.extend(reports)
        sections.extend(dataset_section(entry, reports, titles))
    if not everything:
        raise SystemExit(f"no reports found under {args.raw}; run benchmarks/run_suite.py first")

    versions = sorted({report["tool"]["version"] for report in everything})
    dates = sorted(report["run"]["created_at"][:10] for report in everything)
    detectors_used = sorted({report["suite"]["detector_key"] for report in everything}, key=order.__getitem__)
    detector_rows = []
    for entry in suite["detectors"]:
        if entry["key"] not in detectors_used:
            continue
        commit = entry["spec"].partition("@")[2]
        detector_rows.append(
            [
                f"`{titles[entry['key']]}`",
                f"`{commit[:12]}`" if commit else "this repository",
                entry.get("license", "Apache-2.0"),
                entry.get("languages", ""),
            ]
        )

    lines = [
        "# Results",
        "",
        "<!-- Generated by benchmarks/build_results.py from results/raw. Do not edit by hand. -->",
        "",
        suite["description"],
        "",
        f"- Run on {dates[0]}"
        + ("" if dates[0] == dates[-1] else f" to {dates[-1]}")
        + f" with BenignTwin {', '.join(versions)}.",
        f"- Every detector is used at a threshold of {suite['threshold']:g}: an input is flagged when the "
        "attack score is at or above it.",
        f"- The range in brackets is the {suite['confidence'] * 100:g}% Wilson confidence interval; "
        "the fraction is the count behind the rate.",
        "- *Attacks caught* is recall. *Benign flagged* is the false-positive rate. *Pairs separated* is "
        "pair accuracy: the share of matched pairs where the attack is flagged and its benign twin is not.",
        "- Rows are sorted by pairs separated where the data has pairs. Rows whose intervals overlap are "
        "not clearly different.",
        "",
        "## Detectors",
        "",
        *_table(["Detector", "Commit", "Licence", "Languages"], detector_rows, text=True),
        "",
        *[
            f"- `{titles[entry['key']]}`: {entry['note']}"
            for entry in suite["detectors"]
            if entry["key"] in detectors_used and entry.get("note")
        ],
        "",
        *sections,
        "## Limits",
        "",
        "- These are results on specific datasets at one threshold. They do not rank the detectors in "
        "general, and they say nothing about attacks that are not in the data.",
        "- The pair datasets are synthetic and manually reviewed. They test whether a detector can tell an "
        "attack from a legitimate request on the same subject; they do not represent the mix of traffic "
        "of any real application.",
        "- Several detectors are documented by their developers as English-only. A high false-positive "
        "rate on Turkish input from such a detector shows what happens when it is used outside its "
        "documented scope; it is not a defect report.",
        "- A threshold of 0.5 is each model's default decision. A deployment that tunes the threshold "
        "will see different trade-offs; the per-detector reports under `raw/` list other operating points.",
        "- Inputs longer than a model's window are truncated. The reports state how many were.",
        "",
        "## Reproduce",
        "",
        "```bash",
        'pip install "benigntwin[hf]" sentencepiece protobuf tiktoken',
        "python benchmarks/run_suite.py",
        "python benchmarks/build_results.py",
        "```",
        "",
        "The datasets and the model weights are pinned to commits in `benchmarks/suite.json`. "
        "The per-detector reports, with every slice and the run metadata, are under `results/raw/`.",
        "",
    ]
    write_text(args.output / "README.md", "\n".join(lines))

    rows = flat_rows(everything, titles)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    write_text(args.output / "results.csv", buffer.getvalue())
    write_text(args.output / "results.json", json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {args.output / 'README.md'} from {len(everything)} reports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
