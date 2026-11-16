# BenignTwin report: `hf:NeuralTrust/prompt-guard-oss-small`

- **Dataset:** `hf:3nesdeniz/turkish-conversation-prompt-injection` at `29d7593984f563c4ad56876aa800b9ffd948a2fb`, split `all`
- **Examples:** 750 (150 attacks, 600 benign)
- **Matched pairs:** 150
- **Detector:** `hf:NeuralTrust/prompt-guard-oss-small`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 750/750 rows
- **Run:** 2026-11-16T12:27:22Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 70.0% (62.2–76.8%) 105/150 |
| Benign inputs flagged (false-positive rate) | 5.3% (3.8–7.4%) 32/600 |
| Pairs separated (pair accuracy) | 50.0% (42.1–57.9%) 75/150 |
| Precision | 76.6% (68.9–82.9%) 105/137 |
| Balanced accuracy | 0.823 |
| F1 | 0.732 |
| TP / FP / TN / FN | 105 / 32 / 568 / 45 |
| ROC AUC | 0.857 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 75 |
| Blocked both: reacts to the shared wording | 30 |
| Allowed both: attack missed | 43 |
| Inverted: twin flagged, attack missed | 2 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `authority_claim_bypass` | 15 | 53.3% (30.1–75.2%) 8/15 | 1 | 5 | 1 |
| `direct_instruction_override` | 15 | 80.0% (54.8–93.0%) 12/15 | 3 | 0 | 0 |
| `indirect_content_injection` | 15 | 66.7% (41.7–84.8%) 10/15 | 1 | 4 | 0 |
| `memory_context_poisoning` | 15 | 40.0% (19.8–64.3%) 6/15 | 0 | 8 | 1 |
| `obfuscation_code_switching` | 15 | 53.3% (30.1–75.2%) 8/15 | 7 | 0 | 0 |
| `rag_context_poisoning` | 15 | 40.0% (19.8–64.3%) 6/15 | 5 | 4 | 0 |
| `roleplay_jailbreak` | 15 | 66.7% (41.7–84.8%) 10/15 | 3 | 2 | 0 |
| `sensitive_data_exfiltration` | 15 | 20.0% (7.0–45.2%) 3/15 | 0 | 12 | 0 |
| `system_prompt_extraction` | 15 | 40.0% (19.8–64.3%) 6/15 | 9 | 0 | 0 |
| `tool_action_abuse` | 15 | 40.0% (19.8–64.3%) 6/15 | 1 | 8 | 0 |

## By category

| Category | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `benign_boundary` | 150 | n/a | 21.3% (15.5–28.6%) 32/150 |
| `benign_daily` | 410 | n/a | 0.0% (0.0–0.9%) 0/410 |
| `benign_technical` | 40 | n/a | 0.0% (0.0–8.8%) 0/40 |
| `prompt_injection` | 150 | 70.0% (62.2–76.8%) 105/150 | n/a |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `authority_claim_bypass` | 30 | 60.0% (35.7–80.2%) 9/15 | 13.3% (3.7–37.9%) 2/15 |
| `direct_instruction_override` | 30 | 100.0% (79.6–100.0%) 15/15 | 20.0% (7.0–45.2%) 3/15 |
| `indirect_content_injection` | 30 | 73.3% (48.0–89.1%) 11/15 | 6.7% (1.2–29.8%) 1/15 |
| `memory_context_poisoning` | 30 | 40.0% (19.8–64.3%) 6/15 | 6.7% (1.2–29.8%) 1/15 |
| `obfuscation_code_switching` | 30 | 100.0% (79.6–100.0%) 15/15 | 46.7% (24.8–69.9%) 7/15 |
| `rag_context_poisoning` | 30 | 73.3% (48.0–89.1%) 11/15 | 33.3% (15.2–58.3%) 5/15 |
| `roleplay_jailbreak` | 30 | 86.7% (62.1–96.3%) 13/15 | 20.0% (7.0–45.2%) 3/15 |
| `sensitive_data_exfiltration` | 30 | 20.0% (7.0–45.2%) 3/15 | 0.0% (0.0–20.4%) 0/15 |
| `system_prompt_extraction` | 30 | 100.0% (79.6–100.0%) 15/15 | 60.0% (35.7–80.2%) 9/15 |
| `tool_action_abuse` | 30 | 46.7% (24.8–69.9%) 7/15 | 6.7% (1.2–29.8%) 1/15 |
| (none) | 450 | n/a | 0.0% (0.0–0.8%) 0/450 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | n/a | n/a | n/a |
| at most 1.0% of benign inputs flagged | n/a | n/a | n/a |
| at most 5.0% of benign inputs flagged | 0.8711 | 66.7% (58.8–73.7%) 100/150 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 9.9 ms, median 9.7 ms, 95th percentile 12.0 ms per input (750 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
