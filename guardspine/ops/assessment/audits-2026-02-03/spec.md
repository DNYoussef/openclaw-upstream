# GuardSpine Spec - Linus Audit (2026-02-03)

## Scorecard (0-10)

- Contract correctness: 4
- Boundary hygiene: 6
- Test quality: 3
- Operational safety: 8
- Complexity / maintainability: 7

## P0 Findings (Must Fix)

None found.

## P1 Findings (Should Fix)

1. README contradicts the canonical chain definition
   - The README states previous*hash links to prior \_content_hash*, while the schema/spec define previous*hash as prior \_chain_hash*.
   - Impact: Implementers following README will produce invalid chains that fail kernel/verify, causing interop drift.
   - Fix: Align README verification rules with SPECIFICATION.md and schema.
   - File: `D:\Projects\guardspine-spec\README.md`

2. Examples are not v0.2.0 compliant
   - The example bundles under `examples/` use `evidence_type` instead of `content_type`, omit `version`, and omit `immutability_proof`. They are effectively legacy/nonconformant.
   - Impact: Implementers copy these and emit invalid bundles; verify will reject.
   - Fix: Update examples to v0.2.0 or move them into a clearly labeled legacy folder.
   - Files: `D:\Projects\guardspine-spec\examples\code-diff-bundle.json`, `D:\Projects\guardspine-spec\examples\pdf-diff-bundle.json`, `D:\Projects\guardspine-spec\examples\xlsx-diff-bundle.json`

3. README “Bundle Structure” diverges from schema
   - README includes fields not present in schema (e.g., `retention`, `audit_trail`, signature `content_hash`) and duplicates `immutability_proof`.
   - Impact: Consumers may assume required/available fields that are not part of the canonical contract.
   - Fix: Make README structure match the schema exactly; document extensions under `metadata` if intended.
   - File: `D:\Projects\guardspine-spec\README.md`

## P2 Findings (Cleanup / Consistency)

1. Schema duplication risk
   - `schemas/evidence-bundle.schema.json` and `schemas/evidence-bundle-v0.2.0.schema.json` are identical copies with the same `$id`.
   - Impact: future edits can drift and silently desync.
   - Fix: keep only one canonical file or enforce identical content via tests/scripts.
   - Files: `D:\Projects\guardspine-spec\schemas\evidence-bundle.schema.json`, `D:\Projects\guardspine-spec\schemas\evidence-bundle-v0.2.0.schema.json`

2. Schema validation script is not portable and does not validate against schema
   - `validate-schemas.mjs` uses absolute paths and only parses JSON; it does not validate examples against the schema.
   - Impact: false sense of correctness; CI won’t catch schema/example drift.
   - Fix: use relative paths and a JSON Schema validator (ajv) to validate examples.
   - File: `D:\Projects\guardspine-spec\validate-schemas.mjs`

## Concrete Fixes (High-Leverage)

1. Fix README chain rule wording and align bundle structure with schema.
2. Refresh examples to v0.2.0 and add an explicit “legacy” folder for prior formats.
3. Replace validate-schemas script with real schema validation and CI wiring.
4. Remove duplicate schema or add a check that keeps them identical.

## Interop Risk Statement

The current README and examples directly contradict the canonical v0.2.0 schema and hash-chain rules. This is a high-probability source of producer drift and false-negative verification failures across the ecosystem.

## Skeptical Annex (Assumptions / Edge Cases / Evidence)

- Assumptions:
  - The v0.2.0 schema is the canonical source of truth over README/examples.
  - Examples are intended to be valid unless explicitly marked legacy.
- Edge cases not directly tested here:
  - Schema validation for `content` primitives (schema disallows primitives; README is silent).
  - Compatibility migration guidance for v1.0.0/v0.1.0 bundles.
- Possible false positives/negatives:
  - If README/examples are intentionally illustrative only, the severity of P1s may be lower, but this should be stated explicitly in the docs.
- Evidence reviewed:
  - `schemas/evidence-bundle-v0.2.0.schema.json`
  - `SPECIFICATION.md`
  - `README.md`
  - `examples/*.json`
  - `validate-schemas.mjs`
