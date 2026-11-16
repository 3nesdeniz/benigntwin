# Questions and answers

## How do I measure the false-positive rate of a prompt-injection detector?

Run the detector on benign inputs and count how many it flags. The number depends on which benign inputs you use, so use two kinds: ordinary requests from your application, and legitimate requests that resemble attacks (benign twins). InjectBench reports the rate with a confidence interval and the counts behind it:

```bash
injectbench evaluate --dataset hf:3nesdeniz/agentic-prompt-injection-boundary-pairs \
  --detector hf:protectai/deberta-v3-base-prompt-injection-v2
```

## What is a benign twin?

A legitimate input written to match one attack: the same topic, role, tools and trigger words, with only the intent changed. A detector that flags the twin is reacting to the wording, not to the attack.

## What is pair accuracy?

The share of matched pairs in which the detector flags the attack and does not flag its benign twin. See [metrics](metrics.md#matched-pairs).

## Why is high recall not enough?

Because flagging everything gives 100 % recall. A detector is useful only if it also lets legitimate requests through. Always read recall next to the false-positive rate, and prefer pair accuracy when the data has pairs.

## Does it work for languages other than English?

Yes. Results are broken down by language, and when the same items exist in several languages they are compared item by item ([language parity](metrics.md#language-parity)). Rows without a language tag are reported as `unknown`; they are never assumed to be English.

## Which detectors can I evaluate?

Hugging Face classification models, any Python function, any HTTP endpoint that returns a label or a score, and predictions computed elsewhere. See [detectors](detectors.md).

## Can I evaluate a commercial guardrail API?

Yes, through the HTTP adapter or, if the API cannot be reached from your machine, through a predictions file. Check the provider's terms before you publish results.

## Does my data leave my machine?

Only if you choose a detector that sends it: an HTTP endpoint receives the input text. Model and Python detectors run locally. Reports never contain input text.

## Does the detector see the labels?

No. A detector receives the text (and the id, if you ask for it) and nothing else.

## How many examples do I need?

Enough for the interval to be narrower than the difference you care about. As a guide for the false-positive rate: with 0 errors observed, 100 benign inputs bound the rate below about 3.7 %, 300 below about 1.3 %, and 1,000 below about 0.4 % (95 % Wilson intervals). To show a rate below 1 % you need several hundred benign inputs.

## Which threshold should I use?

The one you run in production. The default is `0.5`. The report also shows the best recall the detector reaches under false-positive budgets of 0.1 %, 1 % and 5 %; those thresholds are fitted to the test data, so choose production thresholds on separate data.

## Why is a rate shown as `n/a`?

Its denominator is zero: for example, the false-positive rate of a dataset without benign rows. InjectBench does not print `0` for something it could not measure.

## My model's labels are `LABEL_0` and `LABEL_1`. Which one is the attack?

InjectBench assumes `LABEL_1` and says so in the report. If your model is the other way round, pass `--positive-label LABEL_0`.

## Why does it refuse to load some models?

Models that need custom code from their repository are not loaded (`trust_remote_code` stays off), and by default only `safetensors` weights are loaded, because pickle-based weights can execute code. `--hf-allow-pickle` lifts the second restriction for models you trust.

## Is a good score proof that my application is safe?

No. It is evidence about one detector on one dataset. Attackers adapt, and a detector is one layer among several. See [what this method does not cover](methodology.md#what-this-method-does-not-cover).

## How is this different from garak, promptfoo, PyRIT or PINT?

garak, promptfoo and PyRIT test what a model or an application does under attack. InjectBench tests the detector in front of it. PINT also benchmarks detectors and includes hard negatives, but its data is not public and it reports one balanced-accuracy score. See [related work](related-work.md).

## How do I cite it?

Use the "Cite this repository" button on GitHub, which reads `CITATION.cff`.
