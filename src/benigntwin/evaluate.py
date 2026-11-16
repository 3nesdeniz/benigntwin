"""Run a detector over a dataset and assemble the report."""

from __future__ import annotations

import os
import platform
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ._version import __version__
from .datasets import Dataset, DatasetInfo, ValidationResult, validate_examples
from .detectors.base import Detector
from .metrics import (
    binary_metrics,
    family_resolver,
    language_parity,
    latency_summary,
    pair_metrics,
    slice_metrics,
    threshold_sweep,
)
from .models import BenignTwinError, Example, ModelError, Prediction, Record

__all__ = ["DEFAULT_SLICES", "SCHEMA_VERSION", "Evaluation", "EvaluationError", "evaluate"]

#: Version of the JSON report layout. Bumped when a field changes meaning.
SCHEMA_VERSION = "2.0"
DEFAULT_SLICES: tuple[str, ...] = ("language", "attack_family")


class EvaluationError(BenignTwinError):
    """An evaluation cannot produce a result that should be trusted."""


@dataclass(frozen=True, slots=True)
class Evaluation:
    """The report plus the row-level records it was computed from."""

    report: dict[str, Any]
    records: tuple[Record, ...]
    errors: tuple[dict[str, str], ...]


def _created_at() -> str:
    """UTC timestamp. ``SOURCE_DATE_EPOCH`` pins it for byte-identical reports."""

    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    moment = (
        datetime.fromtimestamp(int(epoch), tz=timezone.utc)
        if epoch and epoch.isdigit()
        else datetime.now(timezone.utc)
    )
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evaluate(
    dataset: Dataset | Sequence[Example],
    detector: Detector,
    *,
    threshold: float = 0.5,
    decision: str = "auto",
    confidence: float = 0.95,
    slice_by: Sequence[str] = DEFAULT_SLICES,
    workers: int = 1,
    allow_errors: bool = False,
    validation: ValidationResult | None = None,
) -> Evaluation:
    """Evaluate ``detector`` on ``dataset``.

    Args:
        dataset: A loaded :class:`~benigntwin.datasets.Dataset` or a plain
            sequence of examples.
        detector: The system under test.
        threshold: Score at or above which an input counts as flagged.
        decision: ``"auto"`` uses the detector's own label when it returns one
            and the threshold otherwise; ``"score"`` always applies the
            threshold; ``"label"`` always uses the label.
        confidence: Level of the confidence intervals.
        slice_by: Dimensions to break the results down by.
        workers: Parallel calls for detectors that are called per example.
        allow_errors: Report on the rows that worked instead of failing when the
            detector errors on some rows. Coverage is always reported.
        validation: A validation result to reuse; computed when omitted.

    Raises:
        EvaluationError: If the dataset is structurally invalid, the settings
            are out of range, or predictions are missing and ``allow_errors``
            is off.
    """

    if isinstance(dataset, Dataset):
        examples: Sequence[Example] = dataset.examples
        info = dataset.info
    else:
        examples = list(dataset)
        info = DatasetInfo(source="(in memory)", kind="memory", split="all")
    if not examples:
        raise EvaluationError("cannot evaluate an empty dataset")
    if not 0.0 <= threshold <= 1.0:
        raise EvaluationError("threshold must be between 0 and 1")
    if not 0.0 < confidence < 1.0:
        raise EvaluationError("confidence must be between 0 and 1")
    if decision not in ("auto", "label", "score"):
        raise EvaluationError("decision must be auto, label or score")

    checked = validation or validate_examples(examples, generated_ids=info.generated_ids)
    if not checked.valid:
        raise EvaluationError("dataset failed validation: " + "; ".join(checked.errors))

    try:
        predictions = detector.predict_many(examples, workers=workers)
    finally:
        detector.close()

    records: list[Record] = []
    errors: list[dict[str, str]] = []
    from_label = 0
    for example in examples:
        prediction = predictions.get(example.id) or Prediction(
            id=example.id, error="detector returned no result"
        )
        if prediction.error:
            errors.append({"id": example.id, "error": prediction.error})
            continue
        try:
            predicted = prediction.decide(threshold, decision=decision)
        except ModelError as exc:
            errors.append({"id": example.id, "error": str(exc)})
            continue
        if decision != "score" and prediction.label is not None:
            from_label += 1
        records.append(Record(example=example, prediction=prediction, predicted=predicted))

    if errors and not allow_errors:
        preview = "; ".join(f"{item['id']}: {item['error']}" for item in errors[:3])
        more = "" if len(errors) <= 3 else f"; and {len(errors) - 3} more"
        raise EvaluationError(
            f"{len(errors)} of {len(examples)} predictions failed ({preview}{more}). "
            "Use --allow-errors only when partial coverage is intended."
        )
    if not records:
        raise EvaluationError("the detector produced no usable prediction")

    resolve_family = family_resolver(records)
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "benigntwin", "version": __version__},
        "run": {
            "created_at": _created_at(),
            "threshold": threshold,
            "decision": decision,
            "decisions_from_label": from_label,
            "decisions_from_score": len(records) - from_label,
            "confidence": confidence,
            "python": platform.python_version(),
            "platform": f"{platform.system()} {platform.machine()}".strip(),
        },
        "dataset": {
            **info.as_dict(),
            **dict(checked.stats),
            "warnings": list(checked.warnings),
        },
        "detector": detector.describe(),
        "coverage": {
            "evaluated": len(records),
            "failed": len(errors),
            "rate": len(records) / len(examples),
        },
        "metrics": binary_metrics(records, confidence),
        "pairs": pair_metrics(records, confidence),
        "slices": {
            dimension: slice_metrics(records, dimension, confidence, resolve_family=resolve_family)
            for dimension in dict.fromkeys(slice_by)
        },
        "language_parity": language_parity(records, confidence),
        "sweep": threshold_sweep(records, confidence),
        "latency_ms": latency_summary(records),
        "gates": [],
        "errors": errors,
    }
    return Evaluation(report=report, records=tuple(records), errors=tuple(errors))
