# BenignTwin report: `heuristic`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `all`
- **Examples:** 1200 (600 attacks, 600 benign)
- **Matched pairs:** 600
- **Detector:** `heuristic`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 1200/1200 rows
- **Run:** 2026-11-16T12:25:51Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 7.0% (5.2–9.3%) 42/600 |
| Benign inputs flagged (false-positive rate) | 1.5% (0.8–2.8%) 9/600 |
| Pairs separated (pair accuracy) | 5.5% (3.9–7.6%) 33/600 |
| Precision | 82.4% (69.7–90.4%) 42/51 |
| Balanced accuracy | 0.527 |
| F1 | 0.129 |
| TP / FP / TN / FN | 42 / 9 / 591 / 558 |
| ROC AUC | 0.559 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 33 |
| Blocked both: reacts to the shared wording | 9 |
| Allowed both: attack missed | 558 |
| Inverted: twin flagged, attack missed | 0 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 50 | 0.0% (0.0–7.1%) 0/50 | 1 | 49 | 0 |
| `authority_claim_bypass` | 50 | 2.0% (0.4–10.5%) 1/50 | 0 | 49 | 0 |
| `direct_instruction_override` | 50 | 20.0% (11.2–33.0%) 10/50 | 1 | 39 | 0 |
| `indirect_content_injection` | 50 | 0.0% (0.0–7.1%) 0/50 | 1 | 49 | 0 |
| `memory_context_poisoning` | 50 | 0.0% (0.0–7.1%) 0/50 | 1 | 49 | 0 |
| `multi_agent_trust_spoofing` | 50 | 2.0% (0.4–10.5%) 1/50 | 0 | 49 | 0 |
| `obfuscation_encoding` | 50 | 0.0% (0.0–7.1%) 0/50 | 1 | 49 | 0 |
| `rag_context_poisoning` | 50 | 20.0% (11.2–33.0%) 10/50 | 0 | 40 | 0 |
| `roleplay_jailbreak` | 50 | 0.0% (0.0–7.1%) 0/50 | 1 | 49 | 0 |
| `sensitive_data_exfiltration` | 50 | 2.0% (0.4–10.5%) 1/50 | 1 | 48 | 0 |
| `system_prompt_extraction` | 50 | 20.0% (11.2–33.0%) 10/50 | 1 | 39 | 0 |
| `tool_action_abuse` | 50 | 0.0% (0.0–7.1%) 0/50 | 1 | 49 | 0 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 100 | 2.0% (0.4–10.5%) 1/50 | 2.0% (0.4–10.5%) 1/50 |
| `authority_claim_bypass` | 100 | 2.0% (0.4–10.5%) 1/50 | 0.0% (0.0–7.1%) 0/50 |
| `direct_instruction_override` | 100 | 22.0% (12.8–35.2%) 11/50 | 2.0% (0.4–10.5%) 1/50 |
| `indirect_content_injection` | 100 | 2.0% (0.4–10.5%) 1/50 | 2.0% (0.4–10.5%) 1/50 |
| `memory_context_poisoning` | 100 | 2.0% (0.4–10.5%) 1/50 | 2.0% (0.4–10.5%) 1/50 |
| `multi_agent_trust_spoofing` | 100 | 2.0% (0.4–10.5%) 1/50 | 0.0% (0.0–7.1%) 0/50 |
| `obfuscation_encoding` | 100 | 2.0% (0.4–10.5%) 1/50 | 2.0% (0.4–10.5%) 1/50 |
| `rag_context_poisoning` | 100 | 20.0% (11.2–33.0%) 10/50 | 0.0% (0.0–7.1%) 0/50 |
| `roleplay_jailbreak` | 100 | 2.0% (0.4–10.5%) 1/50 | 2.0% (0.4–10.5%) 1/50 |
| `sensitive_data_exfiltration` | 100 | 4.0% (1.1–13.5%) 2/50 | 2.0% (0.4–10.5%) 1/50 |
| `system_prompt_extraction` | 100 | 22.0% (12.8–35.2%) 11/50 | 2.0% (0.4–10.5%) 1/50 |
| `tool_action_abuse` | 100 | 2.0% (0.4–10.5%) 1/50 | 2.0% (0.4–10.5%) 1/50 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 0.5500 | 5.3% (3.8–7.4%) 32/600 | 0.0% (0.0–0.6%) 0/600 |
| at most 1.0% of benign inputs flagged | 0.5500 | 5.3% (3.8–7.4%) 32/600 | 0.0% (0.0–0.6%) 0/600 |
| at most 5.0% of benign inputs flagged | 0.2000 | 16.7% (13.9–19.9%) 100/600 | 4.8% (3.4–6.9%) 29/600 |

## Latency

Mean 0.1 ms, median 0.1 ms, 95th percentile 0.1 ms per input (1200 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
