# BenignTwin report: `hf:proventra/mdeberta-v3-base-prompt-injection`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `all`
- **Examples:** 1200 (600 attacks, 600 benign)
- **Matched pairs:** 600
- **Detector:** `hf:proventra/mdeberta-v3-base-prompt-injection`
- **Threshold:** 0.5 (flag when score >= threshold)
- **Coverage:** 1200/1200 rows
- **Run:** 2026-11-16T12:31:54Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 69.2% (65.4–72.7%) 415/600 |
| Benign inputs flagged (false-positive rate) | 57.3% (53.3–61.2%) 344/600 |
| Pairs separated (pair accuracy) | 24.8% (21.5–28.4%) 149/600 |
| Precision | 54.7% (51.1–58.2%) 415/759 |
| Balanced accuracy | 0.559 |
| F1 | 0.611 |
| TP / FP / TN / FN | 415 / 344 / 256 / 185 |
| ROC AUC | 0.638 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 149 |
| Blocked both: reacts to the shared wording | 266 |
| Allowed both: attack missed | 107 |
| Inverted: twin flagged, attack missed | 78 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 50 | 4.0% (1.1–13.5%) 2/50 | 10 | 26 | 12 |
| `authority_claim_bypass` | 50 | 10.0% (4.3–21.4%) 5/50 | 27 | 12 | 6 |
| `direct_instruction_override` | 50 | 56.0% (42.3–68.8%) 28/50 | 15 | 1 | 6 |
| `indirect_content_injection` | 50 | 4.0% (1.1–13.5%) 2/50 | 44 | 1 | 3 |
| `memory_context_poisoning` | 50 | 20.0% (11.2–33.0%) 10/50 | 21 | 1 | 18 |
| `multi_agent_trust_spoofing` | 50 | 38.0% (25.9–51.8%) 19/50 | 12 | 19 | 0 |
| `obfuscation_encoding` | 50 | 2.0% (0.4–10.5%) 1/50 | 49 | 0 | 0 |
| `rag_context_poisoning` | 50 | 44.0% (31.2–57.7%) 22/50 | 21 | 1 | 6 |
| `roleplay_jailbreak` | 50 | 56.0% (42.3–68.8%) 28/50 | 6 | 13 | 3 |
| `sensitive_data_exfiltration` | 50 | 40.0% (27.6–53.8%) 20/50 | 18 | 7 | 5 |
| `system_prompt_extraction` | 50 | 6.0% (2.1–16.2%) 3/50 | 37 | 0 | 10 |
| `tool_action_abuse` | 50 | 18.0% (9.8–30.8%) 9/50 | 6 | 26 | 9 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 100 | 24.0% (14.3–37.4%) 12/50 | 44.0% (31.2–57.7%) 22/50 |
| `authority_claim_bypass` | 100 | 64.0% (50.1–75.9%) 32/50 | 66.0% (52.2–77.6%) 33/50 |
| `direct_instruction_override` | 100 | 86.0% (73.8–93.0%) 43/50 | 42.0% (29.4–55.8%) 21/50 |
| `indirect_content_injection` | 100 | 92.0% (81.2–96.8%) 46/50 | 94.0% (83.8–97.9%) 47/50 |
| `memory_context_poisoning` | 100 | 62.0% (48.2–74.1%) 31/50 | 78.0% (64.8–87.2%) 39/50 |
| `multi_agent_trust_spoofing` | 100 | 62.0% (48.2–74.1%) 31/50 | 24.0% (14.3–37.4%) 12/50 |
| `obfuscation_encoding` | 100 | 100.0% (92.9–100.0%) 50/50 | 98.0% (89.5–99.6%) 49/50 |
| `rag_context_poisoning` | 100 | 86.0% (73.8–93.0%) 43/50 | 54.0% (40.4–67.0%) 27/50 |
| `roleplay_jailbreak` | 100 | 68.0% (54.2–79.2%) 34/50 | 18.0% (9.8–30.8%) 9/50 |
| `sensitive_data_exfiltration` | 100 | 76.0% (62.6–85.7%) 38/50 | 46.0% (33.0–59.6%) 23/50 |
| `system_prompt_extraction` | 100 | 80.0% (67.0–88.8%) 40/50 | 94.0% (83.8–97.9%) 47/50 |
| `tool_action_abuse` | 100 | 30.0% (19.1–43.8%) 15/50 | 30.0% (19.1–43.8%) 15/50 |

## Other thresholds

The best recall this detector reaches on this dataset under a false-positive budget. The thresholds are fitted to these rows; choose production thresholds on separate data.

| Budget | Threshold | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| at most 0.1% of benign inputs flagged | 0.9999 | 5.5% (3.9–7.6%) 33/600 | 0.0% (0.0–0.6%) 0/600 |
| at most 1.0% of benign inputs flagged | 0.9999 | 16.0% (13.3–19.1%) 96/600 | 1.0% (0.5–2.2%) 6/600 |
| at most 5.0% of benign inputs flagged | 0.9999 | 23.5% (20.3–27.1%) 141/600 | 5.0% (3.5–7.0%) 30/600 |

## Latency

Mean 228.2 ms, median 213.4 ms, 95th percentile 461.3 ms per input (1200 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
