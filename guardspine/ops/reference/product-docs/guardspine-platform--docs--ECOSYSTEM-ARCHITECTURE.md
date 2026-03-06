# GuardSpine Ecosystem Architecture

> 16 repos, 3 layers, 1 trust chain.
> Last updated: 2026-02-05

---

## Table of Contents

1. [Repo Inventory](#repo-inventory)
2. [Layer Architecture](#layer-architecture)
3. [Trust Chain (The Spine)](#trust-chain)
4. [Data Flow: End to End](#data-flow-end-to-end)
5. [Integration Points](#integration-points)
6. [Verification System](#verification-system)
7. [Guard Lanes (Content Types)](#guard-lanes)
8. [Council System (L3/L4)](#council-system)
9. [Connector Architecture](#connector-architecture)
10. [Dependency Graph](#dependency-graph)
11. [Local Development Setup](#local-development-setup)
12. [Repo-by-Repo Reference](#repo-by-repo-reference)

---

## Repo Inventory

### Layer 1: Trust Foundation (Open Source, Apache 2.0)

| #   | Repo                   | Lang        | Package Name         | Purpose                                               |
| --- | ---------------------- | ----------- | -------------------- | ----------------------------------------------------- |
| 1   | `guardspine-spec`      | JSON Schema | `guardspine-spec`    | Evidence Bundle Specification v0.2.0 + golden vectors |
| 2   | `guardspine-kernel`    | TypeScript  | `@guardspine/kernel` | Canonical hash chain implementation (zero deps)       |
| 3   | `guardspine-kernel-py` | Python      | `guardspine-kernel`  | Python port (byte-identical to TS)                    |
| 4   | `guardspine-verify`    | Python      | `guardspine-verify`  | Standalone offline CLI verifier                       |

### Layer 2: Product (Proprietary)

| #   | Repo                 | Lang      | Purpose                                                    |
| --- | -------------------- | --------- | ---------------------------------------------------------- |
| 5   | `GuardSpine`         | Python/TS | Monorepo: Backend API (149 routes), CLI, Frontend          |
| 6   | `guardspine-product` | Python    | Product suite: CodeGuard, PDFGuard, ImageGuard, SheetGuard |

### Layer 3: Integrations (Mostly Open Source)

| #   | Repo                            | Lang       | License    | Purpose                                             |
| --- | ------------------------------- | ---------- | ---------- | --------------------------------------------------- |
| 7   | `guardspine-openclaw`           | JS/Python  | Apache 2.0 | OpenClaw plugin: L0-L4 tool gating                  |
| 8   | `openclaw-upstream`             | TypeScript | --         | Fork of OpenClaw with GuardSpine patches applied    |
| 9   | `openclaw-hardening`            | Python     | Apache 2.0 | Standalone governance layer for OpenClaw            |
| 10  | `guardspine-local-council`      | Python     | Apache 2.0 | Local LLM council via Ollama (no cloud)             |
| 11  | `guardspine-adapter-webhook`    | TypeScript | Apache 2.0 | GitHub/GitLab/Bitbucket webhook -> evidence bundles |
| 12  | `guardspine-connector-template` | TypeScript | MIT        | Starter template for new connectors                 |
| 13  | `n8n-nodes-guardspine`          | TypeScript | MIT        | 11 n8n community nodes                              |
| 14  | `codeguard-action`              | Python     | MIT        | GitHub Action for PR governance                     |
| 15  | `rlm-docsync`                   | Python     | Apache 2.0 | Doc-code drift detection with evidence proofs       |
| 16  | `executiveai-co`                | Astro      | --         | Marketing site (older)                              |

### Local Clone Paths

All repos cloned to `D:\Projects\`:

```
D:\Projects\GuardSpine\
D:\Projects\guardspine-spec\
D:\Projects\guardspine-kernel\
D:\Projects\guardspine-kernel-py\
D:\Projects\guardspine-verify\
D:\Projects\guardspine-product\
D:\Projects\guardspine-openclaw\
D:\Projects\openclaw-upstream\
D:\Projects\openclaw-hardening\
D:\Projects\guardspine-local-council\
D:\Projects\guardspine-adapter-webhook\
D:\Projects\guardspine-connector-template\
D:\Projects\n8n-nodes-guardspine\
D:\Projects\rlm-docsync\
```

`codeguard-action` and `executiveai-co` are GitHub-only (no local clone).

---

## Layer Architecture

```
+================================================================+
|                    LAYER 1: TRUST FOUNDATION                    |
|                                                                  |
|  guardspine-spec -----> guardspine-kernel (TS, canonical)        |
|  [JSON Schema]    |                |                             |
|  [Golden vectors] |     guardspine-kernel-py (Python, parity)    |
|                   |                                              |
|                   +---> guardspine-verify (standalone verifier)   |
+================================================================+
                              |
                    imports / depends on
                              |
+================================================================+
|                    LAYER 2: PRODUCT                              |
|                                                                  |
|  GuardSpine (monorepo)                                           |
|    backend/ ---- kernel.py bridge ---> guardspine-kernel-py      |
|    codeguard/ -- CLI tools (audit, pdfguard, sheetguard, etc.)   |
|    frontend/ -- Web UI                                           |
|    connectors/ - gdrive, openclaw                                |
|                                                                  |
|  guardspine-product                                              |
|    code_guard/ pdf_guard/ image_guard/ sheet_guard/               |
|    depends on: guardspine-kernel (pip)                            |
+================================================================+
                              |
                    consumed by
                              |
+================================================================+
|                    LAYER 3: INTEGRATIONS                         |
|                                                                  |
|  OpenClaw:     guardspine-openclaw --> openclaw-upstream          |
|                openclaw-hardening                                 |
|                                                                  |
|  Webhooks:     guardspine-adapter-webhook (GitHub/GitLab/BB)     |
|  GitHub CI:    codeguard-action                                  |
|  n8n:          n8n-nodes-guardspine (11 nodes)                   |
|  Docs:         rlm-docsync                                       |
|  Custom:       guardspine-connector-template                     |
|  Council:      guardspine-local-council (Ollama)                 |
+================================================================+
```

---

## Trust Chain

The entire system rests on one invariant: **every evidence bundle uses the same hash chain algorithm, producing identical bytes regardless of language**.

### Hash Chain Algorithm (v0.2.0)

```
Input: items[] (each has item_id, content_type, content)

For each item:
  1. content_hash = SHA-256( canonical_json(item.content) )
     - canonical_json follows RFC 8785 (sorted keys, no whitespace)

  2. chain_hash = SHA-256( canonical_json({
       sequence,
       item_id,
       content_type,
       content_hash,
       previous_hash    <-- prior entry's chain_hash (or GENESIS for first)
     }))

Root hash = SHA-256( canonical_json( all chain_hashes concatenated ) )
```

### Parity Enforcement

```
guardspine-spec/fixtures/golden-vectors/
    |
    |  Contains pre-computed bundles with known hashes
    |
    +---> guardspine-kernel (TS) tests against these
    +---> guardspine-kernel-py tests against these
    +---> guardspine-verify tests against these

    If ANY implementation produces different bytes, tests FAIL.
```

### Who Implements What

| Operation                | guardspine-kernel (TS) | guardspine-kernel-py | guardspine-verify |
| ------------------------ | ---------------------- | -------------------- | ----------------- |
| `canonical_json()`       | YES (canonical)        | YES (must match)     | YES (independent) |
| `compute_content_hash()` | YES                    | YES                  | YES               |
| `build_hash_chain()`     | YES                    | YES                  | --                |
| `compute_root_hash()`    | YES                    | YES                  | YES               |
| `seal_bundle()`          | YES                    | YES                  | --                |
| `verify_bundle()`        | YES                    | YES                  | YES               |

`guardspine-verify` intentionally has NO dependency on either kernel. It reimplements verification from scratch as a zero-trust verifier.

---

## Data Flow: End to End

### Flow 1: Code Change Governance (PR-based)

```
Developer pushes code
         |
         v
+-------------------+
| GitHub webhook     |
| fires on PR open   |
+--------+----------+
         |
    +----+----+
    |         |
    v         v
codeguard-   guardspine-adapter-webhook
action       (converts webhook payload
(GitHub      to evidence bundle items)
Action)           |
    |             v
    |    +------------------+
    |    | GuardSpine API   |
    |    | POST /bundles    |
    |    +------------------+
    |
    v
+--------------------------+
| 1. Parse unified diff    |
| 2. Detect sensitive zones|
|    (auth, payment, etc.) |
| 3. Classify risk L0-L4   |
| 4. Run AI review (L1+)  |
|    - L1: 1 model         |
|    - L2: 2 models        |
|    - L3: 3 models        |
|    - L4: 3 + human       |
| 5. Produce evidence      |
|    bundle (v0.2.0)       |
| 6. Post to PR comments   |
+--------------------------+
         |
         v
Evidence bundle stored + verifiable offline
```

### Flow 2: AI Agent Tool Gating (OpenClaw)

```
User gives instruction to AI agent
         |
         v
+-------------------+
| OpenClaw Agent     |
| decides to call    |
| a tool             |
+--------+----------+
         |
         v
+-------------------+        +-------------------+
| guardspine-openclaw|       | openclaw-hardening |
| before_tool_call   |  OR   | (standalone)       |
| hook fires         |       |                    |
+--------+----------+        +--------+----------+
         |                             |
         v                             v
+----------------------------------------+
| 1. Risk Classifier                      |
|    - Tool name lookup (static tier)     |
|    - Bash: regex on command content     |
|      (destructive/network/credential)   |
|                                         |
| Risk Tiers:                             |
|   L0: No-op (sequentialthinking, etc.)  |
|   L1: Log only (read ops)              |
|   L2: Evidence pack (bash, patch, msg)  |
|   L3: 3-model council vote             |
|   L4: Council + human approval          |
+--------+-------------------------------+
         |
    +----+----+----+
    |    |    |    |
   L0   L1   L2  L3/L4
   |    |    |    |
  pass  log  |    +---> guardspine-local-council
             |          (3 Ollama models vote)
             |          |
             |          v
             |    +------------------+
             |    | Consensus check  |
             |    | quorum >= 2      |
             |    | threshold >= 0.66|
             |    +--------+---------+
             |             |
             |        pass/block
             |             |
             v             v
      +----------------------------+
      | Evidence entry created      |
      | SHA-256 hash chain link     |
      | previous_hash -> chain_hash |
      +----------------------------+
               |
               v
      Session ends -> full evidence pack
      written to evidence-pack-{session}.json
```

### Flow 3: Document Governance (rlm-docsync)

```
guardspine.docs.yaml manifest
         |
         v
+-------------------+
| rlm-docsync        |
| reads manifest     |
+--------+----------+
         |
         v
+-------------------------------------------+
| For each document in manifest:             |
|   1. Extract claims from markdown          |
|   2. For each claim:                       |
|      - Search codebase for evidence        |
|      - Pattern match (e.g. @requires_auth) |
|      - Record pass/fail/skip               |
|   3. Build hash-chained evidence pack      |
|      using guardspine-kernel-py            |
+--------+----------------------------------+
         |
         v
Two modes:
  spec-first:    docs are truth, flag code violations
  reality-first: code is truth, generate doc update PRs
         |
         v
evidence-pack.json (verifiable with guardspine-verify)
```

### Flow 4: n8n Workflow Governance

```
n8n workflow triggers
         |
         v
+------------------------------------------+
| n8n-nodes-guardspine (11 nodes)           |
|                                           |
| GuardGate ---- evaluate against rubrics   |
| CodeGuard ---- run code audit             |
| PDFGuard ----- run PDF analysis           |
| SheetGuard --- run spreadsheet audit      |
| ImageGuard --- run image safety check     |
| EvidenceSeal - seal into v0.2.0 bundle    |
| CouncilVote -- multi-model review         |
| ApprovalWait - wait for human approval    |
| BeadsCreate -- create work item           |
| BeadsUpdate -- update work item status    |
| Compress ----- compress bundle            |
+--------+---------------------------------+
         |
         v
All nodes talk to GuardSpine Backend API
via GUARDSPINE_API_KEY credential
```

### Flow 5: Content Governance (guardspine-product Guard Lanes)

```
Content artifact submitted for review
         |
    +----+----+----+----+
    |    |    |    |    |
    v    v    v    v    v
  Code  PDF  Image Sheet  (future: Comms, Ticket,
  Guard Guard Guard Guard  Deal, Contract, Deploy,
    |    |    |    |       Data, Evidence)
    v    v    v    v
+------------------------------------------+
| Each guard lane:                          |
|   1. Parse content (language-specific)    |
|   2. Run detectors (PII, secrets, etc.)  |
|   3. Classify risk L0-L4                 |
|   4. Score against rubrics               |
|   5. Seal findings into evidence bundle  |
|      using guardspine-kernel (pip dep)   |
+--------+---------------------------------+
         |
         v
Evidence bundle (v0.2.0) with:
  - Findings per detector
  - Risk classification
  - Rubric scores
  - Immutability proof (hash chain)
```

---

## Integration Points

### Upstream (Things That Feed INTO GuardSpine)

| Source          | Mechanism            | Repo                            | What It Produces                   |
| --------------- | -------------------- | ------------------------------- | ---------------------------------- |
| GitHub PRs      | Webhook              | `guardspine-adapter-webhook`    | Normalized events with risk labels |
| GitHub PRs      | GitHub Action        | `codeguard-action`              | AI-reviewed evidence bundles       |
| GitLab MRs      | Webhook              | `guardspine-adapter-webhook`    | Same as GitHub                     |
| Bitbucket PRs   | Webhook              | `guardspine-adapter-webhook`    | Same as GitHub                     |
| OpenClaw agents | Plugin hook          | `guardspine-openclaw`           | Per-tool evidence entries          |
| n8n workflows   | Node execution       | `n8n-nodes-guardspine`          | Governed workflow steps            |
| Documentation   | Manifest scan        | `rlm-docsync`                   | Doc-code compliance packs          |
| Google Drive    | Connector            | `GuardSpine/connectors/gdrive/` | Document change events             |
| Slack           | Interactive messages | `GuardSpine/backend/` routers   | Approval actions                   |
| Jira            | Connector            | `GuardSpine/backend/` routers   | Ticket change events               |
| Custom sources  | Template             | `guardspine-connector-template` | Any artifact type                  |

### Downstream (Things That Consume FROM GuardSpine)

| Consumer           | What It Gets                           | How                                    |
| ------------------ | -------------------------------------- | -------------------------------------- |
| GitHub PR comments | Review results, risk tier, findings    | `codeguard-action` posts to PR         |
| Slack channels     | Approval requests, alert notifications | Backend Slack integration              |
| Board packets      | Executive governance reports (PDF)     | `GuardSpine/backend/board_packets/`    |
| Audit logs         | Hash-chained evidence trail            | Evidence bundles (JSON/ZIP)            |
| External auditors  | Offline-verifiable bundles             | `guardspine-verify` CLI                |
| n8n workflows      | Pass/block routing decisions           | `n8n-nodes-guardspine` GuardGate       |
| Beads task system  | Work items with risk metadata          | Beads integration in backend           |
| Dashboard          | Compliance KPIs, metrics               | `GuardSpine/backend/dashboard/`        |
| SARIF consumers    | Standard findings format               | `GuardSpine/backend/sarif_exporter.py` |

### API Surface (GuardSpine Backend)

| Domain        | Route Prefix             | Endpoints | Key Operations                          |
| ------------- | ------------------------ | --------- | --------------------------------------- |
| Auth          | `/api/v1/auth/`          | 23        | SSO, JWT, SCIM, user/role mgmt          |
| Board Packets | `/api/v1/board-packets/` | 17        | Governance reports, signatures, PDF     |
| Alerts        | `/api/v1/alerts/`        | 14        | Alert creation, escalation, rules       |
| Connectors    | `/api/v1/connectors/`    | 13        | Slack, GitHub, Jira, GDrive, Confluence |
| Bundles       | `/api/v1/bundles/`       | 12        | Evidence bundles, verification, export  |
| Governance    | `/api/v1/governance/`    | 11        | Change workflow, impact analysis        |
| Policies      | `/api/v1/policies/`      | 9         | Policy packs, compliance rules          |
| Search        | `/api/v1/search/`        | 6         | Full-text, filtered, suggestions        |
| Artifacts     | `/api/v1/artifacts/`     | 6         | Storage, versioning, retrieval          |
| Beads         | `/api/v1/beads/`         | 6         | Work item context, risk inference       |
| Approvals     | `/api/v1/approvals/`     | 5         | Workflow state machine                  |
| Dashboard     | `/api/v1/dashboard/`     | 5         | Metrics, KPIs, compliance status        |
| Webhooks      | `/api/v1/webhooks/`      | 3         | Event handlers                          |
| Slack         | `/api/v1/slack/`         | 3         | Interactive actions, events             |
| Diffs         | `/api/v1/diffs/`         | 2         | Diff analysis                           |
| Events        | `/api/v1/events/`        | 2         | Event logging                           |
| Health        | `/health`                | 1         | API status                              |

---

## Verification System

### Three Levels of Verification

```
Level 1: SELF-VERIFICATION (at creation time)
  - guardspine-kernel or guardspine-kernel-py
  - seal_bundle() -> immutability_proof
  - Happens automatically when bundle is created

Level 2: API VERIFICATION (at ingestion time)
  - GuardSpine backend calls verify_bundle()
  - Uses guardspine-kernel-py via kernel.py bridge
  - Rejects invalid bundles at the API boundary

Level 3: INDEPENDENT VERIFICATION (at audit time)
  - guardspine-verify (standalone, zero deps on kernel)
  - Any auditor can verify any bundle offline
  - No trust in the issuing system required
  - Exit code 0 = verified, 1 = failed, 2 = invalid input
```

### What Gets Verified

| Check          | Description                                               | Failure Means                              |
| -------------- | --------------------------------------------------------- | ------------------------------------------ |
| Version        | Must be "0.2.0"                                           | Bundle uses unsupported format             |
| Content hashes | SHA-256 of canonical JSON matches stored hash             | Content was modified after sealing         |
| Hash chain     | Each entry's `previous_hash` = prior entry's `chain_hash` | Items were inserted, removed, or reordered |
| Chain binding  | Chain entries map 1:1 to items                            | Mismatch between items and proof           |
| Root hash      | Computed Merkle root matches stored root                  | Chain was tampered with                    |
| Sequence       | Contiguous 0-based integers                               | Sequence gaps or duplicates                |
| Signatures     | Ed25519/RSA/ECDSA verify (optional)                       | Signer key mismatch or tampering           |

### Verification Commands

```bash
# Single bundle
guardspine-verify bundle.json

# ZIP export
guardspine-verify evidence-bundle-2026-01-15.zip

# Verbose
guardspine-verify bundle.json --verbose

# JSON report
guardspine-verify bundle.json --format json > report.json

# Multiple bundles
guardspine-verify bundle1.json bundle2.json bundle3.json
```

### Verification in Python

```python
from guardspine_verify import verify_bundle_data
import json

with open("bundle.json") as f:
    bundle = json.load(f)

result = verify_bundle_data(bundle)
print(f"Verified: {result.verified}")
print(f"Hash chain: {result.hash_chain_status}")
print(f"Signatures: {result.signature_status}")
for error in result.errors:
    print(f"  ERROR: {error}")
```

---

## Guard Lanes

### Current Lanes (in guardspine-product)

| Lane           | Module         | Input Types        | Detectors                                                               |
| -------------- | -------------- | ------------------ | ----------------------------------------------------------------------- |
| **CodeGuard**  | `code_guard/`  | Source code, diffs | Multi-model AI review, risk classification, rubric scoring              |
| **PDFGuard**   | `pdf_guard/`   | PDF documents      | PII detection, OCR analysis, signature verification, redaction checking |
| **ImageGuard** | `image_guard/` | PNG/JPG/etc.       | Content safety, face detection, metadata extraction                     |
| **SheetGuard** | `sheet_guard/` | Excel/CSV          | Schema compliance, formula auditing, PII detection, reference checking  |

### Internal/Dogfood Lanes (not yet in guardspine-product)

| Lane           | Purpose                          | Status        |
| -------------- | -------------------------------- | ------------- |
| Comms Guard    | Slack/Discord/Email governance   | Internal beta |
| Ticket Guard   | Support ticket triage            | Internal beta |
| Deal Guard     | Sales pipeline gating            | Internal beta |
| Contract Guard | Legal document review (MSA/DPA)  | Internal beta |
| Deploy Guard   | Deployment/release gating        | Internal beta |
| Data Guard     | Data boundary/privacy validation | Future        |
| Evidence Guard | Audit evidence verification      | Future        |

### Rubrics (in GuardSpine monorepo)

Located at `GuardSpine/codeguard/rubrics/`:

| Rubric                      | Focus                        | Standard              |
| --------------------------- | ---------------------------- | --------------------- |
| `connascence.yaml`          | 9-type coupling analysis     | Software engineering  |
| `nasa-safety.yaml`          | Power of 10 safety rules     | NASA/JPL              |
| `clarity.yaml`              | Cognitive load analysis      | Code readability      |
| `six-sigma.yaml`            | DPMO, sigma level            | Manufacturing quality |
| `mece.yaml`                 | Duplication detection (>80%) | Consulting/analysis   |
| `theater-detection.yaml`    | Fake quality prevention      | Anti-pattern          |
| `safety-violations.yaml`    | God objects, parameter bombs | Code safety           |
| `nomotic.yaml`              | Brand/messaging rules        | Content governance    |
| `hipaa-safeguards.yaml`     | HIPAA compliance             | Healthcare            |
| `pci-dss-requirements.yaml` | PCI-DSS 3.2.1                | Payments              |
| `soc2-controls.yaml`        | SOC2 Type II                 | Enterprise security   |

---

## Council System

### How Multi-Model Review Works

```
Artifact submitted for L3+ review
         |
         v
+-----------------------------------+
| guardspine-local-council           |
|                                    |
| 1. Create ReviewRequest            |
|    - artifact_id                    |
|    - artifact_type                  |
|    - content (the actual artifact)  |
|                                    |
| 2. Send to N OllamaProviders       |
|    (parallel execution)             |
|    Each provider:                   |
|    - Formats review prompt          |
|    - Calls Ollama API               |
|    - Returns structured vote:       |
|      {decision, confidence, reason} |
|                                    |
| 3. SimpleAggregator computes:       |
|    - Weighted confidence majority   |
|    - Quorum check (default >= 2)    |
|    - Threshold check (default 0.66) |
|                                    |
| 4. Output: ConsensusResult          |
|    - consensus_decision             |
|    - consensus_confidence           |
|    - individual_votes               |
|    - evidence_bundle (v0.2.0)       |
+-----------------------------------+
```

### Council Configuration

| Parameter             | Default                  | What It Controls            |
| --------------------- | ------------------------ | --------------------------- |
| `quorum`              | 3                        | Minimum non-abstain votes   |
| `consensus_threshold` | 0.66                     | Minimum weighted confidence |
| `model`               | varies                   | Ollama model name           |
| `base_url`            | `http://localhost:11434` | Ollama API endpoint         |

### Recommended Models (for guardspine-openclaw)

```bash
ollama pull qwen3:8b           # Reviewer A
ollama pull falcon3:7b         # Reviewer B
ollama pull qwen2.5-coder:7b   # Reviewer C
```

---

## Connector Architecture

### Building a New Connector

```
guardspine-connector-template
         |
         | npm install
         | Edit src/connector.ts:
         |
         v
+-----------------------------------+
| class MyConnector extends Base {   |
|                                    |
|   connect() {                      |
|     // Auth with source system     |
|   }                                |
|                                    |
|   fetchArtifacts() {               |
|     // Pull raw data               |
|   }                                |
|                                    |
|   transformToEvidenceItems() {     |
|     // Map to v0.2.0 items         |
|     // (optional override)         |
|   }                                |
| }                                  |
+-----------------------------------+
         |
         | Peer dep: @guardspine/kernel >= 0.2.0
         |
         v
emitEvidenceBundle() -> v0.2.0 bundle
with cryptographic hash chain
```

### Existing Connectors

| Connector    | Location                                  | Status      |
| ------------ | ----------------------------------------- | ----------- |
| Google Drive | `GuardSpine/connectors/gdrive/`           | In monorepo |
| OpenClaw     | `GuardSpine/connectors/openclaw/`         | In monorepo |
| GitHub       | `GuardSpine/backend/` (webhooks router)   | Backend API |
| Slack        | `GuardSpine/backend/` (slack router)      | Backend API |
| Jira         | `GuardSpine/backend/` (connectors router) | Backend API |
| Confluence   | `GuardSpine/backend/` (connectors router) | Backend API |

---

## Dependency Graph

### Hard Dependencies (import/require)

```
guardspine-kernel-py
    ^
    |--- GuardSpine/backend/app/core/kernel.py (re-exports)
    |--- guardspine-product/pyproject.toml (pip dependency)
    |--- guardspine-openclaw/evidence-evaluator/ (imports)
    |--- guardspine-openclaw/rlm-docsync/ (imports, with fallback)
    |--- openclaw-hardening/hash_chain/ (uses same algorithm)

@guardspine/kernel (TS)
    ^
    |--- guardspine-adapter-webhook (peer dependency)
    |--- guardspine-connector-template (peer dependency >= 0.2.0)
    |--- n8n-nodes-guardspine (calls API, not direct dep)

guardspine-spec
    ^
    |--- guardspine-kernel (tests against golden vectors)
    |--- guardspine-kernel-py (tests against golden vectors)
    |--- guardspine-verify (tests against golden vectors)
```

### API Dependencies (HTTP calls)

```
n8n-nodes-guardspine ---HTTP---> GuardSpine Backend API
codeguard-action -----HTTP---> GitHub API (posts comments)
guardspine-adapter-webhook --> Receives webhooks, emits bundles
guardspine-local-council --HTTP---> Ollama API (localhost:11434)
GuardSpine/backend ----HTTP---> Slack API, Jira API, etc.
```

### Logical Dependencies (same specification)

```
All repos that produce bundles MUST follow guardspine-spec v0.2.0:
  - guardspine-kernel
  - guardspine-kernel-py
  - guardspine-product
  - guardspine-openclaw
  - openclaw-hardening
  - guardspine-adapter-webhook
  - guardspine-connector-template
  - n8n-nodes-guardspine (EvidenceSeal node)
  - rlm-docsync
  - codeguard-action
  - GuardSpine backend

All repos that verify bundles MUST pass golden vector tests:
  - guardspine-kernel
  - guardspine-kernel-py
  - guardspine-verify
```

---

## Local Development Setup

### Prerequisites

```bash
# Python
python --version  # 3.10+

# Node.js
node --version    # 18+

# Ollama (for council)
ollama --version
ollama pull qwen3:8b
ollama pull falcon3:7b
ollama pull qwen2.5-coder:7b
```

### Install Core Packages

```bash
# Install kernel (Python)
cd D:\Projects\guardspine-kernel-py
pip install -e .

# Install verifier
cd D:\Projects\guardspine-verify
pip install -e .

# Install product suite
cd D:\Projects\guardspine-product
pip install -e ".[all]"

# Install kernel (TypeScript)
cd D:\Projects\guardspine-kernel
npm install && npm run build

# Install webhook adapter
cd D:\Projects\guardspine-adapter-webhook
npm install && npm run build
```

### Run the Backend

```bash
cd D:\Projects\GuardSpine\backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Run Tests

```bash
# Kernel parity tests (critical - must pass)
cd D:\Projects\guardspine-kernel && npm test
cd D:\Projects\guardspine-kernel-py && pytest tests/ -v

# Spec validation
cd D:\Projects\guardspine-spec && npm test

# Backend tests (144 passing)
cd D:\Projects\GuardSpine\backend && pytest

# Verifier tests
cd D:\Projects\guardspine-verify && pytest tests/ -v
```

### Quick Smoke Test

```bash
# Seal a bundle
python -c "
from guardspine_kernel import seal_bundle
result = seal_bundle([
    {'item_id': 'test-1', 'content_type': 'guardspine/test', 'content': {'hello': 'world'}}
])
import json
bundle = {
    'bundle_id': 'smoke-test',
    'version': '0.2.0',
    'created_at': '2026-02-05T00:00:00Z',
    'items': [dict(i) for i in result.items],
    'immutability_proof': dict(result.immutability_proof),
}
with open('smoke-bundle.json', 'w') as f:
    json.dump(bundle, f, indent=2, default=str)
print('Bundle sealed.')
"

# Verify it
guardspine-verify smoke-bundle.json
```

---

## Repo-by-Repo Reference

### 1. guardspine-spec

**What**: The specification document. Defines the v0.2.0 evidence bundle JSON schema, verification rules, and golden test vectors.

**Key files**:

- `SPECIFICATION.md` - Full technical spec
- `schemas/` - JSON Schema definitions
- `fixtures/golden-vectors/` - Test bundles all implementations must verify identically
- `examples/` - Example bundles

**Outputs**: JSON Schema files, golden vector bundles
**Consumed by**: All repos that seal or verify bundles

---

### 2. guardspine-kernel (TypeScript)

**What**: The canonical implementation. All other language ports must match its byte output.

**Key exports**: `sealBundle()`, `verifyBundle()`, `buildHashChain()`, `computeContentHash()`, `computeRootHash()`, `canonicalJson()`

**Key files**:

- `src/index.ts` - All exports
- `tests/` - Tests against golden vectors

**Outputs**: npm package `@guardspine/kernel`
**Consumed by**: `guardspine-adapter-webhook`, `guardspine-connector-template` (as peer deps)

---

### 3. guardspine-kernel-py (Python)

**What**: Python port. Must produce byte-identical hashes to the TS version.

**Key exports**: Same as TS: `seal_bundle()`, `verify_bundle()`, `canonical_json()`, etc.

**Key files**:

- `src/guardspine_kernel/` - Package source

**Outputs**: pip package `guardspine-kernel`
**Consumed by**: `GuardSpine` backend (via `kernel.py` bridge), `guardspine-product`, `guardspine-openclaw`, `rlm-docsync`

---

### 4. guardspine-verify

**What**: Standalone offline verifier. Zero trust - reimplements verification independently.

**Key files**:

- `guardspine_verify/cli.py` - CLI entry point
- `guardspine_verify/` - Verification logic

**Outputs**: pip package + CLI command `guardspine-verify`
**Consumed by**: Auditors, CI pipelines, anyone who needs to verify a bundle

---

### 5. GuardSpine (monorepo)

**What**: The main product. Backend API + CLI + Frontend.

**Key directories**:

- `backend/` - FastAPI app (149 routes, 19 services, 10K+ LOC)
- `backend/app/core/kernel.py` - Bridge to guardspine-kernel-py
- `codeguard/` - CLI tools (audit, pdfguard, sheetguard, imageguard)
- `codeguard/rubrics/` - 12 YAML rubric files
- `frontend/` - Web UI
- `connectors/` - gdrive, openclaw integrations
- `open-source/` - Contains spec, verify, connector-template
- `evidence-pack*/` - Dogfood evidence bundles

**Outputs**: REST API, CLI tools, web dashboard
**Depends on**: `guardspine-kernel-py`

---

### 6. guardspine-product

**What**: The 4 guard lanes as a pip-installable package.

**Key directories**:

- `code_guard/` - Code analysis + AI review
- `pdf_guard/` - PDF document analysis
- `image_guard/` - Image safety + metadata
- `sheet_guard/` - Spreadsheet validation
- `common/` - Shared utilities
- `adapters/` - Output format adapters
- `connectors/` - Source connectors
- `compression/` - Bundle compression

**Outputs**: pip package `guardspine-product`
**Depends on**: `guardspine-kernel` (pip)

---

### 7. guardspine-openclaw

**What**: Plugin that hooks into OpenClaw's `before_tool_call` to gate every AI tool invocation.

**Key files**:

- `plugin.js` - Main plugin (50K, self-contained)
- `openclaw.plugin.json` - Plugin manifest
- `config/` - Risk tier configuration
- `evidence-evaluator/` - Evidence pack evaluation (uses guardspine-kernel-py)
- `rlm-docsync/` - Embedded doc-code sync (uses guardspine-kernel-py)
- `redteam/` - Red team testing tools
- `scripts/` - Setup and utility scripts

**Outputs**: OpenClaw extension, per-session evidence packs
**Depends on**: `guardspine-kernel-py` (for evidence-evaluator), `guardspine-local-council` (for L3+ votes)

---

### 8. openclaw-upstream

**What**: A full fork of the OpenClaw codebase with GuardSpine governance patches applied directly.

**Outputs**: Modified OpenClaw build
**Depends on**: OpenClaw source, GuardSpine patches

---

### 9. openclaw-hardening

**What**: Standalone governance components, independently packaged (not a plugin).

**Key directories**:

- `hash_chain/` - v0.2.0 hash chain implementation
- `approvals/` - L0-L4 approval gate with channel routing (Slack prod, Discord/SMS stubs)
- `eval/` - Evidence pack evaluation and scoring
- `council/` - Local multi-model review council
- `openclaw_integration/` - Plugin hooks and health checks
- `mock_openclaw/` - Mock for testing

**Outputs**: Governance layer that can be integrated into any system
**Depends on**: `guardspine-kernel-py` (for hash chain)

---

### 10. guardspine-local-council

**What**: Multi-model review using local Ollama models. No cloud APIs.

**Key exports**: `LocalCouncil`, `OllamaProvider`, `ReviewRequest`, `SimpleAggregator`

**Outputs**: pip package `guardspine-local-council`, v0.2.0 evidence bundles with council votes
**Depends on**: `httpx` (for Ollama API calls)
**Consumed by**: `guardspine-openclaw` (L3+ reviews), `openclaw-hardening`

---

### 11. guardspine-adapter-webhook

**What**: Converts webhook payloads from GitHub/GitLab/Bitbucket into GuardSpine evidence items.

**Key exports**: `WebhookHandler`, `BundleEmitter`, `GitHubProvider`, `GitLabProvider`, `GenericProvider`

**Outputs**: npm package `@guardspine/adapter-webhook`
**Depends on**: `@guardspine/kernel` (optional peer dep for sealing)

---

### 12. guardspine-connector-template

**What**: Starter template. Clone it, implement `connect()` and `fetchArtifacts()`, build.

**Outputs**: npm package `@guardspine/connector-template`
**Depends on**: `@guardspine/kernel >= 0.2.0` (peer dep)

---

### 13. n8n-nodes-guardspine

**What**: 11 n8n community nodes for visual workflow governance.

**Nodes**: GuardGate, CodeGuard, PDFGuard, SheetGuard, ImageGuard, EvidenceSeal, CouncilVote, ApprovalWait, BeadsCreate, BeadsUpdate, Compress

**Outputs**: n8n node package
**Depends on**: GuardSpine Backend API (HTTP calls)

---

### 14. codeguard-action

**What**: GitHub Action that runs on PR events. Analyzes diffs, classifies risk, runs multi-model AI review, produces evidence bundles, posts results to PR.

**Outputs**: GitHub Action, PR comments with findings
**Depends on**: GitHub API

---

### 15. rlm-docsync

**What**: Keeps documentation in sync with code. Extracts claims, inspects code for evidence, produces hash-chained evidence packs.

**Key files**:

- `cli/main.py` - CLI entry point (`docsync run`, `docsync verify`)
- `guardspine.docs.yaml` - Manifest format

**Outputs**: Evidence packs proving doc-code alignment
**Depends on**: `guardspine-kernel-py` (for hashing, with fallback)

---

### 16. executiveai-co

**What**: Marketing/product website. Built with Astro. Older, may be superseded by guardspine.ai.

**Outputs**: Static website
**Depends on**: Nothing in the ecosystem

---

## Visual Summary

```
                        THE GUARDSPINE ECOSYSTEM

    SPECIFICATION                    VERIFICATION
    +---------------+               +------------------+
    | guardspine-   |               | guardspine-      |
    | spec          |<-golden------>| verify           |
    | (v0.2.0)      |  vectors      | (standalone CLI) |
    +-------+-------+               +------------------+
            |
     defines schema
            |
    +-------+-------+--------+
    |                        |
    v                        v
+----------+          +-----------+
| kernel   |  parity  | kernel-py |
| (TS)     |<-------->| (Python)  |
+----+-----+          +-----+-----+
     |                       |
     | peer dep              | pip dep
     |                       |
+----+----+            +-----+-----+-----+-----+
|         |            |     |     |     |     |
v         v            v     v     v     v     v
adapter-  connector-  Guard  prod- open- rlm-  open-
webhook   template    Spine  uct   claw  doc-  claw-
                      mono-        plugin sync  hard-
                      repo                      ening
                        |
                   +----+----+
                   |         |
                   v         v
              codeguard-  n8n-nodes-
              action      guardspine

                   guardspine-local-council
                   (feeds into openclaw + hardening for L3+ votes)

                   openclaw-upstream
                   (fork with patches from guardspine-openclaw)
```
