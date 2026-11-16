# Migrating to 0.2

Version 0.2 renames the project from **InjectBench** to **BenignTwin**. The package, the import name and the command are now `benigntwin`. The old name was shared with a 2024 thesis and with a module shipped by an unrelated PyPI package, which made the tool hard to find and could lead to file conflicts.

## From InjectBench 0.1.0

| InjectBench 0.1.0 | BenignTwin 0.2 |
| --- | --- |
| `injectbench` (command and import) | `benigntwin` |
| `from injectbench import load` | `from benigntwin import load_dataset` |
| `load("hf:owner/name", split="test")` | `load_dataset("hf:owner/name", split="test")` |
| `evaluate(detector, examples, dataset_name=...)` | `evaluate(dataset, detector)` (the dataset comes first) |
| `result.overall.fpr` | `result.report["metrics"]["false_positive_rate"]["value"]` |
| `result.paired.boundary_accuracy` | `result.report["pairs"]["pair_accuracy"]["value"]` |
| `render(result, "markdown")` | `render(result.report, "markdown")` |
| `Detector.predict_batch(texts)` | override `predict_many(examples, workers=1)` |
| `pip install "injectbench[hub]"` | not needed: Hub datasets load without extra packages (`[parquet]` for `.parquet` files) |

Behaviour that changed:

- **Labels.** A row with an unknown or missing label is now an error. In 0.1.0 it was counted as benign, which could lower the reported false-positive rate without any sign. Fix the data, or pass `--default-label benign` for a corpus that is benign by construction.
- **Language.** A row without a language tag is `unknown`, no longer `en`. Pass `--default-language` if the dataset has one language.
- **Empty denominators.** A rate that cannot be computed is `null` / `n/a`, no longer `0.000`. A `--max-fpr` gate on data without benign rows now fails.
- **Scores and labels.** A detector that returns only a score is decided by `--threshold`. A detector that returns its own label keeps it unless you pass `--decision score`. The built-in `heuristic` detector now returns a score only.
- **Exit status.** 2 and 3 still mean the false-positive and recall gates failed. Usage errors moved from 2 to 64.
- **Python.** 3.10 or newer.

The options of 0.1.0 still work under the new command: `benigntwin evaluate --dataset ... --detector heuristic --max-fpr 0.05 --min-recall 0.9`.

## From llm-security-testbench

BenignTwin 0.2 contains what the testbench did. The command is `benigntwin` instead of `llmst`.

| llm-security-testbench | BenignTwin 0.2 |
| --- | --- |
| `llmst validate --dataset ...` | `benigntwin validate --dataset ...` |
| `--dataset hf://owner/name@rev` | unchanged (`hf:owner/name@rev` also works) |
| `--predictions file.jsonl` | `--detector predictions:file.jsonl` |
| `--python path.py:function` | `--detector python:path.py:function` |
| `--http https://host/path` | `--detector https://host/path` |
| `--max-workers 4` | `--workers 4` |
| `--allow-missing` | `--allow-errors` |
| `--output-dir reports/` | `--format json -o report.json --save-predictions predictions.jsonl` |
| `llmst export-promptfoo` | `benigntwin export-promptfoo` |

Two things behave differently on purpose:

- **Python functions and HTTP endpoints no longer receive the label, the category or the attack family** of a row. A function now gets the text (if its first parameter is called `text` or `prompt`) or `{"id", "text"}`. An endpoint gets `{"text": ...}`; add `--http-send-id` if it needs the id. Passing the ground truth to the system under test made it possible to score well by accident.
- **Duplicate texts** with the same label are a warning, not an error. The same text with both labels is still an error.

New compared with the testbench: language slices and language parity, confidence intervals, Hugging Face model detectors, the threshold sweep, CI gates and SARIF.
