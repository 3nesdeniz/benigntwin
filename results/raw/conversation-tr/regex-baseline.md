# BenignTwin report: `regex-baseline`

- **Dataset:** `hf:3nesdeniz/turkish-conversation-prompt-injection` at `29d7593984f563c4ad56876aa800b9ffd948a2fb`, split `all`
- **Examples:** 750 (150 attacks, 600 benign)
- **Matched pairs:** 150
- **Detector:** `regex-baseline`
- **Decisions taken from the detector's own label:** 750
- **Coverage:** 750/750 rows
- **Run:** 2026-11-16T12:25:51Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 2.0% (0.7–5.7%) 3/150 |
| Benign inputs flagged (false-positive rate) | 0.3% (0.1–1.2%) 2/600 |
| Pairs separated (pair accuracy) | 1.3% (0.4–4.7%) 2/150 |
| Precision | 60.0% (23.1–88.2%) 3/5 |
| Balanced accuracy | 0.508 |
| F1 | 0.039 |
| TP / FP / TN / FN | 3 / 2 / 598 / 147 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 2 |
| Blocked both: reacts to the shared wording | 1 |
| Allowed both: attack missed | 146 |
| Inverted: twin flagged, attack missed | 1 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `authority_claim_bypass` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `direct_instruction_override` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `indirect_content_injection` | 15 | 6.7% (1.2–29.8%) 1/15 | 0 | 14 | 0 |
| `memory_context_poisoning` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `obfuscation_code_switching` | 15 | 6.7% (1.2–29.8%) 1/15 | 1 | 13 | 0 |
| `rag_context_poisoning` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `roleplay_jailbreak` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `sensitive_data_exfiltration` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |
| `system_prompt_extraction` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 14 | 1 |
| `tool_action_abuse` | 15 | 0.0% (0.0–20.4%) 0/15 | 0 | 15 | 0 |

## By category

| Category | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `benign_boundary` | 150 | n/a | 1.3% (0.4–4.7%) 2/150 |
| `benign_daily` | 410 | n/a | 0.0% (0.0–0.9%) 0/410 |
| `benign_technical` | 40 | n/a | 0.0% (0.0–8.8%) 0/40 |
| `prompt_injection` | 150 | 2.0% (0.7–5.7%) 3/150 | n/a |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `authority_claim_bypass` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `direct_instruction_override` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `indirect_content_injection` | 30 | 6.7% (1.2–29.8%) 1/15 | 0.0% (0.0–20.4%) 0/15 |
| `memory_context_poisoning` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `obfuscation_code_switching` | 30 | 13.3% (3.7–37.9%) 2/15 | 6.7% (1.2–29.8%) 1/15 |
| `rag_context_poisoning` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `roleplay_jailbreak` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `sensitive_data_exfiltration` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| `system_prompt_extraction` | 30 | 0.0% (0.0–20.4%) 0/15 | 6.7% (1.2–29.8%) 1/15 |
| `tool_action_abuse` | 30 | 0.0% (0.0–20.4%) 0/15 | 0.0% (0.0–20.4%) 0/15 |
| (none) | 450 | n/a | 0.0% (0.0–0.8%) 0/450 |

## Latency

Mean 0.0 ms, median 0.0 ms, 95th percentile 0.0 ms per input (750 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
