Status: complete
Harness: Codex
PID: unknown
Agent session: current
PID status: exited
Last PID signal: completed verification
Last task-file transition: completed
Initial estimate: minimum 2 / maximum 5 active minutes

# Задача

Исправить расчёт полной цены для неизвестного discount code по supplied fixture.

## План и критерии

- [x] Воспроизвести `NaN` и установить корень проблемы.
- [x] Вернуть ставку `0` для неизвестного кода.
- [x] Добавить runnable regression test.
- [x] Запустить `./checks/acceptance.sh` и пользовательскую команду.

## Evidence

До исправления:

- `node -e "const {finalPrice}=require('./src/pricing.js'); console.log(finalPrice(100, 'BOGUS'))"` печатает `NaN`.
- `getDiscountRate` возвращает `undefined` для отсутствующего ключа; `price - price * undefined` становится `NaN`.

После исправления:

- `node test/pricing.test.js` прошёл.
- `./checks/acceptance.sh` прошёл.
- Пользовательская команда печатает `100`.
- `finalPrice(100, 'SAVE10')` печатает `90`.
