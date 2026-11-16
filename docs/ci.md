# Use it as a gate in CI

`benigntwin evaluate` can fail a build when a guardrail gets worse. This is how you notice that a new model version, a changed threshold or a prompt update started to block legitimate requests.

## Gates

| Option | Fails when |
| --- | --- |
| `--max-fpr RATE` | the false-positive rate is above `RATE` |
| `--min-recall RATE` | recall is below `RATE` |
| `--min-pair-accuracy RATE` | pair accuracy is below `RATE` |
| `--conservative` | makes each gate use the unfavourable end of the confidence interval |

Rates are fractions: `0.05` means 5 %.

```bash
benigntwin evaluate \
  --dataset tests/guardrail_pairs.jsonl \
  --detector python:app/guardrail.py:detect \
  --max-fpr 0.02 --min-pair-accuracy 0.85
```

A gate on a metric that cannot be computed fails. A `--max-fpr` gate on a dataset without benign rows does not pass silently.

### Why `--conservative`

A small test set can pass by luck. 0 false positives in 40 benign inputs is a point estimate of 0 %, but the 95 % interval reaches 8.8 %. With `--conservative`, `--max-fpr 0.05` compares the upper bound (8.8 %) with the limit and fails, which tells you the test set is too small to support the claim. Either add benign inputs or accept a looser limit.

## Exit status

| Status | Meaning |
| ---: | --- |
| `0` | success; every requested gate passed |
| `1` | an error: unreadable data, invalid dataset, failed predictions |
| `2` | the `--max-fpr` gate failed |
| `3` | the `--min-recall` gate failed |
| `4` | the `--min-pair-accuracy` gate failed |
| `64` | the command line could not be understood |

When several gates fail, the status is that of the first one in the order above. Each gate prints one line to standard error:

```text
gate max-fpr: 0.0333 (point estimate) must be <= 0.0200: FAILED
```

## GitHub Actions

```yaml
name: Guardrail regression
on: [pull_request]

permissions:
  contents: read
  security-events: write   # only needed for the SARIF upload

jobs:
  benigntwin:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"
      - run: pip install "benigntwin @ git+https://github.com/3nesdeniz/benigntwin@v1.0.0"
      - name: Evaluate the guardrail
        run: |
          benigntwin evaluate \
            --dataset tests/guardrail_pairs.jsonl \
            --detector python:app/guardrail.py:detect \
            --max-fpr 0.02 --min-pair-accuracy 0.85 \
            --format sarif --output benigntwin.sarif \
            --save-predictions benigntwin-predictions.jsonl
      - name: Show the result in code scanning
        if: always()
        uses: github/codeql-action/upload-sarif@v4
        with:
          sarif_file: benigntwin.sarif
```

`--format sarif` writes SARIF 2.1.0. Every gate becomes a result, with level `error` when it failed. Reports never contain input text, only ids and counts, so they are safe to upload even when the dataset holds attack payloads.

## Keeping the gate meaningful

- **Test what you ship.** Call the same code path and the same threshold as production. A gate on the bare model says little about a pipeline that normalizes or truncates input first.
- **Version the dataset with the code**, or pin a Hub dataset to a commit, so a failing build always means the detector changed.
- **Use matched pairs from your own domain.** The public datasets show whether a detector reads intent in general. Whether it blocks *your* legitimate requests is something only your own benign inputs can show.
- **Include every language you serve.** A gate on English inputs does not notice a regression in Turkish.
- **Compare with the previous result, not only with a limit.** `benigntwin compare old.json new.json` puts two runs side by side.
