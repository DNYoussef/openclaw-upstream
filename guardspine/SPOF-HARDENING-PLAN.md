# SPOF Hardening Plan: GuardSpine Railway Deployment

## Executive Summary

Three single points of failure exist:

1. **Postgres**: NO connection pooling in decision-engine (per-request psycopg2.connect), unbounded table growth, missing indexes on telemetry_events
2. **LiteLLM**: Single instance, duplicate gpt-5.4 entries, misleading embedding aliases (768-dim Gemini vs 1536-dim OpenAI), free models fail silently
3. **n8n**: 118 live workflows but only 9 in Docker importer (catastrophic data loss on redeploy), 50 workflows missing from git, no CI/CD, Pilot+Morning Brief webhooks stubbed

## SPOF #1: Postgres - Connection Exhaustion & Unbounded Growth

### Bugs Found

**Bug P1: decision-engine has NO connection pooling**

- File: `/app/guardspine/decision-engine/router.py` lines 676, 722, 769
- Creates fresh connection per request: `conn = psycopg2.connect(DB_URL)`
- telemetry-api DOES use `SimpleConnectionPool(minconn=1, maxconn=10)` — inconsistent
- **Impact**: Connection exhaustion under load, immediate denial-of-service

**Bug P2: Unbounded table growth (no retention policy)**

- Tables: `activity_log`, `case_traces` (exists in code but 0 rows), `heartbeat_runs`, `telemetry_events`
- W18 "DB Retention Cleaner" only runs a 90-day DELETE on telemetry_events, does NOT clean activity_log, case_traces, or heartbeat_runs
- **Impact**: Disk exhaustion within weeks

**Bug P3: Missing indexes on high-query columns**

- `telemetry_events` queried by (service, event_type, ts) but no composite index
- activity_log indexed only on timestamp
- **Impact**: Full table scans on every telemetry query

**Bug P4: No credential isolation**

- All services share the same `DATABASE_URL` with full superuser or role
- No role-based access control (RBAC) per service
- **Impact**: Lateral movement if one service is compromised

**Bug P5: Backup RTO/RPO not verified**

- Railway managed instance with no stated recovery SLA
- No cross-region backup mentioned in codebase

### Fixes (Ordered by Blast Radius)

#### Phase 1: Connection Pooling (CRITICAL)

**Time: 1-2 hours**

1. **Add pgBouncer layer inside decision-engine container**
   - Dockerfile: `RUN apt-get install pgbouncer`
   - Start pgBouncer on localhost:6432
   - decision-engine connects to `postgresql://localhost:6432/guardspine` (pgBouncer proxy)
   - Configure: `pool_mode = transaction`, `max_client_conn = 50`, `default_pool_size = 10`

2. **Alternative: Use psycopg2 pool in decision-engine**
   - File: `/app/guardspine/decision-engine/router.py`
   - Add at module level (after imports):
     ```python
     from psycopg2.pool import SimpleConnectionPool
     _pool = SimpleConnectionPool(minconn=2, maxconn=20, dsn=DB_URL)
     ```
   - Replace all `psycopg2.connect(DB_URL)` with `_pool.getconn()`
   - Replace all `conn.close()` with `_pool.putconn(conn)`
   - Add try-finally to ensure putconn on error

3. **Verify pooling in telemetry-api**
   - Already using `SimpleConnectionPool(minconn=1, maxconn=10)` ✓
   - Increase to `maxconn=20` for headroom

#### Phase 2: Retention & Cleanup (HIGH)

**Time: 3-4 hours**

1. **Add table-level retention policies**
   - File: Create `/app/guardspine/data/migration-retention.sql`

   ```sql
   -- Retention: 90 days for telemetry, 30 for activity_log, 180 for case_traces
   ALTER TABLE activity_log ADD CONSTRAINT activity_log_retention
     CHECK (timestamp > NOW() - INTERVAL '30 days');
   ALTER TABLE case_traces ADD CONSTRAINT case_traces_retention
     CHECK (created_at > NOW() - INTERVAL '180 days');
   ALTER TABLE heartbeat_runs ADD CONSTRAINT heartbeat_runs_retention
     CHECK (started_at > NOW() - INTERVAL '90 days');
   ```

2. **Modify W18 (DB Retention Cleaner) workflow**
   - Currently only audits; make it DELETE:

   ```sql
   DELETE FROM activity_log WHERE timestamp < NOW() - INTERVAL '30 days';
   DELETE FROM case_traces WHERE created_at < NOW() - INTERVAL '180 days';
   DELETE FROM heartbeat_runs WHERE started_at < NOW() - INTERVAL '90 days';
   DELETE FROM telemetry_events WHERE ts < NOW() - INTERVAL '90 days';
   ```

3. **Add VACUUM scheduling**
   - M3 "Postgres VACUUM" already exists, verify it runs daily
   - Ensure autovacuum is enabled: `autovacuum = on` in PostgreSQL config

#### Phase 3: Missing Indexes (MEDIUM)

**Time: 30 minutes**

```sql
-- Composite index for most-queried telemetry path
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_telemetry_service_type_ts
  ON telemetry_events(service, event_type, ts DESC);

-- Case trace by case_id (currently no unique index)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_case_traces_case_id
  ON case_traces(case_id);

-- Heartbeat status rollup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_heartbeat_runs_agent_status
  ON heartbeat_runs(agent_id, status, started_at DESC);
```

#### Phase 4: Credential Isolation (MEDIUM)

**Time: 2-3 hours**

1. **Create service-specific roles in Postgres**

   ```sql
   CREATE ROLE decision_engine WITH LOGIN PASSWORD '<random>';
   CREATE ROLE telemetry_api WITH LOGIN PASSWORD '<random>';
   CREATE ROLE n8n WITH LOGIN PASSWORD '<random>';

   -- Restrict each role to needed tables
   GRANT SELECT, INSERT ON telemetry_events, case_traces, decision_journal TO decision_engine;
   GRANT SELECT, INSERT, UPDATE ON telemetry_events, heartbeat_runs, activity_log TO telemetry_api;
   ```

2. **Update Railway env vars**
   - decision-engine: `DATABASE_URL=postgresql://decision_engine:...@postgres.railway.internal/guardspine`
   - telemetry-api: `DATABASE_URL=postgresql://telemetry_api:...@postgres.railway.internal/guardspine`

---

## SPOF #2: LiteLLM - Model Aliasing Chaos & Silent Failures

### Bugs Found

**Bug L1: Duplicate model_name entries**

- File: `/app/guardspine/litellm/config.yaml` line 24 and line 105
- Two entries for `gpt-5.4`: one legit (OpenAI), one for backwards compat
- Router may pick either one non-deterministically

**Bug L2: Misleading embedding aliases**

- `text-embedding-3-small` → `gemini/gemini-embedding-001` (768-dim)
- `text-embedding-004` → `gemini/gemini-embedding-001` (768-dim)
- Consumers expecting OpenAI (1536-dim) get dimension mismatch → silent failures in vector indexing
- **Impact**: Memory queries fail silently, LCM expansion breaks

**Bug L3: Free models lack fallback**

- `free-sim` → `openrouter/meta-llama/llama-3.2-3b-instruct:free` (10 req/min rate limit)
- `deepseek-chat` → SAME endpoint
- No fallback if rate-limited; MiroFish simulations fail silently
- **Impact**: Simulation pipeline hangs

**Bug L4: Legacy routes now paid**

- `openrouter/deepseek/deepseek-v3.2` → routes to haiku (Anthropic paid)
- `deepseek-v3` → haiku instead of actual deepseek-v3
- Original cost assumption (free OpenRouter) now charges per-request
- **Impact**: Cost creep, budget overruns

**Bug L5: No fallbacks for free-sim, deepseek-chat, gpt-5.4-nano**

- config.yaml router_settings.fallbacks missing these entries
- If primary fails, system hangs (no retry)

### Fixes (Ordered by Blast Radius)

#### Phase 1: Deduplicate & Fix Embeddings (CRITICAL)

**Time: 15 minutes**

File: `/app/guardspine/litellm/config.yaml`

1. **Remove duplicate gpt-5.4 entry** (line 105)

   ```yaml
   # DELETE THIS BLOCK:
   - model_name: gpt-5.4
     litellm_params:
       model: openai/gpt-5.4
       api_key: os.environ/OPENAI_API_KEY
   ```

2. **Fix embedding aliases to use actual OpenAI**

   ```yaml
   - model_name: text-embedding-3-small
     litellm_params:
       model: openai/text-embedding-3-small
       api_key: os.environ/OPENAI_API_KEY

   - model_name: text-embedding-004
     litellm_params:
       model: openai/text-embedding-3-large
       api_key: os.environ/OPENAI_API_KEY
   ```

#### Phase 2: Add Fallbacks (HIGH)

**Time: 10 minutes**

```yaml
router_settings:
  fallbacks:
    - free-sim: [haiku, gpt-5.4-nano]
    - deepseek-chat: [llama-70b, gpt-5.4-mini]
    - gpt-5.4-nano: [gpt-5.4-mini, haiku]
```

#### Phase 3: Fix Legacy Cost Creep (MEDIUM)

**Time: 15 minutes**

```yaml
# Option A: Route legacy names to cheap haiku (honest about cost)
- model_name: deepseek-v3
  litellm_params:
    model: anthropic/claude-haiku-4-5-20251001
    api_key: os.environ/ANTHROPIC_API_KEY
# Option B: Drop legacy support entirely (safest)
# (Remove openrouter/* and deepseek-v3, llama-70b entries)
```

---

## SPOF #3: n8n - 109 Missing Workflow Definitions

### Bugs Found

**Bug N1: Only 9 of 118 workflows in Docker importer**

- Directory: `/app/guardspine/n8n-workflows/importer/workflows/`
- 9 .json files vs 118 live in n8n production
- Docker redeploy = CATASTROPHIC DATA LOSS
- **Impact**: Full pipeline failure on any container restart

**Bug N2: Only 35 workflows defined in git**

- Directory: `/app/guardspine/n8n-workflows/definitions/`
- 35 files vs 118 live
- ~50 workflows created via UI, never exported
- **Impact**: Institutional knowledge locked in n8n UI, zero version control

**Bug N3: N8N-WORKFLOW-PLAN.md severely outdated**

- Claims 11 workflows tracked; actually ~35 in definitions/
- Rest are UI-only
- No reliable source of truth

**Bug N4: Pilot Pipeline (P2) webhook stubbed**

- File: `/app/guardspine/extensions/n8n-pipeline/plugin.js` shows webhook endpoint registered
- Workflow definition shows `check_pilot_repos`, `check_evidence_bundles`, `generate_pilot_report` all hardcoded as stubs
- **Impact**: Pilot automation non-functional

**Bug N5: Morning Brief (P8) webhook stubbed**

- Actions: `gather_data`, `format_brief`, `deliver_brief` all return mock data
- **Impact**: Leadership briefings empty

**Bug N6: No CI/CD for workflow definitions**

- Changes to n8n workflows are not version-controlled
- Rollback requires manual UI restoration from n8n backup

**Bug N7: Cache resolution edge case in resolveWorkflowId()**

- File: `/app/guardspine/extensions/n8n-pipeline/plugin.js` line 219-254
- If cache expires between name lookup and ID resolution, returns unverified ID
- Syntax: `if (Date.now() <= workflowCacheExpiry) return nameOrId` (logic is backwards — should be `>=`)
- **Impact**: Wrong workflow executed if cache expires mid-resolution

### Fixes (Ordered by Blast Radius)

#### Phase 1: Export All Workflows from n8n (CRITICAL)

**Time: 2-3 hours**

1. **Create export script**

   ```bash
   #!/bin/bash
   # /app/guardspine/n8n-workflows/export-all.sh
   N8N_API_KEY="${N8N_API_KEY}"
   N8N_URL="https://n8n-production-7528.up.railway.app"

   curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
     "$N8N_URL/api/v1/workflows?limit=200" | \
     jq '.data[] | {id: .id, name: .name}' | \
     while read -r workflow; do
       id=$(echo "$workflow" | jq -r '.id')
       name=$(echo "$workflow" | jq -r '.name' | sed 's/ /-/g' | tr '[:upper:]' '[:lower:]')
       curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
         "$N8N_URL/api/v1/workflows/$id" > "definitions/$id-$name.json"
       echo "Exported: $name ($id)"
     done
   ```

2. **Run export**
   ```bash
   cd /app/guardspine/n8n-workflows
   bash export-all.sh
   git add definitions/
   git commit -m "chore: export all 118 workflows from production n8n"
   ```

#### Phase 2: Update Docker Importer (HIGH)

**Time: 1-2 hours**

1. **Create import-all.py**

   ```python
   # /app/guardspine/n8n-workflows/import-all.py
   import json, os, glob, urllib.request
   from pathlib import Path

   N8N_API_KEY = os.environ["N8N_API_KEY"]
   N8N_URL = "http://n8n.railway.internal:5678"

   definitions = glob.glob("definitions/*.json")
   for defpath in sorted(definitions):
       with open(defpath) as f:
           wf = json.load(f)

       # POST to n8n
       req = urllib.request.Request(
           f"{N8N_URL}/api/v1/workflows",
           data=json.dumps(wf).encode(),
           headers={
               "X-N8N-API-KEY": N8N_API_KEY,
               "Content-Type": "application/json"
           },
           method="POST"
       )
       try:
           resp = urllib.request.urlopen(req, timeout=30)
           result = json.loads(resp.read())
           wf_id = result.get("id")
           print(f"✓ {wf['name']} ({wf_id})")

           # Activate if active in export
           if wf.get("active"):
               act_req = urllib.request.Request(
                   f"{N8N_URL}/api/v1/workflows/{wf_id}",
                   data=json.dumps({"active": True}).encode(),
                   headers={
                       "X-N8N-API-KEY": N8N_API_KEY,
                       "Content-Type": "application/json"
                   },
                   method="PATCH"
               )
               urllib.request.urlopen(act_req, timeout=10)
       except Exception as e:
           print(f"✗ {wf['name']}: {e}")
   ```

2. **Update Dockerfile**
   ```dockerfile
   # /app/guardspine/n8n-workflows/importer/Dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY definitions/ ./definitions/
   COPY import-all.py .
   RUN chmod +x import-all.py
   CMD python import-all.py
   ```

#### Phase 3: Fix resolveWorkflowId Cache Logic (HIGH)

**Time: 15 minutes**

File: `/app/guardspine/extensions/n8n-pipeline/plugin.js` line 241-242

**BEFORE:**

```javascript
// Force-refresh cache once in case workflow was just created
if (Date.now() <= workflowCacheExpiry) {
  // ← WRONG: refreshes on fresh cache
  // Cache is fresh but name not found, try raw
  return nameOrId;
}
```

**AFTER:**

```javascript
// If cache is NOT fresh, force-refresh once
if (Date.now() >= workflowCacheExpiry) {
  // ← FIXED
  await refreshWorkflowCache();
  if (workflowNameCache && workflowNameCache[nameOrId]) {
    return workflowNameCache[nameOrId];
  }
}
```

#### Phase 4: Implement Pilot & Morning Brief (MEDIUM)

**Time: 4-5 hours**

1. **P2 - Pilot Pipeline: Add real workflow definition**
   - Move stub endpoints to `/api/v2/pilot-internal/...` (for testing)
   - Implement real `check_pilot_repos` (query GitHub API for pilot repos)
   - Implement `check_evidence_bundles` (query Paperclip for evidence)
   - Implement `generate_pilot_report` (merge + format findings)

2. **P8 - Morning Brief: Add real workflow definition**
   - Collect metrics from W3, W4, W31
   - Format as Slack Block Kit
   - Post to #leadership-brief channel

#### Phase 5: Add Workflow CI/CD (MEDIUM)

**Time: 2-3 hours**

1. **Create GitHub Actions workflow**

   ```yaml
   # .github/workflows/n8n-export-and-commit.yml
   name: Export n8n Workflows
   on:
     schedule:
       - cron: "0 2 * * *" # Daily at 2 AM UTC
   jobs:
     export:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Export workflows
           env:
             N8N_API_KEY: ${{ secrets.N8N_API_KEY }}
           run: |
             cd guardspine/n8n-workflows
             bash export-all.sh
         - name: Commit if changed
           run: |
             git config user.email "bot@guardspine.ai"
             git config user.name "GuardSpine Workflow Bot"
             git add guardspine/n8n-workflows/definitions/
             git commit -m "chore: auto-export n8n workflows" || true
             git push
   ```

2. **Add GitOps deployment check**
   - On PR: validate all workflows in `definitions/` have unique IDs
   - On merge: trigger `import-all.py` in n8n (or Railway webhook)

---

## Cross-Cutting Concerns

### Issue X1: Single Points of Failure Are Architectural, Not Just Config

**Problem**: Even with fixes above, a single n8n, LiteLLM, or Postgres instance is still a SPOF.

**Mitigations (within Railway constraints)**:

1. **Postgres**: Use Railway managed replication (enable read replicas for telemetry reads)
2. **LiteLLM**: Deploy a second instance behind a round-robin DNS entry
3. **n8n**: Use n8n Cloud's multi-tenant deployment OR split workflows across n8n + Temporal

### Issue X2: Observability Gaps

- No alerts for connection pool exhaustion
- No alerts for table growth rate
- No alerts for LiteLLM fallback failures

**Fix**: Add telemetry events in each SPOF on error/warning:

```python
# decision-engine: log pool exhaustion
if not _pool.closed:
    size = _pool._used + _pool._pool.qsize()
    if size > 18:
        log_telemetry("warning", "connection_pool_near_capacity", {"size": size})
```

---

## Implementation Phases

### Phase 1: Immediate (next 2 days)

- [P1] Fix decision-engine connection pooling
- [L1] Remove duplicate gpt-5.4, fix embedding aliases
- [N1] Export all 118 workflows to git

### Phase 2: Urgent (next week)

- [P2] Add retention policies and fix W18
- [P3] Create missing indexes
- [N7] Fix resolveWorkflowId cache logic
- [L2] Add fallbacks to LiteLLM config

### Phase 3: Important (next 2 weeks)

- [P4] Implement role-based Postgres access
- [N2] Update Docker importer to include all 118 workflows
- [N4/N5] Implement Pilot & Morning Brief endpoints

### Phase 4: Nice-to-have (next month)

- [N6] Full CI/CD for n8n workflows
- [X1/X2] Deploy HA replicas for SPOF services

---

## Testing Checklist

- [ ] Connection pool under load: 100 concurrent requests to decision-engine
- [ ] Retention cleanup: Verify activity_log rows deleted after 30 days
- [ ] Embedding dimension: Verify memory queries use 1536-dim vectors
- [ ] Workflow export: All 118 workflows in definitions/ match production
- [ ] resolveWorkflowId: Test cache expiry scenarios
- [ ] Fallbacks: Unplug free-sim, verify haiku fallback kicks in

---

## Estimated Effort

| Task                              | Hours    | Priority |
| --------------------------------- | -------- | -------- |
| P1: Connection pooling            | 1.5      | CRITICAL |
| P2: Retention + indexes           | 4        | CRITICAL |
| P4: RBAC                          | 2.5      | MEDIUM   |
| L1: Duplicate models + embeddings | 0.5      | CRITICAL |
| L2: Fallbacks                     | 0.25     | HIGH     |
| N1: Export 118 workflows          | 2        | CRITICAL |
| N2: Update importer               | 1.5      | HIGH     |
| N7: Fix cache logic               | 0.25     | HIGH     |
| N4/N5: Pilot + Brief impl         | 5        | MEDIUM   |
| **Total**                         | **17.5** | —        |

**Parallel track**: P+L+N tasks can run concurrently. Total wall-clock time: ~5 days if done as focused sprint.
