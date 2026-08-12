# Agent Workflow Benchmark

This project measures the thing model benchmarks hide: whether a complete
workflow turns the same capable model stack into a better product result.

## Latest result

**Hard SWE-bench Verified: 10 real issues × 4 workflows.** GSD resolved 2/10;
plain Codex, LHC, and Superpowers resolved 1/10 each. The difference is too
small for a universal winner claim, but this round measures real hidden-test
quality rather than only workflow overhead.

- [Hard quality benchmark: method, sanitation and per-task results](docs/RESULTS-HARD-SWEBENCH-VERIFIED-10-2026-08-12.md)
- [Frozen hard campaign](configs/hard-swebench-verified-10.json)
- [Easy 10/10 round: workflow-overhead baseline](docs/BUSINESS-FIRST-WORKFLOW-BENCHMARK-RU.md)

| Workflow revision | Product quality | Effective cost | Time | Status |
|---|---:|---:|---:|---|
| [L0](https://github.com/megamen32/LastHumanCommit/releases/tag/lhc-l0-20260809) — current procedural workflow | **1/1 · 100%** | unknown · subscription route | **64.70s** | pilot complete |
| [L1](https://github.com/megamen32/LastHumanCommit/releases/tag/lhc-l1-20260809) — procedural features exposed as skills | **1/1 · 100%** | unknown · subscription route | **79.34s** | pilot complete |

The comparison uses one declared Codex stack for both revisions:
`gpt-5.6-terra` mentor → `gpt-5.6-luna` Lead → `gpt-5.4-mini` Worker. The
workflow decides how those levels cooperate; the benchmark does not add
parallelism or agents that a workflow does not have.

This is one product-outcome pilot, not a universal winner claim. Quality tied;
L0 was 18.4% faster on this task. The provider route returned no billable
charge, so price is reported as unknown rather than fabricated; the full
receipt and redacted dialogue are in
[`results/lhc-skills-product-outcome-20260809/`](results/lhc-skills-product-outcome-20260809/).

## Why this exists

Model quality is only one input. The harness, rules, delegation, verification,
and human gates decide whether a request is completed, what it costs, and how
long it takes. We therefore report three dimensions separately:

- product quality: did the user-visible acceptance criteria pass?
- effective price: what did the provider actually charge? Missing or subscription
  pricing is reported as unknown, never invented;
- wall-clock time: useful when speed matters, but not merged into quality or
  price.

An optional aggregate may be shown only as a clearly labelled convenience;
quality, price, and time are not universally orderable.

## Reproducibility

Every campaign pins the workflow revision, task-fixture digest, model topology,
Docker image digest, and runner version. Each run keeps one redacted compressed
archive containing the complete dialogue, receipts, acceptance output, and
manifest. The archive is published as a release asset; its SHA-256 and manifest
remain in git.

The runner stops before launching the next cell once cumulative effective cost
exceeds `$5.00`, pending an explicit decision to continue.

## Run locally

```bash
python3 -m pip install -e .
python3 scripts/run_campaign.py configs/manifest.docker-smoke.yaml --output results/smoke
```

The smoke campaign is deterministic and uses a locally cached, digest-pinned
Node image. It validates Docker isolation, receipts, acceptance checks, budget
accounting, and transcript archiving; it is not a model-quality result.

The product campaign is intentionally not runnable until its Codex image is
published under an immutable digest and L1 is frozen:

```bash
python3 scripts/run_campaign.py configs/campaign.yaml --dry-run
```

## Benchmark sources

- [Quorum / Superpowers Evals](https://github.com/prime-radiant-inc/superpowers-evals)
  supplies behavioral scenarios and deterministic receipts.
- [AI Workflow Benchmark](https://github.com/xmpuspus/ai-workflow-benchmark)
  supplies a separate real-repository comparison methodology.
- [SkillsBench](https://github.com/benchflow-ai/skillsbench) checks whether
  skills help when a workflow exposes reusable procedures.

These sources are reference material, not a claim that their tasks alone
measure product quality. This repository also keeps its own product-outcome
tasks and publishes every full transcript.

## Documentation

- [Protocol](docs/PROTOCOL.md)
- [Runner contract](docs/RUNNER.md)
- [Result schema](docs/RESULT_SCHEMA.md)
- [Benchmark rationale](docs/WHY-BENCHMARKS.md)
- [Research catalogue](research/README.md)

MIT — [LICENSE](LICENSE).
