# InjectBench

**A reproducible benchmark for prompt-injection detectors and LLM guardrails — with paired benign/attack evaluation and false-positive-aware scoring.**

[![CI](https://github.com/3nesdeniz/injectbench/actions/workflows/ci.yml/badge.svg)](https://github.com/3nesdeniz/injectbench/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![OWASP LLM01](https://img.shields.io/badge/OWASP-LLM01%20Prompt%20Injection-6f42c1.svg)](https://genai.owasp.org/)

Most "prompt-injection detector" numbers you see are recall on a pile of attacks. That is half a metric. A guardrail that flags every message has perfect recall and is useless. **The number that matters to anyone shipping an LLM is: does it stop attacks *without* tripping on the legitimate users who happen to talk about the same things?**

InjectBench measures both at once. It scores a detector on attacks **and** on *hard negatives* — benign inputs that reuse the same roles, tools, and vocabulary as attacks — and reports the **paired boundary accuracy**: how often the detector flags the attack while clearing its benign twin.

Built by [Enes Deniz](https://altaysec.com.tr/enes-deniz) ([OWASP AI Exchange & GenAI Security contributor](https://github.com/3nesdeniz)), Co-Founder at [AltaySec](https://altaysec.com.tr).

---

## Why this exists

| The usual way | InjectBench |
| --- | --- |
| Recall on an attack-only corpus | Recall **and** false-positive rate, together |
| One aggregate score | Per attack-family and per-language breakdowns |
| No notion of "close calls" | **Paired boundary analysis** on benign/attack twins |
| Ad-hoc scripts | A stable CLI + library + CI gate + SARIF output |
| English-only | English **and** Turkish out of the box |

It plugs directly into the open [AltaySec / Enes Deniz prompt-injection datasets](https://huggingface.co/3nesdeniz) — no schema wrangling.

## Install

```bash
pip install injectbench            # core, zero dependencies
pip install "injectbench[hub]"     # + load datasets straight from the Hugging Face Hub
```

From source:

```bash
git clone https://github.com/3nesdeniz/injectbench
cd injectbench && pip install -e ".[dev,hub]"
```

## Quickstart

Evaluate a built-in baseline on the bundled sample:

```bash
injectbench evaluate --dataset examples/sample_data.jsonl --detector heuristic
```

Evaluate directly against a dataset on the Hugging Face Hub:

```bash
injectbench evaluate --dataset hf:3nesdeniz/english-prompt-injection-3k --split test --detector heuristic --format markdown
```

Use it as a **CI gate** — fail the build if a guardrail regresses on false positives or recall:

```bash
injectbench evaluate --dataset hf:3nesdeniz/english-prompt-injection-3k \
  --detector heuristic --max-fpr 0.05 --min-recall 0.90
# exit code 2 if FPR > 0.05, exit code 3 if recall < 0.90
```

## Plug in your own guardrail

Implement one method. That's the whole contract.

```python
from injectbench import evaluate, load, render
from injectbench.detectors import register
from injectbench.detectors.base import Detector

@register
class MyGuardrail(Detector):
    name = "my-guardrail"

    def predict(self, text: str) -> int:
        # call your model / API / rules; return 1 for injection, 0 for benign
        return int(my_model.is_injection(text))

examples = load("hf:3nesdeniz/english-prompt-injection-3k", split="test")
result = evaluate(MyGuardrail(), examples, dataset_name="english-prompt-injection-3k")
print(render(result, "markdown"))
```

`score(self, text) -> float` is optional; implement it to enable threshold sweeps.

## What you get back

```
## Overall
| Recall (attacks caught) | 1.000 |
| Precision               | 0.833 |
| F1                      | 0.909 |
| False-positive rate     | 0.200 |

## Paired boundary analysis
Boundary accuracy (attack flagged AND benign twin cleared): 0.800 over 5 pairs.

## By attack family / By language
... per-slice recall, FPR, F1 ...
```

Reports render as **Markdown**, **JSON**, or **SARIF 2.1.0** (so results flow into GitHub code-scanning and other security dashboards).

## The metrics, precisely

- **Recall / TPR** — share of injection attempts flagged. High recall alone is cheap.
- **False-positive rate (FPR)** — share of benign inputs wrongly flagged. The number that decides whether users tolerate your guardrail.
- **Precision, F1, accuracy** — standard, for completeness.
- **Paired boundary accuracy** — over matched (benign, attack) twins, the fraction where the detector flags the attack **and** clears the benign. This isolates *intent* discrimination from *surface-pattern* matching — a detector that just greps for the word "ignore" scores high on recall and terribly here.

## Datasets it speaks natively

Any `.jsonl` / `.parquet` with a `text` field and a `label` (or `class`) field. Optional `attack_family`, `language`, and `pair_id` fields unlock the sliced and paired reports. This is exactly the schema of:

- [`3nesdeniz/english-prompt-injection-3k`](https://huggingface.co/datasets/3nesdeniz/english-prompt-injection-3k)
- [`3nesdeniz/agentic-prompt-injection-5k`](https://huggingface.co/datasets/3nesdeniz/agentic-prompt-injection-5k)
- [`3nesdeniz/turkish-prompt-injection-1k`](https://huggingface.co/datasets/3nesdeniz/turkish-prompt-injection-1k)
- [`3nesdeniz/guardrail-hard-negatives`](https://huggingface.co/datasets/3nesdeniz/guardrail-hard-negatives)

## Architecture

```
injectbench/
├── detectors/        # Detector ABC + regex baseline + heuristic + registry
├── datasets.py       # load jsonl / parquet / hf: into a common Example schema
├── metrics.py        # confusion matrix, paired boundary analysis (pure, tested)
├── evaluate.py       # the harness: overall + per-family + per-language + paired
├── report.py         # markdown / json / sarif renderers
└── cli.py            # `injectbench evaluate | list-detectors`
```

Core has **zero runtime dependencies**; parquet/Hub loaders are optional extras.

## Roadmap

- Threshold-sweep / ROC report from `score()`
- Adapters for popular guardrails (Llama Guard, promptfoo, garak probes)
- Cost/latency accounting per detector
- More languages and attack families as the upstream datasets grow

Contributions welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Citation

```bibtex
@software{deniz_injectbench_2026,
  author  = {Deniz, Enes},
  title   = {InjectBench: a reproducible benchmark for prompt-injection detectors and LLM guardrails},
  year    = {2026},
  url      = {https://github.com/3nesdeniz/injectbench},
  note    = {ORCID: 0009-0006-9491-3565}
}
```

## License

[Apache-2.0](LICENSE).
