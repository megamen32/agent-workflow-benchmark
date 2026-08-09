# LHC Codex pilot: L0 vs L1

This is the first pilot of the public protocol. It compares five neutral
Quorum scenarios in Docker with Codex as the coding harness. Superpowers was
not rerun; its published results are not part of these cells.

## Arms

| Arm | Lead route | Worker declaration | Harness |
|---|---|---|---|
| L0 | GPT-5.6 Luna through the local Codex relay | GPT-5.4 Mini | Codex |
| L1 | MiniMax M3 through the official MiniMax Responses endpoint | MiniMax M2.7 | Codex |

The expensive judgement tier is recorded separately as Adviser, Overseer, and
Critic. The common Quorum grader used MiniMax M3. The current Codex receipt
proves the outer coding model and the workflow outcome; it does not yet prove
that every native Codex child used the declared Worker model. Therefore these
results are a valid workflow/harness pilot, but not yet a final claim about the
complete five-role model topology.

## Results

| Arm | Pass | Fail | Pass rate | Wall-clock (sum of cells) | Coding tokens | Coding cost |
|---|---:|---:|---:|---:|---:|---:|
| L0 | 4 | 1 | 80% | 31m 43s | 2,730,500 | $0.2762 |
| L1 | 3 | 2 | 60% | 24m 33s | 1,387,345 | n/a: subscription model unpriced by Quorum |

The L0 cost is the coding-agent estimate only; the MiniMax grader is also
unpriced. L1 used a subscription route, so a per-cell dollar figure would be
false precision. MiniMax documents Token Plan as a fixed monthly subscription
with rolling quota windows rather than a per-cell charge.

Failures:

- L0 failed `cost-spec-plan-duplication`: it wrote a combined task file instead
  of the required separate spec and plan documents.
- L1 failed `claim-without-verification-naive`: it changed code and committed
  before running the required test.
- L1 failed `cost-spec-plan-duplication` for the same missing spec/plan output.

Quality, time, tokens, and cost remain separate dimensions. No aggregate winner
is claimed.
