#!/usr/bin/env python3
"""Build a secret-scanned public bundle from private benchmark receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_workflow_benchmark.redaction import redact


CREDENTIAL_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"gh[opsu]_[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)Authorization:\s*Bearer\s+[^\s\"']+"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
)


def scrub(value: object) -> object:
    value = redact(value)
    if isinstance(value, str):
        for pattern in CREDENTIAL_PATTERNS:
            value = pattern.sub("[REDACTED_CREDENTIAL]", value)
        return value
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, dict):
        return {str(key): scrub(item) for key, item in value.items()}
    return value


def public_jsonl(source: Path, destination: Path) -> None:
    with source.open(encoding="utf-8") as reader, destination.open(
        "w", encoding="utf-8"
    ) as writer:
        for line in reader:
            if line.strip():
                writer.write(json.dumps(scrub(json.loads(line)), ensure_ascii=False))
                writer.write("\n")


def public_transcript(source: Path, destination: Path) -> None:
    with tempfile.TemporaryDirectory() as directory:
        extracted = Path(directory)
        subprocess.run(
            ["tar", "--zstd", "-xf", str(source), "-C", str(extracted)],
            check=True,
        )
        public_jsonl(extracted / "transcripts.jsonl", extracted / "public.jsonl")
        (extracted / "public.jsonl").replace(extracted / "transcripts.jsonl")
        manifest = extracted / "campaign-manifest.json"
        manifest.write_text(
            json.dumps(scrub(json.loads(manifest.read_text())), ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
        subprocess.run(
            [
                "tar",
                "--zstd",
                "-cf",
                str(destination),
                "-C",
                str(extracted),
                "campaign-manifest.json",
                "transcripts.jsonl",
            ],
            check=True,
        )


def add_tree(archive: tarfile.TarFile, root: Path) -> None:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            archive.add(path, arcname=path.relative_to(root))


def assert_secret_free(path: Path) -> None:
    data = subprocess.run(
        ["tar", "--zstd", "-xOf", str(path)], check=True, capture_output=True
    ).stdout.decode("utf-8", errors="replace")
    for pattern in CREDENTIAL_PATTERNS:
        if pattern.search(data):
            raise SystemExit(f"credential-shaped value remains in {path.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as directory:
        stage = Path(directory) / "business-first-10-evidence"
        stage.mkdir()
        for shard in sorted(source.iterdir()):
            if not shard.is_dir():
                continue
            target = stage / shard.name
            target.mkdir()
            public_jsonl(shard / "results.jsonl", target / "results.jsonl")
            summary = scrub(json.loads((shard / "summary.json").read_text()))
            (target / "summary.json").write_text(
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            archive = target / "campaign-transcripts.tar.zst"
            public_transcript(shard / archive.name, archive)
            assert_secret_free(archive)
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            (target / "campaign-transcripts.sha256").write_text(
                f"{digest}  {archive.name}\n", encoding="utf-8"
            )

        uncompressed = output.with_suffix("")
        with tarfile.open(uncompressed, "w") as archive:
            add_tree(archive, stage)
        subprocess.run(["zstd", "-q", "-f", str(uncompressed), "-o", str(output)], check=True)
        uncompressed.unlink()

    sha = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum = output.with_name(output.name.removesuffix(".tar.zst") + ".sha256")
    checksum.write_text(
        f"{sha}  {output.name}\n", encoding="utf-8"
    )
    print(f"{output}\nsha256={sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
