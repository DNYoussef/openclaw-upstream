# GuardSpine Adapter Webhook - Linus Audit (2026-02-03)

## Scorecard (0-10)

- Contract correctness: 5
- Boundary hygiene: 5
- Test quality: 6
- Operational safety: 6
- Complexity / maintainability: 7

## P0 Findings (Must Fix)

None found.

## P1 Findings (Should Fix)

1. `BundleEmitter.sealBundle()` operates on a non-spec bundle shape
   - It passes `EmittedBundle` (with `kind/summary/url/contentHash`) into `@guardspine/kernel` which expects spec-shaped items (`item_id`, `content_type`, `content`).
   - Impact: Kernel output is unreliable or silently dropped; you now have two sealing paths that can diverge (EmittedBundle vs import bundle).
   - Fix: Either (a) remove `sealBundle()` from `BundleEmitter`, or (b) refactor it to construct a spec-compliant bundle (same as `buildImportBundle`) before sealing.
   - Files: `D:\Projects\guardspine-adapter-webhook\src\bundle-emitter.ts`, `D:\Projects\guardspine-adapter-webhook\src\types.ts`

2. `sealBundle()` fails open when kernel is missing or errors
   - It silently returns an unsealed bundle when kernel is missing or throws.
   - Impact: Callers can assume a bundle is sealed when it is not; this is an integrity foot-gun.
   - Fix: Fail loudly or return a typed result with `sealed=false` and an explicit error to force callers to handle the non-sealed case.
   - File: `D:\Projects\guardspine-adapter-webhook\src\bundle-emitter.ts`

3. Type safety is intentionally disabled for kernel integration
   - `src/guardspine-kernel.d.ts` declares `sealBundle` returns `void`, but the code expects `{ items, immutabilityProof }`.
   - Impact: The compiler can’t detect kernel contract drift, and runtime errors are easy to ship.
   - Fix: Define proper types for `sealBundle` (or import from `@guardspine/kernel` once it exports types).
   - File: `D:\Projects\guardspine-adapter-webhook\src\guardspine-kernel.d.ts`

## P2 Findings (Cleanup / Consistency)

1. `EmittedBundle` is described as “ready for ingestion” but isn’t spec-compliant
   - It lacks `immutability_proof`, uses `kind` instead of `content_type`, and has no `item_id/sequence`.
   - Impact: Users following README can post invalid bundles to the backend.
   - Fix: Clarify in README that `EmittedBundle` is pre-seal/pre-import and that `buildImportBundle()` produces the spec bundle.
   - File: `D:\Projects\guardspine-adapter-webhook\README.md`

2. Local content hashing is redundant and potentially misleading
   - `BundleEmitter` computes `contentHash` with a local canonicalizer, but `buildImportBundle()` ignores it and kernel recomputes hashes.
   - Impact: Confusion and risk of downstream consumers relying on a hash that isn’t part of the canonical proof.
   - Fix: Remove `contentHash` from the emitted item or explicitly document that it’s informational only.
   - Files: `D:\Projects\guardspine-adapter-webhook\src\bundle-emitter.ts`, `D:\Projects\guardspine-adapter-webhook\src\types.ts`

3. Import metadata omits top-level spec fields
   - `buildImportBundle()` stores `artifact_id` and `risk_tier` in metadata, not in top-level optional fields.
   - Impact: Some consumers may expect these fields at top-level for indexing/interop.
   - Fix: Populate top-level `artifact_id` and `risk_tier` in the draft bundle in addition to metadata.
   - File: `D:\Projects\guardspine-adapter-webhook\src\importer.ts`

## Concrete Fixes (High-Leverage)

1. Remove or refactor `BundleEmitter.sealBundle()` to only seal spec bundles.
2. Make kernel missing/error a hard failure or return explicit `sealed=false`.
3. Replace the stub kernel type definition with accurate types.
4. Update README to distinguish EmittedBundle (pre-seal) vs ImportBundle (spec).
5. Populate top-level `artifact_id`/`risk_tier` in `buildImportBundle()`.

## Interop Risk Statement

As written, there are two parallel sealing paths with incompatible shapes. This undermines the “single canonical kernel” requirement and risks downstream consumers treating unsealed bundles as valid evidence. Tighten the boundary so only spec-shaped bundles are ever sealed.

## Skeptical Annex (Assumptions / Edge Cases / Evidence)

- Assumptions:
  - `@guardspine/kernel` expects spec-shaped items (item_id/content_type/content) and does not intentionally support the adapter’s EmittedBundle shape.
  - EmittedBundle is not intended to be posted directly to `/bundles/import`.
- Edge cases not directly tested here:
  - Sealing a bundle with large raw payloads (diffs) to check memory pressure.
  - Kernel behavior when given EmittedBundle (non-spec) inputs.
- Possible false positives/negatives:
  - If kernel explicitly supports EmittedBundle, the P1 on sealBundle shape may be downgraded, but this needs documented contract guarantees.
- Evidence reviewed:
  - `src/bundle-emitter.ts`
  - `src/importer.ts`
  - `src/types.ts`
  - `src/guardspine-kernel.d.ts`
  - `tests/bundle-emitter.test.ts`, `tests/importer.test.ts`
  - `README.md`
