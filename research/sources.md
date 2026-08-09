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
- [AI Workflow Benchmark](https://github.com/xmpuspus/ai-workflow-benchmark) —
  tool + workflow evaluation on real-repository tasks.
- [Quorum / Superpowers Evals](https://github.com/prime-radiant-inc/superpowers-evals)
  — workflow-compliance/eval lab; not a neutral universal benchmark.
- [Harness Bench](https://www.harness-bench.ai/) — harness configuration
  effects on sandboxed executable workflow tasks.
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

## Pricing and reproducibility

- [models.dev](https://models.dev/) — useful open model/provider catalogue with
  context, price, release, and update fields. It is a list-price/reference
  source, not proof of the effective price of a private relay or subscription;
  zero/missing prices must not be interpreted as zero cost.
- [GitHub large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
  and [GitHub Releases limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
  — use one compressed campaign archive plus a small manifest; do not split
  every transcript into a separate upload.
