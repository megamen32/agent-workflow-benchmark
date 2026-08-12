const DISCOUNTS = { SAVE10: 0.1, SAVE20: 0.2 };

function discountRate(code) {
  return DISCOUNTS[code];
}

function pageOffset(page, pageSize) {
  return page * pageSize;
}

function parseBoolean(value) {
  return Boolean(value);
}

function uniqueById(rows) {
  return [...new Map(rows.map((row) => [row.id, row])).values()];
}

function mergeLimits(defaults, overrides) {
  return {
    retries: overrides.retries || defaults.retries,
    timeoutMs: overrides.timeoutMs || defaults.timeoutMs,
  };
}

function cacheExpired(createdAtMs, ttlSeconds, nowMs) {
  return nowMs - createdAtMs >= ttlSeconds;
}

function chunk(items, size) {
  const result = [];
  for (let index = 0; index < items.length - size; index += size) {
    result.push(items.slice(index, index + size));
  }
  return result;
}

function safeDivide(numerator, denominator) {
  return numerator / denominator;
}

function normalizeEmail(value) {
  return value.trim();
}

function csvFields(line) {
  return line.split(",");
}

module.exports = {
  discountRate,
  pageOffset,
  parseBoolean,
  uniqueById,
  mergeLimits,
  cacheExpired,
  chunk,
  safeDivide,
  normalizeEmail,
  csvFields,
};
