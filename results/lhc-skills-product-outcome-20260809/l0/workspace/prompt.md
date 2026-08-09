There's a bug in our checkout code. When a customer enters a discount code
we don't recognize, the order total comes out wrong instead of just charging
full price. Running

    node -e "const {finalPrice}=require('./src/pricing.js'); console.log(finalPrice(100, 'BOGUS'))"

prints `NaN`. It should print `100` (full price, no discount) for an unknown
code. Fix the bug, leave a runnable regression test for the unknown-code case,
and verify the acceptance checks before claiming completion.
