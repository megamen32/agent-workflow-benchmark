# Sources and audit notes

Accessed 2026-08-09. Primary repositories, papers, and maintainers' pages are
preferred. Scores quoted by a project are recorded as claims by that project,
not independent facts.

## Coding and model capability

- [SWE-bench repository](https://github.com/SWE-bench/SWE-bench) — executable
  repository-level issue resolution with FAIL_TO_PASS/PASS_TO_PASS tests.
- [SWE-bench Verified announcement](https://openai.com/index/introducing-swe-bench-verified/)
  — human screening, 500 samples, Docker harness, and documented limitations.
- [Why OpenAI no longer evaluates SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)
  — contamination and design audit.
- [SWE-bench Pro paper](https://arxiv.org/abs/2509.16941) — long-horizon,
  enterprise-style task design and 1,865-problem structure.
- [OpenAI: Separating signal from noise in coding evaluations](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)
  — later audit reporting a high broken-task rate in SWE-bench Pro.
- [SWE-rebench V2](https://arxiv.org/abs/2602.23866) — fresh,
  language-agnostic issue-resolution direction.
- [SWE-bench-Live paper](https://openreview.net/pdf?id=OGWkr7gXka) — continuously
  refreshed issues from recent repository activity.
- [SWE-bench Multimodal](https://arxiv.org/abs/2410.03859) and
  [Multi-SWE-bench](https://arxiv.org/abs/2504.02605) — visual/UI and
  multilingual issue resolution.
- [SWE-EVO](https://github.com/SWE-EVO/SWE-EVO) — long-horizon repository
  evolution from software requirements.
- [SWE-Explore-Bench](https://github.com/Qiushao-E/SWE-Explore-Bench) —
  repository exploration/localization as a separate capability.
- [Claw-SWE-Bench paper](https://arxiv.org/abs/2606.12344) and
  [adapter implementation](https://github.com/opensquilla/claw-swe-bench) —
  heterogeneous harness comparison, fixed runtime contract, and cost axis.
- [RoadmapBench](https://arxiv.org/abs/2605.15846) — long-horizon version
  upgrades across large multi-file repositories.
- [LongCLI-Bench](https://aclanthology.org/2026.findings-acl.1497/) — long
  sequential command-line engineering tasks.
- [SlopCodeBench](https://arxiv.org/abs/2603.24755) — degradation and extension
  robustness across iterative coding checkpoints.
- [Terminal-Bench 2.0 repository](https://github.com/harbor-framework/terminal-bench-2)
  and [paper](https://arxiv.org/abs/2601.11868) — hard terminal tasks in
  computer environments.
- [Humanity's Last Code Exam](https://humanity-s-last-code-exam.github.io/website/)
  — competitive-programming difficulty, not repository delivery.
- [Humanity's Last Exam](https://labs.scale.com/papers/humanitys-last-exam)
  — expert-created multimodal closed-ended knowledge benchmark.
- [Arena methodology](https://www.lmsys.org/blog/2023-12-07-leaderboard/)
  and [current “how it works” page](https://arena.ai/how-it-works) — pairwise
  preference and Elo/Bradley-Terry-style ranking.
- [Style effects in Chatbot Arena](https://www.lmsys.org/blog/2024-08-28-style-control/)
  — evidence that style and length affect preference rankings.

## General agents and computer use

- [GAIA paper](https://arxiv.org/abs/2311.12983) — general assistant tasks.
- [AgentBench repository](https://github.com/THUDM/AgentBench) — eight agent
  environments.
- [TheAgentCompany repository](https://github.com/TheAgentCompany/TheAgentCompany)
  — 175 simulated software-company tasks across applications, coding, and
  coworker communication.
- [AutomationBench](https://github.com/zapier/AutomationBench) — 600 simulated
  business workflows across CRM, inbox, calendar, and other SaaS tools, with
  programmatic state checks and cost-export support.
- [Workspace-Bench](https://github.com/OpenDataBox/Workspace-Bench) — large
  file-workspace dependency tasks.
- [WebArena repository](https://github.com/web-arena-x/webarena) — functional,
  self-hosted web environment.
- [OSWorld repository](https://github.com/xlang-ai/OSWorld) — real desktop/OS
  tasks and Docker-supported setup.
- [OSWorld 2.0](https://osworld-v2.xlang.ai/) — newer long-horizon computer-use
  task direction.

## Tools and MCP

- [τ-bench / τ³-bench repository](https://github.com/sierra-research/tau2-bench)
  and [paper](https://arxiv.org/abs/2406.12045) — user-agent-tool interaction,
  policies, and stateful domains.
- [MCP-Bench repository](https://github.com/Accenture/mcp-bench) and
  [paper](https://arxiv.org/abs/2508.20453) — 28 MCP servers, 250 tools,
  discovery, multi-hop use, and completion.
- [MCP-Universe](https://github.com/SalesforceAIResearch/MCP-Universe) and
  [paper](https://arxiv.org/abs/2508.14704) — unfamiliar real-world MCP
  servers and long-horizon tool use.
- [MCP Security Bench](https://iclr.cc/virtual/2026/poster/10007929) and
  [MCPTox](https://ojs.aaai.org/index.php/AAAI/article/view/40895) — MCP attack
  resistance and tool poisoning; security tracks, not productivity scores.
- [MCPMark documentation](https://mcpmark.ai/docs/introduction) and
  [repository](https://github.com/eval-sys/mcpmark) — cross-service MCP tasks,
  Docker runner, and service isolation guidance.
- [ToolSandbox repository](https://github.com/apple/ToolSandbox) and
  [Apple research page](https://machinelearning.apple.com/research/toolsandbox-stateful-conversational-llm-benchmark)
  — stateful simulated world, tools, roles, and full trajectories.

## Skills and workflow/harness

- [SkillsBench repository](https://github.com/benchflow-ai/skillsbench),
  [paper](https://arxiv.org/abs/2602.12670), and [release page](https://www.skillsbench.ai/)
  — no skill vs curated skill vs self-generated skill with deterministic
  verifiers.
- [SWE-Skills-Bench paper](https://arxiv.org/abs/2603.15401) and its
  [Hugging Face dataset](https://huggingface.co/datasets/GeniusHTX/SWE-Skills-Bench)
  — requirement-driven SWE skill ablation. The GitHub URL reported by the
  paper search was unavailable during this audit, so the dataset link is the
  reproducible public source recorded here.
- [SRA-Bench](https://github.com/oneal2000/SR-Agents) and
  [paper](https://arxiv.org/abs/2604.24594) — skill retrieval, incorporation,
  distractor resistance, and end-task execution.
- [AI Workflow Benchmark](https://github.com/xmpuspus/ai-workflow-benchmark) —
  tool + workflow evaluation on real-repository tasks.
- [Quorum / Superpowers Evals](https://github.com/prime-radiant-inc/superpowers-evals)
  — workflow-compliance/eval lab; not a neutral universal benchmark.
- [Harness Bench](https://www.harness-bench.ai/) — harness configuration
  effects on sandboxed executable workflow tasks.
- [ClawBench/shellbench](https://github.com/openclaw/shellbench) — full-stack
  trace scoring, reliability regimes, configuration diagnostics, token/time
  accounting, and an interchange trace format. Treat its trajectory/behavior
  axes as diagnostics until independently validated against business outcomes.
- [CUBE harness](https://github.com/The-AI-Alliance/cube-harness) — alpha
  benchmark-agnostic runtime and trajectory protocol, not a task benchmark.
- [Superpowers](https://github.com/obra/superpowers) and
  [ECC](https://github.com/affaan-m/ECC) — surveyed workflow projects; their
  existence or popularity is not evidence of a shared neutral benchmark.

## Memory

- [LongMemEval](https://github.com/xiaowu0162/LongMemEval) — 500 questions and
  five long-term memory abilities.
- [LoCoMo](https://github.com/snap-research/locomo) — long conversational
  memory, multi-hop and temporal questions.
- [MemoryAgentBench](https://github.com/HUST-AI-HYZ/MemoryAgentBench) —
  incremental multi-turn memory-agent evaluation.
- [MemBench](https://github.com/import-myself/Membench) — effectiveness,
  efficiency, and capacity.
- [Memora benchmark code](https://github.com/geniesinc/Memora) and
  [paper](https://arxiv.org/abs/2604.20006) — personalized memory tasks.
- [MemTensor MemOS](https://github.com/MemTensor/MemOS) and
  [OmniMemEval](https://github.com/MemTensor/OmniMemEval) — MemOS's own
  cross-benchmark memory evaluation and Hermes/OpenClaw-oriented local plugin
  positioning. Treat published scores as vendor claims until independently
  reproduced with the same model and prompt budget.
- [MemoryOS paper/code](https://github.com/BAI-LAB/MemoryOS) — a separate
  project with a similar name; do not conflate it with MemTensor MemOS.
- [EvoMemBench](https://github.com/DSAIL-Memory/EvoMemBench) — memory scope
  and knowledge/execution axes.
- [MemGUI-Bench](https://lgy0404.github.io/MemGUI-Bench/) — mobile GUI memory
  and cross-app workflows.
- [STATE-Bench](https://github.com/microsoft/STATE-Bench) — open, memory-agnostic
  stateful enterprise tasks that measure whether experience improves reliability,
  completion, and efficiency.
- [AIRS-Bench](https://github.com/facebookresearch/airs-bench) — 20 ML research
  tasks with executable metric comparison against published SOTA.
- [DeepSearchQA](https://arxiv.org/abs/2601.20975) — 900 difficult multi-step
  information-seeking tasks.
- [AutoResearchBench](https://arxiv.org/abs/2604.25256) — deep and wide
  scientific literature discovery.
- [PaperBench](https://arxiv.org/abs/2504.01848) — replication of 20 ICML papers.
- [MLE-bench](https://openai.com/index/mle-bench/) — Kaggle-style ML engineering
  agent evaluation.
- [ScienceAgentBench](https://arxiv.org/abs/2410.05080) — multimodal,
  data-driven scientific discovery.
- [CyberGym-E2E](https://www.cybergym.io/cybergym-e2e/) — end-to-end security
  discovery, proof, and patching in real projects.
- [DataAgentBench](https://github.com/ucbepic/DataAgentBench) — executable data
  question answering and data-agent tasks.
- [AI Spreadsheet Benchmark](https://huggingface.co/datasets/rowshq/aispreadsheetbenchmark)
  — 53 realistic spreadsheet workflows.
- [Open Agent Leaderboard](https://huggingface.co/blog/ibm-research/open-agent-leaderboard)
  — open attempt to compare full agent systems rather than only models.
- [Joule Index](https://joule.blankline.org/) and its
  [method paper](https://blankline.org/research/joule-index/paper) — explicit
  dollar, energy, attention, and merge-readiness reporting.

## Fresh discovery sources and secondary material

These were used to discover candidates, not as the authority for benchmark
scores:

- [Habr: benchmarking AI agents on real tasks](https://habr.com/ru/articles/886198/)
  — broad Russian overview of tool interaction and real-task evaluation.
- [Habr: why agents cheat in CI/CD](https://habr.com/ru/articles/1019634/)
  — useful behavioral failure cases, but an adversarial article is not a
  standardized benchmark.
- [Habr: evaluating agents in production](https://habr.com/ru/articles/1040756/)
  — practical distinction between benchmark scores and real production
  traces/checks.
- [GitHub agent-harness survey](https://github.com/Picrew/awesome-agent-harness)
  — discovery index, not evidence of benchmark validity.
- [GitHub agent-skill survey](https://github.com/Cassie07/AgentSkill_Survey)
  — discovery index for SkillsBench, SRA-Bench, and related work.

## Pricing and reproducibility

- [models.dev](https://models.dev/) — useful open model/provider catalogue with
  context, price, release, and update fields. It is a list-price/reference
  source, not proof of the effective price of a private relay or subscription;
  zero/missing prices must not be interpreted as zero cost.
- [GitHub large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
  and [GitHub Releases limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
  — use one compressed campaign archive plus a small manifest; do not split
  every transcript into a separate upload.
