# GuardSpine Audit Claim Validation (2026-02-03)

Scope: Validate findings across all reports in GuardSpine-Audit-Latest-2026-02-03 against current repo state.

## Summary by Report

### guardspine-main (GuardSpine backend)

- Incorrect / outdated:
  - ?SAML callback handling not implemented? is no longer true. `backend/app/services/auth_service.py` now processes SAML responses (metadata, response validation, attribute mapping, user creation). The audit finding is stale.

### guardspine-backend

- All findings confirmed in current code:
  - Kernel duplication without parity tests.
  - Import validation does not enforce `sequence` or content shape.
  - `/bundles/{id}/export` is non?spec and ambiguous.
  - Strict signature mode only Ed25519.
  - In?memory bundle store only.
  - P2 items (created_at null, wrong CLI string, verification instructions mismatch).

### guardspine-adapter-webhook

- All findings confirmed:
  - `sealBundle()` uses non?spec bundle shape and fails open.
  - Kernel typing stub is `void`.
  - README/metadata and hash redundancy issues are present.

### guardspine-connector-template

- All findings confirmed:
  - Python emitter uses non?v0.2.0 fields and non?canonical chain/root.
  - API posts to `/bundles` not `/api/v1/bundles/import`.
  - TS template schema/hashing diverges from spec.
  - README + versioning contradictions; CLI entrypoint missing.
  - P2 gaps (no tests, zip format switch not implemented, non?canonical JSON hashing).

### guardspine-kernel

- All findings confirmed:
  - Version value is not enforced in verify.
  - Proof version is implicit (not recorded in bundle).
  - Unsupported signature algorithm errors are not explicit.

### guardspine-local-council

- All findings confirmed:
  - Local hash/chain implementation without parity tests.
  - Bundle output not validated.
  - Ollama preflight missing.
  - No signature support or explicit unsigned stance.
  - Tests/docs gaps.

### guardspine-openclaw (integration)

- All findings confirmed:
  - Multiple custom canonicalization/chain implementations.
  - L4 self?approval tool lacks auth gating.
  - Evaluator schema mismatch vs rlm?docsync packs.
  - Unknown tool defaults to L2.
  - Evidence packs not imported into backend.
  - P2: `guardspine_root` unused; `created_at` not hashed.

### guardspine-product

- All findings confirmed:
  - Packaging broken (`guardspine_product` package missing).
  - Local non?kernel hashing and bespoke bundle formats.
  - DocEvidencePack not wrapped as v0.2.0 bundle.
  - Tests reference missing enums/constructors (e.g., `EvidenceType.LOG_DATA`).
  - Docs list missing files; absolute imports break installed package.
  - P2: no contract/golden tests; hash prefix ambiguity in adapters.

### guardspine-spec

- All findings confirmed:
  - README chain rule contradicts schema.
  - Examples are not v0.2.0 compliant.
  - README bundle structure diverges from schema.
  - Duplicate schema files; validate script non?portable/no validation.

### guardspine-verify

- All findings confirmed:
  - Hash chain not bound to items.
  - Version not enforced; ZIP limits missing; unsigned bundles can ?verify? with key.
  - HMAC ?base64 hex? is implied by code comment but unsupported in logic.
  - P2: README/API mismatch; legacy chain inconsistency; version label mismatch; CLI exit codes.

### n8n-nodes-guardspine

- All findings confirmed:
  - Guard nodes use `artifact_kind` not `artifact_type`.
  - No bundle import/export path; ApprovalWait fallback URL wrong; CouncilVote demo-only.
  - README/tests gaps.

### openclaw-hardening

- Partially correct:
  - Sequence enforcement is missing (confirmed).
  - Content hash validation _is_ enforced when items are provided to `verify_chain`; the audit?s ?content_hash not enforced? is overstated.
- All other findings confirmed (parity tests missing, legacy gating, Ollama preflight, promptfoo non?spec, P2 items).

### openclaw-local-config

- No findings (confirmed).

### openclaw-source (repo at `C:\Users\17175\Users17175Projectsopenclaw-source`)

- Confirmed: bash?based scripts, unversioned hook events, coverage gaps, dependency overrides.
- Partially verified: low?memory guard is absent; OOM reports are environmental and not provable from code alone.

### openclaw-upstream

- All findings confirmed:
  - bash?based build/test; Windows onboarding test skip; unversioned hook events; Windows CI flags and coverage gaps.

---

## Corrections Applied

- Removed the stale SAML callback finding from the consolidated plan.
- Added missing connector?template P1/P2 items (README/version contradictions, no tests, zip format not implemented, non?canonical JSON hashing).
- Added missing guardspine?product P1/P2 items (broken tests, stale docs, absolute imports, hash prefix ambiguity, missing contract tests).
- Added missing guardspine?openclaw P2 items (`guardspine_root` unused; `created_at` not hashed).
- Adjusted openclaw?hardening validation claim to ?sequence not enforced; content_hash enforced when items provided.?
- Marked openclaw?source OOM as risk/observed behavior, not a provable code defect.
