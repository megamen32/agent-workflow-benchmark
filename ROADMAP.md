# Roadmap

> Goal: a small, auditable workflow benchmark that cannot pretend more than it measured.

## Done

- [x] Pinned runner, images, workflow revisions, receipts, and hidden grading.
- [x] 10-task hard SWE-bench round: four workflows, one route, one repeat.
- [x] Freeze that 10-task set as calibration/dev only.

## Next

- [ ] Select 40 repository tasks before the campaign; keep 30–50 as the normal minimum.
- [ ] Make them held-out: no workflow tuning after task selection.
- [ ] Run the same frozen workflows on 3 model families.
- [ ] Repeat every task/workflow/model cell 3 times; randomize order.
- [ ] Report rates, uncertainty, failures, cost, and time by model family.

## Later

- [ ] Add fresh business-outcome tasks with prewritten, blind acceptance.
- [ ] Expand only after a completed matrix reveals a concrete gap.

## Rules

- Dev results never become test claims.
- Hosted aliases are recorded, not treated as immutable checkpoints.
- Invalid infrastructure runs are published and replaced only under the matched policy.
- No global winner without a scope that supports it.
