# Result schema

Each line in the result file is one completed scenario attempt:

```json
{
  "campaign": "declared-topology-comparison",
  "arm": "lhc-l0",
  "workflow_ref": "lhc-l0",
  "scenario": "verification-phantom-completion",
  "attempt": 1,
  "harness": "opencode",
  "topology": {
    "levels": [
      {"id": "mentor", "roles": ["adviser"], "model": "configured-adviser"},
      {"id": "lead", "roles": ["lead"], "model": "luna-5.4"},
      {"id": "worker", "roles": ["worker"], "model": "gpt-5.4-mini"}
    ],
    "parallelism": {"mode": "sequential", "max_concurrent_children": 1, "actual_children": 2}
  },
  "model_selection": {"policy": "declared", "budget_profile": "cheap", "fallback": false},
  "status": "pass",
  "successful_task": true,
  "wall_clock_seconds": 123.4,
  "input_tokens": 10000,
  "output_tokens": 2000,
  "total_tokens": 12000,
  "cost_usd": null,
  "cost_per_success_usd": null,
  "pricing": {"basis": "models.dev", "snapshot_date": "2026-08-09"},
  "invalid": false,
  "failure_category": null
}
```

Unknown measurements are `null`, not zero. Invalid infrastructure attempts are
retained and excluded from pass-rate denominators only under the published
replacement policy.

Campaign summaries additionally report `pass_rate`, `successful_tasks`,
`total_effective_cost_usd`, `cost_per_success_usd`, and wall-clock. Set
`cost_per_success_usd` to `null` when `successful_tasks == 0`; never turn that
case into a cheap winner.
