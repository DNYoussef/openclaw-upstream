# OpenClaw + Paperclip Bootstrap Prompt

You are bootstrapping the GuardSpine autonomous business system.
Your job: verify every service is healthy, every agent is registered and responsive, every integration path works end-to-end. Do not skip steps. Do not assume anything works until you verify it.

## Phase 0: Verify Your Own Identity

1. Confirm you are running on the OpenClaw gateway at `openclaw-production-e5a2.up.railway.app`
2. Confirm your model: you should be running on `anthropic/claude-opus-4-6` (David's primary)
3. Confirm auth: both Anthropic (setup-token) and OpenAI Codex (OAuth) providers should be available

## Phase 1: Service Health Check

Ping every service on the Railway internal network. For each, do a simple HTTP GET to confirm it responds. Report results as a table.

| Service | URL | Health Check |
|---------|-----|-------------|
| Paperclip | `http://paperclip.railway.internal:3100/` | GET, expect 200 or redirect |
| telemetry-api | `http://telemetry-api.railway.internal:8090/health` | GET |
| decision-engine | `http://decision-engine.railway.internal:8091/health` | GET |
| LiteLLM | `http://litellm.railway.internal:4000/health` | GET |
| n8n | `http://n8n.railway.internal:5678/healthz` | GET |
| guardspine-internal | `http://guardspine-internal.railway.internal:8000/health` | GET |
| mirofish | `http://mirofish-sim.railway.internal:5001/health` | GET |
| Postgres | TCP connect to `postgres.railway.internal:5432` | Connection test via SQL query |

For any service that fails, log the error and continue. Do not block on failures.

## Phase 2: Paperclip Agent Registration

Check that all 7 agents are registered in Paperclip. Query:

```
GET http://paperclip.railway.internal:3100/api/agents
```

Expected agents (6 active + 1 reserved):

| Agent | Model | Heartbeat | Role |
|-------|-------|-----------|------|
| CEO | anthropic/claude-sonnet-4-6 | 24h | Strategic oversight, daily briefing review |
| CMO | anthropic/claude-sonnet-4-6 | 2h | Outreach hunting, drafting, follow-up |
| Content Director | anthropic/claude-sonnet-4-6 | 2h | LinkedIn posts, lead magnets, case studies |
| CTO | openai-codex/gpt-5.4 | 2h | Code review, technical decisions, CI/CD health |
| Chief of Staff | openai-codex/gpt-5.4 | 2h | Cross-dept coordination, blocker resolution |
| Narrowcast Scout | openai-codex/gpt-5.4-mini | 6h | Thread scoring, prospect signal extraction |
| CFO | openai-codex/gpt-5.4 | 24h | Budget tracking, cost monitoring |

If any agent is missing, create it using the Paperclip API.
If any agent has wrong model routing, update it.

Model routing rules:
- CREATIVE agents (CEO, CMO, Content Director) use Anthropic subscription models
- CRITIC agents (CTO, Chief of Staff, CFO, Narrowcast Scout) use OpenAI Codex subscription models
- All flat-rate subscriptions. $0 marginal cost per token. But don't waste context.

## Phase 3: Agent System Prompts

Each agent needs its system prompt loaded. System prompts live at:
- `guardspine/agents/cmo-system-prompt.md`
- `guardspine/agents/cto-system-prompt.md`
- `guardspine/agents/content-system-prompt.md`
- `guardspine/agents/SHARED-CONTEXT.md` (injected into ALL agents)

Every agent gets SHARED-CONTEXT.md as prefix, then its role-specific prompt.

Verify each agent's system prompt is set. If not, read the markdown file and set it via the Paperclip API or OpenClaw agent config.

## Phase 4: Verify Paperclip Issue Pipeline

The work loop is:
1. n8n creates issues in Paperclip (tagged for specific agents)
2. Agent wakes on heartbeat
3. Agent queries: `GET /api/companies/guardspine/issues?assigneeAgentId={me}&status=backlog`
4. Agent claims issue: `POST /api/issues/{id}/checkout`
5. Agent reads issue, applies judgment, posts recommendation: `POST /api/issues/{id}/comments`
6. Agent updates status: `PATCH /api/issues/{id}` (backlog -> in_progress -> done)
7. Agent logs PMC telemetry: `POST telemetry-api.railway.internal:8090/telemetry`

Test the full loop:
1. Create a test issue assigned to CTO: "Bootstrap health check -- verify agent can claim and close issues"
2. Verify CTO agent can retrieve it
3. Post a test comment
4. Mark it done
5. Verify telemetry event was logged

## Phase 5: Decision Engine Integration

Test each component of the S/G/O pipeline:

### S (Simulate) -- MiroFish
```
POST http://decision-engine.railway.internal:8091/simulate
Content-Type: application/json
{"scenario": "test_bootstrap", "personas": 1, "model": "free-sim"}
```
Expected: response with simulation result. Uses free llama-3.2-3b via LiteLLM.

### G (Game Theory) -- Mieza
```
POST http://decision-engine.railway.internal:8091/solve
Content-Type: application/json
{"game_type": "test", "players": 2}
```
Expected: response with Nash equilibrium solution.

### O (Optimize) -- globalMOO
```
POST http://decision-engine.railway.internal:8091/optimize
Content-Type: application/json
{"objective": "test_bootstrap"}
```
Expected: response with optimization result (may return "insufficient data" if < 2 weeks operational data -- that's OK).

### Full Stack
```
POST http://decision-engine.railway.internal:8091/decide
Content-Type: application/json
{"decision_type": "full_stack", "context": "bootstrap test"}
```

## Phase 6: GuardSpine Governance Check

Verify the governance layer is active:

```
GET http://guardspine-internal.railway.internal:8000/health
```

Confirm 29 tools are classified into L0-L4 tiers (they were classified in the Mar 19 session). If all show "unknown" or "L2", the classification was lost and needs to be redone.

Tool risk tiers:
- L0: read-only, no side effects (file reads, searches)
- L1: local writes, reversible (file edits, git operations)
- L2: external reads, API calls (web fetch, API queries)
- L3: external writes, hard to reverse (issue creation, message sending)
- L4: destructive or high-stakes (deployments, data deletion, financial transactions)

## Phase 7: n8n Workflow Verification

Check that n8n has active workflows:

```
GET http://n8n.railway.internal:5678/api/v1/workflows?active=true
```

Expected: 30+ active workflows. Key ones to verify:
- W5: Content Scheduling
- W6: Data Sync Pipeline
- W11: CEO Briefing
- W22: Follow-up Manager
- W23: Narrowcast monitoring
- W26: Auto Updater
- W30: Code Reviewer
- CMO Outreach Pipeline

## Phase 8: Slack Channel Check

If SLACK_BOT_TOKEN and SLACK_APP_TOKEN are set as env vars, verify Slack connectivity:
1. Check that the Slack Bolt app can connect via Socket Mode
2. Post a test message to #alerts: "Bootstrap complete. All systems verified."

If Slack tokens are not set, log this as a gap and move on.

## Phase 9: Telemetry Verification

Post a bootstrap telemetry event:
```
POST http://telemetry-api.railway.internal:8090/telemetry
Content-Type: application/json
{
  "service": "bootstrap",
  "event_type": "system_bootstrap",
  "payload": {
    "timestamp": "<now>",
    "services_checked": <count>,
    "services_healthy": <count>,
    "agents_registered": <count>,
    "agents_healthy": <count>,
    "decision_engine": "ok|degraded|offline",
    "governance": "ok|degraded|offline",
    "n8n_workflows_active": <count>,
    "slack": "connected|disconnected|not_configured"
  }
}
```

## Phase 10: Bootstrap Report

After all phases, produce a summary table:

```
GUARDSPINE AUTONOMOUS BUSINESS -- BOOTSTRAP REPORT
Date: <timestamp>
Gateway: openclaw-production-e5a2.up.railway.app

SERVICES
  Paperclip .............. [OK/FAIL]
  telemetry-api .......... [OK/FAIL]
  decision-engine ........ [OK/FAIL]
  LiteLLM ................ [OK/FAIL]
  n8n .................... [OK/FAIL]
  guardspine-internal .... [OK/FAIL]
  mirofish ............... [OK/FAIL]
  Postgres ............... [OK/FAIL]

AGENTS (7 expected)
  CEO .................... [registered/missing] [heartbeat OK/stale]
  CMO .................... [registered/missing] [heartbeat OK/stale]
  Content Director ....... [registered/missing] [heartbeat OK/stale]
  CTO .................... [registered/missing] [heartbeat OK/stale]
  Chief of Staff ......... [registered/missing] [heartbeat OK/stale]
  CFO .................... [registered/missing] [heartbeat OK/stale]
  Narrowcast Scout ....... [registered/missing] [heartbeat OK/stale]

DECISION ENGINE
  S (MiroFish) ........... [OK/FAIL]
  G (Mieza) .............. [OK/FAIL]
  O (globalMOO) .......... [OK/FAIL]
  Full Stack ............. [OK/FAIL]

GOVERNANCE
  GuardSpine ............. [OK/FAIL]
  Tools classified ....... [count]/29

WORKFLOWS
  n8n active ............. [count]/32

CHANNELS
  Slack .................. [connected/not configured]
  Dashboard .............. [connected]

BLOCKERS
  <list any failures that prevent normal operation>

RECOMMENDATIONS
  <list suggested fixes for any degraded components>
```

If everything is green, post to Slack #alerts: "Bootstrap complete. All systems nominal."
If there are failures, post the blocker list to #alerts and create Paperclip issues for each blocker assigned to CTO or Chief of Staff.

## Rules

1. Do not fabricate results. If a service doesn't respond, report it as FAIL.
2. Do not retry more than 3 times per service. If it fails 3x, move on.
3. Budget: this bootstrap should complete in under 15 minutes.
4. After bootstrap, do NOT start executing agent work. Just report status and stop.
5. Use the banned words list from SHARED-CONTEXT.md. If any agent prompt contains banned words, flag it.
6. Log every HTTP request and response status to telemetry for audit trail.
