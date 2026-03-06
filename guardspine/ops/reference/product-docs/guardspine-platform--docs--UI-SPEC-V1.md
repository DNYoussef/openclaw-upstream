# GuardSpine UI Specification v1.0

> **Strategic Positioning**: This is not a document tool, not an AI audit tool.
> This is a **control surface for AI-mediated work**.

## View Naming Convention (Enterprise Language)

| Internal Name       | Enterprise Name      | Purpose                    |
| ------------------- | -------------------- | -------------------------- |
| Artifact Detail     | **Evidence View**    | Trust calibration surface  |
| Approval Inbox      | **Decision View**    | Approval bottleneck killer |
| Work Graph          | **Control View**     | Governance causality map   |
| Executive Dashboard | **Risk & Flow View** | Board/CISO-level oversight |

---

## Screen 1: Evidence View (Artifact Detail)

### Purpose

Answers: _"What changed, where, and why do I care?"_ in seconds.

### Core Components

| Component           | Description                                 | Data Source             |
| ------------------- | ------------------------------------------- | ----------------------- |
| Split Viewer        | Original (v1) vs Proposed (v2) side-by-side | `artifact_version_diff` |
| Anchored Highlights | Signature block, external link callouts     | `guard_event`s          |
| Tab Panel           | Diff / Annotations / Evidence / Policy      | Multiple                |
| AI Suggestion Card  | Scoped, specific, rule-tied recommendation  | `policy_fire` events    |
| Policy Checklist    | Rules fired with FIRED/PASSED status        | `policy_fire` events    |
| Comments Thread     | Reviewer comments with replies              | `review_comment`        |
| Action Bar          | Approve (green) / Reject (red)              | User action             |

### Enhancements (Reviewer Feedback)

| Enhancement                  | Rationale                                                         |
| ---------------------------- | ----------------------------------------------------------------- |
| **Evidence Scope Indicator** | "Diff computed from v1 -> v2 using deterministic PDF parser v0.9" |
| Parser version badge         | Auditors need to know _how_ diff was generated                    |

### Key Insight

> The PDF itself is not edited - overlays are derived from events. That's defensible.

---

## Screen 2: Decision View (Approval Inbox)

### Purpose

Lets approvers act without opening full documents. Approval bottleneck killer.

### Core Components

| Component        | Description                                     | Data Source        |
| ---------------- | ----------------------------------------------- | ------------------ |
| Inbox Table      | Risk, Status, Artifact, Bead Title, Owner, Time | `inbox_item`       |
| Expandable Row   | Quick Look preview                              | Accordion          |
| Diff Postcard    | 2 thumbnails + 2 callouts + 2 risk labels       | `derived_artifact` |
| Quick Approve    | Fast-path approval                              | User action        |
| Open Full Review | Link to Evidence View                           | Navigation         |

### Enhancements (Reviewer Feedback)

| Enhancement             | Rationale                                        |
| ----------------------- | ------------------------------------------------ |
| **SLA Countdown**       | Approval aging indicator (e.g., "2h remaining")  |
| **Required Role Badge** | Inline indicator: "Legal", "Security", "Finance" |

### Key Insight

> Visual AI becomes infrastructure, not a gimmick. Compressing multi-page legal docs into actionable postcards.

---

## Screen 3: Control View (Work Graph)

### Purpose

Answers: _"Why is my work blocked?"_ - the most expensive question in enterprises.

### Core Components

| Component        | Description                             | Data Source          |
| ---------------- | --------------------------------------- | -------------------- |
| Dependency Graph | Node graph with risk semantics          | `bead` relationships |
| Bead Nodes       | ID, Title, File Type icon, Status badge | `bead`               |
| Blocker Edge     | Red lock icon + "Blocked by #X"         | `gate_block`         |
| Detail Panel     | Owner, Risk Tier, Blocked By, Actions   | `bead` details       |

### Enhancements (Reviewer Feedback)

| Enhancement                | Rationale                                        |
| -------------------------- | ------------------------------------------------ |
| **Dependency Mode Toggle** | "Structural dependencies" vs "Governance blocks" |

### Key Insight

> This is a control-flow graph with risk semantics, not a task graph.
> Cross-artifact blocking (DOCX -> XLSX -> PDF) is rare and extremely valuable.

### Beads Alignment

- Nodes = Beads
- Edges = Dependencies / Blocks
- GuardSpine adds **policy-driven blocking** instead of just task dependencies

---

## Screen 4: Risk & Flow View (Executive Dashboard)

### Purpose

Board-level and CISO-level view. Answers: _"Are we governing AI-mediated work at scale?"_

### Core Components

| Component             | Description                                            | Data Source      |
| --------------------- | ------------------------------------------------------ | ---------------- |
| Risk Tier Queue       | Bar chart: L4 Critical (3), L3 High (12)               | `risk_summary`   |
| Top Risk Drivers      | Treemap: Signature 40%, Macros 25%, PII 20%, Links 15% | `risk_drivers`   |
| Governed Event Volume | Line chart by type (Code, PDF, XLSX, Image)            | `event_volume`   |
| Blocked Work          | Alert list of blocked beads                            | `blocked_beads`  |
| Coverage Health       | Gauge: 88% Governed                                    | `coverage_stats` |

### Enhancements (Reviewer Feedback)

| Enhancement            | Rationale                                      |
| ---------------------- | ---------------------------------------------- |
| **Ungoverned Changes** | "Ungoverned changes detected this week" metric |
| **AI vs Human Ratio**  | "AI-generated vs human-authored change ratio"  |

### Key Insight

> Showing **control coverage**, not just alerts/findings. This is strategic positioning.

---

## Technical Architecture

### Data Model Alignment

| UI Concept | Beads Entity | GuardSpine Extension         |
| ---------- | ------------ | ---------------------------- |
| Artifact   | `bead`       | `artifact_version`           |
| Change     | `bead_event` | `guard_event`                |
| Block      | `dependency` | `gate_block` + `policy_fire` |
| Approval   | `bead_state` | `approval_event`             |

### API Endpoints

```
# Evidence View
GET  /api/artifacts/:id/diff
GET  /api/artifacts/:id/events
GET  /api/artifacts/:id/policy
POST /api/artifacts/:id/approve
POST /api/artifacts/:id/reject
POST /api/artifacts/:id/comments

# Decision View
GET  /api/inbox
GET  /api/inbox/:id/postcard
POST /api/inbox/:id/quick-approve

# Control View
GET  /api/beads/graph
GET  /api/beads/:id
GET  /api/beads/:id/blocks
POST /api/beads/:id/unblock

# Risk & Flow View
GET  /api/dashboard/risk-summary
GET  /api/dashboard/risk-drivers
GET  /api/dashboard/event-volume
GET  /api/dashboard/blocked-work
GET  /api/dashboard/coverage
GET  /api/dashboard/ungoverned
GET  /api/dashboard/ai-human-ratio
```

---

## Color Palette (Dark Theme)

| Token                | Hex       | Usage          |
| -------------------- | --------- | -------------- |
| `--surface-primary`  | `#1a1a2e` | Background     |
| `--surface-elevated` | `#16213e` | Cards          |
| `--border-subtle`    | `#2d3748` | Borders        |
| `--risk-l4-critical` | `#e63946` | L4 Critical    |
| `--risk-l3-high`     | `#f4a261` | L3 High        |
| `--risk-l2-medium`   | `#e9c46a` | L2 Medium      |
| `--risk-l1-low`      | `#2a9d8f` | L1 Low         |
| `--success`          | `#10b981` | Approved       |
| `--accent`           | `#4cc9f0` | Interactive    |
| `--text-primary`     | `#ffffff` | Primary text   |
| `--text-secondary`   | `#a8a8a8` | Secondary text |

---

## Competitive Differentiation

### Why Competitors Will Fail

| Their Assumption            | Our Assumption           |
| --------------------------- | ------------------------ |
| Artifacts are files         | Artifacts are events     |
| Git-centric mental model    | Event-native model       |
| Humans must read everything | Humans review exceptions |
| Document storage matters    | Control flow matters     |

### Strategic Positioning

> "Humans review _exceptions_, not content.
> Evidence is _derived_, not authored.
> Control flow matters more than file storage."

---

## MVP Scope

Ship only these four views:

1. **Decision View** (Approval Inbox)
2. **Evidence View** (Artifact Diff)
3. **Control View** (Work Graph)
4. **Risk & Flow View** (Executive Dashboard)

This alone beats most governance vendors who cannot replicate without re-architecting.

---

## Library Reuse Summary

### Direct Copy (~40%)

- `ui/design_system/*` - Card, Badge, MetricCard, Input
- `ui/radix_dialog/*` - Modal dialogs
- `http/api_services/*` - API client patterns
- `state/kanban_store/*` - State management patterns

### New Components (~60%)

- React Flow graph components
- Recharts dashboard charts
- Diff viewer with overlays
- Postcard preview component

---

_Document created: 2026-01-19_
_Version: 1.0_
_Status: Ready for implementation_
