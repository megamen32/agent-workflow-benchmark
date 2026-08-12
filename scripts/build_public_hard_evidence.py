#!/usr/bin/env python3
"""Build a redacted public evidence bundle for the sanitized hard campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_public_evidence import CREDENTIAL_PATTERNS, scrub


PUBLIC_NAMES = {
    "agent-receipt.json",
    "campaign-launcher.log",
    "eval.sh",
    "events.jsonl",
    "patch.diff",
    "prediction.jsonl",
    "report.json",
    "run_instance.log",
    "stderr.log",
    "test_output.txt",
}


def write_scrubbed(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix == ".jsonl":
        with source.open(encoding="utf-8") as reader, destination.open(
            "w", encoding="utf-8"
        ) as writer:
            for line in reader:
                if line.strip():
                    writer.write(
                        json.dumps(scrub(json.loads(line)), ensure_ascii=False) + "\n"
                    )
        return
    if source.suffix == ".json":
        value = scrub(json.loads(source.read_text(encoding="utf-8")))
        destination.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return
    destination.write_text(
        str(scrub(source.read_text(encoding="utf-8", errors="replace"))),
        encoding="utf-8",
    )


def included(path: Path, source: Path) -> bool:
    if path.name in PUBLIC_NAMES:
        return True
    # The official harness writes one top-level aggregate grader report per cell.
    return path.suffix == ".json" and path.parent.parent.parent == source


def add_tree(archive: tarfile.TarFile, root: Path) -> None:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            archive.add(path, arcname=path.relative_to(root))


def assert_secret_free(root: Path) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        data = path.read_text(encoding="utf-8", errors="replace")
        for pattern in CREDENTIAL_PATTERNS:
            if pattern.search(data):
                raise SystemExit(f"credential-shaped value remains in {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    repo = Path(__file__).resolve().parents[1]
    output.parent.mkdir(parents=True, exist_ok=True)

    receipts = sorted(source.glob("*/*/agent-receipt.json"))
    if len(receipts) != 40:
        raise SystemExit(f"expected 40 cells, found {len(receipts)}")
    if not all(json.loads(path.read_text())["git_history_sanitized"] for path in receipts):
        raise SystemExit("refusing to publish a campaign with unsanitized Git history")

    with tempfile.TemporaryDirectory() as directory:
        stage = Path(directory) / "hard-swebench-verified-10-evidence"
        cells = stage / "cells"
        copied = 0
        for path in sorted(source.rglob("*")):
            if path.is_file() and included(path, source):
                write_scrubbed(path, cells / path.relative_to(source))
                copied += 1

        subprocess.run(
            [
                sys.executable,
                str(repo / "scripts/summarize_hard_swebench.py"),
                str(source),
                "--output",
                str(stage / "summary.json"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        write_scrubbed(
            repo / "configs/hard-swebench-verified-10.json", stage / "campaign-config.json"
        )
        write_scrubbed(
            repo / "docs/RESULTS-HARD-SWEBENCH-VERIFIED-10-2026-08-12.md",
            stage / "ARTICLE-RU.md",
        )
        (stage / "README.md").write_text(
            "# Hard SWE-bench Verified 10 evidence\n\n"
            "Public, credential-redacted evidence for 40 final cells: 10 frozen "
            "SWE-bench Verified issues × control, LHC, Superpowers and GSD.\n\n"
            "Included: all agent event streams, predictions and patches, receipts, "
            "official grader reports, evaluation scripts and grader logs. The host-only "
            "frozen dataset snapshot and authentication mounts are intentionally absent.\n\n"
            "Every receipt must state `git_history_sanitized: true`. The earlier "
            "pre-sanitization calibration campaign is invalid and is not in this bundle.\n",
            encoding="utf-8",
        )

        manifest = []
        for path in sorted(stage.rglob("*")):
            if path.is_file() and path.name != "MANIFEST.json":
                manifest.append(
                    {
                        "path": str(path.relative_to(stage)),
                        "bytes": path.stat().st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    }
                )
        (stage / "MANIFEST.json").write_text(
            json.dumps(
                {
                    "campaign": "hard-swebench-verified-10-sanitized",
                    "cells": 40,
                    "copied_result_files": copied,
                    "files": manifest,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        assert_secret_free(stage)

        uncompressed = output.with_suffix("")
        with tarfile.open(uncompressed, "w") as archive:
            add_tree(archive, stage)
        subprocess.run(
            ["zstd", "-q", "-f", str(uncompressed), "-o", str(output)], check=True
        )
        uncompressed.unlink()

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum = output.with_name(output.name.removesuffix(".tar.zst") + ".sha256")
    checksum.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    print(f"{output}\nfiles={copied}\nsha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
