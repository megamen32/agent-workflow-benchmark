# Agent Workflow Benchmark

| Campaign | Guard pass rate | Wall-clock | Cost | Status |
|---|---:|---:|---:|---|
| L0 — Luna → GPT-5.4 Mini | **4/5 · 80%** | 31m 43s | **$0.2762** | pilot complete |
| L1 — MiniMax M3 → MiniMax M2.7 | **3/5 · 60%** | 24m 33s | n/a* | pilot complete |

`*` MiniMax ran through an unpriced subscription route; its cost is not
invented. Full results and failures are in
[RESULTS-LHC-CODEX-2026-08-09.md](docs/RESULTS-LHC-CODEX-2026-08-09.md).

Этот верхний блок — исторический workflow-guard pilot, а не общий benchmark
качества моделей или инженерных результатов. Новый обзор открытых бенчмарков
и методика сравнения находятся в [research/](research/README.md): там отдельно
разведены reference/oracle-проверки и «не хуже по бизнес-результату», а также
качество, фактическая цена и время.

Модели сами по себе ничего не гарантируют. Реальный результат создаёт
workflow: обвязка, правила работы, связи между моделями, проверка и выбор моделей.

У обвязок много, а общего benchmark почти нет. Этот проект сравнивает именно
workflow, не заставляя его быть [LHC](https://github.com/megamen32/LastHumanCommit)
или параллельным.

Мы берём три взаимодополняющих источника:

- **Quorum / Superpowers Evals** — основной behavioral benchmark: реальные
  coding-agent CLI, сценарии, deterministic checks и receipts. Superpowers —
  самый популярный workflow из рассмотренных.
- **AI Workflow Benchmark** — независимая проверка на real-repo задачах, чтобы
  не судить все workflow только по тестам Superpowers.
- **SkillsBench** — отдельная проверка эффекта skills, когда workflow
  переходит от монолитных features к skills.

ECC используется как источник A/B-методики; gstack и остальные популярные
workflow входят в обзор, но не имеют подходящего общего переносимого корпуса.
Подробное обоснование: [WHY-BENCHMARKS.md](docs/WHY-BENCHMARKS.md).

Главные критерии — product quality и цена. Скорость вторична: если агент довёл дело
до конца, когда пользователь спит, лишние минуты не важны. Токены — только
диагностика: миллион токенов может стоить центы или десятки тысяч долларов.
При нулевом числе успешных задач цена за успех не ранжируется вообще.

Топология workflow записывается как есть: одна, две или три модели. Связи
между ними определяет сам workflow. Benchmark не добавляет Worker, Adviser или
параллельность, которых у workflow нет.

В текущий **workflow-guard** campaign pack добавлены пять проверок поведения: верификация перед
заявлением результата, разделение spec/plan, отсутствие лишнего fan-out на
маленькой задаче, устойчивость к давлению «просто подтверди» и обнаружение
phantom completion. Это не общий тест инженерного качества: сложные
product-outcome задачи идут отдельным треком.

Полные транскрипты — обязательные артефакты каждого опубликованного прогона.
В git хранится manifest с хэшами, а сжатые JSONL-транскрипты — в release
assets; перед публикацией они проходят secret/privacy redaction.

Исполняемый runner принимает [unified manifest](configs/manifest.example.yaml).
Codex и OpenCode запускаются только внутри arm-specific Docker images,
зафиксированных digest'ом; verifier запускается в том же контейнере. Mutable
tags, host-side harness execution и host-side acceptance checks запрещены.

```bash
python3 scripts/run_campaign.py configs/manifest.example.yaml --dry-run
python3 scripts/run_campaign.py configs/manifest.example.yaml --output results/example
```

Перед реальным запуском замените примерные image/digest на существующие локально
закэшированные образы; runner использует `docker --pull never`.

```bash
python3 scripts/summarize_results.py results.jsonl
```

См. [протокол](docs/PROTOCOL.md), [runner contract](docs/RUNNER.md), [unified manifest](configs/manifest.example.yaml) и
[схему результата](docs/RESULT_SCHEMA.md).

MIT — [LICENSE](LICENSE).
