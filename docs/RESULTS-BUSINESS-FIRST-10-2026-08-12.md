# Business-first workflow benchmark — 2026-08-12

## Claim

На десяти коротких детерминированных JavaScript bugfix/API-contract задачах
все четыре workflow достигли одинакового результата: `10/10`. Поэтому этот
раунд не доказывает превосходство по качеству. Он показывает различие в
стоимости исполнения при достигнутом quality floor.

## Matched contract

- 10 независимых задач, новый Git fixture на каждую ячейку.
- Один model route: `gpt-5.6-luna`.
- Одинаковый Docker base, auth source, network и 600-second cell timeout.
- Один as-run manifest SHA-256:
  `e9af08c92073790dd4ac4937d2331f193834272c881af2669c4b065f6ef0d6e4`.
- Pass/fail определён executable post-check и обязательным regression test.
- LLM judge и workflow-compliance не влияют на pass/fail.
- No cross-run memory; 0 infrastructure-invalid cells.
- Billable charge provider не вернул: cost остаётся `unknown`, не `0`.

Workflow revisions:

- LHC current: `2c29b3e`.
- Superpowers 6.2.0: `3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9`.
- GSD 1.22.4: `2eaed7a8475839958f9ec76ca4c26d9a0bbfc33f`.
- Control: Codex CLI 0.146.0 без дополнительного workflow.

## Results

| Arm | Success | Median/task | Total task wall | Total tokens | Median tokens/task | Relative median vs LHC |
|---|---:|---:|---:|---:|---:|---:|
| Codex control | 10/10 | 39.58s | 425.30s | 852,364 | 79,185 | 0.72× |
| LHC current | 10/10 | 54.94s | 545.95s | 1,184,331 | 120,213 | 1.00× |
| Superpowers 6.2.0 | 10/10 | 65.28s | 653.91s | 1,875,325 | 186,798 | 1.19× |
| GSD 1.22.4 | 10/10 | 253.94s | 2,697.22s | 6,742,275 | 674,561 | 4.62× |

## Interpretation

1. На этом простом task class дополнительный workflow не поднял quality floor:
   control уже решил 10/10.
2. LHC business-first сохранил 10/10, но добавил 39% total tokens и 39% median
   wall-time относительно control. Это текущий optimisation target.
3. LHC был быстрее Superpowers на 15.8% по median task time и использовал на
   36.8% меньше total tokens.
4. LHC был быстрее GSD на 78.4% по median task time и использовал на 82.4%
   меньше total tokens.
5. GSD успешно выполнил все задачи после получения своего официального
   project precondition (`Git main` + `.planning/ROADMAP.md`/`STATE.md`), но
   quick workflow создавал plan/state/commit artifacts на каждую маленькую
   задачу. Для этого task class это высокий TCO.
6. Победитель этого раунда по Pareto — control: тот же quality floor при
   меньшем времени и token use. LHC не должен скрывать этот результат.
7. GSD installer 1.22.4 с Codex CLI 0.146.0 генерировал несколько role TOML,
   которые Codex отклонял из-за неэкранированных backslash. `$gsd-quick`
   продолжал работу и закончил 10/10, но это реальный compatibility defect и
   часть operational TCO.

## Limits

- `n=10`, один прогон на задачу: это canary, не статистический leaderboard.
- Задачи короткие и локальные. Они не измеряют архитектурное планирование,
  large-project continuity, compaction recovery, parallel delegation,
  high-risk review или production canary quality.
- BMAD и Spec Kit не включены: их официальные многофазные preconditions не
  эквивалентны короткому bugfix task class. Имитировать их одним prompt было бы
  нечестно.
- Token counts включают provider cache accounting из runner receipts и служат
  diagnostic/TCO proxy; billable cost неизвестен.
- Один сильный model route означает, что результат нельзя переносить на другие
  модели без повторного matched run.

## Decision

Применять LHC business-first как selective workflow, а не как обязательный налог
на каждую задачу:

- для ясного локального bugfix default — direct/control-like route;
- подключать LHC coordination, durable research, time control и roles, когда
  есть multi-hop production path, повторяемое исследование, несколько owners,
  compaction risk, real-user canary или consequential release;
- следующий benchmark должен специально проверять этот сложный task class,
  где workflow имеет шанс улучшить quality, а не только увеличить cost.

## Evidence

- Manifest: [`configs/business-first-10.yaml`](../configs/business-first-10.yaml)
- Fixture: [`scenarios/business-first-10/fixture`](../scenarios/business-first-10/fixture)
- Per-cell receipts and redacted transcript archives:
  `results/business-first-10-run/`
- Точный as-run manifest встроен в каждый `campaign-transcripts.tar.zst`.
- Reusable manifest после run получил deterministic Git setup вместо ручного
  nested `.git`; его текущий dry-run SHA-256:
  `84f38358ea036750aec0ceb2bbcc3129599847c37be054c2036760489777f3d7`.
- Calibration runs: `results/business-first-10-smoke/` and
  `results/business-first-10-smoke2/`
- Runner summary fields: `results.jsonl`, `summary.json`,
  `campaign-transcripts.tar.zst` in each shard.
