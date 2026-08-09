# Benchmark protocol

## Principle

The unit being compared is `workflow + harness + declared model topology`, not a
model in isolation. A topology is an ordered list of zero to three model tiers:

```text
smart mentor → medium Lead → cheap Worker
```

The list is descriptive, not prescriptive:

- zero child/delegation levels are valid;
- one model level is valid;
- two levels are valid, such as smart Lead → cheap Worker;
- three levels are valid, such as smart Adviser → medium Lead → cheap Worker.

Do not add a Worker to a one-model workflow, add a third tier to a two-tier
workflow, or add parallel lanes to a sequential workflow. Sequential
delegation is still valid and is represented as `mode: sequential` with
`max_concurrent_children: 1`; parallelism is measured separately from topology
with that limit and the actual child count. Optional
roles (Adviser, Overseer, Critic, Reviewer, Tester) are declared only when the
workflow invokes them.

If the workflow has an explicit model-selection rule, use it. Otherwise use the
best available model inside the campaign's declared budget profile and record
that fallback. The cheap profile is a pilot, not a claim about normal-model
production quality.

## Matched run

For every arm and scenario:

1. use the same scenario text, fixture, acceptance checks, and timeout;
2. use a clean isolated home and workspace;
3. inject only the workflow under test and its declared model topology;
4. randomise arm order where practical;
5. preserve the complete raw receipt and normalized result;
6. discard only infrastructure-invalid runs, recording why and whether a
   matched replacement was purchased.

The workflow may use its normal child-agent mechanism. The harness records every
declared tier and optional role that actually runs; absent tiers are recorded as
absent, not synthesized. A harness adapter must expose declared model overrides
when the workflow supports them. Passing only one model to an outer CLI is not
evidence that a multi-tier topology was exercised.

## Two separate result axes

Quality is reported as pass rate with failure categories. Resource efficiency is
reported independently as wall-clock, input/output/total tokens, and provider
cost. Never declare a workflow the winner by hiding a quality loss inside a
cheaper score, or a cost loss inside a higher pass rate.

An aggregate score is allowed only as an explicitly secondary, user-selected
view with its weights published. The raw dimensions remain authoritative.

## Reproducibility record

Every campaign records:

- workflow commit or release;
- harness and version;
- declared topology levels, role assignments, and model IDs;
- actual child/delegation count and parallelism limit;
- optional judgement-role IDs only when those roles run;
- scenario and fixture revisions;
- provider route and dated pricing snapshot, without secrets;
- repetition count and order randomisation seed;
- invalid-run and replacement policy;
- raw and normalized result locations.

## Security boundary

Credentials are supplied at runtime. Public configuration may contain model
aliases and endpoint names, but never API keys, bearer tokens, private host
paths, or raw user transcripts.

## Pricing precedence

Record the highest-authority available basis:

1. provider invoice or account-effective cost;
2. provider's official published price;
3. a dated `models.dev` snapshot;
4. `null` when the route is subscription, relay, local, or otherwise unpriced.

Never turn an absent price into `$0.00`. Report tokens even when money is
unknown.
