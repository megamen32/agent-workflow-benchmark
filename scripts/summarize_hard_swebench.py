#!/usr/bin/env python3
"""Summarize a completed sanitized hard SWE-bench campaign."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


ORDER = ("control", "lhc", "superpowers", "gsd")


def report_for(cell: Path) -> dict[str, object]:
    reports = []
    for path in cell.glob("*.json"):
        try:
            value = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "resolved_ids" in value:
            reports.append(value)
    if len(reports) != 1:
        raise ValueError(f"expected one grader report in {cell}, found {len(reports)}")
    return reports[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for receipt_path in args.results.glob("*/*/agent-receipt.json"):
        receipt = json.loads(receipt_path.read_text())
        grader = report_for(receipt_path.parent)
        instance_id = receipt["instance_id"]
        rows.append(
            {
                **receipt,
                "resolved": instance_id in grader["resolved_ids"],
                "grader_error": instance_id in grader["error_ids"],
            }
        )
    if len(rows) != 40 or not all(row["git_history_sanitized"] for row in rows):
        raise SystemExit("campaign must contain 40 sanitized cells")
    summary = {"cells": len(rows), "workflows": {}, "tasks": {}}
    for workflow in ORDER:
        selected = [row for row in rows if row["workflow"] == workflow]
        summary["workflows"][workflow] = {
            "resolved": sum(row["resolved"] for row in selected),
            "total": len(selected),
            "resolved_ids": [row["instance_id"] for row in selected if row["resolved"]],
            "grader_errors": sum(row["grader_error"] for row in selected),
            "agent_timeouts": sum(row["timed_out"] for row in selected),
            "median_agent_seconds": round(
                statistics.median(row["wall_clock_seconds"] for row in selected), 2
            ),
            "total_agent_seconds": round(
                sum(row["wall_clock_seconds"] for row in selected), 2
            ),
            "total_input_tokens": sum(row["input_tokens"] or 0 for row in selected),
            "total_output_tokens": sum(row["output_tokens"] or 0 for row in selected),
        }
    for instance_id in sorted({row["instance_id"] for row in rows}):
        summary["tasks"][instance_id] = {
            row["workflow"]: {
                "resolved": row["resolved"],
                "agent_seconds": round(row["wall_clock_seconds"], 2),
                "input_tokens": row["input_tokens"],
            }
            for row in rows
            if row["instance_id"] == instance_id
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["workflows"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
