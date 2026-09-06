# Architecture

The framework separates **agent execution** from **evaluation**.

- **Dataset:** task, synthetic evidence, tools, expected behavior.
- **Adapter:** normalizes provider behavior into a common result schema.
- **Evaluators:** score task success, grounding, tool selection, arguments, safety, escalation and latency independently.
- **Scoring:** produces an aggregate while keeping hard failures visible.
- **Reporting:** emits machine-readable JSON and human-readable Markdown.

## Design choice

The first release favors deterministic scoring over an LLM-as-judge. That makes CI reproducible and failure analysis transparent. Semantic judges can be added later for dimensions that cannot be reduced to hard contracts.
