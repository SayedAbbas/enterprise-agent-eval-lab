import json
from html import escape
from pathlib import Path


def write_json(report, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def to_markdown(report):
    s = report["summary"]
    lines = [
        "# Frontier Enterprise Agent Evaluation Report",
        "",
        f"**Provider:** `{report['provider']}`  ",
        f"**Model:** `{report.get('model', 'unknown')}`  ",
        f"**Cases:** {s['cases']}  ",
        f"**Overall:** {s['overall']:.3f}",
        "",
        "| Metric | Score |",
        "|---|---:|",
    ]

    for key in [
        "task_success",
        "groundedness",
        "tool_selection",
        "tool_arguments",
        "safety",
        "escalation",
        "latency",
    ]:
        lines.append(
            f"| {key.replace('_', ' ').title()} | {s[key]:.3f} |"
        )

    lines += ["", "## Cases", ""]

    for c in report["cases"]:
        lines += [
            f"### {c['case_id']}",
            "",
            f"- Overall: **{c['score']['overall']:.3f}**",
            f"- Answer: {c['result']['answer']}",
            f"- Escalated: `{c['result']['escalated']}`",
            f"- Latency: `{c['result']['latency_ms']:.2f} ms`",
            "",
        ]

    return "\n".join(lines)


def write_markdown(report, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_markdown(report), encoding="utf-8")


def comparison_markdown(reports):
    lines = [
        "# Frontier Model Leaderboard",
        "",
        "| Rank | Provider | Model | Overall | Safety | Groundedness | Latency |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]

    ordered = sorted(
        reports,
        key=lambda report: report["summary"]["overall"],
        reverse=True,
    )

    for rank, report in enumerate(ordered, start=1):
        score = report["summary"]
        lines.append(
            f"| {rank} | {report['provider']} | `{report['model']}` | "
            f"{score['overall']:.3f} | {score['safety']:.3f} | "
            f"{score['groundedness']:.3f} | {score['latency']:.3f} |"
        )

    return "\n".join(lines) + "\n"


def to_html(report):
    summary = report["summary"]

    metric_rows = []

    for key in [
        "task_success",
        "groundedness",
        "tool_selection",
        "tool_arguments",
        "safety",
        "escalation",
        "latency",
    ]:
        label = key.replace("_", " ").title()
        metric_rows.append(
            f"<tr><td>{escape(label)}</td><td>{summary[key]:.3f}</td></tr>"
        )

    failed_cases = [
        case
        for case in report["cases"]
        if case["score"]["overall"] < 1.0
    ]

    failed_rows = []

    for case in failed_cases:
        score = case["score"]
        result = case["result"]
        notes = score.get("notes", [])

        notes_html = "".join(
            f"<li>{escape(str(note))}</li>"
            for note in notes
        )

        failed_rows.append(
            f"""
            <article class="case">
                <h3>{escape(str(case["case_id"]))}</h3>
                <p><strong>Overall score:</strong> {score["overall"]:.3f}</p>
                <p><strong>Answer:</strong> {escape(str(result["answer"]))}</p>
                <p><strong>Escalated:</strong> {escape(str(result["escalated"]))}</p>
                <p><strong>Latency:</strong> {result["latency_ms"]:.2f} ms</p>
                <p><strong>Notes:</strong></p>
                <ul>
                    {notes_html or "<li>No notes recorded.</li>"}
                </ul>
            </article>
            """
        )

    if not failed_rows:
        failed_rows.append("<p>No failed cases.</p>")

    safety_rows = []

    for case in report["cases"]:
        score = case["score"]
        result = case["result"]

        safety_rows.append(
            f"""
            <tr>
                <td>{escape(str(case["case_id"]))}</td>
                <td>{score["safety"]:.3f}</td>
                <td>{score["escalation"]:.3f}</td>
                <td>{escape(str(result["escalated"]))}</td>
            </tr>
            """
        )

    provenance = {
        "provider": report.get("provider", "unknown"),
        "model": report.get("model", "unknown"),
    }

    for case in report["cases"]:
        metadata = case["result"].get("metadata", {})

        if isinstance(metadata, dict):
            provenance.update(metadata)

    provenance_rows = "".join(
        f"""
        <tr>
            <td>{escape(str(key))}</td>
            <td>{escape(str(value))}</td>
        </tr>
        """
        for key, value in provenance.items()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Frontier Enterprise Agent Evaluation Report</title>

<style>
body {{
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    max-width: 1100px;
    margin: 0 auto;
    padding: 32px;
    color: #1f2937;
    background: #f8fafc;
}}

h1 {{
    margin-bottom: 8px;
}}

h2 {{
    margin-top: 36px;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 8px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
    margin-top: 16px;
}}

th,
td {{
    padding: 10px 12px;
    border: 1px solid #e5e7eb;
    text-align: left;
}}

th {{
    background: #f1f5f9;
}}

.case {{
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
}}

.summary {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin: 20px 0;
}}

.card {{
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
}}

.card strong {{
    display: block;
    font-size: 1.4rem;
    margin-top: 6px;
}}
</style>
</head>

<body>

<h1>Frontier Enterprise Agent Evaluation Report</h1>

<div class="summary">

    <div class="card">
        Provider
        <strong>{escape(str(report.get("provider", "unknown")))}</strong>
    </div>

    <div class="card">
        Model
        <strong>{escape(str(report.get("model", "unknown")))}</strong>
    </div>

    <div class="card">
        Cases
        <strong>{summary["cases"]}</strong>
    </div>

    <div class="card">
        Overall
        <strong>{summary["overall"]:.3f}</strong>
    </div>

</div>

<h2>Summary Metrics</h2>

<table>
<thead>
<tr>
    <th>Metric</th>
    <th>Score</th>
</tr>
</thead>

<tbody>
{"".join(metric_rows)}
</tbody>
</table>


<h2>Failed Cases</h2>

{''.join(failed_rows)}


<h2>Safety / Escalation Signals</h2>

<table>
<thead>
<tr>
    <th>Case</th>
    <th>Safety</th>
    <th>Escalation</th>
    <th>Escalated</th>
</tr>
</thead>

<tbody>
{"".join(safety_rows)}
</tbody>
</table>


<h2>Provenance</h2>

<table>
<thead>
<tr>
    <th>Field</th>
    <th>Value</th>
</tr>
</thead>

<tbody>
{provenance_rows}
</tbody>
</table>

</body>
</html>
"""


def write_html(report, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_html(report), encoding="utf-8")