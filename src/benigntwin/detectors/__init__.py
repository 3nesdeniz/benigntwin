"""Detectors: the systems under test.

A detector is chosen with a short specification string:

==============================  =================================================
Specification                   Meaning
==============================  =================================================
``heuristic``                   built-in keyword-scoring reference baseline
``regex-baseline``              built-in phrase-matching reference baseline
``hf:owner/model[@revision]``   a text-classification model from the Hugging Face Hub
``python:file.py:function``     a Python function you provide
``https://host/path``           a guardrail behind an HTTP endpoint
``predictions:file.jsonl``      predictions computed elsewhere
==============================  =================================================
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from .base import Detector, DetectorError, run_per_example
from .baselines import HeuristicDetector, RegexDetector

__all__ = [
    "Detector",
    "DetectorError",
    "DetectorOptions",
    "HeuristicDetector",
    "RegexDetector",
    "available_detectors",
    "build_detector",
    "get_detector",
    "register",
    "run_per_example",
]

_REGISTRY: dict[str, Callable[[], Detector]] = {
    HeuristicDetector.name: HeuristicDetector,
    RegexDetector.name: RegexDetector,
}


def register(cls: type[Detector]) -> type[Detector]:
    """Class decorator: make a detector available by its ``name``."""

    if not getattr(cls, "name", None) or cls.name == Detector.name:
        raise DetectorError(f"{cls.__name__} needs its own name before it can be registered")
    _REGISTRY[cls.name] = cls
    return cls


def available_detectors() -> list[str]:
    """Names of the registered detectors."""

    return sorted(_REGISTRY)


def get_detector(name: str) -> Detector:
    """Create a registered detector by name."""

    try:
        return _REGISTRY[name]()
    except KeyError:
        raise DetectorError(
            f"unknown detector {name!r}; registered: {', '.join(available_detectors())}. "
            "Other forms: hf:owner/model, python:file.py:function, https://host/path, "
            "predictions:file.jsonl"
        ) from None


@dataclass(frozen=True, slots=True)
class DetectorOptions:
    """Settings for the detector kinds that need them."""

    http_text_field: str = "text"
    http_label_field: str = "label"
    http_score_field: str = "score"
    http_timeout: float = 15.0
    http_retries: int = 1
    http_token_env: str | None = None
    http_headers: Mapping[str, str] = field(default_factory=dict)
    http_body: Mapping[str, Any] = field(default_factory=dict)
    http_send_id: bool = False
    hf_positive_labels: tuple[str, ...] = ()
    hf_device: str = "cpu"
    hf_batch_size: int = 16
    hf_max_length: int | None = None
    hf_long_text: str = "truncate"
    hf_allow_pickle: bool = False


def build_detector(spec: str, options: DetectorOptions | None = None) -> Detector:
    """Create a detector from a specification string (see the module docstring)."""

    settings = options or DetectorOptions()
    spec = spec.strip()
    if not spec:
        raise DetectorError("empty detector specification")
    if spec.startswith(("http://", "https://")):
        from .http import HttpDetector

        return HttpDetector(
            spec,
            text_field=settings.http_text_field,
            label_field=settings.http_label_field,
            score_field=settings.http_score_field,
            timeout=settings.http_timeout,
            retries=settings.http_retries,
            token_env=settings.http_token_env,
            headers=settings.http_headers,
            body=settings.http_body,
            send_id=settings.http_send_id,
        )
    kind, separator, target = spec.partition(":")
    if separator and kind == "python":
        from .python_fn import PythonDetector

        return PythonDetector(target)
    if separator and kind == "predictions":
        from .offline import OfflineDetector

        return OfflineDetector(target)
    if separator and kind == "hf":
        from .hf import HuggingFaceDetector, parse_model_spec

        model_id, revision = parse_model_spec(target)
        return HuggingFaceDetector(
            model_id,
            revision=revision,
            positive_labels=settings.hf_positive_labels,
            device=settings.hf_device,
            batch_size=settings.hf_batch_size,
            max_length=settings.hf_max_length,
            long_text=settings.hf_long_text,
            allow_pickle=settings.hf_allow_pickle,
        )
    return get_detector(spec)
