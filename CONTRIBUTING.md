# Contributing to InjectBench

Thanks for your interest. InjectBench aims to stay small, correct, and dependency-light.

## Ways to contribute

- **New detectors.** Implement a `Detector` (see `injectbench/detectors/base.py`), register it, and add tests. Adapters for real guardrails (Llama Guard, promptfoo, garak probes) are especially welcome.
- **New metrics or report formats.** Keep `metrics.py` pure and fully unit-tested.
- **Dataset loaders.** Any source that normalizes to the `Example` schema.
- **Bug reports** with a minimal reproducing input.

## Development

```bash
pip install -e ".[dev,hub]"
pytest -q
```

## Guidelines

- Core (`metrics`, `evaluate`, `detectors.base`) must have **no runtime dependencies**.
- Every new public function ships with a test.
- Run `pytest` before opening a PR; CI runs on Python 3.9–3.12.
- Keep detectors honest: a detector that inflates recall by flagging everything must visibly lose on false-positive rate and paired boundary accuracy — that's the point of the benchmark.

## Good first issues

- Add a threshold-sweep report using `Detector.score()`.
- Add a `--per-family-table` option to the CLI.
- Contribute hard-negative examples in a new language.
