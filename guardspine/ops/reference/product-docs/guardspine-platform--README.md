# GuardSpine

**The audit spine for AI-era work**

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

GuardSpine is a **unified governance and evidence system** for modern office work--where **code, documents, and spreadsheets are all AI-assisted**, and every meaningful change must be **attributable, reviewable, and defensible**.

Instead of governing _models_ or _apps_, GuardSpine governs **work itself**.

---

## Quick Start

### Backend API

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at `http://localhost:8000` with interactive docs at `/docs`.

### CLI Tools

```bash
# Install codeguard CLI
pip install -e .

# Run a code audit
codeguard audit --repo . --output evidence.json

# Run a PDF audit
codeguard pdfguard audit --input policy_v1.pdf --updated policy_v2.pdf

# Run a spreadsheet audit
codeguard sheetguard audit --input finance_v1.xlsx --updated finance_v2.xlsx

# Run an image audit
codeguard imageguard audit --before ui_before.png --after ui_after.png
```

### GitHub Action

```yaml
- uses: DNYoussef/guardspine-action@v1
  with:
    risk-threshold: L2
    ai-review: true
```

---

## Architecture

```
+------------------+     +------------------+     +------------------+
|   Guard Lanes    |     |   Backend API    |     |   Integrations   |
|  (CLI Tools)     |     |   (FastAPI)      |     |                  |
+------------------+     +------------------+     +------------------+
| - CodeGuard      |     | - 149 Routes     |     | - GitHub         |
| - PDFGuard       |<--->| - Artifacts      |<--->| - Jira           |
| - SheetGuard     |     | - Approvals      |     | - Slack          |
| - ImageGuard     |     | - Bundles        |     | - M365           |
+------------------+     | - Webhooks       |     | - DLP/CASB       |
        |                +------------------+     +------------------+
        v                        |
+------------------+             v
| Evidence Bundles |     +------------------+
| (JSON/SARIF/ZIP) |     |   Beads Spine    |
+------------------+     | (Work Graph)     |
                         +------------------+
```

---

## Why GuardSpine Exists

In modern organizations:

- AI assists code changes
- AI reviews and rewrites policies
- AI proposes spreadsheet changes that affect money, risk, and compliance
- Decisions are made through chains of agents, tools, and humans

But existing systems fail in predictable ways:

- **GitHub** governs code, not documents or decisions
- **DMS tools** store files, but don't produce audit-grade diffs or provenance
- **GRC tools** collect evidence _after the fact_
- **AI observability tools** log runs, not accountability
- **"AI governance" platforms** track models, not everyday work artifacts

**GuardSpine fills the gap**: it is the **system of record for governed change** in an AI-assisted office.

---

## Backend API

The GuardSpine backend provides **149 API routes** across these domains:

| Domain            | Endpoints                 | Description                                  |
| ----------------- | ------------------------- | -------------------------------------------- |
| **Artifacts**     | `/api/v1/artifacts/*`     | Artifact registration, versioning, ownership |
| **Approvals**     | `/api/v1/approvals/*`     | Approval workflows, decisions, escalation    |
| **Bundles**       | `/api/v1/bundles/*`       | Evidence bundles, verification, export       |
| **Webhooks**      | `/api/v1/webhooks/*`      | External system integrations                 |
| **Slack**         | `/api/v1/slack/*`         | Slack interactive messages and events        |
| **Search**        | `/api/v1/search/*`        | Full-text and filtered search                |
| **Governance**    | `/api/v1/governance/*`    | Policy management, risk tiers                |
| **Board Packets** | `/api/v1/board-packets/*` | Executive reporting                          |
| **Alerts**        | `/api/v1/alerts/*`        | Notification management                      |
| **Auth**          | `/api/v1/auth/*`          | Authentication and authorization             |

### API Documentation

- **OpenAPI/Swagger**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## External Integrations (Phase 5)

GuardSpine integrates with external systems via webhooks and APIs:

### GitHub Integration

- **Push events**: Trigger artifact versioning on code changes
- **Pull requests**: Link PRs to Beads, track lifecycle
- **Reviews**: Map GitHub approvals to canonical GuardSpine approvals
- **Code scanning**: Ingest security findings as L2-L4 risk items

### Jira Integration

- **Issue created**: Automatically link Jira issues to Beads
- **Status changes**: Sync Jira status to Bead state

### Slack Integration

- **Interactive messages**: Approve/reject directly from Slack
- **Rejection modals**: Capture rejection rationale
- **App mentions**: Bot commands for status queries
- **Events API**: Real-time event processing

### Microsoft 365 Integration

- **SharePoint/OneDrive**: Track document changes via Graph API
- **File sync**: Automatic artifact versioning for Office documents

### DLP/CASB Integration

- **Microsoft Purview**: Sensitivity labels, classification signals
- **Netskope**: DLP incidents, policy violations
- **Risk tier adjustment**: Automatic tier bumps based on PII/PCI/PHI detection

---

## The Guard Lanes (v1)

GuardSpine ships with four first-class "lanes." Each lane governs a different artifact type, but **all emit the same audit events and evidence format**.

### 1) CodeGuard -- Governed Code Changes

- Classifies code changes by risk (L0-L4)
- Runs multi-model AI reviews
- Escalates to human approval when required
- Produces audit-grade evidence bundles (JSON/SARIF)
- Integrates with CI and protected branches

**CodeGuard answers:**

> _"Can we prove how this code change was reviewed and approved?"_

### 2) PDFGuard -- Governed Document Changes

- Tracks version-to-version PDF changes
- Computes deterministic page/text/visual diffs
- Allows AI to **comment, highlight, and tag** -- never edit
- Produces evidence bundles for policy, contract, and disclosure changes
- Supports approval gates for regulated documents

**PDFGuard answers:**

> _"What changed in this policy, why, and who approved it?"_

### 3) SheetGuard -- Governed Spreadsheet Changes

- Tracks XLSX/Sheets version changes
- Diffs cells, formulas, ranges, and structure
- Flags high-risk changes (formulas, macros, external links)
- Allows AI to review and suggest -- never modify
- Produces evidence bundles suitable for SOX, finance, and risk audits

**SheetGuard answers:**

> _"Which spreadsheet changes affected money or risk, and how were they reviewed?"_

### 4) ImageGuard -- Governed Screenshots

- Tracks before/after screenshots or single images with expected state
- Computes deterministic pixel diffs and object-level tags
- Produces annotated overlays and visual evidence bundles
- Emits GuardSpine events for support tickets and UI change review

**ImageGuard answers:**

> _"Which pixels changed in this UI, and how did we review it?"_

---

## Risk Tiers

| Tier   | Description        | Review Required            |
| ------ | ------------------ | -------------------------- |
| **L0** | Cosmetic/trivial   | None                       |
| **L1** | Low risk           | AI review                  |
| **L2** | Medium risk        | AI + human notification    |
| **L3** | High risk          | AI + human approval        |
| **L4** | Critical/regulated | AI + senior human approval |

---

## Evidence Bundles (v0.2.1)

Every governed change produces a **v0.2.1 evidence bundle** with cryptographic integrity:

- **Canonical hashing** via [@guardspine/kernel](https://github.com/DNYoussef/guardspine-kernel) (TypeScript, canonical) or [guardspine-kernel-py](https://github.com/DNYoussef/guardspine-kernel-py) (Python port) -- both produce byte-identical output
- **Hash chain** linking items via `previous_hash` -> `chain_hash` (not content_hash -- this matters)
- **Immutability proof** with incremental SHA-256 root hash
- **Optional signatures** (Ed25519, RSA-SHA256, ECDSA-P256, HMAC-SHA256)
- **Sanitization attestation** (v0.2.1): documents PII/secret redaction engine, method, token format, and redaction count
- **in-toto attestation wrapping**: bundles can be wrapped as [in-toto](https://in-toto.io/) statements for supply-chain interop (CNCF standard)
- **Sigstore integration**: optional cosign signing and verification via `codeguard/sigstore.py`

Bundles can be:

- **Verified offline** with [guardspine-verify](https://github.com/DNYoussef/guardspine-verify) or either kernel library
- Wrapped as in-toto attestations for CNCF supply-chain tooling
- Signed with cosign (Sigstore) for keyless or keyed verification
- Exported to ServiceNow / Jira
- Archived for regulatory retention (1-7+ years)
- Regenerated at any time from the event log

```bash
# Verify any bundle offline
pip install guardspine-verify
guardspine-verify evidence-bundle.json
```

This is not "logging." This is **defensible, cryptographically-verifiable evidence**.

---

## The Beads Spine

GuardSpine uses **Beads** as its underlying _work spine_:

- Each governed change is attached to a **bead** (a unit of work)
- Dependencies between beads model real-world control flow
- Guard lanes emit **append-only audit events** tied to beads
- Evidence bundles are reproducible from the event log

> **Beads = why the work exists**
> **Guard events = how the work was governed**

---

## Critical Design Decision: AI Cannot Edit Artifacts

In GuardSpine:

- **AI may read, analyze, comment, and suggest**
- **AI may never directly modify code, documents, or spreadsheets**
- All AI output is stored as **sidecar annotations with full provenance**

This separation of duties is intentional:

- It simplifies compliance approvals
- It prevents silent or untraceable changes
- It makes audit narratives clean and defensible

---

## Escalation and Approval Workflow

GuardSpine enforces **self-approval prevention** across all approval paths. A single canonical `SelfApprovalError` is shared between the escalation engine (`codeguard/escalation/`) and the governance module (`codeguard/governance.py`). The backend API catches this at the router level and returns HTTP 409.

The escalation workflow supports:

- **Risk-based routing**: L3+ changes require human approval
- **Self-approval guard**: the person who created a change request cannot approve it
- **JWT authentication**: all API endpoints require a valid bearer token (configurable via `GUARDSPINE_JWT_SECRET`)
- **Audit trail**: every approval decision is recorded with `created_by`, timestamp, and rationale

---

## Compliance Rubrics

GuardSpine ships 11 built-in rubrics in `codeguard/rubrics/builtin/`:

| Rubric         | Standard             | Key Patterns                                                   |
| -------------- | -------------------- | -------------------------------------------------------------- |
| `soc2.yaml`    | SOC 2 Trust Services | Access controls, encryption, logging                           |
| `hipaa.yaml`   | HIPAA 164.312        | PHI handling, audit controls, transmission security            |
| `pci-dss.yaml` | PCI-DSS              | Cardholder data, key management, access restriction            |
| `dora.yaml`    | EU DORA              | ICT risk management, incident reporting, third-party oversight |
| `default.yaml` | General              | Broad code quality and security patterns                       |
| + 6 more       | Various              | Language-agnostic code-quality patterns                        |

The **Rubric Hub** (`backend/app/routers/rubric_hub.py`) provides API endpoints for browsing, searching, and applying rubrics dynamically.

---

## Open Source Components

| Project                           | Description                                    | Link                                                                 |
| --------------------------------- | ---------------------------------------------- | -------------------------------------------------------------------- |
| **@guardspine/kernel**            | Canonical hash/seal/verify (TypeScript)        | [GitHub](https://github.com/DNYoussef/guardspine-kernel)             |
| **guardspine-kernel-py**          | Python port (byte-identical output)            | [GitHub](https://github.com/DNYoussef/guardspine-kernel-py)          |
| **guardspine-spec**               | Evidence bundle specification + golden vectors | [GitHub](https://github.com/DNYoussef/guardspine-spec)               |
| **guardspine-verify**             | Offline bundle verifier                        | [GitHub](https://github.com/DNYoussef/guardspine-verify)             |
| **codeguard-action**              | GitHub Action (CI governance)                  | [GitHub](https://github.com/DNYoussef/codeguard-action)              |
| **guardspine-connector-template** | Connector SDK                                  | [GitHub](https://github.com/DNYoussef/guardspine-connector-template) |

---

## Testing

```bash
# Run all tests (737 tests)
python -m pytest tests/ -v --tb=short

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific domains
pytest tests/test_escalation.py tests/test_governance.py   # Approval workflow
pytest tests/test_sigstore.py                               # Sigstore integration
pytest tests/test_intoto.py                                 # in-toto attestations
```

---

## Project Structure

```
GuardSpine/
+-- backend/                 # FastAPI backend (210 routes)
|   +-- app/
|   |   +-- main.py
|   |   +-- routers/         # API endpoints (approvals, rubric_hub, bundles, ...)
|   |   +-- services/        # Business logic (approval_service, ...)
|   |   +-- models/          # Pydantic schemas
|   +-- tests/               # pytest tests (328+)
+-- codeguard/               # Core library + CLI tools
|   +-- exceptions.py        # Canonical exception types (SelfApprovalError)
|   +-- governance.py        # Governance change management
|   +-- intoto.py            # in-toto attestation wrapping
|   +-- sigstore.py          # Sigstore cosign integration
|   +-- escalation/          # Approval workflow engine
|   +-- rubrics/builtin/     # 11 built-in rubrics (SOC2, HIPAA, PCI-DSS, DORA, ...)
|   +-- guards/
|   |   +-- imageguard/
|   |   +-- pdfguard/
|   |   +-- sheetguard/
+-- frontend/                # React dashboard (approval queue, rubric browser)
+-- tests/                   # Integration and unit tests
+-- docs/                    # Documentation
```

---

## Status

| Component            | Status                                         |
| -------------------- | ---------------------------------------------- |
| CodeGuard            | Production-ready                               |
| PDFGuard             | Implemented                                    |
| SheetGuard           | Implemented                                    |
| ImageGuard           | Implemented                                    |
| Backend API          | 210 routes, 737 tests passing                  |
| Escalation Workflow  | Self-approval guard, JWT auth                  |
| in-toto Attestations | Wrap bundles as CNCF supply-chain statements   |
| Sigstore (cosign)    | Sign and verify bundles via Sigstore           |
| DORA Rubric          | EU Digital Operational Resilience Act patterns |
| Rubric Hub API       | Browse, search, and apply rubrics via API      |
| GitHub Integration   | Phase 5 complete                               |
| Jira Integration     | Phase 5 complete                               |
| Slack Integration    | Phase 5 complete                               |
| M365 Integration     | Phase 5 complete                               |
| DLP Integration      | Phase 5 complete                               |

---

## Who This Is For

- Security and GRC teams who need **provable process**
- Engineering orgs operating under compliance constraints
- Legal and compliance teams managing policy and contract changes
- Finance and ops teams whose spreadsheets affect money and risk
- Organizations preparing for an **AI-native audit future**

---

## License

Proprietary - Contact for licensing.

Open source components (guardspine-spec, guardspine-verify, guardspine-connector-template) are Apache 2.0.

---

**GuardSpine is the audit substrate for AI-era work--governing code, documents, and spreadsheets with a single, defensible chain of evidence.**
