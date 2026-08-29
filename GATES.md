# Phase 3A Gate: governance verifier routing consolidation

## G1: the routing check is proven (positive controls prove it can fail) and passes against the real plugin.js

CHECK: node guardspine/lib/check-governance-routing.test.cjs
EXPECT: All governance-routing assertions passed.

## G2: the CLI gate itself runs clean

CHECK: node guardspine/lib/check-governance-routing.cjs
EXPECT: Governance routing OK: plugin.js's own 3-model council is wired to before_tool_call; no reference to the dormant connector.py/openclaw-hardening bridge.
