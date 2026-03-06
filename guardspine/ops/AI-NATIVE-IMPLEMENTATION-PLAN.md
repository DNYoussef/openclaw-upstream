# GuardSpine AI-Native Operating Plan v5

## March 5, 2026

---

## WHAT THIS IS

An AI-assisted founder operating system for a two-person pre-revenue startup.
Not an autonomous company. Not a platform. Not departments.

Two founders with an aggressive machine-assisted operating model:

- Humans do judgment, relationships, commitments, and trust.
- Machines do research, drafting, data assembly, and repetitive ops.
- Every machine action either saves founder time or improves conversion. If it does neither within 2 weeks, delete it.

---

## ONE GOOD ABSTRACTION

```
OpenClaw (messy creative work)
    |
    v
n8n (deterministic pipeline + quality gates)
    |
    v
Human approval (on anything with real consequences)
```

That is the entire architecture. Everything else is implementation detail.

- **OpenClaw** improvises: research prospects, draft messages, browse websites, compose novel tool chains.
- **n8n** governs: validate output, route by type, enforce quality gates, generate evidence bundles, notify Slack.
- **Humans** decide: approve outreach to real people, commit to meetings, make promises.

Both run on Railway (always-on, 24/7). David's machine is dev-only.
Model calls route through LiteLLM (credential isolation, cost ceiling).
Deploys go through GitHub -> codeguard-action -> Railway auto-build.

---

## THREE BUSINESS LOOPS (Nothing Else Until These Work)

### Loop 1: Lead Loop

Research prospect -> draft follow-up -> prepare meeting brief.

```
OpenClaw cron (2 AM):
  - Pick next 5-10 prospects from outreach DB
  - Research each (company site, news, tech stack)
  - Draft personalized follow-up per prospect
  - Package as structured JSON
       |
       v
n8n "Lead Pipeline":
  - Validate: word count, banned terms, swap test
  - Route by lane (buyer/builder/investor/connector)
  - If sending to a real person: queue for human approval
  - Store evidence bundle
  - Post to Slack #ops
       |
       v
David reviews in morning:
  - Approve/edit/reject each draft
  - Send approved messages
```

**Business metric:** Warm lead response latency (hours from signal to follow-up).

### Loop 2: Pilot Loop

Collect repo/PR data -> generate proof case -> assemble evidence.

```
OpenClaw heartbeat (every 30 min):
  - Monitor pilot repos for new PRs
  - Run codeguard-action review
  - Collect evidence: risk tier, findings, remediation
       |
       v
n8n "Pilot Pipeline":
  - Generate evidence bundle from review
  - Track: PRs reviewed, risks caught, false positive rate
  - Post summary to Slack #product
       |
       v
David/Igor:
  - Use evidence for customer proof case
  - "Here is what codeguard caught on YOUR repo this week"
```

**Business metric:** Pilot activation time. Proof-case turnaround time.

### Loop 3: Ops Loop

Daily summary -> blockers -> next actions.

```
OpenClaw cron (6 AM):
  - Query: what happened overnight?
  - Query: what meetings are today?
  - Query: what is blocked and by whom?
  - Compile into morning brief
       |
       v
n8n "Morning Brief":
  - Format summary
  - Post to Slack #ops
       |
       v
David/Igor:
  - Read brief, adjust day's priorities
```

**Business metric:** Founder hours reclaimed per week.

---

## NORTH STAR METRICS (Not Out-of-Loop Ratio)

Out-of-loop ratio rewards autonomy theater. These reward business outcomes:

| Metric                     | What It Measures                                                  | Target           |
| -------------------------- | ----------------------------------------------------------------- | ---------------- |
| Warm lead response latency | Hours from signal to personalized follow-up                       | <24 hrs          |
| Meeting-prep time saved    | Minutes David does NOT spend on research before calls             | 30+ min/meeting  |
| Pilot activation time      | Days from "interested" to codeguard running on their repo         | <3 days          |
| Proof-case turnaround      | Days from pilot data to formatted proof case                      | <2 days          |
| Founder hours reclaimed    | Hours/week freed by machine-assisted ops                          | 10+ hrs/week     |
| Pilot conversion rate      | % of pilots that become paying customers                          | Track from day 1 |
| Escaped-error count        | Messages sent with wrong info, missed follow-ups, broken promises | 0                |

---

## PHASE 1: SECURE THE BASE (Days 1-3)

Before any machine touches the outside world.

| #   | Action                                                                     | Time    |
| --- | -------------------------------------------------------------------------- | ------- |
| 1   | Railway project + Team plan (David + Igor)                                 | 15 min  |
| 2   | Deploy LiteLLM on Railway (Docker image). ONLY service with raw API keys.  | 1 hr    |
| 3   | Deploy OpenClaw on Railway (via GitHub). Proxy key only, $10/day budget.   | 1-2 hrs |
| 4   | Deploy n8n on Railway (Docker image). Persistent volume. Webhook auth.     | 1-2 hrs |
| 5   | Verify internal networking (all services can reach each other)             | 30 min  |
| 6   | Codeguard-action on GitHub repos. Branch protection on main.               | 30 min  |
| 7   | Cloudflare Access on n8n UI (GitHub OAuth, David + Igor only)              | 30 min  |
| 8   | Slack workspace + channels (#ops, #alerts) + bot                           | 30 min  |
| 9   | File incorporation via Clerky                                              | 1 hr    |
| 10  | Follow-ups: Sanjay, Catoya, Logan MOU, Andy trial prep, Jason/Igor meeting | ongoing |

**Rules during Phase 1:**

- No external autonomous actions. Machine drafts, human sends.
- No browsing in production until prompt injection defenses are tested (SEC-3).
- No ClawHub skill installs. Only skills you wrote and reviewed.
- Content drafter is the ONLY skill deployed.

**Exit criteria:** 4 Railway services running. Codeguard reviewing PRs. n8n behind Cloudflare Access. Webhook auth on all endpoints. Incorporation filed. Follow-ups sent (by humans).

---

## PHASE 2: THREE LOOPS LIVE (Days 4-10)

Build the three loops. Nothing else.

| #   | Action                                                                 | Time       |
| --- | ---------------------------------------------------------------------- | ---------- |
| 1   | Build content drafter skill (pure LLM, no browser)                     | 2-3 hrs    |
| 2   | Build Lead Pipeline in n8n (webhook -> gates -> approval -> Slack)     | 2-3 hrs    |
| 3   | Wire OpenClaw cron -> n8n webhook (Lead Loop end-to-end)               | 1-2 hrs    |
| 4   | First overnight run: 5 prospects, review next morning                  | 1 hr setup |
| 5   | Build pilot monitoring (codeguard on pilot repos, evidence collection) | 2-3 hrs    |
| 6   | Build morning brief (daily summary -> Slack #ops)                      | 1-2 hrs    |
| 7   | Run all 3 loops for 3 nights. Fix what breaks each morning.            | 3 mornings |

**Rules during Phase 2:**

- Every loop output reviewed by a human before any external action.
- If a loop produces garbage, fix it or turn it off. Do not add complexity.
- No new skills, no new tools, no new infrastructure. Only the 3 loops.

**Exit criteria:** All 3 loops running overnight. David reviews output each morning in <30 minutes. At least one real follow-up improved by machine research. At least one pilot proof case assembled by machine.

---

## PHASE 3: MEASURE AND PRUNE (Week 2-3)

Each loop gets 2 weeks to prove business value. If it does not save real founder time or improve conversion, delete it.

| Loop       | Keep If                                                                          | Delete If                                                                  |
| ---------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Lead Loop  | Response latency drops. Follow-ups are higher quality. David sends more of them. | Drafts require so much editing they take longer than writing from scratch. |
| Pilot Loop | Proof cases assembled faster. Pilots see value in evidence.                      | Nobody looks at the evidence bundles. Pilots do not care.                  |
| Ops Loop   | Morning brief actually changes David's day.                                      | David skips reading it after 3 days.                                       |

**Add complexity ONLY when a working loop hits a specific bottleneck:**

| Bottleneck                              | Then Add                                              | Not Before                                             |
| --------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------ |
| Same prospect contacted twice           | Duplicate detection (simple DB query, not Memory-MCP) | Loop 1 is sending real messages                        |
| Draft quality plateaus                  | A/B test different prompts (manual, not DSPy)         | 50+ messages sent with tracked outcomes                |
| Need SOC 2 evidence for a real customer | Evidence bundle schema + R2 storage                   | A customer asks for it                                 |
| Too many skills to track                | APPROVED-SKILLS.md file (not a quarantine pipeline)   | >10 custom skills in production                        |
| Prompt injection is a real risk         | SEC-3 content sanitization                            | Browser-based skills in production                     |
| Memory would measurably help            | Simple key-value store (not 3-layer RAG)              | "I contacted this person 2 weeks ago" happens 3+ times |

---

## WHAT GOT CUT (AND WHEN IT COMES BACK)

| Cut                                                  | Why                                                             | Comes Back When                                                                 |
| ---------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Department functions (Revenue, Product, Finance, CS) | Org-chart cosplay for 2 people                                  | Team grows to 5+ with actual department owners                                  |
| Executive synthesis                                  | No departments to synthesize across                             | Never, unless departments exist                                                 |
| Board Meeting Protocol                               | No board, no multi-agent decisions needed                       | 3+ agents making conflicting recommendations                                    |
| Critic function                                      | Second-order machinery before first-order loops proven          | Escaped-error count rises above 0                                               |
| Tool Registry                                        | Premature when you have <10 tools                               | >20 tools and losing track                                                      |
| Meta-governance                                      | Governance of governance before governance exists               | Governance volume makes manual review impossible                                |
| Skill Factory + Quarantine                           | Building a skill factory before you have 3 working skills       | >10 custom skills, community skill installs needed                              |
| DSPy self-improvement                                | Optimizing prompts before you know which prompts matter         | 50+ scored examples AND manual A/B testing has plateaued                        |
| Memory-MCP on Railway                                | Big image, big surface, weak immediate payoff                   | Duplicate contacts happen 3+ times, or memory measurably improves draft quality |
| Beads                                                | "Probably not, maybe JSONL" means aspirational not foundational | Cross-function dependency tracking is a real daily problem                      |
| SOC 2 Track 10                                       | No customers requiring compliance yet                           | A live pilot explicitly requires it                                             |
| Observability dashboards                             | Nobody looks at dashboards when there is nothing to look at     | 3+ loops running for 2+ weeks                                                   |
| Out-of-loop ratio metric                             | Rewards autonomy theater, not business outcomes                 | All 7 business metrics are green                                                |

---

## TECHNOLOGY STACK (Minimal)

### Production (Railway, always-on)

| Service  | Source                                 | Purpose                                |
| -------- | -------------------------------------- | -------------------------------------- |
| OpenClaw | GitHub repo, auto-deploy               | Creative work + cron scheduling        |
| n8n      | Docker image `n8nio/n8n`               | Governed pipelines + quality gates     |
| LiteLLM  | Docker image `ghcr.io/berriai/litellm` | Model routing + cost ceiling ($10/day) |

### Infrastructure

| Tool                      | Purpose                                    |
| ------------------------- | ------------------------------------------ |
| Railway Team plan         | Hosting, $20/user/mo, audit log            |
| GitHub + codeguard-action | CI/CD, branch protection, evidence bundles |
| Cloudflare Access (free)  | Zero-trust auth for n8n UI                 |
| Cloudflare R2 (free)      | Evidence bundle storage (when needed)      |
| Slack (free)              | #ops and #alerts channels                  |
| Logfire (free)            | Traces when debugging, not dashboards      |

### Cost

| Item                        | Monthly         |
| --------------------------- | --------------- |
| Railway (3 services + team) | $55-80          |
| Cloudflare                  | $0              |
| LLM API calls               | $50-150         |
| **Total**                   | **$105-230/mo** |

---

## SECURITY (Minimal Viable, Not SOC 2 Theater)

| #     | What                                                   | When                      |
| ----- | ------------------------------------------------------ | ------------------------- |
| SEC-1 | Webhook auth (Bearer token on all n8n webhooks)        | Day 1                     |
| SEC-2 | Credential isolation (only LiteLLM holds raw API keys) | Day 1                     |
| SEC-5 | LiteLLM cost ceiling ($10/day per key, $20/day global) | Day 1                     |
| SEC-7 | Only use skills you wrote and reviewed                 | Day 1                     |
| SEC-3 | Prompt injection defense (content sanitization)        | Before any browsing skill |
| SEC-4 | n8n flow backup to git (nightly export)                | After first flow is built |

Everything else (SOC 2 controls, quarantine pipeline, evidence schemas, 2FA on all services) waits until a customer or pilot requires it.

---

## THE OPENCLAW -> n8n INTEGRATION PATTERN

This is the only architectural pattern that matters.

```
OpenClaw cron: "every day at 2am"
    |
    v
OpenClaw Skill executes
    - research, draft, compile
    - package results as structured JSON
    |
    v
HTTP POST to n8n webhook (http://n8n.railway.internal:5678)
    Authorization: Bearer $WEBHOOK_SECRET
    |
    v
n8n Flow:
    +-- validate JSON schema
    +-- run quality gates
    +-- if real consequences: queue for human approval
    +-- store evidence bundle (when needed)
    +-- post summary to Slack #ops
```

---

## THE GRADUATION PATTERN

Still valid. The only discipline that matters for growing loops:

```
STAGE 1: Human does the work manually, notes the pattern.
STAGE 2: Machine drafts, human reviews and edits everything.
STAGE 3: Machine drafts, human approves or rejects (no editing).
STAGE 4: Machine acts autonomously on low-risk items. Human reviews summary.
```

Each loop starts at Stage 2. Promotion to Stage 3 requires 2 weeks of zero escaped errors. Promotion to Stage 4 requires a month.

---

## SOURCE DOCUMENTS

| Document                              | Role                                                                 |
| ------------------------------------- | -------------------------------------------------------------------- |
| AI-Native Architecture v3.1           | Reference for governance patterns (use when needed, not all at once) |
| Secure Agent Harness Landscape Report | Security checklist (SEC-1 through SEC-7 extracted)                   |
| AI-NATIVE-TASK-BREAKDOWN.md           | Detailed task breakdown for Phase 1 + 2 implementation               |

---

_v5 -- March 5, 2026. Rewritten from v4 per Linus critique: cut department cosplay, cut second-order machinery, focus on 3 business loops with measurable outcomes. Talk is cheap. Show me the conversion, the saved hours, and the pilots._
