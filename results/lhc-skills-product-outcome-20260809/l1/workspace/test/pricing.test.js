const assert = require('node:assert/strict');
const { getDiscountRate, finalPrice } = require('../src/pricing.js');

assert.equal(getDiscountRate('BOGUS'), 0);
assert.equal(finalPrice(100, 'BOGUS'), 100);
assert.equal(finalPrice(100, 'SAVE10'), 90);

console.log('pricing regression tests passed');
