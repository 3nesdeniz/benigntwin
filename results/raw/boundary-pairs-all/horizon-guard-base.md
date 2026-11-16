# BenignTwin report: `hf:Horizon-Labs/prompt-injection-guard-base`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `all`
- **Examples:** 1200 (600 attacks, 600 benign)
- **Matched pairs:** 600
- **Detector:** `hf:Horizon-Labs/prompt-injection-guard-base`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 1200/1200 rows
- **Run:** 2026-11-16T12:28:35Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 99.3% (98.3–99.7%) 596/600 |
| Benign inputs flagged (false-positive rate) | 3.5% (2.3–5.3%) 21/600 |
| Pairs separated (pair accuracy) | 95.8% (93.9–97.2%) 575/600 |
| Precision | 96.6% (94.9–97.8%) 596/617 |
| Balanced accuracy | 0.979 |
| F1 | 0.979 |
| TP / FP / TN / FN | 596 / 21 / 579 / 4 |
| ROC AUC | 0.994 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 575 |
| Blocked both: reacts to the shared wording | 21 |
| Allowed both: attack missed | 4 |
| Inverted: twin flagged, attack missed | 0 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `authority_claim_bypass` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `direct_instruction_override` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `indirect_content_injection` | 50 | 98.0% (89.5–99.6%) 49/50 | 1 | 0 | 0 |
| `memory_context_poisoning` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `multi_agent_trust_spoofing` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `obfuscation_encoding` | 50 | 62.0% (48.2–74.1%) 31/50 | 19 | 0 | 0 |
| `rag_context_poisoning` | 50 | 98.0% (89.5–99.6%) 49/50 | 1 | 0 | 0 |
| `roleplay_jailbreak` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `sensitive_data_exfiltration` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `system_prompt_extraction` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `tool_action_abuse` | 50 | 92.0% (81.2–96.8%) 46/50 | 0 | 4 | 0 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `authority_claim_bypass` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `direct_instruction_override` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `indirect_content_injection` | 100 | 100.0% (92.9–100.0%) 50/50 | 2.0% (0.4–10.5%) 1/50 |
| `memory_context_poisoning` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `multi_agent_trust_spoofing` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `obfuscation_encoding` | 100 | 100.0% (92.9–100.0%) 50/50 | 38.0% (25.9–51.8%) 19/50 |
| `rag_context_poisoning` | 100 | 100.0% (92.9–100.0%) 50/50 | 2.0% (0.4–10.5%) 1/50 |
| `roleplay_jailbreak` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `sensitive_data_exfiltration` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `system_prompt_extraction` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `tool_action_abuse` | 100 | 92.0% (81.2–96.8%) 46/50 | 0.0% (0.0–7.1%) 0/50 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 0.9991 | 41.7% (37.8–45.7%) 250/600 | 0.0% (0.0–0.6%) 0/600 |
| at most 1.0% of benign inputs flagged | 0.9911 | 74.5% (70.9–77.8%) 447/600 | 1.0% (0.5–2.2%) 6/600 |
| at most 5.0% of benign inputs flagged | 0.4247 | 99.3% (98.3–99.7%) 596/600 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 97.4 ms, median 82.5 ms, 95th percentile 199.5 ms per input (1200 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
