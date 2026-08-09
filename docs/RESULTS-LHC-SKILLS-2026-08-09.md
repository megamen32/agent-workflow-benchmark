# LHC L0 vs L1 product-outcome pilot

The pilot compared the frozen procedural [LastHumanCommit L0](https://github.com/megamen32/LastHumanCommit/releases/tag/lhc-l0-20260809) with L1, where six reusable procedures are exposed as canonical skills. Both cells used the same fixture, Docker image content ID, Codex harness, and declared stack: `gpt-5.6-terra` mentor → `gpt-5.6-luna` Lead → `gpt-5.4-mini` Worker.

| Cell | Product result | Effective price | Wall-clock | Tokens (diagnostic) |
|---|---:|---:|---:|---:|
| L0 | 1/1 passed | unknown; provider returned no charge | 64.70s | 148,691 |
| L1 | 1/1 passed | unknown; provider returned no charge | 79.34s | 169,050 |

## Task

The fixture was a checkout pricing bug: an unknown discount code made the
total `NaN`. Acceptance required the producer to return numeric zero, the
unknown code to charge full price, a known discount to remain correct, and a
runnable regression test to be left behind. This is a real product-outcome
check, not a workflow-ceremony check.

## Interpretation

On this one task, quality tied. L0 finished 14.63 seconds faster (18.4%); L1
used 20,359 more diagnostic tokens. That is evidence for this fixture only and
does not establish a general superiority claim. The route is a ChatGPT
subscription route with no billable per-call charge in the receipt; the
benchmark therefore does not convert tokens into a fake dollar amount.

## Reproducibility

- L0 commit: `44da5d900fe631d45cff292efb7284fcedb25ba1`
- L1 commit: `3c79d6c445447a8be94ed59608db8c4946ee4f7f`
- Docker image content ID: `sha256:f84f67e05d1b7bdedd12a31c01bd7ec90b7aeb1c9d32cb64e76904c51e00095e`
- L0 source snapshot: `sha256:20587eaecc3c605e77057cd6a90ea0d7b93a1c992b5c8725af6184896c4ac932`
- L1 source snapshot: `sha256:21df01a4651f6d62fff4be926b0b426df93748de1fd019ad14fb71d6eebaa5f9`
- L1 skill snapshot: `sha256:235042763b828e2a41d52dc54d2eefdaf237c1075eab9d9c7bdd26a3f6fb5986`
- Shared task fixture digest: `sha256:41e6f3a5cc2b5f9d1a87d165a7563633f4a7ef7ec04b51de81e928e644dda624`
- L0 transcript archive: `27f5991cce325b6cd3b4cb60e2373362d69410489aaaa8dae4adf3799d70a8ee`
- L1 transcript archive: `961aadf9a41a7e5b650ee7d991fd6f22530b32b0f270a1118e2a96223dc673bb`

The complete redacted dialogue, receipt, acceptance output, command, and
snapshot are stored under
[`results/lhc-skills-product-outcome-20260809/`](../results/lhc-skills-product-outcome-20260809/).
