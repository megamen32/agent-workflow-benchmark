#!/usr/bin/env python3
"""Run one matched workflow cell, then grade its patch with SWE-bench."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from datasets import load_dataset


DATASET = "SWE-bench/SWE-bench_Verified"


def public_prompt(instance: dict[str, object], workflow: str = "control") -> str:
    """Expose the issue, never the gold patch or hidden acceptance contract."""

    workflow_instruction = {
        "control": "",
        "lhc": "Follow the mounted Last Human Commit business-first instructions. ",
        "superpowers": "Use the official $using-superpowers workflow and relevant skills. ",
        "gsd": "Use the official $gsd-quick workflow end-to-end. ",
    }[workflow]
    return (
        workflow_instruction
        +
        "Fix the following real repository issue. Work directly in /testbed. "
        "Trace the relevant production path, implement the smallest complete "
        "fix, and run focused public tests when practical. Do not search the "
        "internet for the issue or its solution. Do not commit changes; leave "
        "the final patch in the working tree.\n\n"
        + str(instance["problem_statement"])
    )


def instance_by_id(instance_id: str, dataset: str, revision: str | None = None) -> dict[str, object]:
    path = Path(dataset)
    rows = (
        json.loads(path.read_text())
        if path.is_file()
        else load_dataset(dataset, split="test", revision=revision)
    )
    for row in rows:
        if row["instance_id"] == instance_id:
            return dict(row)
    raise SystemExit(f"unknown instance: {instance_id}")


def run(*argv: str, check: bool = True, **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(argv), text=True, check=check, **kwargs)


def extract_usage(events: list[dict[str, object]]) -> dict[str, int | None]:
    input_tokens: list[int] = []
    output_tokens: list[int] = []
    total_tokens: list[int] = []

    def visit(value: object) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = str(key).lower().replace("-", "_")
                if isinstance(child, int):
                    if normalized in {"input_tokens", "prompt_tokens"}:
                        input_tokens.append(child)
                    elif normalized in {"output_tokens", "completion_tokens"}:
                        output_tokens.append(child)
                    elif normalized == "total_tokens":
                        total_tokens.append(child)
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(events)
    return {
        "input_tokens": max(input_tokens) if input_tokens else None,
        "output_tokens": max(output_tokens) if output_tokens else None,
        "total_tokens": max(total_tokens) if total_tokens else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance_id")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--dataset", default=DATASET)
    parser.add_argument("--dataset-revision")
    parser.add_argument("--image-digest")
    parser.add_argument("--preserve-git-history", action="store_true")
    parser.add_argument(
        "--workflow", choices=("control", "lhc", "superpowers", "gsd"), default="control"
    )
    parser.add_argument("--workflow-source", type=Path)
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--declared-topology-json", default='{"levels":[{"id":"lead"}]}')
    parser.add_argument("--require-topology-receipt", action="store_true")
    parser.add_argument("--swebench-python", type=Path, required=True)
    parser.add_argument("--codex", type=Path, required=True)
    args = parser.parse_args()
    args.output = args.output.resolve()
    if not args.swebench_python.is_absolute():
        args.swebench_python = Path.cwd() / args.swebench_python
    args.codex = args.codex.resolve()
    if args.workflow_source:
        args.workflow_source = args.workflow_source.resolve()
    if args.workflow != "control" and not (
        args.workflow_source and args.workflow_source.is_dir()
    ):
        raise SystemExit(f"{args.workflow} requires --workflow-source")

    if args.repeat < 1:
        raise SystemExit("repeat must be positive")
    try:
        declared_topology = json.loads(args.declared_topology_json)
    except json.JSONDecodeError as exc:
        raise SystemExit("declared topology must be valid JSON") from exc
    if not isinstance(declared_topology, dict) or not isinstance(declared_topology.get("levels"), list):
        raise SystemExit("declared topology must contain levels")
    instance = instance_by_id(args.instance_id, args.dataset, args.dataset_revision)
    image = str(instance["image"])
    base_commit = str(instance["base_commit"])
    if not re.fullmatch(r"swebench/sweb\.eval\.[a-z0-9._:-]+", image):
        raise SystemExit(f"unexpected image name: {image}")
    if args.image_digest:
        inspected = run(
            "docker",
            "image",
            "inspect",
            image,
            "--format",
            "{{json .RepoDigests}}",
            capture_output=True,
            check=False,
        )
        if inspected.returncode != 0:
            raise SystemExit(f"pinned image is not local: {image}")
        repo_digests = json.loads(inspected.stdout or "[]")
        if not any(str(value).endswith("@" + args.image_digest) for value in repo_digests):
            raise SystemExit(f"image digest mismatch for {image}")
    if not re.fullmatch(r"[0-9a-f]{40}", base_commit):
        raise SystemExit(f"unexpected base commit: {base_commit}")
    auth_root = Path(os.environ.get("CODEX_HOME", "")).resolve()
    for name in ("auth.json", ".credentials.json"):
        if not (auth_root / name).is_file():
            raise SystemExit(f"missing {name} in CODEX_HOME")
    args.output.mkdir(parents=True, exist_ok=True)
    container = f"arena-{args.workflow}-{args.instance_id.lower()}-{os.getpid()}"
    events_path = args.output / "events.jsonl"
    prediction_path = args.output / "prediction.jsonl"
    started = time.monotonic()

    try:
        with tempfile.TemporaryDirectory(prefix="arena-swebench-auth-") as directory:
            auth_stage = Path(directory)
            for name in ("auth.json", ".credentials.json"):
                shutil.copyfile(auth_root / name, auth_stage / name)
                (auth_stage / name).chmod(0o600)
            run(
                "docker",
                "create",
                "--name",
                container,
                "--network",
                "host",
                "--volume",
                f"{args.codex.resolve()}:/opt/codex:ro",
                "--volume",
                f"{auth_stage}:/auth/codex:ro",
                *(
                    ["--volume", f"{args.workflow_source}:/arena/workflow:ro"]
                    if args.workflow_source
                    else []
                ),
                image,
                "tail",
                "-f",
                "/dev/null",
                capture_output=True,
            )
            run("docker", "start", container, capture_output=True)
            setup = [
                "mkdir -p /arena/home /arena/codex-home",
                "cp /auth/codex/auth.json /auth/codex/.credentials.json /arena/codex-home/",
            ]
            if not args.preserve_git_history:
                setup.extend(
                    [
                        "cd /testbed",
                        "find .git -depth -delete",
                        "git init -q",
                        "git config user.name 'Arena Baseline'",
                        "git config user.email 'arena-baseline@example.invalid'",
                        "git add -A",
                        "GIT_AUTHOR_DATE='2000-01-01T00:00:00Z' "
                        "GIT_COMMITTER_DATE='2000-01-01T00:00:00Z' "
                        "git commit -qm 'arena synthetic baseline'",
                        "git tag arena-baseline",
                        "test \"$(git rev-list --all --count)\" = 1",
                        "test -z \"$(git remote)\"",
                    ]
                )
            if args.workflow == "lhc":
                setup.extend(
                    [
                        "mkdir -p /home/roomhacker/.local/share/last-human-commit",
                        "ln -s /arena/workflow /home/roomhacker/.local/share/last-human-commit/current",
                        "cp /arena/workflow/AGENTS.md /testbed/AGENTS.md",
                        "cp /arena/workflow/CLAUDE.md /testbed/CLAUDE.md",
                    ]
                )
            elif args.workflow in {"superpowers", "gsd"}:
                setup.extend(
                    [
                        "mkdir -p /testbed/.codex",
                        "cp -a /arena/workflow/. /testbed/.codex/",
                    ]
                )
            if args.workflow == "gsd":
                setup.extend(
                    [
                        "mkdir -p /testbed/.planning",
                        "printf '# Roadmap\\n\\n## Current\\n\\n- Resolve the assigned issue.\\n' > /testbed/.planning/ROADMAP.md",
                        "printf '# State\\n\\nCurrent task: resolve the assigned issue.\\n' > /testbed/.planning/STATE.md",
                    ]
                )
            run(
                "docker",
                "exec",
                container,
                "/bin/bash",
                "-lc",
                " && ".join(setup),
                capture_output=True,
            )
            command = [
            "docker",
            "exec",
            "-e",
            "HOME=/arena/home",
            "-e",
            "CODEX_HOME=/arena/codex-home",
            "-w",
            "/testbed",
            container,
            "/opt/codex",
            "exec",
            "--json",
            "--ephemeral",
            "--ignore-user-config",
            "--skip-git-repo-check",
            "--model",
            args.model,
            "--dangerously-bypass-approvals-and-sandbox",
            public_prompt(instance, args.workflow),
            ]
            try:
                completed = subprocess.run(
                    command,
                    text=True,
                    capture_output=True,
                    timeout=args.timeout,
                    check=False,
                )
                timed_out = False
            except subprocess.TimeoutExpired as exc:
                completed = subprocess.CompletedProcess(
                    command,
                    124,
                    stdout=exc.stdout or "",
                    stderr=exc.stderr or "",
                )
                timed_out = True
        events_path.write_text(completed.stdout, encoding="utf-8")
        (args.output / "stderr.log").write_text(completed.stderr, encoding="utf-8")
        patch = run(
            "docker",
            "exec",
            "-w",
            "/testbed",
            container,
            "/bin/bash",
            "-lc",
            "git add -N -- . ':(exclude)AGENTS.md' ':(exclude)CLAUDE.md' "
            "':(exclude).codex/**' ':(exclude).planning/**' ':(exclude).agents/**' && "
            "git diff --binary arena-baseline -- . "
            "':(exclude)AGENTS.md' ':(exclude)CLAUDE.md' "
            "':(exclude).codex/**' ':(exclude).planning/**' ':(exclude).agents/**'",
            capture_output=True,
        ).stdout
    finally:
        run("docker", "rm", "-f", container, check=False, capture_output=True)

    events = []
    for line in completed.stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    prediction = {
        "instance_id": args.instance_id,
        "model_name_or_path": f"{args.workflow}/{args.model}",
        "model_patch": patch,
    }
    prediction_path.write_text(json.dumps(prediction) + "\n", encoding="utf-8")
    actual_model_invocations = [
        {"role": "lead", "model": args.model, "source": "outer-codex-cli"}
    ]
    expected_levels = declared_topology["levels"]
    topology_receipt_status = (
        "verified"
        if len(expected_levels) == 1
        and expected_levels[0].get("model") in (None, args.model)
        and not args.require_topology_receipt
        else "missing"
    )
    receipt = {
        "instance_id": args.instance_id,
        "image": image,
        "model": args.model,
        "workflow": args.workflow,
        "repeat": args.repeat,
        "declared_topology": declared_topology,
        "actual_model_invocations": actual_model_invocations,
        "topology_receipt_status": topology_receipt_status,
        "git_history_sanitized": not args.preserve_git_history,
        "dataset_base_commit": base_commit,
        "agent_returncode": completed.returncode,
        "timed_out": timed_out,
        "patch_bytes": len(patch.encode()),
        "wall_clock_seconds": time.monotonic() - started,
        **extract_usage(events),
    }
    (args.output / "agent-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2))

    evaluation = run(
        str(args.swebench_python),
        "-m",
        "swebench.harness.run_evaluation",
        "--dataset_name",
        args.dataset,
        "--split",
        "test",
        "--predictions_path",
        str(prediction_path.resolve()),
        "--max_workers",
        "1",
        "--instance_ids",
        args.instance_id,
        "--run_id",
        f"arena-{args.instance_id.lower()}-{os.getpid()}",
        "--timeout",
        str(args.timeout),
        "--report_dir",
        str(args.output.resolve()),
        capture_output=False,
        check=False,
        cwd=args.output.resolve(),
    )
    return evaluation.returncode


if __name__ == "__main__":
    raise SystemExit(main())
