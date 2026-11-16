# BenignTwin report: `hf:protectai/deberta-v3-base-prompt-injection-v2`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `test`
- **Examples:** 240 (120 attacks, 120 benign)
- **Matched pairs:** 120
- **Detector:** `hf:protectai/deberta-v3-base-prompt-injection-v2`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 240/240 rows
- **Run:** 2026-11-16T12:26:53Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 84.2% (76.6–89.6%) 101/120 |
| Benign inputs flagged (false-positive rate) | 57.5% (48.6–66.0%) 69/120 |
| Pairs separated (pair accuracy) | 31.7% (24.0–40.4%) 38/120 |
| Precision | 59.4% (51.9–66.5%) 101/170 |
| Balanced accuracy | 0.633 |
| F1 | 0.697 |
| TP / FP / TN / FN | 101 / 69 / 51 / 19 |
| ROC AUC | 0.720 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 38 |
| Blocked both: reacts to the shared wording | 63 |
| Allowed both: attack missed | 13 |
| Inverted: twin flagged, attack missed | 6 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 10 | 0.0% (0.0–27.8%) 0/10 | 5 | 4 | 1 |
| `authority_claim_bypass` | 10 | 50.0% (23.7–76.3%) 5/10 | 5 | 0 | 0 |
| `direct_instruction_override` | 10 | 70.0% (39.7–89.2%) 7/10 | 3 | 0 | 0 |
| `indirect_content_injection` | 10 | 60.0% (31.3–83.2%) 6/10 | 4 | 0 | 0 |
| `memory_context_poisoning` | 10 | 10.0% (1.8–40.4%) 1/10 | 6 | 0 | 3 |
| `multi_agent_trust_spoofing` | 10 | 50.0% (23.7–76.3%) 5/10 | 4 | 0 | 1 |
| `obfuscation_encoding` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `rag_context_poisoning` | 10 | 40.0% (16.8–68.7%) 4/10 | 6 | 0 | 0 |
| `roleplay_jailbreak` | 10 | 20.0% (5.7–51.0%) 2/10 | 8 | 0 | 0 |
| `sensitive_data_exfiltration` | 10 | 40.0% (16.8–68.7%) 4/10 | 3 | 3 | 0 |
| `system_prompt_extraction` | 10 | 20.0% (5.7–51.0%) 2/10 | 7 | 0 | 1 |
| `tool_action_abuse` | 10 | 20.0% (5.7–51.0%) 2/10 | 2 | 6 | 0 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 20 | 50.0% (23.7–76.3%) 5/10 | 60.0% (31.3–83.2%) 6/10 |
| `authority_claim_bypass` | 20 | 100.0% (72.2–100.0%) 10/10 | 50.0% (23.7–76.3%) 5/10 |
| `direct_instruction_override` | 20 | 100.0% (72.2–100.0%) 10/10 | 30.0% (10.8–60.3%) 3/10 |
| `indirect_content_injection` | 20 | 100.0% (72.2–100.0%) 10/10 | 40.0% (16.8–68.7%) 4/10 |
| `memory_context_poisoning` | 20 | 70.0% (39.7–89.2%) 7/10 | 90.0% (59.6–98.2%) 9/10 |
| `multi_agent_trust_spoofing` | 20 | 90.0% (59.6–98.2%) 9/10 | 50.0% (23.7–76.3%) 5/10 |
| `obfuscation_encoding` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `rag_context_poisoning` | 20 | 100.0% (72.2–100.0%) 10/10 | 60.0% (31.3–83.2%) 6/10 |
| `roleplay_jailbreak` | 20 | 100.0% (72.2–100.0%) 10/10 | 80.0% (49.0–94.3%) 8/10 |
| `sensitive_data_exfiltration` | 20 | 70.0% (39.7–89.2%) 7/10 | 30.0% (10.8–60.3%) 3/10 |
| `system_prompt_extraction` | 20 | 90.0% (59.6–98.2%) 9/10 | 80.0% (49.0–94.3%) 8/10 |
| `tool_action_abuse` | 20 | 40.0% (16.8–68.7%) 4/10 | 20.0% (5.7–51.0%) 2/10 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | n/a | n/a | n/a |
| at most 1.0% of benign inputs flagged | n/a | n/a | n/a |
| at most 5.0% of benign inputs flagged | 1.0000 | 25.0% (18.1–33.4%) 30/120 | 2.5% (0.9–7.1%) 3/120 |

## Latency

Mean 172.3 ms, median 196.9 ms, 95th percentile 223.9 ms per input (240 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
