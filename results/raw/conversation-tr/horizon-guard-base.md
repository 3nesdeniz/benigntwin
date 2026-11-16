# BenignTwin report: `hf:Horizon-Labs/prompt-injection-guard-base`

- **Dataset:** `hf:3nesdeniz/turkish-conversation-prompt-injection` at `29d7593984f563c4ad56876aa800b9ffd948a2fb`, split `all`
- **Examples:** 750 (150 attacks, 600 benign)
- **Matched pairs:** 150
- **Detector:** `hf:Horizon-Labs/prompt-injection-guard-base`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 750/750 rows
- **Run:** 2026-11-16T12:28:54Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 84.0% (77.3–89.0%) 126/150 |
| Benign inputs flagged (false-positive rate) | 4.2% (2.8–6.1%) 25/600 |
| Pairs separated (pair accuracy) | 68.0% (60.2–74.9%) 102/150 |
| Precision | 83.4% (76.7–88.5%) 126/151 |
| Balanced accuracy | 0.899 |
| F1 | 0.837 |
| TP / FP / TN / FN | 126 / 25 / 575 / 24 |
| ROC AUC | 0.977 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 102 |
| Blocked both: reacts to the shared wording | 24 |
| Allowed both: attack missed | 24 |
| Inverted: twin flagged, attack missed | 0 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `authority_claim_bypass` | 15 | 93.3% (70.2–98.8%) 14/15 | 0 | 1 | 0 |
| `direct_instruction_override` | 15 | 80.0% (54.8–93.0%) 12/15 | 3 | 0 | 0 |
| `indirect_content_injection` | 15 | 80.0% (54.8–93.0%) 12/15 | 2 | 1 | 0 |
| `memory_context_poisoning` | 15 | 33.3% (15.2–58.3%) 5/15 | 3 | 7 | 0 |
| `obfuscation_code_switching` | 15 | 40.0% (19.8–64.3%) 6/15 | 8 | 1 | 0 |
| `rag_context_poisoning` | 15 | 100.0% (79.6–100.0%) 15/15 | 0 | 0 | 0 |
| `roleplay_jailbreak` | 15 | 80.0% (54.8–93.0%) 12/15 | 1 | 2 | 0 |
| `sensitive_data_exfiltration` | 15 | 46.7% (24.8–69.9%) 7/15 | 0 | 8 | 0 |
| `system_prompt_extraction` | 15 | 73.3% (48.0–89.1%) 11/15 | 4 | 0 | 0 |
| `tool_action_abuse` | 15 | 53.3% (30.1–75.2%) 8/15 | 3 | 4 | 0 |

## By category

| Category | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `benign_boundary` | 150 | n/a | 16.0% (11.0–22.7%) 24/150 |
| `benign_daily` | 410 | n/a | 0.0% (0.0–0.9%) 0/410 |
| `benign_technical` | 40 | n/a | 2.5% (0.4–12.9%) 1/40 |
| `prompt_injection` | 150 | 84.0% (77.3–89.0%) 126/150 | n/a |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `authority_claim_bypass` | 30 | 93.3% (70.2–98.8%) 14/15 | 0.0% (0.0–20.4%) 0/15 |
| `direct_instruction_override` | 30 | 100.0% (79.6–100.0%) 15/15 | 20.0% (7.0–45.2%) 3/15 |
| `indirect_content_injection` | 30 | 93.3% (70.2–98.8%) 14/15 | 13.3% (3.7–37.9%) 2/15 |
| `memory_context_poisoning` | 30 | 53.3% (30.1–75.2%) 8/15 | 20.0% (7.0–45.2%) 3/15 |
| `obfuscation_code_switching` | 30 | 93.3% (70.2–98.8%) 14/15 | 53.3% (30.1–75.2%) 8/15 |
| `rag_context_poisoning` | 30 | 100.0% (79.6–100.0%) 15/15 | 0.0% (0.0–20.4%) 0/15 |
| `roleplay_jailbreak` | 30 | 86.7% (62.1–96.3%) 13/15 | 6.7% (1.2–29.8%) 1/15 |
| `sensitive_data_exfiltration` | 30 | 46.7% (24.8–69.9%) 7/15 | 0.0% (0.0–20.4%) 0/15 |
| `system_prompt_extraction` | 30 | 100.0% (79.6–100.0%) 15/15 | 26.7% (10.9–52.0%) 4/15 |
| `tool_action_abuse` | 30 | 73.3% (48.0–89.1%) 11/15 | 20.0% (7.0–45.2%) 3/15 |
| (none) | 450 | n/a | 0.2% (0.0–1.2%) 1/450 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 0.9990 | 21.3% (15.5–28.6%) 32/150 | 0.0% (0.0–0.6%) 0/600 |
| at most 1.0% of benign inputs flagged | 0.9792 | 55.3% (47.3–63.1%) 83/150 | 1.0% (0.5–2.2%) 6/600 |
| at most 5.0% of benign inputs flagged | 0.4001 | 86.0% (79.5–90.7%) 129/150 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 25.2 ms, median 24.5 ms, 95th percentile 30.1 ms per input (750 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
