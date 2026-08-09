# Agent Workflow Benchmark

Модели сами по себе ничего не гарантируют. Реальный результат создаёт
workflow: обвязка, правила работы, делегация, проверка и выбор моделей.

У обвязок много, а общего benchmark почти нет. Этот проект сравнивает именно
workflow, не заставляя его быть LHC, многоуровневым или параллельным.

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

Главные критерии — качество и цена. Скорость вторична: если агент довёл дело
до конца, когда пользователь спит, лишние минуты не важны. Токены — только
диагностика: миллион токенов может стоить центы или десятки тысяч долларов.
При нулевом числе успешных задач цена за успех не ранжируется вообще.

Топология workflow записывается как есть: от нуля до трёх уровней. Benchmark
не добавляет Worker, Adviser или параллельность, которых у workflow нет.

```bash
python3 scripts/summarize_results.py results.jsonl
```

См. [протокол](docs/PROTOCOL.md), [конфигурацию](configs/campaign.yaml) и
[схему результата](docs/RESULT_SCHEMA.md).

MIT — [LICENSE](LICENSE).
