# GuardSpine Backend - Linus Audit (2026-02-03)

## Scorecard (0-10)

- Contract correctness: 5
- Boundary hygiene: 6
- Test quality: 6
- Operational safety: 5
- Complexity / maintainability: 6

## P0 Findings (Must Fix)

None found.

## P1 Findings (Should Fix)

1. Canonical kernel logic is duplicated in Python without parity tests
   - The backend relies on `app/core/kernel.py`, a reimplementation of the canonical kernel. There is no enforced parity check against `@guardspine/kernel` golden vectors.
   - Impact: Silent drift breaks import verification and sealing across ecosystems.
   - Fix: Add golden-vector parity tests (same fixtures as kernel) or delegate validation to a single canonical implementation.
   - Files: `D:\Projects\GuardSpine\backend\app\core\kernel.py`, `D:\Projects\GuardSpine\backend\app\services\imported_bundle_service.py`

2. Import verification does not enforce item sequence rules or content shape
   - Spec requires `sequence` to match item index and `content` to be object/array; import currently ignores `item.sequence` and accepts primitives.
   - Impact: Spec-invalid bundles can be accepted and stored as “verified.”
   - Fix: Enforce `item.sequence == index` and reject primitive `content` types.
   - File: `D:\Projects\GuardSpine\backend\app\services\imported_bundle_service.py`

3. `/bundles/{id}/export` is not spec-compliant but appears to be an evidence-bundle export
   - The export payload omits `version`, uses non-spec fields, and includes internal metadata. This conflicts with the canonical v0.2.0 bundle format.
   - Impact: Integrators may treat this export as a spec bundle and fail verification downstream.
   - Fix: Rename the endpoint to clarify it’s a report export, or add a spec-compliant export endpoint (distinct from the raw import/export paths).
   - Files: `D:\Projects\GuardSpine\backend\app\routers\bundles.py`, `D:\Projects\GuardSpine\backend\app\services\export_service.py`

4. Signature strict mode supports only Ed25519
   - `GUARDSPINE_IMPORT_REQUIRE_SIGNATURES=1` rejects RSA/ECDSA/HMAC signatures despite being valid per spec.
   - Impact: Valid spec bundles are rejected in strict mode.
   - Fix: Support all spec algorithms or document a restricted profile and expose it explicitly.
   - File: `D:\Projects\GuardSpine\backend\app\services\imported_bundle_service.py`

5. Core evidence storage is in-memory only
   - `BundleService` stores evidence bundles in memory with demo initialization. No persistence means data loss on restart.
   - Impact: Integrity and auditability collapse if deployed as-is.
   - Fix: Introduce durable storage or hard-disable non-demo operation without persistence configured.
   - File: `D:\Projects\GuardSpine\backend\app\services\bundle_service.py`

## P2 Findings (Cleanup / Consistency)

1. Spec bundle builder can emit invalid `created_at` fields
   - `_build_spec_bundle` always includes `created_at` per item, but uses `None` when missing (serializes to `null`), which violates schema string type.
   - Fix: Omit `created_at` when `None`.
   - File: `D:\Projects\GuardSpine\backend\app\services\bundle_service.py`

2. Evidence seal response references a non-existent CLI
   - `offline_verify_cmd` uses `guardspine verify ...` but the actual verifier is `guardspine-verify`.
   - Fix: Update the command string or document the intended CLI.
   - File: `D:\Projects\GuardSpine\backend\app\routers\evidence.py`

3. Export verification instructions are inaccurate
   - Instructions say signatures verify against content hashes; spec requires signatures over the bundle without the signatures array.
   - Fix: Align instructions with spec to avoid misleading auditors.
   - File: `D:\Projects\GuardSpine\backend\app\services\export_service.py`

## Concrete Fixes (High-Leverage)

1. Add kernel parity tests using the same golden vector fixtures as `guardspine-kernel`.
2. Enforce `item.sequence` and content-type constraints at import to match v0.2.0.
3. Split “spec bundle export” from “report export” and name endpoints accordingly.
4. Expand signature verification to all spec algorithms or explicitly profile the accepted subset.
5. Replace in-memory bundle store with durable persistence or gate non-demo mode.

## Interop Risk Statement

The backend is now a byte-fidelity conduit for imported bundles, but its internal kernel duplication and permissive import validation allow spec-invalid bundles and create drift risk. The export endpoint name also risks downstream consumers treating non-spec exports as canonical bundles.

## Skeptical Annex (Assumptions / Edge Cases / Evidence)

- Assumptions:
  - The backend’s `/bundles/{id}/export` is intended for external consumption; if it’s strictly UI-only, downgrade P1 #3.
  - Strict signature mode is expected to honor all algorithms listed in the spec.
- Edge cases not directly tested here:
  - Very large imports under max byte limits (memory pressure behavior).
  - Concurrency behavior of disk-backed imported bundle store.
  - Bundle items with `content` primitives or missing `sequence`.
- Possible false positives/negatives:
  - If demo-only use is intentional, the in-memory store severity could be downgraded.
  - If strict mode is intentionally Ed25519-only, document and surface this profile.
- Evidence reviewed:
  - `app/services/imported_bundle_service.py`
  - `app/core/kernel.py`
  - `app/services/bundle_service.py`
  - `app/routers/bundles.py`
  - `app/routers/evidence.py`
  - `app/services/export_service.py`
