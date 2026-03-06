# Beads Integration Guide for GuardSpine

## Overview

GuardSpine is built on top of **Beads** (Steve Yegge's atomic work item system). This document captures the compatibility requirements and integration architecture.

**Beads Repository**: https://github.com/steveyegge/beads
**Local CLI**: `C:\Users\17175\AppData\Local\beads\bd.exe`

---

## What is Beads?

Beads is a lightweight issue tracker with first-class dependency support, using Git as the underlying storage mechanism:

- **Storage**: JSONL files in `.beads/` directory
- **IDs**: Hash-based format `bd-a1b2` preventing merge collisions
- **Hierarchy**: Epic -> Task -> Sub-task (`bd-a3f8.1.1`)
- **Sync**: Background daemon for auto-synchronization

---

## Beads Data Model

### Core Properties

```typescript
interface BeadsTask {
  id: string; // e.g., "bd-a1b2" or "task-001"
  description: string;
  status: "pending" | "in_progress" | "completed" | "blocked";
  created_at: string; // ISO8601
  updated_at: string;
  metadata: TaskMetadata;
}

interface TaskMetadata {
  scope: "internal" | "external"; // external = +1 risk
  reversible: boolean; // false = +1 risk
  domain: string; // security/payments/etc
  files: string[]; // linked file paths
  tags: string[]; // critical, production, pii
}
```

### Dependency Types

| Type         | Visual      | Meaning               |
| ------------ | ----------- | --------------------- |
| `depends_on` | Gray arrow  | Structural dependency |
| `blocks`     | Red dashed  | Governance block      |
| `related`    | Dotted gray | Informational link    |

---

## GuardSpine Extensions

GuardSpine wraps Beads with governance concepts:

### 1. GuardEvent (`.beads/guard_events.jsonl`)

```python
@dataclass
class GuardEvent:
    event_type: str        # AUDIT_STARTED, APPROVAL_REQUESTED, etc.
    bead_id: str           # Links to parent bead
    correlation_id: str    # Groups related events
    artifact: dict         # {kind, title, locator}
    integrity: dict        # {file_hash, diff_hash}
    occurred_at: str
    event_id: str          # evt_{uuid}
    actor: dict            # {type: "ai"|"human", id}
    refs: dict             # External references
    outputs: dict          # Audit outputs
    risk_tier: str         # L0-L4
```

### 2. Risk Tier Calculation

Base tier from audit level, adjusted by task context:

| Factor             | Adjustment | Example             |
| ------------------ | ---------- | ------------------- |
| `scope=external`   | +1         | External-facing API |
| `reversible=false` | +1         | Database migration  |
| `domain=security`  | +1         | Auth code           |
| `domain=payments`  | +2         | Payment processing  |
| `tags=[critical]`  | +1         | Production code     |

**Domain Risk Mappings**:

```python
DOMAIN_RISK_LEVELS = {
    "security": 1,
    "authentication": 1,
    "authorization": 1,
    "payments": 2,
    "billing": 2,
    "financial": 2,
    "pii": 2,
    "compliance": 2,
    "infrastructure": 1,
    "deployment": 1,
    "database": 1,
}
```

### 3. Approval Workflow

```
L0-L2: Auto-approve (AI can proceed)
L3:    Review queue (human glances)
L4:    Explicit approval required
```

**Approval States**: pending -> approved | rejected | expired

---

## CLI Commands (bd.exe)

### Essential Commands for GuardSpine

```bash
# List ready tasks (no blocking dependencies)
bd ready

# Get task by ID
bd show <id>

# Create task with priority
bd create "Title" -p 0

# Manage dependencies
bd dep add <child> <parent>
bd dep list <id>

# View dependency graph
bd graph

# Search tasks
bd search "query"

# Export to JSONL
bd export --format jsonl

# Sync with remote
bd sync
```

### JSON Output Mode

```bash
bd list --json             # Machine-readable output
bd show <id> --json        # Task details as JSON
```

---

## File Structure

```
.beads/
  beads.db           # SQLite cache (query optimization)
  beads.jsonl        # Authoritative task data (Git-tracked)
  guard_events.jsonl # GuardSpine events (Git-tracked)
  tasks.jsonl        # Alternative format used by reader.py
```

---

## Backend API Requirements

### Beads-Compatible Endpoints

| Endpoint                | Beads Data Source     | Purpose          |
| ----------------------- | --------------------- | ---------------- |
| `GET /beads`            | `bd list --json`      | List all beads   |
| `GET /beads/{id}`       | `bd show {id} --json` | Bead details     |
| `GET /beads/{id}/graph` | `bd graph`            | Dependency graph |
| `GET /beads?ready=true` | `bd ready --json`     | Ready tasks only |

### GuardSpine-Extended Endpoints

| Endpoint                         | Data Source                   | Purpose            |
| -------------------------------- | ----------------------------- | ------------------ |
| `GET /approvals`                 | `.codeguard/approvals/*.json` | Approval queue     |
| `GET /approvals/{id}`            | Single approval file          | Approval detail    |
| `POST /approvals/{id}/decisions` | Update approval               | Approve/reject     |
| `GET /dashboard/summary`         | Aggregated metrics            | KPIs               |
| `GET /artifacts`                 | `.beads/guard_events.jsonl`   | Governed artifacts |
| `GET /bundles`                   | Evidence bundle storage       | Audit evidence     |

---

## Frontend Component Mapping

### Beads -> UI View

| Beads Concept | GuardSpine View | Page              |
| ------------- | --------------- | ----------------- |
| Task list     | Work Spine      | `/work-graph`     |
| Task detail   | Bead Detail     | `/beads/:id`      |
| Dependencies  | Control Graph   | React Flow canvas |
| Ready tasks   | Dashboard KPI   | `/`               |
| Blocked tasks | Dashboard KPI   | `/`               |

### GuardEvent -> UI View

| Event Type           | UI Location       |
| -------------------- | ----------------- |
| `AUDIT_STARTED`      | Artifact timeline |
| `APPROVAL_REQUESTED` | Approval inbox    |
| `APPROVAL_GRANTED`   | Decision history  |
| `BUNDLE_CREATED`     | Evidence library  |

---

## Integration Checklist

### Backend

- [ ] FastAPI app at `D:\Projects\GuardSpine\backend\`
- [ ] Beads CLI wrapper (`bd.exe` subprocess calls)
- [ ] JSONL reader for guard_events
- [ ] Approval workflow integration
- [ ] WebSocket for real-time events

### Frontend

- [x] React scaffold with routing
- [x] API client with typed endpoints
- [ ] Dashboard with real data
- [ ] React Flow graph for beads
- [ ] Approval detail with decision actions
- [ ] Artifact diff viewers (code/pdf/sheet/image)

---

## Data Flow

```
User Request
     |
     v
Frontend (React)
     |
     | HTTP/WebSocket
     v
Backend (FastAPI)
     |
     +---> bd.exe CLI ---> .beads/beads.jsonl
     |
     +---> Reader.py ---> .beads/guard_events.jsonl
     |
     +---> Workflow.py ---> .codeguard/approvals/
     |
     v
Response (JSON)
```

---

## Next Steps

1. **Create FastAPI backend** at `backend/` with:
   - Beads CLI integration
   - JSONL readers
   - Approval endpoints
   - WebSocket events

2. **Implement real API calls** in frontend:
   - Replace mock data
   - Add TanStack Query for caching
   - WebSocket subscription

3. **Build React Flow graph**:
   - Fetch beads and dependencies
   - Render as interactive graph
   - Color by status/risk tier

---

_Document created: 2026-01-19_
_Source: Beads repo + GuardSpine codebase analysis_
