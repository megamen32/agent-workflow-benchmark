"""Load and validate the harness-neutral campaign manifest."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml


class ManifestError(ValueError):
    """Raised when a campaign manifest cannot safely be executed."""


REQUIRED_ROOT = ("manifest_version", "campaign", "environment", "arms", "scenarios")
PINNED_IMAGE = re.compile(r"^.+@sha256:[0-9a-f]{64}$")
IMAGE_ID = re.compile(r"^sha256:[0-9a-f]{64}$")


def _require(mapping: dict[str, Any], key: str, where: str) -> Any:
    if key not in mapping:
        raise ManifestError(f"{where} is missing required field {key!r}")
    return mapping[key]


def _as_list(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list):
        raise ManifestError(f"{where} must be a list")
    return value


def load_manifest(path: str | Path) -> tuple[dict[str, Any], Path]:
    """Load YAML and validate fields required by the runner."""
    manifest_path = Path(path).resolve()
    try:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError(f"manifest not found: {manifest_path}") from exc
    except yaml.YAMLError as exc:
        raise ManifestError(f"invalid YAML in {manifest_path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ManifestError("manifest root must be a mapping")
    for key in REQUIRED_ROOT:
        _require(raw, key, "manifest")
    if raw["manifest_version"] != 1:
        raise ManifestError("only manifest_version: 1 is supported")
    campaign = raw["campaign"]
    if not isinstance(campaign, dict):
        raise ManifestError("campaign must be a mapping")
    campaign_name = _require(campaign, "name", "campaign")
    if not isinstance(campaign_name, str) or not campaign_name.strip():
        raise ManifestError("campaign.name must be a non-empty string")
    environment = raw["environment"]
    if not isinstance(environment, dict):
        raise ManifestError("environment must be a mapping")
    timeout = environment.get("timeout_seconds", 1800)
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ManifestError("environment.timeout_seconds must be positive")
    runtime = _require(environment, "container_runtime", "environment")
    if not isinstance(runtime, dict) or runtime.get("engine") != "docker":
        raise ManifestError("environment.container_runtime.engine must be docker")
    if runtime.get("pull_policy", "never") != "never":
        raise ManifestError("environment.container_runtime.pull_policy must be never")

    arms = _as_list(raw["arms"], "arms")
    arm_ids: set[str] = set()
    for index, arm in enumerate(arms):
        where = f"arms[{index}]"
        if not isinstance(arm, dict):
            raise ManifestError(f"{where} must be a mapping")
        arm_id = _require(arm, "id", where)
        if not isinstance(arm_id, str) or not arm_id:
            raise ManifestError(f"{where}.id must be a non-empty string")
        if arm_id in arm_ids:
            raise ManifestError(f"duplicate arm id: {arm_id}")
        arm_ids.add(arm_id)
        _validate_topology(arm.get("topology", {}), where)
        harness = str(_require(arm, "harness", where))
        if harness not in {"codex", "opencode"}:
            raise ManifestError(f"{where}.harness must be codex or opencode")
        container = _require(arm, "container", where)
        if not isinstance(container, dict):
            raise ManifestError(f"{where}.container must be a mapping")
        image = _require(container, "image", f"{where}.container")
        digest = _require(container, "digest", f"{where}.container")
        local_image_id = container.get("image_id")
        registry_pinned = isinstance(image, str) and PINNED_IMAGE.fullmatch(image)
        local_pinned = bool(container.get("allow_local_image_id")) and isinstance(image, str) and IMAGE_ID.fullmatch(digest or "")
        if not registry_pinned and not local_pinned:
            raise ManifestError(f"{where}.container.image must use an immutable @sha256 digest or an explicitly allowed local image ID")
        if registry_pinned and digest != image.rsplit("@", 1)[1]:
            raise ManifestError(f"{where}.container.digest must match the image digest")
        if local_pinned:
            if not isinstance(local_image_id, str) or local_image_id != digest:
                raise ManifestError(f"{where}.container.image_id must match the local immutable digest")
        if container.get("platform") not in {None, "linux/amd64", "linux/arm64"}:
            raise ManifestError(f"{where}.container.platform must be linux/amd64 or linux/arm64")
        auth = arm.get("auth")
        if auth is not None:
            if not isinstance(auth, dict):
                raise ManifestError(f"{where}.auth must be a mapping")
            host_env = _require(auth, "host_env", f"{where}.auth")
            target = _require(auth, "container_path", f"{where}.auth")
            if not isinstance(host_env, str) or not host_env:
                raise ManifestError(f"{where}.auth.host_env must be a non-empty environment variable name")
            if not isinstance(target, str) or not target.startswith("/"):
                raise ManifestError(f"{where}.auth.container_path must be an absolute container path")
        for level in arm["topology"]["levels"]:
            if level["harness"] != harness:
                raise ManifestError(f"{where} topology levels must use the arm harness container")
        arm["harness"] = harness
        if "snapshot" in arm:
            _validate_snapshot(arm["snapshot"], f"{where}.snapshot")

    scenarios = _as_list(raw["scenarios"], "scenarios")
    scenario_ids: set[str] = set()
    for index, scenario in enumerate(scenarios):
        where = f"scenarios[{index}]"
        if not isinstance(scenario, dict):
            raise ManifestError(f"{where} must be a mapping")
        scenario_id = _require(scenario, "id", where)
        if not isinstance(scenario_id, str) or not scenario_id:
            raise ManifestError(f"{where}.id must be a non-empty string")
        if scenario_id in scenario_ids:
            raise ManifestError(f"duplicate scenario id: {scenario_id}")
        scenario_ids.add(scenario_id)
        _require(scenario, "prompt", where)
        acceptance = _require(scenario, "acceptance", where)
        if not isinstance(acceptance, dict):
            raise ManifestError(f"{where}.acceptance must be a mapping")
        command = _require(acceptance, "command", f"{where}.acceptance")
        if not isinstance(command, (str, list)) or not command:
            raise ManifestError(f"{where}.acceptance.command must be a string or list")

    if not arms:
        raise ManifestError("manifest must declare at least one arm")
    if not scenarios:
        raise ManifestError("manifest must declare at least one scenario")
    return raw, manifest_path.parent


def _validate_topology(topology: Any, where: str) -> None:
    if not isinstance(topology, dict):
        raise ManifestError(f"{where}.topology must be a mapping")
    levels = _as_list(_require(topology, "levels", f"{where}.topology"), f"{where}.topology.levels")
    if not 1 <= len(levels) <= 3:
        raise ManifestError(f"{where}.topology.levels must contain one to three levels")
    ids: set[str] = set()
    for index, level in enumerate(levels):
        level_where = f"{where}.topology.levels[{index}]"
        if not isinstance(level, dict):
            raise ManifestError(f"{level_where} must be a mapping")
        level_id = _require(level, "id", level_where)
        if level_id in ids:
            raise ManifestError(f"duplicate topology level id: {level_id}")
        ids.add(level_id)
        _require(level, "harness", level_where)
        _require(level, "model", level_where)


def _validate_snapshot(snapshot: Any, where: str) -> None:
    if not isinstance(snapshot, dict):
        raise ManifestError(f"{where} must be a mapping")
    source_path = _require(snapshot, "source_path", where)
    if not isinstance(source_path, str) or not source_path.strip():
        raise ManifestError(f"{where}.source_path must be a non-empty path")
    skills_path = snapshot.get("skills_path")
    if skills_path is not None and (not isinstance(skills_path, str) or not skills_path.strip()):
        raise ManifestError(f"{where}.skills_path must be a path or null")
    inputs = snapshot.get("inputs", {})
    if not isinstance(inputs, dict):
        raise ManifestError(f"{where}.inputs must be a mapping")
    for category in ("source", "skills", "task"):
        values = inputs.get(category, [])
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise ManifestError(f"{where}.inputs.{category} must be a list of strings")
    mounts = snapshot.get("mounts", [])
    if not isinstance(mounts, list):
        raise ManifestError(f"{where}.mounts must be a list")
    for index, mount in enumerate(mounts):
        mount_where = f"{where}.mounts[{index}]"
        if not isinstance(mount, dict):
            raise ManifestError(f"{mount_where} must be a mapping")
        category = _require(mount, "category", mount_where)
        target = _require(mount, "target", mount_where)
        if category not in {"source", "skills", "task"}:
            raise ManifestError(f"{mount_where}.category must be source, skills, or task")
        if not isinstance(target, str) or not target.startswith("/"):
            raise ManifestError(f"{mount_where}.target must be an absolute container path")


def canonical_manifest(raw: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-safe copy suitable for hashing and publishing."""
    def normalize(value: Any) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, dict):
            return {str(key): normalize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [normalize(item) for item in value]
        return value

    return normalize(raw)


def manifest_sha256(raw: dict[str, Any]) -> str:
    payload = json.dumps(canonical_manifest(raw), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
