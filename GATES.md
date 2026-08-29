# Phase 3B Gate: evidence-pack durability

## G1: the extracted evidence-pack module's own tests pass, including a positive control proving the durability fix can actually fail

CHECK: node guardspine/lib/evidence-pack.test.cjs
EXPECT: All evidence-pack assertions passed.

## G2: Phase 3A's governance-routing gate still passes against the modified plugin.js (extraction must not change routing/wiring)

CHECK: node guardspine/lib/check-governance-routing.test.cjs
EXPECT: All governance-routing assertions passed.

## G3: plugin.js still parses (syntax-only smoke check; it cannot be safely required standalone -- it registers live network/Discord/Slack hooks)

CHECK: node -c guardspine/extensions/guardspine/plugin.js
EXPECT: (no output, exit 0)
