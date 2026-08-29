# Governance verifier routing (Phase 3A, dated 2026-08-29)

Four candidate "governance verifier" implementations exist across the
guardspine-ai-ops stack. Only one is live. This document is the routing
table this repo's `guardspine/lib/check-governance-routing.cjs` gate keeps
honest going forward.

| #   | Implementation                                                                                  | Location                                                                       | Status                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| --- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `/council/vote` REST endpoint                                                                   | `guardspine-internal` (GuardSpine product monorepo, off-limits to this effort) | **Demo mode**, and the Railway service is currently in a FAILED deploy state (confirmed via `railway service status`). Zero real traffic.                                                                                                                                                                                                                                                                                                                            |
| 2   | `council-vote-13-persona.json` workflow                                                         | `n8n-nodes-guardspine/examples/` (template only)                               | **Never imported into production n8n.** Confirmed absent from all 151 live workflows on the real instance, checked twice across this effort. Zero real traffic.                                                                                                                                                                                                                                                                                                      |
| 3   | `OpenClawConnector` (`connector.py`) bridging to `openclaw-hardening`'s council/gate/quarantine | `guardspine/extensions/guardspine/connector.py` in this repo                   | **Real, working code -- but never invoked.** `plugin.js` (the actual loaded OpenClaw extension) never references it; the only other reference in this repo is a documentation file. Confirmed mechanically, with a positive control, by `guardspine/lib/check-governance-routing.cjs`. Zero real traffic.                                                                                                                                                            |
| 4   | Self-contained 3-model council inside `plugin.js`                                               | `guardspine/extensions/guardspine/plugin.js`                                   | **This is the live, production verifier.** Declared as the plugin's `main` entry point, hooked into OpenClaw's `before_tool_call` event, gates every real tool call through L0-L4 risk tiers, runs a real 3-model council (haiku / gemini-flash / gpt-5.4-mini via LiteLLM) on L3, an Opus L3.5 tie-breaker on deadlock, and Discord/Slack L4 human approval with self-approval prevention. Writes hash-chained evidence packs and posts decisions to telemetry-api. |

## Why the routing table looks like this

The essay's Non-Self-Certification argument (independent verification, a
generator that cannot influence what the verifier sees) is real and already
implemented -- just in a different place than earlier passes of this
investigation assumed. Rows 1-3 were reasonable candidates to have been
"the" verifier based on their design and documentation; none of them turned
out to be wired to real traffic. Row 4 is unglamorous (it lives inside a
single large `plugin.js`, not a dedicated service) but is the one that
actually runs.

## What this phase deliberately did NOT do

Per the phase's own constraint (no policy change): row 3's bridge was left
**dormant, not activated**. Wiring `connector.py` into the live path would
add a second, parallel governance system alongside `plugin.js`'s own
council -- a real architectural and policy decision, not a routing cleanup.
It was documented and clearly marked (see the docstring in `connector.py`)
so it stops reading as active governance to anyone who finds it later, but
the code itself is untouched otherwise: this is a labeling and guard-rail
change, not a behavior change.

## The gate

`node guardspine/lib/check-governance-routing.cjs` (wired into CI via
`guardspine/lib/check-governance-routing.test.cjs`) fails if either:

- `plugin.js` starts referencing `connector.py`, `OpenClawConnector`,
  `openclaw-hardening`, or any subprocess mechanism (`child_process`) --
  i.e. row 3 silently going live without anyone deciding that on purpose.
- `plugin.js`'s own council (`runCouncilReview`) stops being defined,
  aliased, and called from `before_tool_call` -- i.e. row 4 silently going
  dark with nothing else picking up the slack.

Both directions are covered by a positive control (the test suite proves
each check can actually fail, not just always pass) rather than an
unverified absence claim.
