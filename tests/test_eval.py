import json

import pytest

from agent_eval_lab.adapters.frontier import FrontierAdapter, ProviderError
from agent_eval_lab.adapters.mock import MockAgentAdapter
from agent_eval_lab.adapters.registry import build_adapter
from agent_eval_lab.dataset import load_jsonl
from agent_eval_lab.evaluators import safety
from agent_eval_lab.schema import AgentResult, ToolCall
from agent_eval_lab.scoring import score_case


def test_dataset_and_mock_score():
    cases = load_jsonl("datasets/claims.jsonl")
    assert len(cases) == 3
    score = score_case(cases[0], MockAgentAdapter().run(cases[0]))
    assert score.overall == 1.0

def test_forbidden_tool_is_hard_failure():
    case = load_jsonl("datasets/claims.jsonl")[0]
    result = AgentResult(answer="settled", tool_calls=[ToolCall(name="settle_claim", arguments={})])
    score, notes = safety(case, result)
    assert score == 0.0
    assert notes


def test_openai_compatible_adapter(monkeypatch):
    monkeypatch.setenv("TEST_API_KEY", "not-a-real-key")
    captured = {}

    def transport(url, headers, payload, timeout):
        captured.update(url=url, headers=headers, payload=payload, timeout=timeout)
        result = {
            "answer": "Recommendation: deduction. Evidence: INR 5,000/day",
            "tool_calls": [{"name": "calculate_deduction", "arguments": {"amount": 4000}}],
            "escalated": False,
        }
        return {"output_text": json.dumps(result), "usage": {"input_tokens": 10, "output_tokens": 5}}

    adapter = FrontierAdapter(
        "test", "frontier-test", "TEST_API_KEY", "https://example.test/responses", "openai", transport=transport
    )
    case = load_jsonl("datasets/claims.jsonl")[0]
    result = adapter.run(case)
    assert result.tool_calls[0].name == "calculate_deduction"
    assert result.input_tokens == 10
    assert captured["payload"]["model"] == "frontier-test"
    assert captured["headers"]["Authorization"].startswith("Bearer ")


def test_missing_key_names_variable_not_secret(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="OPENAI_API_KEY"):
        build_adapter("openai").run(load_jsonl("datasets/claims.jsonl")[0])
