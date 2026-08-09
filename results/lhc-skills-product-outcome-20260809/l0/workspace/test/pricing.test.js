const assert = require('node:assert/strict');
const { finalPrice } = require('../src/pricing.js');

assert.equal(finalPrice(100, 'BOGUS'), 100);
