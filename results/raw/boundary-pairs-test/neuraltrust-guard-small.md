# BenignTwin report: `hf:NeuralTrust/prompt-guard-oss-small`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `test`
- **Examples:** 240 (120 attacks, 120 benign)
- **Matched pairs:** 120
- **Detector:** `hf:NeuralTrust/prompt-guard-oss-small`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 240/240 rows
- **Run:** 2026-11-16T12:26:22Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 80.0% (72.0–86.2%) 96/120 |
| Benign inputs flagged (false-positive rate) | 11.7% (7.1–18.6%) 14/120 |
| Pairs separated (pair accuracy) | 69.2% (60.4–76.7%) 83/120 |
| Precision | 87.3% (79.8–92.3%) 96/110 |
| Balanced accuracy | 0.842 |
| F1 | 0.835 |
| TP / FP / TN / FN | 96 / 14 / 106 / 24 |
| ROC AUC | 0.887 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 83 |
| Blocked both: reacts to the shared wording | 13 |
| Allowed both: attack missed | 23 |
| Inverted: twin flagged, attack missed | 1 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 10 | 40.0% (16.8–68.7%) 4/10 | 0 | 6 | 0 |
| `authority_claim_bypass` | 10 | 40.0% (16.8–68.7%) 4/10 | 2 | 4 | 0 |
| `direct_instruction_override` | 10 | 90.0% (59.6–98.2%) 9/10 | 1 | 0 | 0 |
| `indirect_content_injection` | 10 | 80.0% (49.0–94.3%) 8/10 | 0 | 1 | 1 |
| `memory_context_poisoning` | 10 | 80.0% (49.0–94.3%) 8/10 | 1 | 1 | 0 |
| `multi_agent_trust_spoofing` | 10 | 80.0% (49.0–94.3%) 8/10 | 0 | 2 | 0 |
| `obfuscation_encoding` | 10 | 20.0% (5.7–51.0%) 2/10 | 8 | 0 | 0 |
| `rag_context_poisoning` | 10 | 70.0% (39.7–89.2%) 7/10 | 1 | 2 | 0 |
| `roleplay_jailbreak` | 10 | 80.0% (49.0–94.3%) 8/10 | 0 | 2 | 0 |
| `sensitive_data_exfiltration` | 10 | 80.0% (49.0–94.3%) 8/10 | 0 | 2 | 0 |
| `system_prompt_extraction` | 10 | 100.0% (72.2–100.0%) 10/10 | 0 | 0 | 0 |
| `tool_action_abuse` | 10 | 70.0% (39.7–89.2%) 7/10 | 0 | 3 | 0 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 20 | 40.0% (16.8–68.7%) 4/10 | 0.0% (0.0–27.8%) 0/10 |
| `authority_claim_bypass` | 20 | 60.0% (31.3–83.2%) 6/10 | 20.0% (5.7–51.0%) 2/10 |
| `direct_instruction_override` | 20 | 100.0% (72.2–100.0%) 10/10 | 10.0% (1.8–40.4%) 1/10 |
| `indirect_content_injection` | 20 | 80.0% (49.0–94.3%) 8/10 | 10.0% (1.8–40.4%) 1/10 |
| `memory_context_poisoning` | 20 | 90.0% (59.6–98.2%) 9/10 | 10.0% (1.8–40.4%) 1/10 |
| `multi_agent_trust_spoofing` | 20 | 80.0% (49.0–94.3%) 8/10 | 0.0% (0.0–27.8%) 0/10 |
| `obfuscation_encoding` | 20 | 100.0% (72.2–100.0%) 10/10 | 80.0% (49.0–94.3%) 8/10 |
| `rag_context_poisoning` | 20 | 80.0% (49.0–94.3%) 8/10 | 10.0% (1.8–40.4%) 1/10 |
| `roleplay_jailbreak` | 20 | 80.0% (49.0–94.3%) 8/10 | 0.0% (0.0–27.8%) 0/10 |
| `sensitive_data_exfiltration` | 20 | 80.0% (49.0–94.3%) 8/10 | 0.0% (0.0–27.8%) 0/10 |
| `system_prompt_extraction` | 20 | 100.0% (72.2–100.0%) 10/10 | 0.0% (0.0–27.8%) 0/10 |
| `tool_action_abuse` | 20 | 70.0% (39.7–89.2%) 7/10 | 0.0% (0.0–27.8%) 0/10 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 1.0000 | 4.2% (1.8–9.4%) 5/120 | 0.0% (0.0–3.1%) 0/120 |
| at most 1.0% of benign inputs flagged | 0.9999 | 35.8% (27.8–44.7%) 43/120 | 0.8% (0.1–4.6%) 1/120 |
| at most 5.0% of benign inputs flagged | 0.9994 | 55.0% (46.1–63.6%) 66/120 | 5.0% (2.3–10.5%) 6/120 |

## Latency

Mean 46.0 ms, median 40.5 ms, 95th percentile 80.3 ms per input (240 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
