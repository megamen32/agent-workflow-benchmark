#!/usr/bin/env bash
set -euo pipefail

test -f src/pricing.js
node - <<'NODE'
const {getDiscountRate, finalPrice} = require('./src/pricing.js');
const rate = getDiscountRate('BOGUS');
if (typeof rate !== 'number' || Number.isNaN(rate)) process.exit(1);
if (finalPrice(100, 'BOGUS') !== 100) process.exit(1);
if (finalPrice(100, 'SAVE10') !== 90) process.exit(1);
NODE

find . -type f -name '*test*.js' -print -quit | grep -q .
