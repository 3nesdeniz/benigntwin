"""Render an EvalResult as JSON, Markdown, or SARIF."""
from __future__ import annotations

import json
from typing import List

from .evaluate import EvalResult


def to_json(result: EvalResult, indent: int = 2) -> str:
    return json.dumps(result.as_dict(), indent=indent, ensure_ascii=False)


def to_markdown(result: EvalResult) -> str:
    o = result.overall
    lines: List[str] = []
    lines.append(f"# InjectBench report — `{result.detector}`")
    lines.append("")
    lines.append(f"- **Dataset:** `{result.dataset}`")
    lines.append(f"- **Examples:** {result.n}")
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Recall (attacks caught) | {o.recall:.3f} |")
    lines.append(f"| Precision | {o.precision:.3f} |")
    lines.append(f"| F1 | {o.f1:.3f} |")
    lines.append(f"| False-positive rate | {o.fpr:.3f} |")
    lines.append(f"| Accuracy | {o.accuracy:.3f} |")
    lines.append(f"| TP / FP / TN / FN | {o.tp} / {o.fp} / {o.tn} / {o.fn} |")
    lines.append("")

    if result.paired:
        p = result.paired
        lines.append("## Paired boundary analysis")
        lines.append("")
        lines.append(f"Boundary accuracy (attack flagged **and** benign twin cleared): **{p.boundary_accuracy:.3f}** over {p.pairs} pairs.")
        lines.append("")
        lines.append("| Outcome | Count |")
        lines.append("| --- | --- |")
        lines.append(f"| Both correct | {p.both_correct} |")
        lines.append(f"| Attack caught, benign false-positive | {p.attack_only} |")
        lines.append(f"| Benign cleared, attack missed | {p.benign_only} |")
        lines.append(f"| Both wrong | {p.both_wrong} |")
        lines.append("")

    if result.by_family:
        lines.append("## By attack family")
        lines.append("")
        lines.append("| Family | N | Recall | FPR | F1 |")
        lines.append("| --- | ---: | ---: | ---: | ---: |")
        for fam, c in sorted(result.by_family.items()):
            lines.append(f"| {fam} | {c.total} | {c.recall:.3f} | {c.fpr:.3f} | {c.f1:.3f} |")
        lines.append("")

    if result.by_language:
        lines.append("## By language")
        lines.append("")
        lines.append("| Language | N | Recall | FPR | F1 |")
        lines.append("| --- | ---: | ---: | ---: | ---: |")
        for lang, c in sorted(result.by_language.items()):
            lines.append(f"| {lang} | {c.total} | {c.recall:.3f} | {c.fpr:.3f} | {c.f1:.3f} |")
        lines.append("")

    return "\n".join(lines)


def to_sarif(result: EvalResult) -> str:
    """Minimal SARIF 2.1.0 wrapper so results can flow into code-scanning UIs."""
    o = result.overall
    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "InjectBench",
                        "informationUri": "https://github.com/3nesdeniz/injectbench",
                        "rules": [
                            {"id": "injection-recall", "name": "InjectionRecall"},
                            {"id": "benign-false-positive-rate", "name": "BenignFalsePositiveRate"},
                        ],
                    }
                },
                "properties": {
                    "detector": result.detector,
                    "dataset": result.dataset,
                    "recall": round(o.recall, 4),
                    "precision": round(o.precision, 4),
                    "f1": round(o.f1, 4),
                    "fpr": round(o.fpr, 4),
                },
                "results": [
                    {
                        "ruleId": "injection-recall",
                        "level": "note",
                        "message": {"text": f"Recall {o.recall:.3f} over {o.tp + o.fn} attacks."},
                    },
                    {
                        "ruleId": "benign-false-positive-rate",
                        "level": ("warning" if o.fpr > 0.1 else "note"),
                        "message": {"text": f"False-positive rate {o.fpr:.3f} over {o.fp + o.tn} benign inputs."},
                    },
                ],
            }
        ],
    }
    return json.dumps(sarif, indent=2, ensure_ascii=False)


def render(result: EvalResult, fmt: str) -> str:
    fmt = fmt.lower()
    if fmt == "json":
        return to_json(result)
    if fmt in ("md", "markdown"):
        return to_markdown(result)
    if fmt == "sarif":
        return to_sarif(result)
    raise ValueError(f"unknown report format: {fmt}")
