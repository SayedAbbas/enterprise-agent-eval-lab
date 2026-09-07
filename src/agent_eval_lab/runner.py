from dataclasses import asdict

from .scoring import aggregate, score_case


def run_evaluation(cases, adapter, latency_target_ms=5000.0):
    reports, scores = [], []
    for case in cases:
        result = adapter.run(case)
        score = score_case(case, result, latency_target_ms)
        scores.append(score)
        reports.append({"case_id": case.id, "result": asdict(result), "score": asdict(score)})
    summary = aggregate(scores)
    summary.pop("case_scores", None)
    return {
        "provider": adapter.name,
        "model": getattr(adapter, "model", adapter.name),
        "summary": summary,
        "cases": reports,
    }
