# Work: unknown discount code charges full price

Status: complete
Harness: local-api
PID: 355
Agent session: current
PID status: alive
Last PID signal: started
Last task-file transition: completed
Initial estimate: minimum 2 / maximum 5 active minutes

## Запрос

Воспроизвести пользовательский сбой для неизвестного discount code, найти root cause,
внести минимальное полное исправление, добавить runnable regression test и доказать
прохождение product acceptance command.

## Исследование

`node -e "const {finalPrice}=require('./src/pricing.js'); console.log(finalPrice(100, 'BOGUS'))"`
возвращает `NaN`. `RATES['BOGUS']` равен `undefined`, поэтому `price - price * rate`
становится арифметикой с `undefined`.

## План

1. Заменить отсутствующую ставку на `0`.
2. Добавить `test/pricing.test.js` с неизвестным кодом и существующей скидкой.
3. Запустить regression test и `bash checks/acceptance.sh`.

## Выполнение и доказательства

- В `getDiscountRate` добавлен fallback `0` через `RATES[code] ?? 0`.
- Добавлен runnable test `test/pricing.test.js`.
- Пользовательский repro после исправления: `100`.
- `node test/pricing.test.js`: passed (`pricing regression tests passed`).
- `bash checks/acceptance.sh`: passed, exit code `0`.
