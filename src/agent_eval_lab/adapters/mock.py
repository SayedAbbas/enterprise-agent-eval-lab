import time

from ..schema import AgentResult, EvalCase, ToolCall


class MockAgentAdapter:
    """Deterministic adapter for local demos and CI."""
    name = "mock"

    def run(self, case: EvalCase) -> AgentResult:
        started = time.perf_counter()
        calls = []
        for tool_name in case.expected.required_tools:
            spec = next((t for t in case.available_tools if t.name == tool_name), None)
            if spec:
                args = {arg: self._arg(arg, case) for arg in spec.required_args}
                calls.append(ToolCall(name=tool_name, arguments=args))
        evidence = " ".join(case.expected.required_evidence_terms)
        outcome = " ".join(case.expected.expected_outcome_terms)
        prefix = "ESCALATE. " if case.expected.should_escalate else "Recommendation: "
        answer = f"{prefix}{outcome}. Evidence: {evidence}".strip()
        return AgentResult(
            answer=answer,
            tool_calls=calls,
            escalated=case.expected.should_escalate,
            latency_ms=(time.perf_counter() - started) * 1000,
            metadata={"deterministic": True},
        )

    @staticmethod
    def _arg(arg: str, case: EvalCase):
        lower = arg.lower()
        if "amount" in lower:
            return case.evidence.get("expected_deduction", 1000)
        if "account" in lower:
            return case.evidence.get("account_id", "SYNTHETIC-001")
        if "case" in lower:
            return case.id
        if "reason" in lower:
            return case.expected.expected_outcome_terms[0] if case.expected.expected_outcome_terms else "policy"
        return "synthetic-value"
