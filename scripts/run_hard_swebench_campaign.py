#!/usr/bin/env python3
"""Run the frozen hard SWE-bench campaign with bounded task-level parallelism."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import random
import subprocess
import sys
from pathlib import Path


def planned_cells(
    config: dict[str, object], output: Path
) -> list[tuple[str, str, int, Path]]:
    """Return one isolated cell per task, workflow, and matched repeat."""

    repetitions = config.get("repetitions", 1)
    if not isinstance(repetitions, int) or repetitions < 1:
        raise ValueError("repetitions must be a positive integer")
    instances = config.get("instances")
    workflows = config.get("workflows")
    if not isinstance(instances, list) or not isinstance(workflows, dict):
        raise ValueError("instances and workflows are required")
    return [
        (str(instance["id"]), workflow, repeat, output / str(instance["id"]) / workflow / f"repeat-{repeat}")
        for instance in instances
        if isinstance(instance, dict)
        for workflow in workflows
        for repeat in range(1, repetitions + 1)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-instance", action="append", default=[])
    parser.add_argument("--max-parallel", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    config = json.loads(args.config.resolve().read_text())
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    launcher = root / "scripts/run_swebench_control_canary.py"
    dataset = config.get(
        "dataset_snapshot", root / ".agents/at/hard-swebench-verified-10-dataset.json"
    )
    dataset = Path(dataset) if isinstance(dataset, str) and Path(dataset).is_file() else str(config["dataset"])
    dataset_revision = config.get("dataset_revision")
    if not isinstance(dataset_revision, str) or len(dataset_revision) != 40:
        raise SystemExit("dataset_revision must be a pinned 40-character commit")
    swebench_python = root / ".agents/at/swebench-venv/bin/python"
    codex = Path("/home/roomhacker/.codex/packages/standalone/current/bin/codex")
    jobs: list[tuple[str, str, int, list[str], Path]] = []
    instances = {str(instance["id"]): instance for instance in config["instances"]}
    for instance_id, workflow, repeat, cell in planned_cells(config, output):
        if instance_id in args.skip_instance:
            continue
        workflow_config = config["workflows"][workflow]
        if not isinstance(workflow_config, dict):
            raise SystemExit(f"workflow {workflow} must be an object")
        if (cell / "agent-receipt.json").is_file():
            continue
        instance = instances[instance_id]
        command = [
            sys.executable,
            str(launcher),
            instance_id,
            "--workflow",
            workflow,
            "--output",
            str(cell),
            "--model",
            str(workflow_config.get("lead_model", config["model"])),
            "--dataset",
            str(dataset),
            "--dataset-revision",
            dataset_revision,
            "--image-digest",
            str(instance["image_digest"]),
            "--repeat",
            str(repeat),
            "--declared-topology-json",
            json.dumps(workflow_config.get("topology", {"levels": [{"id": "lead"}]})),
            "--timeout",
            "1200",
            "--swebench-python",
            str(swebench_python),
            "--codex",
            str(codex),
        ]
        if workflow_config.get("require_topology_receipt"):
            command.append("--require-topology-receipt")
        source = workflow_config.get("source")
        if source:
            source_path = Path(str(source))
            if not source_path.is_absolute():
                source_path = root / source_path
            command.extend(["--workflow-source", str(source_path)])
        jobs.append((instance_id, workflow, repeat, command, cell))
    random.Random(config.get("order_seed", 0)).shuffle(jobs)
    if args.dry_run:
        plan = [
            {"instance_id": instance_id, "workflow": workflow, "repeat": repeat, "output": str(cell)}
            for instance_id, workflow, repeat, _, cell in jobs
        ]
        print(json.dumps({"planned_cells": len(plan), "cells": plan}, indent=2))
        return 0

    def run_job(job: tuple[str, str, int, list[str], Path]) -> dict[str, object]:
        instance_id, workflow, repeat, command, cell = job
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True)
        log = cell / "campaign-launcher.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(completed.stdout + completed.stderr, encoding="utf-8")
        return {
            "instance_id": instance_id,
            "workflow": workflow,
            "repeat": repeat,
            "returncode": completed.returncode,
        }

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_parallel) as pool:
        for row in pool.map(run_job, jobs):
            rows.append(row)
            print(json.dumps(row), flush=True)
    (output / "campaign-status.json").write_text(
        json.dumps(rows, indent=2) + "\n", encoding="utf-8"
    )
    return 1 if any(row["returncode"] != 0 for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
