# GuardSpine Local Council - Linus Audit (2026-02-03)

## Scorecard (0-10)

- Contract correctness: 4
- Boundary hygiene: 6
- Test quality: 4
- Operational safety: 5
- Complexity / maintainability: 7

## P0 Findings (Must Fix)

None found.

## P1 Findings (Should Fix)

1. Evidence bundle hashing is reimplemented without parity tests
   - `_content_hash` + chain construction are local copies of kernel behavior with no golden-vector parity tests.
   - Impact: drift risk; council evidence bundles can fail verification by the canonical verifier.
   - Fix: add parity tests using kernel fixtures or import canonical hashing from a single source.
   - File: `D:\Projects\guardspine-local-council\src\guardspine_local_council\council.py`

2. Council evidence bundles are not validated against spec
   - Bundles are constructed but never validated for required fields, sequence continuity, or hash-chain correctness before being returned.
   - Impact: invalid bundles can be emitted and later rejected by verify/import.
   - Fix: validate bundle at build time (sequence check, hash-chain verify) or run `guardspine-verify` in tests.
   - File: `D:\Projects\guardspine-local-council\src\guardspine_local_council\council.py`

3. Ollama provider has no reachability/model preflight
   - It assumes Ollama is running and the model exists; failures are only caught after request timeout.
   - Impact: council runs can appear to succeed with abstains instead of hard failure.
   - Fix: add a preflight to check `/api/tags` and require configured models.
   - File: `D:\Projects\guardspine-local-council\src\guardspine_local_council\providers\ollama.py`

4. Evidence bundles lack any signature support
   - Council bundles are unsigned, and no signing hooks exist in this repo.
   - Impact: bundles are format-only and cannot be cryptographically attributed to a council instance.
   - Fix: optional signing hook or explicit guidance that signatures are out-of-scope for local council outputs.
   - Files: `D:\Projects\guardspine-local-council\src\guardspine_local_council\council.py`, `README.md`

## P2 Findings (Cleanup / Consistency)

1. Tests do not cover evidence bundle validity
   - There are no tests for hash-chain integrity or verification of the generated evidence bundle.
   - Fix: add a smoke test that generates a bundle and verifies with `guardspine-verify`.
   - Files: `D:\Projects\guardspine-local-council\tests\test_council.py`

2. README omits evidence-bundle output contract
   - README documents review flow but does not state that a v0.2.0 evidence bundle is emitted, nor how to verify it.
   - Fix: document bundle output and verification command.
   - File: `D:\Projects\guardspine-local-council\README.md`

## Concrete Fixes (High-Leverage)

1. Add kernel parity tests for `_content_hash` and chain construction.
2. Validate council bundle against v0.2.0 rules before returning.
3. Add Ollama preflight (reachable + model exists) with explicit error on failure.
4. Provide optional signing hook or documented “unsigned by design” stance.
5. Add a test that runs `guardspine-verify` on a generated council bundle.

## Interop Risk Statement

Council bundles are a downstream producer in the evidence pipeline. Without parity tests and validation, drift in canonicalization or chain rules can silently produce bundles that fail verification elsewhere, undermining the governance workflow.

## Skeptical Annex (Assumptions / Edge Cases / Evidence)

- Assumptions:
  - Council evidence bundles are intended to be v0.2.0 compliant and used outside this repo.
  - Signature support is desirable but not required for local-only use.
- Edge cases not directly tested here:
  - Large review payloads (prompt size) and their impact on hashing/performance.
  - Ollama timeouts and partial responses in `_parse_response`.
- Possible false positives/negatives:
  - If council bundles are purely internal diagnostics, severity of P1 #2 can be downgraded.
- Evidence reviewed:
  - `src/guardspine_local_council/council.py`
  - `src/guardspine_local_council/providers/ollama.py`
  - `src/guardspine_local_council/types.py`
  - `tests/test_council.py`, `tests/test_aggregator.py`
  - `README.md`
