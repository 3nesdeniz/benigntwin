"""The evaluation harness: run a detector over a dataset and compute the full
metric surface (overall, per attack-family, per language, paired-boundary)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from .detectors.base import Detector
from .datasets import Example, pairs_from
from .metrics import (
    Confusion,
    confusion,
    grouped_confusion,
    paired_analysis,
    PairedResult,
)


@dataclass
class EvalResult:
    detector: str
    dataset: str
    n: int
    overall: Confusion
    by_family: Dict[str, Confusion] = field(default_factory=dict)
    by_language: Dict[str, Confusion] = field(default_factory=dict)
    paired: Optional[PairedResult] = None

    def as_dict(self) -> dict:
        return {
            "detector": self.detector,
            "dataset": self.dataset,
            "n": self.n,
            "overall": self.overall.as_dict(),
            "by_family": {k: v.as_dict() for k, v in sorted(self.by_family.items())},
            "by_language": {k: v.as_dict() for k, v in sorted(self.by_language.items())},
            "paired": self.paired.as_dict() if self.paired else None,
        }


def evaluate(
    detector: Detector,
    examples: List[Example],
    dataset_name: str = "dataset",
) -> EvalResult:
    if not examples:
        raise ValueError("no examples to evaluate")
    preds = detector.predict_batch([e.text for e in examples])
    y_true = [e.label for e in examples]

    overall = confusion(y_true, preds)
    # group attack families only over attack examples for a meaningful recall;
    # benign examples all share the 'benign' family for FPR readouts.
    fam = grouped_confusion(y_true, preds, [e.attack_family for e in examples])
    lang = grouped_confusion(y_true, preds, [e.language for e in examples])

    paired = None
    prs = pairs_from(examples)
    if prs:
        attack_pred = [detector.predict(a.text) for (_b, a) in prs]
        benign_pred = [detector.predict(b.text) for (b, _a) in prs]
        paired = paired_analysis(attack_pred, benign_pred)

    return EvalResult(
        detector=detector.name,
        dataset=dataset_name,
        n=len(examples),
        overall=overall,
        by_family=fam,
        by_language=lang,
        paired=paired,
    )
