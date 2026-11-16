"""Command-line interface: ``benigntwin evaluate | validate | compare | detectors | export-promptfoo``.

Exit status of ``evaluate``:

* ``0`` success, and every requested gate passed
* ``1`` an error (bad arguments, unreadable data, failed predictions)
* ``2`` the ``--max-fpr`` gate failed
* ``3`` the ``--min-recall`` gate failed
* ``4`` the ``--min-pair-accuracy`` gate failed
* ``64`` the command line could not be understood
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from typing import Any, NoReturn

from ._version import __version__
from .compare import compare_reports, load_report, render_comparison
from .datasets import SPLITS, Dataset, FieldMap, load_dataset, validate_examples
from .detectors import DetectorOptions, available_detectors, build_detector
from .evaluate import DEFAULT_SLICES, evaluate
from .export import export_promptfoo
from .gates import EXIT_ERROR, EXIT_OK, EXIT_USAGE, check_gates, exit_code
from .models import BenignTwinError
from .report import FORMATS, predictions_jsonl, render, write_text

__all__ = ["build_parser", "main"]

_DETECTOR_HELP = (
    "detector to evaluate: a registered name (see `benigntwin detectors`), "
    "hf:owner/model[@revision], python:file.py:function, https://host/path "
    "or predictions:file.jsonl"
)


def _add_dataset_arguments(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group("dataset")
    group.add_argument(
        "--dataset",
        required=True,
        help="a .jsonl/.json/.parquet file, a directory, or hf:owner/name[@revision]",
    )
    group.add_argument(
        "--split",
        choices=(*SPLITS, "all"),
        help="split to load (default: test for directories and Hub datasets, every row for a file)",
    )
    group.add_argument("--revision", help="branch, tag or commit of a Hub dataset")
    group.add_argument("--hf-file", help="exact file inside a Hub dataset, for non-standard layouts")
    group.add_argument("--refresh", action="store_true", help="download Hub files again")
    group.add_argument("--text-field", help="column holding the input text")
    group.add_argument("--label-field", help="column holding the label")
    group.add_argument("--id-field", help="column holding the row id, or 'auto' to generate ids")
    group.add_argument("--language-field", help="column holding the language tag")
    group.add_argument("--pair-field", help="column linking an attack to its benign twin")
    group.add_argument("--family-field", help="column holding the attack family")
    group.add_argument("--default-language", help="language tag for rows that have none")
    group.add_argument(
        "--where",
        action="append",
        default=[],
        metavar="COLUMN=VALUE",
        help="keep only rows whose column equals the value; repeatable",
    )
    group.add_argument(
        "--default-label",
        help="label for rows that have none, e.g. 'benign' for a corpus of ordinary traffic",
    )


def _load(args: argparse.Namespace) -> Dataset:
    field_map = FieldMap.from_options(
        text_field=args.text_field,
        label_field=args.label_field,
        id_field=args.id_field,
        language_field=args.language_field,
        pair_field=args.pair_field,
        family_field=args.family_field,
        default_language=args.default_language,
        default_label=args.default_label,
    )
    return load_dataset(
        args.dataset,
        split=args.split,
        revision=args.revision,
        hf_file=args.hf_file,
        field_map=field_map,
        refresh=args.refresh,
        where=_key_value(args.where, "filter"),
    )


def _key_value(values: Sequence[str], what: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        key, separator, rest = value.partition("=")
        if not separator or not key.strip():
            raise BenignTwinError(f"invalid {what} {value!r}; expected KEY=VALUE")
        result[key.strip()] = rest
    return result


def _fraction(text: str) -> float:
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from None
    if not 0.0 <= value <= 1.0:
        raise argparse.ArgumentTypeError("must be between 0 and 1 (0.05 means 5%)")
    return value


class _Parser(argparse.ArgumentParser):
    """Usage errors exit with 64 so they cannot be mistaken for a failed gate."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(EXIT_USAGE, f"{self.prog}: error: {message}\n")


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""

    parser = _Parser(
        prog="benigntwin",
        description=(
            "Benchmark prompt-injection detectors and LLM guardrails on matched benign/attack "
            "pairs: attack recall, false-positive rate and pair accuracy, per attack family and "
            "per language, with confidence intervals."
        ),
        epilog="Documentation: https://github.com/3nesdeniz/benigntwin",
    )
    parser.add_argument("--version", action="version", version=f"benigntwin {__version__}")
    commands = parser.add_subparsers(dest="command", required=True, metavar="command")

    evaluate_parser = commands.add_parser(
        "evaluate",
        help="run a detector on a dataset and report the results",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _add_dataset_arguments(evaluate_parser)
    detector = evaluate_parser.add_argument_group("detector")
    detector.add_argument("--detector", required=True, help=_DETECTOR_HELP)
    detector.add_argument(
        "--threshold", type=_fraction, default=0.5, help="flag when score >= threshold (default: 0.5)"
    )
    detector.add_argument(
        "--decision",
        choices=("auto", "label", "score"),
        default="auto",
        help="auto: the detector's own label if it gives one, else the threshold (default)",
    )
    detector.add_argument("--workers", type=int, default=1, help="parallel calls (python and HTTP detectors)")
    detector.add_argument(
        "--allow-errors",
        action="store_true",
        help="report on the rows that worked when the detector fails on some rows",
    )
    hf = evaluate_parser.add_argument_group("Hugging Face models (hf:...)")
    hf.add_argument(
        "--positive-label",
        action="append",
        default=[],
        metavar="NAME",
        help="output label that means attack; repeatable (default: recognized automatically)",
    )
    hf.add_argument("--device", default="cpu", help="cpu, cuda, mps or auto (default: cpu)")
    hf.add_argument("--batch-size", type=int, default=16)
    hf.add_argument("--max-length", type=int, help="token window (default: the model's own limit)")
    hf.add_argument(
        "--long-text",
        choices=("truncate", "window"),
        default="truncate",
        help="inputs longer than the window: cut them, or score overlapping windows and keep the maximum",
    )
    hf.add_argument(
        "--hf-allow-pickle",
        action="store_true",
        help="also load pickle-based weights (can execute code; only for models you trust)",
    )
    http = evaluate_parser.add_argument_group("HTTP endpoints (https://...)")
    http.add_argument("--http-text-field", default="text", help="request field for the input text")
    http.add_argument("--http-label-field", default="label", help="dotted path of the label in the response")
    http.add_argument("--http-score-field", default="score", help="dotted path of the score in the response")
    http.add_argument("--http-timeout", type=float, default=15.0, help="seconds per request")
    http.add_argument("--http-retries", type=int, default=1)
    http.add_argument("--http-token-env", metavar="VAR", help="environment variable holding a bearer token")
    http.add_argument(
        "--http-header",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="extra request header; repeatable",
    )
    http.add_argument(
        "--http-body",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="extra request body field; repeatable",
    )
    http.add_argument("--http-send-id", action="store_true", help="include the example id in the request")
    output = evaluate_parser.add_argument_group("report")
    output.add_argument("--format", default="markdown", choices=(*FORMATS, "md"))
    output.add_argument("-o", "--output", help="write the report to this file instead of standard output")
    output.add_argument("--save-predictions", metavar="FILE", help="also write row-level decisions as JSONL")
    output.add_argument(
        "--slice-by",
        default=",".join(DEFAULT_SLICES),
        help="comma-separated columns to break results down by; join two with + for a "
        "cross-tabulation (default: %(default)s)",
    )
    output.add_argument("--confidence", type=float, default=0.95, help="confidence level (default: 0.95)")
    gates = evaluate_parser.add_argument_group("gates (non-zero exit status when one fails)")
    gates.add_argument(
        "--max-fpr", type=_fraction, metavar="RATE", help="highest acceptable false-positive rate"
    )
    gates.add_argument("--min-recall", type=_fraction, metavar="RATE", help="lowest acceptable attack recall")
    gates.add_argument(
        "--min-pair-accuracy", type=_fraction, metavar="RATE", help="lowest acceptable pair accuracy"
    )
    gates.add_argument(
        "--conservative",
        action="store_true",
        help="gate on the unfavourable end of the confidence interval instead of the point estimate",
    )

    validate_parser = commands.add_parser("validate", help="check the structure of a dataset")
    _add_dataset_arguments(validate_parser)
    validate_parser.add_argument("--json", action="store_true", help="print the result as JSON")

    compare_parser = commands.add_parser("compare", help="put several JSON reports side by side")
    compare_parser.add_argument("reports", nargs="+", metavar="REPORT.json")
    compare_parser.add_argument("--format", default="markdown", choices=("markdown", "md", "json"))
    compare_parser.add_argument(
        "--sort-by",
        default="pair_accuracy",
        choices=("pair_accuracy", "false_positive_rate", "recall", "detector"),
    )
    compare_parser.add_argument("-o", "--output", help="write the comparison to this file")

    commands.add_parser("detectors", help="list the registered detectors and the other forms")

    export_parser = commands.add_parser(
        "export-promptfoo", help="export a dataset as a Promptfoo test suite for a detector endpoint"
    )
    _add_dataset_arguments(export_parser)
    export_parser.add_argument("--output-dir", required=True)
    return parser


def _detector_options(args: argparse.Namespace) -> DetectorOptions:
    return DetectorOptions(
        http_text_field=args.http_text_field,
        http_label_field=args.http_label_field,
        http_score_field=args.http_score_field,
        http_timeout=args.http_timeout,
        http_retries=args.http_retries,
        http_token_env=args.http_token_env,
        http_headers=_key_value(args.http_header, "HTTP header"),
        http_body=_key_value(args.http_body, "HTTP body field"),
        http_send_id=args.http_send_id,
        hf_positive_labels=tuple(args.positive_label),
        hf_device=args.device,
        hf_batch_size=args.batch_size,
        hf_max_length=args.max_length,
        hf_long_text=args.long_text,
        hf_allow_pickle=args.hf_allow_pickle,
    )


def _emit(text: str, output: str | None, what: str) -> None:
    if output:
        path = write_text(output, text)
        print(f"wrote {what} to {path}", file=sys.stderr)
    else:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")


def _run_evaluate(args: argparse.Namespace) -> int:
    dataset = _load(args)
    validation = validate_examples(dataset.examples, generated_ids=dataset.info.generated_ids)
    for warning in validation.warnings:
        print(f"note: {warning}", file=sys.stderr)
    detector = build_detector(args.detector, _detector_options(args))
    slices = [part.strip() for part in args.slice_by.split(",") if part.strip()]
    result = evaluate(
        dataset,
        detector,
        threshold=args.threshold,
        decision=args.decision,
        confidence=args.confidence,
        slice_by=slices,
        workers=args.workers,
        allow_errors=args.allow_errors,
        validation=validation,
    )
    gate_results = check_gates(
        result.report,
        max_fpr=args.max_fpr,
        min_recall=args.min_recall,
        min_pair_accuracy=args.min_pair_accuracy,
        conservative=args.conservative,
    )
    result.report["gates"] = [gate.as_dict() for gate in gate_results]
    _emit(render(result.report, args.format), args.output, f"{args.format} report")
    if args.save_predictions:
        path = write_text(args.save_predictions, predictions_jsonl(result.records))
        print(f"wrote predictions to {path}", file=sys.stderr)
    for gate in gate_results:
        print(f"gate {gate.message}", file=sys.stderr)
    return exit_code(gate_results)


def _run_validate(args: argparse.Namespace) -> int:
    dataset = _load(args)
    result = validate_examples(dataset.examples, generated_ids=dataset.info.generated_ids)
    if args.json:
        payload: dict[str, Any] = {
            "valid": result.valid,
            "errors": list(result.errors),
            "warnings": list(result.warnings),
            "stats": dict(result.stats),
            "source": dataset.info.as_dict(),
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return EXIT_OK if result.valid else EXIT_ERROR
    stats = result.stats
    print(f"Source:    {dataset.info.source} (split: {dataset.info.split})")
    if dataset.info.resolved_revision:
        print(f"Revision:  {dataset.info.resolved_revision}")
    print(f"Examples:  {stats['examples']} ({stats['attacks']} attacks, {stats['benign']} benign)")
    languages = ", ".join(
        f"{name}: {counts['attacks']} attacks / {counts['benign']} benign"
        for name, counts in stats["languages"].items()
    )
    print(f"Languages: {languages}")
    pairs = stats["pairs"]
    print(
        f"Pairs:     {pairs['complete']} complete, {pairs['incomplete']} incomplete, "
        f"{pairs['in_several_languages']} present in several languages"
    )
    if stats["text_chars"]:
        chars = stats["text_chars"]
        print(f"Text:      {chars['min']}-{chars['max']} characters, median {chars['median']}")
    for warning in result.warnings:
        print(f"Warning:   {warning}")
    for error in result.errors:
        print(f"Error:     {error}", file=sys.stderr)
    print("Result:    valid" if result.valid else "Result:    INVALID")
    return EXIT_OK if result.valid else EXIT_ERROR


def _run_compare(args: argparse.Namespace) -> int:
    comparison = compare_reports([load_report(path) for path in args.reports], sort_by=args.sort_by)
    if not comparison["same_dataset"]:
        print("warning: the reports were not computed on the same data", file=sys.stderr)
    _emit(render_comparison(comparison, args.format), args.output, "comparison")
    return EXIT_OK


def _run_detectors(_args: argparse.Namespace) -> int:
    print("Registered detectors:")
    for name in available_detectors():
        print(f"  {name}")
    print()
    print("Other forms:")
    print("  hf:owner/model[@revision]   a Hugging Face text-classification model")
    print("  python:file.py:function     your own Python function")
    print("  https://host/path           a guardrail behind an HTTP endpoint")
    print("  predictions:file.jsonl      predictions computed elsewhere")
    return EXIT_OK


def _run_export(args: argparse.Namespace) -> int:
    dataset = _load(args)
    validation = validate_examples(dataset.examples, generated_ids=dataset.info.generated_ids)
    if not validation.valid:
        raise BenignTwinError("dataset failed validation: " + "; ".join(validation.errors))
    paths = export_promptfoo(
        dataset.examples, args.output_dir, dataset_source=dataset.info.source, split=dataset.info.split
    )
    print(f"exported {len(dataset)} tests; see {paths['instructions']}")
    return EXIT_OK


_COMMANDS = {
    "evaluate": _run_evaluate,
    "validate": _run_validate,
    "compare": _run_compare,
    "detectors": _run_detectors,
    "export-promptfoo": _run_export,
}


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns the process exit status."""

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _COMMANDS[args.command](args)
    except BenignTwinError as exc:
        if os.environ.get("BENIGNTWIN_DEBUG"):
            raise
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
