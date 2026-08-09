"""Shared process adapter contract."""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..redaction import redact_text


@dataclass
class AdapterResult:
    returncode: int | None
    timed_out: bool
    events: list[dict[str, Any]] = field(default_factory=list)
    raw_stdout: str = ""
    stderr: str = ""
    wall_clock_seconds: float = 0.0
    session_id: str | None = None
    container_metadata: dict[str, Any] = field(default_factory=dict)


class HarnessAdapter:
    name = "base"

    def __init__(self, arm: dict[str, Any]):
        self.arm = arm

    def command(self, prompt: str, workdir: Path, model: str | None) -> list[str]:
        raise NotImplementedError

    def container(self) -> dict[str, Any]:
        return self.arm["container"]

    def docker_command(self, inner: list[str], workdir: Path, run_dir: Path, env: dict[str, str]) -> list[str]:
        container = self.container()
        argv = ["docker", "run", "--rm", "--init", "--pull", "never"]
        platform = container.get("platform")
        if platform:
            argv.extend(["--platform", str(platform)])
        argv.extend(["--network", str(container.get("network", "none"))])
        argv.extend(["--workdir", "/workspace"])
        argv.extend(["--volume", f"{workdir.resolve()}:/workspace:rw"])
        argv.extend(["--volume", f"{run_dir.resolve()}:/artifacts:rw"])
        snapshot = self.arm.get("snapshot") or {}
        for mount in snapshot.get("mounts", []):
            category = str(mount["category"])
            host_path = run_dir / "snapshot-inputs" / category
            if not host_path.is_dir():
                raise ValueError(f"declared snapshot mount has no materialized directory: {category}")
            argv.extend(["--volume", f"{host_path.resolve()}:{mount['target']}:ro"])
        argv.extend(["--env", "HOME=/home/agent"])
        if self.name == "codex":
            argv.extend(["--env", "CODEX_HOME=/home/agent/.codex"])
        if self.name == "opencode":
            argv.extend(["--env", "OPENCODE_CONFIG_DIR=/home/agent/.config/opencode"])
        for key in sorted(env):
            if key not in {"PATH", "HOME", "CODEX_HOME", "OPENCODE_CONFIG_DIR"}:
                argv.extend(["--env", key])
        argv.append(str(container["image"]))
        argv.extend(inner)
        return argv

    def preflight_container(self, run_dir: Path) -> dict[str, Any]:
        """Prove the exact digest is present locally before starting a run."""
        image = str(self.container()["image"])
        expected = str(self.container()["digest"])
        version = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        inspect = subprocess.run(
            ["docker", "image", "inspect", image, "--format", "{{json .RepoDigests}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if version.returncode != 0:
            raise RuntimeError(f"Docker server is unavailable: {version.stderr.strip()}")
        if inspect.returncode != 0:
            raise RuntimeError(f"pinned image is not cached locally: {image}")
        repo_digests = json.loads(inspect.stdout.strip() or "[]")
        if not any(str(digest).endswith(f"@{expected}") for digest in repo_digests):
            raise RuntimeError(f"cached image digest does not match manifest: {image}")
        metadata = {
            "runtime": "docker",
            "engine_version": version.stdout.strip(),
            "image": image,
            "digest": expected,
            "repo_digests": repo_digests,
        }
        (run_dir / "container-preflight.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return metadata

    def run(
        self,
        prompt: str,
        workdir: Path,
        run_dir: Path,
        timeout_seconds: float,
        env: dict[str, str],
        model: str | None,
    ) -> AdapterResult:
        container_metadata = self.preflight_container(run_dir)
        inner = self.command(prompt, workdir, model)
        argv = self.docker_command(inner, workdir, run_dir, env)
        started = time.monotonic()
        events: list[dict[str, Any]] = []
        timed_out = False
        process: subprocess.Popen[str] | None = None
        try:
            process = subprocess.Popen(
                argv,
                cwd=workdir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            raw_stdout, stderr = process.communicate(timeout=timeout_seconds)
            returncode = process.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            if process is not None:
                process.kill()
            raw_stdout, stderr = process.communicate()
            raw_stdout = (exc.stdout or "") + raw_stdout
            stderr = (exc.stderr or "") + stderr
            returncode = process.returncode
        except OSError as exc:
            raw_stdout = ""
            stderr = str(exc)
            returncode = None
        wall_clock = time.monotonic() - started
        for line in raw_stdout.splitlines():
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                parsed = {"type": "text", "text": line}
            if isinstance(parsed, dict):
                events.append(parsed)
        (run_dir / "command.json").write_text(json.dumps(argv, ensure_ascii=False, indent=2), encoding="utf-8")
        (run_dir / "events.jsonl").write_text(redact_text(raw_stdout), encoding="utf-8")
        (run_dir / "stderr.log").write_text(redact_text(stderr), encoding="utf-8")
        return AdapterResult(
            returncode=returncode,
            timed_out=timed_out,
            events=events,
            raw_stdout=raw_stdout,
            stderr=stderr,
            wall_clock_seconds=wall_clock,
            session_id=extract_session_id(events),
            container_metadata=container_metadata,
        )

    def run_command(
        self,
        command: str | list[str],
        workdir: Path,
        run_dir: Path,
        timeout_seconds: float,
        env: dict[str, str],
    ) -> tuple[int | None, str, bool]:
        """Run an acceptance command inside the same pinned image."""
        self.preflight_container(run_dir)
        inner = ["/bin/sh", "-lc", command] if isinstance(command, str) else [str(part) for part in command]
        argv = self.docker_command(inner, workdir, run_dir, env)
        try:
            completed = subprocess.run(
                argv,
                cwd=workdir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            return completed.returncode, (completed.stdout or "") + (completed.stderr or ""), False
        except subprocess.TimeoutExpired as exc:
            return None, (exc.stdout or "") + (exc.stderr or ""), True
        except OSError as exc:
            return None, str(exc), False


def extract_session_id(events: list[dict[str, Any]]) -> str | None:
    for event in events:
        for key in ("session_id", "sessionId", "sessionID"):
            value = event.get(key)
            if isinstance(value, (str, int)):
                return str(value)
        properties = event.get("properties")
        if isinstance(properties, dict):
            for key in ("sessionID", "sessionId", "session_id"):
                value = properties.get(key)
                if isinstance(value, (str, int)):
                    return str(value)
    return None


def build_env(run_dir: Path, arm: dict[str, Any], manifest_env: dict[str, Any]) -> dict[str, str]:
    """Create an isolated environment, inheriting only explicitly allowed vars."""
    allow = set(manifest_env.get("inherit_env", []))
    result = {key: value for key, value in os.environ.items() if key in allow}
    (run_dir / "home").mkdir(parents=True, exist_ok=True)
    result.update({"HOME": "/home/agent", "PATH": os.environ.get("PATH", "")})
    harness = str(arm.get("harness", ""))
    if harness == "codex":
        result["CODEX_HOME"] = "/home/agent/.codex"
    if harness == "opencode":
        result["OPENCODE_CONFIG_DIR"] = "/home/agent/.config/opencode"
    for key, value in (arm.get("env", {}) or {}).items():
        if not isinstance(value, str):
            raise ValueError(f"arm env value for {key} must be a string")
        result[key] = value
    return result
