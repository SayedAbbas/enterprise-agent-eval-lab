import json
from pathlib import Path

from .schema import EvalCase, ExpectedBehavior, ToolSpec


def load_jsonl(path: str | Path) -> list[EvalCase]:
    cases = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
            cases.append(EvalCase(
                id=row["id"], task=row["task"], evidence=row.get("evidence", {}),
                available_tools=[ToolSpec(**t) for t in row.get("available_tools", [])],
                expected=ExpectedBehavior(**row.get("expected", {})),
            ))
    return cases
