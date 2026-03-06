# GuardSpine Strategic Analysis

> Synthesized from: PDF deck, ChatGPT strategic conversation, OWASP 7-layer model, and codebase audit

---

## Executive Summary

**What GuardSpine Is:**
The "missing middle" between process controls and semantic review - implementing OWASP layers 3-7 for ALL artifact types (code, PDF, sheets, images) with offline-verifiable evidence bundles.

**The Wedge:**
"PR approval is not evidence. GuardSpine turns review into verifiable evidence."

**Current State:**

- Frontend: 89% complete
- Backend: 84% complete
- Evidence System: 100% complete
- Rubrics: 11 YAML packs (106+ rules)

**Critical Gap:**
Approve/Reject workflow with messaging + Slack integration + Nomotic Mode v1

---

## 1. OWASP 7-Layer Mapping

The OWASP AI Exchange defines 7 protection layers for agentic AI. GuardSpine implements layers 3-7:

| #   | OWASP Layer                | GuardSpine Feature                           | Status    | Gap                           |
| --- | -------------------------- | -------------------------------------------- | --------- | ----------------------------- |
| 1   | Model Alignment            | Out of scope (upstream)                      | N/A       | -                             |
| 2   | Prompt Injection Defense   | Out of scope (upstream)                      | N/A       | -                             |
| 3   | **Human Oversight**        | Approval Inbox, Diff Postcards               | 89%       | Reject-with-reason loop       |
| 4   | **Automated Oversight**    | Rubrics, Risk Tiers (L0-L4), SARIF           | 84%       | Theater detection integration |
| 5   | **User-Based Privilege**   | CODEOWNERS, role-based approvers             | Partial   | Authority mapping UI          |
| 6   | **Intent-Based Privilege** | Nomotic authority_basis, constraints_applied | Planned   | nomotic-core.yaml             |
| 7   | **Just-In-Time Auth**      | Stop-the-line enforcement, merge gating      | Code only | Docs/sheets/images            |

**Competitive Advantage:** Only GuardSpine covers ALL artifact types with semantic governance.

---

## 2. Competitor Analysis (The Missing Middle)

| Competitor       | Process Controls | Code Governance | Signature Auth | Data Movement | **Semantic Artifact Governance** |
| ---------------- | ---------------- | --------------- | -------------- | ------------- | -------------------------------- |
| Vanta/ServiceNow | Yes              | No              | No             | No            | **No**                           |
| GitHub           | No               | Yes             | Yes            | No            | **No**                           |
| DocuSign         | No               | No              | Yes            | No            | **No**                           |
| DLP/Purview      | No               | No              | No             | Yes           | **No**                           |
| **GuardSpine**   | **Yes**          | **Yes**         | **Yes**        | **Yes**       | **Yes**                          |

**The Gap:** "Who authorized the semantic shift in the Q3 model?"

- Only GuardSpine can answer this across ALL artifact types.

---

## 3. Feature Requirements (Prioritized)

### Phase 1: Critical Path (Days 1-7) - "Approver Lives Here"

#### 3.1 Approve/Reject with Message API

**Priority: P0 - Blocking**

```python
# Required Events
APPROVAL_REQUESTED = "approval_requested"
APPROVED = "approved"
REJECTED = "rejected"  # MUST include reason
REVISION_SUBMITTED = "revision_submitted"
REAPPROVAL_REQUESTED = "reapproval_requested"

# State Machine
# Pending -> Approved (unblocks)
# Pending -> Rejected (blocks + requires revision)
# Rejected -> Revision Submitted -> Pending (new cycle)
```

**API Endpoints:**

```
POST /api/approvals/{id}/approve
  body: { message?: string, signature?: string }

POST /api/approvals/{id}/reject
  body: { message: string (REQUIRED), reason_category?: enum, signature?: string }
```

**Data Model:**

```python
class ApprovalRequest:
    id: str
    artifact_refs: List[str]
    bundle_ref: str
    risk_level: int  # L0-L4
    rubric_id: str
    required_roles: List[str]
    requester: str
    created_at: datetime

class ApprovalDecision:
    decision: Literal["approve", "reject"]
    message: str  # Required if reject
    actor: str
    timestamp: datetime
    signature: Optional[str]
```

#### 3.2 Slack Interactive Messages

**Priority: P0 - Adoption lever**

```json
{
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*L3 Review Required*\n:warning: External link + signature block changed"
      }
    },
    {
      "type": "section",
      "fields": [
        { "type": "mrkdwn", "text": "*Risk Tier:* L3 (High)" },
        { "type": "mrkdwn", "text": "*Artifact:* contract-v2.pdf" }
      ]
    },
    {
      "type": "actions",
      "elements": [
        { "type": "button", "text": "View Diff", "url": "..." },
        { "type": "button", "text": "Approve", "style": "primary", "action_id": "approve" },
        { "type": "button", "text": "Reject", "style": "danger", "action_id": "reject" }
      ]
    }
  ]
}
```

**On Reject:** Open modal requiring reason + route back to author.

#### 3.3 Reject Routes Back to Author

**Priority: P0 - Closes the loop**

Author receives notification in:

- GitHub PR comment (for code)
- Slack DM/thread reply
- GuardSpine inbox
- Email fallback

Message format:

```
GuardSpine: Changes Requested (L3)
By: Alex Chen (Security)
Reason: External API call added without allowlist + missing tests.
Required: Add tests + document allowlist justification.
[Open Diff] [Resubmit: push new commit]
```

---

### Phase 2: Evidence Completeness (Days 8-14)

#### 3.4 Postcard Schema Normalization

All 4 lanes must produce consistent postcard JSON:

```python
class PostcardSchema:
    artifact_id: str
    artifact_type: Literal["code", "pdf", "xlsx", "image"]
    version_from: str
    version_to: str
    summary: str  # Human-readable
    risk_tier: int
    risk_drivers: List[RiskDriver]
    changes: List[Change]  # Type-specific
    ai_suggestions: List[AISuggestion]

class RiskDriver:
    category: str  # "auth", "payments", "pii", "external_link"
    description: str
    weight: int
```

**Per-Lane Changes:**

- **Code:** file paths, line ranges, patterns matched
- **PDF:** pages changed, clauses altered, signatures, external links
- **Sheet:** sheets touched, formulas changed, external connections
- **Image:** pixel diff regions, object tags, bounding boxes

#### 3.5 Auditor Pack Export

```
GET /api/bundles/export?from=2025-01-01&to=2025-01-31&risk=L3,L4
```

Output: ZIP containing:

```
auditor-pack-2025-01/
  index.html          # Summary report
  index.json          # Machine-readable
  bundles/
    bundle-001.json
    bundle-002.json
    ...
  artifacts/
    diffs/
    postcards/
  verification/
    verify-instructions.md
    guardspine-verify (binary)
```

#### 3.6 Search + Filters + Alerts

**Search API:**

```
GET /api/search?q=payment&type=code,pdf&risk=L3,L4&from=2025-01-01&to=2025-01-31
```

**Unmanaged Change Detection:**

- Detect commits/changes without matching bundles
- Fire "UNMANAGED_CHANGE" event
- Alert via configured channels

---

### Phase 3: Nomotic Mode (Days 15-21)

#### 3.7 nomotic-core.yaml Implementation

```yaml
name: nomotic-core
version: "1.0"
description: "Nomotic AI governance rules - direct citations only"
partner: "Nomotic AI (Chris Hood)"

bundle_extensions:
  - authority_basis # Who has the right to approve
  - constraints_applied # What rules fired
  - interrupts_triggered # What stop-the-line events occurred

rules:
  # Authority Layer
  - id: NOM-001
    name: explicit_authority
    description: "All approvals must cite authority basis"
    required_field: authority_basis

  - id: NOM-002
    name: interrupt_rights
    description: "Certain conditions trigger mandatory human review"
    triggers:
      - external_link_added
      - signature_changed
      - financial_formula_changed
      - liability_clause_altered

  - id: NOM-003
    name: governed_adaptation
    description: "Changes to rubrics require multi-party approval"
    artifact_pattern: "rubrics/*.yaml"
    required_approvers: ["policy_owner", "security_reviewer"]
```

**Partner Control:** All Nomotic references are direct citations. No AI summarization of rules.

#### 3.8 Governed Adaptation Workflow

Changes to rubrics/policies are themselves governed:

1. PR to rubrics/ directory triggers L4
2. Requires policy_owner + security_reviewer approval
3. Creates evidence bundle for the governance change
4. Versioned with changelog

---

### Phase 4: Multi-Artifact (Days 22-30)

#### 3.9 Board Packet Workflow

**Trigger:** `.ready-for-review` marker on Beads task containing:

- Slide deck (PPT/PDF)
- KPI spreadsheet (XLSX)
- Appendix documents (PDF)

**Flow:**

1. Marker triggers GuardSpine audit on all linked artifacts
2. Each artifact gets Diff Postcard + risk tier
3. L3/L4 items added to approval queue
4. `.ready-for-board` blocked until all approvals complete
5. Export: "Board Packet Evidence Pack"

**Example Timeline (from PDF p5):**

```
9:14 AM - ImageGuard: External link on Slide 12 -> Blocked until L3 Review
10:47 AM - SheetGuard: 14 formula changes -> Finance Authority Rule Fires
2:15 PM - PDFGuard: Liability clause change -> General Counsel Interrupt
4:30 PM - All conditions met -> Board Packet Finalized, Bundle Exported
```

---

## 4. Quality Thresholds

### 4.1 Kill Criteria (30-day pilot)

| Metric                       | Threshold   | Action if Failed                                  |
| ---------------------------- | ----------- | ------------------------------------------------- |
| Median L3/L4 approval time   | > 5 minutes | UX friction - simplify workflow                   |
| False positive rate on L3/L4 | > 20%       | Noise killing adoption - tune rules               |
| Auditor pack requests        | Zero        | Evidence value not resonating - pivot positioning |

### 4.2 North Star Metrics (weekly tracking)

| Metric              | Definition                          |
| ------------------- | ----------------------------------- |
| Activation          | % repos where action ran on >=3 PRs |
| Governed Throughput | # PRs with bundles/week             |
| Escalation Quality  | L3/L4 rate + override rate          |
| Speed               | Median time-to-approve for L3/L4    |
| Trust Proof         | # times verifier is run             |

### 4.3 Six Sigma Quality Gates

From existing rubrics:

- DPMO < 6,210 (4 Sigma minimum)
- NASA Compliance >= 95%
- MECE Score >= 80%
- Theater Risk < 20%
- Critical Violations = 0

---

## 5. Testing Requirements

### 5.1 Golden Demo Smoke Tests

```bash
# Must pass before any new work
pytest tests/ -k "test_pipeline and test_bundle"

# Manual verification
1. Create PR touching auth code
2. Verify Diff Postcard appears as PR comment
3. Verify risk tier is L3 or L4
4. Verify evidence bundle generated
5. Run: guardspine-verify bundle.zip
6. Confirm: INTEGRITY: VALID
```

### 5.2 Approval Loop Tests

```python
def test_reject_routes_to_author():
    # Create approval request
    response = client.post(f"/api/approvals/{id}/reject", json={
        "message": "Missing auth tests",
        "reason_category": "testing"
    })

    # Verify rejection recorded
    assert response.status_code == 200

    # Verify author notified (check notification service)
    notifications = get_notifications_for(original_author)
    assert any(n.type == "APPROVAL_REJECTED" for n in notifications)

    # Verify bundle updated
    bundle = get_bundle(approval.bundle_ref)
    assert any(e.type == "REJECTED" for e in bundle.events)
```

### 5.3 Evidence Completeness Tests

```python
def test_bundle_completeness():
    bundle = generate_bundle(artifact_id)

    # Required fields
    assert bundle.diff_hash is not None
    assert bundle.policy_version is not None
    assert bundle.approvals is not None
    assert bundle.prev_hash is not None  # Hash chain

    # Verify offline
    result = verify_bundle(bundle)
    assert result.integrity == "VALID"
    assert result.signature == "VERIFIED"
```

### 5.4 Integration Tests Matrix

| Integration         | Test                     | Status   |
| ------------------- | ------------------------ | -------- |
| GitHub Action       | PR comment appears       | Existing |
| GitHub Status Check | L4 blocks merge          | Existing |
| Slack               | Interactive message sent | **NEW**  |
| Slack               | Reject modal works       | **NEW**  |
| Google Drive        | Connector sync           | Existing |
| SharePoint          | Connector sync           | **NEW**  |

---

## 6. API Specification

### 6.1 Existing Endpoints (Verified)

```
GET  /api/health
GET  /api/beads
GET  /api/artifacts
GET  /api/diffs/{id}
GET  /api/events
GET  /api/policies
GET  /api/connectors
POST /api/webhooks
GET  /api/bundles/{id}
POST /api/auth/login
```

### 6.2 New Endpoints Required

```
# Approvals
GET  /api/approvals?status=pending|approved|rejected&risk=&assignee=
GET  /api/approvals/{id}
POST /api/approvals/{id}/approve
POST /api/approvals/{id}/reject

# Search
GET  /api/search?q=&type=&risk=&from=&to=

# Postcards (normalized)
GET  /api/postcards/{artifact_id}

# Export
GET  /api/bundles/export?from=&to=&filters=
GET  /api/bundles/{id}/export

# Slack Integration
POST /api/integrations/slack/interactive
POST /api/integrations/slack/events
```

---

## 7. UI Pages Audit

### 7.1 Existing Pages (from codebase)

| Page            | File                   | Status                       |
| --------------- | ---------------------- | ---------------------------- |
| Home/Dashboard  | HomePage.tsx           | Exists                       |
| Approvals Inbox | ApprovalsPage.tsx      | Exists                       |
| Approval Detail | ApprovalDetailPage.tsx | **Needs reject-with-reason** |
| Work Graph      | WorkGraphPage.tsx      | Exists                       |
| Bead Detail     | BeadDetailPage.tsx     | Exists                       |
| Artifact Detail | ArtifactDetailPage.tsx | Exists                       |
| Bundle Detail   | BundleDetailPage.tsx   | Exists                       |
| Policies        | PoliciesPage.tsx       | Exists                       |
| Policy Packs    | PolicyPacksPage.tsx    | Exists                       |
| Connectors      | ConnectorsPage.tsx     | Exists                       |
| Evidence        | EvidencePage.tsx       | Exists                       |
| Search          | SearchPage.tsx         | **Needs filters**            |
| Drift Alerts    | DriftAlertsPage.tsx    | Exists                       |

### 7.2 UI Gaps

1. **ApprovalDetailPage.tsx:** Add required message field on reject
2. **SearchPage.tsx:** Add risk tier, type, date range filters
3. **NEW:** Slack/Teams integration settings page
4. **NEW:** Nomotic Mode configuration page

---

## 8. Execution Checklist (for AI Agents)

### Pre-Flight Verification

```bash
# 1. Verify project structure
ls -la D:\Projects\GuardSpine\backend\app\routers\
ls -la D:\Projects\GuardSpine\frontend\src\pages\
ls -la D:\Projects\GuardSpine\rubrics\

# 2. Run existing tests
cd D:\Projects\GuardSpine
pytest tests/ -v

# 3. Verify evidence system
python -m codeguard --help
```

### Execution Order

1. [ ] Implement POST /api/approvals/{id}/reject with required message
2. [ ] Update ApprovalDetailPage.tsx with reject modal
3. [ ] Implement Slack interactive messages endpoint
4. [ ] Add Slack button handlers (approve/reject)
5. [ ] Implement reject notification routing to author
6. [ ] Normalize Postcard schema across all 4 lanes
7. [ ] Implement /api/bundles/export for auditor packs
8. [ ] Add search filters (risk, type, date)
9. [ ] Create nomotic-core.yaml rubric pack
10. [ ] Implement Board Packet workflow
11. [ ] Write integration tests for each new feature
12. [ ] Update documentation

---

## 9. Netflix Pilot Specification

### Scope

- 1 repo / 1 service directory
- 10-30 PRs/week
- 2-week duration

### Deliverables

1. GitHub Action installed + configured
2. Slack approval loop (Approve/Reject with reason)
3. Weekly PDF/HTML report
4. 3-5 "caught it early" examples
5. Auditor pack export demo

### Success Criteria

| Metric                | Target                     |
| --------------------- | -------------------------- |
| MTTD for risky diffs  | < 5 minutes                |
| Approval throughput   | > 10/hour for L3/L4        |
| False positive rate   | < 20%                      |
| Evidence completeness | 100% (all required fields) |

### Positioning

"Loss prevention at AI velocity - catch expensive drift fast, prove who approved what."

---

## 10. Unicorn Path Summary

1. **Own the Category:** "AI throughput -> audit debt"
2. **Daily Touch:** Embed where approvals happen (PR + Slack + email)
3. **Proof Flywheel:** Evidence bundles get forwarded internally
4. **Ecosystem Scale:** Open spec/verifier + packs + connectors
5. **Expand:** Code -> Board Packets -> All work artifacts

**The Moat:** Semantic artifact governance with offline-verifiable evidence across ALL artifact types.

---

_Generated: 2026-01-22_
_Sources: The_Architecture_of_AI_Accountability.pdf, ChatGPT strategic conversation, OWASP AI Exchange 7-layer model_
