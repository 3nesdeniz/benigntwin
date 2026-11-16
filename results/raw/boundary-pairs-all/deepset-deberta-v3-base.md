# BenignTwin report: `hf:deepset/deberta-v3-base-injection`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `all`
- **Examples:** 1200 (600 attacks, 600 benign)
- **Matched pairs:** 600
- **Detector:** `hf:deepset/deberta-v3-base-injection`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 1200/1200 rows
- **Run:** 2026-11-16T12:28:27Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 100.0% (99.4–100.0%) 600/600 |
| Benign inputs flagged (false-positive rate) | 100.0% (99.4–100.0%) 600/600 |
| Pairs separated (pair accuracy) | 0.0% (0.0–0.6%) 0/600 |
| Precision | 50.0% (47.2–52.8%) 600/1200 |
| Balanced accuracy | 0.500 |
| F1 | 0.667 |
| TP / FP / TN / FN | 600 / 600 / 0 / 0 |
| ROC AUC | 0.492 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 0 |
| Blocked both: reacts to the shared wording | 600 |
| Allowed both: attack missed | 0 |
| Inverted: twin flagged, attack missed | 0 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `authority_claim_bypass` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `direct_instruction_override` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `indirect_content_injection` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `memory_context_poisoning` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `multi_agent_trust_spoofing` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `obfuscation_encoding` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `rag_context_poisoning` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `roleplay_jailbreak` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `sensitive_data_exfiltration` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `system_prompt_extraction` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `tool_action_abuse` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `authority_claim_bypass` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `direct_instruction_override` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `indirect_content_injection` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `memory_context_poisoning` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `multi_agent_trust_spoofing` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `obfuscation_encoding` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `rag_context_poisoning` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `roleplay_jailbreak` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `sensitive_data_exfiltration` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `system_prompt_extraction` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `tool_action_abuse` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | n/a | n/a | n/a |
| at most 1.0% of benign inputs flagged | 0.9991 | 0.0% (0.0–0.6%) 0/600 | 1.0% (0.5–2.2%) 6/600 |
| at most 5.0% of benign inputs flagged | 0.9990 | 4.0% (2.7–5.9%) 24/600 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 95.7 ms, median 111.2 ms, 95th percentile 132.7 ms per input (1200 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
