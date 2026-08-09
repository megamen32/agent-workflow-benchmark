# Why these benchmarks

Исходное решение было сформировано в чате [«SSS и notify-эскалация»](chatgpt-conversation://6a70f198-95c4-83eb-b4f7-f2e8a4444093).

## Что именно мы измеряем

Не «какая модель умнее», а `workflow + harness + правила + модельная
топология`. Любой model benchmark уже неявно тестирует обвязку запуска, prompt,
инструменты, лимиты и проверку результата. Поэтому честнее вынести workflow в
самостоятельную единицу сравнения.

Workflow может иметь ноль уровней делегации, одну модель, две модели или три.
Последовательный workflow не превращается в параллельный только ради красивой
архитектуры.

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
