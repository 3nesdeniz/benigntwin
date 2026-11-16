# Related work

InjectBench is one of several ways to evaluate prompt-injection detectors. This page says what the others measure, so you can pick the right tool or combine them. Facts were checked against each project's own pages on 16 November 2026; corrections are welcome as issues.

## Benchmarks for detectors and guardrails

| Project | What it measures | Benign side | Languages | Data |
| --- | --- | --- | --- | --- |
| [PINT](https://github.com/lakeraai/pint-benchmark) (Lakera) | one balanced-accuracy score for injection detectors on 4,314 inputs | includes a `hard_negatives` category | 3,016 English and 1,298 non-English inputs | a blend of public and proprietary data, not published; repository archived |
| [NotInject](https://huggingface.co/datasets/leolee99/NotInject) with [PIGuard / InjecGuard](https://github.com/leolee99/PIGuard) (ACL 2025) | over-defense: 339 benign prompts that contain trigger words | benign only, no matched attacks | English | public, MIT |
| [GuardBench](https://github.com/AmenRa/GuardBench) (EMNLP 2024) | content-safety guardrail models on 40 datasets | F1 and recall by default; false-positive rate selectable | mostly English | public sources, EUPL-1.2 |
| [Horizon-Labs evaluation suite](https://huggingface.co/datasets/Horizon-Labs/prompt-injection-eval-suite) | nine open detectors on twelve public sets at threshold 0.5 | F1 with benign false-positive rate, per row | synthetic sets in 30 languages | public, mixed licences |
| [PIDS-Bench](https://arxiv.org/abs/2609.15017) | seven detectors: detection and benign false-positive rate at fixed thresholds, obfuscation, distribution shift | 1,472 hard-benign prompts | English | public |
| [Benign-instruction benchmark](https://github.com/lzwhehe/benign-instruction-bench) ("Passing the Test You Trained On", arXiv 2610.03448) | detectors on benign and injected tool outputs of agent benchmarks | false-positive rate on benign tool outputs | English | public, MIT |
| [injection-bench](https://github.com/ashishdhillon/injection-bench) | time-split harness: AUC and recall at fixed false-positive rates with bootstrap intervals | false-positive-anchored operating points | English | public, MIT |
| [Open-Prompt-Injection](https://github.com/liu00222/Open-Prompt-Injection) (USENIX Security 2024) | attacks and defenses across tasks and models | false-positive and false-negative rates for its own detection defenses | English | public, MIT |

Several of these report a false-positive rate, and some use hard negatives. What InjectBench adds is the **pair as the unit of scoring**: each attack is evaluated together with its own benign twin, and the result says in how many pairs the detector flagged the attack and cleared the twin. We did not find another open tool for text detectors that reports this joint outcome. If you know one, please open an issue so this page can be corrected.

The other differences are practical: confidence intervals with the counts on every rate, a comparison of languages on matched items, exit codes for CI, and adapters for models, functions, endpoints and offline predictions in one command.

## Over-refusal test suites for language models

[XSTest](https://github.com/paul-rottger/xstest) (NAACL 2024) pairs 250 safe prompts that look unsafe with 200 unsafe contrast prompts, and [OR-Bench](https://huggingface.co/datasets/bench-llm/or-bench) (ICML 2025) collects prompts that models wrongly refuse. Both measure whether a *language model* refuses a safe request. InjectBench applies the same idea, a benign input that resembles a harmful one, to *detectors*, and scores each benign input against its matched attack.

## Tools that test models and agents, not detectors

| Project | Subject of the test |
| --- | --- |
| [garak](https://github.com/NVIDIA/garak) | probes a target model for vulnerabilities; its detectors judge model outputs |
| [promptfoo](https://www.promptfoo.dev/) | evaluations and red teaming of applications; its guardrail guide defines the false-positive rate on benign cases you supply |
| [PyRIT](https://github.com/microsoft/PyRIT) | red teaming of generative AI systems |
| [AgentDojo](https://github.com/ethz-spylab/agentdojo) | agents under attack: utility, utility under attack, attack success |
| [BIPIA](https://github.com/microsoft/BIPIA), [InjecAgent](https://github.com/uiuc-kang-lab/InjecAgent) | indirect prompt injection against models and tool-using agents |
| [CyberSecEval](https://github.com/meta-llama/PurpleLlama) | susceptibility of models to prompt injection, including a multilingual set |

These answer a different question: does the model or the agent do what the attack asks? InjectBench answers: does the detector in front of it tell an attack from a legitimate request? The two are complementary. `injectbench export-promptfoo` writes a dataset as a Promptfoo test suite for teams that already run Promptfoo.

## Where the datasets in the results are used elsewhere

The [boundary-pairs dataset](https://huggingface.co/datasets/3nesdeniz/agentic-prompt-injection-boundary-pairs) used in the [results](../results/README.md) is also part of the Horizon-Labs evaluation suite (`boundary_pairs_test`), where it is scored per row. The model card of `Horizon-Labs/prompt-injection-guard-base` lists the train split of that dataset among its training data, which is why that model is marked in the results on all splits.

## A note on the name

"InjectBench" is also the title of a 2024 master's thesis on indirect prompt injection ([Kong, Virginia Tech](https://vtechworks.lib.vt.edu/items/c8a6b2f2-9b51-4e02-9778-aa4840fa30d8)), and the unrelated PyPI package `injection-bench` installs a module called `injectbench`. This project is not connected to either.
