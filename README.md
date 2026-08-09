# Agent Workflow Benchmark

> Compare AI coding workflows by the result they deliver, the time they take,
> and the money and tokens they consume.

Most agent benchmarks compare models. This project compares the workflow around
the model: lead orchestration, delegation, tool use, verification, and the
worker model selected by the lead. Independent judgement roles are not silently
made cheap: Adviser, Overseer, and Critic remain on the expensive tier.

## The core experiment

Each workflow runs the same scenario with the same fixture and its own native
orchestration. A normal campaign records five explicit model roles:

```text
Adviser (expensive, fixed) ─┐
Overseer (expensive, fixed) ├→ Lead model → Worker model
Critic (expensive, fixed) ──┘
                             oc/gpt-5.6-luna → oc/gpt-5.4-mini
                             oc/minimax-m3  → oc/minimax-m2.7
```

The Adviser, Overseer, and Critic are separate expensive planning/audit/review
roles and are held constant between arms. The lead is allowed to choose and use
its worker according to the workflow under test. We do not flatten this into
one fixed-model comparison.

## What we report

The benchmark keeps separate dimensions:

- quality: scenario pass rate and failure categories;
- time: wall-clock and critical-path time;
- cost: provider cost and tokens per solved scenario.

There is no mandatory single winner. An optional aggregate is clearly labelled
as a convenience ranking, because two-criteria optimisation has no universally
correct answer.

## Status

This repository contains the public protocol and runner components. The first
campaign is an L0/L1 comparison of a workflow before and after a skills
migration. It is intentionally reproducible without publishing credentials,
private endpoints, or raw private transcripts.

## Quick start

```bash
python3 scripts/summarize_results.py results.jsonl
```

The input is newline-delimited JSON. See [the protocol](docs/PROTOCOL.md) and
[the campaign configuration](configs/campaign.yaml).

## Design

- [Benchmark protocol](docs/PROTOCOL.md)
- [Campaign configuration](configs/campaign.yaml)
- [Result schema](docs/RESULT_SCHEMA.md)

## License

MIT. See [LICENSE](LICENSE).
