"""Pass/fail gates for continuous integration.

A gate compares one headline metric with a limit. With ``conservative=True``
the gate uses the unfavourable end of the confidence interval instead of the
point estimate, so a small test set cannot pass by luck: 0 false positives in
40 benign inputs has a point estimate of 0 % but an upper bound of about 9 %.

A gate on a metric that cannot be computed (for example a false-positive gate
on a dataset without benign rows) fails. It never passes silently.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

__all__ = [
    "EXIT_ERROR",
    "EXIT_FPR",
    "EXIT_OK",
    "EXIT_PAIR",
    "EXIT_RECALL",
    "EXIT_USAGE",
    "GateResult",
    "check_gates",
    "exit_code",
]

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_FPR = 2
EXIT_RECALL = 3
EXIT_PAIR = 4
EXIT_USAGE = 64


@dataclass(frozen=True, slots=True)
class GateResult:
    """Outcome of one gate."""

    name: str
    metric: str
    limit: float
    observed: float | None
    basis: str
    passed: bool
    exit_code: int

    @property
    def message(self) -> str:
        if self.observed is None:
            return f"{self.name}: cannot be measured on this dataset (limit {self.limit:.4f})"
        relation = "<=" if self.name.startswith("max") else ">="
        verdict = "ok" if self.passed else "FAILED"
        return (
            f"{self.name}: {self.observed:.4f} ({self.basis}) must be {relation} {self.limit:.4f}: {verdict}"
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "metric": self.metric,
            "limit": self.limit,
            "observed": self.observed,
            "basis": self.basis,
            "passed": self.passed,
        }


def _observed(value: Mapping[str, Any] | None, *, upper: bool, conservative: bool) -> float | None:
    if value is None:
        return None
    if not conservative:
        return float(value["value"])
    return float(value["ci_high"] if upper else value["ci_low"])


def check_gates(
    report: Mapping[str, Any],
    *,
    max_fpr: float | None = None,
    min_recall: float | None = None,
    min_pair_accuracy: float | None = None,
    conservative: bool = False,
) -> list[GateResult]:
    """Evaluate the requested gates against a report."""

    basis = "confidence bound" if conservative else "point estimate"
    results: list[GateResult] = []
    metrics = report["metrics"]
    if max_fpr is not None:
        observed = _observed(metrics["false_positive_rate"], upper=True, conservative=conservative)
        results.append(
            GateResult(
                name="max-fpr",
                metric="false_positive_rate",
                limit=max_fpr,
                observed=observed,
                basis=basis,
                passed=observed is not None and observed <= max_fpr,
                exit_code=EXIT_FPR,
            )
        )
    if min_recall is not None:
        observed = _observed(metrics["recall"], upper=False, conservative=conservative)
        results.append(
            GateResult(
                name="min-recall",
                metric="recall",
                limit=min_recall,
                observed=observed,
                basis=basis,
                passed=observed is not None and observed >= min_recall,
                exit_code=EXIT_RECALL,
            )
        )
    if min_pair_accuracy is not None:
        observed = _observed(report["pairs"]["pair_accuracy"], upper=False, conservative=conservative)
        results.append(
            GateResult(
                name="min-pair-accuracy",
                metric="pair_accuracy",
                limit=min_pair_accuracy,
                observed=observed,
                basis=basis,
                passed=observed is not None and observed >= min_pair_accuracy,
                exit_code=EXIT_PAIR,
            )
        )
    return results


def exit_code(results: list[GateResult]) -> int:
    """Exit status for a set of gate results: the first failure, else 0."""

    for result in results:
        if not result.passed:
            return result.exit_code
    return EXIT_OK
