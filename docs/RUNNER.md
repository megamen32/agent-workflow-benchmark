# Unified Docker runner

The executable boundary is `scripts/run_campaign.py`. The input is one YAML
manifest containing the campaign, arms, scenarios, fixtures, acceptance
commands, topology, pricing policy, and pinned containers.

## Mandatory reproducibility fields

Every manifest must declare:

```yaml
environment:
  container_runtime:
    engine: docker
    pull_policy: never

arms:
  - harness: codex  # or opencode
    container:
      image: registry.example/harness:version@sha256:<64-hex-digest>
      digest: sha256:<same-64-hex-digest>
```

The loader rejects mutable tags, missing digests, mismatched digests, missing
Docker runtime declaration, mixed Codex/OpenCode levels inside one arm, and
topologies with more than three levels.

Before each attempt the runner proves that the exact image digest exists in the
local Docker cache. It uses `docker run --pull never`, mounts only the isolated
`/workspace` and `/artifacts`, defaults to `--network none`, and records the
Docker Engine version plus image `RepoDigests` in `container-preflight.json`.
The agent and acceptance verifier both run in that same image. Nothing from the
host harness binary, host home, or host-side verifier is used.

## Run modes

```bash
python3 scripts/run_campaign.py configs/manifest.example.yaml --dry-run
python3 scripts/run_campaign.py configs/manifest.docker-smoke.yaml \
  --output /tmp/agent-workflow-smoke
```

The smoke manifest uses a real locally cached digest and a Node fixture command;
it verifies container isolation and receipt/archive behavior, not model quality.

## Outputs

Each campaign output contains `results.jsonl`, `summary.json`, one
`campaign-transcripts.tar.zst`, and its SHA-256. The archive has exactly two
members: `campaign-manifest.json` and `transcripts.jsonl`. The transcript starts
with the user prompt, then preserves JSONL harness events in order. API keys,
Bearer values, cookies, passwords, and other configured secret patterns are
redacted before local event files and publication artifacts are written.

Quality, total effective cost, cost per successful task, and wall-clock are
reported separately. Tokens remain diagnostic. If there are zero successful
tasks, `cost_per_success_usd` is `null`, never zero.

The image digest makes the adapter/harness environment reproducible. Exact LLM
output additionally depends on the declared provider route and its inference
behavior; campaigns must record model ID, endpoint class, pricing basis, and
repetition seed, and should publish the full transcript for audit.

For a local-only image that has not been pushed to a registry, a manifest may
explicitly set `allow_local_image_id: true` and provide the exact Docker image
content ID in both `digest` and `image_id`. The runner then verifies `.Id` before
execution and records `verification: local-image-id`. This mode cannot pull the
image and is not a substitute for a registry digest in a public release.

## Benchmark source snapshots

An arm may declare benchmark-only source inputs. Before that cell starts, the
runner copies only the listed files into the isolated `snapshot-inputs/` tree;
it rejects absolute paths, `..` traversal, missing files, directories, and
symlinked inputs. `task` inputs are resolved under `source_path`.

```yaml
arms:
  - id: lhc-l1
    snapshot:
      source_path: /path/to/l0-source
      skills_path: /path/to/l1-skills
      inputs:
        source: [common/agents/Worker.md]
        skills: [planning/SKILL.md]
        task: [.agents/tasks/work-benchmark.md]
```

The cell receipt records deterministic `source_digest`, `skill_digest`, and
`task_digest`, the exact relative file list and file digests, plus the pinned
source commit, model stack, Docker digest, redacted transcript archive, and
effective-cost stop state. The campaign manifest inside the archive repeats
one path-free materialization record per arm.

If `mounts` are declared, only the corresponding materialized category is
mounted read-only at the declared container target. The runner copies
`AGENTS.md` and `CLAUDE.md` from the source snapshot into the isolated task
workspace, while the read-only mount preserves any absolute role paths used by
the workflow package. A scenario fixture cannot silently replace those marker
files.

Codex auth is configured separately through an `auth.host_env` variable. The
runner resolves that host path only at execution time, mounts it read-only at
`auth.container_path`, and never serializes the host path or credential into a
manifest or transcript.

The LHC campaign passes Codex's sandbox bypass only inside the pinned Docker
container. Docker is the isolation boundary for this benchmark; the flag is
not a host-side default and is not enabled by the generic adapter.
