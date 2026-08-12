#!/usr/bin/env python3
"""Run the frozen hard SWE-bench campaign with bounded task-level parallelism."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-instance", action="append", default=[])
    parser.add_argument("--max-parallel", type=int, default=4)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    config = json.loads(args.config.resolve().read_text())
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    launcher = root / "scripts/run_swebench_control_canary.py"
    dataset = root / ".agents/at/hard-swebench-verified-10-dataset.json"
    if not dataset.is_file():
        raise SystemExit(f"missing frozen dataset snapshot: {dataset}")
    swebench_python = root / ".agents/at/swebench-venv/bin/python"
    codex = Path("/home/roomhacker/.codex/packages/standalone/current/bin/codex")
    jobs: list[tuple[str, str, list[str]]] = []
    for instance in config["instances"]:
        instance_id = instance["id"]
        if instance_id in args.skip_instance:
            continue
        for workflow, workflow_config in config["workflows"].items():
            cell = output / instance_id / workflow
            if list(cell.glob("*.json")) and (cell / "agent-receipt.json").exists():
                continue
            command = [
                sys.executable,
                str(launcher),
                instance_id,
                "--workflow",
                workflow,
                "--output",
                str(cell),
                "--model",
                config["model"],
                "--dataset",
                str(dataset),
                "--image-digest",
                instance["image_digest"],
                "--timeout",
                "1200",
                "--swebench-python",
                str(swebench_python),
                "--codex",
                str(codex),
            ]
            source = workflow_config.get("source")
            if source:
                source_path = Path(source)
                if not source_path.is_absolute():
                    source_path = root / source_path
                command.extend(["--workflow-source", str(source_path)])
            jobs.append((instance_id, workflow, command))

    def run_job(job: tuple[str, str, list[str]]) -> dict[str, object]:
        instance_id, workflow, command = job
        completed = subprocess.run(command, cwd=root, text=True, capture_output=True)
        log = output / instance_id / workflow / "campaign-launcher.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(completed.stdout + completed.stderr, encoding="utf-8")
        return {
            "instance_id": instance_id,
            "workflow": workflow,
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
