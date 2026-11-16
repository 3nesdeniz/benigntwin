# BenignTwin report: `hf:testsavantai/prompt-injection-defender-base-v1`

- **Dataset:** `hf:3nesdeniz/turkish-conversation-prompt-injection` at `29d7593984f563c4ad56876aa800b9ffd948a2fb`, split `all`
- **Examples:** 750 (150 attacks, 600 benign)
- **Matched pairs:** 150
- **Detector:** `hf:testsavantai/prompt-injection-defender-base-v1`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 750/750 rows
- **Run:** 2026-11-16T12:29:43Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 8.0% (4.6–13.5%) 12/150 |
| Benign inputs flagged (false-positive rate) | 6.0% (4.4–8.2%) 36/600 |
| Pairs separated (pair accuracy) | 4.7% (2.3–9.3%) 7/150 |
| Precision | 25.0% (14.9–38.8%) 12/48 |
| Balanced accuracy | 0.510 |
| F1 | 0.121 |
| TP / FP / TN / FN | 12 / 36 / 564 / 138 |
| ROC AUC | 0.377 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 7 |
| Blocked both: reacts to the shared wording | 5 |
| Allowed both: attack missed | 134 |
| Inverted: twin flagged, attack missed | 4 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `authority_claim_bypass` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `direct_instruction_override` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `indirect_content_injection` | 15 | 13.3% (3.7–37.9%) 2/15 | 0 | 13 | 0 |
| `memory_context_poisoning` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `obfuscation_code_switching` | 15 | 26.7% (10.9–52.0%) 4/15 | 5 | 3 | 3 |
| `rag_context_poisoning` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `roleplay_jailbreak` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `sensitive_data_exfiltration` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `system_prompt_extraction` | 15 | 6.7% (1.2–29.8%) 1/15 | 0 | 14 | 0 |
| `tool_action_abuse` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 14 | 1 |

## By category

| Category | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `benign_boundary` | 150 | n/a | 6.0% (3.2–11.0%) 9/150 |
| `benign_daily` | 410 | n/a | 4.4% (2.8–6.8%) 18/410 |
| `benign_technical` | 40 | n/a | 22.5% (12.3–37.5%) 9/40 |
| `prompt_injection` | 150 | 8.0% (4.6–13.5%) 12/150 | n/a |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `authority_claim_bypass` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `direct_instruction_override` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `indirect_content_injection` | 30 | 13.3% (3.7–37.9%) 2/15 | 0.0% (0.0–20.4%) 0/15 |
| `memory_context_poisoning` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `obfuscation_code_switching` | 30 | 60.0% (35.7–80.2%) 9/15 | 53.3% (30.1–75.2%) 8/15 |
| `rag_context_poisoning` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `roleplay_jailbreak` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `sensitive_data_exfiltration` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `system_prompt_extraction` | 30 | 6.7% (1.2–29.8%) 1/15 | 0.0% (0.0–20.4%) 0/15 |
| `tool_action_abuse` | 30 | 0.0% (0.0–20.4%) 0/15 | 6.7% (1.2–29.8%) 1/15 |
| (none) | 450 | n/a | 6.0% (4.2–8.6%) 27/450 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 0.9810 | 3.3% (1.4–7.6%) 5/150 | 0.0% (0.0–0.6%) 0/600 |
| at most 1.0% of benign inputs flagged | 0.8441 | 4.7% (2.3–9.3%) 7/150 | 1.0% (0.5–2.2%) 6/600 |
| at most 5.0% of benign inputs flagged | 0.5284 | 8.0% (4.6–13.5%) 12/150 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 55.5 ms, median 54.8 ms, 95th percentile 63.8 ms per input (750 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
