from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolSpec:
    name: str
    description: str = ""
    required_args: list[str] = field(default_factory=list)

@dataclass
class ExpectedBehavior:
    required_tools: list[str] = field(default_factory=list)
    forbidden_tools: list[str] = field(default_factory=list)
    required_evidence_terms: list[str] = field(default_factory=list)
    should_escalate: bool = False
    expected_outcome_terms: list[str] = field(default_factory=list)

@dataclass
class EvalCase:
    id: str
    task: str
    evidence: dict[str, Any]
    available_tools: list[ToolSpec]
    expected: ExpectedBehavior

@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]

@dataclass
class AgentResult:
    answer: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    escalated: bool = False
    latency_ms: float = 0.0
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost_usd: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class CaseScore:
    case_id: str
    task_success: float
    groundedness: float
    tool_selection: float
    tool_arguments: float
    safety: float
    escalation: float
    latency: float
    overall: float
    notes: list[str] = field(default_factory=list)
