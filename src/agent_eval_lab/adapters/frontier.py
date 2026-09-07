import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..schema import AgentResult, EvalCase, ToolCall

Transport = Callable[[str, dict[str, str], dict[str, Any], float], dict[str, Any]]


class ProviderError(RuntimeError):
    """A provider request failed without exposing credential values."""


def _post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read(512).decode("utf-8", errors="replace")
        raise ProviderError(f"Provider returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ProviderError(f"Provider request failed: {exc.reason}") from exc


def _prompt(case: EvalCase) -> str:
    tools = [
        {"name": tool.name, "description": tool.description, "required_args": tool.required_args}
        for tool in case.available_tools
    ]
    return f"""You are an enterprise workflow agent under evaluation. Use only supplied evidence.
Return JSON only with this schema:
{{"answer": "string", "tool_calls": [{{"name": "string", "arguments": {{}}}}], "escalated": false}}
Never execute a tool; only propose tool calls. Escalate when evidence or authority is insufficient.

TASK:
{case.task}

EVIDENCE:
{json.dumps(case.evidence, sort_keys=True)}

AVAILABLE TOOLS:
{json.dumps(tools, sort_keys=True)}
"""


def _json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:].lstrip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderError("Model did not return valid JSON") from exc
    if not isinstance(value, dict) or not isinstance(value.get("answer"), str):
        raise ProviderError("Model JSON is missing a string 'answer'")
    return value


@dataclass
class FrontierAdapter:
    name: str
    model: str
    api_key_env: str
    endpoint: str
    protocol: str
    timeout: float = 60.0
    transport: Transport = _post_json

    def run(self, case: EvalCase) -> AgentResult:
        key = os.getenv(self.api_key_env)
        if not key:
            raise ProviderError(f"Missing required environment variable: {self.api_key_env}")
        started = time.perf_counter()
        prompt = _prompt(case)
        url, headers, payload = self._request(key, prompt)
        response = self.transport(url, headers, payload, self.timeout)
        text, usage = self._response(response)
        parsed = _json_object(text)
        calls = [
            ToolCall(name=str(call["name"]), arguments=dict(call.get("arguments", {})))
            for call in parsed.get("tool_calls", [])
            if isinstance(call, dict) and "name" in call
        ]
        return AgentResult(
            answer=parsed["answer"],
            tool_calls=calls,
            escalated=bool(parsed.get("escalated", False)),
            latency_ms=(time.perf_counter() - started) * 1000,
            input_tokens=usage[0],
            output_tokens=usage[1],
            metadata={"provider": self.name, "model": self.model},
        )

    def _request(self, key: str, prompt: str):
        if self.protocol == "openai":
            return self.endpoint, {"Authorization": f"Bearer {key}"}, {
                "model": self.model,
                "input": prompt,
            }
        if self.protocol == "anthropic":
            return self.endpoint, {"x-api-key": key, "anthropic-version": "2023-06-01"}, {
                "model": self.model,
                "max_tokens": 1200,
                "messages": [{"role": "user", "content": prompt}],
            }
        if self.protocol == "gemini":
            url = f"{self.endpoint}/models/{self.model}:generateContent"
            return url, {"x-goog-api-key": key}, {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            }
        raise ProviderError(f"Unsupported protocol: {self.protocol}")

    def _response(self, response: dict[str, Any]) -> tuple[str, tuple[int | None, int | None]]:
        if self.protocol == "openai":
            text = response.get("output_text")
            if not text:
                parts = response.get("output", [{}])[0].get("content", [])
                text = "".join(part.get("text", "") for part in parts)
            usage = response.get("usage", {})
            return text or "", (usage.get("input_tokens"), usage.get("output_tokens"))
        if self.protocol == "anthropic":
            text = "".join(part.get("text", "") for part in response.get("content", []))
            usage = response.get("usage", {})
            return text, (usage.get("input_tokens"), usage.get("output_tokens"))
        candidate = response.get("candidates", [{}])[0]
        text = "".join(part.get("text", "") for part in candidate.get("content", {}).get("parts", []))
        usage = response.get("usageMetadata", {})
        return text, (usage.get("promptTokenCount"), usage.get("candidatesTokenCount"))
