from typing import Protocol

from ..schema import AgentResult, EvalCase


class AgentAdapter(Protocol):
    name: str
    model: str

    def run(self, case: EvalCase) -> AgentResult: ...
