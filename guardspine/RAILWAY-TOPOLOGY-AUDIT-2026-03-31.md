# GuardSpine Railway Topology Audit — 2026-03-31

**Requested by:** David Youssef  
**Method:** 14 parallel deep-dive agents (13 services + 1 wiring specialist)  
**Duration:** ~17 minutes total

---

## Executive Summary

The GuardSpine deployment runs **13 services on Railway**, with the OpenClaw Gateway as the central hub. The architecture is **sophisticated and well-designed** but has **critical gaps** in authentication, redundancy, and data retention that require immediate attention.

**Top-line findings:**

- 🔴 **5 critical risks** requiring immediate action
- 🟡 **12 high/medium risks** requiring planned fixes
- 🟢 **Core governance architecture is solid** (deny-by-default, hash-chained evidence)
- ⚠️ **1 service is quarantined** (Ops Portal — fake data)
- ⚠️ **1 service is undeployed** (GDrive Connector — code exists, not wired)

---

## The 13 Services

### 1. OpenClaw Gateway

- **Role:** Central hub — all user messages flow through here
- **Runtime:** Node.js v22, port 18789, non-root user via `gosu`
- **Channel:** Slack only (`allowFrom: ["*"]`)
- **Model:** Claude Opus 4.6 (fallback: Sonnet → GPT-5.4 → Haiku)
- **Plugins:** GuardSpine, n8n-pipeline, lossless-claw
- **Public URL:** `openclaw-production-e5a2.up.railway.app`
- **Config:** Immutable — baked config restored from image at every boot
- **Risks:**
  - 🟡 `allowFrom: ["*"]` on Slack — any user can interact
  - 🟡 Auth profiles baked into Docker image
  - 🟢 Good: non-root runtime, privilege drop, immutable config

### 2. LiteLLM

- **Role:** Central AI gateway routing to Anthropic, OpenAI, Google Gemini, OpenRouter
- **Version:** v1.82.3-stable.patch.2 (pinned to avoid TeamPCP supply chain compromise)
- **Risks:**
  - 🔴 Duplicate `gpt-5.4` entry in config
  - 🟡 Missing fallbacks for MiroFish simulation models and `gpt-5.4-nano`
  - 🟡 Misleading `deepseek-chat` alias (routes to LLaMA 3B, not DeepSeek)
  - 🟡 Embedding aliases redirect to Gemini (768-dim vs OpenAI 1536-dim)
  - 🟡 Legacy OpenRouter aliases now route to paid Anthropic models (cost creep)

### 3. n8n

- **Role:** Deterministic automation backbone — handles 95% of work
- **Workflows:** 118 live (Heartbeat: 13, Weekly/Daily: 51, Monthly: 31, Agent: 10, Pipeline: 4, Four-Fit: 6, Other: 3)
- **Risks:**
  - 🔴 Single point of failure for 95% of automation — no failover
  - 🔴 No CI/CD — 118 live workflows have diverged from git (~50 files); UI edits not persisted
  - 🟡 Docker importer covers only 9 of 118 workflows — data loss risk on redeploy
  - 🟡 Pilot and Morning Brief webhooks fully stubbed
  - 🟡 `N8N-WORKFLOW-PLAN.md` severely outdated (tracks only 11 workflows)

### 4. Postgres

- **Role:** Central database for all services
- **Tables:** prospects (39 cols), telemetry_events, decision_journal, case_traces, agents, heartbeat_runs, issues, issue_comments, activity_log, narrowcast tables, KPI views
- **Connections:** telemetry-api (pooled 1-10), decision-engine (no pooling), soak-monitor (pg_isready), n8n (via telemetry-api proxy)
- **Risks:**
  - 🔴 Decision-engine creates fresh connection per request — no pooling
  - 🔴 Unbounded growth on activity_log, issues, heartbeat_runs — no retention
  - 🟡 No indexes on telemetry_events (service, event_type, ts)
  - 🟡 All services share same DATABASE_URL credential — no role separation
  - 🟡 No documented backup RTO/RPO; W18 retention cleaner audits only, doesn't delete
  - 🟡 case_traces table created but never written to (dead code)

### 5. Paperclip

- **Role:** Agent task manager and org chart
- **Port:** 3100 internal
- **Agents:** 13 registered (7 active "operating council", 6 deactivated)
- **Models:** Claude for creative work, GPT-5.4 for critic work
- **Risks:**
  - 🔴 6 heartbeat workflows (H8-H13) exist for deactivated agents — if active in n8n, they could wake inactive agents
  - 🟡 CMO and Content Director agents may run on stale `SHARED-CONTEXT.md`
  - 🟡 `update_all_agents.py` bypasses Paperclip API with direct DB writes

### 6. GuardSpine Governance Kernel

- **Role:** Deny-by-default governance with L0-L4 risk tiers
- **Architecture:** Two plugins — portable (1252 lines) + production (2369 lines)
- **Council:** 3-model sequential via Ollama (qwen3:8b, qwen3-coder:30b, gpt-oss:20b); split → L3.5 Opus tie-breaker ($5/day budget)
- **Evidence:** SHA256 hash-chained evidence packs per session
- **Risks:**
  - 🔴 **Allowlist bypass** — can downgrade L4→L1 with zero audit trail
  - 🔴 **Frozen paths incomplete** — only `bash` & `apply_patch` checked; `edit`/`write`/`exec` bypass frozen governance files
  - 🟡 Allowlist has no signature/audit trail (plain JSON, no creator/timestamp)
  - 🟡 Evidence pack integrity vulnerable to disk tampering
  - 🟡 Budget bypass possible at midnight UTC (daily reset, not rolling window)
  - 🟡 No rate limiting on council calls (DoS vector)

### 7. Telemetry API

- **Role:** Central event sink and analytics proxy
- **Runtime:** Raw Python `http.server`, single-threaded
- **Port:** 8090 internal
- **Risks:**
  - 🔴 `POST /telemetry` is **unauthenticated** — any internal service can write arbitrary events
  - 🔴 Single-threaded HTTP server — concurrency ceiling
  - 🟡 No indexes on telemetry_events (performance risk)
  - 🟡 64KB body size cap
  - 🟡 Retention only runs on explicit `/sync` calls
  - 🟡 `TELEMETRY-EVENTS.md` out of sync with code

### 8. Decision Engine

- **Role:** Routes decision requests to solver backends (MiroFish, Mieza GTO, pymoo, GuardSpine)
- **Endpoints:** `/health`, `/decide`, `/simulate`, `/solve`, `/optimize`, `/trace/{id}/outcome`
- **Design:** Intentionally LLM-free; supports 9 decision types across 6 domains
- **Risks:**
  - 🟡 `verify_stack` decision_type declared but no handler
  - 🟡 No authentication on any endpoint
  - 🟡 Shallow MiroFish integration vs. documented spec
  - 🟡 Single-connection DB writes (no pooling)

### 9. MiroFish Simulator

- **Role:** Simplified OASIS simulation wrapper
- **Integration:** Called by Decision Engine; uses LiteLLM for LLM reasoning
- **Status:** Active but using simplified wrapper instead of full OASIS pipeline

### 10. Soak Monitor

- **Role:** Health polling daemon — checks 10 services every 5 minutes
- **Runtime:** Pure shell script (`health-check.sh`) on Alpine Linux
- **Checks:** 9 HTTP services + 1 Postgres (via pg_isready)
- **Risks:**
  - 🟡 No direct alerting on failures (relies on Telemetry API consumers)
  - 🟡 Telemetry API downtime → silent data loss
  - 🟡 Sequential 20s timeouts → up to 200s cycle time
  - 🟡 Only 10 of 13 services monitored (Redis, Railway proxy, self not covered)

### 11. Ops Portal

- **Role:** Web UI frontend for Paperclip
- **Port:** 8080 internal
- **Public URL:** `ops-portal-production-bb8b.up.railway.app`
- **Status:** ⚠️ **QUARANTINED** — serves static HTML with fake green dots, not connected to real data
- **Risks:**
  - 🔴 Fake data creates false confidence — masks real failures
  - 🟡 No authentication on public URL
  - 🟡 Source code not found in deployment repo
  - **Rebuild path:** Query telemetry-api `/kpi/*` endpoints for real metrics

### 12. GDrive Connector

- **Role:** Google Drive document monitoring + evidence bundle generation
- **Status:** ⚠️ **NOT DEPLOYED** — code exists, fully implemented, but not wired into Railway
- **Auth:** OAuth 2.0 (credentials on disk, no key vault)
- **Risks:**
  - 🟡 Undeployed code — no production exposure currently
  - 🟡 OAuth credentials stored locally without encryption
  - 🟡 No rate limiting for Google Drive API calls
  - **Decision needed:** Deploy as service, or archive

### 13. Lossless-Claw (LCM)

- **Role:** DAG-based conversation summarization — replaces sliding-window truncation
- **Version:** 0.5.1
- **Storage:** SQLite (`~/.openclaw/lcm.db`)
- **Compaction:** Triggers at 75% context window; 32-message fresh tail preserved
- **Summarizer:** Gemini Flash via LiteLLM ($0.15/M input tokens)
- **Tools:** `lcm_grep`, `lcm_expand`, `lcm_describe`, `lcm_expand_query`
- **Risks:**
  - 🟡 SQLite single-file — no replication, backup needed
  - 🟡 Summarization cost scales with conversation length
  - 🟡 Unlimited incremental depth (-1) may cause slow compaction for very long conversations
  - 🟢 Production-ready, no critical defects

---

## Service Wiring Summary

### Port Map

| Service          | Internal DNS                     | Port  | Health Path |
| ---------------- | -------------------------------- | ----- | ----------- |
| OpenClaw Gateway | openclaw.railway.internal        | 18789 | /health     |
| LiteLLM          | litellm.railway.internal         | 4000  | /health     |
| n8n              | n8n.railway.internal             | 5678  | /healthz    |
| Postgres         | postgres.railway.internal        | 5432  | pg_isready  |
| Paperclip        | paperclip.railway.internal       | 3100  | /api/health |
| Telemetry API    | telemetry-api.railway.internal   | 8090  | /health     |
| Decision Engine  | decision-engine.railway.internal | 8091  | /health     |
| MiroFish Sim     | mirofish-sim.railway.internal    | 8092  | /health     |
| Soak Monitor     | (no HTTP endpoint)               | —     | —           |
| Ops Portal       | ops-portal.railway.internal      | 8080  | /           |

### Dependency Chain (Critical Path)

```
Postgres ← ALL SERVICES (🔴 SPOF #1)
  ├── LiteLLM ← ALL LLM REASONING (🔴 SPOF #2)
  ├── n8n ← 95% AUTOMATION (🔴 SPOF #3)
  │     ├── Heartbeat workflows → Paperclip → Agents
  │     ├── Pipeline webhooks → Outreach/Narrowcast/Pilot
  │     └── Maintenance workflows → DB cleanup, monitoring
  ├── OpenClaw Gateway ← ALL USER INTERACTION
  │     ├── Slack channel (inbound)
  │     ├── GuardSpine governance (tool gating)
  │     ├── LCM context engine (memory)
  │     └── n8n-pipeline plugin (webhook dispatch)
  ├── Telemetry API ← Event ingestion + KPI views
  ├── Decision Engine ← Strategic decisions
  │     └── MiroFish Sim (simulation backend)
  ├── Soak Monitor → Telemetry API (health loop every 5min)
  └── Paperclip ← Agent task management
        └── Ops Portal (quarantined UI)
```

### Auth Between Services

- **LiteLLM:** Bearer token
- **n8n:** X-N8N-API-KEY
- **Postgres:** Connection string (shared credential)
- **Slack:** OAuth bot token
- **Telemetry API:** Optional X-Service-Token (disabled in migration mode!)
- **Decision Engine:** No auth
- **No mTLS** — trust Railway `.railway.internal` LAN only

---

## 🔴 Critical Actions (P0)

| #   | Finding                                     | Service       | Action                                             |
| --- | ------------------------------------------- | ------------- | -------------------------------------------------- |
| 1   | Allowlist bypass (L4→L1 with zero audit)    | GuardSpine    | Sign allowlist, add modification logging           |
| 2   | Frozen paths incomplete (edit/write bypass) | GuardSpine    | Extend frozen-path checks to all write tools       |
| 3   | Unauthenticated POST /telemetry             | Telemetry API | Enforce X-Service-Token even in migration mode     |
| 4   | n8n single point of failure, no CI/CD       | n8n           | Git-sync 118 workflows; document restore procedure |
| 5   | Ops Portal fake data                        | Ops Portal    | Label "Demo" or take offline until rebuilt         |

## 🟡 High-Priority Actions (P1)

| #   | Finding                          | Service       | Action                                                       |
| --- | -------------------------------- | ------------- | ------------------------------------------------------------ |
| 6   | Decision-engine connection leak  | Postgres      | Add connection pooling                                       |
| 7   | Unbounded table growth           | Postgres      | Implement retention for activity_log, issues, heartbeat_runs |
| 8   | Missing telemetry_events indexes | Postgres      | Add (service, ts), (event_type, ts) indexes                  |
| 9   | Deactivated agent heartbeats     | Paperclip/n8n | Deactivate H8-H13 workflows if agents are inactive           |
| 10  | Single-threaded telemetry-api    | Telemetry API | Add gunicorn/uvicorn or rewrite with async                   |
| 11  | Embedding dimension mismatch     | LiteLLM       | Validate 768-dim Gemini embeddings work with Memory MCP      |
| 12  | No backup verification           | Postgres      | Document Railway backup SLA; test restore                    |

---

_Report generated by 14 parallel audit agents on 2026-03-31 13:13–13:30 UTC._
