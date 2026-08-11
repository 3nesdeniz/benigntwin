"""InjectBench — a reproducible benchmark for prompt-injection detectors and LLM guardrails.

Public API:
    from injectbench import evaluate, load, get_detector, render
"""
from __future__ import annotations

__version__ = "0.1.0"

from .datasets import Example, load, load_jsonl, load_parquet, load_hf, pairs_from
from .detectors import Detector, get_detector, available_detectors, register
from .evaluate import evaluate, EvalResult
from .metrics import Confusion, confusion, paired_analysis, PairedResult
from .report import render, to_json, to_markdown, to_sarif

__all__ = [
    "__version__",
    "Example",
    "load",
    "load_jsonl",
    "load_parquet",
    "load_hf",
    "pairs_from",
    "Detector",
    "get_detector",
    "available_detectors",
    "register",
    "evaluate",
    "EvalResult",
    "Confusion",
    "confusion",
    "paired_analysis",
    "PairedResult",
    "render",
    "to_json",
    "to_markdown",
    "to_sarif",
]
