# 271 000 звёзд, 6,7 млн токенов — и всё это ради десяти маленьких багфиксов?

> **Обновление:** этот раунд теперь классифицируется только как
> [workflow-overhead baseline](RESULTS-HARD-SWEBENCH-VERIFIED-10-2026-08-12.md).
> Он не отвечает на вопрос, кто лучше решает сложные repository issues. Для
> quality comparison проведён отдельный sanitized SWE-bench Verified раунд.

Мы взяли два широко известных workflow для coding agents, наш
business-first workflow и чистый Codex без дополнительного процесса. Затем
дали каждому одну модель, одинаковое окружение и десять коротких задач.

Результат получился неудобным, а потому полезным:

> Все четыре участника исправили 10 из 10 ошибок. Самым быстрым и экономным
> оказался Codex без workflow. Процесс не добавил качества — только накладные
> расходы.

Это не означает, что workflow бесполезны. Это означает, что workflow должен
оправдывать собственную стоимость сложностью задачи, а не включаться по
умолчанию.

## Кто участвовал

### Superpowers 6.2.0

[Superpowers](https://github.com/obra/superpowers) — самый популярный из
включённых в этот раунд внешних workflow: **271 142 GitHub stars** на момент
снимка 12 августа 2026 года. Это полноценная методология разработки с
компонуемыми skills, обязательным bootstrap, systematic debugging и TDD.

В бенче использовался официальный release 6.2.0, commit
[`3dcbd5c`](https://github.com/obra/superpowers/commit/3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9).

### Get Shit Done 1.22.4

[Get Shit Done](https://github.com/gsd-build/get-shit-done) — второй широко
известный внешний workflow в сравнении: **64 715 GitHub stars** на тот же
момент. GSD строит spec-driven процесс вокруг planning state, phase execution,
context engineering и специализированных агентов.

В бенче использовался официальный release 1.22.4, commit
[`2eaed7a`](https://github.com/gsd-build/get-shit-done/commit/2eaed7a8475839958f9ec76ca4c26d9a0bbfc33f).

### Last Human Commit business-first

[Last Human Commit](https://github.com/megamen32/LastHumanCommit) — наш
workflow. В проверяемой версии бизнес-результат и кратчайшая реальная canary
первичны, а роли, гейты, delegation и durable state подключаются только когда
их ожидаемая польза выше задержки.

Использовался commit `2c29b3e`.

### Codex control

Codex CLI 0.146.0 без дополнительного workflow. Это контрольная группа: та же
модель, тот же prompt, fixture, контейнер, timeout и executable acceptance.

## И всё это ради чего?

Ради десяти локальных JavaScript contract bugs:

| № | Задача | Требуемое поведение |
|---:|---|---|
| 1 | `unknown-discount` | Неизвестный discount code означает скидку `0` |
| 2 | `pagination-offset` | Одноиндексные страницы дают правильный offset |
| 3 | `boolean-parser` | `true`/`false` разбираются без truthy-ловушки |
| 4 | `first-write-idempotency` | Дедупликация сохраняет первую запись и порядок |
| 5 | `falsy-config-overrides` | Явный `0` не заменяется default-значением |
| 6 | `cache-ttl-units` | TTL в секундах корректно сравнивается с ms timestamps |
| 7 | `chunk-tail` | Последний chunk не теряется, размер `0` запрещён |
| 8 | `safe-divide-contract` | Деление на ноль возвращает `null` |
| 9 | `canonical-email` | Email нормализуется по пробелам и регистру |
| 10 | `quoted-csv-field` | CSV понимает запятые и doubled quotes внутри кавычек |

Каждая задача требовала не только patch, но и отдельный запускаемый regression
test. Pass/fail определялся детерминированной командой после завершения агента,
а не субъективной оценкой LLM.

## Главный результат

| Workflow | Успех | Медиана на задачу | Суммарное task time | Всего токенов | Медиана токенов | Время к control | Токены к control |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Codex control** | **10/10** | **39,58 с** | **425,30 с** | **852 364** | **79 185** | **1,00×** | **1,00×** |
| LHC business-first | 10/10 | 54,94 с | 545,95 с | 1 184 331 | 120 213 | 1,39× | 1,39× |
| Superpowers 6.2.0 | 10/10 | 65,28 с | 653,91 с | 1 875 325 | 186 798 | 1,65× | 2,20× |
| GSD 1.22.4 | 10/10 | 253,94 с | 2 697,22 с | 6 742 275 | 674 561 | 6,42× | 7,91× |

Quality floor у всех одинаковый: **100%**. Поэтому Pareto-победитель этого
раунда — control. Он дал тот же подтверждённый результат быстрее и с меньшим
числом токенов.

Среди полноценных workflow первым оказался LHC:

- на **15,8% быстрее** Superpowers по median task time;
- на **36,8% меньше** total tokens, чем Superpowers;
- на **78,4% быстрее** GSD;
- на **82,4% меньше** total tokens, чем GSD.

Но главный optimisation target находится у нас самих: LHC всё ещё потребовал
примерно на **39% больше времени и токенов**, чем чистый Codex, не подняв
качество на этом классе задач.

## Время каждой задачи

Значения ниже — wall-clock секунды одной agent cell.

| Задача | Control | LHC | Superpowers | GSD |
|---|---:|---:|---:|---:|
| `unknown-discount` | **38,74** | 42,46 | 62,55 | 265,78 |
| `pagination-offset` | **32,97** | 51,61 | 58,44 | 241,11 |
| `boolean-parser` | **40,99** | 62,21 | 66,32 | 233,42 |
| `first-write-idempotency` | **48,69** | 51,71 | 64,45 | 242,10 |
| `falsy-config-overrides` | **40,42** | 55,24 | 66,57 | 439,69 |
| `cache-ttl-units` | **38,53** | 55,04 | 63,80 | 282,28 |
| `chunk-tail` | **61,46** | 68,95 | 78,06 | 306,13 |
| `safe-divide-contract` | **32,24** | 46,90 | 68,24 | 271,14 |
| `canonical-email` | **34,39** | 57,00 | 59,37 | 175,81 |
| `quoted-csv-field` | 56,87 | **54,84** | 66,11 | 239,75 |

LHC выиграл у control одну задачу из десяти по времени; control — остальные
девять.

## Токены каждой задачи

Это provider-reported token accounting, включая cache accounting. Это полезный
TCO proxy, но не денежная цена.

| Задача | Control | LHC | Superpowers | GSD |
|---|---:|---:|---:|---:|
| `unknown-discount` | **64 553** | 100 515 | 185 014 | 689 040 |
| `pagination-offset` | **65 148** | 114 585 | 140 165 | 580 048 |
| `boolean-parser` | **79 990** | 126 773 | 162 097 | 631 331 |
| `first-write-idempotency` | **118 673** | 125 596 | 212 389 | 622 959 |
| `falsy-config-overrides` | **79 672** | 123 012 | 199 195 | 765 803 |
| `cache-ttl-units` | **78 699** | 91 765 | 179 252 | 660 082 |
| `chunk-tail` | **117 662** | 145 669 | 188 475 | 977 647 |
| `safe-divide-contract` | **65 660** | 117 414 | 185 121 | 828 974 |
| `canonical-email` | **78 527** | 115 577 | 201 676 | 293 390 |
| `quoted-csv-field` | **103 780** | 123 425 | 221 941 | 693 001 |

Control использовал меньше токенов во всех десяти задачах.

## Что именно измерялось

- 10 независимых задач, свежий Git fixture для каждой cell;
- один model route: `gpt-5.6-luna`;
- последовательное выполнение, не более одного child;
- один Docker base contract и одинаковая сеть;
- timeout 600 секунд на cell;
- одинаковая auth source и отсутствие cross-run memory;
- один executable post-check и обязательный regression test;
- LLM judge и workflow-compliance не влияли на pass/fail;
- 40 из 40 cells валидны, infrastructure-invalid cells: `0`.

As-run manifest SHA-256:

```text
e9af08c92073790dd4ac4937d2331f193834272c881af2669c4b065f6ef0d6e4
```

Точная конфигурация кампании находится в
[`configs/business-first-10.yaml`](../configs/business-first-10.yaml).

## Почему workflow потратили больше

### Superpowers

Superpowers действительно активировал официальный bootstrap, systematic
debugging и TDD. На сложной ошибке эта дисциплина может предотвратить неверный
patch. Здесь acceptance уже был узким, детерминированным и локальным, поэтому
дополнительное рассуждение не изменило 10/10, но увеличило время и token use.

### GSD

GSD получил собственные официальные project preconditions: Git `main`,
`.planning/ROADMAP.md`, `.planning/STATE.md` и `$gsd-quick`. Он создавал
planning/state/commit artifacts вокруг каждого маленького bugfix. Это полезная
continuity-машина для большой работы, но дорогое обрамление для функции на
несколько строк.

Во время запуска обнаружился и operational defect: installer GSD 1.22.4
сгенерировал несколько role TOML с неэкранированными backslash, которые Codex
CLI 0.146.0 отклонил. `$gsd-quick` всё равно активировался и завершил 10/10, но
ошибка установки остаётся частью реального TCO.

### LHC

Business-first версия уже отказывается от обязательной оркестрации и широких
гейтов, если direct route дешевле. Поэтому она заметно экономнее двух внешних
workflow. Однако наличие большого instruction surface само по себе осталось
налогом даже тогда, когда Lead выбрал прямой путь.

## Практическое решение

Для короткого понятного bugfix default должен быть таким:

```text
real consumer path
→ smallest reproduction
→ failing regression test
→ minimal patch
→ regression
→ cheapest business canary
```

Без обязательных Overseer, Reviewer, task-card ceremony, phase planning или
архитектурного эссе.

LHC и другие workflow следует подключать, когда появляется хотя бы одна
причина, способная окупить overhead:

- production path проходит через несколько компонентов;
- неверный маршрут дорог или необратим;
- исследование уже повторялось и требует durable receipt;
- несколько owners или параллельных Workers;
- compaction и long-horizon continuity;
- реальный release, migration или user-facing canary;
- качество control начинает падать.

Коротко: **не “какой workflow лучший вообще?”, а “добавил ли workflow качество
на этой задаче больше, чем стоил?”**

## Что этот результат не доказывает

- `n=10`, один запуск на задачу: это matched canary, не статистический
  leaderboard.
- Задачи короткие, локальные и синтетические. Они не проверяют архитектурное
  планирование, многодневную continuity, parallel delegation, compaction
  recovery, production rollout или disputed acceptance.
- Денежная стоимость неизвестна: provider не вернул billable charge. `unknown`
  нельзя заменять на `$0`.
- Результат относится к одному model route и этим frozen revisions.
- BMAD и Spec Kit не включались: сравнивать их многофазные planning contracts на
  одноминутных bugfix-задачах было бы task-class mismatch.

Следующий честный раунд должен состоять из десяти сложных planning/architecture
и production-path задач. Только там workflow получают возможность не просто
потратить больше, а реально поднять quality floor.

## Полные доказательства

- [Исходный result report](RESULTS-BUSINESS-FIRST-10-2026-08-12.md)
- [Frozen campaign manifest](../configs/business-first-10.yaml)
- [Fixtures и acceptance](../scenarios/business-first-10/fixture)
- [Полный evidence bundle: receipts, summaries, SHA-256 и redacted transcripts](https://github.com/megamen32/agent-workflow-benchmark/releases/download/business-first-10-20260812/business-first-10-complete-evidence.tar.zst)
- [SHA-256 evidence bundle](https://github.com/megamen32/agent-workflow-benchmark/releases/download/business-first-10-20260812/business-first-10-complete-evidence.sha256)

Полный bundle содержит результаты всех 40 cells. Перед публикацией transcript
archives прошли отдельную credential-redaction и secret scan; SHA-256 были
пересчитаны после очистки. Manifest каждого запуска и digest материализованных
inputs сохранены в receipts.
