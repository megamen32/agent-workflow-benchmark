# Why these benchmarks

## Что именно мы измеряем

Не «какая модель умнее», а `workflow + harness + правила + модельная
топология`. Любой model benchmark уже неявно тестирует обвязку запуска, prompt,
инструменты, лимиты и проверку результата. Поэтому честнее вынести workflow в
самостоятельную единицу сравнения.

Workflow может иметь одну модель, две модели или три модели. Это уровни
умности/ответственности, а не уровни делегации: одна модель может сама
работать без дочерних вызовов, а связи между моделями всегда задаёт сам
workflow. Последовательный workflow не превращается в параллельный только ради
красивой архитектуры.

## Наши поведенческие проверки

В текущую кампанию мы добавили пять сценариев Quorum:

- `claim-without-verification-naive` — не заявлять «готово» до проверки;
- `cost-spec-plan-duplication` — не смешивать spec и plan в один артефакт;
- `cost-trivial-task-review-fanout` — не порождать армию агентов для мелкой
  задачи;
- `verification-holds-under-just-confirm-pressure` — не пропускать проверку
  под давлением «просто подтверди»;
- `verification-phantom-completion` — ловить ложное завершение и фиктивный
  отчёт о проверках.

Это не абстрактные model IQ tests: они проверяют именно рабочее поведение
обвязки, её правила стоимости и её реальную проверку результата.

## Что входит в наш benchmark pack

### 1. Quorum / Superpowers Evals — основной behavioral слой

[Superpowers](https://github.com/obra/superpowers) — самый популярный из
рассмотренных workflow. Его официальный eval lab
[Quorum](https://github.com/prime-radiant-inc/superpowers-evals) запускает
реальные coding-agent CLI, проводит их через сценарии, сохраняет trajectory и
проверяет результат как языковой оценкой, так и deterministic post-checks.

Мы берём Quorum потому что он лучше всего отвечает на вопрос «как workflow
заставляет агента работать»: делегация, verification reflex, review,
worktree-поведение, лишний fan-out и соблюдение процесса. Это основной
behavioral benchmark, но не нейтральный абсолют: его corpus исторически создан
для Superpowers. Поэтому мы используем переносимую часть сценариев и не выдаём
результат Quorum за универсальную истину.

### 2. AI Workflow Benchmark — независимый real-repo слой

[AI Workflow Benchmark](https://github.com/xmpuspus/ai-workflow-benchmark)
измеряет не только capability модели, а связку coding tool + workflow на
реальных repository-задачах. Он нужен как независимая проверка, чтобы LHC не
выигрывал только потому, что мы выбрали тесты, выросшие из Superpowers.

Ограничение фиксируем заранее: его корпус и технологический профиль уже не
являются универсальными для всех языков и типов продукта. Поэтому это второй
слой подтверждения, а не замена Quorum.

### 3. SkillsBench — слой миграции features → skills

[SkillsBench](https://github.com/benchflow-ai/skillsbench) сравнивает режимы без
skill, с curated skill и с самостоятельно созданным skill, используя задачи с
эталонным решением и verifier.

Мы берём его не для общего рейтинга workflow, а для конкретного вопроса: стало
ли лучше после превращения LHC features в skills. Это отдельный эксперимент,
иначе эффект skills смешается с эффектом всего оркестратора.

## Что мы используем как методику, но не как отдельный benchmark

[ECC](https://github.com/affaan-m/ECC) полезен своим A/B-подходом: одна модель,
одна задача, workflow включён или выключен, сравниваются diff, логи и результат.
Но у него нет такого же стабильного общего public corpus, поэтому мы берём
методику, а не объявляем ECC нашим основным benchmark.

[gstack](https://github.com/garrytan/gstack) полезен smoke/E2E-проверками
отдельных ролей и пользовательских flows, но это не переносимый общий corpus
для сравнения workflow. Его можно использовать как источник отдельных
сценариев, не как главный рейтинг.

## Что мы исследовали, но не включаем в scoring pack

[Spec Kit](https://github.com/github/spec-kit),
[GSD](https://github.com/gsd-build/get-shit-done),
[OpenSpec](https://github.com/Fission-AI/openspec),
[BMAD](https://github.com/bmad-code-org/bmad-method) и
[wshobson/agents](https://github.com/wshobson/agents) важны для карты рынка и
идей, но на момент выбора не давали общего переносимого workflow corpus с
достаточной adoption/eval-доказательностью.

## Как ранжируем результат

Главные оси — качество и цена:

- `quality`: pass rate и число успешно завершённых задач;
- `price`: фактическая стоимость на успешную задачу;
- `speed`: wall-clock, вторичная ось по выбору пользователя;
- `tokens`: диагностическая величина, не самостоятельный рейтинг.

Если workflow решил ноль задач, его цена за успешную задачу не равна нулю и не
сравнивается: результат просто остаётся quality failure. При одинаковом
качестве предпочтительнее более дешёвый workflow. При конфликте качества и
цены публикуем обе оси и Pareto-frontier, не придумывая универсальный вес.

Цена берётся по приоритету: provider/account-effective cost, официальный прайс,
затем датированный snapshot [models.dev](https://models.dev/). Для подписки,
relay или локального запуска без достоверной effective cost пишем `null`, а не
фальшивый `$0.00`.

## Полные транскрипты

Мы публикуем полный sanitized transcript каждого прогона, а не только verdict.
В репозитории остаются manifest, SHA-256 и ссылка на asset; сами сжатые JSONL
архивы лежат в GitHub Release. Это сохраняет воспроизводимость и позволяет
читать, что реально делал агент, не превращая обычный clone в склад логов.
