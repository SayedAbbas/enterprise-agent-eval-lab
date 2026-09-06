from agent_eval_lab.adapters.mock import MockAgentAdapter
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
