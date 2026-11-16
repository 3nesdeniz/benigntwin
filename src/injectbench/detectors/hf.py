"""Evaluate a text-classification model from the Hugging Face Hub.

``hf:owner/model`` or ``hf:owner/model@revision``. Needs ``transformers`` and
``torch``: ``pip install "injectbench[hf]"``.

Security defaults:

* ``trust_remote_code`` is always off: no code from a model repository runs.
* Only ``safetensors`` weights are loaded, because pickle-based weight files can
  execute code when they are opened. ``allow_pickle=True`` lifts this for
  models that ship no safetensors file.

The score of an input is the probability mass on the model's attack labels.
Inputs longer than the model's window are truncated by default; the report
states how many were. ``long_text="window"`` scores overlapping windows and
keeps the highest score instead.
"""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from typing import Any

from ..models import NEGATIVE_LABELS, POSITIVE_LABELS, Example, Prediction
from .base import Detector, DetectorError

__all__ = ["HuggingFaceDetector", "parse_model_spec", "resolve_positive_labels"]

_NEGATIVE_PREFIXES = ("no_", "non_", "not_")
_POSITIVE_HINTS = ("injection", "jailbreak")
_LONG_TEXT_MODES = ("truncate", "window")


def _canonical(name: str) -> str:
    return name.strip().casefold().replace("-", "_").replace(" ", "_")


def parse_model_spec(target: str) -> tuple[str, str | None]:
    """Split ``owner/model@revision`` into its two parts."""

    model_id, _, revision = target.partition("@")
    model_id = model_id.strip()
    if not model_id:
        raise DetectorError("a Hugging Face detector looks like hf:owner/model or hf:owner/model@revision")
    return model_id, (revision.strip() or None)


def resolve_positive_labels(
    id2label: Mapping[Any, Any],
    requested: Sequence[str] = (),
) -> tuple[list[int], bool]:
    """Find which output classes mean "attack".

    Returns the class indexes and whether they had to be assumed. Explicit
    ``requested`` names always win. Otherwise names such as ``INJECTION`` or
    ``jailbreak`` are recognized. A model that only exposes ``LABEL_0`` and
    ``LABEL_1`` is assumed to use ``LABEL_1`` for attacks, and the report says so.
    """

    names = {int(index): str(name) for index, name in id2label.items()}
    if not names:
        raise DetectorError("the model config has no id2label mapping")
    listing = ", ".join(names[index] for index in sorted(names))

    if requested:
        wanted = {_canonical(name) for name in requested}
        found = [index for index, name in names.items() if _canonical(name) in wanted]
        missing = wanted - {_canonical(names[index]) for index in found}
        if missing:
            raise DetectorError(f"label(s) {', '.join(sorted(missing))} not found; the model has: {listing}")
        if len(found) == len(names):
            raise DetectorError("every output label was marked as an attack label")
        return sorted(found), False

    def is_negative(name: str) -> bool:
        return name in NEGATIVE_LABELS or name.startswith(_NEGATIVE_PREFIXES)

    positive = [
        index
        for index, name in names.items()
        if not is_negative(_canonical(name))
        and (_canonical(name) in POSITIVE_LABELS or any(hint in _canonical(name) for hint in _POSITIVE_HINTS))
    ]
    if positive and len(positive) < len(names):
        return sorted(positive), False
    if {_canonical(name) for name in names.values()} == {"label_0", "label_1"}:
        return [index for index, name in names.items() if _canonical(name) == "label_1"], True
    raise DetectorError(
        f"cannot tell which output label means 'attack' (the model has: {listing}); "
        "name it with --positive-label"
    )


class HuggingFaceDetector(Detector):
    """Runs a sequence-classification model locally."""

    def __init__(
        self,
        model_id: str,
        *,
        revision: str | None = None,
        positive_labels: Sequence[str] = (),
        device: str = "cpu",
        batch_size: int = 16,
        max_length: int | None = None,
        long_text: str = "truncate",
        allow_pickle: bool = False,
    ) -> None:
        if long_text not in _LONG_TEXT_MODES:
            raise DetectorError(f"long_text must be one of: {', '.join(_LONG_TEXT_MODES)}")
        if batch_size < 1:
            raise DetectorError("batch_size must be at least 1")
        try:
            import torch
            import transformers
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
        except ImportError as exc:
            raise DetectorError(
                'Hugging Face detectors need transformers and torch: pip install "injectbench[hf]"'
            ) from exc

        self._torch = torch
        self.model_id = model_id
        self.revision = revision
        self.batch_size = batch_size
        self.long_text = long_text
        self.allow_pickle = allow_pickle
        self.name = f"hf:{model_id}"
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(
                model_id, revision=revision, trust_remote_code=False
            )
            self._model = AutoModelForSequenceClassification.from_pretrained(
                model_id,
                revision=revision,
                trust_remote_code=False,
                use_safetensors=None if allow_pickle else True,
            )
        except Exception as exc:
            hint = (
                "" if allow_pickle else " (if this model has no safetensors weights, see --hf-allow-pickle)"
            )
            raise DetectorError(f"could not load {model_id}: {type(exc).__name__}: {exc}{hint}") from exc

        self.device = self._pick_device(device)
        self._model.to(self.device)
        self._model.eval()

        config = self._model.config
        self.labels = {int(index): str(name) for index, name in config.id2label.items()}
        self._positive, self.positive_assumed = resolve_positive_labels(self.labels, positive_labels)
        limits = [
            value
            for value in (
                getattr(self._tokenizer, "model_max_length", None),
                getattr(config, "max_position_embeddings", None),
            )
            if isinstance(value, int) and 0 < value < 100_000
        ]
        self.max_length = max_length or (min(limits) if limits else 512)
        self.commit = getattr(config, "_commit_hash", None)
        self.truncated_inputs = 0
        self._versions = {"transformers": transformers.__version__, "torch": torch.__version__}

    def _pick_device(self, requested: str) -> str:
        torch = self._torch
        if requested != "auto":
            return requested
        if torch.cuda.is_available():
            return "cuda"
        mps = getattr(torch.backends, "mps", None)
        if mps is not None and mps.is_available():
            return "mps"
        return "cpu"

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": "huggingface",
            "model": self.model_id,
            "revision": self.revision,
            "commit": self.commit,
            "labels": [self.labels[index] for index in sorted(self.labels)],
            "attack_labels": [self.labels[index] for index in self._positive],
            "attack_labels_assumed": self.positive_assumed,
            "max_length": self.max_length,
            "long_text": self.long_text,
            "truncated_inputs": self.truncated_inputs,
            "device": self.device,
            "batch_size": self.batch_size,
            "weights": "any" if self.allow_pickle else "safetensors only",
            **self._versions,
        }

    def _score_batch(self, texts: Sequence[str]) -> list[float]:
        torch = self._torch
        windowed = self.long_text == "window"
        lengths = self._tokenizer(list(texts), truncation=False, add_special_tokens=True, verbose=False)[
            "input_ids"
        ]
        self.truncated_inputs += 0 if windowed else sum(1 for ids in lengths if len(ids) > self.max_length)
        encoded = self._tokenizer(
            list(texts),
            truncation=True,
            max_length=self.max_length,
            padding=True,
            return_tensors="pt",
            return_overflowing_tokens=windowed,
            stride=self.max_length // 4 if windowed else 0,
        )
        mapping = encoded.pop("overflow_to_sample_mapping", None)
        encoded = {key: value.to(self.device) for key, value in encoded.items()}
        with torch.inference_mode():
            logits = self._model(**encoded).logits
        probabilities = torch.softmax(logits, dim=-1)[:, self._positive].sum(dim=-1).tolist()
        if mapping is None:
            return [min(1.0, max(0.0, float(value))) for value in probabilities]
        best = [0.0] * len(texts)
        for window, sample in enumerate(mapping.tolist()):
            best[sample] = max(best[sample], float(probabilities[window]))
        return [min(1.0, max(0.0, value)) for value in best]

    def predict_many(
        self,
        examples: Sequence[Example],
        *,
        workers: int = 1,
    ) -> dict[str, Prediction]:
        del workers  # batching replaces threads here
        self.truncated_inputs = 0
        predictions: dict[str, Prediction] = {}
        for start in range(0, len(examples), self.batch_size):
            batch = examples[start : start + self.batch_size]
            started = time.perf_counter()
            try:
                scores = self._score_batch([example.text for example in batch])
            except Exception as exc:  # noqa: BLE001 - keep the run alive, report the rows
                for example in batch:
                    predictions[example.id] = Prediction(id=example.id, error=f"{type(exc).__name__}: {exc}")
                continue
            latency = (time.perf_counter() - started) * 1000.0 / len(batch)
            for example, score in zip(batch, scores, strict=True):
                predictions[example.id] = Prediction(id=example.id, score=score, latency_ms=latency)
        return predictions
