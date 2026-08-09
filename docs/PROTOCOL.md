# Benchmark protocol

## Principle

The unit being compared is `workflow + harness + model topology`, not a model
in isolation. The topology records five roles:

```text
Adviser (expensive, fixed) ─┐
Overseer (expensive, fixed) ├→ Lead → Worker
Critic (expensive, fixed) ──┘
```

Adviser, Overseer, and Critic are held constant between arms. Lead and Worker
are the arm's declared pair. A lead may delegate to a worker, and that
delegation is part of the workflow being measured.

## Matched run

For every arm and scenario:

1. use the same scenario text, fixture, acceptance checks, and timeout;
2. use a clean isolated home and workspace;
3. inject only the workflow under test and its declared model topology;
4. randomise arm order where practical;
5. preserve the complete raw receipt and normalized result;
6. discard only infrastructure-invalid runs, recording why and whether a
   matched replacement was purchased.

The workflow may use its normal child-agent mechanism. The harness must record
all five role model IDs rather than silently replacing any of them. A harness
adapter must expose the worker-model override to the workflow;
passing only one model to the outer CLI is not evidence that the topology was
actually exercised.

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
- lead and worker model IDs;
- adviser, overseer, and critic model IDs and proof that they were held
  constant;
- scenario and fixture revisions;
- provider route and pricing snapshot, without secrets;
- repetition count and order randomisation seed;
- invalid-run and replacement policy;
- raw and normalized result locations.

## Security boundary

Credentials are supplied at runtime. Public configuration may contain model
aliases and endpoint names, but never API keys, bearer tokens, private host
paths, or raw user transcripts.
