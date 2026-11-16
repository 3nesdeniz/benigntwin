# BenignTwin report: `hf:proventra/mdeberta-v3-base-prompt-injection`

- **Dataset:** `hf:3nesdeniz/turkish-conversation-prompt-injection` at `29d7593984f563c4ad56876aa800b9ffd948a2fb`, split `all`
- **Examples:** 750 (150 attacks, 600 benign)
- **Matched pairs:** 150
- **Detector:** `hf:proventra/mdeberta-v3-base-prompt-injection`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 750/750 rows
- **Run:** 2026-11-16T12:32:45Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 60.7% (52.7–68.1%) 91/150 |
| Benign inputs flagged (false-positive rate) | 8.7% (6.7–11.2%) 52/600 |
| Pairs separated (pair accuracy) | 36.0% (28.8–43.9%) 54/150 |
| Precision | 63.6% (55.5–71.1%) 91/143 |
| Balanced accuracy | 0.760 |
| F1 | 0.621 |
| TP / FP / TN / FN | 91 / 52 / 548 / 59 |
| ROC AUC | 0.863 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 54 |
| Blocked both: reacts to the shared wording | 37 |
| Allowed both: attack missed | 52 |
| Inverted: twin flagged, attack missed | 7 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `authority_claim_bypass` | 15 | 66.7% (41.7–84.8%) 10/15 | 0 | 4 | 1 |
| `direct_instruction_override` | 15 | 40.0% (19.8–64.3%) 6/15 | 8 | 1 | 0 |
| `indirect_content_injection` | 15 | 66.7% (41.7–84.8%) 10/15 | 1 | 4 | 0 |
| `memory_context_poisoning` | 15 | 33.3% (15.2–58.3%) 5/15 | 0 | 8 | 2 |
| `obfuscation_code_switching` | 15 | 20.0% (7.0–45.2%) 3/15 | 11 | 1 | 0 |
| `rag_context_poisoning` | 15 | 13.3% (3.7–37.9%) 2/15 | 3 | 10 | 0 |
| `roleplay_jailbreak` | 15 | 60.0% (35.7–80.2%) 9/15 | 2 | 4 | 0 |
| `sensitive_data_exfiltration` | 15 | 13.3% (3.7–37.9%) 2/15 | 1 | 11 | 1 |
| `system_prompt_extraction` | 15 | 40.0% (19.8–64.3%) 6/15 | 7 | 1 | 1 |
| `tool_action_abuse` | 15 | 6.7% (1.2–29.8%) 1/15 | 4 | 8 | 2 |

## By category

| Category | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `benign_boundary` | 150 | n/a | 29.3% (22.6–37.1%) 44/150 |
| `benign_daily` | 410 | n/a | 1.7% (0.8–3.5%) 7/410 |
| `benign_technical` | 40 | n/a | 2.5% (0.4–12.9%) 1/40 |
| `prompt_injection` | 150 | 60.7% (52.7–68.1%) 91/150 | n/a |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `authority_claim_bypass` | 30 | 66.7% (41.7–84.8%) 10/15 | 6.7% (1.2–29.8%) 1/15 |
| `direct_instruction_override` | 30 | 93.3% (70.2–98.8%) 14/15 | 53.3% (30.1–75.2%) 8/15 |
| `indirect_content_injection` | 30 | 73.3% (48.0–89.1%) 11/15 | 6.7% (1.2–29.8%) 1/15 |
| `memory_context_poisoning` | 30 | 33.3% (15.2–58.3%) 5/15 | 13.3% (3.7–37.9%) 2/15 |
| `obfuscation_code_switching` | 30 | 93.3% (70.2–98.8%) 14/15 | 73.3% (48.0–89.1%) 11/15 |
| `rag_context_poisoning` | 30 | 33.3% (15.2–58.3%) 5/15 | 20.0% (7.0–45.2%) 3/15 |
| `roleplay_jailbreak` | 30 | 73.3% (48.0–89.1%) 11/15 | 13.3% (3.7–37.9%) 2/15 |
| `sensitive_data_exfiltration` | 30 | 20.0% (7.0–45.2%) 3/15 | 13.3% (3.7–37.9%) 2/15 |
| `system_prompt_extraction` | 30 | 86.7% (62.1–96.3%) 13/15 | 53.3% (30.1–75.2%) 8/15 |
| `tool_action_abuse` | 30 | 33.3% (15.2–58.3%) 5/15 | 40.0% (19.8–64.3%) 6/15 |
| (none) | 450 | n/a | 1.8% (0.9–3.5%) 8/450 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 0.9999 | 5.3% (2.7–10.2%) 8/150 | 0.0% (0.0–0.6%) 0/600 |
| at most 1.0% of benign inputs flagged | 0.9999 | 14.0% (9.3–20.5%) 21/150 | 1.0% (0.5–2.2%) 6/600 |
| at most 5.0% of benign inputs flagged | 0.9979 | 50.7% (42.7–58.6%) 76/150 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 68.1 ms, median 67.0 ms, 95th percentile 76.7 ms per input (750 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
