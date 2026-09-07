from .frontier import FrontierAdapter
from .mock import MockAgentAdapter

PROVIDERS = {
    "openai": ("OPENAI_API_KEY", "https://api.openai.com/v1/responses", "openai", "gpt-5"),
    "anthropic": ("ANTHROPIC_API_KEY", "https://api.anthropic.com/v1/messages", "anthropic", "claude-sonnet-4-5"),
    "gemini": ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta", "gemini", "gemini-2.5-pro"),
    "grok": ("XAI_API_KEY", "https://api.x.ai/v1/responses", "openai", "grok-4"),
}


def build_adapter(provider: str, model: str | None = None, timeout: float = 60.0):
    if provider == "mock":
        return MockAgentAdapter()
    try:
        env, endpoint, protocol, default_model = PROVIDERS[provider]
    except KeyError as exc:
        raise ValueError(f"Unknown provider: {provider}") from exc
    return FrontierAdapter(provider, model or default_model, env, endpoint, protocol, timeout)
