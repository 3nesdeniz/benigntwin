"""Core data models: labelled examples, detector predictions and label normalization.

The positive class (label ``1``) is an attack: a prompt injection or jailbreak
attempt. The negative class (label ``0``) is a legitimate, benign input.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "NEGATIVE_LABELS",
    "POSITIVE_LABELS",
    "BenignTwinError",
    "Example",
    "LabelError",
    "ModelError",
    "Prediction",
    "Record",
    "normalize_label",
    "normalize_language",
]


class BenignTwinError(Exception):
    """Base class for every error BenignTwin raises on purpose."""


class ModelError(BenignTwinError, ValueError):
    """A row or a prediction cannot be turned into a valid object."""


class LabelError(ModelError):
    """A label is not one of the supported binary values."""


POSITIVE_LABELS: frozenset[str] = frozenset(
    {
        "1",
        "attack",
        "blocked",
        "injection",
        "jailbreak",
        "malicious",
        "positive",
        "prompt_injection",
        "true",
        "unsafe",
        "yes",
    }
)
NEGATIVE_LABELS: frozenset[str] = frozenset(
    {
        "0",
        "allowed",
        "benign",
        "false",
        "legitimate",
        "negative",
        "no",
        "safe",
    }
)

#: Family values that mean "this benign row has no attack family of its own".
_NO_FAMILY = frozenset({"", "none", "benign", "unknown", "n/a", "na", "null"})


def _canonical(value: str) -> str:
    return value.strip().casefold().replace("-", "_").replace(" ", "_")


def normalize_label(
    value: Any,
    *,
    positive: frozenset[str] = POSITIVE_LABELS,
    negative: frozenset[str] = NEGATIVE_LABELS,
) -> int:
    """Turn a binary security label into ``0`` (benign) or ``1`` (attack).

    Anything that is not clearly one of the two classes raises
    :class:`LabelError`. A benchmark that silently treats an unknown label as
    benign reports a false-positive rate that is wrong, so this never guesses.
    """

    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        if value in (0, 1):
            return value
    elif isinstance(value, float):
        if value in (0.0, 1.0):
            return int(value)
    elif isinstance(value, str):
        canonical = _canonical(value)
        if canonical in positive:
            return 1
        if canonical in negative:
            return 0
    raise LabelError(f"unsupported binary label: {value!r}")


def normalize_language(value: Any) -> str:
    """Normalize a language tag to lower case with ``-`` separators.

    ``None`` and empty values become ``"unknown"``: BenignTwin never assumes
    that an untagged row is English.
    """

    if value is None:
        return "unknown"
    text = str(value).strip().lower().replace("_", "-")
    return text or "unknown"


def normalize_family(value: Any, *, label: int) -> str | None:
    """Normalize an attack family.

    Benign rows often carry a placeholder such as ``"none"`` or ``"benign"``;
    those become ``None``. An attack row without a family becomes ``"unknown"``.
    """

    text = "" if value is None else str(value).strip()
    if label == 0:
        return None if text.casefold() in _NO_FAMILY else text
    return text or "unknown"


@dataclass(frozen=True, slots=True)
class Example:
    """One labelled input.

    Attributes:
        id: Unique identifier within the loaded dataset.
        text: The input a detector has to classify.
        label: ``1`` for an attack, ``0`` for a benign input.
        language: Lower-case language tag, ``"unknown"`` when the data has none.
        attack_family: Family of an attack row. ``None`` for benign rows.
        pair_family: Family of the pair a row belongs to, when the dataset
            records it on both rows (used for per-family false-positive rates).
        pair_id: Identifier shared by an attack and its benign twin.
        split: Dataset split the row came from, if known.
        fields: Remaining scalar columns of the source row, available for slicing.
    """

    id: str
    text: str
    label: int
    language: str = "unknown"
    attack_family: str | None = None
    pair_family: str | None = None
    pair_id: str | None = None
    split: str | None = None
    fields: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.label not in (0, 1):
            raise ModelError(f"example {self.id!r}: label must be 0 or 1")
        if not self.text.strip():
            raise ModelError(f"example {self.id!r}: text is empty")

    @property
    def is_attack(self) -> bool:
        return self.label == 1

    @property
    def pair_key(self) -> tuple[str, str] | None:
        """Pairs are matched within one language: ``(pair_id, language)``."""

        if self.pair_id is None:
            return None
        return (self.pair_id, self.language)

    def get(self, name: str) -> Any:
        """Look up a slicing dimension by name."""

        if name in ("language", "attack_family", "pair_family", "split", "label", "pair_id"):
            return getattr(self, name)
        return self.fields.get(name)

    def detector_input(self) -> dict[str, str]:
        """What a detector is allowed to see: the identifier and the text.

        Labels, families and every other column stay with the benchmark, so a
        detector under test cannot use the ground truth, even by accident.
        """

        return {"id": self.id, "text": self.text}


@dataclass(frozen=True, slots=True)
class Prediction:
    """What a detector returned for one example.

    A prediction carries a hard ``label``, an attack ``score`` in ``[0, 1]``,
    or both. ``error`` is set when the detector failed on this example.
    """

    id: str
    label: int | None = None
    score: float | None = None
    latency_ms: float | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if self.label is not None and self.label not in (0, 1):
            raise ModelError("prediction label must be 0, 1 or null")
        if self.score is not None and not (
            isinstance(self.score, (int, float)) and not math.isnan(self.score) and 0.0 <= self.score <= 1.0
        ):
            raise ModelError("prediction score must be a number between 0 and 1")

    @classmethod
    def from_value(
        cls,
        example_id: str,
        value: Any,
        *,
        latency_ms: float | None = None,
    ) -> Prediction:
        """Normalize what a Python function, an HTTP endpoint or a file returned.

        Accepted shapes:

        * a mapping with ``prediction`` (or ``predicted_label`` / ``label``)
          and/or ``score``;
        * a ``float``: an attack score between 0 and 1;
        * a ``bool``, ``0``/``1`` or a label string such as ``"attack"``.

        ``prediction`` wins over ``label`` so that a file which carries both the
        ground truth (``label``) and the detector output (``prediction``) is
        never scored against itself.
        """

        label: int | None = None
        score: float | None = None

        if isinstance(value, Mapping):
            raw_label = next(
                (
                    value[key]
                    for key in ("prediction", "predicted_label", "label")
                    if value.get(key) is not None
                ),
                None,
            )
            if raw_label is not None:
                label = normalize_label(raw_label)
            if value.get("score") is not None:
                score = _as_score(value["score"])
        elif isinstance(value, float):
            score = _as_score(value)
        elif value is None:
            raise ModelError("detector returned nothing")
        else:
            label = normalize_label(value)

        if label is None and score is None:
            raise ModelError("prediction needs a label, a score or both")
        return cls(id=example_id, label=label, score=score, latency_ms=latency_ms)

    def decide(self, threshold: float, *, decision: str = "auto") -> int:
        """Resolve the prediction to ``0`` or ``1``.

        ``decision="auto"`` keeps the detector's own label when it gave one and
        otherwise applies ``threshold`` to the score. ``"score"`` always applies
        the threshold and ``"label"`` always uses the label.
        """

        if decision not in ("auto", "label", "score"):
            raise ModelError(f"unknown decision mode: {decision!r}")
        if decision in ("auto", "label") and self.label is not None:
            return self.label
        if decision == "label":
            raise ModelError(f"prediction {self.id!r} has no label")
        if self.score is None:
            raise ModelError(f"prediction {self.id!r} has no score")
        return int(self.score >= threshold)


def _as_score(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelError(f"score must be a number, got {value!r}")
    score = float(value)
    if math.isnan(score) or not 0.0 <= score <= 1.0:
        raise ModelError(f"score must be between 0 and 1, got {value!r}")
    return score


@dataclass(frozen=True, slots=True)
class Record:
    """A labelled example joined with the decision a detector made on it."""

    example: Example
    prediction: Prediction
    predicted: int

    @property
    def correct(self) -> bool:
        return self.example.label == self.predicted

    @property
    def flagged(self) -> bool:
        return self.predicted == 1
