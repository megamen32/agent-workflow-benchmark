// Pricing helpers for checkout.

const RATES = {
  SAVE10: 0.1,
  SAVE20: 0.2,
  HALFOFF: 0.5,
};

function getDiscountRate(code) {
  return RATES[code] ?? 0;
}

function finalPrice(price, code) {
  const rate = getDiscountRate(code);
  return price - price * rate;
}

module.exports = { getDiscountRate, finalPrice };
