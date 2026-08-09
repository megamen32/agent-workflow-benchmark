from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_workflow_benchmark.adapters.codex import CodexAdapter
from agent_workflow_benchmark.adapters.opencode import OpenCodeAdapter
from agent_workflow_benchmark.manifest import ManifestError, load_manifest, manifest_sha256
from agent_workflow_benchmark.redaction import redact_text
from agent_workflow_benchmark.runner import extract_usage


DIGEST = "sha256:" + "a" * 64


def manifest(harness: str = "codex") -> str:
    return f"""
manifest_version: 1
campaign:
  name: test
environment:
  timeout_seconds: 30
  container_runtime:
    engine: docker
    pull_policy: never
arms:
  - id: arm
    harness: {harness}
    container:
      image: example/test@{DIGEST}
      digest: {DIGEST}
    topology:
      levels:
        - id: lead
          harness: {harness}
          model: test-model
scenarios:
  - id: scenario
    prompt: do it
    acceptance:
      command: [sh, -lc, test]
"""


class RunnerContractTests(unittest.TestCase):
    def test_manifest_requires_pinned_container_and_hashes_canonically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.yaml"
            path.write_text(manifest(), encoding="utf-8")
            loaded, _ = load_manifest(path)
            self.assertEqual(loaded["arms"][0]["container"]["digest"], DIGEST)
            self.assertEqual(len(manifest_sha256(loaded)), 64)

    def test_manifest_rejects_mutable_container_tag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.yaml"
            path.write_text(manifest().replace(f"example/test@{DIGEST}", "example/test:latest"), encoding="utf-8")
            with self.assertRaises(ManifestError):
                load_manifest(path)

    def test_codex_and_opencode_commands_are_inner_container_commands(self) -> None:
        arm = load_manifest_from_text(manifest("codex"))[0]["arms"][0]
        codex = CodexAdapter(arm).command("hello", Path("/host/workspace"), "model")
        self.assertIn("/workspace", codex)
        self.assertNotIn("/host/workspace", codex)
        arm = load_manifest_from_text(manifest("opencode"))[0]["arms"][0]
        opencode = OpenCodeAdapter(arm).command("hello", Path("/host/workspace"), "model")
        self.assertIn("/workspace", opencode)
        self.assertNotIn("/host/workspace", opencode)
        docker = OpenCodeAdapter(arm | {"harness": "opencode", "container": {"image": "example/test@" + "b" * 64, "digest": "sha256:" + "b" * 64}}).docker_command(
            opencode, Path("/host/workspace"), Path("/host/run"), {"OPENAI_API_KEY": "secret"}
        )
        self.assertIn("--pull", docker)
        self.assertIn("never", docker)
        self.assertIn("example/test@" + "b" * 64, docker)
        self.assertNotIn("secret", docker)

    def test_usage_and_redaction_are_not_zero_filled(self) -> None:
        usage = extract_usage([{"usage": {"prompt_tokens": 10, "completion_tokens": 7, "total_tokens": 17}, "cost": 0.12}])
        self.assertEqual(usage["total_tokens"], 17)
        self.assertEqual(usage["cost_usd"], 0.12)
        self.assertIn("[REDACTED]", redact_text("Authorization: Bearer secret-token"))


def load_manifest_from_text(value: str):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "manifest.yaml"
        path.write_text(value, encoding="utf-8")
        return load_manifest(path)


if __name__ == "__main__":
    unittest.main()
