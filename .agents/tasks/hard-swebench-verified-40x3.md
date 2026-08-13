# Hard SWE-bench Verified 40×3

Status: ready for topology canary
Started at: 2026-08-14T00:45:00+03:00
Initial estimate (minimum / maximum active minutes): 15 / 30
Active minutes: 25

## Outcome

Replace the 10-task, one-repeat headline with a frozen 40-task, three-repeat
workflow comparison without flattening workflow-owned model routing.

## Canaries

1. Dry-run: 480 unique cells (`40 × 4 × 3`) with isolated repeat paths.
2. Before the full campaign, one new task across all arms and repeats must emit
   an invocation receipt for every model/role it actually uses.

## Evidence

- `configs/hard-swebench-verified-40x3.json` freezes 35 remaining hard tasks
  and five declared medium tasks; all 40 image digests are pinned.
- `scripts/run_hard_swebench_campaign.py --dry-run` planned 480 unique cells.
- LHC's current Codex adapter declares `model_override: unproven`; current
  events do not contain child-model invocations. The next LHC canary must prove
  that path or the LHC arm stays infrastructure-invalid.

## Excluded

- No 480-cell live run before the topology canary and explicit spend decision.
- No claim that SWE-bench tasks are outside model training data.
