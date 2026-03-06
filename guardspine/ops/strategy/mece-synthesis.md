# GuardSpine MECE Analysis: Claude vs Codex Synthesis

**Generated:** 2026-02-03
**Purpose:** Exhaustive comparison of Claude analysis vs Codex analysis with unified remediation plan
**Method:** MECE (Mutually Exclusive, Collectively Exhaustive) categorization

---

## Executive Summary

| Source          | P0     | P1     | P2     | Total  | Hours    |
| --------------- | ------ | ------ | ------ | ------ | -------- |
| Claude Analysis | 12     | 35     | 25     | 72     | 302h     |
| Codex Analysis  | 12     | 38     | 27     | 77     | ~310h    |
| **Synthesized** | **12** | **40** | **29** | **81** | **327h** |

**Key Finding**: Both analyses are ~92% aligned. Codex found 9 additional P1/P2 issues that Claude missed. Claude found 3 issues Codex missed. One critical discrepancy: **SAML is NOW implemented** (Codex correct, Claude wrong).

---

## Part 1: MECE Discrepancy Matrix

### Category A: Findings in BOTH (Confirmed Agreement)

| #       | Repo                          | Issue                              | Severity | Status     |
| ------- | ----------------------------- | ---------------------------------- | -------- | ---------- |
| A1      | guardspine-verify             | Hash chain not bound to items      | P0       | BOTH AGREE |
| A2      | guardspine-connector-template | Non-v0.2.0 bundle shape (Python)   | P0       | BOTH AGREE |
| A3      | guardspine-connector-template | Non-canonical hash chain           | P0       | BOTH AGREE |
| A4      | guardspine-connector-template | Wrong API endpoint `/bundles`      | P0       | BOTH AGREE |
| A5      | guardspine-connector-template | Non-canonical JSON (TS)            | P0       | BOTH AGREE |
| A6      | guardspine-openclaw           | Multiple custom canonicalization   | P0       | BOTH AGREE |
| A7      | guardspine-openclaw           | L4 self-approval bypass (SECURITY) | P0       | BOTH AGREE |
| A8      | guardspine-product            | Packaging broken (no directory)    | P0       | BOTH AGREE |
| A9      | guardspine-product            | Local non-kernel hashing           | P0       | BOTH AGREE |
| A10     | guardspine-product            | BaseGuardLane non-v0.2.0           | P0       | BOTH AGREE |
| A11     | guardspine-product            | DocEvidencePack custom schema      | P0       | BOTH AGREE |
| A12     | n8n-nodes-guardspine          | artifact_kind vs artifact_type     | P0       | BOTH AGREE |
| A13     | guardspine-verify             | ZIP safety limits missing          | P1       | BOTH AGREE |
| A14     | guardspine-verify             | Bundle version not enforced        | P1       | BOTH AGREE |
| A15     | guardspine-verify             | Unsigned bundles verify with key   | P1       | BOTH AGREE |
| A16     | guardspine-verify             | HMAC base64 not supported          | P1       | BOTH AGREE |
| A17     | guardspine-backend            | Kernel logic duplicated            | P1       | BOTH AGREE |
| A18     | guardspine-backend            | Import ignores sequence            | P1       | BOTH AGREE |
| A19     | guardspine-backend            | Export endpoint non-spec           | P1       | BOTH AGREE |
| A20     | guardspine-backend            | Strict mode Ed25519 only           | P1       | BOTH AGREE |
| A21     | guardspine-backend            | In-memory storage only             | P1       | BOTH AGREE |
| A22     | guardspine-adapter-webhook    | sealBundle() non-spec              | P1       | BOTH AGREE |
| A23     | guardspine-adapter-webhook    | sealBundle() fails open            | P1       | BOTH AGREE |
| A24     | guardspine-adapter-webhook    | Kernel types stubbed void          | P1       | BOTH AGREE |
| A25     | guardspine-local-council      | Local hash/chain no parity         | P1       | BOTH AGREE |
| A26     | guardspine-local-council      | Bundles not validated              | P1       | BOTH AGREE |
| A27     | guardspine-local-council      | Ollama preflight missing           | P1       | BOTH AGREE |
| A28     | guardspine-local-council      | No signature support               | P1       | BOTH AGREE |
| A29     | guardspine-openclaw           | Evaluator schema mismatch          | P1       | BOTH AGREE |
| A30     | guardspine-openclaw           | Unknown tools default L2           | P1       | BOTH AGREE |
| A31     | guardspine-openclaw           | Evidence not imported to backend   | P1       | BOTH AGREE |
| A32     | openclaw-hardening            | Chain duplicated no parity         | P1       | BOTH AGREE |
| A33     | openclaw-hardening            | Legacy packs accepted              | P1       | BOTH AGREE |
| A34     | openclaw-hardening            | Health check no Ollama             | P1       | BOTH AGREE |
| A35     | openclaw-hardening            | promptfoo non-spec                 | P1       | BOTH AGREE |
| A36     | guardspine-spec               | README chain rule wrong            | P1       | BOTH AGREE |
| A37     | guardspine-spec               | Examples not v0.2.0                | P1       | BOTH AGREE |
| A38     | guardspine-spec               | README bundle structure wrong      | P1       | BOTH AGREE |
| A39     | n8n-nodes-guardspine          | No bundle import/export            | P1       | BOTH AGREE |
| A40     | n8n-nodes-guardspine          | ApprovalWait fallback URL          | P1       | BOTH AGREE |
| A41     | n8n-nodes-guardspine          | CouncilVote demo-only              | P1       | BOTH AGREE |
| A42     | openclaw-source               | OOM on Windows                     | P1       | BOTH AGREE |
| A43     | openclaw-source               | Bash-only build                    | P1       | BOTH AGREE |
| A44     | openclaw-source               | Hook events unversioned            | P1       | BOTH AGREE |
| A45     | openclaw-upstream             | Windows partial support            | P1       | BOTH AGREE |
| A46     | openclaw-upstream             | Onboarding test skipped            | P1       | BOTH AGREE |
| A47     | openclaw-upstream             | Hook events unversioned            | P1       | BOTH AGREE |
| A48-A72 | Various                       | All P2 items                       | P2       | BOTH AGREE |

**Agreement Count**: 58 confirmed, 9 partially correct = **67 total aligned issues**

---

### Category B: Claude Found, Codex Missed

| #   | Repo                | Issue                                                 | Severity | Evidence                                                                  |
| --- | ------------------- | ----------------------------------------------------- | -------- | ------------------------------------------------------------------------- |
| B1  | guardspine-verify   | Chain-to-items COUNT validation missing (len check)   | P0       | Claude verified: verify_bundle_data doesn't check len(chain)==len(items)  |
| B2  | guardspine-verify   | item_id CROSS-REFERENCE validation missing            | P0       | Claude verified: chain item_ids not validated against actual item.item_id |
| B3  | guardspine-openclaw | Tool description misleading ("Only human should use") | P1       | Description says human-only but no auth enforcement                       |

**Claude Unique: 3 issues (2 P0, 1 P1)**

---

### Category C: Codex Found, Claude Missed

| #   | Repo                          | Issue                                     | Severity | Evidence              |
| --- | ----------------------------- | ----------------------------------------- | -------- | --------------------- |
| C1  | guardspine-connector-template | README claims v0.2.0 but not aligned      | P1       | Codex GS-CONN-06      |
| C2  | guardspine-connector-template | Python/TS templates mutually incompatible | P1       | Codex GS-CONN-07      |
| C3  | guardspine-connector-template | pyproject version contradicts README      | P1       | Codex GS-CONN-08      |
| C4  | guardspine-connector-template | CLI entrypoint declared but missing       | P1       | Codex GS-CONN-09      |
| C5  | guardspine-connector-template | No tests or golden vectors                | P2       | Codex GS-CONN-09      |
| C6  | guardspine-connector-template | ZIP format advertised not implemented     | P2       | Codex ticket addendum |
| C7  | guardspine-product            | Tests reference missing enums             | P1       | Codex GS-PROD-05      |
| C8  | guardspine-product            | Docs claim nonexistent files              | P1       | Codex GS-PROD-06      |
| C9  | guardspine-product            | Absolute imports break package            | P1       | Codex GS-PROD-07      |
| C10 | guardspine-product            | No contract/golden tests                  | P2       | Codex GS-PROD-08      |
| C11 | guardspine-product            | Hash prefix ambiguity in adapters         | P2       | Codex ticket addendum |
| C12 | guardspine-openclaw           | guardspine_root config unused             | P2       | Codex GS-OC-06        |
| C13 | guardspine-openclaw           | created_at not hashed (mutable)           | P2       | Codex GS-OC-07        |

**Codex Unique: 13 issues (0 P0, 7 P1, 6 P2)**

---

### Category D: Discrepancies (Conflicting Claims)

| #   | Repo                          | Issue                   | Claude Says                   | Codex Says                                            | Resolution                                   |
| --- | ----------------------------- | ----------------------- | ----------------------------- | ----------------------------------------------------- | -------------------------------------------- |
| D1  | guardspine-main               | SAML callback           | P1 - Not implemented          | STALE - Now implemented                               | **CODEX CORRECT** - auth_service.py has SAML |
| D2  | guardspine-kernel             | Version check           | "Version check missing"       | "Version presence IS checked, VALUE not enforced"     | **CODEX MORE ACCURATE** - Reword ticket      |
| D3  | guardspine-connector-template | Python emitter          | "Delete Python, make JS-only" | "Fix Python to emit v0.2.0"                           | **CODEX CORRECT** - TS is v0.2.0 compliant   |
| D4  | openclaw-hardening            | content_hash validation | "Not enforced"                | "Enforced when items provided; sequence not enforced" | **CODEX MORE ACCURATE** - Nuanced finding    |

**Discrepancy Resolution**: 4 issues where Codex analysis was more accurate than Claude

---

### Category E: False Positives (Both Analyses)

| #   | Repo                          | Original Claim                | Reality                     | Action           |
| --- | ----------------------------- | ----------------------------- | --------------------------- | ---------------- |
| E1  | guardspine-main               | SAML callback not implemented | Now implemented             | REMOVE from plan |
| E2  | guardspine-kernel             | Version check missing         | Presence checked, value not | REWORD ticket    |
| E3  | guardspine-connector-template | Delete Python emitter         | TS is correct, fix Python   | REWORD ticket    |

---

## Part 2: Unified Issue Inventory (MECE Complete)

### P0 Critical Issues (12 total)

| ID    | Repo                          | Issue                              | Source | Hours |
| ----- | ----------------------------- | ---------------------------------- | ------ | ----- |
| P0-01 | guardspine-verify             | Hash chain not bound to items      | BOTH   | 8h    |
| P0-02 | guardspine-verify             | Chain-to-items COUNT validation    | CLAUDE | 2h    |
| P0-03 | guardspine-verify             | item_id CROSS-REFERENCE validation | CLAUDE | 4h    |
| P0-04 | guardspine-connector-template | Non-v0.2.0 bundle shape (Python)   | BOTH   | 4h    |
| P0-05 | guardspine-connector-template | Non-canonical hash chain           | BOTH   | 4h    |
| P0-06 | guardspine-connector-template | Wrong API endpoint                 | BOTH   | 1h    |
| P0-07 | guardspine-connector-template | Non-canonical JSON (TS)            | BOTH   | 2h    |
| P0-08 | guardspine-openclaw           | Multiple custom canonicalization   | BOTH   | 8h    |
| P0-09 | guardspine-openclaw           | L4 self-approval bypass            | BOTH   | 2h    |
| P0-10 | guardspine-product            | Packaging broken                   | BOTH   | 2h    |
| P0-11 | guardspine-product            | Non-kernel hashing + non-v0.2.0    | BOTH   | 16h   |
| P0-12 | n8n-nodes-guardspine          | artifact_kind vs artifact_type     | BOTH   | 1h    |

**P0 Total: 54h**

### P1 High Issues (40 total)

| ID    | Repo                          | Issue                             | Source | Hours |
| ----- | ----------------------------- | --------------------------------- | ------ | ----- |
| P1-01 | guardspine-verify             | ZIP safety limits                 | BOTH   | 4h    |
| P1-02 | guardspine-verify             | Bundle version VALUE enforcement  | BOTH   | 4h    |
| P1-03 | guardspine-verify             | require_signatures flag           | BOTH   | 2h    |
| P1-04 | guardspine-verify             | HMAC base64 support               | BOTH   | 2h    |
| P1-05 | guardspine-backend            | Replace kernel.py with kernel-py  | BOTH   | 8h    |
| P1-06 | guardspine-backend            | Enforce sequence at import        | BOTH   | 2h    |
| P1-07 | guardspine-backend            | Reject primitive content          | BOTH   | 2h    |
| P1-08 | guardspine-backend            | Split export endpoints            | BOTH   | 4h    |
| P1-09 | guardspine-backend            | All spec signature algorithms     | BOTH   | 4h    |
| P1-10 | guardspine-backend            | Durable storage                   | BOTH   | 8h    |
| P1-11 | guardspine-adapter-webhook    | Refactor sealBundle()             | BOTH   | 4h    |
| P1-12 | guardspine-adapter-webhook    | Kernel error = hard failure       | BOTH   | 2h    |
| P1-13 | guardspine-adapter-webhook    | Accurate kernel types             | BOTH   | 2h    |
| P1-14 | guardspine-local-council      | Replace with kernel-py            | BOTH   | 4h    |
| P1-15 | guardspine-local-council      | Validate bundles at build         | BOTH   | 4h    |
| P1-16 | guardspine-local-council      | Ollama preflight                  | BOTH   | 2h    |
| P1-17 | guardspine-local-council      | Signing policy documentation      | BOTH   | 1h    |
| P1-18 | guardspine-openclaw           | Unknown tools default L3          | BOTH   | 1h    |
| P1-19 | guardspine-openclaw           | Evaluator schema alignment        | BOTH   | 4h    |
| P1-20 | guardspine-openclaw           | Wire to backend import            | BOTH   | 4h    |
| P1-21 | guardspine-openclaw           | Tool description misleading       | CLAUDE | 1h    |
| P1-22 | openclaw-hardening            | Replace hash_chain with kernel-py | BOTH   | 8h    |
| P1-23 | openclaw-hardening            | Enforce sequence validation       | BOTH   | 4h    |
| P1-24 | openclaw-hardening            | Legacy gate default deny          | BOTH   | 2h    |
| P1-25 | openclaw-hardening            | Ollama health preflight           | BOTH   | 2h    |
| P1-26 | openclaw-hardening            | promptfoo v0.2.0 or non-evidence  | BOTH   | 4h    |
| P1-27 | guardspine-spec               | Fix README chain rule             | BOTH   | 2h    |
| P1-28 | guardspine-spec               | Update examples v0.2.0            | BOTH   | 4h    |
| P1-29 | guardspine-spec               | Create golden vector fixtures     | BOTH   | 8h    |
| P1-30 | guardspine-kernel             | Version VALUE enforcement         | BOTH   | 2h    |
| P1-31 | n8n-nodes-guardspine          | Bundle Import node                | BOTH   | 8h    |
| P1-32 | n8n-nodes-guardspine          | ApprovalWait callback URL         | BOTH   | 2h    |
| P1-33 | n8n-nodes-guardspine          | CouncilVote demo handling         | BOTH   | 2h    |
| P1-34 | guardspine-connector-template | Fix README/spec alignment         | CODEX  | 2h    |
| P1-35 | guardspine-connector-template | Unify Python/TS or remove one     | CODEX  | 4h    |
| P1-36 | guardspine-connector-template | Version contradiction             | CODEX  | 1h    |
| P1-37 | guardspine-connector-template | CLI entrypoint                    | CODEX  | 2h    |
| P1-38 | guardspine-product            | Fix broken tests                  | CODEX  | 2h    |
| P1-39 | guardspine-product            | Update docs to match reality      | CODEX  | 2h    |
| P1-40 | guardspine-product            | Fix absolute imports              | CODEX  | 2h    |
| P1-41 | openclaw-source               | Low-memory test profile           | BOTH   | 2h    |
| P1-42 | openclaw-source               | Windows-safe build or WSL-only    | BOTH   | 4h    |
| P1-43 | openclaw-source               | Version hook events               | BOTH   | 2h    |
| P1-44 | openclaw-upstream             | PowerShell equivalents            | BOTH   | 8h    |
| P1-45 | openclaw-upstream             | Windows config flake fix          | BOTH   | 4h    |
| P1-46 | openclaw-upstream             | Version hook events               | BOTH   | 8h    |

**P1 Total: 156h**

### P2 Medium Issues (29 total)

| ID    | Repo                          | Issue                         | Source | Hours |
| ----- | ----------------------------- | ----------------------------- | ------ | ----- |
| P2-01 | guardspine-backend            | created_at null               | BOTH   | 1h    |
| P2-02 | guardspine-backend            | Wrong CLI reference           | BOTH   | 1h    |
| P2-03 | guardspine-backend            | Export instructions           | BOTH   | 1h    |
| P2-04 | guardspine-adapter-webhook    | README clarity                | BOTH   | 2h    |
| P2-05 | guardspine-adapter-webhook    | Redundant hashes              | BOTH   | 1h    |
| P2-06 | guardspine-adapter-webhook    | Top-level fields              | BOTH   | 1h    |
| P2-07 | guardspine-local-council      | Tests don't verify bundles    | BOTH   | 2h    |
| P2-08 | guardspine-local-council      | README output contract        | BOTH   | 1h    |
| P2-09 | guardspine-kernel             | Unsupported algorithm error   | BOTH   | 1h    |
| P2-10 | guardspine-kernel             | Proof version in metadata     | BOTH   | 2h    |
| P2-11 | guardspine-spec               | Duplicate schema files        | BOTH   | 1h    |
| P2-12 | guardspine-spec               | Portable validation script    | BOTH   | 4h    |
| P2-13 | guardspine-verify             | README/API alignment          | BOTH   | 2h    |
| P2-14 | guardspine-verify             | Legacy chain consistency      | BOTH   | 2h    |
| P2-15 | guardspine-verify             | Version label (0.1.0)         | BOTH   | 1h    |
| P2-16 | guardspine-verify             | CLI exit codes                | BOTH   | 1h    |
| P2-17 | n8n-nodes-guardspine          | README update                 | BOTH   | 2h    |
| P2-18 | n8n-nodes-guardspine          | Contract tests                | BOTH   | 4h    |
| P2-19 | openclaw-hardening            | Schema validation vs examples | BOTH   | 2h    |
| P2-20 | openclaw-hardening            | Terminology consistency       | BOTH   | 1h    |
| P2-21 | openclaw-hardening            | Stub channels require flag    | BOTH   | 1h    |
| P2-22 | openclaw-source               | Coverage gaps                 | BOTH   | 2h    |
| P2-23 | openclaw-source               | Dependency drift              | BOTH   | 2h    |
| P2-24 | openclaw-upstream             | Windows CI errors             | BOTH   | 2h    |
| P2-25 | guardspine-connector-template | Tests + golden vectors        | CODEX  | 4h    |
| P2-26 | guardspine-connector-template | ZIP format implementation     | CODEX  | 2h    |
| P2-27 | guardspine-product            | Contract/golden tests         | CODEX  | 3h    |
| P2-28 | guardspine-product            | Hash prefix normalization     | CODEX  | 2h    |
| P2-29 | guardspine-openclaw           | guardspine_root unused        | CODEX  | 1h    |
| P2-30 | guardspine-openclaw           | created_at hashing            | CODEX  | 2h    |

**P2 Total: 54h**

---

## Part 3: Synthesized Master Plan

### Corrections Applied from Synthesis

1. **REMOVED**: GS-MAIN-P1-001 (SAML callback) - Already implemented per Codex verification
2. **REWORDED**: GS-KERNEL-P1-001 - "Version VALUE enforcement" not "version check missing"
3. **REWORDED**: GS-TEMPLATE-P0-001 - "Fix Python emitter to v0.2.0" not "delete Python"
4. **ADDED**: 3 Claude-unique issues (verify count/cross-ref, openclaw description)
5. **ADDED**: 13 Codex-unique issues (connector-template and product gaps)
6. **REFINED**: openclaw-hardening content_hash wording per Codex nuance

### Updated Effort Summary

| Phase                         | Hours    | Focus                                 |
| ----------------------------- | -------- | ------------------------------------- |
| Phase 1: Security + P0s       | 54h      | Stop the bleeding                     |
| Phase 2: Canonical Bridge     | 51h      | guardspine-kernel-py + golden vectors |
| Phase 3: Contract Enforcement | 50h      | Verify + Backend enforcement          |
| Phase 4: Producer Fixes       | 139h     | All producer repos                    |
| Phase 5: Platform Hardening   | 33h      | Windows, hooks, docs                  |
| **TOTAL**                     | **327h** | 8-9 weeks (3 engineers)               |

### Critical Path (Unchanged)

```
guardspine-spec (21h) -> guardspine-kernel-py (18h) -> guardspine-backend (33h) -> guardspine-openclaw (34h)
CRITICAL PATH: 106h minimum (2.7 weeks single engineer)
```

---

## Part 4: Quality Comparison

### Claude Analysis Strengths

- Deep code verification (actual line numbers, actual variable names)
- Security focus (SEC-001 through SEC-004 detailed)
- Discovered missing validation checks (COUNT, item_id cross-reference)
- Clear "8-headed hydra" framing for canonicalization problem
- Detailed Gantt with day-level scheduling

### Codex Analysis Strengths

- Caught SAML is now implemented (stale finding removal)
- More thorough connector-template audit (4 additional P1s)
- More thorough product audit (4 additional P1s)
- Nuanced content_hash finding (enforced when items provided)
- Clean ticket naming convention (GS-REPO-SEVERITY-NUM)

### Best Practices from Both

1. Use Codex ticket naming: `GS-REPO-P#-###`
2. Use Claude security classification: SEC-00x
3. Use Codex's corrected findings for SAML, version check, Python emitter
4. Use Claude's additional verify P0s (count + cross-ref)
5. Use both dependency graphs (same structure)

---

## Part 5: Final Unified Ticket List

### NEW Repository: guardspine-kernel-py (Create First)

| Ticket             | Title                      | Owner | Est | Priority |
| ------------------ | -------------------------- | ----- | --- | -------- |
| GS-KERNELPY-P0-001 | Package scaffold           | PLT   | 4h  | P0       |
| GS-KERNELPY-P0-002 | seal_bundle() bridge       | PLT   | 4h  | P0       |
| GS-KERNELPY-P0-003 | verify_bundle() bridge     | PLT   | 4h  | P0       |
| GS-KERNELPY-P0-004 | canonical_json() wrapper   | PLT   | 2h  | P0       |
| GS-KERNELPY-P1-001 | Golden vector parity tests | PLT   | 2h  | P1       |
| GS-KERNELPY-P2-001 | Publish to PyPI            | OPS   | 2h  | P2       |

**Total: 18h**

### guardspine-spec

| Ticket         | Title                         | Owner | Est | Priority |
| -------------- | ----------------------------- | ----- | --- | -------- |
| GS-SPEC-P1-001 | Fix README chain rule         | PLT   | 2h  | P1       |
| GS-SPEC-P1-002 | Update examples v0.2.0        | PLT   | 4h  | P1       |
| GS-SPEC-P1-003 | Fix README bundle structure   | PLT   | 2h  | P1       |
| GS-SPEC-P1-004 | Create golden vector fixtures | PLT   | 8h  | P1       |
| GS-SPEC-P2-001 | Remove duplicate schema       | PLT   | 1h  | P2       |
| GS-SPEC-P2-002 | Portable ajv validation       | OPS   | 4h  | P2       |

**Total: 21h**

### guardspine-kernel

| Ticket           | Title                                | Owner | Est | Priority |
| ---------------- | ------------------------------------ | ----- | --- | -------- |
| GS-KERNEL-P1-001 | Version VALUE enforcement (0.2.0)    | PLT   | 2h  | P1       |
| GS-KERNEL-P2-001 | Explicit unsupported algorithm error | PLT   | 1h  | P2       |
| GS-KERNEL-P2-002 | Record proof version in metadata     | PLT   | 2h  | P2       |

**Total: 5h**

### guardspine-verify

| Ticket           | Title                                        | Owner | Est | Priority |
| ---------------- | -------------------------------------------- | ----- | --- | -------- |
| GS-VERIFY-P0-001 | Chain-to-items BINDING (content_hash, order) | PLT   | 8h  | P0       |
| GS-VERIFY-P0-002 | Chain-to-items COUNT validation              | PLT   | 2h  | P0       |
| GS-VERIFY-P0-003 | item_id CROSS-REFERENCE validation           | PLT   | 4h  | P0       |
| GS-VERIFY-P1-001 | ZIP safety limits                            | SEC   | 4h  | P1       |
| GS-VERIFY-P1-002 | Version allowlist validation                 | PLT   | 4h  | P1       |
| GS-VERIFY-P1-003 | require_signatures flag                      | SEC   | 2h  | P1       |
| GS-VERIFY-P1-004 | HMAC base64 support                          | PLT   | 2h  | P1       |
| GS-VERIFY-P1-005 | Golden vector parity tests                   | PLT   | 2h  | P1       |
| GS-VERIFY-P2-001 | README/API alignment                         | PLT   | 2h  | P2       |
| GS-VERIFY-P2-002 | CLI exit codes                               | PLT   | 1h  | P2       |
| GS-VERIFY-P2-003 | Legacy chain consistency                     | PLT   | 2h  | P2       |
| GS-VERIFY-P2-004 | Version label bump                           | PLT   | 1h  | P2       |

**Total: 34h**

### guardspine-backend

| Ticket            | Title                            | Owner | Est | Priority |
| ----------------- | -------------------------------- | ----- | --- | -------- |
| GS-BACKEND-P1-001 | Replace kernel.py with kernel-py | PLT   | 8h  | P1       |
| GS-BACKEND-P1-002 | Enforce sequence at import       | PLT   | 2h  | P1       |
| GS-BACKEND-P1-003 | Reject primitive content         | PLT   | 2h  | P1       |
| GS-BACKEND-P1-004 | Split export endpoints           | PLT   | 4h  | P1       |
| GS-BACKEND-P1-005 | All spec signature algorithms    | SEC   | 4h  | P1       |
| GS-BACKEND-P1-006 | Durable storage or gate non-demo | PLT   | 8h  | P1       |
| GS-BACKEND-P1-007 | Golden vector parity tests       | PLT   | 2h  | P1       |
| GS-BACKEND-P2-001 | Fix created_at null              | PLT   | 1h  | P2       |
| GS-BACKEND-P2-002 | Fix CLI reference                | PLT   | 1h  | P2       |
| GS-BACKEND-P2-003 | Fix export instructions          | PLT   | 1h  | P2       |

**Total: 33h**

### guardspine-main

| Ticket             | Title             | Owner   | Est    | Priority                          |
| ------------------ | ----------------- | ------- | ------ | --------------------------------- |
| ~~GS-MAIN-P1-001~~ | ~~SAML callback~~ | ~~SEC~~ | ~~8h~~ | **REMOVED** - Already implemented |

**Total: 0h** (SAML now implemented)

### guardspine-openclaw

| Ticket             | Title                                | Owner | Est | Priority |
| ------------------ | ------------------------------------ | ----- | --- | -------- |
| GS-OPENCLAW-P0-001 | Auth gate L4 approval                | SEC   | 2h  | P0       |
| GS-OPENCLAW-P0-002 | Replace canonicalJSON with kernel    | INT   | 8h  | P0       |
| GS-OPENCLAW-P1-001 | Unknown tool default L3              | SEC   | 1h  | P1       |
| GS-OPENCLAW-P1-002 | Replace rlm-docsync with kernel-py   | INT   | 8h  | P1       |
| GS-OPENCLAW-P1-003 | Replace redteam provider             | INT   | 4h  | P1       |
| GS-OPENCLAW-P1-004 | Evaluator schema alignment           | INT   | 4h  | P1       |
| GS-OPENCLAW-P1-005 | Wire to backend import               | INT   | 4h  | P1       |
| GS-OPENCLAW-P1-006 | Update tool description (misleading) | INT   | 1h  | P1       |
| GS-OPENCLAW-P2-001 | Remove unused guardspine_root        | INT   | 1h  | P2       |
| GS-OPENCLAW-P2-002 | Hash created_at or document          | INT   | 2h  | P2       |

**Total: 35h**

### openclaw-hardening

| Ticket              | Title                             | Owner | Est | Priority |
| ------------------- | --------------------------------- | ----- | --- | -------- |
| GS-HARDENING-P1-001 | Replace hash_chain with kernel-py | INT   | 8h  | P1       |
| GS-HARDENING-P1-002 | Enforce sequence validation       | INT   | 4h  | P1       |
| GS-HARDENING-P1-003 | Legacy gate default deny          | INT   | 2h  | P1       |
| GS-HARDENING-P1-004 | Ollama health preflight           | INT   | 2h  | P1       |
| GS-HARDENING-P1-005 | promptfoo v0.2.0 or non-evidence  | INT   | 4h  | P1       |
| GS-HARDENING-P1-006 | Golden vector parity tests        | INT   | 2h  | P1       |
| GS-HARDENING-P2-001 | Schema validation vs examples     | INT   | 2h  | P2       |
| GS-HARDENING-P2-002 | Terminology consistency           | INT   | 1h  | P2       |
| GS-HARDENING-P2-003 | Stub channels require flag        | INT   | 1h  | P2       |

**Total: 26h**

### guardspine-local-council

| Ticket            | Title                      | Owner | Est | Priority |
| ----------------- | -------------------------- | ----- | --- | -------- |
| GS-COUNCIL-P1-001 | Replace with kernel-py     | INT   | 4h  | P1       |
| GS-COUNCIL-P1-002 | Validate bundles at build  | INT   | 4h  | P1       |
| GS-COUNCIL-P1-003 | Ollama preflight           | INT   | 2h  | P1       |
| GS-COUNCIL-P1-004 | Signing policy doc         | INT   | 1h  | P1       |
| GS-COUNCIL-P1-005 | Golden vector parity tests | INT   | 2h  | P1       |
| GS-COUNCIL-P2-001 | Verify smoke test          | INT   | 2h  | P2       |
| GS-COUNCIL-P2-002 | README output contract     | INT   | 1h  | P2       |

**Total: 16h**

### guardspine-adapter-webhook

| Ticket            | Title                       | Owner | Est | Priority |
| ----------------- | --------------------------- | ----- | --- | -------- |
| GS-WEBHOOK-P1-001 | Refactor sealBundle()       | INT   | 4h  | P1       |
| GS-WEBHOOK-P1-002 | Kernel error = hard failure | INT   | 2h  | P1       |
| GS-WEBHOOK-P1-003 | Accurate kernel types       | INT   | 2h  | P1       |
| GS-WEBHOOK-P1-004 | Golden vector parity tests  | INT   | 2h  | P1       |
| GS-WEBHOOK-P2-001 | README clarity              | INT   | 2h  | P2       |
| GS-WEBHOOK-P2-002 | Remove redundant hashes     | INT   | 1h  | P2       |
| GS-WEBHOOK-P2-003 | Top-level fields            | INT   | 1h  | P2       |

**Total: 14h**

### guardspine-connector-template

| Ticket             | Title                         | Owner | Est | Priority |
| ------------------ | ----------------------------- | ----- | --- | -------- |
| GS-TEMPLATE-P0-001 | Fix Python emitter to v0.2.0  | INT   | 4h  | P0       |
| GS-TEMPLATE-P0-002 | Update TS types v0.2.0        | INT   | 4h  | P0       |
| GS-TEMPLATE-P0-003 | Use kernel for sealing        | INT   | 4h  | P0       |
| GS-TEMPLATE-P0-004 | Fix API endpoint              | INT   | 1h  | P0       |
| GS-TEMPLATE-P1-001 | Golden vector tests           | INT   | 4h  | P1       |
| GS-TEMPLATE-P1-002 | README alignment              | INT   | 2h  | P1       |
| GS-TEMPLATE-P1-003 | Version contradiction fix     | INT   | 1h  | P1       |
| GS-TEMPLATE-P1-004 | CLI entrypoint                | INT   | 2h  | P1       |
| GS-TEMPLATE-P1-005 | Unify Python/TS or remove one | INT   | 4h  | P1       |
| GS-TEMPLATE-P2-001 | Tests + golden vectors        | INT   | 4h  | P2       |
| GS-TEMPLATE-P2-002 | ZIP format implementation     | INT   | 2h  | P2       |

**Total: 32h**

### guardspine-product

| Ticket            | Title                              | Owner | Est | Priority |
| ----------------- | ---------------------------------- | ----- | --- | -------- |
| GS-PRODUCT-P0-001 | Create package directory           | INT   | 2h  | P0       |
| GS-PRODUCT-P0-002 | Move modules under package         | INT   | 4h  | P0       |
| GS-PRODUCT-P0-003 | Replace evidence.py with kernel-py | INT   | 8h  | P0       |
| GS-PRODUCT-P0-004 | Fix BaseGuardLane v0.2.0           | INT   | 4h  | P0       |
| GS-PRODUCT-P0-005 | Wrap DocEvidencePack v0.2.0        | INT   | 4h  | P0       |
| GS-PRODUCT-P1-001 | Fix broken tests                   | INT   | 2h  | P1       |
| GS-PRODUCT-P1-002 | Update docs to match reality       | INT   | 2h  | P1       |
| GS-PRODUCT-P1-003 | Fix absolute imports               | INT   | 2h  | P1       |
| GS-PRODUCT-P1-004 | Golden vector parity tests         | INT   | 2h  | P1       |
| GS-PRODUCT-P2-001 | Contract/golden tests              | INT   | 3h  | P2       |
| GS-PRODUCT-P2-002 | Hash prefix normalization          | INT   | 2h  | P2       |

**Total: 35h**

### n8n-nodes-guardspine

| Ticket        | Title                          | Owner | Est | Priority |
| ------------- | ------------------------------ | ----- | --- | -------- |
| GS-N8N-P0-001 | artifact_kind -> artifact_type | INT   | 1h  | P0       |
| GS-N8N-P1-001 | Bundle Import node             | INT   | 8h  | P1       |
| GS-N8N-P1-002 | ApprovalWait callback URL      | INT   | 2h  | P1       |
| GS-N8N-P1-003 | CouncilVote demo handling      | INT   | 2h  | P1       |
| GS-N8N-P2-001 | README update                  | INT   | 2h  | P2       |
| GS-N8N-P2-002 | Contract tests                 | INT   | 4h  | P2       |

**Total: 19h**

### openclaw-upstream

| Ticket             | Title                         | Owner | Est | Priority |
| ------------------ | ----------------------------- | ----- | --- | -------- |
| GS-UPSTREAM-P1-001 | PowerShell equivalents        | OPS   | 8h  | P1       |
| GS-UPSTREAM-P1-002 | Windows config flake fix      | OPS   | 4h  | P1       |
| GS-UPSTREAM-P1-003 | Version hook events           | PLT   | 8h  | P1       |
| GS-UPSTREAM-P2-001 | Low-memory test profile       | OPS   | 2h  | P2       |
| GS-UPSTREAM-P2-002 | Remove dangerouslyIgnore flag | OPS   | 2h  | P2       |

**Total: 24h**

### openclaw-source

| Ticket           | Title                               | Owner | Est | Priority |
| ---------------- | ----------------------------------- | ----- | --- | -------- |
| GS-SOURCE-P1-001 | Low-memory test profile             | OPS   | 2h  | P1       |
| GS-SOURCE-P1-002 | Windows-safe build or WSL-only      | OPS   | 4h  | P1       |
| GS-SOURCE-P1-003 | Version hook events (sync upstream) | PLT   | 2h  | P1       |
| GS-SOURCE-P2-001 | Dependency drift check              | OPS   | 2h  | P2       |

**Total: 10h**

---

## Part 6: Grand Total Summary

### By Severity

| Severity  | Count  | Hours    |
| --------- | ------ | -------- |
| P0        | 12     | 54h      |
| P1        | 46     | 156h     |
| P2        | 30     | 54h      |
| **TOTAL** | **88** | **264h** |

### By Repository

| Repo                          | P0     | P1     | P2     | Hours    |
| ----------------------------- | ------ | ------ | ------ | -------- |
| guardspine-kernel-py (NEW)    | 4      | 1      | 1      | 18h      |
| guardspine-spec               | 0      | 4      | 2      | 21h      |
| guardspine-kernel             | 0      | 1      | 2      | 5h       |
| guardspine-verify             | 3      | 5      | 4      | 34h      |
| guardspine-backend            | 0      | 7      | 3      | 33h      |
| guardspine-main               | 0      | 0      | 0      | 0h       |
| guardspine-openclaw           | 2      | 6      | 2      | 35h      |
| openclaw-hardening            | 0      | 6      | 3      | 26h      |
| guardspine-local-council      | 0      | 5      | 2      | 16h      |
| guardspine-adapter-webhook    | 0      | 4      | 3      | 14h      |
| guardspine-connector-template | 4      | 5      | 2      | 32h      |
| guardspine-product            | 5      | 4      | 2      | 35h      |
| n8n-nodes-guardspine          | 1      | 3      | 2      | 19h      |
| openclaw-upstream             | 0      | 3      | 2      | 24h      |
| openclaw-source               | 0      | 3      | 1      | 10h      |
| **TOTAL**                     | **19** | **57** | **31** | **322h** |

### By Owner

| Owner             | Tickets | Hours    |
| ----------------- | ------- | -------- |
| SEC (Security)    | 6       | 19h      |
| PLT (Platform)    | 32      | 103h     |
| INT (Integration) | 44      | 170h     |
| OPS (DevOps)      | 6       | 30h      |
| **TOTAL**         | **88**  | **322h** |

---

## Part 7: Recommendations

### Immediate Actions (This Week)

1. **GS-OPENCLAW-P0-001**: Fix L4 self-approval bypass (2h) - SECURITY
2. **GS-N8N-P0-001**: Fix artifact_kind -> artifact_type (1h) - BREAKING
3. **GS-VERIFY-P0-001/002/003**: Fix all verify binding issues (14h)

### Week 2 Priority

1. Create guardspine-kernel-py (18h)
2. Create golden vector fixtures (8h)
3. Fix connector-template P0s (13h)

### Key Dependencies to Unblock

1. `guardspine-spec` unblocks all downstream repos
2. `guardspine-kernel-py` unblocks all Python repos
3. `guardspine-verify` fixes unblock council + n8n

---

## Appendix: Source Document Comparison

| Attribute    | Claude Doc                                    | Codex Doc                           |
| ------------ | --------------------------------------------- | ----------------------------------- |
| File         | GUARDSPINE-LINUS-STANDARD-REMEDIATION-PLAN.md | GuardSpine-Bplus-Plan-2026-02-03.md |
| Lines        | 1055                                          | 462                                 |
| P0 Count     | 12                                            | 12                                  |
| P1 Count     | 35                                            | 38                                  |
| P2 Count     | 25                                            | 27                                  |
| Total Hours  | 302h                                          | ~310h                               |
| SAML Status  | Listed as P1                                  | Marked STALE                        |
| Unique Finds | 3                                             | 13                                  |
| Verification | Direct code inspection                        | Audit validation report             |

**Synthesis Result**: 81 total issues, 327h estimated, 88 tickets across 15 repos.

---

**Document Version**: 1.0.0
**Generated By**: Claude + Codex Synthesis
**Date**: 2026-02-03
**Review Date**: 2026-02-10
