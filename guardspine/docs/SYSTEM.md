# GuardSpine System Reference

> Last verified: 2026-03-18T17:15 UTC (live Railway + Postgres inspection)
> Method: Railway CLI logs, n8n API executions, live Postgres queries. No guessing.

---

## Service Map

| Service             | Purpose                                     | Port   | Health Endpoint   | Status                                                                                | Deploy Method                                                 |
| ------------------- | ------------------------------------------- | ------ | ----------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Postgres            | Shared database                             | 5432   | pg_isready        | CORE - Running                                                                        | Railway managed                                               |
| Paperclip           | Org chart, task delegation, agent heartbeat | 3100   | /api/health       | CORE - Running (B-)                                                                   | Railway dashboard                                             |
| LiteLLM             | LLM model proxy with budget controls        | 4000   | /health/readiness | CORE - BROKEN (F)                                                                     | Railway dashboard                                             |
| OpenClaw            | AI agent gateway, WebSocket protocol        | varies | /health           | CORE - BROKEN (F)                                                                     | Railway dashboard                                             |
| telemetry-api       | Event logging + named query registry        | 8090   | /health           | CORE - Running (B+) DEPLOYED 2026-03-19 01:25 UTC. Raw SQL blocked. 11 named queries. | `cd guardspine/telemetry-api && railway up --detach`          |
| n8n                 | Workflow automation (crons, pipelines)      | 5678   | /healthz          | CORE - Partially Working (D+). W3 passing (6+ runs). Others waiting on cron cycles.   | Railway dashboard                                             |
| soak-monitor        | Health checks all services on cron          | N/A    | N/A (cron job)    | CORE - Running (D)                                                                    | `cd guardspine/soak-monitor && railway up --detach`           |
| guardspine-internal | Governance API (evidence bundles)           | 8000   | /health           | CORE - Running (B)                                                                    | Railway dashboard                                             |
| decision-engine     | S/G/O decision routing                      | 8091   | /health           | QUARANTINED - stubs only                                                              | `cd guardspine/decision-engine && railway up --detach`        |
| mirofish            | OASIS swarm simulation                      | 5001   | /health           | QUARANTINED - wrong service deployed                                                  | Railway dashboard                                             |
| ops-portal          | Operations dashboard                        | varies | N/A               | QUARANTINED - static HTML with fake green dots                                        | Railway dashboard                                             |
| memory-mcp          | Cross-session memory (triple-layer)         | varies | N/A               | QUARANTINED - lifecycle errors                                                        | Railway dashboard                                             |
| n8n-importer        | One-shot workflow import tool               | N/A    | N/A (one-shot)    | Complete - 2 workflows failed to activate                                             | `cd guardspine/n8n-workflows/importer && railway up --detach` |

### Internal Railway URLs

All services communicate via Railway's private network:

```
paperclip.railway.internal:3100
telemetry-api.railway.internal:8090
decision-engine.railway.internal:8091
litellm.railway.internal:4000
n8n.railway.internal:5678
guardspine-internal.railway.internal:8000
mirofish.railway.internal:5001
postgres.railway.internal:5432
```

Public domain for n8n: `n8n-production-7528.up.railway.app`
Public domain for Postgres proxy: `interchange.proxy.rlwy.net:14013`

---

## Current System Health (2026-03-18)

### Root Cause Chain

```
OpenRouter credits exhausted ($0 balance)
  -> LiteLLM 402 on all models (deepseek-v3.2, gemini-flash, gpt-4o-mini, llama-70b)
  -> OpenClaw agents hit 402, enter context overflow loop
  -> Compaction attempts fail (no real messages to summarize)
  -> Agent heartbeats fail (CEO 3/4, CMO 4/12, CTO 4/12 failed)
  -> Paperclip records failed heartbeats
  -> System looks alive but produces errors
```

### n8n Failure Chain (separate from LLM billing)

```
Workflows use $env.* in Code nodes
  -> n8n security policy blocks env var access
  -> Every workflow with Code nodes fails immediately
  -> 47/47 executions = error since deployment
```

### Human Blockers

- **H1 (CRITICAL)**: Top up OpenRouter credits. Without this, LiteLLM/OpenClaw/agents cannot function.
- **H2**: Approve secret rotation scope.
- **H6 (conditional)**: Reset n8n password if API credential creation fails.

---

## Postgres Schema

Database: Railway-managed PostgreSQL.
Connection: `interchange.proxy.rlwy.net:14013` (external) or `postgres.railway.internal:5432` (internal).

### Tables (key ones with row counts as of 2026-03-18)

| Table            | Rows   | Writers                      | Purpose                                                   |
| ---------------- | ------ | ---------------------------- | --------------------------------------------------------- |
| agents           | 12     | Paperclip                    | Agent roster (6 active/idle, 6 inactive)                  |
| heartbeat_runs   | 192    | Paperclip/OpenClaw           | Agent heartbeat execution records                         |
| telemetry_events | 281    | telemetry-api                | All system events (outreach, content, health, governance) |
| issues           | 187    | Paperclip, n8n               | Task queue (CMO outreach prospects, content tasks)        |
| issue_comments   | 67     | Agents via Paperclip         | Agent-generated drafts and outputs                        |
| decision_journal | 1      | decision-engine              | S/G/O decision traces                                     |
| case_traces      | 0      | decision-engine              | Never written to                                          |
| champion_scores  | 0      | telemetry-api POST /champion | Referral leaderboard events                               |
| activity_log     | varies | Paperclip                    | Action audit trail                                        |

### Views (all currently returning 0 rows)

| View                 | Source                                        | Purpose                            |
| -------------------- | --------------------------------------------- | ---------------------------------- |
| kpi_health           | telemetry_events WHERE service='soak-monitor' | Daily health check aggregates      |
| kpi_content          | telemetry_events WHERE service='content'      | Content pipeline metrics           |
| kpi_funnel           | telemetry_events WHERE service='funnel'       | Lead funnel conversion metrics     |
| kpi_outreach         | telemetry_events WHERE service='outreach'     | Outreach pipeline metrics          |
| kpi_automation       | telemetry_events WHERE service='paperclip'    | Agent automation metrics           |
| kpi_governance       | telemetry_events WHERE service='guardspine'   | Governance decision metrics        |
| champion_leaderboard | champion_scores                               | Aggregated referral scores by user |

Most views are empty. Exception: kpi_health now has data (soak-monitor deployed 2026-03-19, writing health_check events). kpi_automation has 2 rows. Others empty because upstream services (LLM billing, content pipeline) are not yet producing events.

---

## n8n Workflow Status

| Workflow              | Schedule      | Status                                                    | Failing Node             | Error                                                  |
| --------------------- | ------------- | --------------------------------------------------------- | ------------------------ | ------------------------------------------------------ |
| W3 Health Dashboard   | Every 30min   | PASSING (6+ consecutive successes since 22:00 UTC Mar 18) | N/A                      | Fixed: hardcoded URLs, sequential chain, jsonBody POST |
| CMO Outreach Pipeline | Every 2hr     | FAILING                                                   | Fetch CMO Backlog Issues | paperclip-auth credential missing                      |
| W5 Content Scheduling | Every 4hr     | FAILING                                                   | Fetch Content Backlog    | $env access denied                                     |
| W6 Data Sync          | Every 6hr     | FAILING                                                   | Fetch Paperclip Issues   | $env access denied                                     |
| W11 CEO Briefing      | Daily         | FAILING                                                   | Automation KPIs          | $env access denied                                     |
| Narrowcast Scanner    | Once (Mar 14) | FAILED                                                    | Email Digest to David    | no credentials set                                     |

W3 is the first workflow to pass 3 consecutive clean runs (verified live Mar 18 23:00 UTC). W6 has 1 success (Paperclip credential issue on some paths). CMO/W5/W6/W11 crons restarted at 01:20 UTC Mar 19 -- waiting for first post-fix executions. Fixes applied: hardcoded URLs (L001), correct port 3100 (L005), jsonBody POST bodies (L002), sequential chains (L003), cron restart after PUT (L016).

---

## Agent Roster

### Active (6)

Agents with heartbeat_runs entries. All failing due to LiteLLM 402 (OpenRouter credits exhausted).

| Agent            | Role                                | Heartbeat (24hr)    | Status                  |
| ---------------- | ----------------------------------- | ------------------- | ----------------------- |
| CEO              | Strategic planning, escalation      | 1 success, 3 failed | Degraded                |
| Chief of Staff   | Coordination, blocker resolution    | 13 succeeded        | Working (no LLM needed) |
| CMO              | Outreach drafting                   | 8 success, 4 failed | Degraded                |
| Content Director | LinkedIn post drafting              | 9 success, 1 failed | Mostly working          |
| CTO              | Technical decisions, code review    | 8 success, 4 failed | Degraded                |
| Narrowcast Scout | DISABLED -- hunting merged into CMO | N/A                 | Inactive                |

### Inactive (6) -- disabled 2026-03-18 during remediation

| Agent          | Reason                                                            |
| -------------- | ----------------------------------------------------------------- |
| Memory Curator | 1 run ever, no output. Orphaned.                                  |
| Model Lab      | 1 run ever, no output. Orphaned.                                  |
| CRO            | 1 run, zero work. No input pipeline.                              |
| BizDev Scout   | 1 run, zero work. No task queue.                                  |
| COO Workflow   | 17 runs, zero output. Redundant with n8n health checks.           |
| OpenClaw       | Gateway agent. Intentionally deactivated (not a department head). |
| Research       | Not implemented                                                   |
| Security       | Not implemented                                                   |

---

## Quarantined Services

These are deployed but broken or fake. Do not depend on them.

| Service         | Problem                                                                                | When to Unquarantine                                             |
| --------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| decision-engine | Stubs only. pymoo not installed. Mieza token not set. MiroFish unreachable.            | When at least one solver (S, G, or O) has a working backend      |
| mirofish        | Wrong service deployed -- a Chinese Flask app, not the OASIS wrapper                   | Redeploy with correct Docker image from guardspine/mirofish-sim/ |
| ops-portal      | Static HTML showing fake green dots. Not connected to real data.                       | Rebuild to query telemetry-api /kpi/\* endpoints                 |
| memory-mcp      | Shares Railway logs with telemetry-api (same process). cleanup_expired AttributeError. | Fix lifecycle_scheduler code, deploy as separate service         |

---

## Deploy Procedure

### From subdirectory (verified working)

```bash
# 1. Link to the Railway project and service
railway link -p PROJECT_ID -s SERVICE_NAME -e production

# 2. Deploy from the service subdirectory (NOT the repo root)
cd guardspine/<service-dir>/
railway up --detach
```

**WARNING**: `railway up` from the repo root fails with "memory allocation of 13958643712 bytes failed" because Railway CLI tries to index the entire monorepo. Always deploy from the subdirectory. See LEARNINGS.md L006.

### Service-to-directory mapping

| Railway Service | Directory                          |
| --------------- | ---------------------------------- |
| telemetry-api   | guardspine/telemetry-api/          |
| soak-monitor    | guardspine/soak-monitor/           |
| decision-engine | guardspine/decision-engine/        |
| mirofish        | guardspine/mirofish-sim/           |
| n8n-importer    | guardspine/n8n-workflows/importer/ |

### Post-deploy verification

NEVER claim a fix is done until verified against the LIVE system. See LEARNINGS.md L008, L013.

```
Coded != Deployed != Verified
```

After every deploy:

1. Check Railway deploy logs for startup errors
2. Hit the /health endpoint
3. Verify the specific fix (run the failing query, trigger the workflow, etc.)

---

## Known Issues and LEARNINGS References

| Issue                                            | LEARNINGS Entry | Status                                           |
| ------------------------------------------------ | --------------- | ------------------------------------------------ |
| n8n Code nodes block $env.\*                     | L001            | Fix: hardcode Railway internal URLs              |
| n8n POST body config                             | L002            | Fix: use specifyBody: 'json' with jsonBody       |
| n8n parallel node race conditions                | L003            | Fix: chain sequentially or use Merge node        |
| n8n PUT resets cron timers                       | L004, L016      | Fix: deactivate/activate cycle after PUT         |
| Paperclip runs on port 3100                      | L005            | Fix: use 3100 not 3000                           |
| Railway monorepo deploy OOM                      | L006            | Fix: deploy from subdirectory                    |
| Railway cron "crash" emails are normal           | L007            | No action needed                                 |
| Code changes not auto-deployed                   | L008            | Always verify live after deploy                  |
| telemetry-api rejects missing service/event_type | L009            | Fixed: defaults to "unknown"/"untyped"           |
| telemetry-api and memory-mcp share logs          | L010            | Different codebases, same Railway process        |
| n8n credential name mismatch                     | L011            | Check GET /api/v1/credentials, use ID not name   |
| OpenRouter $0 cascades to all agents             | L012            | Top up credits, add non-OpenRouter fallback      |
| Paperclip uses Better Auth, not static keys      | L015            | Need valid session token or internal auth bypass |

Full details: `guardspine/workspace/LEARNINGS.md` and `Desktop/guardspine/LEARNINGS.md`
