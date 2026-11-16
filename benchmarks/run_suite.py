"""Run the detectors of a suite file on its datasets and save one report per combination.

    python benchmarks/run_suite.py                      # everything in benchmarks/suite.json
    python benchmarks/run_suite.py --detector heuristic # one detector on every dataset
    python benchmarks/run_suite.py --dataset boundary-pairs-test --detector heuristic

Reports are written to ``results/raw/<dataset key>/<detector key>.json`` (and ``.md``).
Turn them into the published tables with ``python benchmarks/build_results.py``.

Every dataset and every model in the suite file is pinned to a commit, so a run
on another machine evaluates exactly the same inputs with exactly the same weights.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from benigntwin import (
    BenignTwinError,
    Dataset,
    DetectorOptions,
    FieldMap,
    build_detector,
    evaluate,
    load_dataset,
    render,
)
from benigntwin.report import format_rate, write_text

ROOT = Path(__file__).resolve().parents[1]


def load_suite(path: Path) -> dict[str, Any]:
    suite = json.loads(path.read_text(encoding="utf-8"))
    if suite.get("schema") != 1:
        raise SystemExit(f"{path}: unsupported suite schema {suite.get('schema')!r}")
    return suite


def select(entries: list[dict[str, Any]], keys: list[str], what: str) -> list[dict[str, Any]]:
    if not keys:
        return entries
    known = {entry["key"] for entry in entries}
    unknown = [key for key in keys if key not in known]
    if unknown:
        raise SystemExit(
            f"unknown {what} key(s): {', '.join(unknown)}; available: {', '.join(sorted(known))}"
        )
    return [entry for entry in entries if entry["key"] in keys]


def load_entry(entry: dict[str, Any]) -> Dataset:
    return load_dataset(
        entry["source"],
        split=entry.get("split"),
        revision=entry.get("revision"),
        hf_file=entry.get("hf_file"),
        field_map=FieldMap.from_options(default_language=entry.get("default_language")),
        where=entry.get("where"),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--suite", type=Path, default=ROOT / "benchmarks" / "suite.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "raw")
    parser.add_argument("--detector", action="append", default=[], help="detector key; repeatable")
    parser.add_argument("--dataset", action="append", default=[], help="dataset key; repeatable")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--list", choices=("detectors", "datasets"), help="print the keys as JSON and exit")
    args = parser.parse_args(argv)

    suite = load_suite(args.suite)
    if args.list:
        print(json.dumps([entry["key"] for entry in suite[args.list]]))
        return 0
    detectors = select(suite["detectors"], args.detector, "detector")
    dataset_entries = select(suite["datasets"], args.dataset, "dataset")

    loaded: dict[str, Dataset] = {}
    failures = 0
    for detector_entry in detectors:
        options = DetectorOptions(
            hf_positive_labels=tuple(detector_entry.get("positive_labels", ())),
            hf_device=args.device,
            hf_batch_size=args.batch_size,
        )
        try:
            detector = build_detector(detector_entry["spec"], options)
        except BenignTwinError as exc:
            print(f"FAILED {detector_entry['key']}: {exc}", file=sys.stderr)
            failures += 1
            continue
        for dataset_entry in dataset_entries:
            key = dataset_entry["key"]
            started = time.perf_counter()
            try:
                if key not in loaded:
                    loaded[key] = load_entry(dataset_entry)
                result = evaluate(
                    loaded[key],
                    detector,
                    threshold=suite["threshold"],
                    confidence=suite["confidence"],
                    slice_by=["language", *dataset_entry.get("slice_by", [])],
                )
            except BenignTwinError as exc:
                print(f"FAILED {key} x {detector_entry['key']}: {exc}", file=sys.stderr)
                failures += 1
                continue
            report = result.report
            report["suite"] = {
                "name": suite["name"],
                "dataset_key": key,
                "detector_key": detector_entry["key"],
                "trained_on_this_dataset": key in detector_entry.get("trained_on", []),
            }
            target = args.output / key / detector_entry["key"]
            write_text(target.with_suffix(".json"), render(report, "json"))
            write_text(target.with_suffix(".md"), render(report, "markdown"))
            metrics = report["metrics"]
            print(
                f"{key:22} {detector_entry['key']:30} "
                f"recall {format_rate(metrics['recall'], interval=False):>14}  "
                f"fpr {format_rate(metrics['false_positive_rate'], interval=False):>14}  "
                f"pairs {format_rate(report['pairs']['pair_accuracy'], interval=False):>14}  "
                f"({time.perf_counter() - started:.0f}s)",
                flush=True,
            )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
