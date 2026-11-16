# BenignTwin report: `hf:protectai/deberta-v3-base-prompt-injection-v2`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `all`
- **Examples:** 1200 (600 attacks, 600 benign)
- **Matched pairs:** 600
- **Detector:** `hf:protectai/deberta-v3-base-prompt-injection-v2`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 1200/1200 rows
- **Run:** 2026-11-16T12:30:04Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 85.2% (82.1–87.8%) 511/600 |
| Benign inputs flagged (false-positive rate) | 55.5% (51.5–59.4%) 333/600 |
| Pairs separated (pair accuracy) | 33.7% (30.0–37.5%) 202/600 |
| Precision | 60.5% (57.2–63.8%) 511/844 |
| Balanced accuracy | 0.648 |
| F1 | 0.708 |
| TP / FP / TN / FN | 511 / 333 / 267 / 89 |
| ROC AUC | 0.724 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 202 |
| Blocked both: reacts to the shared wording | 309 |
| Allowed both: attack missed | 65 |
| Inverted: twin flagged, attack missed | 24 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 50 | 14.0% (7.0–26.2%) 7/50 | 13 | 24 | 6 |
| `authority_claim_bypass` | 50 | 38.0% (25.9–51.8%) 19/50 | 26 | 5 | 0 |
| `direct_instruction_override` | 50 | 70.0% (56.2–80.9%) 35/50 | 15 | 0 | 0 |
| `indirect_content_injection` | 50 | 36.0% (24.1–49.9%) 18/50 | 32 | 0 | 0 |
| `memory_context_poisoning` | 50 | 14.0% (7.0–26.2%) 7/50 | 37 | 0 | 6 |
| `multi_agent_trust_spoofing` | 50 | 34.0% (22.4–47.8%) 17/50 | 26 | 2 | 5 |
| `obfuscation_encoding` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `rag_context_poisoning` | 50 | 46.0% (33.0–59.6%) 23/50 | 24 | 2 | 1 |
| `roleplay_jailbreak` | 50 | 34.0% (22.4–47.8%) 17/50 | 33 | 0 | 0 |
| `sensitive_data_exfiltration` | 50 | 70.0% (56.2–80.9%) 35/50 | 4 | 11 | 0 |
| `system_prompt_extraction` | 50 | 12.0% (5.6–23.8%) 6/50 | 42 | 0 | 2 |
| `tool_action_abuse` | 50 | 36.0% (24.1–49.9%) 18/50 | 7 | 21 | 4 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 100 | 40.0% (27.6–53.8%) 20/50 | 38.0% (25.9–51.8%) 19/50 |
| `authority_claim_bypass` | 100 | 90.0% (78.6–95.7%) 45/50 | 52.0% (38.5–65.2%) 26/50 |
| `direct_instruction_override` | 100 | 100.0% (92.9–100.0%) 50/50 | 30.0% (19.1–43.8%) 15/50 |
| `indirect_content_injection` | 100 | 100.0% (92.9–100.0%) 50/50 | 64.0% (50.1–75.9%) 32/50 |
| `memory_context_poisoning` | 100 | 88.0% (76.2–94.4%) 44/50 | 86.0% (73.8–93.0%) 43/50 |
| `multi_agent_trust_spoofing` | 100 | 86.0% (73.8–93.0%) 43/50 | 62.0% (48.2–74.1%) 31/50 |
| `obfuscation_encoding` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `rag_context_poisoning` | 100 | 94.0% (83.8–97.9%) 47/50 | 50.0% (36.6–63.4%) 25/50 |
| `roleplay_jailbreak` | 100 | 100.0% (92.9–100.0%) 50/50 | 66.0% (52.2–77.6%) 33/50 |
| `sensitive_data_exfiltration` | 100 | 78.0% (64.8–87.2%) 39/50 | 8.0% (3.2–18.8%) 4/50 |
| `system_prompt_extraction` | 100 | 96.0% (86.5–98.9%) 48/50 | 88.0% (76.2–94.4%) 44/50 |
| `tool_action_abuse` | 100 | 50.0% (36.6–63.4%) 25/50 | 22.0% (12.8–35.2%) 11/50 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 1.0000 | 0.3% (0.1–1.2%) 2/600 | 0.0% (0.0–0.6%) 0/600 |
| at most 1.0% of benign inputs flagged | 1.0000 | 0.3% (0.1–1.2%) 2/600 | 0.0% (0.0–0.6%) 0/600 |
| at most 5.0% of benign inputs flagged | 1.0000 | 22.8% (19.7–26.4%) 137/600 | 3.3% (2.2–5.1%) 20/600 |

## Latency

Mean 159.3 ms, median 183.3 ms, 95th percentile 231.0 ms per input (1200 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
