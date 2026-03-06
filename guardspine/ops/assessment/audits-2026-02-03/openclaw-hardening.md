# OpenClaw Hardening - Linus Audit (2026-02-03)

## Scorecard (0-10)

- Contract correctness: 5
- Boundary hygiene: 6
- Test quality: 5
- Operational safety: 6
- Complexity / maintainability: 6

## P0 Findings (Must Fix)

None found.

## P1 Findings (Should Fix)

1. Canonical chain implementation is duplicated without parity tests
   - `hash_chain/chain.py` reimplements canonical JSON + chain hashing, but there are no golden-vector parity tests against `@guardspine/kernel` or `guardspine-verify`.
   - Impact: drift risk; bundles may verify in hardening but fail in the ecosystem.
   - Fix: Add golden-vector parity tests using the same fixtures used in the kernel/verify repos.
   - Files: `D:\Projects\openclaw-hardening\hash_chain\chain.py`, `D:\Projects\openclaw-hardening\tests\test_hash_chain.py`

2. v0.2.0 validation is incomplete (sequence + content_hash not enforced)
   - Validation and verification logic checks presence of fields and chain integrity but does not enforce `sequence` contiguity or item `content_hash` correctness.
   - Impact: spec-invalid bundles can pass internal checks and proceed through approvals.
   - Fix: enforce `sequence == index`, verify item content_hash against canonical content; fail if missing/invalid.
   - Files: `D:\Projects\openclaw-hardening\hash_chain\chain.py`, `D:\Projects\openclaw-hardening\eval\evaluate_evidence.py`, `D:\Projects\openclaw-hardening\approvals\approval_gate.py`

3. Legacy evidence packs still accepted without explicit gating
   - The approval gate and evaluation logic accept both legacy packs and v0.2.0 bundles without a strict “legacy allowed” flag.
   - Impact: non-canonical evidence can bypass chain and signature requirements.
   - Fix: add explicit config to allow/deny legacy format; default to deny in production.
   - Files: `D:\Projects\openclaw-hardening\approvals\approval_gate.py`, `D:\Projects\openclaw-hardening\eval\evaluate_evidence.py`

4. Health check does not validate Ollama reachability or model availability
   - `openclaw_integration/health_check.py` only validates config fields and local files.
   - Impact: false green when council models are unavailable or Ollama is down.
   - Fix: perform an actual `/api/tags` or small generate request for configured models.
   - File: `D:\Projects\openclaw-hardening\openclaw_integration\health_check.py`

5. Promptfoo provider emits non-spec “evidence bundles”
   - `bundle_src/bundle2/guardspine_provider.py` writes evidence artifacts with `hash` but no v0.2.0 bundle structure or immutability proof.
   - Impact: if these are used in governance decisions, integrity guarantees are void.
   - Fix: either upgrade to v0.2.0 bundles or clearly label as non-evidence diagnostics and keep them out of approval flows.
   - File: `D:\Projects\openclaw-hardening\bundle_src\bundle2\guardspine_provider.py`

## P2 Findings (Cleanup / Consistency)

1. Evidence pack schema is duplicated and not validated against examples
   - `schemas/evidence_pack.json` duplicates the canonical spec; tests only validate JSON structure, not schema conformance.
   - Impact: silent drift between schema and produced artifacts.
   - Fix: wire schema validation against emitted bundles or stored fixtures.
   - Files: `D:\Projects\openclaw-hardening\schemas\evidence_pack.json`, `D:\Projects\openclaw-hardening\tests\test_schemas.py`

2. Mixed terminology (`schema_version` vs `version`) adds confusion
   - `EvidencePack` uses `schema_version` while bundles use `version`. This leaks into metadata and docs.
   - Impact: implementers confuse legacy/modern schema fields.
   - Fix: treat `schema_version` as legacy-only and document conversion to v0.2.0 `version`.
   - Files: `D:\Projects\openclaw-hardening\bundle_src\bundle4\rlm_docsync.py`, `D:\Projects\openclaw-hardening\docs\ARCHITECTURE.md`

3. Approval channel stubs are easy to misuse
   - Discord/SMS stubs are documented but are real code paths; no explicit guard to prevent production usage.
   - Impact: false sense of human approval in L4 flows.
   - Fix: require explicit `ALLOW_STUB_CHANNELS=1` or error in production.
   - Files: `D:\Projects\openclaw-hardening\approvals\channels\discord_stub.py`, `D:\Projects\openclaw-hardening\approvals\channels\sms_stub.py`

## Concrete Fixes (High-Leverage)

1. Add kernel parity tests for `hash_chain` using golden vectors.
2. Enforce v0.2.0 sequence + content_hash validation in approval and evaluation paths.
3. Gate legacy evidence pack acceptance behind a config flag (default deny).
4. Add Ollama reachability/model preflight to health check.
5. Replace promptfoo provider evidence artifacts with real v0.2.0 bundles or label as non-evidence logs.

## Interop Risk Statement

OpenClaw Hardening produces v0.2.0 bundles but still accepts legacy artifacts and uses a local hash-chain implementation without parity tests. This combination allows spec-invalid evidence to pass internal governance and creates drift risk against the canonical GuardSpine kernel/verifier.

## Skeptical Annex (Assumptions / Edge Cases / Evidence)

- Assumptions:
  - v0.2.0 is the only canonical format in production flows.
  - Legacy evidence packs are not required for current interop guarantees.
- Edge cases not directly tested here:
  - Out-of-order `sequence` values with otherwise valid chains.
  - Very large evidence items and memory pressure in chain building.
  - Multi-model council with Ollama model eviction under load.
- Possible false positives/negatives:
  - If promptfoo artifacts are strictly test-only, downgrade P1 #5.
  - If legacy packs are intentionally supported in production, document that acceptance and tighten verification.
- Evidence reviewed:
  - `hash_chain/chain.py`
  - `bundle_src/bundle4/rlm_docsync.py`
  - `openclaw_integration/health_check.py`
  - `approvals/approval_gate.py`
  - `eval/evaluate_evidence.py`
  - `bundle_src/bundle2/guardspine_provider.py`
  - `schemas/evidence_pack.json`
