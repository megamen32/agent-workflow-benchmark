# Recommended evaluation method

## 1. Separate the object being compared

The same task can measure different objects depending on what is held fixed.

| Comparison | Hold fixed | Vary | Valid question |
|---|---|---|---|
| Model | task, tools, harness, limits | model | Which model solves this task better/cheaper in this wrapper? |
| Memory | model, task sequence, harness | memory backend | Does memory improve later outcomes enough to justify its cost? |
| Skill | model, task, harness, tools | skill enabled/disabled | Does this skill add outcome value, and at what cost? |
| Plugin/MCP | model, task, harness, authority | tool/plugin surface | Does this capability complete tasks that the baseline cannot, and what overhead does it add? |
| Harness/workflow | task, authority, model topology policy | orchestration/wrapper | Does this wrapper improve successful business outcomes or only process compliance? |
| Full product | task distribution and constraints | everything in the product | Which system is not worse in real use, and which is cheaper/faster? |

“Same model” is appropriate for isolating a harness effect, but it is not a
requirement for a product comparison. If a workflow intentionally routes a
strong lead to a cheaper worker, that topology is part of the workflow and
must be measured as delivered. A fair general comparison should support 1, 2,
or 3 model levels rather than forcing every system into one topology.

## 2. Use three result axes, not one magical score

### Quality

```text
valid_successes / eligible_tasks
```

For real user work, a task is successful only when the requested outcome is
present and usable through the real consumer path. A green unit test is
evidence, not the definition of success, unless the task contract explicitly
makes that test the product boundary.

### Economics

```text
effective_cost_per_success = total_effective_cost / valid_successes
```

Effective cost means the actual provider/account/relay bill or a clearly
declared list-price estimate. If there are zero successes, the denominator is
zero and the result is undefined/infinite, never “cheap”. Report fixed setup
cost separately from per-task cost.

### Time

Report wall-clock time to successful completion, p50/p95, and abandoned or
blocked runs. Time is independent of cost: a user who goes to sleep may value
eventual completion and price, while an interactive operator may value latency.

Tokens are a diagnostic field. Report input/output/tool tokens and calls, but
do not use them as a quality or cost proxy when the real price is known.

## 3. Build the task pack in layers

### Layer A: public reference tasks

Use a small, reproducible set from SWE-bench Pro, Terminal-Bench 2.0,
OSWorld/WebArena, τ-bench, SkillsBench, MCP-Bench, LongMemEval, and
MemoryAgentBench. Keep the benchmark's own score, but add cost and runtime
around the complete run.

### Layer B: held-out real tasks

Use fresh tasks from repositories or products that were not in training,
published examples, or the workflow's own documentation. The acceptance
contract should be written before the run and the evaluator should be blind to
which system produced the artifact.

### Layer C: business outcome tasks

Use the actual work that the harness is meant to do: a release, migration,
integration, incident repair, research delivery, or user-facing flow. Do not
turn this into a checklist of preferred architecture. Define only the desired
state, constraints, and disqualifying failures.

### Layer D: diagnostics

Collect traces, task states, tool calls, model routing, memory reads/writes,
retries, and workflow events. These explain a win or loss. They do not create a
win by themselves.

## 4. Prevent reward hacking without worshipping process

The goal is not “more checks”. The goal is trustworthy evidence for the
outcome. Use the cheapest verifier that proves the claimed boundary:

- hidden tests or state oracles for reference tasks;
- independent artifact and live-consumer checks for product tasks;
- held-out and fresh tasks to reduce contamination;
- multiple independent graders only where the result is genuinely semantic;
- complete transcripts and raw artifacts so a result can be audited;
- no bonus for number of agents, plan length, test count, token count, or
  architectural style;
- explicit penalties only for a real business failure, not for taking a
  different valid route.

This still leaves an unavoidable distinction: an oracle can prove that a
candidate passed its tests, but it cannot prove the tests describe the whole
user need. That is why reference and outcome-equivalence tracks must remain
separate.

## 5. Publication format

For every run publish one compressed campaign archive, not one archive per
agent:

```text
campaign.tar.zst
├── manifest.json
├── results.jsonl
├── transcripts.jsonl
├── artifacts/
└── evaluator/
```

The manifest must include benchmark version/commit, task IDs, model IDs and
topology, harness/plugin/skill versions, prompts/instructions, tool authority,
effective pricing source, start/end timestamps, retries, and whether the run
was completed or abandoned. Publish failed runs too. A transcript is useful
only when its provenance lets another person reproduce the claim.

## 6. Recommended headline for this repository

The public project should not claim “the best workflow”. It should say:

> We compare complete agent workflows on the same work. We publish whether the
> requested outcome was achieved, what it cost, and how long it took. Model
> leaderboards are inputs, not substitutes for workflow evaluation.

The result page should show at least:

| Workflow | Quality | Cost per success | Time to success | Failures | Notes |
|---|---:|---:|---:|---:|---|
| A |  |  |  |  |  |
| B |  |  |  |  |  |

Do not rank two systems with one composite number unless the user supplies the
weights. Show the Pareto frontier and, if desired, a clearly labeled weighted
view.
