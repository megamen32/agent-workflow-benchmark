# Open benchmarks for models, agents, memory, skills, tools, and workflows

Research snapshot: 2026-08-09.

## Executive answer

There is no single benchmark that answers the question we actually care about:

> Did the system complete the user's task, and what did that successful result
> cost in money and time?

The public ecosystem is split into layers. Model exams measure closed-ended
knowledge. SWE-bench and Terminal-Bench measure executable tasks in constrained
environments. Memory suites measure recall and update behavior. Skills and MCP
benchmarks measure the marginal effect of instructions or tools. Workflow and
harness suites measure the wrapper itself. None of these layers is a complete
business benchmark by itself.

The full comparison is in [catalog.md](catalog.md). The proposed way to use it
is in [method.md](method.md), with primary links and scope notes in
[sources.md](sources.md).

## Two meanings of “better”

The catalogue separates two fundamentally different claims.

### Reference / known-answer

The evaluator has a reference answer, hidden tests, a simulator state, or an
oracle that defines correctness. This is useful for measuring capability and
regression, but it does **not** prove that the reference implementation is the
only good route or that the benchmark is globally representative. A fixed test
can be contaminated, overfit, or reward a shortcut.

Examples: SWE-bench, Terminal-Bench, HLE, SkillsBench, MCP-Bench, WebArena,
LongMemEval, MemoryAgentBench.

### Not-worse-than-X / outcome equivalence

There is no canonical implementation. Two systems receive the same user goal
and are equivalent if both produce an acceptable business result under the
same external constraints. The route, language, architecture, number of
agents, and number of tool calls are free variables.

This is the right class for comparing complete harnesses such as Codex,
Hermes, OpenCode, or a custom workflow. It needs a task-specific acceptance
contract, independent artifact/live checks, and a record of cost and elapsed
time. It must not score “more process” as quality.

Arena-style preference is a third, supporting class: it measures which answer
people prefer, not whether a real task was completed. It is useful for model
selection but cannot replace either of the two classes above.

## What the research says

1. **SWE-bench is closer to real engineering than academic model exams**, but
   benchmark validity is a moving target. SWE-bench Verified was designed to
   remove infeasible samples; later audits found contamination and design
   problems, and SWE-bench Pro itself has a substantial broken-task rate.
2. **Terminal-Bench and OSWorld are stronger for agent execution** because the
   agent must change a live environment, not merely return text. They still
   have an oracle and therefore remain reference benchmarks.
3. **SkillsBench is the best direct evidence that skills are interventions, not
   magic.** Its paired no-skill/curated-skill/self-generated-skill design can
   measure marginal lift. The reported average lift hides negative tasks and
   token overhead, so the paired per-task result matters more than the mean.
4. **MCP-Bench, MCPMark, ToolSandbox, and τ-bench test tool use at different
   levels.** Tool discovery, argument correctness, state transitions, policy
   compliance, and end-to-end completion must not be collapsed into one score.
5. **Memory benchmarks mostly test recall, not whether memory improves the
   final business task.** LongMemEval, LoCoMo, MemoryAgentBench, MemBench,
   Memora, and MemOS/OmniMemEval are useful layers; a real harness comparison
   additionally needs the same task with memory disabled and enabled, plus
   memory-write/read cost.
6. **Workflow/harness benchmarks are young and easy to mistake for product
   benchmarks.** Quorum/Superpowers Evals and Harness Bench can expose
   orchestration effects, but a workflow rule must not win merely because it
   triggered more agents, checks, or tokens. Their product result must be
   reported separately from workflow compliance.

## Result of the fresh GitHub/web/Habr sweep

The first pass was not exhaustive. A second search over current GitHub
repositories, recent papers, project sites, and Russian practitioner coverage
found several important additions:

- **Closest to the harness question:** [Claw-SWE-Bench](https://github.com/opensquilla/claw-swe-bench)
  fixes a prompt/runtime/workspace/patch contract across heterogeneous claws;
  its paper explicitly reports harness variance and total API cost.
- **Closest to the full-stack economics question:**
  [ClawBench/shellbench](https://github.com/openclaw/shellbench) records model,
  plugin, harness, trace, token, time, artifacts, and reliability regimes.
  Its trajectory/behavior score is still a diagnostic and must not replace
  completion or cost-per-success.
- **Closest to business outcomes:** [AutomationBench](https://github.com/zapier/AutomationBench)
  and [TheAgentCompany](https://github.com/TheAgentCompany/TheAgentCompany)
  leave simulated CRM/company worlds in a checked state after multi-application
  work.
- **Closest to real long-horizon coding:** [SWE-EVO](https://github.com/SWE-EVO/SWE-EVO),
  [SWE-bench-Live](https://openreview.net/pdf?id=OGWkr7gXka), and
  [Multi-SWE-bench](https://arxiv.org/abs/2504.02605).
- **Closest to skill routing:** [SRA-Bench](https://github.com/oneal2000/SR-Agents)
  tests retrieving and applying the right skill among distractors, which is a
  different problem from SkillsBench's skill-present/skill-absent ablation.
- **Closest to the MCP problem:** [MCP-Universe](https://github.com/SalesforceAIResearch/MCP-Universe)
  adds large unfamiliar tool spaces and long-horizon composition to MCP
  evaluation.

So the answer is **not “there are no other benchmarks”**. There are many more;
the actual shortage is a neutral, open benchmark that simultaneously allows an
arbitrary model topology, measures end-user outcome, captures real cost/time,
and publishes auditable traces. The new candidates are now included in the
catalogue with explicit validity and openness caveats.

## What should be reported

Do not compress everything into one score by default. Publish two primary
rankings:

- **Quality:** successful user outcomes / valid task completions.
- **Economics:** effective cost per successful task and elapsed time to a
  successful task.

If a system solves zero tasks, its cost-per-success is undefined/infinite; a
low raw spend does not make it cheap. Tokens are diagnostic only: the same
token count can have radically different prices, and extra tokens are
acceptable when they buy a successful result. Speed is a separate axis because
it matters differently for an unattended overnight task than for an interactive
one.

The honest aggregate is a Pareto frontier or a user-chosen weighted score, not
an allegedly universal “best” number. Full transcripts, manifests, artifacts,
model topology, tool configuration, effective billing, and failed runs should
be published together.

## Previous pilot

The earlier five-scenario L0/L1 run is retained only as a **workflow-guard
pilot**. It is not evidence of general engineering quality, model capability,
or harness superiority. It should not be used as the headline benchmark for
this repository.
