# Changelog

All notable changes are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the versions follow [semantic versioning](https://semver.org/).

## [1.0.1] - 2026-11-16

### Changed

- The package is on PyPI: `pip install benigntwin`. The documentation uses that command.

### Fixed

- The release workflow reads the package version correctly and can publish an existing tag by hand.

## [1.0.0] - 2026-11-16

**The project is renamed from InjectBench to BenignTwin** (package, import name and command: `benigntwin`). This release also rebuilds the tool and merges in [llm-security-testbench](https://github.com/3nesdeniz/llm-security-testbench), which did the same job. See [docs/migration.md](docs/migration.md) if you used either.

### Added

- Detectors beyond the two built-in baselines: Hugging Face classification models (`hf:owner/model[@revision]`), Python functions, HTTP endpoints and predictions computed elsewhere.
- A Wilson confidence interval and the underlying counts on every rate.
- Four pair outcomes (`separated`, `blocked_both`, `allowed_both`, `inverted`) and pair accuracy per language and per attack family.
- Language parity: languages compared on the items that exist in both, with an exact McNemar test.
- Threshold sweep with ROC AUC and the best recall under false-positive budgets of 0.1 %, 1 % and 5 %.
- `benigntwin validate` for dataset structure, `benigntwin compare` for several reports, `benigntwin export-promptfoo`.
- `--min-pair-accuracy` and `--conservative` gates; `--slice-by`, `--where`, `--default-language`, `--default-label` and column options.
- Run metadata in every report: tool version, dataset commit and file hashes, detector configuration and model commit, threshold, coverage.
- Hub datasets load with the standard library and are pinned to the commit they resolved to.
- A pinned benchmark suite (`benchmarks/`) and published results (`results/`).

### Changed

- Detectors receive only the input text. Labels and metadata are no longer passed to Python functions or sent to HTTP endpoints.
- An unknown or missing label is an error. Version 0.1.0 treated it as benign.
- A row without a language tag is reported as `unknown`. Version 0.1.0 treated it as English.
- A rate with a zero denominator is `null` / `n/a`. Version 0.1.0 printed `0.000`.
- Pairs are matched within a language, and a benign row inherits the attack family of its twin in per-family results.
- Usage errors exit with status 64, so they cannot be mistaken for a failed gate (2, 3, 4).
- Python 3.10 or newer is required. The package uses a `src` layout and ships type information.
- The JSON report has a new layout (`schema_version` 2.0).

### Removed

- `Detector.predict_batch`, `load_jsonl`, `load_parquet`, `load_hf` and `pairs_from` (use `load_dataset`).
- The `huggingface_hub` and `pandas` dependencies of the `hub` extra.

### Fixed

- Pair analysis no longer calls the detector a second time for the rows of each pair.
- A gate on a metric that cannot be computed now fails instead of passing.
- The licence file contains the full Apache-2.0 text.

## [0.1.0] - 2026-08-12

First release: regex and heuristic baselines, recall and false-positive rate, paired boundary accuracy, per-family and per-language tables, Markdown, JSON and SARIF reports.

[1.0.1]: https://github.com/3nesdeniz/benigntwin/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/3nesdeniz/benigntwin/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/3nesdeniz/benigntwin/releases/tag/v0.1.0

Version 0.1.0 was released under the name InjectBench.
