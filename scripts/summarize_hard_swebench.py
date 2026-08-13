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


def summarize_task_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Keep every repeat visible instead of overwriting it by workflow key."""

    tasks: dict[str, object] = {}
    for instance_id in sorted({str(row["instance_id"]) for row in rows}):
        task: dict[str, object] = {}
        for workflow in ORDER:
            cells = sorted(
                (row for row in rows if row["instance_id"] == instance_id and row["workflow"] == workflow),
                key=lambda row: int(row.get("repeat", 1)),
            )
            if not cells:
                continue
            task[workflow] = {
                "resolved": sum(bool(row["resolved"]) for row in cells),
                "total": len(cells),
                "repeats": [
                    {
                        "repeat": row.get("repeat", 1),
                        "resolved": row["resolved"],
                        "agent_seconds": round(float(row["wall_clock_seconds"]), 2),
                        "input_tokens": row["input_tokens"],
                    }
                    for row in cells
                ],
            }
        tasks[instance_id] = task
    return tasks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-tasks", type=int)
    parser.add_argument("--expected-repeats", type=int, default=1)
    parser.add_argument("--require-topology-receipts", action="store_true")
    args = parser.parse_args()
    rows = []
    for receipt_path in args.results.glob("**/agent-receipt.json"):
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
    expected_cells = (
        args.expected_tasks * args.expected_repeats * len(ORDER)
        if args.expected_tasks is not None
        else 40
    )
    if len(rows) != expected_cells or not all(row.get("git_history_sanitized") for row in rows):
        raise SystemExit(f"campaign must contain {expected_cells} sanitized cells")
    summary = {"cells": len(rows), "workflows": {}, "tasks": {}}
    for workflow in ORDER:
        selected = [row for row in rows if row["workflow"] == workflow]
        invalid_topology = [
            row
            for row in selected
            if args.require_topology_receipts
            and row.get("topology_receipt_status") != "verified"
        ]
        eligible = [row for row in selected if row not in invalid_topology]
        summary["workflows"][workflow] = {
            "status": "infrastructure-invalid" if invalid_topology else "valid",
            "resolved": sum(row["resolved"] for row in eligible),
            "total": len(eligible),
            "invalid_topology_cells": len(invalid_topology),
            "resolved_ids": [row["instance_id"] for row in eligible if row["resolved"]],
            "grader_errors": sum(row["grader_error"] for row in eligible),
            "agent_timeouts": sum(row["timed_out"] for row in eligible),
            "median_agent_seconds": (
                round(statistics.median(row["wall_clock_seconds"] for row in eligible), 2)
                if eligible
                else None
            ),
            "total_agent_seconds": round(
                sum(row["wall_clock_seconds"] for row in eligible), 2
            ),
            "total_input_tokens": sum(row["input_tokens"] or 0 for row in eligible),
            "total_output_tokens": sum(row["output_tokens"] or 0 for row in eligible),
        }
    summary["tasks"] = summarize_task_rows(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["workflows"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
