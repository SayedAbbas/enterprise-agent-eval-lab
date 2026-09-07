import argparse
from pathlib import Path

from .adapters.frontier import ProviderError
from .adapters.registry import PROVIDERS, build_adapter
from .dataset import load_jsonl
from .reporting import comparison_markdown, write_json, write_markdown
from .runner import run_evaluation


def main():
    parser = argparse.ArgumentParser(description="Evaluate frontier enterprise agent behavior")
    sub = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dataset", required=True)
    common.add_argument("--latency-target-ms", type=float, default=5000.0)
    common.add_argument("--timeout", type=float, default=60.0)
    run = sub.add_parser("run", parents=[common])
    run.add_argument("--provider", default="mock", choices=["mock", *PROVIDERS])
    run.add_argument("--model", help="Override the provider's default model ID")
    run.add_argument("--output", default="results/latest.json")
    compare = sub.add_parser("compare", parents=[common])
    compare.add_argument("--providers", nargs="+", default=["mock"], choices=["mock", *PROVIDERS])
    compare.add_argument("--output-dir", default="results/comparison")
    args = parser.parse_args()
    cases = load_jsonl(args.dataset)
    try:
        if args.command == "compare":
            reports = []
            output_dir = Path(args.output_dir)
            for provider in args.providers:
                report = run_evaluation(cases, build_adapter(provider, timeout=args.timeout), args.latency_target_ms)
                reports.append(report)
                write_json(report, output_dir / f"{provider}.json")
            leaderboard = output_dir / "leaderboard.md"
            leaderboard.parent.mkdir(parents=True, exist_ok=True)
            leaderboard.write_text(comparison_markdown(reports), encoding="utf-8")
            print(comparison_markdown(reports), end="")
            return
        report = run_evaluation(
            cases,
            build_adapter(args.provider, args.model, args.timeout),
            args.latency_target_ms,
        )
    except ProviderError as exc:
        parser.error(str(exc))
    output = Path(args.output)
    write_json(report, output)
    write_markdown(report, output.with_suffix(".md"))
    for metric, value in report["summary"].items():
        print(f"{metric.replace('_',' ').title()}: {value if metric == 'cases' else f'{value:.3f}'}")

if __name__ == "__main__": main()
