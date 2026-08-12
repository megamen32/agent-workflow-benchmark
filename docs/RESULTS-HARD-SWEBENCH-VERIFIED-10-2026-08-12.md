# Hard SWE-bench Verified workflow benchmark — 2026-08-12

Мы сравнили чистый Codex, наш LHC business-first и два широко известных
внешних workflow: [Superpowers](https://github.com/obra/superpowers) — около
271 тыс. GitHub stars — и [GSD](https://github.com/gsd-build/get-shit-done) —
около 65 тыс. stars на момент публикации. Один и тот же model route получил
одни и те же десять сложных repository issues; менялся только workflow.

## Короткий ответ

Предыдущий 10-task benchmark был слишком лёгким: все четыре режима получили
`10/10`, поэтому он измерял только overhead. Этот раунд использует реальные
GitHub issues из SWE-bench Verified с human difficulty `1–4 hours` или `>4
hours`, frozen repository images и official hidden-test grading.

Численный результат:

| Workflow | Resolved | Median agent time | Total agent time | Input tokens |
|---|---:|---:|---:|---:|
| GSD 1.22.4 | **2/10** | 368,81 с | 3 743,69 с | 11 317 968 |
| Codex control | 1/10 | **136,44 с** | **1 347,44 с** | **4 923 385** |
| LHC business-first | 1/10 | 163,79 с | 1 628,32 с | 6 716 583 |
| Superpowers 6.2.0 | 1/10 | 189,30 с | 1 867,71 с | 10 905 155 |

GSD решил одну дополнительную задачу (`pytest-dev__pytest-5787`), которую
остальные три workflow не решили. Все четыре режима решили
`django__django-13344`; остальные восемь задач не решил никто.

Это **не статистически доказанная победа GSD**. При `n=10` разница `2/10` и
`1/10` слишком мала для общего winner claim. Это доказательство более узкого
утверждения: на этой frozen десятке GSD дал один реальный additional resolved
issue, но потребовал примерно `2,8×` total agent time и `2,3×` input tokens
относительно control.

И всё это ради чего? Ради одной дополнительной принятой задачи из десяти.
Цена этого прироста в текущем раунде — примерно 40 дополнительных минут agent
time и 6,4 млн input tokens относительно control. У LHC и Superpowers измеренной
прибавки качества вообще не появилось.

## Почему это сильнее предыдущего раунда

- реальные repository snapshots, а не функции на несколько строк;
- 6 upstream repositories: Astropy, Django, Pylint, Pytest, Sympy, Xarray;
- official engineer-verified issues;
- 9 задач с difficulty `1–4 hours`, одна `>4 hours`;
- gold patches до 6 production files;
- hidden FAIL_TO_PASS и до 945 PASS_TO_PASS regression tests;
- agent не видит `patch`, `test_patch`, FAIL_TO_PASS или PASS_TO_PASS;
- pass/fail выставляет official SWE-bench harness, не LLM judge.
- exact public bundle содержит 40 redacted event streams, patches, receipts и
  grader logs; credential mounts и host-only hidden dataset snapshot исключены.

## Sanitized Git-history contract

Первый calibration run оказался загрязнён: official SWE-bench images содержали
полную Git history, и некоторые agents делали `git log -S`/`git show`. В
pre-sanitization run это дало GSD `2/10` и Superpowers `1/10`, но один GSD patch
имел `0,865` similarity с gold patch. Эти результаты **отброшены**.

Финальные 40 cells перезапущены полностью, чтобы избежать survivor bias. В
каждом disposable agent container:

1. исходная `.git` history удалена;
2. создан один synthetic `arena-baseline` commit;
3. `git rev-list --all --count == 1`;
4. remotes отсутствуют;
5. patch строится как `arena-baseline → final tree`;
6. hidden grading запускается только после удаления agent container.

Успешная дифференцирующая GSD cell не выполняла network lookup, не видела hidden
field names, активировала `$gsd-quick`, а similarity с gold patch составила
`0,342`.

## Per-task hidden result

| SWE-bench instance | Difficulty | Control | LHC | Superpowers | GSD |
|---|---|---:|---:|---:|---:|
| `astropy__astropy-13398` | 1–4h | fail | fail | fail | fail |
| `django__django-11885` | 1–4h | fail | fail | fail | fail |
| `django__django-13344` | 1–4h | **pass** | **pass** | **pass** | **pass** |
| `django__django-16263` | 1–4h | fail | fail | fail | fail |
| `pydata__xarray-6992` | >4h | fail | fail | fail | fail |
| `pylint-dev__pylint-4551` | 1–4h | fail | fail | fail | fail |
| `pytest-dev__pytest-5787` | 1–4h | fail | fail | fail | **pass** |
| `sympy__sympy-14248` | 1–4h | fail | fail | fail | fail |
| `sympy__sympy-16597` | 1–4h | fail | fail | fail | fail |
| `sympy__sympy-18199` | 1–4h | fail | fail | fail | fail |

## Что это говорит о workflow

### GSD

Единственный workflow, который улучшил resolved count относительно control на
этой десятке. Его planning/context machinery иногда окупается на сложной
repository задаче, но цена высока: около 62 минут суммарного agent time и 11,3
млн input tokens ради двух resolved issues.

### LHC business-first

Не улучшил quality floor относительно control: те же `1/10`, но на 21% больше
total agent time и на 36% больше input tokens. На этом наборе текущий LHC —
overhead без измеренного quality lift. Это прямой optimisation target.

### Superpowers

После удаления Git history получил те же `1/10`, что control, при `1,39×`
total agent time и `2,21×` input tokens. Ранняя дополнительная победа на Pytest
не пережила sanitation и потому не считается.

### Control

Самый дешёвый при quality floor `1/10`. Но решает только одну из десяти задач,
поэтому этот раунд уже нельзя свести к вопросу времени: абсолютное качество
низкое у всех.

## Важные ограничения

- один run на task/workflow; variance не измерена;
- `n=10`, поэтому confidence intervals широкие;
- задачи могли присутствовать в training data модели; Git-history sanitation
  не устраняет training contamination;
- agent time не включает hidden grader time;
- provider не вернул billable charge, поэтому денежная стоимость `unknown`;
- задачи намеренно hard-tail: общий resolved rate низок;
- результат относится к `gpt-5.6-luna`, Codex CLI 0.145.0 и frozen workflow
  revisions.

## Frozen contract

- Dataset: `SWE-bench/SWE-bench_Verified`
- Dataset revision: `03e151cf5560b1af6a4363c6a9d766deaaea6b56`
- Campaign config: [`configs/hard-swebench-verified-10.json`](../configs/hard-swebench-verified-10.json)
- Model: `gpt-5.6-luna`
- Control: Codex CLI 0.145.0
- LHC: `2c29b3e`
- Superpowers: `3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9`
- GSD: `2eaed7a8475839958f9ec76ca4c26d9a0bbfc33f`
- 10 exact Docker registry digests сохранены в campaign config.
- 40/40 final cells: grader errors `0`, agent timeouts `0`.
- Pairwise exact McNemar для GSD против каждого `1/10` workflow: `p=1,0`;
  numerical lead не является statistical significance.

## Решение

Предыдущий easy benchmark остаётся полезным overhead baseline, но не quality
leaderboard. Этот hard benchmark становится основной quality проверкой.

Практический вывод сейчас:

- direct/control — default для понятных коротких задач;
- GSD показал потенциальный quality lift на сложной repository работе, но его
  нужно подтвердить более крупным `n` и повторными runs;
- текущий LHC не доказал пользу на hard set, поэтому нельзя утверждать, что он
  лучше готовых конкурентов;
- следующий раунд должен расширить denominator вокруг задач средней сложности,
  где expected control rate ближе к 20–50%, а не выбирать ещё более тяжёлый
  tail.
