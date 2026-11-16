# BenignTwin report: `regex-baseline`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `all`
- **Examples:** 1200 (600 attacks, 600 benign)
- **Matched pairs:** 600
- **Detector:** `regex-baseline`
- **Decisions taken from the detector's own label:** 1200
- **Coverage:** 1200/1200 rows
- **Run:** 2026-11-16T12:25:51Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 5.2% (3.7–7.2%) 31/600 |
| Benign inputs flagged (false-positive rate) | 1.7% (0.9–3.0%) 10/600 |
| Pairs separated (pair accuracy) | 3.5% (2.3–5.3%) 21/600 |
| Precision | 75.6% (60.7–86.2%) 31/41 |
| Balanced accuracy | 0.517 |
| F1 | 0.097 |
| TP / FP / TN / FN | 31 / 10 / 590 / 569 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 21 |
| Blocked both: reacts to the shared wording | 10 |
| Allowed both: attack missed | 569 |
| Inverted: twin flagged, attack missed | 0 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 50 | 0.0% (0.0–7.1%) 0/50 | 0 | 50 | 0 |
| `authority_claim_bypass` | 50 | 0.0% (0.0–7.1%) 0/50 | 0 | 50 | 0 |
| `direct_instruction_override` | 50 | 20.0% (11.2–33.0%) 10/50 | 0 | 40 | 0 |
| `indirect_content_injection` | 50 | 0.0% (0.0–7.1%) 0/50 | 0 | 50 | 0 |
| `memory_context_poisoning` | 50 | 0.0% (0.0–7.1%) 0/50 | 0 | 50 | 0 |
| `multi_agent_trust_spoofing` | 50 | 0.0% (0.0–7.1%) 0/50 | 0 | 50 | 0 |
| `obfuscation_encoding` | 50 | 0.0% (0.0–7.1%) 0/50 | 10 | 40 | 0 |
| `rag_context_poisoning` | 50 | 0.0% (0.0–7.1%) 0/50 | 0 | 50 | 0 |
| `roleplay_jailbreak` | 50 | 0.0% (0.0–7.1%) 0/50 | 0 | 50 | 0 |
| `sensitive_data_exfiltration` | 50 | 2.0% (0.4–10.5%) 1/50 | 0 | 49 | 0 |
| `system_prompt_extraction` | 50 | 20.0% (11.2–33.0%) 10/50 | 0 | 40 | 0 |
| `tool_action_abuse` | 50 | 0.0% (0.0–7.1%) 0/50 | 0 | 50 | 0 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 100 | 0.0% (0.0–7.1%) 0/50 | 0.0% (0.0–7.1%) 0/50 |
| `authority_claim_bypass` | 100 | 0.0% (0.0–7.1%) 0/50 | 0.0% (0.0–7.1%) 0/50 |
| `direct_instruction_override` | 100 | 20.0% (11.2–33.0%) 10/50 | 0.0% (0.0–7.1%) 0/50 |
| `indirect_content_injection` | 100 | 0.0% (0.0–7.1%) 0/50 | 0.0% (0.0–7.1%) 0/50 |
| `memory_context_poisoning` | 100 | 0.0% (0.0–7.1%) 0/50 | 0.0% (0.0–7.1%) 0/50 |
| `multi_agent_trust_spoofing` | 100 | 0.0% (0.0–7.1%) 0/50 | 0.0% (0.0–7.1%) 0/50 |
| `obfuscation_encoding` | 100 | 20.0% (11.2–33.0%) 10/50 | 20.0% (11.2–33.0%) 10/50 |
| `rag_context_poisoning` | 100 | 0.0% (0.0–7.1%) 0/50 | 0.0% (0.0–7.1%) 0/50 |
| `roleplay_jailbreak` | 100 | 0.0% (0.0–7.1%) 0/50 | 0.0% (0.0–7.1%) 0/50 |
| `sensitive_data_exfiltration` | 100 | 2.0% (0.4–10.5%) 1/50 | 0.0% (0.0–7.1%) 0/50 |
| `system_prompt_extraction` | 100 | 20.0% (11.2–33.0%) 10/50 | 0.0% (0.0–7.1%) 0/50 |
| `tool_action_abuse` | 100 | 0.0% (0.0–7.1%) 0/50 | 0.0% (0.0–7.1%) 0/50 |

## Latency

Mean 0.0 ms, median 0.0 ms, 95th percentile 0.1 ms per input (1200 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
