# guardspine-connector-template audit (2026-02-03)

## Scorecard (0-10)

- Contract correctness: 1
- Boundary hygiene: 2
- Test quality: 0
- Operational safety: 2
- Complexity / maintainability: 4

## P0 findings (breaks contract or evidence integrity)

- Emits non-v0.2.0 bundle shape (field names and top-level schema differ) and will not pass the current oracle/backend ingest. Evidence items use `evidence_type` instead of `content_type`, and the bundle lacks the v0.2.0 `version` field, so emitted bundles are not spec-compliant. (`connector/bundle_emitter.py:109-195`)
- Hash chain and root hash are non-canonical and do not follow the current v0.2.0 proof semantics: chain entries are built from `content_hash` with `previous_hash` linking content hashes, and root hash concatenates content hashes instead of chain hashes. This diverges from kernel canonicalization and will fail verification. (`connector/bundle_emitter.py:203-233`)
- API emission posts to `/bundles` instead of the live import surface (`/api/v1/bundles/import`), so a default configuration cannot interoperate with the backend seam. (`connector/bundle_emitter.py:235-247`)
- TypeScript template defines a different schema (`schemaVersion`, `bundleId`, `EvidenceItem { id, source, kind, payload }`, and `ImmutabilityProof.chain`) and computes hashes via `JSON.stringify`, which is not canonical. This does not match the v0.2.0 bundle/immutability proof currently enforced by kernel/verify. (`src/types.ts:9-57`, `src/connector.ts:95-150`)

## P1 findings (interop drift or misleading guidance)

- README asserts v0.2.0 schema compatibility and kernel-verifiable hash chain, but the provided templates are not aligned with the actual v0.2.0 contract. This is actively misleading for downstream connector authors. (`README.md:15-24`)
- Python and TypeScript templates are mutually incompatible (field naming, bundle shape, proof format), so connectors written in each stack would emit different schemas. (`connector/bundle_emitter.py:109-195`, `src/types.ts:29-57`)
- `pyproject.toml` describes the template as "spec v1.0.0 compatible" while README/TS templates target v0.2.0. This is a versioning contradiction that will confuse integrators. (`pyproject.toml:6-18`, `README.md:15-24`)
- CLI entrypoint is declared but missing: `guardspine-connector = connector.cli:main` points to a non-existent module, so packaging/install scripts will fail. (`pyproject.toml:48-49`, no `connector/cli.py`)

## P2 findings (quality, completeness, or safety gaps)

- No tests exist (only dev dependencies). There are no golden vector fixtures, no verify integration tests, and no emit/verify round-trip checks. (`pyproject.toml:34-40`, `rg "test_"` shows no tests)
- Config advertises `format: zip`, but file emitter only writes JSON; the format switch is not implemented. (`config.example.yaml:25-27`, `connector/bundle_emitter.py:250-262`)
- The template computes content hashes over `json.dumps(..., sort_keys=True)`, which is not the canonical JSON used by the kernel. This invites silent drift even if field names were corrected. (`connector/bundle_emitter.py:197-201`)

## Concrete fixes (downstream-only)

- Replace local bundle building with kernel sealing (single canonical source). If a Python kernel bridge is not available, remove the Python emitter and make the template JS-only until it can call the canonical kernel implementation.
- Update schema fields to match v0.2.0 exactly (top-level `version`, item `content_type`, `item_id`, and proof structure). Align both TS and Python (or remove the Python template) so there is one schema.
- Route API emission to `/api/v1/bundles/import` and use raw-byte fidelity expectations (no mutation). Add an option to POST to the import endpoint only.
- Add golden vector tests: produce a fixed bundle fixture and verify against `guardspine-verify` (and the kernel) to lock canonicalization.
- Fix packaging: either add `connector/cli.py` or remove the declared entrypoint to avoid broken installs.

## Interop risk statement

This template is currently a schema fork. Any connector generated from it will emit bundles that the current kernel/verify/backend import surface will reject. If left as-is, it guarantees interop drift and undermines evidence integrity guarantees for any new connectors built from this template.

## Skeptical Annex (assumptions and gaps)

- Assumption: v0.2.0 contract matches the currently deployed kernel/verify and backend import endpoint (`/api/v1/bundles/import`); this repo was audited against that ecosystem baseline, not against a local spec file in this repo.
- Not validated: no live emit/verify run for this template because it does not match canonical schemas; any "pass" would require rewriting to the kernel contract first.
- Missing evidence: no tests or fixtures exist to prove canonicalization or proof correctness.
- False positives risk: if the spec explicitly allows the alternate schema used here (unlikely given current kernel/verify), some P1 findings could be downgraded. Confirm by aligning with `guardspine-spec` v0.2.0.
