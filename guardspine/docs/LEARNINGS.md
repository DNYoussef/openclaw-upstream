# System Learnings

> Every debugging lesson gets recorded here so the system never makes the same mistake twice.
> Referenced by agents, future Claude Code sessions, and the remediation process.

---

## n8n Workflow Debugging

### L001: n8n Code nodes block $env.\* access (2026-03-18)

**Problem**: All workflows using `$env.TELEMETRY_API_URL` etc. in Code nodes fail with "access to env vars denied"
**Root cause**: n8n security policy blocks process.env access in Code nodes by default
**Fix**: Hardcode internal Railway URLs directly in Code nodes. Use n8n credentials for secrets, explicit workflow parameters for non-secrets. Never use $env.\* in Code nodes.

### L002: n8n HTTP Request POST body requires explicit config (2026-03-18)

**Problem**: POST nodes to /telemetry return 400 "Bad request"
**Root cause**: n8n HTTP Request node needs `sendBody: true` + `specifyBody: 'json'` + body in `jsonBody` field. Without these, body is empty or malformed.
**Failed attempts**: `specifyBody: 'string'` with raw JSON (expressions not resolved), `body.json` nesting (sends {"json":{...}} wrapper)
**Working fix**: Use `specifyBody: 'json'` with `jsonBody` containing the JSON string. n8n resolves expressions in this mode.

### L003: n8n parallel node connections cause race conditions (2026-03-18)

**Problem**: W3 "Check Thresholds" node fails with "Node 'Query Automation KPIs' hasn't been executed"
**Root cause**: When two nodes connect to the same downstream node, n8n fires it when EITHER completes, not BOTH
**Fix**: Chain queries sequentially (A -> B -> C) instead of parallel fan-in (A+B -> C). Or use a Merge node.

### L004: n8n workflow PUT updates reset cron intervals (2026-03-18)

**Problem**: After pushing workflow updates via API, cron doesn't fire at expected clock times
**Root cause**: PUT /api/v1/workflows/{id} deactivates and reactivates the workflow, resetting the interval timer relative to activation time
**Mitigation**: Account for ~30 min delay after any workflow update before expecting the next cron fire.

## Railway / Infrastructure

### L005: Paperclip runs on port 3100, not 3000 (2026-03-18)

**Problem**: Workflows calling http://paperclip.railway.internal:3000 get connection refused
**Root cause**: Paperclip's PORT env var is set to 3100 in Railway
**Fix**: Always check `railway variables --service <name>` for the actual PORT before hardcoding URLs

### L006: Railway CLI `railway up` fails on large monorepos -- subdirectory deploy WORKS (2026-03-18)

**Problem**: `railway up` from openclaw-upstream root fails with "memory allocation of 13958643712 bytes failed"
**Root cause**: Railway CLI tries to index the entire repo (~13GB allocation attempt)
**WORKING FIX**: Deploy from the SERVICE SUBDIRECTORY: `cd guardspine/telemetry-api && railway up --detach`. This indexes only the subdirectory (~KB not ~GB). Verified working for telemetry-api, soak-monitor, decision-engine.
**Procedure**: `railway link -p PROJECT_ID -s SERVICE_NAME -e production` then `cd guardspine/SERVICE_DIR && railway up --detach`

### L007: Railway "crash" emails for cron jobs are normal (2026-03-18)

**Problem**: Receiving "Deployment crashed" emails for soak-monitor and n8n-importer
**Root cause**: These are cron/one-shot jobs that exit after completion. Railway reports the container stop as a "crash"
**Fix**: No action needed. Check logs to confirm the job ran successfully before exiting.

### L008: Code changes in repo are NOT automatically deployed (2026-03-18)

**Problem**: All code fixes from the session were in the repo but the live services ran old code
**Root cause**: Railway services were not connected to auto-deploy from git, or the deploy path was unclear
**Lesson**: NEVER claim a fix is done until verified against the LIVE system. Coded != Deployed != Verified.

## Telemetry API

### L009: telemetry-api POST /telemetry rejects bodies missing service or event_type (2026-03-18)

**Problem**: n8n error handlers POSTing to /telemetry get 400
**Root cause**: The API requires top-level `service` and `event_type` fields. Nested JSON `{"json":{"service":...}}` fails.
**Fix**: Send flat JSON body with service and event_type at top level.

### L010: telemetry-api and memory-mcp share Railway logs (2026-03-18)

**Problem**: Identical log entries appearing under both service names
**Root cause**: They are the SAME Railway service (memory-mcp runs an internal telemetry bridge in the same process)
**Implication**: telemetry-api (guardspine/telemetry-api/) is a DIFFERENT codebase from the Railway service labeled telemetry-api

## Outreach

### L011: n8n credential names must match exactly (2026-03-18)

**Problem**: CMO workflow fails with "Credential 'paperclip-auth' does not exist"
**Root cause**: The credential in n8n was named "Paperclip API Key" (ID: AXD4VXk71OMLdnex), but workflow JSON referenced "paperclip-auth"
**Fix**: Check existing credentials via GET /api/v1/credentials before assuming names. Use the ID, not just the name.

### L012: OpenRouter credits at $0 cascades to entire agent chain (2026-03-18)

**Problem**: All agents fail with 402 billing errors, enter context overflow loops, compaction fails
**Root cause**: OpenRouter balance = $0. LiteLLM returns 402 on deepseek-v3.2. Fallbacks (gemini-flash, gpt-4o-mini, llama-70b) also fail (all through same OpenRouter key).
**Fix**: Top up credits. Also: configure at least one model that uses a DIFFERENT billing path (direct Gemini API key, not through OpenRouter).
**Prevention**: Add LiteLLM budget alerting. Agent should degrade gracefully on billing failure, not loop.

### L015: Paperclip API uses Better Auth sessions, not static API keys (2026-03-18)

**Problem**: W6 "Fetch Paperclip Issues" returns 403 Forbidden even with "Paperclip API Key" credential
**Root cause**: Paperclip has PAPERCLIP_DEPLOYMENT_MODE=authenticated with BETTER_AUTH_SECRET. It expects a Better Auth session token, not a static API key. The n8n credential "Paperclip API Key" likely has a stale or wrong token.
**Fix needed**: Generate a valid API token from Paperclip's auth system (David or Igor must do this). Or: if Paperclip supports API key auth alongside Better Auth, set one up. Or: switch Paperclip to allow internal Railway traffic without auth.
**Workaround**: W6's non-Paperclip path (telemetry query) works. Only the Paperclip fetch node fails.

### L016: n8n PUT workflow updates may silently stop cron triggers (2026-03-18)

**Problem**: CMO and W5 stopped firing after PUT /api/v1/workflows/{id} update at 22:15 UTC. W3 kept working.
**Root cause**: n8n sometimes doesn't restart the cron scheduler after a PUT update, even though `active: true` is reported. Workflows show as active but the trigger never fires.
**Fix**: After any PUT update, always do a deactivate->activate cycle: POST /deactivate then POST /activate. This forces n8n to restart the cron scheduler.
**Prevention**: Add this to the standard workflow push script.

## Process

### L013: Always check live state before claiming a fix (2026-03-18)

**Problem**: Earlier session edited 14 files, pushed 14 workflows, created 2 tables, disabled 5 agents, wrote 1131-line guide. Independent review found live system unchanged.
**Root cause**: Confusing "code was written" with "system is fixed"
**Rule**: MEASURE-CUT-MEASURE. Show the failing command. Deploy the fix. Show the passing command. No exceptions.

### L014: Live n8n export may differ from repo JSON (2026-03-18)

**Problem**: Repo workflow JSON and live n8n workflow JSON diverge after manual edits or API updates
**Root cause**: n8n adds runtime metadata (credential IDs, execution counts, positions) that repo copies don't have
**Fix**: After fixing a workflow, export the LIVE version as canonical. Diff only behavior-bearing fields.
