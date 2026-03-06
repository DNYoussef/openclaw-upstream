# GuardSpine Verify - Linus Audit (2026-02-03)

## Scorecard (0-10)

- Contract correctness: 5
- Boundary hygiene: 6
- Test quality: 4
- Operational safety: 4
- Complexity / maintainability: 7

## P0 Findings (Must Fix)

1. Hash chain is not bound to the items list
   - Risk: A bundle can include evidence items that are not covered by the immutability proof and still verify. `verify_hash_chain` and `verify_content_hashes` run independently and never enforce a 1:1 mapping between chain entries and items.
   - Impact: Unchained evidence can be inserted or reordered without invalidating the proof; verification can return "verified" while integrity is not fully covered.
   - Fix: Enforce exact alignment between chain entries and items (same count, same item_id, same content_hash, same order or defined order). Fail if any item is missing from the chain or any chain entry lacks a corresponding item.
   - File: `D:\Projects\guardspine-verify\guardspine_verify\verifier.py`

## P1 Findings (Should Fix)

1. Bundle version is not enforced
   - Risk: Verifier accepts bundles with missing or unknown version fields. This creates silent interop drift when schema changes.
   - Fix: Require `schemaVersion` (or `version`, if spec says so) and validate against an allowed list (e.g., `["0.2.0"]`). Provide an explicit option for legacy acceptance if needed.
   - Files: `D:\Projects\guardspine-verify\guardspine_verify\verifier.py`, `D:\Projects\guardspine-verify\tests\test_vectors\external-signed-bundle.json`

2. ZIP ingestion has no safety limits
   - Risk: Zip bombs or huge entries can cause memory/CPU spikes. This is especially risky if verify is run on untrusted artifacts or wired into automation.
   - Fix: Add max compressed size, max uncompressed size, max entry count, and path traversal checks. Reject nested archives unless explicitly supported.
   - File: `D:\Projects\guardspine-verify\guardspine_verify\verifier.py`

3. Unsigned bundle can still be "verified" even when a public key is provided
   - Risk: If callers pass `public_key_pem` expecting cryptographic assurance, an unsigned bundle still returns `verified=True` (with warnings), which can be misinterpreted as cryptographic success.
   - Fix: Add a strict mode (e.g., `require_signatures=True`) or treat "no signatures" as mismatch when a public key is provided.
   - Files: `D:\Projects\guardspine-verify\guardspine_verify\verifier.py`, `D:\Projects\guardspine-verify\guardspine_verify\cli.py`

4. HMAC base64-encoded hex is documented but not supported
   - Risk: `verify_signatures` claims to accept base64-encoded hex, but it only compares the raw string to `hexdigest()`. Valid HMAC signatures can be rejected.
   - Fix: If `signature_value` is base64, decode to hex bytes before compare (or remove the claim and enforce a single encoding).
   - File: `D:\Projects\guardspine-verify\guardspine_verify\verifier.py`

## P2 Findings (Cleanup / Consistency)

1. README claims features that do not exist
   - Claims `verify_bundles` API and directory support, neither is implemented. Also claims AI provenance checks and fields (`item_count`, `signature_count`) not present in `VerificationResult`.
   - Fix: Update README to match reality, or implement the missing functionality.
   - Files: `D:\Projects\guardspine-verify\README.md`, `D:\Projects\guardspine-verify\guardspine_verify\__init__.py`

2. Legacy chain container support is inconsistent
   - `_extract_chain_entries` accepts legacy structure but `verify_hash_chain` still requires v0.2.0 fields, so legacy chains always fail with field errors.
   - Fix: Either implement legacy verification explicitly or remove the legacy path to avoid confusion.
   - File: `D:\Projects\guardspine-verify\guardspine_verify\verifier.py`

3. Package version is out of step with current spec
   - `__version__` is `0.1.0` while the bundle format under test is `0.2.0`. This is confusing for operators and automation.
   - Fix: Bump package version or add explicit compatibility statement in the CLI output/README.
   - File: `D:\Projects\guardspine-verify\guardspine_verify\__init__.py`

4. CLI invalid-input exit codes are inconsistent with docs
   - Docs say invalid input should return exit code 2, but unsupported file formats are treated as verification failure (exit 1).
   - Fix: Map unsupported file formats to exit code 2 to match docs.
   - Files: `D:\Projects\guardspine-verify\guardspine_verify\cli.py`, `D:\Projects\guardspine-verify\guardspine_verify\verifier.py`

## Concrete Fixes (High-Leverage)

1. Add chain-to-items binding checks (count, item_id, content_hash) and reject mismatches.
2. Enforce `schemaVersion`/`version` allowlist in `verify_bundle_data`.
3. Add ZIP safety guards (size, entry count, traversal).
4. Add `require_signatures` flag (CLI + API) for cryptographic enforcement.
5. Align README and API exports; remove stale claims or implement missing functions.

## Interop Risk Statement

Without chain-to-items binding and version enforcement, the verifier can mark bundles as verified even when parts of the evidence are outside the immutability proof or when schema drift occurs. This undermines the ecosystem’s core guarantee (auditability) and can mask upstream/downstream contract divergence.

## Skeptical Annex (Assumptions / Edge Cases / Evidence)

- Assumptions:
  - The v0.2.0 chain is intended to cover every item exactly once; otherwise P0 #1 is lower severity.
  - `schemaVersion` or `version` is mandatory per spec.
- Edge cases not directly tested here:
  - Float canonicalization parity with `@guardspine/kernel` for exponent notation and huge integers.
  - Multiple signatures with different public keys (current API only accepts one key).
  - Large ZIPs, nested ZIPs, or path traversal attempts.
- Possible false positives/negatives:
  - If spec intentionally allows items outside the hash chain, the P0 should be downgraded.
  - If signature verification is meant to be strictly opt-in, the unsigned-when-key-provided issue is policy, not a bug.
- Evidence reviewed:
  - `guardspine_verify/verifier.py`, `guardspine_verify/cli.py`, `guardspine_verify/__init__.py`
  - `tests/test_verifier_smoke.py` + `tests/test_vectors/*`
  - `README.md`
