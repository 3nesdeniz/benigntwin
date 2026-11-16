# BenignTwin report: `hf:testsavantai/prompt-injection-defender-base-v1`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `all`
- **Examples:** 1200 (600 attacks, 600 benign)
- **Matched pairs:** 600
- **Detector:** `hf:testsavantai/prompt-injection-defender-base-v1`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 1200/1200 rows
- **Run:** 2026-11-16T12:29:01Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 77.8% (74.3–81.0%) 467/600 |
| Benign inputs flagged (false-positive rate) | 73.8% (70.2–77.2%) 443/600 |
| Pairs separated (pair accuracy) | 17.3% (14.5–20.6%) 104/600 |
| Precision | 51.3% (48.1–54.6%) 467/910 |
| Balanced accuracy | 0.520 |
| F1 | 0.619 |
| TP / FP / TN / FN | 467 / 443 / 157 / 133 |
| ROC AUC | 0.607 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 104 |
| Blocked both: reacts to the shared wording | 363 |
| Allowed both: attack missed | 53 |
| Inverted: twin flagged, attack missed | 80 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 50 | 0.0% (0.0–7.1%) 0/50 | 14 | 18 | 18 |
| `authority_claim_bypass` | 50 | 26.0% (15.9–39.6%) 13/50 | 21 | 4 | 12 |
| `direct_instruction_override` | 50 | 66.0% (52.2–77.6%) 33/50 | 17 | 0 | 0 |
| `indirect_content_injection` | 50 | 18.0% (9.8–30.8%) 9/50 | 40 | 0 | 1 |
| `memory_context_poisoning` | 50 | 0.0% (0.0–7.1%) 0/50 | 44 | 0 | 6 |
| `multi_agent_trust_spoofing` | 50 | 2.0% (0.4–10.5%) 1/50 | 33 | 8 | 8 |
| `obfuscation_encoding` | 50 | 0.0% (0.0–7.1%) 0/50 | 50 | 0 | 0 |
| `rag_context_poisoning` | 50 | 16.0% (8.3–28.5%) 8/50 | 32 | 5 | 5 |
| `roleplay_jailbreak` | 50 | 36.0% (24.1–49.9%) 18/50 | 16 | 8 | 8 |
| `sensitive_data_exfiltration` | 50 | 4.0% (1.1–13.5%) 2/50 | 38 | 0 | 10 |
| `system_prompt_extraction` | 50 | 0.0% (0.0–7.1%) 0/50 | 48 | 0 | 2 |
| `tool_action_abuse` | 50 | 40.0% (27.6–53.8%) 20/50 | 10 | 10 | 10 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 100 | 28.0% (17.5–41.7%) 14/50 | 64.0% (50.1–75.9%) 32/50 |
| `authority_claim_bypass` | 100 | 68.0% (54.2–79.2%) 34/50 | 66.0% (52.2–77.6%) 33/50 |
| `direct_instruction_override` | 100 | 100.0% (92.9–100.0%) 50/50 | 34.0% (22.4–47.8%) 17/50 |
| `indirect_content_injection` | 100 | 98.0% (89.5–99.6%) 49/50 | 82.0% (69.2–90.2%) 41/50 |
| `memory_context_poisoning` | 100 | 88.0% (76.2–94.4%) 44/50 | 100.0% (92.9–100.0%) 50/50 |
| `multi_agent_trust_spoofing` | 100 | 68.0% (54.2–79.2%) 34/50 | 82.0% (69.2–90.2%) 41/50 |
| `obfuscation_encoding` | 100 | 100.0% (92.9–100.0%) 50/50 | 100.0% (92.9–100.0%) 50/50 |
| `rag_context_poisoning` | 100 | 80.0% (67.0–88.8%) 40/50 | 74.0% (60.4–84.1%) 37/50 |
| `roleplay_jailbreak` | 100 | 68.0% (54.2–79.2%) 34/50 | 48.0% (34.8–61.5%) 24/50 |
| `sensitive_data_exfiltration` | 100 | 80.0% (67.0–88.8%) 40/50 | 96.0% (86.5–98.9%) 48/50 |
| `system_prompt_extraction` | 100 | 96.0% (86.5–98.9%) 48/50 | 100.0% (92.9–100.0%) 50/50 |
| `tool_action_abuse` | 100 | 60.0% (46.2–72.4%) 30/50 | 40.0% (27.6–53.8%) 20/50 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 0.9989 | 1.7% (0.9–3.0%) 10/600 | 0.0% (0.0–0.6%) 0/600 |
| at most 1.0% of benign inputs flagged | 0.9986 | 15.5% (12.8–18.6%) 93/600 | 1.0% (0.5–2.2%) 6/600 |
| at most 5.0% of benign inputs flagged | 0.9983 | 26.0% (22.7–29.7%) 156/600 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 111.1 ms, median 131.3 ms, 95th percentile 154.3 ms per input (1200 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
