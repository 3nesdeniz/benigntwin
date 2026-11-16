"""InjectBench: benchmark prompt-injection detectors and LLM guardrails.

Every attack is evaluated next to a benign twin that shares its topic and
vocabulary, so a detector gets credit only when it catches the attack *and*
lets the legitimate request through. Results come with the false-positive
rate, per attack family and per language breakdowns, and confidence intervals.

Quick start::

    from injectbench import build_detector, evaluate, load_dataset, render

    dataset = load_dataset("hf:3nesdeniz/agentic-prompt-injection-boundary-pairs")
    result = evaluate(dataset, build_detector("heuristic"))
    print(render(result.report, "markdown"))
"""

from __future__ import annotations

from ._version import __version__
from .compare import compare_reports, load_report, render_comparison
from .datasets import Dataset, DatasetError, FieldMap, load_dataset, validate_examples
from .detectors import (
    Detector,
    DetectorError,
    DetectorOptions,
    available_detectors,
    build_detector,
    get_detector,
    register,
)
from .evaluate import Evaluation, EvaluationError, evaluate
from .gates import check_gates
from .models import Example, InjectBenchError, Prediction, Record
from .report import render, to_json, to_markdown, to_sarif

__all__ = [
    "Dataset",
    "DatasetError",
    "Detector",
    "DetectorError",
    "DetectorOptions",
    "Evaluation",
    "EvaluationError",
    "Example",
    "FieldMap",
    "InjectBenchError",
    "Prediction",
    "Record",
    "__version__",
    "available_detectors",
    "build_detector",
    "check_gates",
    "compare_reports",
    "evaluate",
    "get_detector",
    "load_dataset",
    "load_report",
    "register",
    "render",
    "render_comparison",
    "to_json",
    "to_markdown",
    "to_sarif",
    "validate_examples",
]
