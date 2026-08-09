#!/usr/bin/env python3
"""Summarize normalized workflow benchmark results by arm and model topology."""

from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def read_rows(path: Path) -> list[dict]:
    """Read JSONL rows and reject malformed records with a useful error."""
    rows = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSON at line {number}: {exc}") from exc
        if not isinstance(row, dict):
            raise SystemExit(f"line {number} is not a JSON object")
        rows.append(row)
    return rows


def median(values: list[float]) -> float | None:
    """Return a median while preserving missing measurements as missing."""
    return statistics.median(values) if values else None


def main() -> int:
    """Print separate quality, time, token, and cost summaries."""
    if len(sys.argv) != 2:
        raise SystemExit("usage: summarize_results.py RESULTS.jsonl")
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in read_rows(Path(sys.argv[1])):
        if not row.get("invalid", False):
            groups[str(row.get("arm", "unknown"))].append(row)
    print("arm\tpass_rate\tsuccessful_tasks\tmedian_wall_s\ttotal_cost_usd\tcost_per_success_usd\tmedian_total_tokens")
    for arm, rows in sorted(groups.items()):
        passed = sum(row.get("status") == "pass" for row in rows)
        wall = [float(row["wall_clock_seconds"]) for row in rows if row.get("wall_clock_seconds") is not None]
        tokens = [float(row["total_tokens"]) for row in rows if row.get("total_tokens") is not None]
        cost = [float(row["cost_usd"]) for row in rows if row.get("cost_usd") is not None]
        rate = passed / len(rows) if rows else 0.0
        total_cost = sum(cost) if cost else None
        cost_per_success = total_cost / passed if total_cost is not None and passed else None
        print(f"{arm}\t{rate:.3f}\t{passed}\t{median(wall)}\t{total_cost}\t{cost_per_success}\t{median(tokens)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
