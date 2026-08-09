# Benchmark catalogue

Legend:

- **R** — reference/known-answer: correctness is defined by an answer, hidden
  tests, a simulator oracle, or deterministic post-checks.
- **O** — outcome-equivalence candidate: can support “not worse than X” when
  paired with an external business acceptance contract; the benchmark itself
  may still contain R-style checks.
- **P** — preference: human or model preference, not task completion.
- **D** — diagnostic: useful for explaining behavior, not a product-quality
  ranking on its own.

| Layer | Benchmark | What is actually tested | Class | Cost/time in official result? | Main value | Main trap / reward-hacking risk |
|---|---|---|---|---|---|---|
| Coding | [SWE-bench](https://github.com/SWE-bench/SWE-bench) | Agent edits a pinned repository to resolve a real GitHub issue; FAIL_TO_PASS and PASS_TO_PASS tests grade the patch | R | Usually not standardized | Real repository-level issue resolution | Public issues and tests can be contaminated; tests define accepted behavior and may miss valid behavior |
| Coding | [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) | 500 human-screened SWE-bench instances with containerized evaluation | R | Not a universal cost track | Better-curated issue descriptions/tests than original SWE-bench | Later audit says it no longer gives meaningful frontier signal due to contamination/design; do not treat its leaderboard as ground truth |
| Coding | [SWE-bench Pro](https://arxiv.org/abs/2509.16941) | 1,865 longer-horizon tasks from 41 repositories, with public, held-out, and commercial partitions | R | Varies by runner | More realistic complexity and contamination resistance than small issue sets | Task validity is not perfect; an OpenAI audit estimated roughly 30% problematic tasks |
| Coding | [SWE-rebench V2](https://arxiv.org/abs/2602.23866) | Fresh/language-agnostic issue-resolution collection with setup and filtering pipeline | R | Research-dependent | Useful direction for decontaminated, current SWE tasks | New and less historically comparable; audit the generated setup and judge filters |
| Coding | [SWE-bench-Live](https://openreview.net/pdf?id=OGWkr7gXka) | Continuously refreshed issues from recent GitHub activity | R | Runner-dependent | Direct attack on benchmark contamination and stale tasks | Fresh tasks still need validity checks; live mining can change the distribution |
| Coding | [SWE-bench Multimodal](https://arxiv.org/abs/2410.03859) | 617 JavaScript issues where visual/UI context is part of the repair | R | Runner-dependent | Tests visual software engineering absent from Python-only SWE-bench | UI libraries, screenshots, and task-specific tests can dominate |
| Coding | [Multi-SWE-bench](https://arxiv.org/abs/2504.02605) | Issue resolution across Java, TypeScript, JavaScript, Go, Rust, C and C++ | R | Runner-dependent | Language/ecosystem diversity | Different build systems make cross-language scores less comparable |
| Coding | [SWE-EVO](https://github.com/SWE-EVO/SWE-EVO) | Multi-step evolution of large repositories from high-level software requirements | R/O | Runtime/cost can be wrapped | Closer to long-lived product change than one isolated bug | New benchmark; SRS and historical project selection define the target |
| Coding | [SWE-Explore-Bench](https://github.com/Qiushao-E/SWE-Explore-Bench) | Exploration/localization before editing, scored against line-level ground truth | R/D | Read/tool cost can be measured | Isolates repository exploration and context selection | A good locator can still fail the actual user task; not a full outcome score |
| Coding/harness | [Claw-SWE-Bench](https://github.com/opensquilla/claw-swe-bench) | 350 multilingual issue tasks with an adapter contract for heterogeneous agent harnesses | R/O | Explicitly treats harness and total API cost as axes | One of the closest new matches to comparing Codex/Hermes/OpenCode-like wrappers | Derived from existing SWE sets; adapter compliance and prompt/runtime budgets matter |
| Coding | [RoadmapBench](https://arxiv.org/abs/2605.15846) | 115 multi-target version-upgrade tasks across 17 repositories and 5 languages | R/O | Runtime/cost can be wrapped | Long-horizon product evolution rather than isolated issue repair | Target version is a reference implementation; large patches can reward imitation |
| Coding | [LongCLI-Bench](https://aclanthology.org/2026.findings-acl.1497/) | Long sequential engineering tasks in command-line environments | R/O | Runner-dependent | Directly tests sustained CLI execution | Preliminary benchmark; inspect task validity and oracle behavior |
| Coding | [SlopCodeBench](https://arxiv.org/abs/2603.24755) | 20 problems and 93 checkpoints measuring extension degradation, verbosity, and structural erosion | D/R | Cost can be added but is not primary | Catches “passes tests now, becomes unmaintainable later” | Its quality proxies are not the same as user outcome and can become style policing |
| Coding | [Terminal-Bench 2.0](https://github.com/harbor-framework/terminal-bench-2) | 89 hard terminal tasks in realistic Linux environments | R/O | Harness can capture runtime; cost is not the quality score | Better measure of terminal agency and long-horizon execution than code-only tests | Environment/oracle bugs; benchmark-specific shell habits can be learned |
| Coding | [Humanity's Last Code Exam](https://humanity-s-last-code-exam.github.io/website/) | 235 very hard IOI/ICPC-style programming problems | R | Usually no business-cost track | Measures algorithmic coding capability and difficulty | Not repository engineering, tool use, or product delivery |
| General model | [Humanity's Last Exam](https://labs.scale.com/papers/humanitys-last-exam) | 3,000 expert-created multimodal closed-ended questions across broad disciplines | R | No end-to-end cost track | Frontier knowledge/reasoning ceiling with verifiable answers | Academic closed questions are not user-task completion; contamination and judge calibration still matter |
| General model | [Chatbot Arena / Arena](https://arena.ai/how-it-works) | Pairwise human preference over model responses, represented by Elo/Bradley-Terry-style ratings | P | No task cost | Real-user preference signal and broad model comparison | Style, verbosity, prompt mix, refusal behavior, and selection bias can move the ranking; preference is not correctness |
| General agent | [GAIA](https://arxiv.org/abs/2311.12983) | General assistant tasks requiring reasoning, browsing, and tool use | R | Usually no normalized cost | Broad assistant capability beyond coding | Mixed task difficulty, hidden answers, and tool/environment variance |
| General agent | [AgentBench](https://github.com/THUDM/AgentBench) | Eight environments including OS, DB, KG, WebShop, web browsing, household tasks, games, and puzzles | R | Runner can measure it; headline score usually does not | Multi-environment agent capability | Heterogeneous environments are hard to compare; old integrations and infrastructure can dominate |
| General workplace | [TheAgentCompany](https://github.com/TheAgentCompany/TheAgentCompany) | 175 simulated-company tasks involving web apps, coding, files, and coworker communication | R/O | Can be wrapped; official score is completion-oriented | Consequential multi-application work rather than isolated QA | Simulated colleagues and product state are still an artificial world |
| Business automation | [AutomationBench](https://github.com/zapier/AutomationBench) | 600 simulated CRM/calendar/inbox/SaaS workflows across six business domains | R/O | Runner exports token usage and cost estimates | Directly tests whether a business state is left correct | Simulated SaaS semantics and task distribution; public/private split is not full reproduction |
| Workspace | [Workspace-Bench](https://github.com/OpenDataBox/Workspace-Bench) | Large-scale file-workspace tasks with explicit and implicit dependencies | R/O | Runner/judge can capture it | Relevant to agents working through many project documents, not just code | LLM judge and workspace corpus can reward benchmark-specific organization |
| Browser/desktop | [WebArena](https://github.com/web-arena-x/webarena) | Long-horizon tasks across self-hosted functional websites | R | Runtime can be collected | End-to-end web completion with reproducible state | Site simulator/oracle and browser interaction patterns can be overfit |
| Browser/desktop | [OSWorld](https://github.com/xlang-ai/OSWorld) / [OSWorld 2.0](https://osworld-v2.xlang.ai/) | Open-ended tasks in real desktop applications and OS environments | R/O | Runtime is measurable; official headline is mostly success | Closest open benchmark to computer-use product work | VM/image/version, UI timing, and brittle state can dominate; still not arbitrary business equivalence |
| Tools/API | [τ-bench / τ³-bench](https://github.com/sierra-research/tau2-bench) | Multi-turn user-agent interaction with domain APIs, policies, state, and user simulation | R | Usually task reward; cost needs wrapper | Customer-service-like tool use, policy adherence, and state transitions | Simulated user/policies are an oracle; policy compliance can be mistaken for business value |
| Tools/MCP | [MCP-Bench](https://github.com/Accenture/mcp-bench) | Tool discovery, schema use, argument precision, multi-hop coordination across 28 live MCP servers / 250 tools | R/D | Can log calls/tokens; not primary score | Directly tests MCP ecosystems and fuzzy tool selection | External services, tool availability, and schema familiarity; many calls are not automatically better |
| Tools/MCP | [MCPMark](https://github.com/eval-sys/mcpmark) | Real MCP use across GitHub, Notion, filesystem, Postgres, Playwright and other services | R/O | Docker runner can capture it | More realistic cross-service tasks than isolated function calling | Credentials, rate limits, mutable external state, and service drift |
| Tools/MCP | [MCP-Universe](https://github.com/SalesforceAIResearch/MCP-Universe) | Real-world MCP servers, large unfamiliar tool spaces, long-horizon general tool use | R | Research runner-dependent | Stronger test of discovering and composing unfamiliar MCP capabilities | External APIs, provider credentials, and tool corpus can dominate |
| Tools/security | [MCP Security Bench](https://iclr.cc/virtual/2026/poster/10007929) | End-to-end resistance to MCP-specific attacks across planning, invocation, and response handling | R/D | Security/performance trade-off is measured; cost not primary | Tests whether tool capability creates unacceptable attack surface | Security score is not business quality; attack harness must be isolated |
| Tools/security | [MCPTox](https://ojs.aaai.org/index.php/AAAI/article/view/40895) | Tool-poisoning attacks against agents using real-world MCP servers | R/D | Usually success/robustness, not cost | Important safety failure mode missing from normal MCP task scores | Adversarial task distribution and changing server ecosystem |
| Tools | [ToolSandbox](https://github.com/apple/ToolSandbox) | Stateful conversational tool use with a simulated world and composable tools | R | Artifacts include full trajectories; cost requires wrapper | Clean isolation of state, tool calls, user simulation, and final outcome | Simulated API semantics are not production APIs; LLM user simulation can be noisy |
| Skills | [SkillsBench](https://github.com/benchflow-ai/skillsbench) | Same task under no skill, curated skill, and self-generated skill conditions with deterministic verifiers | R/D | Trajectories available; token overhead can be measured | Best direct paired test of skill marginal utility | Average lift hides negative tasks and cost; curated skills may fit the benchmark |
| Skills/SWE | [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401) ([dataset](https://huggingface.co/datasets/GeniusHTX/SWE-Skills-Bench)) | 49 public SWE skills paired with pinned repos and requirement-driven acceptance tests | R/D | Reports token overhead in research; reproduce to verify | Measures whether skills help actual SWE tasks rather than whether docs look good | Skill/repo version mismatch and task curation; new benchmark needs independent replication |
| Skills/retrieval | [SRA-Bench](https://github.com/oneal2000/SR-Agents) | 5,400 instances testing retrieval, incorporation, and execution of skills among distractors | R/D | Retrieval and end-task cost can be added | Directly measures skill discovery instead of assuming the right skill is already injected | Gold skill corpus and distractors may not represent a real user's skill library |
| Workflow | [AI Workflow Benchmark](https://github.com/xmpuspus/ai-workflow-benchmark) | Tool + workflow on 100 real-repo tasks across capability dimensions | R/D | Designed to report tokens/cost/runtime | Closest existing attempt to compare workflow wrappers | Public scoring choices, model/harness coupling, and task distribution can dominate |
| Workflow | [Quorum / Superpowers Evals](https://github.com/prime-radiant-inc/superpowers-evals) | Superpowers workflow compliance, triggering, subagents, verification, review, worktrees, and cost-shaping | D/R | Cost-shaping is observable | Finds whether a workflow rule was followed | It explicitly is an eval lab for one workflow, not a neutral product benchmark |
| Workflow | [Harness Bench](https://www.harness-bench.ai/) | Harness configuration effects across 106 sandboxed offline workflow tasks with oracle checks | D/R | Intended to measure effects; inspect runner output | Directly isolates wrapper/harness deltas | Harness compliance can be mistaken for product quality; task suite is still its own oracle |
| Workflow | [ClawBench / shellbench](https://github.com/openclaw/shellbench) | Full-stack harness/config/model traces, reliability, failure regimes, and configuration diagnostics | D/O | Explicit trace, token, timing, and artifact fields | Closest public design to “what did the whole agent system cost and accomplish?” | OpenClaw-native assumptions and a weighted trajectory axis can reward process; use completion and economics separately |
| Workflow | [CUBE harness](https://github.com/The-AI-Alliance/cube-harness) | Interchange/runtime for running agents against CUBE-compatible environments and recording trajectories | D | Runner can collect it | Potential common execution protocol across many benchmarks | Alpha infrastructure, not a benchmark/task corpus itself |
| Workflow | [OpenHands evaluation](https://github.com/All-Hands-AI/OpenHands) | Agent execution/evaluation infrastructure commonly used for SWE and tool tasks | D | Depends on selected benchmark | Useful adapter and reproducible runner | OpenHands is a harness, not a universal ground-truth benchmark |
| Memory | [LongMemEval](https://github.com/xiaowu0162/LongMemEval) | 500 questions across extraction, multi-session reasoning, updates, temporal reasoning, and abstention | R | Token/latency can be added; not the headline | Strong long-term interactive-memory regression suite | Mostly QA/recall; high recall does not prove improved task completion |
| Memory | [LoCoMo](https://github.com/snap-research/locomo) | Very long conversations with single-hop, multi-hop, temporal, open-domain QA and summaries | R | Usually score only | Widely used, simple comparison point for conversational memory | Small number of conversations and QA-shaped behavior; retrieval score is not business value |
| Memory | [MemoryAgentBench](https://github.com/HUST-AI-HYZ/MemoryAgentBench) | Incremental multi-turn memory with accurate retrieval, updates and agent-memory tasks | R | Can be measured by wrapper | Better agent-oriented memory interaction than one-shot QA | New benchmark and task-specific answer matching; compare full conditions, not quoted scores |
| Memory | [MemBench](https://github.com/import-myself/Membench) | Effectiveness, efficiency, and capacity of LLM-agent memory | R | Explicitly includes efficiency | Broader memory dimensions than pure recall | Dataset assumptions and judge/scoring details need auditing |
| Memory | [Memora](https://github.com/geniesinc/Memora) | Personalized long-term memory with task-level remembering, recommending, and reasoning | R/O | Paper reports task-level metrics; reproduce cost | Tests whether memory supports personalized actions, not only retrieval | New dataset/model stack; reported scores are not automatically comparable |
| Memory | [MemOS / OmniMemEval](https://github.com/MemTensor/MemOS) | MemTensor MemOS reports user-memory and agent-memory suites including LoCoMo, LongMemEval, BEAM, SWE-Bench and others | R/D | MemOS reports token savings in some releases; verify same backbone | Relevant to Hermes/OpenClaw-style memory adapters and cross-task skill reuse | Vendor-maintained results are not independent; compare with the same model, prompts, and memory budget |
| Memory | [STATE-Bench](https://github.com/microsoft/STATE-Bench) | 450 stateful enterprise tasks; tests whether agents improve with experience under pluggable memory | R/O | Explicitly targets reliability, turns, and efficiency | Best new match for “does memory actually improve later work?” | Three simulated domains and user simulators; still not arbitrary production work |
| Memory | [EvoMemBench](https://github.com/DSAIL-Memory/EvoMemBench) | In-episode vs cross-episode and knowledge-oriented vs execution-oriented memory | R | Research-dependent | Explicitly separates memory types that are often conflated | Very new; limited ecosystem comparability |
| Memory/mobile | [MemGUI-Bench](https://lgy0404.github.io/MemGUI-Bench/) | Mobile GUI memory, cross-app workflows, long-term improvement and recovery | R/O | Includes efficiency views; confirm raw cost | Relevant to mobile agents and S21-style device use | UI model/device/app version confounds; leaderboard is young |
| Research agent | [AIRS-Bench](https://github.com/facebookresearch/airs-bench) | 20 ML research tasks requiring an agent to improve a metric on a dataset relative to SOTA | R/O | Compute and runtime can be measured | Evaluates an actual research loop, not only literature answers | Domain-specific ML scaffolds and SOTA target can bias the result |
| Research agent | [DeepSearchQA](https://arxiv.org/abs/2601.20975) | 900 difficult multi-step information-seeking tasks across 17 fields | R | Search/tool cost can be wrapped | More demanding research retrieval than simple fact QA | Short-answer/reference grading may miss useful but differently framed research |
| Research agent | [AutoResearchBench](https://arxiv.org/abs/2604.25256) | Deep and wide scientific literature discovery | R/O | Runner-dependent | Separates finding one target paper from comprehensive collection | New, specialist, and search-index dependent |
| Research agent | [PaperBench](https://arxiv.org/abs/2504.01848) | Reproducing 20 ICML papers from understanding through code and experiments | R/O | Compute/time can be measured | Full research replication workflow | Reproduction score uses paper-specific rubric and substantial compute |
| Research agent | [MLE-bench](https://openai.com/index/mle-bench/) | Kaggle-style machine-learning engineering competitions | R/O | Compute cost matters but is not standardized | Real ML engineering and measurable competition outcome | Kaggle/task-specific optimization; not general software workflow |
| Research agent | [ScienceAgentBench](https://arxiv.org/abs/2410.05080) | 102 multimodal data-driven scientific discovery tasks | R/O | Compute/runtime can be wrapped | Scientific data-analysis and code execution | Scientific benchmark domains do not represent ordinary business work |
| Security agent | [CyberGym / CyberGym-E2E](https://www.cybergym.io/cybergym-e2e/) | Vulnerability reproduction, exploit generation, and end-to-end discover/patch tasks | R/O | Runner-dependent; safety isolation is mandatory | Real security outcomes on open-source projects | Specialized adversarial domain; unsafe evaluation can affect external systems |
| Data agent | [DataAgentBench](https://github.com/ucbepic/DataAgentBench) | Agents answer questions over data with executable evaluation | R/O | Can be wrapped | Data-agent outcome rather than generic QA | Dataset and SQL/tool assumptions narrow transfer |
| Spreadsheet agent | [AI Spreadsheet Benchmark](https://huggingface.co/datasets/rowshq/aispreadsheetbenchmark) | 53 realistic spreadsheet analysis, enrichment, visualization, and management workflows | R/O | Cost/time requires wrapper | Concrete office productivity tasks | Small dataset and workbook-specific acceptance |
| Full agent | [Open Agent Leaderboard](https://huggingface.co/blog/ibm-research/open-agent-leaderboard) | Compares full agent systems through an open evaluation framework | D/O | Inspect per-run metrics; not automatically comparable | Explicitly moves beyond model-only leaderboards | Composite leaderboard may conflate model, harness, tools, and task mix |
| Cost | [Joule Index](https://joule.blankline.org/) | Cost, energy, attention, and merge-readiness on real coding tasks | O/D | Cost and energy are headline metrics | Closest discovered match to cost-first reporting | Very small task sample and proprietary reference agent |

## What belongs in the “known better” column

Use R benchmarks when the question is narrow and the oracle is credible:

- Can the agent resolve this repository issue under hidden tests?
- Can it complete this terminal or desktop state transition?
- Can it retrieve/update the correct memory fact?
- Did the skill/tool call produce the expected state?
- Did the answer match a verified expert answer?

The result is “better on this benchmark under this evaluator”, not “better in
all useful work”. Every R row needs a validity audit and contamination note.

## How open is “open”?

“Open benchmark” is not one status. The practical split is:

- **Open data + runner:** SWE-bench, Terminal-Bench, AgentBench, WebArena,
  OSWorld, τ-bench, ToolSandbox, SkillsBench, LongMemEval, LoCoMo,
  MemoryAgentBench, MemBench, and the public parts of MCP-Bench/MCPMark.
- **Open public portion, hidden or commercial holdout:** SWE-bench Pro. This is
  useful for honest evaluation, but a public reproduction cannot claim to have
  reproduced the whole benchmark.
- **Open questions/runner, closed or changing answer pool:** GAIA and Arena.
  A public score is not necessarily a locally reproducible score.
- **Open vendor runner/results, independent replication still required:**
  MemOS/OmniMemEval and other memory product leaderboards. A repository being
  open does not make a vendor's reported model stack an independent result.
- **Open workflow-specific evaluator:** Quorum/Superpowers Evals and Harness
  Bench. They are valuable diagnostics, but their task and rubric choices are
  part of what is being evaluated.

For publication, the manifest must state whether the run used public data,
held-out data, a private task set, a vendor leaderboard, or a locally authored
business set. Those are different evidence grades and must not be mixed in one
table without labels.

## What belongs in the “not worse than X” column

Use O-style evaluation for a complete harness or product workflow:

1. Freeze the user request and external constraints, not the implementation.
2. Give each system the same starting state and authority.
3. Define acceptance in business terms: the requested artifact/state exists,
   works through the real consumer path, and has no disqualifying regression.
4. Allow any valid route, model topology, language, tool, or delegation level.
5. Record effective cost, wall-clock completion time, failures, retries, and
   all artifacts/transcripts.
6. Report quality and economics separately. A cheaper failure is still a
   failure; a more expensive success is not automatically bad.
