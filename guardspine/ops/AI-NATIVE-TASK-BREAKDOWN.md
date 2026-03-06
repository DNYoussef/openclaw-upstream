# AI-Native Operating Plan -- 10-Day Execution

## March 5, 2026

Parent doc: `AI-NATIVE-IMPLEMENTATION-PLAN.md` (v5, three loops, business metrics)

---

## THE RULE

Every task either:

1. Gets the 3 loops running, or
2. Prevents a security breach.

If it does neither, it is not on this list.

---

## PHASE 1: SECURE THE BASE (Days 1-2)

### Day 1 Morning: Infrastructure (all parallel)

| Task    | Action                                                                                                                                                                    | Time   |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| RW-1    | `railway project create guardspine-ai-ops`. Connect GitHub (grant access to `openclaw-upstream`).                                                                         | 10 min |
| TEAM-1  | Create Railway Team "guardspine". Transfer project. Invite Igor as Admin.                                                                                                 | 15 min |
| GH-1    | Add `.github/workflows/codeguard.yml` to `openclaw-upstream`. Set `OPENROUTER_API_KEY` repo secret. Branch protection on main (require PR + codeguard pass + 1 approval). | 30 min |
| SLACK-1 | Create Slack workspace. Channels: #ops, #alerts. Create bot app (chat:write, channels:read).                                                                              | 30 min |
| BIZ-1   | Start Clerky incorporation (Delaware C-Corp).                                                                                                                             | 1 hr   |

### Day 1 Afternoon: Deploy 3 Services (sequential after RW-1)

| Task | Action                                                                                                                                                                                                                                                                                                                                | Time    |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| RW-4 | Deploy LiteLLM: Docker image `ghcr.io/berriai/litellm:main-latest`. Set `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `LITELLM_MASTER_KEY`, `PORT=4000`. Set per-key budget: $10/day. Global: $20/day.                                                                                                                                       | 1 hr    |
| RW-2 | Deploy OpenClaw: GitHub repo -> Railway auto-detects Dockerfile. Set `SETUP_PASSWORD`, `PORT=8080`, `OPENCLAW_STATE_DIR=/data/.openclaw`, `OPENCLAW_WORKSPACE_DIR=/data/workspace`, `OPENCLAW_GATEWAY_TOKEN`. Add volume at `/data`. Set `LITELLM_BASE_URL=http://litellm.railway.internal:4000`. Proxy key only -- NOT raw API keys. | 1-2 hrs |
| RW-3 | Deploy n8n: Docker image `n8nio/n8n`. Set `N8N_HOST=0.0.0.0`, `N8N_PORT=5678`, `WEBHOOK_URL=https://<domain>`, `N8N_ENCRYPTION_KEY`. Add volume at `/home/node/.n8n`. Generate webhook secret: `WEBHOOK_SECRET`.                                                                                                                      | 1-2 hrs |

### Day 1 Evening: Security Lockdown

| Task  | Action                                                                                                     | Time   |
| ----- | ---------------------------------------------------------------------------------------------------------- | ------ |
| RW-5  | Verify internal networking: OpenClaw -> n8n, OpenClaw -> LiteLLM, n8n -> LiteLLM.                          | 30 min |
| SEC-1 | Add webhook auth to n8n: first node checks `Authorization: Bearer $WEBHOOK_SECRET`. Reject 401 without it. | 15 min |
| CF-3  | Cloudflare Access on n8n public URL. GitHub OAuth. Allow David + Igor only.                                | 30 min |

**Day 1 exit:** 3 services running on Railway. Codeguard on PRs. n8n behind auth. Webhook protected. Incorporation started.

### Day 2: Verify + Business Follow-ups

| Task  | Action                                                                                                                                                              | Time    |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| OC-1  | Configure OpenClaw via `/setup` wizard. Model routing to LiteLLM. Test cron (log "alive" every 60s). Test a built-in skill.                                         | 1-2 hrs |
| SEC-4 | Export n8n flows as JSON. Create private repo `guardspine-n8n-flows`. Commit. Set up nightly export (manual for now, automate later).                               | 30 min  |
| BIZ-2 | Send follow-ups: Sanjay Nagaraj, Catoya materials, Logan MOU status, Andy trial prep (Mar 9), Jason/Igor meeting prep (Mar 9). **Humans send these, not machines.** | 2-3 hrs |

**Day 2 exit:** OpenClaw configured and responding. n8n flows backed up. All urgent follow-ups sent.

---

## PHASE 2: THREE LOOPS (Days 3-7)

### Loop 1: Lead Loop (Days 3-4)

| Task  | Action                                                                                                                                                                                                                                                                                                                          | Time    |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| OC-2  | Build content drafter skill. Input: prospect JSON (company, contacts, lane, context). Output: structured JSON with messages, quality_score, gate_results. Quality gates: word count (100-300), banned terms, swap test. Test with 5 real prospects. **No browser. Pure LLM only.**                                              | 2-3 hrs |
| N8-1  | Build Lead Pipeline in n8n. Nodes: Webhook (POST `/webhook/lead-intake`, check auth header) -> Validate JSON schema -> Word count gate -> Banned terms gate -> Swap test gate -> Route by lane -> IF risk >= 2: post to Slack for approval -> Generate evidence JSON -> Post summary to Slack #ops -> Error trigger -> #alerts. | 2-3 hrs |
| INT-1 | Wire OpenClaw cron -> n8n webhook. Configure cron: 2 AM EST (7 AM UTC). Test full chain manually first: trigger skill, watch n8n execution log, verify Slack message, verify evidence JSON. Then enable cron.                                                                                                                   | 1-2 hrs |

**Test:** POST test prospect to webhook. Assert: n8n executes, gates fire, Slack #ops gets message, evidence JSON created. POST without auth header. Assert: 401 rejected.

### Loop 2: Pilot Loop (Day 5)

| Task | Action                                                                                                                                                                                                                          | Time    |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| N8-2 | Build Pilot Pipeline in n8n. Trigger: webhook POST `/webhook/pilot-review`. Input: PR data from codeguard-action. Nodes: parse review output -> extract risk tier + findings -> generate evidence bundle -> post to Slack #ops. | 2 hrs   |
| OC-3 | Configure OpenClaw heartbeat (every 30 min) to check pilot repos. If new PRs: trigger codeguard review, POST results to n8n pilot webhook. **If no pilot repos yet:** build this against your own repos as proof case.          | 1-2 hrs |

**Test:** Open a PR on `openclaw-upstream`. Assert: codeguard reviews it, n8n processes the results, Slack gets summary.

### Loop 3: Ops Loop (Day 6)

| Task | Action                                                                                                                                                       | Time    |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| OC-4 | Build morning brief skill. Queries: Slack #ops last 24h summary, today's calendar (manual input for now), any blocked items. Compiles into structured brief. | 1-2 hrs |
| N8-3 | Build Morning Brief flow in n8n. Cron: 6 AM EST (11 AM UTC). Receives brief JSON -> formats -> posts to Slack #ops.                                          | 1 hr    |

**Test:** Trigger morning brief manually. Assert: Slack gets formatted summary. Read it. Is it useful? If not, fix it now.

### First Overnight Run (Day 6 evening)

| Task  | Action                                                                                                                                                          | Time |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| INT-2 | Enable all 3 crons. Lead Loop at 2 AM, Ops Loop at 6 AM. Pilot Loop runs on heartbeat. Set up dead-man's switch: if no Slack message by 7 AM, something failed. | 1 hr |

**Day 7: Morning Review**

Read Slack #ops. Did all 3 loops fire? Review lead drafts. Are they sendable? Review pilot evidence. Is it useful? Review morning brief. Did it save time?

Fix what broke. Run again night 2 and night 3.

---

## PHASE 3: MEASURE AND PRUNE (Days 8-10+)

### Day 8-10: Track Business Metrics

| Metric                     | How to Measure                              | Source                         |
| -------------------------- | ------------------------------------------- | ------------------------------ |
| Warm lead response latency | Time from prospect signal to follow-up sent | Slack timestamps + outreach DB |
| Meeting-prep time saved    | David self-reports before/after             | Manual log                     |
| Pilot activation time      | Days from "interested" to codeguard running | Git timestamps                 |
| Proof-case turnaround      | Days from pilot data to formatted evidence  | n8n execution timestamps       |
| Founder hours reclaimed    | Hours/week freed                            | David self-reports weekly      |
| Escaped-error count        | Wrong info sent, missed follow-ups          | Manual log (target: 0)         |

### The 2-Week Rule

Each loop gets 2 weeks to prove value. At Day 14:

| If                                                  | Then                                                           |
| --------------------------------------------------- | -------------------------------------------------------------- |
| Lead Loop saves time AND improves follow-up quality | Keep. Consider Stage 3 promotion (approve/reject, no editing). |
| Lead Loop drafts need heavy editing                 | Fix prompts. If still bad after another week, delete.          |
| Pilot Loop produces evidence customers care about   | Keep. Build toward automated proof case assembly.              |
| Pilot Loop evidence sits unread                     | Delete. Do proof cases manually.                               |
| Ops Loop brief changes David's day                  | Keep.                                                          |
| David skips reading the brief                       | Delete.                                                        |

---

## ADD COMPLEXITY ONLY AT THESE TRIGGERS

| Trigger                                      | Add                                                 | Not Before                              |
| -------------------------------------------- | --------------------------------------------------- | --------------------------------------- |
| Same prospect contacted twice                | Duplicate check (SQL query on outreach DB)          | Lead Loop sending real messages         |
| Draft quality plateaus at 50+ messages       | Manual A/B testing different prompt approaches      | 50+ messages with tracked outcomes      |
| Customer asks for SOC 2 evidence             | Evidence bundle schema (SEC-8) + R2 storage         | A real customer asks                    |
| Browser-based research needed                | SEC-3 prompt injection defense, then browsing skill | Lead Loop proven without browser        |
| 3+ instances of "I already contacted them"   | Simple key-value memory (SQLite, not Memory-MCP)    | Pattern confirmed                       |
| >10 custom skills and losing track           | APPROVED-SKILLS.md file                             | Actually have >10 skills                |
| Manual A/B testing plateaus at 200+ examples | Evaluate DSPy                                       | Manual optimization exhausted           |
| Governance volume overwhelming               | Quarantine pipeline, meta-governance                | Actually overwhelmed, not theoretically |

---

## KILL LIST (Deferred From v4)

Everything below was in the previous plan. All cut. Comes back only at documented trigger.

| Cut Item                                             | Previous Location     | Trigger to Revisit                                                |
| ---------------------------------------------------- | --------------------- | ----------------------------------------------------------------- |
| Memory-MCP on Railway                                | Track 5B (7 tasks)    | Duplicate contacts 3+ times, or memory measurably improves drafts |
| Beads integration                                    | Track 5 (2 tasks)     | Cross-function dependencies are a real daily problem              |
| Department functions (Revenue, Product, Finance, CS) | Week 2 plan           | Team grows to 5+                                                  |
| Executive synthesis                                  | Week 3 plan           | Departments exist                                                 |
| Board Meeting Protocol                               | Week 3 plan           | 3+ agents making conflicting recommendations                      |
| Critic function                                      | Week 3 plan           | Escaped-error count > 0                                           |
| Tool Registry                                        | Week 3 plan           | >20 tools                                                         |
| Scoped Context Rules                                 | Week 3 plan           | Agents seeing irrelevant context                                  |
| Cross-Agent Invocation                               | Week 3 plan           | Agents need to call each other                                    |
| Meta-governance                                      | Week 4 plan           | Governance volume overwhelming                                    |
| Ideal State Document                                 | Week 4 plan           | Enough telemetry to define "good"                                 |
| Skill Factory + Quarantine                           | Track 11 (7 tasks)    | >10 skills, community installs needed                             |
| DSPy self-improvement                                | Track 12 (5 tasks)    | Manual A/B testing plateaus at 200+ examples                      |
| SOC 2 evidence automation                            | Track 10              | A customer requires it                                            |
| SOC 2 control documentation                          | Track 10              | A customer requires it                                            |
| Observability dashboards                             | Track 6               | 3+ loops running 2+ weeks                                         |
| Cloudflare D1 migration                              | Track 2               | Outreach DB size exceeds local SQLite limits                      |
| Cloudflare R2 evidence storage                       | Track 2               | Customer requires immutable evidence trail                        |
| Railway service hardening (SEC-9)                    | Track 9               | Before first paying customer                                      |
| Out-of-loop ratio metric                             | Observability section | All 7 business metrics are green                                  |
| GlobalMOO                                            | Arch doc 9.2          | Optimization targets formally defined                             |
| Comprehension Lock-In                                | Arch doc 15           | 30+ days operational history AND memory proven useful             |
| Silent Drift Detection                               | Arch doc FM5          | Evidence bundle versions pinned                                   |

---

## DAILY SCHEDULE TEMPLATE (Once Loops Are Running)

```
7:00 AM  Read morning brief in Slack #ops (5 min)
7:05 AM  Review overnight lead drafts (15-20 min)
         - Approve, edit, or reject each
         - Send approved messages
7:30 AM  Review pilot evidence (10 min)
         - Flag anything to share with prospects
7:40 AM  Check #alerts for failures (2 min)
8:00 AM  Start founder work: calls, meetings, strategy, relationships
```

Total machine-assisted ops time: ~35 minutes/morning.
Everything else is human judgment work that machines cannot do.

---

_v5 -- March 5, 2026. Rewritten from v4. Cut 40+ tasks down to 20. Three business loops, not twelve infrastructure tracks. Business metrics, not autonomy ratios. Add complexity only at documented triggers. The company runs at machine speed without handing the keys to a hallucinating intern._
