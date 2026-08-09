# Agent Workflow Benchmark

> Compare AI coding workflows by the result they deliver, the time they take,
> and the money and tokens they consume.

Most agent benchmarks compare models. This project compares the workflow around
the model: orchestration, delegation, tool use, verification, and the model
selection policy. A workflow may have no delegation, one model, two tiers, or
three tiers. The benchmark never adds a child, a parallel lane, or a judgement
role that the workflow does not declare.

## The core experiment

Each workflow runs the same scenario with the same fixture and its own native
orchestration. A campaign records an ordered topology of zero to three model
tiers. A three-tier workflow may look like this:

```text
smart mentor/adviser → medium Lead → cheap Worker
```

Two-tier and one-tier workflows remain exactly that. A workflow with zero
parallelism remains sequential; parallelism is a separate measured property,
not a required topology level. Optional roles such as Adviser, Overseer,
Critic, Reviewer, or Tester are recorded only when the workflow actually uses
them.

If a workflow documents model selection, the harness follows that policy. If it
does not, the campaign chooses the strongest available model in the selected
test budget and records the fallback. Cheap and normal campaigns are separate
profiles, so a cheap pilot can later be repeated with normal models without
changing the workflow definition.

## What we report

The benchmark keeps separate dimensions:

- quality: scenario pass rate and failure categories;
- time: wall-clock and critical-path time;
- cost: effective provider cost and tokens per solved scenario.

Pricing is pinned to a dated snapshot. `models.dev` is a useful open catalog and
list-price fallback, but a zero or missing price is not treated as free: for a
subscription, relay, or local model the effective cost is `null` unless the
provider/account billing basis is known.

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
