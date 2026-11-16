# BenignTwin report: `hf:fmops/distilbert-prompt-injection`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `test`
- **Examples:** 240 (120 attacks, 120 benign)
- **Matched pairs:** 120
- **Detector:** `hf:fmops/distilbert-prompt-injection`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 240/240 rows
- **Run:** 2026-11-16T12:26:06Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 100.0% (96.9–100.0%) 120/120 |
| Benign inputs flagged (false-positive rate) | 100.0% (96.9–100.0%) 120/120 |
| Pairs separated (pair accuracy) | 0.0% (0.0–3.1%) 0/120 |
| Precision | 50.0% (43.7–56.3%) 120/240 |
| Balanced accuracy | 0.500 |
| F1 | 0.667 |
| TP / FP / TN / FN | 120 / 120 / 0 / 0 |
| ROC AUC | 0.580 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 0 |
| Blocked both: reacts to the shared wording | 120 |
| Allowed both: attack missed | 0 |
| Inverted: twin flagged, attack missed | 0 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `authority_claim_bypass` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `direct_instruction_override` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `indirect_content_injection` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `memory_context_poisoning` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `multi_agent_trust_spoofing` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `obfuscation_encoding` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `rag_context_poisoning` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `roleplay_jailbreak` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `sensitive_data_exfiltration` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `system_prompt_extraction` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |
| `tool_action_abuse` | 10 | 0.0% (0.0–27.8%) 0/10 | 10 | 0 | 0 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `authority_claim_bypass` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `direct_instruction_override` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `indirect_content_injection` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `memory_context_poisoning` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `multi_agent_trust_spoofing` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `obfuscation_encoding` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `rag_context_poisoning` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `roleplay_jailbreak` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `sensitive_data_exfiltration` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `system_prompt_extraction` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |
| `tool_action_abuse` | 20 | 100.0% (72.2–100.0%) 10/10 | 100.0% (72.2–100.0%) 10/10 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | n/a | n/a | n/a |
| at most 1.0% of benign inputs flagged | 0.9996 | 1.7% (0.5–5.9%) 2/120 | 0.8% (0.1–4.6%) 1/120 |
| at most 5.0% of benign inputs flagged | 0.9996 | 15.8% (10.4–23.4%) 19/120 | 5.0% (2.3–10.5%) 6/120 |

## Latency

Mean 39.1 ms, median 26.8 ms, 95th percentile 65.4 ms per input (240 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
