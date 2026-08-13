# Hard real-repository workflow benchmark

Status: complete
Started at: 2026-08-12T19:20:00+03:00
Original estimate: 25 / 50 active minutes for design and first control calibration
Full sanitized campaign estimate after calibration: 25 / 70 active minutes
Completed at: 2026-08-12T23:06:45+03:00
Wall-clock: 226 minutes
Active-time source: not continuously measured; exact active time not controlled

## Business outcome

Replace the weak 10-function result as an overall workflow comparison with a
matched hard-task benchmark that can expose a quality difference.

## Shortest canary

One official SWE-bench Verified 1-4h instance runs in its frozen repository and
environment, Codex produces a patch, and the official hidden-test harness emits
resolved/unresolved. Measure wall time, tokens, and Docker disk delta.

## Selected route

Use official SWE-bench Verified instances and harness. Reuse the Arena runner
contract; do not invent synthetic hard fixtures or expose `test_patch` to the
agent. Calibrate control before freezing the final ten tasks.

## Stop conditions

- Do not clean foreign Docker cache.
- Do not start the 40-cell headline run until one cell proves the execution and
  grading path and its time/storage cost is known.
- Reject a final set where control is 0/10 or 10/10.

## Evidence

- Dataset: `SWE-bench/SWE-bench_Verified`, revision
  `03e151cf5560b1af6a4363c6a9d766deaaea6b56`.
- Official source: `/home/roomhacker/source_codes/SWE-bench`.
- Server free disk before build: 148 GB; existing Docker images: 145.1 GB.
- Final result: control 1/10, LHC 1/10, Superpowers 1/10, GSD 2/10.
- All 40 final cells used a synthetic one-commit Git history; 0 grader errors,
  0 agent timeouts.
- Invalidated the full pre-sanitization campaign after agents inspected embedded
  Git history; reran all cells to avoid survivor bias.
- Article and reproducible harness committed as `5fa1430` and pushed to `main`.
- Public evidence release:
  `hard-swebench-verified-10-20260812`, SHA-256
  `641815267952caf1344825da91ff40346bd2ebe3a3ff22c44e19f5b96cc3fe54`.
- Telegram Saved Messages: old easy result corrected in `#269`; hard article
  delivered and read back as `#275`.
