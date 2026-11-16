# Detectors

A detector is the system under test. It is chosen with `--detector` and one of these forms:

| Form | What it evaluates |
| --- | --- |
| `hf:owner/model[@revision]` | a text-classification model from the Hugging Face Hub, run locally |
| `python:file.py:function` | a Python function you provide |
| `https://host/path` | a guardrail behind an HTTP endpoint |
| `predictions:file.jsonl` | predictions that were computed somewhere else |
| `heuristic`, `regex-baseline` | two built-in keyword baselines, as a floor to compare against |

**A detector only ever receives the text of an input** (and its id, if you ask for that). Labels, attack families and every other column stay inside the benchmark, so the system under test cannot use the ground truth, not even by accident.

## Hugging Face models

```bash
pip install "benigntwin[hf]"
benigntwin evaluate \
  --dataset hf:3nesdeniz/agentic-prompt-injection-boundary-pairs \
  --detector hf:protectai/deberta-v3-base-prompt-injection-v2@90c9989b1a34
```

The score of an input is the probability the model puts on its attack labels. The input is flagged when that score reaches `--threshold` (default `0.5`).

| Option | Default | Meaning |
| --- | --- | --- |
| `@revision` | the default branch | branch, tag or commit of the model; pin a commit for a result you publish |
| `--positive-label NAME` | recognized automatically | output label that means attack; repeat it for models with several attack classes |
| `--device` | `cpu` | `cpu`, `cuda`, `mps` or `auto` |
| `--batch-size` | `16` | inputs per forward pass |
| `--max-length` | the model's own limit | token window |
| `--long-text` | `truncate` | `truncate` cuts inputs at the window; `window` scores overlapping windows and keeps the highest score |
| `--hf-allow-pickle` | off | also load pickle-based weight files |

**Attack labels.** Names such as `INJECTION`, `jailbreak` or `unsafe` are recognized. A model that only exposes `LABEL_0` and `LABEL_1` is assumed to use `LABEL_1` for attacks, and the report says that this was assumed. If the labels cannot be told apart, the run stops and lists them so you can pass `--positive-label`.

**Long inputs.** Most of these models read 512 tokens. With `truncate`, anything after the window is invisible to the model, and the report states how many inputs were cut (`detector.truncated_inputs`). An attack placed at the end of a long document is then missed for a reason that has nothing to do with the model's quality, so check that number before you interpret a result on long inputs.

**Security defaults.**

- `trust_remote_code` is always off. A model that needs custom code from its repository cannot be loaded.
- Only `safetensors` weights are loaded. Pickle-based weight files can execute code when they are opened; `--hf-allow-pickle` lifts the restriction for models you trust.

The report records the model commit, its labels, the window, the device and the library versions.

## Python functions

```python
# my_guardrail.py
def detect(text: str) -> float:
    """Return the probability that `text` is an attack."""
    return my_model.attack_probability(text)
```

```bash
benigntwin evaluate --dataset pairs.jsonl --detector python:my_guardrail.py:detect --workers 8
```

The function is called once per input and may return:

- a `float`: an attack score between 0 and 1;
- `0`/`1`, a `bool`, or a label such as `"attack"` or `"benign"`;
- a dictionary with `label` and/or `score`.

If the first parameter is named `text` or `prompt`, the function receives the text. Otherwise it receives `{"id": ..., "text": ...}`. `module:function` works for an installed module.

An exception in the function is recorded as a failed row; it does not end the run. Loading a detector imports and runs that file, so only point this at code you trust.

## HTTP endpoints

```bash
export GUARD_TOKEN=...
benigntwin evaluate --dataset pairs.jsonl \
  --detector https://guard.example.com/v1/classify \
  --http-label-field result.label --http-score-field result.score \
  --http-token-env GUARD_TOKEN --workers 4
```

One `POST` per input. The request body is JSON and contains only the text:

```json
{"text": "input to classify"}
```

The response must be a JSON object with a label, a score or both. Nested values are addressed with dotted paths:

```json
{"result": {"label": "attack", "score": 0.93}}
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--http-text-field` | `text` | request field for the input |
| `--http-label-field` | `label` | path of the label in the response |
| `--http-score-field` | `score` | path of the attack score in the response |
| `--http-body KEY=VALUE` | none | extra request field, for example a model name; repeatable |
| `--http-header KEY=VALUE` | none | extra request header; repeatable |
| `--http-token-env VAR` | none | environment variable holding a bearer token |
| `--http-send-id` | off | add the example id to the request |
| `--http-timeout` | `15` | seconds per request |
| `--http-retries` | `1` | retries after a timeout, a connection error or HTTP 408, 425, 429 or 5xx |

Scores must be attack probabilities. If your API returns the probability of *safe*, wrap it in a Python function.

Keep secrets out of `--http-header`: command lines end up in shell history. Use `--http-token-env`. The report records the endpoint and the names of the extra headers and fields, never their values or the token.

The endpoint receives the full input text, and its logs may keep it. Do not send private production data to an endpoint that is not approved for it.

## Predictions computed elsewhere

When the system cannot be called from the machine that runs the benchmark, run it where it lives and bring the predictions back:

```json
{"id": "apibp_0595_a", "prediction": "attack", "score": 0.97}
{"id": "apibp_0595_b", "score": 0.04}
```

```bash
benigntwin evaluate --dataset pairs.jsonl --detector predictions:preds.jsonl
```

Each line needs the row `id` and a `prediction` (or `predicted_label` / `label`), a `score`, or both. If a line has both `prediction` and `label`, `prediction` is used, so a file that also carries the ground truth is never scored against itself. A row without a prediction is a failed row.

`--save-predictions FILE` writes this format, so any run can be re-scored later without calling the detector again.

## Writing a detector class

For anything that needs state or batching, subclass `Detector`:

```python
from benigntwin import Detector, evaluate, load_dataset, render

class MyGuardrail(Detector):
    name = "my-guardrail-1.4"

    def score(self, text: str) -> float:
        return my_model.attack_probability(text)

dataset = load_dataset("hf:3nesdeniz/agentic-prompt-injection-boundary-pairs")
result = evaluate(dataset, MyGuardrail(), threshold=0.5)
print(render(result.report, "markdown"))
```

| Method | Purpose |
| --- | --- |
| `predict(text)` | the detector's own decision: `1`/`0`, a `bool` or a label |
| `score(text)` | an attack score between 0 and 1 |
| `predict_many(examples, workers=1)` | override to batch requests; return a `Prediction` per example id |
| `describe()` | configuration to record in the report; never put secrets here |
| `close()` | release resources after the run |

Implement `score` if you want the threshold and the threshold sweep to apply, `predict` if the system makes its own decision, or both. `@register` makes a class available by its `name` on the command line.

## The built-in baselines

`regex-baseline` flags an input when a known attack phrase matches. `heuristic` adds up weighted keyword signals into a score. Both cover English and Turkish phrases.

They exist to give every report a floor. A detector that cannot beat a keyword list on pair accuracy is not reading intent. They are not guardrails; do not deploy them.

## Failures

A row for which the detector raises, times out or returns something unusable is a failed row. By default the run stops and names the first failures, because metrics over an arbitrary subset are misleading. `--allow-errors` reports on the rows that worked; the report then lists the failed ids and the coverage.
