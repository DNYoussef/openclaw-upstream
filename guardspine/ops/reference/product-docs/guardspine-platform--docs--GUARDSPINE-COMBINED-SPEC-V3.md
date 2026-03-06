# GuardSpine Combined Specification v3.0

> **Vision**: AI-mediated work governance that unblocks throughput while generating defensible evidence.

## Executive Summary

GuardSpine is an enterprise governance platform built on the Beads atomic work item system. This specification incorporates:

- UI mockup analysis (4 core screens)
- Expert council recommendations ($1B hiring panel)
- Enterprise integration architecture

**Core Insight from Expert Council**: "Your UI is the differentiator. Truth must be deterministic. You win by integration. Your defensibility is the product."

---

## Part 1: Expert Council Requirements Matrix

### 1.1 Stakeholder Requirements

| Expert                 | Primary Concern                  | Key Requirement                                      | Priority |
| ---------------------- | -------------------------------- | ---------------------------------------------------- | -------- |
| **Enterprise CISO**    | Risk reduction + unblocking work | Work Graph + Inbox as primary product                | P0       |
| **Head of Compliance** | Audit evidence quality           | Evidence scope, deterministic diffs, signer identity | P0       |
| **Product Counsel**    | Liability + chain-of-custody     | Immutability semantics, retention policies           | P0       |
| **Records Management** | Legal holds, retention schedules | Provenance layer, not file store                     | P1       |
| **ML Lead**            | Deterministic vs model-based     | Models suggest, never author truth                   | P0       |
| **Crypto Architect**   | Tamper evidence                  | Bundle signing, offline verification                 | P1       |
| **Workflow Architect** | Enterprise landing               | Pristine API, ServiceNow/Jira integration            | P0       |
| **VP Product**         | Adoption + packaging             | Sell approval inbox first                            | P1       |
| **Sales Lead**         | Champion/blocker dynamics        | Start with one artifact class                        | P2       |
| **UX Lead**            | Approval throughput              | Diff Postcard as wedge, 10-second approvals          | P0       |

### 1.2 Expert Convergence Points (Unanimous)

1. **UI is the differentiator** - Approval throughput + visual trust calibration
2. **Truth must be deterministic** - Models annotate/suggest, never define ground truth
3. **Win by integration** - SharePoint/Drive + ServiceNow/Jira + DLP feeds
4. **Defensibility is the product** - Bundle verification, retention semantics, provenance

### 1.3 Non-Negotiable Requirements

```yaml
evidence_bundle:
  must_have:
    - evidence_scope: "What is asserted"
    - deterministic_diff_metadata: true
    - signer_identity_guarantees: true
    - immutability_semantics: true
    - retention_policies: configurable
    - offline_verification: supported
  export_format: "boring and standard"

diff_system:
  deterministic: true
  model_role: "suggest, highlight, annotate"
  model_never: "author truth, make decisions"

api:
  quality: "pristine"
  operations:
    - search
    - fetch_artifacts
    - approval_decisions
    - export_bundles
```

---

## Part 2: UI Specification (From Mockups)

### 2.1 Screen 1: Executive Dashboard (Risk & Flow)

**Purpose**: "Are we in control?" - 30-second executive answer

```
+------------------------------------------------------------------+
|  GuardSpine Executive Control: Risk & Flow                        |
+------------------------------------------------------------------+
| +---------------+ +------------------------+ +------------------+ |
| | Risk Tier     | | Top Risk Drivers       | | Governed Event   | |
| | Queue         | | (Treemap)              | | Volume           | |
| |               | |                        | | (Multi-line)     | |
| | [Bar Chart]   | | Signature Changed 40%  | |                  | |
| | L4: 3         | | Macros Added 25%       | | Code  ----/      | |
| | L3: 12        | | PII Detected 20%       | | PDF   ----/      | |
| |               | | External Link 15%      | | XLSX  ----/      | |
| +---------------+ +------------------------+ +------------------+ |
| +---------------------------+ +----------------------------------+ |
| | Blocked Work              | | Coverage Health                  | |
| | Bead #452 blocked by #450 | | [Gauge] 88% Governed             | |
| +---------------------------+ +----------------------------------+ |
+------------------------------------------------------------------+
```

**Components**:
| Component | Data Source | Interactive |
|-----------|-------------|-------------|
| Risk Tier Queue | `/dashboard/approvals-summary` | Click -> filtered approvals |
| Top Risk Drivers | `/dashboard/risk-drivers` | Click -> filtered by reason |
| Governed Event Volume | `/dashboard/event-volume` | Hover -> details |
| Blocked Work | `/beads?status=blocked` | Click -> Work Graph |
| Coverage Health | `/dashboard/coverage` | Click -> Coverage page |

**New API Endpoints Required**:

```python
GET /api/v1/dashboard/risk-drivers
# Returns: { "drivers": [{"reason": "signature_changed", "count": 40, "percent": 0.40}, ...] }

GET /api/v1/dashboard/event-volume?range=7d
# Returns: { "series": [{"date": "2026-01-19", "code": 50, "pdf": 30, "xlsx": 20, "image": 10}] }
```

### 2.2 Screen 2: Work Graph (Control Flow)

**Purpose**: Visualize dependencies and governance blocks

```
+------------------------------------------------------------------+
|  GuardSpine Work Graph: Control Flow                              |
+------------------------------------------------------------------+
|                                                    +-------------+|
|  +--------+     +--------+     +--------+         | Bead #452   ||
|  | #448   |---->| #452   |---->| #450   |         |-------------|
|  | Data   |     | Q3 Fin |     | Legal  |         | Owner:      ||
|  | Export |     | Report |     | Policy |         | Jane Doe    ||
|  | (CSV)  |     | (XLSX) |     | (DOCX) |         |             ||
|  +--------+     | BLOCKED|     +--------+         | Risk: L3    ||
|                 +--------+                        |             ||
|                      |                            | Blocked By: ||
|                      v                            | #450        ||
|                 +--------+                        |             ||
|                 | #453   |                        |[View Blocker]|
|                 | Exec   |                        +-------------+|
|                 | Review |                                       |
|                 | (PDF)  |                                       |
|                 +--------+                                       |
+------------------------------------------------------------------+
```

**Node States**:
| State | Border | Background | Label |
|-------|--------|------------|-------|
| Ready | Green | Transparent | "Ready" |
| Blocked | Red | Red/10% | "Blocked" |
| Pending Approval | Orange | Orange/10% | "Approval Requested" |
| Approved | Green | Green/20% | "Approved" |

**Edge Types**:
| Type | Style | Color |
|------|-------|-------|
| Dependency | Solid | Gray |
| Blocking | Animated, dashed | Red |
| Approved flow | Solid | Green |

**Sidebar Panel**:

- Bead ID + Title
- Owner
- Risk Tier (badge)
- Blocked By (link to blocker)
- Linked Artifacts
- [View Blocker] button
- [Request Unblock] button

### 2.3 Screen 3: Approval Inbox

**Purpose**: Fast triage and approval throughput

```
+------------------------------------------------------------------+
|  GuardSpine Approval Inbox                                        |
+------------------------------------------------------------------+
| Risk | Status           | Artifact | Bead Title        | Owner  | Time |
|------|------------------|----------|-------------------|--------|------|
| > L3 | Awaiting Approval| [DOC]    | Bead #450: Legal..| J.Smith| 2h   |
| v L3 | Awaiting Approval| [DOC]    | Bead #450: Legal..| J.Smith| 2h   |
+------------------------------------------------------------------+
| Quick Look: Diff Postcard                                    [X] |
| +-----------------------------+-----------------------------+    |
| |  [Original v1]              |  [Proposed v2]              |    |
| |                             |   +------------------+      |    |
| |                             |   | Signature Block  |      |    |
| |                             |   | Changed          |      |    |
| |                             |   +------------------+      |    |
| |                             |                             |    |
| |                             |   +------------------+      |    |
| |                             |   | New External Link|      |    |
| |                             |   | Detected         |      |    |
| |                             |   +------------------+      |    |
| +-----------------------------+-----------------------------+    |
| [Quick Approve]  [Open Full Review Details]                      |
+------------------------------------------------------------------+
```

**Table Columns**:
| Column | Content | Sortable | Filterable |
|--------|---------|----------|------------|
| Risk | L0-L4 badge | Yes | Yes |
| Status | Awaiting/Approved/Rejected | Yes | Yes |
| Artifact | Icon + truncated name | No | By type |
| Bead Title | Bead ID + title | Yes | No |
| Owner | User name | Yes | Yes |
| Time | Relative timestamp | Yes | By range |

**Diff Postcard (Quick Look)**:

- Side-by-side thumbnail comparison
- Callout annotations for key changes
- Maximum 3 annotations visible
- Click to expand to full detail view

**Actions**:

- `Quick Approve` - One-click with default rationale
- `Open Full Review Details` - Navigate to Artifact Detail
- Row click - Toggle Diff Postcard

### 2.4 Screen 4: Artifact Detail

**Purpose**: Full evidence review with approval decision

```
+------------------------------------------------------------------+
|  GuardSpine Artifact Detail: Bead #450 Legal Policy Update.pdf   |
+------------------------------------------------------------------+
| +------------------------+  +------------------------+  +-------+ |
| | Original (v1)          |  | Proposed (v2)          |  | Diff  | |
| |                        |  |                        |  | Annot | |
| | [Document content]     |  | [Document content]     |  | Evid  | |
| |                        |  | +------------------+   |  | Policy| |
| |                        |  | | HIGHLIGHTED      |   |  +-------+ |
| |                        |  | | CHANGE AREA      |   |            |
| |                        |  | +------------------+   |  | Page 2: | |
| |                        |  |                        |  | Sig mod | |
| |                        |  |                        |  |         | |
| |                        |  |                        |  | Page 2: | |
| |                        |  |                        |  | Ext link| |
| +------------------------+  +------------------------+  +---------+ |
|                                                                    |
| +--------------------------------------------------------------+ |
| | AI Suggestion: This change requires L3 approval due to        | |
| | external link.                                                 | |
| +--------------------------------------------------------------+ |
|                                                                    |
| +--------------------------------------------------------------+ |
| | Policy Checklist                                               | |
| | [X] Rule: External Links Detected (Requires L3) - FIRED       | |
| +--------------------------------------------------------------+ |
|                                                                    |
| Sarah Jones replied: "Looks correct, but please confirm..."      |
| [Comment box]                                                     |
|                                                                    |
|                                        [Approve]  [Reject]        |
+------------------------------------------------------------------+
```

**Left Panel - Document Comparison**:

- Original (v1) rendered view
- Proposed (v2) rendered view with change highlights
- Synchronized scrolling
- Zoom controls

**Right Panel - Context Tabs**:
| Tab | Content |
|-----|---------|
| Diff | Change summary, line-by-line if code |
| Annotations | AI annotations, reviewer comments |
| Evidence | Bundle contents, hashes, signatures |
| Policy | Policy pack, rules evaluated, results |

**AI Suggestion Panel**:

- Model-generated explanation of risk tier
- Never authoritative - "suggestion" framing
- Link to policy rule that triggered

**Policy Checklist**:

- All evaluated rules
- FIRED / PASSED status
- Click to see rule definition

**Comment Thread**:

- Threaded discussion
- Mention support (@user)
- Timestamped

**Decision Actions**:
| Action | Behavior |
|--------|----------|
| Approve | Opens rationale modal, creates signed approval event |
| Reject | Opens rationale modal with required reason |
| Request Changes | Opens comment box, notifies owner |

---

## Part 3: Data Model Enhancements

### 3.1 Evidence Bundle Schema

```python
class EvidenceBundle(BaseModel):
    """Court-admissible evidence bundle."""
    bundle_id: str
    created_at: datetime

    # Evidence Scope (what is asserted)
    scope: EvidenceScope

    # Artifacts
    artifacts: list[BundleArtifact]

    # Diff Metadata (deterministic)
    diff_metadata: DiffMetadata

    # Signatures
    signatures: list[BundleSignature]

    # Retention
    retention: RetentionPolicy

    # Verification
    verification: VerificationInfo

class EvidenceScope(BaseModel):
    """What this bundle asserts."""
    assertion_type: str  # "change_approval", "version_snapshot", "audit_evidence"
    assertion_text: str  # Human-readable
    bead_id: str
    artifact_ids: list[str]
    from_version: str
    to_version: str
    approval_decision: Optional[str]  # "approved", "rejected"

class DiffMetadata(BaseModel):
    """Deterministic diff information."""
    algorithm: str  # "semantic_diff_v1", "line_diff", "visual_diff"
    algorithm_version: str
    content_hash_before: str
    content_hash_after: str
    change_regions: list[ChangeRegion]
    deterministic: bool = True  # Always true for ground truth

class ChangeRegion(BaseModel):
    """A detected change area."""
    region_id: str
    location: str  # "page:2:para:3" or "line:45-52"
    change_type: str  # "addition", "deletion", "modification"
    content_hash: str
    # AI annotation (suggestion only)
    ai_annotation: Optional[AIAnnotation]

class AIAnnotation(BaseModel):
    """Model-generated annotation (not ground truth)."""
    model_id: str
    annotation_type: str  # "risk_flag", "summary", "highlight"
    confidence: float
    text: str
    is_suggestion: bool = True  # Always true

class BundleSignature(BaseModel):
    """Cryptographic signature."""
    signer_id: str
    signer_identity: SignerIdentity
    signature_algorithm: str
    signature: str
    signed_at: datetime
    key_id: str

class SignerIdentity(BaseModel):
    """Verified signer identity."""
    type: str  # "user", "service", "system"
    identifier: str  # email, service account
    display_name: str
    identity_provider: str  # "okta", "entra", "internal"
    verified: bool

class RetentionPolicy(BaseModel):
    """Retention and legal hold configuration."""
    retention_class: str  # "standard", "legal_hold", "regulatory"
    retention_days: int
    legal_hold_id: Optional[str]
    delete_after: Optional[datetime]
    immutable: bool

class VerificationInfo(BaseModel):
    """Offline verification support."""
    verification_url: str
    offline_verifiable: bool
    verification_script_hash: str
    public_key_pem: str
```

### 3.2 Approval Event Schema

```python
class ApprovalEvent(BaseModel):
    """Signed approval decision event."""
    event_id: str
    event_type: str  # "approval_granted", "approval_denied", "changes_requested"
    created_at: datetime

    # Reference
    approval_id: str
    bead_id: str
    artifact_id: str
    bundle_id: str

    # Decision
    decision: ApprovalDecision

    # Signature (non-repudiation)
    signature: BundleSignature

class ApprovalDecision(BaseModel):
    """The actual decision with rationale."""
    result: str  # "approved", "rejected", "changes_requested"
    rationale: str
    conditions: list[str]

    # Reviewer info
    reviewer_id: str
    reviewer_role: str

    # What was reviewed
    reviewed_scope: EvidenceScope

    # Policy alignment
    policy_pack_id: str
    rules_evaluated: list[RuleResult]

class RuleResult(BaseModel):
    """Result of a policy rule evaluation."""
    rule_id: str
    rule_name: str
    fired: bool
    severity: str
    details: str
```

---

## Part 4: Integration Architecture

### 4.1 Integration Priority Order

```
Phase 1 (MVP Launch):
  1. SSO + SCIM (Okta/Entra) - Identity foundation
  2. ServiceNow or Jira - Workflow anchor
  3. Microsoft 365 or Google Drive - Document universe
  4. GitHub - Code lane credibility

Phase 2 (Enterprise Expansion):
  5. Slack/Teams - Approval nudges
  6. GRC export (ServiceNow GRC / Archer / OneTrust)
  7. DLP/CASB signals (Purview/Netskope)

Phase 3 (Full Platform):
  8. Additional document systems (Box, Confluence)
  9. Analytics export (Power BI, Tableau)
  10. Vendor intake systems
```

### 4.2 Integration Object Mapping

```yaml
identity_systems:
  okta:
    auth: SAML/OIDC
    provisioning: SCIM
    role_mapping: Groups -> GuardSpine roles

  entra_id:
    auth: SAML/OIDC
    provisioning: SCIM
    role_mapping: Azure AD groups -> GuardSpine roles

workflow_systems:
  servicenow:
    object_model:
      artifact: Attachment / CMDB CI
      version: sysmod_created
      change_event: sys_audit
    integration:
      - Create/update approval tasks
      - Push status (approved/rejected/exported)
      - Link bead IDs in tickets
    api: REST API v2

  jira:
    object_model:
      artifact: Attachment
      version: Version field
      change_event: Changelog
    integration:
      - Create approval subtasks
      - Update custom fields
      - JQL for queries
    api: REST API v3

document_systems:
  microsoft_365:
    sharepoint:
      artifact: DriveItem
      version: DriveItemVersion
      change_event: ActivityDelta
    integration:
      - Webhook for changes
      - Download content snapshots
      - Write approval status as metadata
    api: Microsoft Graph API

  google_drive:
    artifact: File
    version: Revision
    change_event: Changes API
    integration:
      - Push notifications
      - Export content
      - Custom properties for status
    api: Drive API v3

code_systems:
  github:
    artifact: File (blob)
    version: Commit SHA
    change_event: Push / PR events
    integration:
      - Status checks on PRs
      - Block merge on L3/L4
      - Attach SARIF artifacts
    api: GitHub REST + GraphQL

signal_sources:
  microsoft_purview:
    signals:
      - PII detected
      - Sensitive labels
      - External sharing
    integration: Activity API polling

  netskope:
    signals:
      - DLP violations
      - Cloud app usage
      - Data exposure
    integration: Webhook / API
```

### 4.3 API Design (Pristine)

```yaml
# Core API Contract

/api/v1/search:
  GET:
    params: q, type, lane, from, to, limit
    returns: SearchResults

/api/v1/artifacts:
  GET:
    params: kind, risk_tier, limit, cursor
    returns: PaginatedArtifacts
  GET /{id}:
    returns: Artifact with versions
  GET /{id}/diff/{from_version}/{to_version}:
    returns: DeterministicDiff

/api/v1/approvals:
  GET:
    params: status, risk_tier, lane, limit, cursor
    returns: PaginatedApprovals
  GET /{id}:
    returns: Approval with history
  POST /{id}/decisions:
    body: ApprovalDecision
    returns: SignedApprovalEvent

/api/v1/bundles:
  GET:
    params: artifact_id, integrity_status, limit, cursor
    returns: PaginatedBundles
  GET /{id}:
    returns: Bundle with verification info
  POST /{id}/verify:
    returns: VerificationResult
  GET /{id}/export:
    params: format (json, zip, pdf)
    returns: ExportedBundle

/api/v1/beads:
  GET:
    params: status, owner, blocked, limit, cursor
    returns: PaginatedBeads
  GET /{id}:
    returns: Bead with artifacts
  GET /{id}/graph:
    returns: DependencyGraph

# Integration webhooks
/api/v1/webhooks:
  POST /github:
    handles: push, pull_request, check_run
  POST /servicenow:
    handles: incident, change_request
  POST /jira:
    handles: issue_created, issue_updated
```

---

## Part 5: Implementation Phases

### Phase 1: Core Platform (Current Sprint)

**Goal**: Approval inbox + Work graph as primary product

```
Week 1-2:
  [x] FastAPI backend with Beads integration
  [x] Dashboard with real API calls
  [x] Approvals list and detail pages
  [x] Work Graph with React Flow
  [x] Artifacts list

Week 3-4:
  [ ] Enhanced Dashboard (treemap, event volume charts)
  [ ] Diff Postcard component
  [ ] Evidence bundle generation
  [ ] Basic signing infrastructure
```

### Phase 2: Evidence & Verification

**Goal**: Defensible evidence bundles with offline verification

```
Week 5-6:
  [ ] Evidence bundle schema implementation
  [ ] Deterministic diff engine
  [ ] Bundle signing with key management
  [ ] Offline verification tooling
  [ ] Retention policy configuration

Week 7-8:
  [ ] Policy checklist UI
  [ ] AI suggestion integration (model as annotator)
  [ ] Comment threads on approvals
  [ ] Export formats (JSON, ZIP, PDF)
```

### Phase 3: Integration Layer

**Goal**: SSO + first workflow integration

```
Week 9-10:
  [ ] Okta/Entra SSO integration
  [ ] SCIM user provisioning
  [ ] Role mapping configuration

Week 11-12:
  [ ] ServiceNow or Jira integration
  [ ] Webhook event processing
  [ ] Bidirectional status sync
```

### Phase 4: Document Intelligence

**Goal**: Microsoft 365 or Google Drive integration

```
Week 13-14:
  [ ] SharePoint/OneDrive or Google Drive connector
  [ ] Version tracking and change detection
  [ ] Content snapshot for diffing

Week 15-16:
  [ ] Visual diff for PDFs/images
  [ ] Table extraction for spreadsheets
  [ ] Watermarking and redaction support
```

---

## Part 6: Success Metrics

### 6.1 Product Metrics

| Metric                          | Target        | Rationale           |
| ------------------------------- | ------------- | ------------------- |
| Approval throughput             | 10 sec median | UX Lead requirement |
| Evidence bundle generation      | < 5 sec       | Compliance need     |
| Offline verification success    | 100%          | Legal requirement   |
| False positive rate (risk tier) | < 5%          | CISO trust          |

### 6.2 Adoption Metrics

| Metric                    | Phase 1 Target | Phase 2 Target            |
| ------------------------- | -------------- | ------------------------- |
| Active approvers          | 10+            | 50+                       |
| Governed artifacts        | 100+           | 1000+                     |
| Integrations active       | 1 (SSO)        | 3 (SSO + workflow + docs) |
| Evidence bundles exported | 50+            | 500+                      |

### 6.3 Compliance Metrics

| Metric                 | Target        | Evidence               |
| ---------------------- | ------------- | ---------------------- |
| Audit preparation time | 50% reduction | Bundle export logs     |
| Control coverage       | 95%+          | Coverage dashboard     |
| Retention compliance   | 100%          | Retention policy audit |

---

## Appendix A: Technology Stack

```yaml
frontend:
  framework: React 19 + TypeScript
  state: TanStack Query
  routing: React Router 7
  visualization:
    - React Flow (work graph)
    - Recharts (charts)
    - react-diff-viewer-continued (diffs)
  ui: Tailwind CSS 4 + Radix UI

backend:
  framework: FastAPI
  database: SQLite (dev) -> PostgreSQL (prod)
  cache: Redis
  queue: Celery (background tasks)

integrations:
  auth: Okta SDK, MSAL (Entra)
  storage: S3/Azure Blob/GCS
  signing: PyNaCl / age encryption

beads:
  cli: bd.exe
  storage: JSONL files
  events: guard_events.jsonl
```

## Appendix B: Risk Tier Definitions

| Tier | Auto-approve | SLA | Required Approver    |
| ---- | ------------ | --- | -------------------- |
| L0   | Yes          | -   | System               |
| L1   | Yes          | 72h | System               |
| L2   | Yes          | 24h | Any reviewer         |
| L3   | No           | 8h  | Domain expert        |
| L4   | No           | 4h  | Multiple + executive |

## Appendix C: Expert Council Contact Points

For each integration, identify:

1. **Champion**: Compliance ops (wants reduced audit prep)
2. **Blocker**: IT/change management (fears disruption)
3. **Strategy**: Start with one artifact class (PDF or XLSX)

---

_Document Version: 3.0_
_Last Updated: 2026-01-19_
_Status: Living Specification_
