# GuardSpine Code Architecture

> For agents that need to understand the codebase, service boundaries, and data flow.
> Repo: D:/Projects/openclaw-upstream (GitHub: openclaw-upstream)

---

## Repository Structure

```
openclaw-upstream/
  guardspine/                    # All GuardSpine services and config
    agents/                      # Agent system prompts and shared context
      SHARED-CONTEXT.md          # Injected into every agent's context window
      cmo-system-prompt.md       # CMO outreach drafting instructions
      content-system-prompt.md   # Content Director instructions
      update_all_agents.py       # Bulk agent config updater
    content/                     # Marketing and sales collateral
      GROWTH-ENGINE-SPEC.md      # PLG growth model and pricing
      case-study-pr29-caught-it.md
      linkedin-free-action-post.md
      partner-collateral-kit.md
    data/                        # Local data files
      evidence-packs/            # Sample evidence bundles
      migration.sql              # Database schema migrations
      outreach.db                # SQLite outreach prospect database
    decision-engine/             # S/G/O decision routing service
      router.py                  # HTTP server + classify + route logic
      Dockerfile
      OPTIMIZATION-SPEC.md       # DSPy module integration spec
      INTERACTION-ATLAS.md       # Full combinatorial decision space
      MIROFISH-INTEGRATION.md    # MiroFish OASIS adapter spec
      archetypes/                # Decision archetype definitions
      examples/                  # Example decision payloads
    extensions/                  # Browser and platform extensions
      gdrive/
      guardspine/
      n8n-pipeline/
    mirofish-sim/                # OASIS swarm simulation service
      app.py                     # Flask server with archetype endpoints
      Dockerfile
      archetypes/                # Simulation archetype configs
    n8n-workflows/               # Workflow definitions and import tools
      definitions/               # Workflow JSON files
      templates/                 # Workflow templates
      backups/                   # Pre-edit workflow backups
      importer/                  # One-shot workflow import service
      import-inline.py           # Inline workflow pusher
      import-workflow.py         # Workflow import script
      N8N-WORKFLOW-PLAN.md       # Workflow design document
      PMC-NODE-PATTERNS.md       # Psychological Motion Capture patterns
      WORKFLOW-AGENT-SPLIT.md    # What n8n does vs what agents do
    ops/                         # Business operations docs (from Desktop mirror)
      assessment/
      eric-prep/
      financial/
      investor/
      legal/
      reference/
      research/
      strategy/
      templates/
    scripts/                     # Operational scripts
      backup/
      dry-run/
      outreach/
      smoke/                     # Smoke test scripts
    skills/                      # Agent skill definitions
      content-drafter.md
      morning-brief.md
    soak-monitor/                # Health check cron service
      health-check.sh            # Shell script checking all services
      Dockerfile
    telemetry-api/               # Event logging + Postgres query proxy
      app.py                     # HTTP server (Python, stdlib only)
      Dockerfile
      TELEMETRY-EVENTS.md        # Event catalog (all event types)
    workspace/                   # Working documents and handoffs
      AGENTS.md
      BUSINESS.md
      ERRORS.md
      FEATURE-REQUESTS.md
      HANDOFF-TEMPLATE.md
      HEARTBEAT.md
      IDENTITY.md
      LEARNINGS.md               # CRITICAL: debugging lessons, check before fixing anything
      MEMORY.md
      PATTERNS.md
      SOUL.md
      TOOLS.md
      USER.md
```

---

## Service Architecture

### telemetry-api (Python, stdlib http.server + psycopg2)

The central data hub. No raw SQL from clients -- uses a query registry pattern.

**Routes:**

| Method | Path                  | Auth            | Purpose                                                                                                                                                        |
| ------ | --------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| POST   | /telemetry            | None            | Insert telemetry event. Accepts partial payloads (defaults service="unknown", event_type="untyped").                                                           |
| POST   | /query                | X-Service-Token | Execute named query from registry. Returns JSON rows. Raw SQL rejected with helpful error.                                                                     |
| POST   | /sync                 | X-Service-Token | Sync heartbeat_runs + activity_log from Paperclip tables into telemetry_events. Prunes >90 day old events.                                                     |
| POST   | /champion             | X-Service-Token | Insert champion score event (install=1pt, activate=3pt, second_repo=5pt, paid_convert=15pt).                                                                   |
| GET    | /health               | None            | Health check with DB connectivity test. Returns route list.                                                                                                    |
| GET    | /queries              | None            | List available named queries and their parameter schemas.                                                                                                      |
| GET    | /kpi/{view}           | None            | Query a KPI view (kpi_health, kpi_content, kpi_funnel, kpi_outreach, kpi_automation, kpi_governance, champion_leaderboard). Supports ?limit and ?weeks params. |
| GET    | /champion/leaderboard | None            | Champion referral leaderboard.                                                                                                                                 |

**Named queries in registry:**

| Query Name           | Parameters                                       | Returns                              |
| -------------------- | ------------------------------------------------ | ------------------------------------ |
| recent_telemetry     | limit (int, default 20, max 1000)                | Latest telemetry events              |
| kpi_health           | (none)                                           | Health check aggregates              |
| kpi_automation       | (none)                                           | Automation metrics                   |
| kpi_governance       | (none)                                           | Governance decision metrics          |
| kpi_content          | (none)                                           | Content pipeline metrics             |
| kpi_funnel           | (none)                                           | Lead funnel metrics                  |
| kpi_outreach         | (none)                                           | Outreach pipeline metrics            |
| champion_leaderboard | (none)                                           | Referral scores                      |
| agent_heartbeats     | hours (interval, default "24 hours")             | Heartbeat counts by agent and status |
| agent_status         | (none)                                           | Agent names and statuses             |
| telemetry_by_service | service (str, required), limit (int, default 20) | Events filtered by service name      |

### decision-engine (Python, stdlib http.server + psycopg2)

Routes decisions to the correct solver based on type classification.

**Primitive solvers:**

- policy_only -> GuardSpine governance API (can this action happen?)
- optimization_only -> pymoo NSGA-II (what tradeoff is best?) -- STUB, pymoo not installed
- strategic_only -> Mieza MCP (how will actors react?) -- STUB, no API token
- simulation_only -> MiroFish OASIS (what worlds emerge?) -- STUB, MiroFish unreachable

Pairwise and three-tool compositions are DISABLED because the primitives are stubs.

**Routes:**

| Method | Path    | Purpose                             |
| ------ | ------- | ----------------------------------- |
| POST   | /decide | Classify and route a decision       |
| GET    | /health | Health check with dependency status |

### soak-monitor (Shell script, cron)

Checks health of all services via curl/pg_isready. Posts results to telemetry-api.

**Services checked:**
guardspine, n8n, openclaw, paperclip, postgres, litellm, telemetry-api, decision-engine, mirofish

**Output:** JSON summary posted to POST /telemetry with service="soak-monitor", event_type="health_check".

### mirofish-sim (Python, Flask)

OASIS swarm simulation. Currently has wrong Docker image deployed (a Chinese Flask app, not the OASIS wrapper). The correct code is in guardspine/mirofish-sim/app.py.

### Paperclip (external service, not in this repo)

Org chart + task management. Agents interact through its API.

**Key endpoints:**

- GET /api/agents/me -- agent profile
- GET /api/companies/{id}/issues?assigneeAgentId={id}&status=backlog -- work queue
- POST /api/issues/{id}/comments -- post output
- PATCH /api/issues/{id} -- update status (backlog -> in_progress -> done)
- POST /api/issues/{id}/checkout -- claim an issue

**Auth:** Better Auth sessions (not static API keys). See LEARNINGS.md L015.

---

## Data Flow

### Who Writes What

| Table            | Writers                                                                                                                                    | How                              |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------- |
| telemetry_events | telemetry-api (direct), soak-monitor (via POST /telemetry), n8n workflows (via POST /telemetry), telemetry-api /sync (from heartbeat_runs) | POST /telemetry or POST /sync    |
| heartbeat_runs   | Paperclip + OpenClaw                                                                                                                       | Agent heartbeat execution        |
| agents           | Paperclip                                                                                                                                  | Agent registration and status    |
| issues           | Paperclip, n8n workflows                                                                                                                   | Task creation and updates        |
| issue_comments   | Agents via Paperclip API                                                                                                                   | Draft outputs posted as comments |
| decision_journal | decision-engine                                                                                                                            | POST /decide writes trace        |
| champion_scores  | telemetry-api                                                                                                                              | POST /champion                   |
| activity_log     | Paperclip                                                                                                                                  | Automatic action recording       |

### Event Flow

```
Agent heartbeat fires (OpenClaw -> Paperclip)
  -> Paperclip records in heartbeat_runs
  -> telemetry-api /sync copies to telemetry_events
  -> soak-monitor checks /health endpoints
  -> soak-monitor POSTs results to telemetry-api
  -> kpi_health view aggregates health_check events
  -> n8n W3 workflow queries kpi_health view via POST /query
  -> W3 checks thresholds, sends alerts if needed
```

### Agent Interaction Model

```
1. n8n workflow creates Paperclip issue (e.g., outreach prospect to draft)
2. Paperclip assigns issue to agent based on role
3. Agent heartbeat fires via OpenClaw
4. Agent reads assigned issues (GET /api/companies/{id}/issues)
5. Agent processes issue (apply judgment, draft message, etc.)
6. Agent posts result as issue comment (POST /api/issues/{id}/comments)
7. Agent updates issue status (PATCH /api/issues/{id})
8. David reviews and approves/rejects
```

---

## Telemetry Event Types

All events follow: `{ "service": "...", "event_type": "...", "payload": {...} }`

Full catalog: `guardspine/telemetry-api/TELEMETRY-EVENTS.md`

Key categories:

- **outreach**: outreach_draft, outreach_sent, outreach_response, outreach_negative, outreach_override
- **content**: content_draft, content_published, content_rejected, content_engagement
- **paperclip/openclaw**: heartbeat*succeeded, heartbeat_failed, heartbeat_timed_out, activity*\*
- **guardspine**: council_decision, policy_violation
- **funnel**: funnel_impression through funnel_referral (7 stages)
- **infrastructure**: health_check, service_crash, service_restart

---

## Key Files for Debugging

| Need                    | File                                             |
| ----------------------- | ------------------------------------------------ |
| What went wrong before  | guardspine/workspace/LEARNINGS.md                |
| What each service does  | This file (CODE-ARCHITECTURE.md)                 |
| System health snapshot  | docs/SYSTEM.md                                   |
| Telemetry event catalog | guardspine/telemetry-api/TELEMETRY-EVENTS.md     |
| n8n workflow design     | guardspine/n8n-workflows/N8N-WORKFLOW-PLAN.md    |
| Agent-vs-n8n split      | guardspine/n8n-workflows/WORKFLOW-AGENT-SPLIT.md |
| Decision engine design  | guardspine/decision-engine/INTERACTION-ATLAS.md  |
