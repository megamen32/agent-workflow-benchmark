# Result schema

Each line in the result file is one completed scenario attempt:

```json
{
  "campaign": "two-level-workflow-comparison",
  "arm": "lhc-l0",
  "workflow_ref": "lhc-l0",
  "scenario": "verification-phantom-completion",
  "attempt": 1,
  "harness": "opencode",
  "adviser_model": "configured-expensive-adviser",
  "lead_model": "luna-5.4",
  "worker_model": "gpt-5.4-mini",
  "status": "pass",
  "wall_clock_seconds": 123.4,
  "input_tokens": 10000,
  "output_tokens": 2000,
  "total_tokens": 12000,
  "cost_usd": 0.12,
  "invalid": false,
  "failure_category": null
}
```

Unknown measurements are `null`, not zero. Invalid infrastructure attempts are
retained and excluded from pass-rate denominators only under the published
replacement policy.
