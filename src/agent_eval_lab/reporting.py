import json
from pathlib import Path


def write_json(report, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")

def to_markdown(report):
    s = report["summary"]
    lines = ["# Enterprise Agent Evaluation Report", "", f"**Provider:** `{report['provider']}`  ", f"**Cases:** {s['cases']}  ", f"**Overall:** {s['overall']:.3f}", "", "| Metric | Score |", "|---|---:|"]
    for key in ["task_success","groundedness","tool_selection","tool_arguments","safety","escalation","latency"]:
        lines.append(f"| {key.replace('_',' ').title()} | {s[key]:.3f} |")
    lines += ["", "## Cases", ""]
    for c in report["cases"]:
        lines += [f"### {c['case_id']}", "", f"- Overall: **{c['score']['overall']:.3f}**", f"- Answer: {c['result']['answer']}", f"- Escalated: `{c['result']['escalated']}`", f"- Latency: `{c['result']['latency_ms']:.2f} ms`", ""]
    return "\n".join(lines)

def write_markdown(report, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_markdown(report), encoding="utf-8")
