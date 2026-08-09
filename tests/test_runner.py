from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agent_workflow_benchmark.adapters.codex import CodexAdapter
from agent_workflow_benchmark.adapters.opencode import OpenCodeAdapter
from agent_workflow_benchmark.manifest import ManifestError, load_manifest, manifest_sha256
from agent_workflow_benchmark.redaction import redact_text
from agent_workflow_benchmark.runner import extract_usage, run_campaign
from agent_workflow_benchmark.snapshot import SnapshotError, materialize_snapshot, snapshot_sha256


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

    def test_snapshot_mounts_are_read_only_and_use_materialized_categories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = root / "run"
            (run_dir / "snapshot-inputs/source").mkdir(parents=True)
            arm = {
                "harness": "codex",
                "container": {
                    "image": "example/test@" + "a" * 64,
                    "digest": DIGEST,
                    "network": "none",
                },
                "snapshot": {
                    "mounts": [{"category": "source", "target": "/workflow/current"}],
                },
            }
            command = CodexAdapter(arm).docker_command(["codex"], root / "workspace", run_dir, {})
            self.assertIn(
                f"{(run_dir / 'snapshot-inputs/source').resolve()}:/workflow/current:ro",
                command,
            )

    def test_snapshot_materializer_copies_only_declared_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "l0"
            skills = root / "l1-skills"
            source.joinpath("agents").mkdir(parents=True)
            source.joinpath("tasks").mkdir()
            skills.joinpath("planning").mkdir(parents=True)
            source.joinpath("agents/Lead.md").write_text("lead-v1\n", encoding="utf-8")
            source.joinpath("agents/secret.md").write_text("must-not-copy\n", encoding="utf-8")
            source.joinpath("tasks/task.md").write_text("task-v1\n", encoding="utf-8")
            skills.joinpath("planning/SKILL.md").write_text("skill-v1\n", encoding="utf-8")
            output = root / "snapshot"

            receipt = materialize_snapshot(
                output,
                source_path=source,
                skills_path=skills,
                source_inputs=["agents/Lead.md"],
                skill_inputs=["planning/SKILL.md"],
                task_inputs=["tasks/task.md"],
            )

            self.assertEqual((output / "source/agents/Lead.md").read_text(encoding="utf-8"), "lead-v1\n")
            self.assertEqual((output / "skills/planning/SKILL.md").read_text(encoding="utf-8"), "skill-v1\n")
            self.assertEqual((output / "task/tasks/task.md").read_text(encoding="utf-8"), "task-v1\n")
            self.assertFalse((output / "source/agents/secret.md").exists())
            self.assertEqual([item["path"] for item in receipt["inputs"]["source"]], ["agents/Lead.md"])
            self.assertTrue(receipt["source_digest"].startswith("sha256:"))
            self.assertTrue(receipt["skill_digest"].startswith("sha256:"))
            self.assertTrue(receipt["task_digest"].startswith("sha256:"))

    def test_snapshot_materializer_digest_changes_when_declared_input_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "l0"
            source.mkdir()
            (source / "input.txt").write_text("v1\n", encoding="utf-8")
            first = materialize_snapshot(
                root / "first",
                source_path=source,
                skills_path=None,
                source_inputs=["input.txt"],
                skill_inputs=[],
            )
            (source / "input.txt").write_text("v2\n", encoding="utf-8")
            second = materialize_snapshot(
                root / "second",
                source_path=source,
                skills_path=None,
                source_inputs=["input.txt"],
                skill_inputs=[],
            )
            self.assertNotEqual(first["source_digest"], second["source_digest"])

    def test_snapshot_materializer_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "l0"
            source.mkdir()
            (root / "outside.txt").write_text("outside\n", encoding="utf-8")
            with self.assertRaises(SnapshotError):
                materialize_snapshot(
                    root / "snapshot",
                    source_path=source,
                    skills_path=None,
                    source_inputs=["../outside.txt"],
                    skill_inputs=[],
                )

    def test_snapshot_digests_differ_for_l0_and_l1_inputs(self) -> None:
        arm0 = {
            "id": "lhc-l0",
            "container": {"digest": "sha256:" + "1" * 64},
            "topology": {"levels": [{"id": "lead", "harness": "codex", "model": "terra", "roles": ["lead"]}]},
            "source_commit": "44da5d9",
            "skill_digest": None,
            "task_digest": "task-l0",
        }
        arm1 = {
            "id": "lhc-l1",
            "container": {"digest": "sha256:" + "2" * 64},
            "topology": {"levels": [{"id": "lead", "harness": "codex", "model": "terra", "roles": ["lead"]}]},
            "source_commit": "88bb77c",
            "skill_digest": "skills-l1",
            "task_digest": "task-l1",
        }
        base = {
            "manifest_sha256": "m" * 64,
            "scenario": {"id": "scenario"},
            "attempt": 1,
            "receipt": {"status": "pass"},
            "transcript_archive": {"name": "campaign-transcripts.tar.zst", "redacted": True},
            "cumulative_effective_cost_usd": 0.0,
            "budget_stop_effective_cost_usd": 5.0,
        }
        snap0 = {
            **base,
            "arm": arm0["id"],
            "source_commit": arm0["source_commit"],
            "skill_digest": arm0["skill_digest"],
            "task_digest": arm0["task_digest"],
            "docker_image_digest": arm0["container"]["digest"],
            "model_stack": arm0["topology"]["levels"],
        }
        snap1 = {
            **base,
            "arm": arm1["id"],
            "source_commit": arm1["source_commit"],
            "skill_digest": arm1["skill_digest"],
            "task_digest": arm1["task_digest"],
            "docker_image_digest": arm1["container"]["digest"],
            "model_stack": arm1["topology"]["levels"],
        }
        self.assertNotEqual(snapshot_sha256(snap0), snapshot_sha256(snap1))

    def test_budget_gate_stops_before_next_cell_after_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_source = Path(directory) / "snapshot-source"
            snapshot_skills = Path(directory) / "snapshot-skills"
            snapshot_source.mkdir()
            snapshot_skills.mkdir()
            (snapshot_source / "source.txt").write_text("source\n", encoding="utf-8")
            (snapshot_source / "task.md").write_text("task\n", encoding="utf-8")
            (snapshot_skills / "SKILL.md").write_text("skill\n", encoding="utf-8")
            manifest_path = Path(directory) / "manifest.yaml"
            manifest_path.write_text(
                """
manifest_version: 1
campaign:
  name: budget-stop
  budget_stop_effective_cost_usd: 5.0
environment:
  timeout_seconds: 5
  container_runtime:
    engine: docker
    pull_policy: never
arms:
  - id: arm
    harness: codex
    source_commit: abc
    skill_digest: skill
    task_digest: task
    snapshot:
      source_path: SNAPSHOT_SOURCE
      skills_path: SNAPSHOT_SKILLS
      inputs:
        source: [source.txt]
        skills: [SKILL.md]
        task: [task.md]
    container:
      image: example/test@sha256:{digest}
      digest: sha256:{digest}
    topology:
      levels:
        - id: lead
          harness: codex
          model: model
scenarios:
  - id: first
    prompt: first
    acceptance:
      command: [sh, -lc, true]
  - id: second
    prompt: second
    acceptance:
      command: [sh, -lc, true]
""".format(digest="3" * 64).replace("SNAPSHOT_SOURCE", str(snapshot_source)).replace("SNAPSHOT_SKILLS", str(snapshot_skills)),
                encoding="utf-8",
            )
            output_dir = Path(directory) / "out"

            class FakeAdapter:
                def __init__(self, arm):
                    self.arm = arm

                def container(self):
                    return self.arm["container"]

                def run(self, **kwargs):
                    return mock.Mock(
                        returncode=0,
                        timed_out=False,
                        events=[{"usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}, "cost_usd": 5.1}],
                        raw_stdout='{"usage":{"prompt_tokens":1,"completion_tokens":1,"total_tokens":2},"cost_usd":5.1}\n',
                        stderr="",
                        wall_clock_seconds=0.1,
                        session_id="session-1",
                        container_metadata={"engine_version": "test"},
                    )

                def run_command(self, *args, **kwargs):
                    return 0, "", False

            with mock.patch("agent_workflow_benchmark.runner._adapter", side_effect=lambda arm: FakeAdapter(arm)):
                summary = run_campaign(manifest_path, output_dir)

            self.assertTrue(summary["budget_stop_triggered"])
            self.assertGreater(summary["cumulative_effective_cost_usd"], 5.0)
            results = (output_dir / "results.jsonl").read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(results), 1)
            self.assertTrue((output_dir / "arm" / "first" / "attempt-1" / "snapshot.json").exists())
            receipt = json.loads(results[0])
            self.assertTrue(receipt["snapshot"]["source_digest"].startswith("sha256:"))
            self.assertTrue(receipt["snapshot"]["skill_digest"].startswith("sha256:"))
            self.assertTrue(receipt["snapshot"]["task_digest"].startswith("sha256:"))
            self.assertIn("arm", summary["snapshot_materializations"])


def load_manifest_from_text(value: str):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "manifest.yaml"
        path.write_text(value, encoding="utf-8")
        return load_manifest(path)


if __name__ == "__main__":
    unittest.main()
