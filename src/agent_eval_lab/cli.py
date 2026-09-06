import argparse
from pathlib import Path

from .adapters.mock import MockAgentAdapter
from .dataset import load_jsonl
from .reporting import write_json, write_markdown
from .runner import run_evaluation


def main():
    parser = argparse.ArgumentParser(description="Evaluate enterprise AI agent behavior")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--dataset", required=True)
    run.add_argument("--provider", default="mock", choices=["mock"])
    run.add_argument("--output", default="results/latest.json")
    run.add_argument("--latency-target-ms", type=float, default=5000.0)
    args = parser.parse_args()
    cases = load_jsonl(args.dataset)
    report = run_evaluation(cases, MockAgentAdapter(), args.latency_target_ms)
    output = Path(args.output)
    write_json(report, output); write_markdown(report, output.with_suffix(".md"))
    for metric, value in report["summary"].items():
        print(f"{metric.replace('_',' ').title()}: {value if metric == 'cases' else f'{value:.3f}'}")

if __name__ == "__main__": main()
