# BenignTwin report: `regex-baseline`

- **Dataset:** `hf:3nesdeniz/agentic-prompt-injection-boundary-pairs` at `a5682e7573e1c7bc4b12e64d49c0dcd90ca776cf`, split `test`
- **Examples:** 240 (120 attacks, 120 benign)
- **Matched pairs:** 120
- **Detector:** `regex-baseline`
- **Decisions taken from the detector's own label:** 240
- **Coverage:** 240/240 rows
- **Run:** 2026-11-16T12:25:50Z, BenignTwin 1.0.0, 95% Wilson confidence intervals

## Summary

| Metric | Value |
| --- | ---: |
| Attacks caught (recall) | 5.0% (2.3–10.5%) 6/120 |
| Benign inputs flagged (false-positive rate) | 1.7% (0.5–5.9%) 2/120 |
| Pairs separated (pair accuracy) | 3.3% (1.3–8.3%) 4/120 |
| Precision | 75.0% (40.9–92.9%) 6/8 |
| Balanced accuracy | 0.517 |
| F1 | 0.094 |
| TP / FP / TN / FN | 6 / 2 / 118 / 114 |

## Matched pairs

Each attack has a benign twin with the same topic and vocabulary. A pair counts only when the attack is flagged and the twin is not.

| Outcome | Pairs |
| --- | ---: |
| Separated: attack flagged, twin cleared | 4 |
| Blocked both: reacts to the shared wording | 2 |
| Allowed both: attack missed | 114 |
| Inverted: twin flagged, attack missed | 0 |

### Pair accuracy by attack family

| Attack family | Pairs | Pair accuracy | Blocked both | Allowed both | Inverted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `approval_workflow_bypass` | 10 | 0.0% (0.0–27.8%) 0/10 | 0 | 10 | 0 |
| `authority_claim_bypass` | 10 | 0.0% (0.0–27.8%) 0/10 | 0 | 10 | 0 |
| `direct_instruction_override` | 10 | 20.0% (5.7–51.0%) 2/10 | 0 | 8 | 0 |
| `indirect_content_injection` | 10 | 0.0% (0.0–27.8%) 0/10 | 0 | 10 | 0 |
| `memory_context_poisoning` | 10 | 0.0% (0.0–27.8%) 0/10 | 0 | 10 | 0 |
| `multi_agent_trust_spoofing` | 10 | 0.0% (0.0–27.8%) 0/10 | 0 | 10 | 0 |
| `obfuscation_encoding` | 10 | 0.0% (0.0–27.8%) 0/10 | 2 | 8 | 0 |
| `rag_context_poisoning` | 10 | 0.0% (0.0–27.8%) 0/10 | 0 | 10 | 0 |
| `roleplay_jailbreak` | 10 | 0.0% (0.0–27.8%) 0/10 | 0 | 10 | 0 |
| `sensitive_data_exfiltration` | 10 | 0.0% (0.0–27.8%) 0/10 | 0 | 10 | 0 |
| `system_prompt_extraction` | 10 | 20.0% (5.7–51.0%) 2/10 | 0 | 8 | 0 |
| `tool_action_abuse` | 10 | 0.0% (0.0–27.8%) 0/10 | 0 | 10 | 0 |

## By attack family

| Attack family | Rows | Recall | False-positive rate |
| --- | ---: | ---: | ---: |
| `approval_workflow_bypass` | 20 | 0.0% (0.0–27.8%) 0/10 | 0.0% (0.0–27.8%) 0/10 |
| `authority_claim_bypass` | 20 | 0.0% (0.0–27.8%) 0/10 | 0.0% (0.0–27.8%) 0/10 |
| `direct_instruction_override` | 20 | 20.0% (5.7–51.0%) 2/10 | 0.0% (0.0–27.8%) 0/10 |
| `indirect_content_injection` | 20 | 0.0% (0.0–27.8%) 0/10 | 0.0% (0.0–27.8%) 0/10 |
| `memory_context_poisoning` | 20 | 0.0% (0.0–27.8%) 0/10 | 0.0% (0.0–27.8%) 0/10 |
| `multi_agent_trust_spoofing` | 20 | 0.0% (0.0–27.8%) 0/10 | 0.0% (0.0–27.8%) 0/10 |
| `obfuscation_encoding` | 20 | 20.0% (5.7–51.0%) 2/10 | 20.0% (5.7–51.0%) 2/10 |
| `rag_context_poisoning` | 20 | 0.0% (0.0–27.8%) 0/10 | 0.0% (0.0–27.8%) 0/10 |
| `roleplay_jailbreak` | 20 | 0.0% (0.0–27.8%) 0/10 | 0.0% (0.0–27.8%) 0/10 |
| `sensitive_data_exfiltration` | 20 | 0.0% (0.0–27.8%) 0/10 | 0.0% (0.0–27.8%) 0/10 |
| `system_prompt_extraction` | 20 | 20.0% (5.7–51.0%) 2/10 | 0.0% (0.0–27.8%) 0/10 |
| `tool_action_abuse` | 20 | 0.0% (0.0–27.8%) 0/10 | 0.0% (0.0–27.8%) 0/10 |

## Latency

Mean 0.0 ms, median 0.0 ms, 95th percentile 0.1 ms per input (240 measured).

## How to read this

These numbers describe one detector on one dataset. The ranges in brackets are Wilson confidence intervals at the level stated above: with few rows they are wide, and a rate of 0% still has an upper bound above zero. A good result here is evidence about these inputs, not proof that a system is secure against attacks it has not seen.
