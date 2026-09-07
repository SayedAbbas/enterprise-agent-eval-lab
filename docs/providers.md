# Provider matrix

Phase 2 ships direct, dependency-free HTTPS adapters. Credentials are read only from environment variables and are never written to reports.

| Provider | Default model | Credential variable | Protocol |
|---|---|---|---|
| OpenAI | `gpt-5` | `OPENAI_API_KEY` | Responses API |
| Anthropic | `claude-sonnet-4-5` | `ANTHROPIC_API_KEY` | Messages API |
| Google | `gemini-2.5-pro` | `GEMINI_API_KEY` | Gemini GenerateContent |
| xAI | `grok-4` | `XAI_API_KEY` | Responses-compatible API |
| Local/CI | `deterministic-reference` | none | in-process mock |

Model IDs evolve. Use `--model` to select any model supported by the chosen provider without changing source code.

## Security contract

- Put keys in environment variables, never command arguments or configuration files.
- `.env` is ignored, but this project does not parse it automatically.
- Errors identify a missing variable by name but never print its value.
- Reports record provider and model IDs, token counts, scores, and timing—not credentials or request headers.

## Fair-comparison guidance

Pin model IDs when providers offer versioned identifiers, use the same dataset and latency target, repeat runs, and retain raw JSON reports. Treat this small synthetic suite as an engineering demonstration rather than a universal model ranking.
