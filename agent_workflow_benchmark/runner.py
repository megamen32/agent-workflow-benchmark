"""Execute a manifest and emit normalized results plus one transcript archive."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Iterable

from .adapters import CodexAdapter, HarnessAdapter, OpenCodeAdapter
from .adapters.base import AdapterResult, build_env
from .manifest import canonical_manifest, load_manifest, manifest_sha256
from .redaction import redact


ADAPTERS = {"codex": CodexAdapter, "opencode": OpenCodeAdapter}


def _number(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _walk_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_dicts(child)


def extract_usage(events: list[dict[str, Any]]) -> dict[str, float | None]:
    """Extract cumulative usage without assuming one vendor's event schema."""
    inputs: list[float] = []
    outputs: list[float] = []
    totals: list[float] = []
    costs: list[float] = []
    for mapping in _walk_dicts(events):
        for key, value in mapping.items():
            number = _number(value)
            if number is None:
                continue
            normalized = str(key).lower().replace("-", "_")
            if normalized in {"input_tokens", "prompt_tokens", "inputtokens"}:
                inputs.append(number)
            elif normalized in {"output_tokens", "completion_tokens", "outputtokens"}:
                outputs.append(number)
            elif normalized in {"total_tokens", "totaltokens"}:
                totals.append(number)
            elif normalized in {"cost", "cost_usd", "total_cost", "total_cost_usd"}:
                costs.append(number)
    total = max(totals) if totals else (sum(inputs) + sum(outputs) if inputs or outputs else None)
    return {
        "input_tokens": sum(inputs) if inputs else None,
        "output_tokens": sum(outputs) if outputs else None,
        "total_tokens": total,
        "cost_usd": max(costs) if costs else None,
    }


def _resolve_path(value: str | None, base: Path) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def _prepare_workspace(scenario: dict[str, Any], base: Path, run_dir: Path) -> Path:
    workspace = run_dir / "workspace"
    fixture = _resolve_path(scenario.get("fixture"), base)
    if fixture:
        if not fixture.is_dir():
            raise FileNotFoundError(f"scenario fixture is not a directory: {fixture}")
        shutil.copytree(fixture, workspace)
    else:
        workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def _command_argv(command: str | list[Any]) -> tuple[list[str] | str, bool]:
    if isinstance(command, list):
        return [str(part) for part in command], False
    return command, True


def _run_acceptance(
    adapter: HarnessAdapter,
    scenario: dict[str, Any],
    workspace: Path,
    env: dict[str, str],
    timeout: float,
    run_dir: Path,
) -> tuple[int | None, str, bool]:
    command = scenario["acceptance"]["command"]
    started = time.monotonic()
    returncode, output, timed_out = adapter.run_command(
        command,
        workspace,
        run_dir,
        float(scenario["acceptance"].get("timeout_seconds", timeout)),
        env,
    )
    (run_dir / "acceptance.json").write_text(
        json.dumps(
            {
                "returncode": returncode,
                "timed_out": timed_out,
                "output": redact(output),
                "wall_clock_seconds": time.monotonic() - started,
                "container_image": adapter.container()["image"],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return returncode, output, timed_out


def _topology(arm: dict[str, Any]) -> dict[str, Any]:
    levels = arm["topology"]["levels"]
    return {
        "levels": [
            {
                "id": level["id"],
                "roles": level.get("roles", []),
                "harness": level["harness"],
                "model": level["model"],
            }
            for level in levels
        ],
        "parallelism": {
            "mode": arm.get("topology", {}).get("parallelism", {}).get("mode", "unknown"),
            "max_concurrent_children": arm.get("topology", {}).get("parallelism", {}).get(
                "max_concurrent_children"
            ),
            "actual_children": None,
        },
    }


def _model_for_arm(arm: dict[str, Any]) -> str | None:
    for level in arm["topology"]["levels"]:
        if level.get("id") == "lead":
            return str(level.get("model"))
    return str(arm["topology"]["levels"][0].get("model"))


def _adapter(arm: dict[str, Any]) -> HarnessAdapter:
    try:
        return ADAPTERS[arm["harness"]](arm)
    except KeyError as exc:
        raise ValueError(f"unsupported harness: {arm.get('harness')}") from exc


def _transcript_lines(
    arm: dict[str, Any], scenario: dict[str, Any], attempt: int, result: AdapterResult
) -> list[str]:
    lines = [
        json.dumps(
            redact(
                {
                    "arm": arm["id"],
                    "scenario": scenario["id"],
                    "attempt": attempt,
                    "sequence": 0,
                    "harness": arm["harness"],
                    "event": {"type": "user_prompt", "text": scenario["prompt"]},
                }
            ),
            ensure_ascii=False,
            sort_keys=True,
        )
    ]
    for sequence, event in enumerate(result.events):
        lines.append(
            json.dumps(
                redact(
                    {
                        "arm": arm["id"],
                        "scenario": scenario["id"],
                        "attempt": attempt,
                        "sequence": sequence + 1,
                        "harness": arm["harness"],
                        "event": event,
                    }
                ),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    if not lines and result.raw_stdout:
        lines.append(
            json.dumps(
                redact(
                    {
                        "arm": arm["id"],
                        "scenario": scenario["id"],
                        "attempt": attempt,
                        "sequence": 0,
                        "harness": arm["harness"],
                        "event": {"type": "text", "text": result.raw_stdout},
                    }
                ),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    return lines


def run_campaign(
    manifest_path: str | Path,
    output_dir: str | Path,
    arm_filter: set[str] | None = None,
    scenario_limit: int | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    raw, base = load_manifest(manifest_path)
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    campaign = raw["campaign"]
    environment = raw["environment"]
    timeout = float(environment.get("timeout_seconds", 1800))
    arms = [arm for arm in raw["arms"] if not arm_filter or arm["id"] in arm_filter]
    scenarios = raw["scenarios"][:scenario_limit] if scenario_limit else raw["scenarios"]
    if not arms:
        raise ValueError("arm filter selected no arms")
    if dry_run:
        return {
            "campaign": campaign["name"],
            "manifest_sha256": manifest_sha256(raw),
            "arms": [arm["id"] for arm in arms],
            "scenarios": [scenario["id"] for scenario in scenarios],
            "output_dir": str(output),
            "dry_run": True,
        }

    transcript_lines: list[str] = []
    rows: list[dict[str, Any]] = []
    for arm in arms:
        adapter = _adapter(arm)
        for scenario in scenarios:
            repetitions = int(raw["campaign"].get("scenario_repetitions", 1))
            for attempt in range(1, repetitions + 1):
                run_dir = output / arm["id"] / scenario["id"] / f"attempt-{attempt}"
                run_dir.mkdir(parents=True, exist_ok=True)
                started_at = time.time()
                started_monotonic = time.monotonic()
                try:
                    workspace = _prepare_workspace(scenario, base, run_dir)
                    env = build_env(run_dir, arm, environment)
                    prompt = str(scenario["prompt"])
                    adapter_result = adapter.run(
                        prompt=prompt,
                        workdir=workspace,
                        run_dir=run_dir,
                        timeout_seconds=float(scenario.get("timeout_seconds", timeout)),
                        env=env,
                        model=_model_for_arm(arm),
                    )
                    acceptance_code, acceptance_output, acceptance_timeout = _run_acceptance(
                        adapter, scenario, workspace, env, timeout, run_dir
                    )
                    usage = extract_usage(adapter_result.events)
                    infrastructure_invalid = adapter_result.returncode is None and not adapter_result.timed_out
                    if infrastructure_invalid:
                        status = "invalid"
                        failure_category = "infrastructure"
                    elif adapter_result.timed_out or acceptance_timeout:
                        status = "fail"
                        failure_category = "timeout"
                    elif adapter_result.returncode != 0:
                        status = "fail"
                        failure_category = "agent_process"
                    elif acceptance_code != 0:
                        status = "fail"
                        failure_category = "acceptance"
                    else:
                        status = "pass"
                        failure_category = None
                    row = {
                        "campaign": campaign["name"],
                        "manifest_sha256": manifest_sha256(raw),
                        "arm": arm["id"],
                        "workflow_ref": arm.get("workflow_ref", arm["id"]),
                        "scenario": scenario["id"],
                        "scenario_track": scenario.get("track", raw["campaign"].get("scenario_track")),
                        "attempt": attempt,
                        "harness": arm["harness"],
                        "container": {
                            "runtime": "docker",
                            "image": arm["container"]["image"],
                            "digest": arm["container"]["digest"],
                            "platform": arm["container"].get("platform"),
                            "engine_version": adapter_result.container_metadata.get("engine_version"),
                            "network": arm["container"].get("network", "none"),
                        },
                        "topology": _topology(arm),
                        "model_selection": raw["campaign"].get("model_selection", {}),
                        "status": status,
                        "successful_task": status == "pass",
                        "wall_clock_seconds": time.monotonic() - started_monotonic,
                        "agent_wall_clock_seconds": adapter_result.wall_clock_seconds,
                        "input_tokens": usage["input_tokens"],
                        "output_tokens": usage["output_tokens"],
                        "total_tokens": usage["total_tokens"],
                        "cost_usd": usage["cost_usd"],
                        "cost_per_success_usd": usage["cost_usd"] if status == "pass" else None,
                        "pricing": canonical_manifest(raw["campaign"].get("pricing", {})),
                        "session_id": adapter_result.session_id,
                        "transcript": {
                            "archive": "campaign-transcripts.tar.zst",
                            "member": "transcripts.jsonl",
                            "dialog_only": True,
                            "redacted": True,
                        },
                        "invalid": infrastructure_invalid,
                        "failure_category": failure_category,
                        "acceptance_returncode": acceptance_code,
                        "started_at_epoch": started_at,
                    }
                    (run_dir / "result.json").write_text(
                        json.dumps(redact(row), indent=2, ensure_ascii=False), encoding="utf-8"
                    )
                    transcript_lines.extend(_transcript_lines(arm, scenario, attempt, adapter_result))
                    rows.append(row)
                    _ = acceptance_output
                except Exception as exc:  # retain a durable invalid receipt for setup failures
                    row = {
                        "campaign": campaign["name"],
                        "manifest_sha256": manifest_sha256(raw),
                        "arm": arm["id"],
                        "scenario": scenario["id"],
                        "attempt": attempt,
                        "status": "invalid",
                        "successful_task": False,
                        "invalid": True,
                        "failure_category": "setup",
                        "error": redact(str(exc)),
                        "transcript": {
                            "archive": "campaign-transcripts.tar.zst",
                            "member": "transcripts.jsonl",
                            "dialog_only": True,
                            "redacted": True,
                        },
                    }
                    (run_dir / "result.json").write_text(
                        json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8"
                    )
                    rows.append(row)

    results_path = output / "results.jsonl"
    results_path.write_text("".join(json.dumps(redact(row), ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    summary = _summary(rows)
    archive = _write_archive(output, raw, rows, transcript_lines, summary)
    summary["transcript_archive"] = archive
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if not row.get("invalid", False)]
    successful = [row for row in valid if row.get("successful_task") is True]
    costs = [float(row["cost_usd"]) for row in valid if isinstance(row.get("cost_usd"), (int, float))]
    walls = [float(row["wall_clock_seconds"]) for row in valid if isinstance(row.get("wall_clock_seconds"), (int, float))]
    total_cost = sum(costs) if costs else None
    return {
        "attempts": len(rows),
        "valid_attempts": len(valid),
        "successful_tasks": len(successful),
        "pass_rate": (len(successful) / len(valid)) if valid else None,
        "total_effective_cost_usd": total_cost,
        "cost_per_success_usd": (total_cost / len(successful)) if total_cost is not None and successful else None,
        "total_wall_clock_seconds": sum(walls) if walls else None,
        "failure_categories": _failure_counts(valid),
    }


def _failure_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        category = row.get("failure_category")
        if category:
            counts[category] = counts.get(category, 0) + 1
    return counts


def _write_archive(
    output: Path,
    raw_manifest: dict[str, Any],
    rows: list[dict[str, Any]],
    transcript_lines: list[str],
    summary: dict[str, Any],
) -> dict[str, Any]:
    stage = Path(tempfile.mkdtemp(prefix="campaign-archive-", dir=output))
    try:
        manifest_payload = {
            "manifest": canonical_manifest(raw_manifest),
            "manifest_sha256": manifest_sha256(raw_manifest),
            "summary": summary,
            "runs": [
                {
                    "arm": row.get("arm"),
                    "scenario": row.get("scenario"),
                    "attempt": row.get("attempt"),
                    "status": row.get("status"),
                    "cost_usd": row.get("cost_usd"),
                    "wall_clock_seconds": row.get("wall_clock_seconds"),
                    "session_id": row.get("session_id"),
                }
                for row in rows
            ],
        }
        (stage / "campaign-manifest.json").write_text(
            json.dumps(redact(manifest_payload), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (stage / "transcripts.jsonl").write_text("\n".join(transcript_lines) + ("\n" if transcript_lines else ""), encoding="utf-8")
        archive = output / "campaign-transcripts.tar.zst"
        subprocess.run(
            ["tar", "--zstd", "-cf", str(archive), "-C", str(stage), "campaign-manifest.json", "transcripts.jsonl"],
            check=True,
            capture_output=True,
            text=True,
        )
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        (output / "campaign-transcripts.sha256").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
        return {"path": str(archive), "sha256": digest, "members": ["campaign-manifest.json", "transcripts.jsonl"]}
    finally:
        shutil.rmtree(stage, ignore_errors=True)
