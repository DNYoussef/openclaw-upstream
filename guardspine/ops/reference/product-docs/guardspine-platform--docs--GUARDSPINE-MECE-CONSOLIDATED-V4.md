# GuardSpine MECE Consolidated Specification v4.0

> **Vision**: AI-mediated work governance that unblocks throughput while generating defensible evidence.
> **Status**: Active Development | Last Updated: 2026-01-19

---

## Quick Status Summary

| Category            | Total Items | Done | Remaining | % Complete |
| ------------------- | ----------- | ---- | --------- | ---------- |
| **Frontend UI**     | 18          | 16   | 2         | 89%        |
| **Backend API**     | 25          | 21   | 4         | 84%        |
| **Evidence System** | 12          | 12   | 0         | 100%       |
| **Integrations**    | 10          | 4    | 6         | 40%        |
| **Open-Source**     | 3           | 3    | 0         | 100%       |
| **TOTAL**           | 68          | 56   | 12        | **82%**    |

---

## Part 1: Expert Council Requirements Matrix

### 1.1 The $1B Hiring Panel

| #   | Role                   | Key Question                              | Requirement                          | Status                                            |
| --- | ---------------------- | ----------------------------------------- | ------------------------------------ | ------------------------------------------------- |
| 1   | **Enterprise CISO**    | "Will this reduce risk and unblock work?" | Work Graph + Inbox as primary        | [x] UI Done                                       |
| 2   | **Head of Compliance** | "Can I hand this to an auditor?"          | Evidence scope, deterministic diffs  | [x] EvidenceScope + audit trail                   |
| 3   | **Product Counsel**    | "Who is liable? Is this subpoena-proof?"  | Immutability, retention              | [x] HashChain + RetentionConfig                   |
| 4   | **Records Management** | "Artifacts are records"                   | Provenance layer                     | [x] Full evidence bundle system                   |
| 5   | **ML Lead**            | "What is deterministic vs model-based?"   | Models suggest only                  | [x] UI shows "suggestion" framing                 |
| 6   | **Crypto Architect**   | "How do we prove no tampering?"           | Bundle signing, offline verification | [x] signing_service + export with VERIFICATION.md |
| 7   | **Workflow Architect** | "How does this land without revolt?"      | Pristine API, integrations           | [~] Partial API                                   |
| 8   | **VP Product**         | "What do we sell first?"                  | Approval inbox first                 | [x] UI Done                                       |
| 9   | **Sales Lead**         | "Who signs, blocks, champions?"           | Start with one artifact class        | [x] Strategy documented                           |
| 10  | **UX Lead**            | "Can humans approve in 10 seconds?"       | Diff Postcard wedge                  | [x] UI Done                                       |

### 1.2 Unanimous Convergence Points

| Point                               | Requirement                         | Implementation Status                                          |
| ----------------------------------- | ----------------------------------- | -------------------------------------------------------------- |
| **1. UI IS THE DIFFERENTIATOR**     | Approval throughput, visual trust   | [x] 4 screens implemented                                      |
| **2. TRUTH MUST BE DETERMINISTIC**  | Models annotate, never author truth | [x] UI framing + backend evidence system                       |
| **3. WIN BY INTEGRATION**           | SharePoint/Drive + ServiceNow/Jira  | [ ] Not started                                                |
| **4. DEFENSIBILITY IS THE PRODUCT** | Bundle verification, retention      | [x] Full implementation with signing, hash chains, audit trail |

### 1.3 Red Lines (Never Cross)

- [x] **Models never author truth** - UI shows "AI Suggestions" with confidence
- [x] **Verification must work offline** - Implemented with hash chains and export
- [x] **Evidence bundles are records** - Full implementation with audit trail
- [~] **API must be pristine** - Partial implementation
- [x] **Identity is verified (SSO)** - OIDC/SAML + SCIM provisioning implemented

---

## Part 2: MECE View Hierarchy (Frontend)

### Complete UI Architecture

```
GuardSpine UI
|
+-- 1. HOME (Risk & Flow) ------------ [x] DONE - HomePage.tsx
|   +-- Risk Tier Queue Bar Chart ---- [x] DONE
|   +-- Top Risk Drivers Treemap ----- [x] DONE (RiskDriversTreemap.tsx)
|   +-- Governed Event Volume Chart -- [x] DONE (EventVolumeChart.tsx)
|   +-- Blocked Work Panel ----------- [x] DONE
|   +-- Coverage Gauge --------------- [x] DONE (SVG arc)
|   +-- AI/Human Ratio --------------- [x] DONE
|
+-- 2. DECISIONS ----------------------
|   +-- 2.1 Inbox -------------------- [x] DONE - ApprovalsPage.tsx
|   |   +-- Expandable Rows ---------- [x] DONE
|   |   +-- DiffPostcard Quick Look -- [x] DONE (DiffPostcard.tsx)
|   +-- 2.2 Detail ------------------- [x] DONE - ApprovalDetailPage.tsx
|       +-- Split Diff View ---------- [x] DONE
|       +-- AI Suggestions Panel ----- [x] DONE
|       +-- Policy Checklist --------- [x] DONE
|       +-- Comments Section --------- [x] DONE
|       +-- Evidence Bundle Card ----- [x] DONE (mock)
|
+-- 3. WORK SPINE --------------------
|   +-- 3.1 Graph View --------------- [x] DONE - WorkGraphPage.tsx
|   |   +-- React Flow Canvas -------- [x] DONE
|   |   +-- Bead Nodes --------------- [x] DONE
|   |   +-- Dependency Edges --------- [x] DONE
|   |   +-- Sidebar Panel ------------ [x] DONE (selected bead details)
|   +-- 3.2 Bead Detail -------------- [x] DONE - BeadDetailPage.tsx
|
+-- 4. ARTIFACTS ---------------------
|   +-- 4.1 List --------------------- [x] DONE - ArtifactsPage.tsx
|   +-- 4.2 Detail ------------------- [x] DONE - ArtifactDetailPage.tsx
|       +-- 4.2.1 Code Diff ---------- [x] DONE (split/unified view)
|       +-- 4.2.2 PDF Diff ----------- [~] Partial (mock)
|       +-- 4.2.3 Sheet Diff --------- [~] Partial (mock)
|       +-- 4.2.4 Image Diff --------- [~] Partial (mock)
|
+-- 5. EVIDENCE ---------------------- [ ] NOT STARTED
|   +-- 5.1 Bundle Library ----------- [ ] TODO
|   +-- 5.2 Bundle Detail ------------ [ ] TODO
|
+-- 6. POLICIES ---------------------- [ ] NOT STARTED
|   +-- 6.1 Pack Registry ------------ [ ] TODO
|   +-- 6.2 Simulation --------------- [ ] TODO
|
+-- 7. COVERAGE ---------------------- [ ] NOT STARTED
|   +-- 7.1 Dashboard ---------------- [ ] TODO
|   +-- 7.2 Drift Alerts ------------- [ ] TODO
|
+-- 8. SEARCH ------------------------ [ ] NOT STARTED
|
+-- 9. ADMIN ------------------------- [ ] NOT STARTED
```

### Frontend Status Summary

| Screen              | Status   | Components Done                                            |
| ------------------- | -------- | ---------------------------------------------------------- |
| 1. Home (Dashboard) | **DONE** | RiskDriversTreemap, EventVolumeChart, CoverageGauge        |
| 2.1 Approval Inbox  | **DONE** | Table, expandable rows, DiffPostcard                       |
| 2.2 Approval Detail | **DONE** | Split diff, AI suggestions, policy checklist, comments     |
| 3.1 Work Graph      | **DONE** | React Flow, sidebar panel                                  |
| 3.2 Bead Detail     | **DONE** | Overview, events, approvals, dependencies tabs             |
| 4.1 Artifacts List  | **DONE** | Table with filters                                         |
| 4.2 Artifact Detail | **DONE** | Split/unified diff, annotations, evidence, history, policy |
| 5-9                 | TODO     | Not started                                                |

---

## Part 3: Backend API Checklist

### 3.1 MVP Endpoints (Required for UI)

| Endpoint                                | Status   | Notes              |
| --------------------------------------- | -------- | ------------------ |
| `GET /health`                           | [x] DONE | Basic health check |
| `GET /api/v1/dashboard/summary`         | [x] DONE | Dashboard KPIs     |
| `GET /api/v1/approvals`                 | [x] DONE | Approval list      |
| `GET /api/v1/approvals/{id}`            | [x] DONE | Approval detail    |
| `POST /api/v1/approvals/{id}/decisions` | [x] DONE | Submit decision    |
| `GET /api/v1/beads`                     | [x] DONE | Beads list         |
| `GET /api/v1/beads/{id}`                | [x] DONE | Bead detail        |
| `GET /api/v1/artifacts`                 | [x] DONE | Artifacts list     |

### 3.2 Extended Endpoints (Full Platform)

| Endpoint                                  | Status   | Priority                       |
| ----------------------------------------- | -------- | ------------------------------ |
| `GET /api/v1/dashboard/risk-drivers`      | [x] DONE | P1 - Real data for treemap     |
| `GET /api/v1/dashboard/event-volume`      | [x] DONE | P1 - Real data for chart       |
| `GET /api/v1/beads/{id}/graph`            | [x] DONE | P1 - Graph API                 |
| `GET /api/v1/artifacts/{id}`              | [x] DONE | P1 - Artifact detail           |
| `GET /api/v1/artifacts/{id}/versions`     | [x] DONE | P2                             |
| `GET /api/v1/diffs`                       | [x] DONE | P1 - Diff engine               |
| `GET /api/v1/diffs/{id}`                  | [x] DONE | P1 - Diff by ID                |
| `GET /api/v1/bundles`                     | [x] DONE | P2 - List with filters         |
| `GET /api/v1/bundles/{id}`                | [x] DONE | P2 - Full bundle details       |
| `POST /api/v1/bundles/{id}/verify`        | [x] DONE | P2 - Integrity verification    |
| `POST /api/v1/bundles/{id}/export`        | [x] DONE | P2 - JSON/ZIP/PDF/SARIF export |
| `GET /api/v1/search`                      | [ ] TODO | P3                             |
| `GET /api/v1/coverage`                    | [ ] TODO | P3                             |
| `GET /api/v1/drift`                       | [ ] TODO | P3                             |
| `GET /api/v1/policy-packs`                | [ ] TODO | P3                             |
| `POST /api/v1/policy-packs/{id}/simulate` | [ ] TODO | P3                             |
| `GET /api/v1/events/subscribe` (SSE)      | [x] DONE | P2 - Real-time updates         |

---

## Part 4: Evidence System (Council Critical)

### 4.1 Evidence Bundle Schema

| Component                           | Status   | Council Expert                                                                |
| ----------------------------------- | -------- | ----------------------------------------------------------------------------- |
| Evidence Scope ("what is asserted") | [x] DONE | Product Counsel - EvidenceScope model                                         |
| Deterministic Diff Metadata         | [x] DONE | ML Lead - EvidenceItem with content_hash                                      |
| Signer Identity Guarantees          | [x] DONE | Head of Compliance - SignerIdentity with AI model tracking                    |
| Immutability Semantics              | [x] DONE | Records Management - HashChain + ImmutabilityProof                            |
| Retention Policies                  | [x] DONE | Records Management - RetentionConfig (standard/extended/regulatory/permanent) |
| Export Formats (JSON/ZIP/PDF)       | [x] DONE | VP Product - export_service.py with 4 formats                                 |
| Offline Verification                | [x] DONE | Crypto Architect - VERIFICATION.md in ZIP exports                             |

### 4.2 Diff System

| Component              | Status        | Requirement                                               |
| ---------------------- | ------------- | --------------------------------------------------------- |
| Deterministic Core     | [x] DONE      | Same input = same output (difflib-based)                  |
| Model Annotation Layer | [x] DONE (UI) | Separate from ground truth                                |
| AI Suggestion Framing  | [x] DONE (UI) | Never says "is", always "suggests"                        |
| Confidence Scores      | [x] DONE (UI) | Visible to reviewer                                       |
| Audit Trail            | [x] DONE      | AuditTrail with entries tracking actor, action, timestamp |

---

## Part 5: Integration Priority (Phased)

### Phase 1 - Foundation (MVP Launch)

| Integration                      | Status   | Priority                                         |
| -------------------------------- | -------- | ------------------------------------------------ |
| 1. SSO + SCIM (Okta/Entra)       | [x] DONE | Non-negotiable - auth_service.py, auth.py router |
| 2. ServiceNow or Jira            | [ ] TODO | Workflow anchor                                  |
| 3. Microsoft 365 or Google Drive | [ ] TODO | Document source                                  |
| 4. GitHub                        | [ ] TODO | Code credibility                                 |

### Phase 2 - Expansion

| Integration    | Status   | Priority        |
| -------------- | -------- | --------------- |
| 5. Slack/Teams | [ ] TODO | Notifications   |
| 6. GRC export  | [ ] TODO | Compliance      |
| 7. DLP signals | [ ] TODO | Risk automation |

### Phase 3 - Platform

| Integration               | Status   | Priority          |
| ------------------------- | -------- | ----------------- |
| 8. Additional doc systems | [ ] TODO | Box, Confluence   |
| 9. Analytics export       | [ ] TODO | Power BI, Tableau |
| 10. Vendor intake         | [ ] TODO | Custom            |

---

## Part 6: Implementation Plan (Next Steps)

### Sprint 1: Complete Core UI (DONE)

- [x] ~~Dashboard with all charts~~
- [x] ~~Approval Inbox with DiffPostcard~~
- [x] ~~Approval Detail with split diff~~
- [x] ~~Work Graph with sidebar~~
- [x] ~~Bead Detail page (overview, events, approvals, dependencies)~~
- [x] ~~Artifact Detail with split/unified diff viewer~~

### Sprint 2: Backend Enhancement (DONE)

- [x] ~~Real data for dashboard charts (risk-drivers, event-volume endpoints)~~
- [x] ~~Graph API for beads~~
- [x] ~~Basic diff engine (code lane first)~~
- [x] ~~SSE for real-time updates~~

### Sprint 3: Evidence System (DONE)

- [x] ~~Evidence Bundle model implementation~~ - evidence_schemas.py
- [x] ~~Deterministic diff metadata~~ - EvidenceItem with content_hash
- [x] ~~Basic signing infrastructure~~ - signing_service.py
- [x] ~~Bundle export (JSON, ZIP)~~ - export_service.py with 4 formats
- [x] ~~Signer identity (AI model tracking)~~ - SignerIdentity model
- [x] ~~Immutability proof (hash chain)~~ - HashChain + ImmutabilityProof
- [x] ~~Retention policies~~ - RetentionConfig
- [x] ~~Offline verification instructions~~ - VERIFICATION.md in exports
- [x] ~~Audit trail~~ - AuditTrail with full action tracking

### Sprint 4: First Integration (DONE)

- [x] ~~Okta/Entra SSO setup~~ - auth_schemas.py + auth_service.py with OIDC/SAML support
- [x] ~~Role mapping configuration~~ - RoleMapping model + IdP group to role mapping
- [x] ~~User provisioning (SCIM)~~ - Full SCIM 2.0 API (RFC 7643/7644) endpoints
- [x] ~~User management endpoints~~ - CRUD + role assignment
- [x] ~~Session management~~ - Session creation, refresh, logout
- [x] ~~Authentication audit log~~ - Login/logout tracking
- [x] ~~Frontend auth context integration~~ - AuthContext.tsx, ProtectedRoute.tsx, LoginPage.tsx, AuthCallbackPage.tsx

### Sprint 5: Connector Framework (TODO)

- [ ] SharePoint connector
- [ ] Google Drive connector
- [ ] Jira connector
- [ ] ServiceNow connector

---

## Part 7: Open-Source Strategy ("Trust Ladder")

### 7.1 Philosophy

> "You don't need to trust me. Verify the bundle yourself."

In governance/security markets, buyers trust:

- **Verifiability** (can an auditor verify without you?)
- **Standards** (is this vendor-neutral?)
- **Integration** (does it fit existing workflows?)

GuardSpine builds trust through **open verification, closed workflow**.

### 7.2 What's Open (Apache 2.0)

| Component                         | Repository                                   | Purpose                                         |
| --------------------------------- | -------------------------------------------- | ----------------------------------------------- |
| **guardspine-spec**               | `open-source/guardspine-spec/`               | Bundle schema, signing rules, verification spec |
| **guardspine-verify**             | `open-source/guardspine-verify/`             | Standalone CLI for offline verification         |
| **guardspine-connector-template** | `open-source/guardspine-connector-template/` | Skeleton for building connectors                |

**Open-source benefits:**

- Auditors can verify without installing GuardSpine SaaS
- Any system can produce/consume compliant bundles
- Ecosystem can build around the spec

### 7.3 What's Closed (Commercial)

| Component                 | Value                | Rationale              |
| ------------------------- | -------------------- | ---------------------- |
| **Diff Postcard UI**      | 10-second approvals  | UX differentiation     |
| **Approval Inbox**        | Workflow efficiency  | Core product value     |
| **SSO/SCIM Auth**         | Enterprise security  | Enterprise requirement |
| **Premium Connectors**    | Deep integrations    | Monetization           |
| **Industry Rubric Packs** | Compliance templates | Monetization           |
| **Control Plane API**     | Full platform        | Stickiness             |

### 7.4 Licensing Strategy

| Layer              | License    | Rationale             |
| ------------------ | ---------- | --------------------- |
| Spec               | Apache 2.0 | Maximum adoption      |
| Verifier           | Apache 2.0 | Trust anchor          |
| Connector Template | Apache 2.0 | Ecosystem enablement  |
| Backend/Frontend   | Commercial | Value capture         |
| Rubric Packs       | Commercial | Vertical monetization |

### 7.5 Lock-In Protection

Before open-sourcing more, must lock:

- [x] **Spec Authority** - guardspine-spec is canonical format
- [ ] **Integration Lead** - Best connectors (SharePoint, Drive)
- [ ] **Rubric Lead** - Default packs for SOC2/HIPAA/SOX

### 7.6 Open-Source Directory Structure

```
D:\Projects\GuardSpine\open-source\
|
+-- guardspine-spec/
|   +-- README.md              # Quick start
|   +-- SPECIFICATION.md       # Full spec v0.1.0
|   +-- LICENSE                # Apache 2.0
|   +-- schemas/
|   |   +-- evidence-bundle.schema.json
|   +-- examples/
|   +-- test-vectors/
|
+-- guardspine-verify/
|   +-- README.md
|   +-- LICENSE
|   +-- pyproject.toml
|   +-- guardspine_verify/
|       +-- __init__.py
|       +-- verifier.py        # Core verification logic
|       +-- cli.py             # CLI interface
|
+-- guardspine-connector-template/
    +-- README.md
    +-- LICENSE
    +-- pyproject.toml
    +-- config.example.yaml
    +-- connector/
    |   +-- base.py            # BaseConnector class
    |   +-- events.py          # Event types
    |   +-- bundle_emitter.py  # Bundle creation
    +-- examples/
        +-- github_connector.py
```

---

## Part 8: Project Structure

### Directory Layout

```
D:\Projects\GuardSpine\
|
+-- backend/
|   +-- app/
|   |   +-- main.py           # FastAPI app
|   |   +-- routers/          # API routes
|   |   +-- services/         # Business logic
|   |   +-- models/           # Pydantic models
|   +-- requirements.txt
|
+-- frontend/
|   +-- src/
|   |   +-- pages/            # Route pages
|   |   +-- components/       # Reusable components
|   |   |   +-- charts/       # RiskDriversTreemap, EventVolumeChart
|   |   |   +-- DiffPostcard.tsx
|   |   +-- hooks/            # useApi, useDashboardSummary
|   |   +-- types/            # TypeScript interfaces
|   +-- package.json
|
+-- codeguard/                # Python package (core logic)
|   +-- audit.py
|   +-- classifier.py
|   +-- cli.py
|   +-- config.py
|   +-- diff.py
|   +-- evidence.py
|   +-- pipeline.py
|   +-- beads/
|   +-- guards/
|   +-- integrations/
|   +-- models/
|
+-- .codeguard/               # Data storage
|   +-- approvals/            # Approval JSON files
|   +-- logs/
|
+-- docs/
|   +-- GUARDSPINE-MECE-CONSOLIDATED-V4.md  (this file)
|   +-- EXPERT-COUNCIL-REQUIREMENTS.md
|   +-- UI-SPEC-V2-MECE.md
|   +-- BEADS-INTEGRATION.md
```

---

## Part 8: Success Metrics

### Product Metrics (Targets)

| Metric                          | Target        | Status              |
| ------------------------------- | ------------- | ------------------- |
| Approval throughput             | 10 sec median | [ ] Not measured    |
| Evidence bundle generation      | < 5 sec       | [ ] Not implemented |
| Offline verification success    | 100%          | [ ] Not implemented |
| False positive rate (risk tier) | < 5%          | [ ] Not measured    |

### Adoption Metrics (Phase 1)

| Metric                    | Target  | Status              |
| ------------------------- | ------- | ------------------- |
| Active approvers          | 10+     | [ ] Not deployed    |
| Governed artifacts        | 100+    | [ ] Not deployed    |
| Integrations active       | 1 (SSO) | [ ] Not started     |
| Evidence bundles exported | 50+     | [ ] Not implemented |

---

## Appendix A: Technology Stack

```yaml
frontend:
  framework: React 19 + TypeScript
  state: TanStack Query v5
  routing: React Router 7
  visualization:
    - React Flow 12 (work graph)
    - Recharts (charts)
  ui: Tailwind CSS 4

backend:
  framework: FastAPI
  database: SQLite (dev) -> PostgreSQL (prod)
  beads_cli: bd.exe subprocess

codeguard:
  language: Python 3.11+
  location: D:\Projects\GuardSpine\codeguard\
  entry: cli.py, pipeline.py
```

---

## Appendix B: Consolidation Notes

### Codeguard Folder Structure

| Path                     | Purpose                        | Keep/Delete       |
| ------------------------ | ------------------------------ | ----------------- |
| `GuardSpine/codeguard/`  | Python package (core logic)    | **KEEP**          |
| `GuardSpine/.codeguard/` | Data storage (approvals, logs) | **KEEP**          |
| `life-os-*/codeguard`    | Old copies                     | IGNORE (per user) |

**No consolidation needed** - The two folders serve different purposes:

- `codeguard/` = CODE (Python modules)
- `.codeguard/` = DATA (runtime files)

---

_Document Version: 4.0 MECE Consolidated_
_Last Updated: 2026-01-19_
_Status: Living Specification_
