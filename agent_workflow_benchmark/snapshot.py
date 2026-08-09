"""Build immutable per-cell benchmark snapshot records and materialize inputs."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path, PureWindowsPath
from typing import Any, Iterable, Sequence


class SnapshotError(ValueError):
    """Raised when a declared benchmark snapshot cannot be materialized safely."""


def canonical_snapshot(raw: dict[str, Any]) -> dict[str, Any]:
    def normalize(value: Any) -> Any:
        if isinstance(value, dict):
            return {str(key): normalize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [normalize(item) for item in value]
        return value

    return normalize(raw)


def snapshot_sha256(raw: dict[str, Any]) -> str:
    payload = json.dumps(canonical_snapshot(raw), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _safe_relative(value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise SnapshotError(f"snapshot input must be a relative POSIX path: {value!r}")
    path = Path(value)
    if path.is_absolute() or PureWindowsPath(value).is_absolute() or PureWindowsPath(value).drive:
        raise SnapshotError(f"snapshot input must be relative: {value!r}")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise SnapshotError(f"snapshot input escapes its root: {value!r}")
    return path


def _root(value: str | Path | None, label: str) -> Path | None:
    if value is None:
        return None
    path = Path(value).resolve()
    if not path.is_dir():
        raise SnapshotError(f"{label} must be an existing directory: {path}")
    return path


def _source_file(root: Path, relative: Path) -> Path:
    candidate = root.joinpath(relative)
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise SnapshotError(f"snapshot input may not use symlinks: {relative.as_posix()}")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (FileNotFoundError, ValueError) as exc:
        raise SnapshotError(f"snapshot input is outside or missing: {relative.as_posix()}") from exc
    if not resolved.is_file():
        raise SnapshotError(f"snapshot input must be a file: {relative.as_posix()}")
    return resolved


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _records_digest(records: list[dict[str, Any]]) -> str:
    payload = json.dumps(records, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def _copy_category(
    destination: Path,
    category: str,
    root: Path | None,
    inputs: Iterable[str],
    *,
    required: bool,
) -> tuple[list[dict[str, Any]], str | None]:
    declared = list(inputs)
    if root is None:
        if declared:
            raise SnapshotError(f"{category} inputs require a {category} root")
        return [], None
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in declared:
        relative = _safe_relative(raw)
        name = relative.as_posix()
        if name in seen:
            raise SnapshotError(f"duplicate {category} snapshot input: {name}")
        seen.add(name)
        source = _source_file(root, relative)
        target = destination / category / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        records.append({"path": name, "sha256": _file_digest(source), "size": source.stat().st_size})
    records.sort(key=lambda item: item["path"])
    if not records and not required:
        return [], None
    return records, _records_digest(records)


def materialize_snapshot(
    destination: str | Path,
    *,
    source_path: str | Path,
    skills_path: str | Path | None,
    source_inputs: Sequence[str],
    skill_inputs: Sequence[str],
    task_inputs: Sequence[str] = (),
) -> dict[str, Any]:
    """Copy only declared source, skill, and task files into an isolated directory."""
    if source_path is None:
        raise SnapshotError("source_path is required")
    target = Path(destination)
    if target.exists():
        if target.is_symlink() or not target.is_dir() or any(target.iterdir()):
            raise SnapshotError(f"snapshot destination must be a new empty directory: {target}")
    else:
        target.mkdir(parents=True)
    source_root = _root(source_path, "source_path")
    skill_root = _root(skills_path, "skills_path")
    source_records, source_digest = _copy_category(
        target, "source", source_root, source_inputs, required=True
    )
    skill_records, skill_digest = _copy_category(
        target, "skills", skill_root, skill_inputs, required=False
    )
    task_records, task_digest = _copy_category(
        target, "task", source_root, task_inputs, required=True
    )
    materialization = {
        "format": "snapshot-v1",
        "source_digest": source_digest,
        "skill_digest": skill_digest,
        "task_digest": task_digest,
        "inputs": {
            "source": source_records,
            "skills": skill_records,
            "task": task_records,
        },
    }
    return canonical_snapshot(materialization)


def materialize_manifest_snapshot(
    destination: str | Path,
    spec: dict[str, Any] | None,
    base: str | Path,
) -> dict[str, Any] | None:
    """Materialize an optional arm.snapshot manifest declaration."""
    if spec is None:
        return None
    if not isinstance(spec, dict):
        raise SnapshotError("arm.snapshot must be a mapping")
    inputs = spec.get("inputs", {})
    if not isinstance(inputs, dict):
        raise SnapshotError("arm.snapshot.inputs must be a mapping")
    root_base = Path(base).resolve()

    def rooted(value: Any) -> Path | None:
        if value is None:
            return None
        if not isinstance(value, str) or not value:
            raise SnapshotError("snapshot roots must be non-empty paths")
        path = Path(value)
        return path if path.is_absolute() else root_base / path

    def declared(category: str) -> list[str]:
        value = inputs.get(category, [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise SnapshotError(f"arm.snapshot.inputs.{category} must be a list of strings")
        return value

    return materialize_snapshot(
        destination,
        source_path=rooted(spec.get("source_path")),
        skills_path=rooted(spec.get("skills_path")),
        source_inputs=declared("source"),
        skill_inputs=declared("skills"),
        task_inputs=declared("task"),
    )
