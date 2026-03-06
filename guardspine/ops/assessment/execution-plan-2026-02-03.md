# GuardSpine Remediation: Sequential Execution Plan

**Generated:** 2026-02-03
**Purpose:** Dependency-aware execution plan with tests, dry runs, and interop validation
**Total Effort:** 322h across 88 tickets
**Duration:** 8 weeks (3 engineers) or 16 weeks (1 engineer)

---

## Executive Summary

This plan uses a **strict layered dependency model** to prevent cascading failures. Each layer must have GREEN CI before the next layer starts.

```
LAYER 0: Spec + Kernel (Foundation)     <- No dependencies
    |
    v
LAYER 1: Python Bridge (kernel-py)      <- Depends on Layer 0
    |
    v
LAYER 2: Validators (verify + backend)  <- Depends on Layer 0 + 1
    |
    v
LAYER 3: Producers (7 repos)            <- Depends on Layer 0 + 1 + 2
    |
    v
LAYER 4: Integration (openclaw + n8n)   <- Depends on ALL above
    |
LAYER 5: Platform (Windows) -----------> Parallel track, no blockers
```

---

## Part 1: Dependency Flow Diagram

```
                    +-------------------+
                    |   LAYER 0         |
                    |   FOUNDATION      |
                    +-------------------+
                    |                   |
        +-----------+                   +-----------+
        |                                           |
        v                                           v
+----------------+                         +----------------+
| guardspine-    |                         | guardspine-    |
| spec           |                         | kernel         |
| - Fix README   |                         | - Version      |
| - Examples     |                         |   enforcement  |
| - Golden       |                         |                |
|   vectors      |                         |                |
+-------+--------+                         +--------+-------+
        |                                           |
        |  OUTPUTS: Golden vectors,                 |
        |  corrected spec                           |
        +-------------------+   +-------------------+
                            |   |
                            v   v
                    +-------------------+
                    |   LAYER 1         |
                    |   PYTHON BRIDGE   |
                    +-------------------+
                    | guardspine-       |
                    | kernel-py         |
                    | - seal_bundle()   |
                    | - verify_bundle() |
                    | - canonical_json()|
                    +--------+----------+
                             |
                             | OUTPUTS: Python functions
                             | with 100% JS parity
                             v
        +--------------------+--------------------+
        |                                         |
        v                                         v
+----------------+                         +----------------+
| guardspine-    |                         | guardspine-    |
| verify         |                         | backend        |
| LAYER 2A       |                         | LAYER 2B       |
| - Chain binding|                         | - Use kernel-py|
| - ZIP limits   |                         | - Enforce seq  |
| - Version check|                         | - Split export |
+-------+--------+                         +--------+-------+
        |                                           |
        |  OUTPUTS: Strict validators               |
        +-------------------+   +-------------------+
                            |   |
                            v   v
                    +-------------------+
                    |   LAYER 3         |
                    |   PRODUCERS       |
                    |   (7 repos)       |
                    +-------------------+
                            |
        +-------+-------+---+---+-------+-------+
        |       |       |       |       |       |
        v       v       v       v       v       v
     +-----+ +-----+ +-----+ +-----+ +-----+ +-----+
     |conn-| |prod-| |coun-| |adapt| |hard-| |n8n  |
     |ector| |uct  | |cil  | |er   | |ening| |nodes|
     +--+--+ +--+--+ +--+--+ +--+--+ +--+--+ +--+--+
        |       |       |       |       |       |
        +-------+-------+---+---+-------+-------+
                            |
                            v
                    +-------------------+
                    |   LAYER 4         |
                    |   INTEGRATION     |
                    +-------------------+
                    | guardspine-       |
                    | openclaw          |
                    | - Use kernel      |
                    | - Wire to backend |
                    | - Security fixes  |
                    +-------------------+
```

---

## Part 2: Data Flow Specification

### 2.1 Golden Vector Data Flow

```
+-------------------+     +-------------------+     +-------------------+
| guardspine-spec/  |     | ALL REPOS         |     | CI PIPELINE       |
| fixtures/         |---->| import fixtures   |---->| parity test       |
| golden-vectors/   |     | run parity tests  |     | PASS/FAIL         |
+-------------------+     +-------------------+     +-------------------+

Files:
  fixtures/golden-vectors/
    v0.2.0-minimal-bundle.json      <- Smallest valid bundle
    v0.2.0-signed-bundle.json       <- Bundle with Ed25519 signature
    v0.2.0-multi-item-bundle.json   <- Bundle with 5+ items
    v0.2.0-chained-bundle.json      <- Bundle demonstrating chain linkage
    expected-hashes.json            <- SHA256 hashes for each bundle
    expected-chain.json             <- Chain hash values
    malformed/                      <- Invalid bundles (MUST reject)
      missing-version.json
      wrong-chain-linkage.json
      unbound-items.json
      duplicate-item-ids.json
```

### 2.2 Kernel Bridge Data Flow

```
+-------------------+     +-------------------+     +-------------------+
| Python caller     |     | guardspine-       |     | @guardspine/      |
|                   |---->| kernel-py         |---->| kernel (Node.js)  |
| seal_bundle(      |     | subprocess call   |     | sealBundle()      |
|   items=[...])    |     | JSON serialization|     | actual impl       |
+-------------------+     +-------------------+     +-------------------+
                                    |
                                    v
                          +-------------------+
                          | RETURN            |
                          | SealedBundle      |
                          | (identical to JS) |
                          +-------------------+

Bridge Protocol:
  1. Python serializes input to JSON
  2. Spawns: node -e "require('@guardspine/kernel').sealBundle(JSON.parse(input))"
  3. Captures stdout JSON
  4. Deserializes to Python types
  5. MUST produce byte-identical hashes
```

### 2.3 Validation Data Flow

```
+-------------------+     +-------------------+     +-------------------+
| ANY PRODUCER      |     | guardspine-       |     | guardspine-       |
| seal_bundle()     |---->| verify            |---->| backend           |
|                   |     | verify_bundle()   |     | /api/v1/import    |
+-------------------+     +-------------------+     +-------------------+
        |                         |                         |
        v                         v                         v
   SealedBundle              VerifyResult              ImportResult
   {                         {                         {
     version: "0.2.0",         valid: true,             success: true,
     items: [...],             chain_valid: true,       bundle_id: "...",
     hash_chain: [...],        items_bound: true,       warnings: []
     signatures: [...]         version_ok: true       }
   }                         }
```

---

## Part 3: Task Breakdown by Layer

### LAYER 0: Foundation (Week 1)

| Task ID | Title                            | Depends On | Hours | Owner | Exit Criteria                           |
| ------- | -------------------------------- | ---------- | ----- | ----- | --------------------------------------- |
| T0.1    | Fix README chain rule            | -          | 2h    | PLT   | README matches SPECIFICATION.md         |
| T0.2    | Update examples to v0.2.0        | T0.1       | 4h    | PLT   | All examples pass ajv validation        |
| T0.3    | Create golden vector fixtures    | T0.1       | 8h    | PLT   | 6+ valid, 6+ invalid fixtures           |
| T0.4    | Kernel version VALUE enforcement | -          | 2h    | PLT   | verifyBundle rejects version != "0.2.0" |
| T0.5    | Portable ajv validation script   | T0.2       | 4h    | OPS   | npm run validate passes                 |

**Blockers:** None
**Exit Gate:** `npm run test:golden-vectors` passes in guardspine-spec

### LAYER 1: Python Bridge (Week 2)

| Task ID | Title                      | Depends On       | Hours | Owner | Exit Criteria          |
| ------- | -------------------------- | ---------------- | ----- | ----- | ---------------------- |
| T1.1    | Package scaffold           | T0.3             | 4h    | PLT   | pip install -e . works |
| T1.2    | seal_bundle() bridge       | T1.1             | 4h    | PLT   | Parity test passes     |
| T1.3    | verify_bundle() bridge     | T1.1             | 4h    | PLT   | Parity test passes     |
| T1.4    | canonical_json() wrapper   | T1.1             | 2h    | PLT   | Parity test passes     |
| T1.5    | Golden vector parity tests | T1.2, T1.3, T1.4 | 2h    | PLT   | 100% parity            |

**Blockers:** T0.3 (golden vectors must exist)
**Exit Gate:** `pytest tests/test_parity.py` passes with 100% match

### LAYER 2A: Verify Enforcement (Week 3)

| Task ID | Title                     | Depends On | Hours | Owner | Exit Criteria             |
| ------- | ------------------------- | ---------- | ----- | ----- | ------------------------- |
| T2.1    | Chain-to-items BINDING    | T1.5       | 8h    | PLT   | Unbound items rejected    |
| T2.2    | Chain-to-items COUNT      | T2.1       | 2h    | PLT   | len mismatch rejected     |
| T2.3    | item_id CROSS-REFERENCE   | T2.1       | 4h    | PLT   | ID mismatch rejected      |
| T2.4    | ZIP safety limits         | -          | 4h    | SEC   | >100MB zip rejected       |
| T2.5    | Version VALUE enforcement | T0.4       | 4h    | PLT   | version != 0.2.0 rejected |
| T2.6    | require_signatures flag   | -          | 2h    | SEC   | unsigned+key = FAIL       |

**Blockers:** T1.5 (kernel-py must be usable)
**Exit Gate:** ALL malformed golden vectors rejected, ALL valid accepted

### LAYER 2B: Backend Enforcement (Week 3-4)

| Task ID | Title                     | Depends On | Hours | Owner | Exit Criteria                  |
| ------- | ------------------------- | ---------- | ----- | ----- | ------------------------------ |
| T2.7    | Replace kernel.py         | T1.5       | 8h    | PLT   | No local hashing               |
| T2.8    | Enforce sequence == index | T2.7       | 2h    | PLT   | Out-of-order rejected          |
| T2.9    | Split export endpoints    | T2.7       | 4h    | PLT   | /export/spec vs /export/report |
| T2.10   | All spec signature algos  | T2.7       | 4h    | SEC   | RSA/ECDSA/HMAC accepted        |
| T2.11   | Durable storage           | T2.7       | 8h    | PLT   | PostgreSQL backend             |

**Blockers:** T1.5 (kernel-py)
**Exit Gate:** `pytest tests/test_import.py` passes with golden vectors

### LAYER 3: Producers (Week 4-5) - PARALLEL EXECUTION

| Task ID | Title                           | Depends On | Hours | Owner | Exit Criteria         |
| ------- | ------------------------------- | ---------- | ----- | ----- | --------------------- |
| T3.1    | connector-template: Fix Python  | T2.1       | 4h    | INT   | Verify accepts output |
| T3.2    | connector-template: Fix TS JSON | T2.1       | 2h    | INT   | Verify accepts output |
| T3.3    | connector-template: Use kernel  | T3.1       | 4h    | INT   | No local hashing      |
| T3.4    | product: Fix packaging          | -          | 2h    | INT   | pip install works     |
| T3.5    | product: Replace evidence.py    | T1.5, T3.4 | 8h    | INT   | No local hashing      |
| T3.6    | product: Fix BaseGuardLane      | T3.5       | 4h    | INT   | v0.2.0 output         |
| T3.7    | product: Fix DocEvidencePack    | T3.5       | 4h    | INT   | v0.2.0 output         |
| T3.8    | council: Replace \_content_hash | T1.5       | 4h    | INT   | No local hashing      |
| T3.9    | council: Validate at build      | T3.8       | 4h    | INT   | Verify accepts output |
| T3.10   | webhook: Refactor sealBundle    | T0.4       | 4h    | INT   | Use kernel            |
| T3.11   | webhook: Fail closed            | T3.10      | 2h    | INT   | Error = hard fail     |
| T3.12   | hardening: Replace hash_chain   | T1.5       | 8h    | INT   | No local hashing      |
| T3.13   | hardening: Enforce sequence     | T3.12      | 4h    | INT   | Verify accepts output |

**Blockers:** T2.1-T2.6 (verify must be strict first)
**Exit Gate:** EVERY producer's output passes verify validation

### LAYER 4: Integration (Week 5-6)

| Task ID | Title                           | Depends On | Hours | Owner | Exit Criteria            |
| ------- | ------------------------------- | ---------- | ----- | ----- | ------------------------ |
| T4.1    | [SECURITY] Auth gate L4         | -          | 2h    | SEC   | Unauth approval rejected |
| T4.2    | [SECURITY] Unknown tool L3      | -          | 1h    | SEC   | Unknown = council review |
| T4.3    | openclaw: Replace canonicalJSON | T3.x       | 8h    | INT   | No local hashing         |
| T4.4    | openclaw: Replace rlm-docsync   | T1.5       | 8h    | INT   | Use kernel-py            |
| T4.5    | openclaw: Wire to backend       | T2.9, T4.4 | 4h    | INT   | Import API called        |
| T4.6    | n8n: Fix artifact_type          | -          | 1h    | INT   | No 422 errors            |
| T4.7    | n8n: Bundle Import node         | T2.9       | 8h    | INT   | Import from workflow     |

**Blockers:** ALL Layer 3 producers must pass verify
**Exit Gate:** Full E2E pipeline test passes

### LAYER 5: Platform (Week 6-7) - PARALLEL TRACK

| Task ID | Title                         | Depends On | Hours | Owner | Exit Criteria       |
| ------- | ----------------------------- | ---------- | ----- | ----- | ------------------- |
| T5.1    | upstream: PowerShell scripts  | -          | 8h    | OPS   | Windows build works |
| T5.2    | upstream: Windows config fix  | T5.1       | 4h    | OPS   | No flaky tests      |
| T5.3    | upstream: Version hook events | -          | 8h    | PLT   | Schema published    |
| T5.4    | source: Low-memory profile    | -          | 2h    | OPS   | WORKERS=1 works     |
| T5.5    | source: Windows-safe build    | T5.1       | 4h    | OPS   | or WSL-only gate    |

**Blockers:** None (parallel track)
**Exit Gate:** Windows CI green without dangerouslyIgnore flag

---

## Part 4: Test Specifications

### 4.1 Unit Tests (Per Repo)

```yaml
guardspine-spec:
  - test_schema_validates_examples.js
  - test_golden_vectors_valid.js
  - test_malformed_rejected.js

guardspine-kernel-py:
  - test_seal_bundle_basic.py
  - test_seal_bundle_multi_item.py
  - test_seal_bundle_signed.py
  - test_verify_bundle_valid.py
  - test_verify_bundle_invalid.py
  - test_canonical_json_sorting.py
  - test_canonical_json_unicode.py

guardspine-verify:
  - test_chain_binding.py
  - test_chain_count.py
  - test_item_id_crossref.py
  - test_zip_safety.py
  - test_version_enforcement.py
  - test_signature_required.py

guardspine-backend:
  - test_import_valid.py
  - test_import_invalid_sequence.py
  - test_import_invalid_version.py
  - test_export_spec.py
  - test_export_report.py
```

### 4.2 Parity Tests (Layer 1)

```python
# tests/test_parity.py

import json
from guardspine_kernel_py import seal_bundle, verify_bundle, canonical_json
from subprocess import run

GOLDEN_VECTORS = [
    "fixtures/golden-vectors/v0.2.0-minimal-bundle.json",
    "fixtures/golden-vectors/v0.2.0-signed-bundle.json",
    "fixtures/golden-vectors/v0.2.0-multi-item-bundle.json",
]

def test_seal_bundle_parity():
    """Python seal_bundle produces identical output to JS sealBundle"""
    for vector_path in GOLDEN_VECTORS:
        with open(vector_path) as f:
            input_data = json.load(f)

        # Python result
        py_result = seal_bundle(input_data["items"])

        # JS result (subprocess)
        js_result = run_js_seal(input_data["items"])

        # MUST be byte-identical
        assert py_result["root_hash"] == js_result["root_hash"]
        assert py_result["hash_chain"] == js_result["hash_chain"]

def test_canonical_json_parity():
    """Python canonical_json produces identical output to JS canonicalJSON"""
    test_objects = [
        {"z": 1, "a": 2},  # Key ordering
        {"emoji": "\\u2764"},  # Unicode
        {"nested": {"b": 1, "a": 2}},  # Nested ordering
    ]
    for obj in test_objects:
        py_result = canonical_json(obj)
        js_result = run_js_canonical(obj)
        assert py_result == js_result, f"Mismatch for {obj}"
```

### 4.3 Contract Tests (Golden Vectors)

```python
# tests/test_contract.py

VALID_VECTORS = glob("fixtures/golden-vectors/v0.2.0-*.json")
MALFORMED_VECTORS = glob("fixtures/golden-vectors/malformed/*.json")
EXPECTED_HASHES = json.load(open("fixtures/golden-vectors/expected-hashes.json"))

def test_valid_vectors_pass():
    """All valid golden vectors must pass verification"""
    for vector_path in VALID_VECTORS:
        bundle = json.load(open(vector_path))
        result = verify_bundle(bundle)
        assert result["valid"] == True, f"Valid vector failed: {vector_path}"

def test_malformed_vectors_fail():
    """All malformed golden vectors must FAIL verification"""
    for vector_path in MALFORMED_VECTORS:
        bundle = json.load(open(vector_path))
        result = verify_bundle(bundle)
        assert result["valid"] == False, f"Malformed vector passed: {vector_path}"

def test_hashes_match_expected():
    """Computed hashes must match expected hashes"""
    for vector_name, expected_hash in EXPECTED_HASHES.items():
        bundle = json.load(open(f"fixtures/golden-vectors/{vector_name}"))
        result = seal_bundle(bundle["items"])
        assert result["root_hash"] == expected_hash, f"Hash mismatch: {vector_name}"
```

### 4.4 Interoperability Tests (Producer -> Verify -> Backend)

```python
# tests/test_interop.py

PRODUCERS = [
    ("connector-template-py", seal_bundle_connector_py),
    ("connector-template-ts", seal_bundle_connector_ts),
    ("guardspine-product", seal_bundle_product),
    ("guardspine-council", seal_bundle_council),
    ("adapter-webhook", seal_bundle_webhook),
    ("openclaw-hardening", seal_bundle_hardening),
    ("guardspine-openclaw", seal_bundle_openclaw),
]

@pytest.mark.parametrize("producer_name,seal_fn", PRODUCERS)
def test_producer_to_verify(producer_name, seal_fn):
    """Each producer's output must pass guardspine-verify"""
    items = load_test_items()
    bundle = seal_fn(items)

    # Verify with guardspine-verify
    result = verify_bundle(bundle)
    assert result["valid"] == True, f"{producer_name} output failed verify"

@pytest.mark.parametrize("producer_name,seal_fn", PRODUCERS)
def test_producer_to_backend(producer_name, seal_fn):
    """Each producer's output must be importable to backend"""
    items = load_test_items()
    bundle = seal_fn(items)

    # Import to backend
    response = backend_client.post("/api/v1/bundles/import", json=bundle)
    assert response.status_code == 200, f"{producer_name} import failed"

def test_all_producers_same_hash():
    """All producers sealing same input must produce same root_hash"""
    items = load_test_items()
    hashes = set()

    for producer_name, seal_fn in PRODUCERS:
        bundle = seal_fn(items)
        hashes.add(bundle["root_hash"])

    assert len(hashes) == 1, f"Hash divergence: {hashes}"
```

### 4.5 Regression Tests

```python
# tests/test_regression.py

PRODUCTION_BUNDLES = glob("fixtures/production-snapshots/*.json")

def test_existing_bundles_still_valid():
    """
    CRITICAL: No existing valid bundle should become invalid after fixes.
    This prevents breaking production data.
    """
    for bundle_path in PRODUCTION_BUNDLES:
        bundle = json.load(open(bundle_path))
        result = verify_bundle(bundle)

        # If it was valid before, it must be valid now
        if bundle.get("_was_valid", True):
            assert result["valid"] == True, \
                f"REGRESSION: {bundle_path} was valid, now invalid"
```

### 4.6 End-to-End Tests

```python
# tests/test_e2e.py

def test_full_evidence_pipeline():
    """
    Full pipeline: Agent action -> seal -> import -> verify -> export -> verify
    """
    # 1. Simulate agent action
    action = {"tool": "file_write", "path": "/tmp/test.txt", "content": "hello"}

    # 2. Create evidence item
    item = create_evidence_item(action)

    # 3. Seal bundle (using kernel-py)
    bundle = seal_bundle([item])

    # 4. Verify locally
    local_result = verify_bundle(bundle)
    assert local_result["valid"] == True

    # 5. Import to backend
    import_response = backend_client.post("/api/v1/bundles/import", json=bundle)
    assert import_response.status_code == 200
    bundle_id = import_response.json()["bundle_id"]

    # 6. Export from backend
    export_response = backend_client.get(f"/api/v1/bundles/{bundle_id}/export/spec")
    exported_bundle = export_response.json()

    # 7. Verify exported bundle
    final_result = verify_bundle(exported_bundle)
    assert final_result["valid"] == True

    # 8. Hashes must match
    assert bundle["root_hash"] == exported_bundle["root_hash"]

def test_security_l4_auth_required():
    """L4 approval without auth token must be rejected"""
    response = backend_client.post(
        "/api/v1/approvals/create",
        json={"action_id": "test", "decision": "approve"},
        headers={}  # No auth
    )
    assert response.status_code == 401

def test_n8n_artifact_type_accepted():
    """n8n nodes sending artifact_type (not artifact_kind) must succeed"""
    response = backend_client.post(
        "/api/v1/evidence/seal",
        json={
            "artifact_type": "image",  # CORRECT field
            "content": "base64data..."
        }
    )
    assert response.status_code == 200
```

---

## Part 5: Dry Run Protocol

### 5.1 Pre-Merge Dry Run

Before ANY merge to main:

```bash
#!/bin/bash
# dry-run.sh

echo "=== DRY RUN PROTOCOL ==="

# 1. Create test bundles with OLD code (current main)
git stash
npm run test:create-bundles > /tmp/old-bundles/

# 2. Apply changes
git stash pop

# 3. Verify OLD bundles with NEW code
npm run test:verify-bundles /tmp/old-bundles/
if [ $? -ne 0 ]; then
    echo "REGRESSION: Old bundles fail with new code"
    exit 1
fi

# 4. Create NEW bundles
npm run test:create-bundles > /tmp/new-bundles/

# 5. Verify NEW bundles pass
npm run test:verify-bundles /tmp/new-bundles/
if [ $? -ne 0 ]; then
    echo "ERROR: New bundles fail verification"
    exit 1
fi

# 6. Cross-verify: NEW bundles with OLD verify (compatibility)
git stash
npm run test:verify-bundles /tmp/new-bundles/
git stash pop
if [ $? -ne 0 ]; then
    echo "WARNING: New bundles incompatible with old verify (breaking change)"
    # This is OK if intentional, but must be documented
fi

echo "=== DRY RUN PASSED ==="
```

### 5.2 Interop Dry Run Matrix

Before Layer 4 integration:

| Producer     | Verifier | Backend | Expected | Actual |
| ------------ | -------- | ------- | -------- | ------ |
| connector-py | verify   | backend | PASS     | ?      |
| connector-ts | verify   | backend | PASS     | ?      |
| product      | verify   | backend | PASS     | ?      |
| council      | verify   | backend | PASS     | ?      |
| webhook      | verify   | backend | PASS     | ?      |
| hardening    | verify   | backend | PASS     | ?      |
| openclaw     | verify   | backend | PASS     | ?      |

**ALL cells must be PASS before Layer 4 starts.**

---

## Part 6: CI/CD Integration

### 6.1 Pre-Merge Gate (All Repos)

```yaml
# .github/workflows/pre-merge.yml
name: Pre-Merge Gate

on: [pull_request]

jobs:
  parity-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: npm ci && pip install -e .

      - name: Fetch golden vectors
        run: |
          git clone --depth 1 https://github.com/org/guardspine-spec.git /tmp/spec
          cp -r /tmp/spec/fixtures/golden-vectors ./fixtures/

      - name: Run parity tests
        run: pytest tests/test_parity.py -v

      - name: Run contract tests
        run: pytest tests/test_contract.py -v

      - name: Run regression tests
        run: pytest tests/test_regression.py -v

  interop-test:
    runs-on: ubuntu-latest
    needs: parity-test
    steps:
      - name: Run interop tests
        run: pytest tests/test_interop.py -v
```

### 6.2 Nightly Full E2E

```yaml
# .github/workflows/nightly-e2e.yml
name: Nightly E2E

on:
  schedule:
    - cron: "0 2 * * *" # 2 AM daily

jobs:
  e2e:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
      redis:
        image: redis:7

    steps:
      - name: Checkout all repos
        run: |
          git clone https://github.com/org/guardspine-backend.git
          git clone https://github.com/org/guardspine-verify.git
          # ... all repos

      - name: Start backend
        run: cd guardspine-backend && docker-compose up -d

      - name: Run E2E tests
        run: pytest tests/test_e2e.py -v --tb=long

      - name: Notify on failure
        if: failure()
        run: |
          curl -X POST $SLACK_WEBHOOK -d '{"text": "E2E tests failed!"}'
```

---

## Part 7: Milestone Checkpoints

| Milestone       | Week | Exit Criteria                      | Verification                   |
| --------------- | ---- | ---------------------------------- | ------------------------------ |
| M0: Foundation  | 1    | Golden vectors created, spec fixed | `npm run test` green in spec   |
| M1: Bridge      | 2    | kernel-py 100% parity              | `pytest test_parity.py` passes |
| M2: Validators  | 3    | verify + backend strict            | ALL malformed rejected         |
| M3: Producers   | 5    | ALL producers pass verify          | Interop matrix 7/7 PASS        |
| M4: Integration | 6    | Full E2E pipeline works            | E2E test passes                |
| M5: Platform    | 7    | Windows CI green                   | No dangerouslyIgnore flag      |
| M6: Release     | 8    | All repos score >= 8.0             | Audit scorecard                |

---

## Part 8: Risk Mitigation

| Risk                              | Likelihood | Impact   | Mitigation                                 |
| --------------------------------- | ---------- | -------- | ------------------------------------------ |
| Python-Node bridge too slow       | Medium     | Medium   | Add connection pooling, consider HTTP mode |
| Breaking existing production data | High       | Critical | REGRESSION TESTS on production snapshots   |
| Hash algorithm divergence         | Medium     | High     | Golden vectors locked in CI                |
| Merge conflicts across repos      | High       | Medium   | Coordinated merge windows                  |
| Windows CI flakiness              | High       | Medium   | Low-memory profile, retry logic            |

---

## Appendix: Task Dependency Graph (Mermaid)

```mermaid
gantt
    title GuardSpine Remediation Critical Path
    dateFormat  YYYY-MM-DD
    axisFormat  %m-%d

    section Layer 0
    T0.1 Fix README          :crit, t01, 2026-02-03, 1d
    T0.2 Update examples     :crit, t02, after t01, 2d
    T0.3 Golden vectors      :crit, t03, after t01, 4d
    T0.4 Kernel version      :t04, 2026-02-03, 1d
    T0.5 ajv validation      :t05, after t02, 2d

    section Layer 1
    T1.1 Package scaffold    :crit, t11, after t03, 2d
    T1.2 seal_bundle bridge  :crit, t12, after t11, 2d
    T1.3 verify_bundle bridge:crit, t13, after t11, 2d
    T1.4 canonical_json      :t14, after t11, 1d
    T1.5 Parity tests        :crit, t15, after t12 t13 t14, 1d

    section Layer 2
    T2.1 Chain binding       :crit, t21, after t15, 4d
    T2.2 Chain count         :t22, after t21, 1d
    T2.3 item_id crossref    :t23, after t21, 2d
    T2.4 ZIP safety          :t24, after t15, 2d
    T2.5 Version enforcement :t25, after t15, 2d
    T2.7 Backend kernel-py   :crit, t27, after t15, 4d
    T2.8 Enforce sequence    :t28, after t27, 1d
    T2.9 Split export        :t29, after t27, 2d

    section Layer 3 (Parallel)
    T3.1 connector-py        :t31, after t21, 2d
    T3.3 connector-kernel    :t33, after t31, 2d
    T3.5 product evidence.py :t35, after t15, 4d
    T3.8 council hash        :t38, after t15, 2d
    T3.10 webhook seal       :t310, after t04, 2d
    T3.12 hardening hash     :t312, after t15, 4d

    section Layer 4
    T4.1 Security L4 auth    :crit, t41, 2026-02-03, 1d
    T4.3 openclaw canonical  :crit, t43, after t31 t35 t38 t312, 4d
    T4.5 openclaw backend    :t45, after t43 t29, 2d
    T4.6 n8n artifact_type   :t46, 2026-02-03, 1d
    T4.7 n8n Bundle Import   :t47, after t29, 4d

    section Layer 5 (Parallel)
    T5.1 PowerShell scripts  :t51, 2026-02-10, 4d
    T5.2 Windows config fix  :t52, after t51, 2d
    T5.3 Hook versioning     :t53, 2026-02-10, 4d
```

---

**Document Version:** 1.0.0
**Author:** Sequential Planning Analysis
**Date:** 2026-02-03
**Next Review:** After M2 (Week 3)
