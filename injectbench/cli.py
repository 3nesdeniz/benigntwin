"""Command-line interface: ``injectbench evaluate|list-detectors``."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .detectors import get_detector, available_detectors
from .datasets import load
from .evaluate import evaluate
from .report import render


def _cmd_list(_args) -> int:
    print("Available detectors:")
    for name in available_detectors():
        print(f"  - {name}")
    return 0


def _cmd_evaluate(args) -> int:
    detector = get_detector(args.detector)
    examples = load(args.dataset, split=args.split)
    result = evaluate(detector, examples, dataset_name=args.dataset)
    text = render(result, args.format)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {args.format} report to {args.output}", file=sys.stderr)
    else:
        print(text)
    # non-zero exit if false-positive rate blows past the gate (useful in CI)
    if args.max_fpr is not None and result.overall.fpr > args.max_fpr:
        print(f"FPR {result.overall.fpr:.3f} exceeds --max-fpr {args.max_fpr}", file=sys.stderr)
        return 2
    if args.min_recall is not None and result.overall.recall < args.min_recall:
        print(f"recall {result.overall.recall:.3f} below --min-recall {args.min_recall}", file=sys.stderr)
        return 3
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="injectbench", description="Reproducible benchmark for prompt-injection detectors and LLM guardrails.")
    p.add_argument("--version", action="version", version=f"injectbench {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    lp = sub.add_parser("list-detectors", help="list built-in detectors")
    lp.set_defaults(func=_cmd_list)

    ep = sub.add_parser("evaluate", help="evaluate a detector on a dataset")
    ep.add_argument("--dataset", required=True, help="path to .jsonl/.parquet, or hf:owner/name")
    ep.add_argument("--detector", default="heuristic", help=f"one of: {', '.join(available_detectors())}")
    ep.add_argument("--split", default="test", help="split to load for hf: sources (default: test)")
    ep.add_argument("--format", default="markdown", choices=["markdown", "md", "json", "sarif"])
    ep.add_argument("--output", "-o", help="write report to file instead of stdout")
    ep.add_argument("--max-fpr", type=float, default=None, help="fail (exit 2) if false-positive rate exceeds this")
    ep.add_argument("--min-recall", type=float, default=None, help="fail (exit 3) if recall falls below this")
    ep.set_defaults(func=_cmd_evaluate)
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
