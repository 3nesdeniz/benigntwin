# BenignTwin report: `hf:patronus-studio/wolf-defender-prompt-injection`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `all`
- **Examples:** 1200 (600 attacks, 600 benign)
- **Matched pairs:** 600
- **Detector:** `hf:patronus-studio/wolf-defender-prompt-injection`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 1200/1200 rows
- **Run:** 2026-11-16T12:31:16Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 99.7% (98.8–99.9%) 598/600 |
| Benign inputs flagged (false-positive rate) | 0.2% (0.0–0.9%) 1/600 |
| Pairs separated (pair accuracy) | 99.5% (98.5–99.8%) 597/600 |
| Precision | 99.8% (99.1–100.0%) 598/599 |
| Balanced accuracy | 0.998 |
| F1 | 0.997 |
| TP / FP / TN / FN | 598 / 1 / 599 / 2 |
| ROC AUC | 1.000 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 597 |
| Blocked both: reacts to the shared wording | 1 |
| Allowed both: attack missed | 2 |
| Inverted: twin flagged, attack missed | 0 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `authority_claim_bypass` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `direct_instruction_override` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `indirect_content_injection` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `memory_context_poisoning` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `multi_agent_trust_spoofing` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `obfuscation_encoding` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `rag_context_poisoning` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `roleplay_jailbreak` | 50 | 98.0% (89.5–99.6%) 49/50 | 1 | 0 | 0 |
| `sensitive_data_exfiltration` | 50 | 96.0% (86.5–98.9%) 48/50 | 0 | 2 | 0 |
| `system_prompt_extraction` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |
| `tool_action_abuse` | 50 | 100.0% (92.9–100.0%) 50/50 | 0 | 0 | 0 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `authority_claim_bypass` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `direct_instruction_override` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `indirect_content_injection` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `memory_context_poisoning` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `multi_agent_trust_spoofing` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `obfuscation_encoding` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `rag_context_poisoning` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `roleplay_jailbreak` | 100 | 100.0% (92.9–100.0%) 50/50 | 2.0% (0.4–10.5%) 1/50 |
| `sensitive_data_exfiltration` | 100 | 96.0% (86.5–98.9%) 48/50 | 0.0% (0.0–7.1%) 0/50 |
| `system_prompt_extraction` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |
| `tool_action_abuse` | 100 | 100.0% (92.9–100.0%) 50/50 | 0.0% (0.0–7.1%) 0/50 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 0.7843 | 98.8% (97.6–99.4%) 593/600 | 0.0% (0.0–0.6%) 0/600 |
| at most 1.0% of benign inputs flagged | 0.0017 | 100.0% (99.4–100.0%) 600/600 | 1.0% (0.5–2.2%) 6/600 |
| at most 5.0% of benign inputs flagged | 0.0001 | 100.0% (99.4–100.0%) 600/600 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 209.5 ms, median 183.0 ms, 95th percentile 409.4 ms per input (1200 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
