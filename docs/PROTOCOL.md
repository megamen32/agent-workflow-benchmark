# Benchmark protocol

## Principle

The unit being compared is `workflow + harness + declared model topology`, not a
model in isolation. A topology is an ordered list of one to three model tiers:

```text
smart mentor → medium Lead → cheap Worker
```

The list is descriptive, not prescriptive:

- one model is valid even when it makes no child calls;
- two levels are valid, such as smart Lead → cheap Worker;
- three levels are valid, such as smart Adviser → medium Lead → cheap Worker.

Do not add a Worker to a one-model workflow, add a third tier to a two-tier
workflow, or add parallel lanes to a sequential workflow. The connections
between model levels belong to the workflow. Sequential connections are still
valid and are represented as `mode: sequential` with
`max_concurrent_children: 1`; parallelism is measured separately from model
topology with that limit and the actual child count. Optional
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

## Reproducibility boundary

The adapter, harness CLI, runtime dependencies, and verifier execute inside a
Docker image pinned by immutable digest. A manifest without
`environment.container_runtime.engine: docker`, `pull_policy: never`, and an
arm-level `container.image` ending in `@sha256:<64 hex>` is invalid.

The host runner is deliberately thin: it creates the isolated run directory,
mounts `/workspace` and `/artifacts`, starts the pinned image, and collects the
receipt. It must not execute the agent or acceptance command directly on the
host, silently pull a mutable tag, or reuse a host home/configuration. The
container image, digest, platform, network mode, command, manifest hash, and
Docker version are recorded in the run receipt.

## Ranking priorities

Quality and price are the primary dimensions. Report quality as pass rate,
successful-task count, and failure categories. Report price as total effective
cost and cost per successful task. If successful-task count is zero, cost per
success is not a number and must not be used to rank that workflow; its spend is
still reported separately.

Wall-clock is a secondary dimension: useful when the user is waiting, irrelevant
when the user is away and completion/cost are the real concerns. Input/output/
total tokens are diagnostics only. Token count without a price basis is not a
cost ranking.

Never declare a workflow the winner by hiding a quality loss inside a cheaper
score, or a cost loss inside a higher pass rate. When quality and price conflict,
publish both axes and the Pareto frontier. An aggregate score is allowed only as
an explicitly secondary, user-selected view with its weights published.

The raw dimensions remain authoritative.

## Scenario tracks

Do not merge different kinds of evidence into one quality number:

- `product_outcome` — complex bug fixes, features, refactors, integration and
  user-visible behavior checked by hidden/deterministic product tests;
- `workflow_guard` — verification order, honest completion, unnecessary fan-out,
  scope/cost discipline, and other process invariants;
- `hybrid` — a product task with an explicit workflow invariant.

The current five-scenario L0/L1 pilot is `workflow_guard`. Its 80% versus 60%
result says that L0 was more reliable on these process guards; it is not a
claim that L0 is generally better at difficult engineering tasks. A publication
must show track-level rates separately. In particular, a rule such as
"verify a claimed passing test before committing" measures trust and evidence
ordering. It is not a universal ban on every commit before every test, and it
must not be mislabeled as a complete TDD or product-quality benchmark.

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
- raw and normalized result locations;
- the single campaign transcript archive, its compression format, SHA-256, and
  public release-asset URL;
- total effective cost and cost per successful task; the latter is `null` when
  the workflow solved zero tasks;

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

## Transcript publication

Every published campaign includes one archive containing exactly:

```text
campaign-manifest.json   # verdicts, models, timing, cost, hashes, redaction
transcripts.jsonl        # all run dialogs concatenated in stable order
```

Compress the whole combined JSONL stream with `zstd` or `gzip`; do not create a
separate compressed file for every run. Keep the archive SHA-256 in git and
publish the archive as one GitHub Release asset so cloning the benchmark does
not download every run.

Before publication, remove API keys, bearer tokens, cookies, environment
values, private hostnames, private paths, and unapproved user content. A redacted
transcript must retain event order, role/model metadata, tool calls, tool
results, timing, token/cost fields, and the final filesystem/check evidence.
