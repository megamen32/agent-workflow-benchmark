#!/usr/bin/env sh
set -eu

git init -q -b main
git config user.email benchmark@local.invalid
git config user.name "Benchmark Fixture"
git add package.json src/contracts.js .planning/ROADMAP.md .planning/STATE.md .planning/config.json
git commit -qm "fixture: seed contract bugs"
