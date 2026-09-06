# Evaluation Methodology

The baseline evaluates seven production dimensions: task success, groundedness, tool selection, required tool arguments, forbidden-action safety, expected escalation, and latency.

## Why hard checks first?

An LLM judge can be useful for nuanced semantic quality, but some enterprise requirements are contracts rather than opinions. Whether an agent called a forbidden action or omitted a required argument should be evaluated deterministically.

## Recommended production extension

For serious model comparisons add larger stratified datasets, repeated runs, variance/confidence intervals, calibrated semantic judges, human review, adversarial cases, regression baselines, provider/model/version metadata, and normalized cost per successful task.
