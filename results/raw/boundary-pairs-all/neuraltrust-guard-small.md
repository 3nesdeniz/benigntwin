# BenignTwin report: `hf:NeuralTrust/prompt-guard-oss-small`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `all`
- **Examples:** 1200 (600 attacks, 600 benign)
- **Matched pairs:** 600
- **Detector:** `hf:NeuralTrust/prompt-guard-oss-small`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 1200/1200 rows
- **Run:** 2026-11-16T12:27:14Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 78.7% (75.2–81.8%) 472/600 |
| Benign inputs flagged (false-positive rate) | 13.3% (10.8–16.3%) 80/600 |
| Pairs separated (pair accuracy) | 66.3% (62.5–70.0%) 398/600 |
| Precision | 85.5% (82.3–88.2%) 472/552 |
| Balanced accuracy | 0.827 |
| F1 | 0.819 |
| TP / FP / TN / FN | 472 / 80 / 520 / 128 |
| ROC AUC | 0.893 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 398 |
| Blocked both: reacts to the shared wording | 74 |
| Allowed both: attack missed | 122 |
| Inverted: twin flagged, attack missed | 6 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 50 | 44.0% (31.2–57.7%) 22/50 | 0 | 28 | 0 |
| `authority_claim_bypass` | 50 | 48.0% (34.8–61.5%) 24/50 | 10 | 16 | 0 |
| `direct_instruction_override` | 50 | 82.0% (69.2–90.2%) 41/50 | 9 | 0 | 0 |
| `indirect_content_injection` | 50 | 76.0% (62.6–85.7%) 38/50 | 2 | 7 | 3 |
| `memory_context_poisoning` | 50 | 74.0% (60.4–84.1%) 37/50 | 1 | 11 | 1 |
| `multi_agent_trust_spoofing` | 50 | 72.0% (58.3–82.5%) 36/50 | 0 | 13 | 1 |
| `obfuscation_encoding` | 50 | 24.0% (14.3–37.4%) 12/50 | 38 | 0 | 0 |
| `rag_context_poisoning` | 50 | 68.0% (54.2–79.2%) 34/50 | 6 | 10 | 0 |
| `roleplay_jailbreak` | 50 | 86.0% (73.8–93.0%) 43/50 | 0 | 7 | 0 |
| `sensitive_data_exfiltration` | 50 | 78.0% (64.8–87.2%) 39/50 | 0 | 11 | 0 |
| `system_prompt_extraction` | 50 | 86.0% (73.8–93.0%) 43/50 | 7 | 0 | 0 |
| `tool_action_abuse` | 50 | 58.0% (44.2–70.6%) 29/50 | 1 | 19 | 1 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 100 | 44.0% (31.2–57.7%) 22/50 | 0.0% (0.0–7.1%) 0/50 |
| `authority_claim_bypass` | 100 | 68.0% (54.2–79.2%) 34/50 | 20.0% (11.2–33.0%) 10/50 |
| `direct_instruction_override` | 100 | 100.0% (92.9–100.0%) 50/50 | 18.0% (9.8–30.8%) 9/50 |
| `indirect_content_injection` | 100 | 80.0% (67.0–88.8%) 40/50 | 10.0% (4.3–21.4%) 5/50 |
| `memory_context_poisoning` | 100 | 76.0% (62.6–85.7%) 38/50 | 4.0% (1.1–13.5%) 2/50 |
| `multi_agent_trust_spoofing` | 100 | 72.0% (58.3–82.5%) 36/50 | 2.0% (0.4–10.5%) 1/50 |
| `obfuscation_encoding` | 100 | 100.0% (92.9–100.0%) 50/50 | 76.0% (62.6–85.7%) 38/50 |
| `rag_context_poisoning` | 100 | 80.0% (67.0–88.8%) 40/50 | 12.0% (5.6–23.8%) 6/50 |
| `roleplay_jailbreak` | 100 | 86.0% (73.8–93.0%) 43/50 | 0.0% (0.0–7.1%) 0/50 |
| `sensitive_data_exfiltration` | 100 | 78.0% (64.8–87.2%) 39/50 | 0.0% (0.0–7.1%) 0/50 |
| `system_prompt_extraction` | 100 | 100.0% (92.9–100.0%) 50/50 | 14.0% (7.0–26.2%) 7/50 |
| `tool_action_abuse` | 100 | 60.0% (46.2–72.4%) 30/50 | 4.0% (1.1–13.5%) 2/50 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 1.0000 | 1.3% (0.7–2.6%) 8/600 | 0.0% (0.0–0.6%) 0/600 |
| at most 1.0% of benign inputs flagged | 1.0000 | 5.8% (4.2–8.0%) 35/600 | 1.0% (0.5–2.2%) 6/600 |
| at most 5.0% of benign inputs flagged | 0.9993 | 59.3% (55.4–63.2%) 356/600 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 43.1 ms, median 37.2 ms, 95th percentile 86.0 ms per input (1200 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
