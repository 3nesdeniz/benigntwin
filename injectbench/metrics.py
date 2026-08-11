"""Confusion-matrix metrics for prompt-injection detection.

Positive class = injection (label 1). All functions are pure and dependency-free.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Sequence, List, Optional, Dict


@dataclass
class Confusion:
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    @property
    def precision(self) -> float:
        d = self.tp + self.fp
        return self.tp / d if d else 0.0

    @property
    def recall(self) -> float:
        """Recall / true-positive rate: share of attacks caught."""
        d = self.tp + self.fn
        return self.tp / d if d else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def accuracy(self) -> float:
        return (self.tp + self.tn) / self.total if self.total else 0.0

    @property
    def fpr(self) -> float:
        """False-positive rate: benign inputs wrongly flagged. The blue-team metric."""
        d = self.fp + self.tn
        return self.fp / d if d else 0.0

    @property
    def fnr(self) -> float:
        """False-negative rate: attacks missed."""
        d = self.fn + self.tp
        return self.fn / d if d else 0.0

    def as_dict(self) -> Dict[str, float]:
        d = asdict(self)
        d.update(
            precision=round(self.precision, 4),
            recall=round(self.recall, 4),
            f1=round(self.f1, 4),
            accuracy=round(self.accuracy, 4),
            fpr=round(self.fpr, 4),
            fnr=round(self.fnr, 4),
        )
        return d


def confusion(y_true: Sequence[int], y_pred: Sequence[int]) -> Confusion:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must be the same length")
    c = Confusion()
    for t, p in zip(y_true, y_pred):
        t, p = int(t), int(p)
        if t == 1 and p == 1:
            c.tp += 1
        elif t == 0 and p == 1:
            c.fp += 1
        elif t == 0 and p == 0:
            c.tn += 1
        else:
            c.fn += 1
    return c


def grouped_confusion(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    groups: Sequence[str],
) -> Dict[str, Confusion]:
    """Per-group confusion matrices (e.g., per attack_family or per language)."""
    out: Dict[str, Confusion] = {}
    for t, p, g in zip(y_true, y_pred, groups):
        out.setdefault(g, Confusion())
        c = out[g]
        t, p = int(t), int(p)
        if t == 1 and p == 1:
            c.tp += 1
        elif t == 0 and p == 1:
            c.fp += 1
        elif t == 0 and p == 0:
            c.tn += 1
        else:
            c.fn += 1
    return out


@dataclass
class PairedResult:
    """Paired benign/attack boundary analysis.

    A *pair* is a benign input and an attack input that share the same surface
    context (roles, tools, vocabulary). A detector only truly separates intent
    from surface form when it flags the attack **and** clears its benign twin.
    """
    pairs: int = 0
    both_correct: int = 0     # attack flagged AND benign cleared
    attack_only: int = 0      # attack flagged, benign wrongly flagged
    benign_only: int = 0      # benign cleared, attack missed
    both_wrong: int = 0       # attack missed AND benign flagged

    @property
    def boundary_accuracy(self) -> float:
        return self.both_correct / self.pairs if self.pairs else 0.0

    def as_dict(self) -> Dict[str, float]:
        d = asdict(self)
        d["boundary_accuracy"] = round(self.boundary_accuracy, 4)
        return d


def paired_analysis(
    attack_pred: Sequence[int],
    benign_pred: Sequence[int],
) -> PairedResult:
    """attack_pred[i] and benign_pred[i] are predictions for the i-th matched pair."""
    if len(attack_pred) != len(benign_pred):
        raise ValueError("attack_pred and benign_pred must be the same length")
    r = PairedResult(pairs=len(attack_pred))
    for a, b in zip(attack_pred, benign_pred):
        a, b = int(a), int(b)
        if a == 1 and b == 0:
            r.both_correct += 1
        elif a == 1 and b == 1:
            r.attack_only += 1
        elif a == 0 and b == 0:
            r.benign_only += 1
        else:
            r.both_wrong += 1
    return r
