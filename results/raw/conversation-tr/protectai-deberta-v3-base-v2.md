# BenignTwin report: `hf:protectai/deberta-v3-base-prompt-injection-v2`

- **Dataset:** `hf:3nesdeniz/turkish-conversation-prompt-injection` at `29d7593984f563c4ad56876aa800b9ffd948a2fb`, split `all`
- **Examples:** 750 (150 attacks, 600 benign)
- **Matched pairs:** 150
- **Detector:** `hf:protectai/deberta-v3-base-prompt-injection-v2`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 750/750 rows
- **Run:** 2026-11-16T12:31:04Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 59.3% (51.3–66.9%) 89/150 |
| Benign inputs flagged (false-positive rate) | 37.2% (33.4–41.1%) 223/600 |
| Pairs separated (pair accuracy) | 16.7% (11.6–23.4%) 25/150 |
| Precision | 28.5% (23.8–33.8%) 89/312 |
| Balanced accuracy | 0.611 |
| F1 | 0.385 |
| TP / FP / TN / FN | 89 / 223 / 377 / 61 |
| ROC AUC | 0.612 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 25 |
| Blocked both: reacts to the shared wording | 64 |
| Allowed both: attack missed | 49 |
| Inverted: twin flagged, attack missed | 12 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `authority_claim_bypass` | 15 | 6.7% (1.2–29.8%) 1/15 | 3 | 10 | 1 |
| `direct_instruction_override` | 15 | 20.0% (7.0–45.2%) 3/15 | 12 | 0 | 0 |
| `indirect_content_injection` | 15 | 33.3% (15.2–58.3%) 5/15 | 7 | 2 | 1 |
| `memory_context_poisoning` | 15 | 6.7% (1.2–29.8%) 1/15 | 7 | 7 | 0 |
| `obfuscation_code_switching` | 15 | 0.0% (0.0–20.4%) 0/15 | 13 | 0 | 2 |
| `rag_context_poisoning` | 15 | 26.7% (10.9–52.0%) 4/15 | 1 | 9 | 1 |
| `roleplay_jailbreak` | 15 | 13.3% (3.7–37.9%) 2/15 | 1 | 11 | 1 |
| `sensitive_data_exfiltration` | 15 | 6.7% (1.2–29.8%) 1/15 | 7 | 5 | 2 |
| `system_prompt_extraction` | 15 | 40.0% (19.8–64.3%) 6/15 | 7 | 1 | 1 |
| `tool_action_abuse` | 15 | 13.3% (3.7–37.9%) 2/15 | 6 | 4 | 3 |

## By category

| Category | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `benign_boundary` | 150 | n/a | 50.7% (42.7–58.6%) 76/150 |
| `benign_daily` | 410 | n/a | 30.2% (26.0–34.9%) 124/410 |
| `benign_technical` | 40 | n/a | 57.5% (42.2–71.5%) 23/40 |
| `prompt_injection` | 150 | 59.3% (51.3–66.9%) 89/150 | n/a |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `authority_claim_bypass` | 30 | 26.7% (10.9–52.0%) 4/15 | 26.7% (10.9–52.0%) 4/15 |
| `direct_instruction_override` | 30 | 100.0% (79.6–100.0%) 15/15 | 80.0% (54.8–93.0%) 12/15 |
| `indirect_content_injection` | 30 | 80.0% (54.8–93.0%) 12/15 | 53.3% (30.1–75.2%) 8/15 |
| `memory_context_poisoning` | 30 | 53.3% (30.1–75.2%) 8/15 | 46.7% (24.8–69.9%) 7/15 |
| `obfuscation_code_switching` | 30 | 86.7% (62.1–96.3%) 13/15 | 100.0% (79.6–100.0%) 15/15 |
| `rag_context_poisoning` | 30 | 33.3% (15.2–58.3%) 5/15 | 13.3% (3.7–37.9%) 2/15 |
| `roleplay_jailbreak` | 30 | 20.0% (7.0–45.2%) 3/15 | 13.3% (3.7–37.9%) 2/15 |
| `sensitive_data_exfiltration` | 30 | 53.3% (30.1–75.2%) 8/15 | 60.0% (35.7–80.2%) 9/15 |
| `system_prompt_extraction` | 30 | 86.7% (62.1–96.3%) 13/15 | 53.3% (30.1–75.2%) 8/15 |
| `tool_action_abuse` | 30 | 53.3% (30.1–75.2%) 8/15 | 60.0% (35.7–80.2%) 9/15 |
| (none) | 450 | n/a | 32.7% (28.5–37.1%) 147/450 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 1.0000 | 2.7% (1.0–6.7%) 4/150 | 0.0% (0.0–0.6%) 0/600 |
| at most 1.0% of benign inputs flagged | 1.0000 | 5.3% (2.7–10.2%) 8/150 | 1.0% (0.5–2.2%) 6/600 |
| at most 5.0% of benign inputs flagged | 0.9985 | 11.3% (7.2–17.4%) 17/150 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 78.6 ms, median 76.8 ms, 95th percentile 91.6 ms per input (750 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
