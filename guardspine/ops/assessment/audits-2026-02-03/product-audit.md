# guardspine-product audit (2026-02-03)

## Scorecard (0-10)

- Contract correctness: 2
- Boundary hygiene: 3
- Test quality: 2
- Operational safety: 4
- Complexity / maintainability: 3

## P0 findings (breaks contract or runtime)

- Packaging is broken: `pyproject.toml` declares `packages = ["guardspine_product"]`, but there is no `guardspine_product/` package directory. The code lives in top-level packages (`common/`, `code_guard/`, etc.), so `pip install guardspine-product` produces an empty or invalid wheel and `from guardspine_product...` imports fail. (`pyproject.toml:75-78`, repo layout)
- Evidence bundles are generated via local, non-kernel hashing logic. `common/evidence.py` builds chain hashes from a custom string concatenation and uses a local canonical JSON function; this is a second canonical implementation and will drift from `@guardspine/kernel` + `guardspine-verify` behavior. Any bundle emitted here risks verify failure. (`common/evidence.py:53-182`)
- BaseGuardLane emits a bespoke "bundle" format (`bundle_type`, `content`, `hash_sha256`) that is not v0.2.0 and cannot be ingested/verified by the backend/import seam. If used as evidence, it breaks interop. (`common/base_guard_lane.py:277-306`)
- DocEvidencePack is a custom schema (`DOC_EVIDENCE_PACK/1.0`) with its own integrity hash; it is not wrapped into a v0.2.0 evidence bundle or assigned a canonical `content_type`. Any DocSync output is currently incompatible with the backend import/verify contract. (`common/doc_evidence_pack.py:16-280`, `common/docsync_engine.py:410-497`)

## P1 findings (interop drift, failing tests, or misleading docs)

- Tests reference non-existent enums and incorrect constructors. `EvidenceType.LOG_DATA` is not defined, and `EvidenceBundle` is instantiated with arguments it does not accept. The test suite is therefore broken and cannot validate behavior. (`tests/test_common_imports.py:24-33`, `tests/test_common_imports.py:225-233`, `common/evidence.py:18-52`)
- Documentation claims files and modules that do not exist (`board_packet_gate.py`, `board_packet_demo.py`, `evidence_bundle.py`). The repo map is stale and misleading. (`REPO-STRUCTURE.md:39-60`, filesystem listing)
- Internal imports are absolute to `common` and siblings, not `guardspine_product.common`. This only works when running from repo root; it fails for installed packages. (`common/docsync_engine.py:22-27`, `common/rlm_inspection.py:14-21`)

## P2 findings (quality and completeness gaps)

- No contract/golden-vector tests exist. There are no tests proving that any emitted evidence artifact matches the canonical kernel/verify expectations.
- Multiple subsystems generate hashes for drift detection (`pdf_adapter`, `sheet_adapter`, `image_adapter`) but do not prefix with `sha256:` or document how these hashes relate to evidence items, increasing ambiguity if they are later reused in bundles. (`adapters/pdf_adapter.py:143-145`, similar in sheet/slide adapters)
- `REPO-STRUCTURE.md` and `README.md` present a monorepo-style API, but packaging metadata does not match that structure; this increases onboarding risk and import confusion.

## Concrete fixes (downstream-only)

- Fix packaging: either create a real `guardspine_product/` package directory and move/alias modules under it, or adjust build config to include the actual top-level packages. Update README import examples accordingly.
- Remove local canonicalization from `common/evidence.py` and call the kernel (or a shared Python bridge) for sealing/verification. If kernel bridge is not available, do not claim v0.2.0 compliance in this module.
- Wrap DocEvidencePack into a spec-compliant evidence bundle with a canonical `content_type` (e.g., `guardspine/doc-evidence-pack`) and seal it with the kernel before emission.
- Replace `BaseGuardLane.generate_evidence_bundle` output with a v0.2.0 bundle (or rename it to avoid implying compliance) and route it through the import seam if it is meant to be stored/verified.
- Repair tests to assert real behavior: update enum references, construct `EvidenceBundle` correctly, and add at least one verify-based fixture test.

## Interop risk statement

This repo currently emits multiple evidence artifacts that are not aligned with the canonical v0.2.0 bundle format and do not use kernel sealing. If any of these outputs are treated as evidence bundles, they will fail backend import/verify and break the interop chain. Packaging issues further prevent reliable installation and integration.

## Skeptical Annex (assumptions and gaps)

- Assumption: v0.2.0 bundle semantics are defined by `guardspine-spec` + `@guardspine/kernel` + `guardspine-verify` and are the canonical reference for interop.
- Not validated: no live emission from `guardspine-product` into the backend import seam; findings are based on code inspection only.
- False positive risk: if `common/evidence.py` is intentionally for internal, non-verifiable artifacts, the contract-severity should be downgraded but the docs must be updated to avoid implying v0.2.0 compliance.
- Missing tests/fixtures make it impossible to prove that DocEvidencePack integrity hashes or RLM receipts align with any external verifier.
