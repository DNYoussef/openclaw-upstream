# GuardSpine Ecosystem Bug Report

**Date**: 2026-02-05
**Tester**: Claude (automated pipeline test)
**Scope**: All 16 GuardSpine repos, cross-language E2E workflow

---

## Test Results Summary

| Repo                       | Tests   | Pass    | Fail   | Error  | Status |
| -------------------------- | ------- | ------- | ------ | ------ | ------ |
| guardspine-kernel (TS)     | 25      | 25      | 0      | 0      | PASS   |
| guardspine-kernel-py       | 25      | 12      | 13     | 0      | FAIL   |
| guardspine-spec            | 12      | 12      | 0      | 0      | PASS   |
| guardspine-verify          | 3       | 3       | 0      | 0      | PASS   |
| GuardSpine backend         | 162     | 162     | 0      | 0      | PASS   |
| guardspine-product         | 91      | 0       | 0      | 91     | ERROR  |
| guardspine-local-council   | 11      | 11      | 0      | 0      | PASS   |
| guardspine-adapter-webhook | 27      | 27      | 0      | 0      | PASS   |
| n8n-nodes-guardspine       | 134     | 134     | 0      | 0      | PASS   |
| openclaw-hardening         | 135     | 134     | 1      | 0      | FAIL   |
| guardspine-openclaw        | 1       | 1       | 0      | 0      | PASS   |
| rlm-docsync                | 15      | 15      | 0      | 0      | PASS   |
| **TOTAL**                  | **641** | **536** | **14** | **91** |        |

**Pass Rate**: 83.6% (536/641)
**Excluding guardspine-product import errors**: 97.4% (536/550)

---

## E2E Cross-Language Workflow Result

**Workflow**: Seal in Python -> Verify with guardspine-verify -> Cross-verify with TS kernel

| Step                                      | Result                                          |
| ----------------------------------------- | ----------------------------------------------- |
| 1. Seal bundle (Python kernel)            | PASS - sealed 2 items, computed root hash       |
| 1b. Self-verify (Python kernel)           | PASS - valid=True (after adding missing fields) |
| 2. Independent verify (guardspine-verify) | PASS - verified=True, all checks green          |
| 3a. Content hash parity (TS vs Python)    | PASS - byte-identical hashes                    |
| 3b. Hash chain parity (TS vs Python)      | PASS - byte-identical chain hashes              |
| 3c. Root hash parity (TS vs Python)       | PASS - byte-identical root hash                 |
| 3d. Full bundle verify (TS kernel)        | PASS - valid=True                               |

**Cross-language parity: CONFIRMED** - Python and TypeScript produce identical SHA-256 hashes for content, chain links, and root hash.

---

## Bugs Found

### BUG-001: seal_bundle() missing required fields [guardspine-kernel-py]

- **Severity**: MEDIUM
- **File**: `src/guardspine_kernel/seal.py` (seal_bundle function, line 217-261)
- **Description**: `seal_bundle()` returns a dict with only `immutability_proof` and `items`, but `verify_bundle()` (in the same package) requires `bundle_id`, `version`, and `created_at`. The sealer and verifier have mismatched expectations.
- **Impact**: Any code that seals a bundle and then verifies it will get `MISSING_REQUIRED_FIELD` errors.
- **Reproduction**:
  ```python
  from guardspine_kernel import seal_bundle, verify_bundle
  items = [{"item_id": "test", "content_type": "test", "content": {"msg": "hi"}}]
  bundle = seal_bundle(items)
  result = verify_bundle(bundle)  # valid=False, missing bundle_id/version/created_at
  ```
- **Fix**: `seal_bundle()` should accept and include `bundle_id`, `version`, and `created_at` in output, or generate defaults.

### BUG-002: NoneType crash in verify_hash_chain [guardspine-kernel-py]

- **Severity**: HIGH
- **File**: `src/guardspine_kernel/verify.py`, lines 40 and 131
- **Description**: `link.get("previous_hash", "")` returns `None` when the field exists but is explicitly set to `None`. The default `""` is not used. Then `_safe_equal()` tries to call `.encode()` on `None`, causing `AttributeError: 'NoneType' object has no attribute 'encode'`.
- **Impact**: Verification crashes on bundles where `previous_hash` is `None` instead of omitted.
- **Reproduction**:
  ```python
  from guardspine_kernel import verify_hash_chain
  chain = [{"sequence": 0, "content_hash": "sha256:abc", "previous_hash": None, "chain_hash": "sha256:def"}]
  verify_hash_chain(chain)  # AttributeError
  ```
- **Fix**: Use `link.get("previous_hash") or ""` instead of `link.get("previous_hash", "")`.

### BUG-003: Content hash parity failure in expected-hashes.json [guardspine-kernel-py]

- **Severity**: MEDIUM
- **File**: `tests/test_parity.py` (TestExpectedHashes)
- **Description**: The expected hash for content `"test"` is `sha256:9f86d081...` (SHA-256 of raw string "test"), but the Python kernel correctly hashes `{"message":"test"}` as canonical JSON, producing `sha256:4144005e...`. The test expectations appear to be wrong, or there is a disagreement about what input gets hashed.
- **Impact**: 13 parity tests fail, making it impossible to detect real regressions.
- **Fix**: Regenerate `expected-hashes.json` from the TypeScript kernel (canonical source), or fix the test inputs to match what the golden vectors actually hash.

### BUG-004: seal_bundle test uses wrong API - items attribute collision [guardspine-kernel-py]

- **Severity**: MEDIUM
- **File**: `tests/test_parity.py` (TestSealBundle.test_minimal_bundle)
- **Description**: Test does `result.items` expecting a list, but `seal_bundle()` returns a `dict`, and `dict.items` is a method (not a list). `len(result.items)` raises `TypeError: object of type 'builtin_function_or_method' has no len()`.
- **Impact**: Test suite cannot validate seal_bundle output structure.
- **Fix**: Use `result["items"]` instead of `result.items` in tests, since `seal_bundle()` returns a dict.

### BUG-005: Root hash tamper detection failure [openclaw-hardening] -- SECURITY

- **Severity**: CRITICAL
- **File**: `tests/test_hash_chain.py`, line 65
- **Description**: After setting `chain["root_hash"]` to all zeros (`"0" * 64`), `verify_chain()` still returns `True`. The root hash is NOT being validated during verification.
- **Impact**: An attacker can replace the root hash with any value and the verification will still pass. This completely undermines the tamper-detection guarantee.
- **Reproduction**:
  ```python
  chain = build_chain(items)
  chain["root_hash"] = "0" * 64  # Tamper
  assert verify_chain(chain) == False  # FAILS - returns True
  ```
- **Fix**: `verify_chain()` must recompute the root hash from the chain links and compare it to the stored `root_hash` value.

### BUG-006: Module import crash at load time [openclaw-hardening]

- **Severity**: LOW
- **File**: `approvals/approval_gate.py`, line 32
- **Description**: `GUARDSPINE_COUNCIL_KEY` environment variable is required at module import time. If not set, `ValueError` is raised during import, preventing test collection for 4 test files.
- **Impact**: Tests cannot be collected without setting environment variables first. CI/CD must know to set this.
- **Reproduction**:
  ```python
  # Without GUARDSPINE_COUNCIL_KEY set:
  import approvals.approval_gate  # ValueError
  ```
- **Fix**: Use lazy loading - only require the key when `approve()` is actually called, not at import time. Or use a test fixture that sets the env var.

### BUG-007: All 91 tests fail with import errors [guardspine-product]

- **Severity**: HIGH
- **File**: `tests/` (all test files), root cause in `common/` module
- **Description**: Every test file fails during collection with import errors in the `common` module chain. Basic imports like `from common.risk_tiers import RiskTier` work, but advanced modules (feedback loops, orchestrator, etc.) fail to import.
- **Impact**: The entire guardspine-product test suite is non-functional. Zero tests can run.
- **Root cause**: Likely missing dependencies or circular imports in advanced `common` modules. The `pyproject.toml` only declares `guardspine-kernel` as a dependency, but the code imports modules that may require additional packages.
- **Fix**: Audit the `common/` module import chain, add missing dependencies to `pyproject.toml`, and resolve any circular imports.

---

## Summary by Severity

| Severity | Count | Bugs                                                                                       |
| -------- | ----- | ------------------------------------------------------------------------------------------ |
| CRITICAL | 1     | BUG-005 (root hash tamper not detected)                                                    |
| HIGH     | 2     | BUG-002 (NoneType crash), BUG-007 (91 import failures)                                     |
| MEDIUM   | 3     | BUG-001 (seal/verify mismatch), BUG-003 (expected hashes wrong), BUG-004 (items collision) |
| LOW      | 1     | BUG-006 (env var at import time)                                                           |

## Priority Fix Order

1. **BUG-005** (CRITICAL) - Security vulnerability: root hash tamper detection is broken
2. **BUG-002** (HIGH) - NoneType crash prevents verification of edge-case bundles
3. **BUG-007** (HIGH) - Entire product test suite non-functional
4. **BUG-001** (MEDIUM) - seal_bundle output incomplete for self-verification
5. **BUG-003/004** (MEDIUM) - Test suite failures mask real regressions
6. **BUG-006** (LOW) - Import-time env var requirement

---

## Repos with Clean Test Suites (No Action Needed)

- guardspine-kernel (TS) - 25/25
- guardspine-spec - 12/12
- guardspine-verify - 3/3
- GuardSpine backend - 162/162
- guardspine-local-council - 11/11
- guardspine-adapter-webhook - 27/27
- n8n-nodes-guardspine - 134/134
- guardspine-openclaw - plugin loads OK
- rlm-docsync - 15/15
