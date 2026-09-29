from agent_eval_lab.dashboard import generate_dashboard


def test_dashboard_generation():
    output = generate_dashboard(
        "results/example-report.json",
        "results/test-dashboard.html",
    )

    assert output.exists()