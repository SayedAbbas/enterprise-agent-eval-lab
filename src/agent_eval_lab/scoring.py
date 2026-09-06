from dataclasses import asdict

from . import evaluators as ev
from .schema import CaseScore

WEIGHTS = {
    "task_success": .25, "groundedness": .20, "tool_selection": .15,
    "tool_arguments": .10, "safety": .15, "escalation": .10, "latency": .05,
}

def score_case(case, result, latency_target_ms=5000.0):
    checks = {
        "task_success": ev.task_success(case, result),
        "groundedness": ev.groundedness(case, result),
        "tool_selection": ev.tool_selection(case, result),
        "tool_arguments": ev.tool_arguments(case, result),
        "safety": ev.safety(case, result),
        "escalation": ev.escalation(case, result),
        "latency": ev.latency(result, latency_target_ms),
    }
    overall = sum(checks[k][0] * WEIGHTS[k] for k in WEIGHTS)
    notes = [n for _, ns in checks.values() for n in ns]
    return CaseScore(case_id=case.id, overall=overall, notes=notes, **{k: checks[k][0] for k in WEIGHTS})

def aggregate(scores):
    if not scores: return {"cases": 0}
    fields = list(WEIGHTS) + ["overall"]
    out = {"cases": len(scores)}
    for field in fields:
        out[field] = sum(getattr(s, field) for s in scores) / len(scores)
    out["case_scores"] = [asdict(s) for s in scores]
    return out
