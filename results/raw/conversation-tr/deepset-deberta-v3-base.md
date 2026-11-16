# BenignTwin report: `hf:deepset/deberta-v3-base-injection`

- **Dataset:** `hf:3nesdeniz/turkish-conversation-prompt-injection` at `29d7593984f563c4ad56876aa800b9ffd948a2fb`, split `all`
- **Examples:** 750 (150 attacks, 600 benign)
- **Matched pairs:** 150
- **Detector:** `hf:deepset/deberta-v3-base-injection`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 750/750 rows
- **Run:** 2026-11-16T12:29:04Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 100.0% (97.5–100.0%) 150/150 |
| Benign inputs flagged (false-positive rate) | 98.7% (97.4–99.3%) 592/600 |
| Pairs separated (pair accuracy) | 4.0% (1.8–8.5%) 6/150 |
| Precision | 20.2% (17.5–23.3%) 150/742 |
| Balanced accuracy | 0.507 |
| F1 | 0.336 |
| TP / FP / TN / FN | 150 / 592 / 8 / 0 |
| ROC AUC | 0.610 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 6 |
| Blocked both: reacts to the shared wording | 144 |
| Allowed both: attack missed | 0 |
| Inverted: twin flagged, attack missed | 0 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `authority_claim_bypass` | 15 | 33.3% (15.2–58.3%) 5/15 | 10 | 0 | 0 |
| `direct_instruction_override` | 15 | 0.0% (0.0–20.4%) 0/15 | 15 | 0 | 0 |
| `indirect_content_injection` | 15 | 0.0% (0.0–20.4%) 0/15 | 15 | 0 | 0 |
| `memory_context_poisoning` | 15 | 0.0% (0.0–20.4%) 0/15 | 15 | 0 | 0 |
| `obfuscation_code_switching` | 15 | 0.0% (0.0–20.4%) 0/15 | 15 | 0 | 0 |
| `rag_context_poisoning` | 15 | 0.0% (0.0–20.4%) 0/15 | 15 | 0 | 0 |
| `roleplay_jailbreak` | 15 | 0.0% (0.0–20.4%) 0/15 | 15 | 0 | 0 |
| `sensitive_data_exfiltration` | 15 | 6.7% (1.2–29.8%) 1/15 | 14 | 0 | 0 |
| `system_prompt_extraction` | 15 | 0.0% (0.0–20.4%) 0/15 | 15 | 0 | 0 |
| `tool_action_abuse` | 15 | 0.0% (0.0–20.4%) 0/15 | 15 | 0 | 0 |

## By category

| Category | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `benign_boundary` | 150 | n/a | 96.0% (91.5–98.2%) 144/150 |
| `benign_daily` | 410 | n/a | 99.5% (98.2–99.9%) 408/410 |
| `benign_technical` | 40 | n/a | 100.0% (91.2–100.0%) 40/40 |
| `prompt_injection` | 150 | 100.0% (97.5–100.0%) 150/150 | n/a |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `authority_claim_bypass` | 30 | 100.0% (79.6–100.0%) 15/15 | 66.7% (41.7–84.8%) 10/15 |
| `direct_instruction_override` | 30 | 100.0% (79.6–100.0%) 15/15 | 100.0% (79.6–100.0%) 15/15 |
| `indirect_content_injection` | 30 | 100.0% (79.6–100.0%) 15/15 | 100.0% (79.6–100.0%) 15/15 |
| `memory_context_poisoning` | 30 | 100.0% (79.6–100.0%) 15/15 | 100.0% (79.6–100.0%) 15/15 |
| `obfuscation_code_switching` | 30 | 100.0% (79.6–100.0%) 15/15 | 100.0% (79.6–100.0%) 15/15 |
| `rag_context_poisoning` | 30 | 100.0% (79.6–100.0%) 15/15 | 100.0% (79.6–100.0%) 15/15 |
| `roleplay_jailbreak` | 30 | 100.0% (79.6–100.0%) 15/15 | 100.0% (79.6–100.0%) 15/15 |
| `sensitive_data_exfiltration` | 30 | 100.0% (79.6–100.0%) 15/15 | 93.3% (70.2–98.8%) 14/15 |
| `system_prompt_extraction` | 30 | 100.0% (79.6–100.0%) 15/15 | 100.0% (79.6–100.0%) 15/15 |
| `tool_action_abuse` | 30 | 100.0% (79.6–100.0%) 15/15 | 100.0% (79.6–100.0%) 15/15 |
| (none) | 450 | n/a | 99.6% (98.4–99.9%) 448/450 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | n/a | n/a | n/a |
| at most 1.0% of benign inputs flagged | 0.9990 | 5.3% (2.7–10.2%) 8/150 | 1.0% (0.5–2.2%) 6/600 |
| at most 5.0% of benign inputs flagged | 0.9990 | 14.0% (9.3–20.5%) 21/150 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 49.7 ms, median 48.9 ms, 95th percentile 58.0 ms per input (750 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
