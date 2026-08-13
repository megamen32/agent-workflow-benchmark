# Hard SWE-bench Sol rerun

Status: full campaign
Started at: 2026-08-12T23:18:00+03:00
Canary estimate: 5 / 10 active minutes
Full campaign estimate after canary: 35 / 90 active minutes
Active-time source: not continuously measured

## Business outcome

Rerun the exact frozen 10-task, 4-workflow sanitized campaign with only the
model changed from `gpt-5.6-luna` to `gpt-5.6-sol`, then compare quality and
cost without changing tasks, images, prompts or workflow revisions.

## Canary

Run `django__django-13344/control` through the sanitized launcher and official
hidden grader. Continue to all 40 cells only if the Sol route executes and the
grader emits a valid result.

Result: `django__django-13344/control` resolved by the official hidden grader.
Agent time 223.95 s, grader time 103.50 s, input tokens 909,783, output tokens
6,943, sanitized Git history true, timeout false.
