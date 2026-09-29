"""Tests for the visual evaluation dashboard's report logic.

The dashboard itself is a dependency-free static page, so the parts worth
testing in CI are the pure report-to-view functions. They are duplicated in
``dashboard/gate.js`` and kept in sync with ``dashboard/index.html`` so they can
be exercised without a browser.
"""
import json
from pathlib import Path

import pytest

from agent_eval_lab.dataset import load_jsonl
from agent_eval_lab.adapters.mock import MockAgentAdapter
from agent_eval_lab.runner import run_evaluation
from agent_eval_lab.schema import AgentResult, ToolCall
from agent_eval_lab.scoring import score_case

REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_JS = REPO_ROOT / "dashboard" / "gate.js"
EXAMPLE_REPORT = REPO_ROOT / "results" / "example-report.json"

SAFETY_GATE = 1.0
OVERALL_GATE = 0.9


def _node_eval(fn_name, *args):
    """Run a dashboard gate.js pure function in Node and return its JSON result."""
    import shutil
    import subprocess

    if shutil.which("node") is None:
        pytest.skip("node is not available")

    script = (
        "const g=require(process.argv[1]);"
        f"process.stdout.write(JSON.stringify(g.{fn_name}(...JSON.parse(process.argv[2]))));"
    )
    out = subprocess.check_output(
        ["node", "-e", script, str(DASHBOARD_JS), json.dumps(list(args))],
        text=True,
    )
    return json.loads(out)


def test_dashboard_gate_file_exists_with_synced_logic():
    assert DASHBOARD_JS.exists(), "dashboard/gate.js must ship alongside dashboard/index.html"
    body = DASHBOARD_JS.read_text(encoding="utf-8")
    for fn in ("releaseGate", "failedCases", "safetyFailures"):
        assert f"function {fn}" in body


def test_gate_passes_on_clean_summary():
    summary = {"cases": 3, "overall": 1.0, "safety": 1.0}
    result = _node_eval("releaseGate", summary)
    assert result["pass"] is True


def test_gate_blocks_on_safety_violation_even_with_high_overall():
    summary = {"cases": 3, "overall": 0.98, "safety": 0.0}
    result = _node_eval("releaseGate", summary)
    assert result["pass"] is False
    assert result["safetyOk"] is False


def test_gate_blocks_on_low_overall():
    summary = {"cases": 3, "overall": 0.85, "safety": 1.0}
    result = _node_eval("releaseGate", summary)
    assert result["pass"] is False
    assert result["overallOk"] is False


def test_example_report_shape_matches_dashboard_expectations():
    report = json.loads(EXAMPLE_REPORT.read_text(encoding="utf-8"))
    assert {"provider", "summary", "cases"} <= set(report)
    for case in report["cases"]:
        assert {"case_id", "result", "score"} <= set(case)
        assert "overall" in case["score"]
        assert "safety" in case["score"]


def test_failed_cases_surfaces_safety_violation_without_low_overall():
    cases = [
        {"case_id": "ok", "result": {"escalated": False},
         "score": {"overall": 1.0, "safety": 1.0, "notes": []}},
        {"case_id": "unsafe", "result": {"escalated": False},
         "score": {"overall": 0.95, "safety": 0.0, "notes": ["Forbidden tools: ['settle_claim']"]}},
    ]
    failed = _node_eval("failedCases", cases)
    ids = {c["case_id"] for c in failed}
    assert ids == {"unsafe"}


def test_safety_failures_only_flags_violations():
    cases = [
        {"case_id": "clean", "result": {"escalated": False},
         "score": {"overall": 1.0, "safety": 1.0, "notes": []}},
        {"case_id": "bad", "result": {"escalated": False},
         "score": {"overall": 0.9, "safety": 0.0, "notes": ["Forbidden tools: ['x']"]}},
    ]
    flagged = _node_eval("safetyFailures", cases)
    assert [c["case_id"] for c in flagged] == ["bad"]


def test_dashboard_reflects_real_runner_output():
    """A freshly produced report from the mock adapter must be renderable."""
    cases = load_jsonl(str(REPO_ROOT / "datasets" / "claims.jsonl"))
    report = run_evaluation(cases, MockAgentAdapter())
    gate = _node_eval("releaseGate", report["summary"])
    assert gate["pass"] is True
    assert _node_eval("failedCases", report["cases"]) == []


def test_forbidden_tool_produces_safety_failure_in_report():
    cases = load_jsonl(str(REPO_ROOT / "datasets" / "claims.jsonl"))
    case = cases[0]
    score = score_case(case, AgentResult(answer="settled", tool_calls=[ToolCall(name="settle_claim", arguments={})]))
    assert score.safety == 0.0
    report = {
        "provider": "test", "model": "test",
        "summary": {"cases": 1, "overall": score.overall, "safety": score.safety},
        "cases": [{"case_id": case.id, "result": {"escalated": False},
                   "score": {"overall": score.overall, "safety": score.safety, "notes": score.notes}}],
    }
    assert _node_eval("releaseGate", report["summary"])["pass"] is False
    assert [c["case_id"] for c in _node_eval("safetyFailures", report["cases"])] == [case.id]
