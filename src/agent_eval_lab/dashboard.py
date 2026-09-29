import json
from pathlib import Path


def generate_dashboard(report_path, output_path="results/dashboard.html"):
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))

    summary = report["summary"]

    failed_cases = [
        case for case in report["cases"]
        if case["score"]["overall"] < 1.0
    ]

    safety_failures = [
        case for case in report["cases"]
        if case["score"]["safety"] < 1.0
    ]

    release_gate = (
        "PASS"
        if summary["overall"] >= 0.8 and summary["safety"] >= 0.8
        else "FAIL"
    )

    status_color = "#22c55e" if release_gate == "PASS" else "#ef4444"

    rows = ""
    for key, value in summary.items():
        if key != "cases":
            rows += f"""
            <tr>
                <td>{key.replace('_', ' ').title()}</td>
                <td>{value:.3f}</td>
            </tr>
            """

    case_rows = ""
    for case in report["cases"]:
        case_rows += f"""
        <tr>
            <td>{case['case_id']}</td>
            <td>{case['score']['overall']:.3f}</td>
            <td>{case['result']['escalated']}</td>
            <td>{case['result']['latency_ms']:.2f}</td>
        </tr>
        """

    failed_html = "".join(
        f"<li>{c['case_id']} ({c['score']['overall']:.3f})</li>"
        for c in failed_cases
    ) or "<li>None</li>"

    safety_html = "".join(
        f"<li>{c['case_id']}</li>"
        for c in safety_failures
    ) or "<li>None</li>"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Enterprise Agent Evaluation Dashboard</title>

<style>
body {{
    font-family: Arial, sans-serif;
    background: #f5f5f5;
    margin: 0;
    padding: 30px;
}}

.container {{
    max-width: 1200px;
    margin: auto;
}}

h1 {{
    margin-bottom: 25px;
}}

.cards {{
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 30px;
}}

.card {{
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    min-width: 200px;
}}

.card h3 {{
    margin: 0;
    color: #666;
    font-size: 16px;
}}

.card p {{
    margin: 10px 0 0;
    font-size: 28px;
    font-weight: bold;
}}

.section {{
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 25px;
}}

.badge {{
    display: inline-block;
    padding: 10px 20px;
    border-radius: 20px;
    color: white;
    font-weight: bold;
    background: {status_color};
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}}

th {{
    background: #f1f5f9;
}}

th, td {{
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}}

ul {{
    margin-top: 10px;
}}
</style>
</head>

<body>

<div class="container">

<h1>Enterprise Agent Evaluation Dashboard</h1>

<div class="cards">

<div class="card">
    <h3>Overall Score</h3>
    <p>{summary["overall"]:.3f}</p>
</div>

<div class="card">
    <h3>Cases</h3>
    <p>{summary["cases"]}</p>
</div>

<div class="card">
    <h3>Safety Score</h3>
    <p>{summary["safety"]:.3f}</p>
</div>

<div class="card">
    <h3>Release Gate</h3>
    <p>{release_gate}</p>
</div>

</div>

<div class="section">
    <h2>Release Gate Status</h2>
    <span class="badge">{release_gate}</span>
</div>

<div class="section">
    <h2>Dimension Scores</h2>

    <table>
        <tr>
            <th>Metric</th>
            <th>Score</th>
        </tr>

        {rows}

    </table>
</div>

<div class="section">
    <h2>Case Summary</h2>

    <table>
        <tr>
            <th>Case ID</th>
            <th>Overall Score</th>
            <th>Escalated</th>
            <th>Latency (ms)</th>
        </tr>

        {case_rows}

    </table>
</div>

<div class="section">
    <h2>Failed Cases</h2>
    <ul>
        {failed_html}
    </ul>
</div>

<div class="section">
    <h2>Safety Failures</h2>
    <ul>
        {safety_html}
    </ul>
</div>

</div>

</body>
</html>
"""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")

    return output