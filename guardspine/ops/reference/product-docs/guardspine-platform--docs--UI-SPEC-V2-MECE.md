# GuardSpine UI Specification v2.0 (MECE)

> **Mission**: Control surface for AI-mediated work
> **Core Insight**: Humans review exceptions, not content. Evidence is derived, not authored.

---

## MECE View Hierarchy

```
GuardSpine UI
|
+-- 1. HOME (Risk & Flow) ------------ "Are we in control?" (30 sec answer)
|
+-- 2. DECISIONS ---------------------- Approval lifecycle
|   +-- 2.1 Inbox -------------------- Queue management
|   +-- 2.2 Detail ------------------- Evidence + action
|
+-- 3. WORK SPINE --------------------- Bead dependencies
|   +-- 3.1 Graph View --------------- Visual control flow
|   +-- 3.2 Bead Detail -------------- Entity deep dive
|
+-- 4. ARTIFACTS ---------------------- Document versions
|   +-- 4.1 List --------------------- Browse all artifacts
|   +-- 4.2 Detail ------------------- Diff/Annotations/Evidence/History/Policy
|       +-- 4.2.1 Code Diff ---------- Git/PR diffs + SARIF
|       +-- 4.2.2 PDF Diff ----------- Page-by-page + overlays
|       +-- 4.2.3 Sheet Diff --------- Cell changes + formulas
|       +-- 4.2.4 Image Diff --------- Before/after + regions
|
+-- 5. EVIDENCE ----------------------- Audit trail bundles
|   +-- 5.1 Bundle Library ----------- All generated bundles
|   +-- 5.2 Bundle Detail ------------ Verify + export
|
+-- 6. POLICIES ----------------------- Governance rules
|   +-- 6.1 Pack Registry ------------ Installed packs
|   +-- 6.2 Simulation --------------- "What if" analysis
|
+-- 7. COVERAGE ----------------------- Governance scope
|   +-- 7.1 Dashboard ---------------- Governed vs ungoverned
|   +-- 7.2 Drift Alerts ------------- Unlinked changes
|
+-- 8. SEARCH ------------------------- Cross-entity forensics
|
+-- 9. ADMIN -------------------------- System configuration
    +-- 9.1 Tenants/Workspaces
    +-- 9.2 RBAC
    +-- 9.3 Integrations
    +-- 9.4 Retention
```

---

## 1. HOME (Risk & Flow View)

### Purpose

Answer "Are we in control?" in 30 seconds.

### Components (MECE)

| Component                  | Data                   | Action                 |
| -------------------------- | ---------------------- | ---------------------- |
| **Open Approvals by Tier** | L3: X, L4: Y           | Jump to filtered queue |
| **Blocked Beads**          | Count + top 3 blockers | Jump to graph filtered |
| **New High-Risk Events**   | 24h/7d toggle          | Jump to event list     |
| **Coverage Gauge**         | X% governed            | Jump to drift list     |
| **Median Time-to-Approve** | By tier/lane           | Jump to SLA report     |
| **Ungoverned Changes**     | This week count        | Jump to adoption queue |
| **AI/Human Ratio**         | % AI-generated         | Trend analysis         |

### API Endpoints

```
GET /api/v1/dashboard/approvals-summary
GET /api/v1/dashboard/blocked-summary
GET /api/v1/dashboard/events-summary?window=24h|7d
GET /api/v1/dashboard/coverage
GET /api/v1/dashboard/sla-metrics
GET /api/v1/dashboard/ungoverned
GET /api/v1/dashboard/ai-human-ratio
```

---

## 2. DECISIONS

### 2.1 Inbox (Decision Queue)

| Column             | Source                 | Filter                            |
| ------------------ | ---------------------- | --------------------------------- |
| Risk Tier          | `risk_tier`            | L0-L4 multi-select                |
| Status             | `status`               | pending/approved/rejected/expired |
| Artifact           | `artifact.kind` icon   | lane filter                       |
| Title              | `bead.title`           | search                            |
| Owner              | `bead.owner`           | dropdown                          |
| Required Approvers | `required_approvers[]` | role filter                       |
| Deadline           | `due_at`               | SLA countdown                     |
| Last Updated       | `updated_at`           | sort                              |

**Actions per row:**

- Open Detail
- Quick Approve (if L0-L2)
- Bulk select

**API:**

```
GET /api/v1/approvals?status=pending&risk_tier=L3,L4&lane=pdf
```

### 2.2 Detail (Decision View)

| Tab           | Content                                  |
| ------------- | ---------------------------------------- |
| **Summary**   | Risk tier + reasons + policy packs fired |
| **Evidence**  | Diff postcard preview                    |
| **Checklist** | Required controls from policy pack       |
| **Timeline**  | Decision history                         |

**Actions:**

- Approve with rationale + conditions
- Reject with rationale
- Request changes
- Add annotation
- Request model review
- Export to Jira/ServiceNow/GRC

**API:**

```
GET /api/v1/approvals/{id}
POST /api/v1/approvals/{id}/decisions
POST /api/v1/approvals/{id}/request-model-review
```

---

## 3. WORK SPINE (Beads)

### 3.1 Graph View (Control View)

| Node Type        | Visual          | Meaning               |
| ---------------- | --------------- | --------------------- |
| Ready            | Green outline   | Can proceed           |
| Blocked          | Red + lock icon | Waiting on dependency |
| Pending Approval | Orange          | At gate               |
| Approved         | Green filled    | Passed gate           |

| Edge Type  | Visual            | Meaning       |
| ---------- | ----------------- | ------------- |
| depends_on | Gray arrow        | Structural    |
| blocks     | Red dashed + lock | Governance    |
| related    | Dotted gray       | Informational |

**Toggle:** Structural vs Governance dependencies

**API:**

```
GET /api/v1/beads/{id}/graph
```

### 3.2 Bead Detail

| Section          | Content                           |
| ---------------- | --------------------------------- |
| Metadata         | Owner, status, tags, due date     |
| Linked Artifacts | Code/PDF/XLSX/Image list          |
| Event Timeline   | Guard events + bead events merged |
| Current Gates    | What's blocking progress          |

**Actions:**

- Attach artifact
- Trigger audit
- Generate evidence bundle
- Request approval

**API:**

```
GET /api/v1/beads/{id}
GET /api/v1/beads/{id}/events
POST /api/v1/beads/{id}/artifacts
POST /api/v1/beads/{id}/audits
```

---

## 4. ARTIFACTS

### 4.1 List

| Column         | Filter              |
| -------------- | ------------------- |
| Kind           | code/pdf/xlsx/image |
| Title          | search              |
| Latest Version | -                   |
| Risk Tier      | L0-L4               |
| Last Event     | date range          |
| Open Approvals | count               |

**API:**

```
GET /api/v1/artifacts?kind=pdf&risk_tier=L3
```

### 4.2 Detail (Evidence View)

**Tabs (same for all artifact kinds):**

| Tab             | Purpose                     |
| --------------- | --------------------------- |
| **Diff**        | Primary - show what changed |
| **Annotations** | AI + human notes            |
| **Evidence**    | Links to bundles            |
| **History**     | Version timeline            |
| **Policy**      | Rules that apply            |

**Diff Tab by Kind:**

| Kind      | Components                                                     |
| --------- | -------------------------------------------------------------- |
| **Code**  | Commit/PR diff + findings panel + SARIF link                   |
| **PDF**   | Changed pages list + side-by-side + overlays + snippet gallery |
| **Sheet** | Changed cells table + formula changes + range heatmap          |
| **Image** | Before/after + changed regions + bounding box overlays         |

**Evidence Scope Indicator:**
"Diff computed from v1 -> v2 using [parser] v[version]"

**API:**

```
GET /api/v1/artifacts/{id}
GET /api/v1/artifacts/{id}/versions
GET /api/v1/artifacts/{id}/diffs
GET /api/v1/diffs/{id}
GET /api/v1/diffs/{id}/artifacts (signed URLs)
GET /api/v1/artifacts/{id}/annotations
POST /api/v1/artifacts/{id}/annotations
```

---

## 5. EVIDENCE

### 5.1 Bundle Library

| Column        | Filter                       |
| ------------- | ---------------------------- |
| Bead          | link                         |
| Artifact      | link                         |
| Versions      | from -> to                   |
| Risk Tier     | L0-L4                        |
| Created       | date                         |
| Export Status | pending/exported/failed      |
| Integrity     | verified/unverified/mismatch |

**API:**

```
GET /api/v1/bundles?artifact_id=X&integrity_status=verified
```

### 5.2 Bundle Detail

| Section        | Content                             |
| -------------- | ----------------------------------- |
| Summary        | bundle.json rendered human-readable |
| Artifacts      | Refs + SHA256 hashes                |
| Event Chain    | Pointers used                       |
| Visual Gallery | Overlays/postcards/snippets         |

**Actions:**

- Verify integrity (server recompute)
- Download pack
- Export to external system

**API:**

```
GET /api/v1/bundles/{id}
POST /api/v1/bundles/{id}/verify
POST /api/v1/bundles/{id}/export
```

---

## 6. POLICIES

### 6.1 Pack Registry

| Column      | Content         |
| ----------- | --------------- |
| Pack Name   | identifier      |
| Version     | semver          |
| Owner       | team            |
| Status      | active/inactive |
| Rules Count | N rules         |

**Actions:**

- Activate/deactivate per workspace
- Roll forward/back version
- View audit history

**API:**

```
GET /api/v1/policy-packs
GET /api/v1/policy-packs/{id}
POST /api/v1/policy-packs/{id}/activate
```

### 6.2 Simulation

**Input:**

- Time window (from/to)
- Team/workspace filter
- Lane filter

**Output:**

- Would-be-blocked items
- Rules that would fire
- Impact counts

**API:**

```
POST /api/v1/policy-packs/{id}/simulate
GET /api/v1/policy-simulations/{id}
```

---

## 7. COVERAGE

### 7.1 Dashboard

| Metric                 | Visualization       |
| ---------------------- | ------------------- |
| Governed vs Ungoverned | Stacked bar by lane |
| By Team                | Heatmap             |
| Trend                  | Line chart          |
| Top Ungoverned Sources | Table               |

**API:**

```
GET /api/v1/coverage
```

### 7.2 Drift Alerts

| Column         | Filter          |
| -------------- | --------------- |
| Severity       | high/medium/low |
| Source         | location        |
| Suggested Link | artifact_id     |
| Ack Status     | true/false      |

**Actions:**

- Link and backfill (create bead + events)
- Acknowledge/silence

**API:**

```
GET /api/v1/drift
POST /api/v1/drift/{id}/ack
POST /api/v1/drift/{id}/adopt
```

---

## 8. SEARCH

**Single search box across:**

- Beads
- Artifacts
- Bundles
- Events
- Actors
- Policy packs

**Facets:**

- Type
- Lane
- Risk tier
- Time range
- Tags

**API:**

```
GET /api/v1/search?q=...&type=bead,artifact&lane=pdf&from=...&to=...
```

---

## 9. ADMIN

### 9.1 Tenants/Workspaces

- Create/edit/archive
- Workspace hierarchy

### 9.2 RBAC

| Role     | Permissions     |
| -------- | --------------- |
| Viewer   | Read only       |
| Reviewer | Add annotations |
| Approver | Approve/reject  |
| Auditor  | Export bundles  |
| Admin    | Full access     |

### 9.3 Integrations

- Jira
- ServiceNow
- SharePoint
- Google Drive
- Git providers

### 9.4 Retention

- Retention policies
- Legal hold
- Purge scheduling

---

## Global Shell

### Top Navigation

```
[Logo] Home | Approvals | Work Graph | Artifacts | Evidence | Policies | Coverage | [Search] | [Admin]
```

### Global Filters (Persistent)

- Tenant/Workspace selector
- Team filter
- Time range
- Lanes: code | pdf | xlsx | image
- Risk tier: L0 | L1 | L2 | L3 | L4
- Policy packs

### Global Status Bar

- Daemon health indicator
- Last sync time
- Export queue health
- WebSocket connection status

---

## Event Stream (Real-time)

**SSE/WebSocket endpoint:**

```
GET /api/v1/events/subscribe
```

**Events pushed:**

- New approvals
- Approval decisions
- Bundle generation complete
- Drift alerts
- Export completions

---

## MVP Endpoints (Minimum Viable)

```
# Core
GET  /health
GET  /search

# Approvals (Decision View)
GET  /approvals
GET  /approvals/{id}
POST /approvals/{id}/decisions

# Beads (Control View)
GET  /beads
GET  /beads/{id}
GET  /beads/{id}/graph

# Artifacts (Evidence View)
GET  /artifacts
GET  /artifacts/{id}
GET  /diffs/{id}

# Dashboard (Risk & Flow)
GET  /dashboard/approvals-summary
GET  /dashboard/coverage
```

---

_Combined from original spec + detailed sitemap_
_Version: 2.0 MECE_
_Date: 2026-01-19_
