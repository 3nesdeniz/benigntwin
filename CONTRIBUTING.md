# Contributing

Bug reports, corrections to the documentation and new adapters are welcome.

## Setup

```bash
git clone https://github.com/3nesdeniz/injectbench
cd injectbench
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Before you open a pull request

```bash
ruff check .          # lint
ruff format --check . # formatting
mypy                  # types (strict)
pytest                # tests
```

All four run in CI on Python 3.10 to 3.14.

## Ground rules

- **The core stays dependency-free.** Loading data, metrics and reports use the standard library only. Anything that needs a package belongs behind an optional extra.
- **Never guess.** An unknown label, a missing language or a rate with a zero denominator must not be turned into a plausible-looking value.
- **Detectors see the text and nothing else.** No change may pass labels or metadata to a system under test.
- **Reports contain no input text.**
- **Every behaviour has a test.** Metrics are tested against values worked out by hand.
- **Claims about other projects need a source.** `docs/related-work.md` links each one; check the link when you change a row.

## Good first contributions

- An adapter for a guardrail API, as a documented example under `examples/`.
- A matched-pair dataset in a language that has none, with a native speaker's review.
- A worked CI example for a platform other than GitHub Actions.

## Reporting a problem with a published result

Open an issue with the detector, the dataset revision and what you measured. Results are regenerated from `benchmarks/suite.json`; a correction means a new run, not an edit of the tables.

## Security

See [SECURITY.md](SECURITY.md). Please do not report vulnerabilities in public issues.
