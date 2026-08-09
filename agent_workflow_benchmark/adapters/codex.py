"""Codex CLI adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import HarnessAdapter


class CodexAdapter(HarnessAdapter):
    name = "codex"

    def command(self, prompt: str, workdir: Path, model: str | None) -> list[str]:
        config = self.arm.get("adapter", {}) or {}
        if config.get("command"):
            return _render_command(config["command"], prompt, workdir, model)
        executable = str(config.get("executable", "codex"))
        argv = [executable, "exec", "--json", "--skip-git-repo-check", "--cd", "/workspace"]
        if model:
            argv.extend(["--model", model])
        argv.extend(config.get("extra_args", []))
        argv.append(prompt)
        return argv


def _render_command(template: list[Any], prompt: str, workdir: Path, model: str | None) -> list[str]:
    if not isinstance(template, list) or not template:
        raise ValueError("adapter.command must be a non-empty list")
    values = {"prompt": prompt, "workdir": "/workspace", "model": model or ""}
    return [_substitute(str(item), values) for item in template]


def _substitute(value: str, values: dict[str, str]) -> str:
    for key, replacement in values.items():
        value = value.replace("{" + key + "}", replacement)
    return value
