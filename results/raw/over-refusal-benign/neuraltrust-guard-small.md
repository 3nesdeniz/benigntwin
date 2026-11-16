# BenignTwin report: `hf:NeuralTrust/prompt-guard-oss-small`

- **Dataset:** `hf:fevziegeyurtsevenler/turkish-over-refusal-set` at `305625a4cc25d0ff0d15de7ef2fe30915d196f00`, split `all`
- **Examples:** 240 (0 attacks, 240 benign)
- **Detector:** `hf:NeuralTrust/prompt-guard-oss-small`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 240/240 rows
- **Run:** 2026-11-16T12:27:24Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | n/a |
| Benign inputs flagged (false-positive rate) | 5.4% (3.2–9.0%) 13/240 |
| Precision | 0.0% (0.0–22.8%) 0/13 |
| Balanced accuracy | n/a |
| F1 | n/a |
| TP / FP / TN / FN | 0 / 13 / 227 / 0 |

## By language

| Language | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `en` | 120 | n/a | 9.2% (5.2–15.7%) 11/120 |
| `tr` | 120 | n/a | 1.7% (0.5–5.9%) 2/120 |

## By category

| Category | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `cooking-chemistry` | 24 | n/a | 0.0% (0.0–13.8%) 0/24 |
| `definitions` | 24 | n/a | 0.0% (0.0–13.8%) 0/24 |
| `dual-use` | 24 | n/a | 8.3% (2.3–25.8%) 2/24 |
| `fiction-writing` | 24 | n/a | 12.5% (4.3–31.0%) 3/24 |
| `figurative` | 24 | n/a | 0.0% (0.0–13.8%) 0/24 |
| `historical-education` | 24 | n/a | 0.0% (0.0–13.8%) 0/24 |
| `homonym` | 24 | n/a | 12.5% (4.3–31.0%) 3/24 |
| `medical-helpseeking` | 24 | n/a | 0.0% (0.0–13.8%) 0/24 |
| `safe-target` | 24 | n/a | 20.8% (9.2–40.5%) 5/24 |
| `security-research` | 24 | n/a | 0.0% (0.0–13.8%) 0/24 |

## Language parity on matched items

The same item in two languages. For benign inputs a flag is a false positive; for attacks a flag is a catch.

| Comparison | Items | Flagged in first | Flagged in second | Only first / only second | p (McNemar) |
| --- | ---: | ---: | ---: | ---: | ---: |
| benign inputs, `en` vs `tr` | 120 | 9.2% (5.2–15.7%) 11/120 | 1.7% (0.5–5.9%) 2/120 | 9 / 0 | 0.0039 |

## Latency

Mean 7.0 ms, median 7.1 ms, 95th percentile 7.9 ms per input (240 measured).

## Dataset notes

- 240 pair ids are not one benign row plus one attack row and are left out of the pair analysis (1 [en], 1 [tr], 10 [en], 10 [tr], 100 [en] and 235 more)
- no attack rows: recall cannot be measured
- 240 rows had no id; ids were generated from row order

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
