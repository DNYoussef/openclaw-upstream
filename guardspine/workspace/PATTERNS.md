# PATTERNS.md - Operational Patterns & Best Practices

## The Algorithm (Ideal State Management)

The most powerful pattern in all of AI. Everything we do follows this:

1. **Define ideal state** -- What does perfect look like? Explicit, measurable, verifiable criteria.
2. **Snapshot current state** -- Where are we right now? Unified context from all sources.
3. **Continuous gap closure** -- n8n pipelines + OpenClaw agents migrate current toward ideal.
4. **Verification at every step** -- Ideal state criteria ARE verification criteria. Each is discrete, yes/no.

Previous software: you can MAKE anything. Next software: you can VERIFY anything.
We are the verification layer. Evidence bundles prove the gap is closing.

```
Ideal State (defined in SOPs, KPIs, policies, rubrics)
  |
  v
Gap Analysis (morning brief, heartbeat, n8n metrics)
  |
  v
Migration Actions (n8n pipelines close gaps, OpenClaw handles edge cases)
  |
  v
Verification (GuardSpine evidence packs prove each action was correct)
  |
  v
Updated Current State (Memory MCP, databases, workspace files)
  |
  v
[loop back to Gap Analysis]
```

## Core Architecture Principle

**n8n runs the pipeline. OpenClaw handles the edge cases. GuardSpine verifies everything.**

The company IS the operation graph. Every pipeline (P1-P12) is a node. Every node has metrics. GuardSpine provides evidence at every node.

Every operational pipeline follows the same pattern:

1. **n8n workflow** handles the deterministic path (fetch, filter, classify, route, store, notify) -- 95% of work
2. **OpenClaw agent** monitors for edge cases the workflow can't handle (ambiguous classification, novel inputs, rubric feedback, cross-domain connections) -- 5% of work
3. **GuardSpine** verifies both (evidence packs on writes, council on destructive actions)
4. **Ideal State criteria** define what "correct" means for each node

This is NOT "AI does everything." This is structured automation with AI exception handling and continuous verification.

```
Trigger (cron/webhook/event)
  -> n8n workflow (deterministic: fetch, parse, classify, store, route)
     -> 95% of cases: handled automatically, no AI needed
     -> 5% edge cases: OpenClaw agent called via n8n HTTP node
        -> AI resolves ambiguity, updates rubric, stores learning
  -> GuardSpine verifies all writes/sends (evidence pack)
  -> Gap report: did this action close a gap between current and ideal?
```

---

## Pipeline Catalog (n8n Workflows)

### P1: Inbound Email Scoring Pipeline

**Trigger:** Gmail poll every 10 min (n8n Schedule node)
**n8n handles:** Fetch new emails -> quarantine scan (deterministic regex) -> classify sender domain -> score against rubric YAML -> apply Gmail label -> store in CRM DB -> route by score tier
**OpenClaw handles:** Low-confidence classifications (score 40-60 range), unknown sender domains, rubric feedback integration, custom reply drafting for medium-tier
**Output:** Gmail labels applied, CRM updated, replies drafted, exceptions escalated to Discord

### P2: Outreach Signal Monitor

**Trigger:** n8n Schedule (hourly)
**n8n handles:** Query outreach.db for new signal_type changes -> match prospect to lane (INVESTOR/BUILDER/BUYER) -> format notification -> batch by priority -> deliver to Discord
**OpenClaw handles:** Interpreting ambiguous signals (e.g., "interesting, tell me more" -- is that green or yellow?), drafting follow-up messages, cross-referencing with knowledge base
**Output:** Signal dashboard updated, follow-ups queued, stale outreach flagged

### P3: Landing Page Traction Monitor

**Trigger:** n8n Schedule (every 6 hours)
**n8n handles:** Query guardspine.db for new signups/demo requests -> enrich with company research (Clearbit/web scrape) -> classify lead quality -> store in CRM -> notify Discord
**OpenClaw handles:** Deep company research for high-quality leads, personalized welcome email drafting, routing to correct outreach lane
**Output:** New leads in CRM, welcome emails drafted, team notified

### P4: Nightly Security Council

**Trigger:** n8n Cron (3:00 AM EST)
**n8n handles:** Run backup-dbs.sh -> check file permissions on sensitive paths -> scan git repos for committed secrets (trufflehog/gitleaks) -> query GuardSpine audit log for L3+ events -> check Railway service health
**OpenClaw handles:** Analyzing novel security patterns, recommending policy changes, investigating unusual L3+ blocks, updating ERRORS.md with new patterns
**Output:** Security report in Discord, auto-fixes applied, LEARNINGS.md updated

### P5: Nightly Platform Council

**Trigger:** n8n Cron (2:00 AM EST)
**n8n handles:** Check all cron job completion status -> run codeguard-action test suite -> compare workspace file hashes for drift -> check outreach.db integrity (orphan records, stale contacts) -> validate config consistency
**OpenClaw handles:** Diagnosing test failures, resolving prompt drift, fixing config inconsistencies, updating FEATURE-REQUESTS.md
**Output:** Platform health report, auto-fixes, drift alerts

### P6: Innovation Scout

**Trigger:** n8n Cron (4:00 AM EST, 3x/week)
**n8n handles:** Search web for "AI code governance" + "AI compliance" + competitor names -> scrape results -> store raw articles in knowledge base -> check for mentions of GuardSpine
**OpenClaw handles:** Analyzing competitive intelligence, generating feature ideas, cross-referencing with current roadmap, writing summaries
**Output:** 2-3 new ideas in FEATURE-REQUESTS.md, competitive intel in knowledge base

### P7: Notification Batcher

**Trigger:** n8n Cron (every 15 min)
**n8n handles:** Read notification queue DB -> classify by priority (critical/high/medium/low) -> batch non-critical -> format digest -> deliver critical immediately, high hourly, medium every 3h, low daily
**OpenClaw handles:** Nothing (fully deterministic). AI only called if notification content needs interpretation.
**Output:** Batched digests to Discord, reduced noise

### P8: Morning Brief

**Trigger:** n8n Cron (7:00 AM EST)
**n8n handles:** Aggregate overnight cron results -> pull outreach metrics -> check landing page signups -> check GitHub notifications -> pull calendar for today -> compile digest
**OpenClaw handles:** Writing the narrative summary (not just data dump), highlighting what needs David's attention, suggesting priorities for the day
**Output:** Morning brief message to Discord DM

### P9: Knowledge Base Ingestion

**Trigger:** n8n Webhook (Discord command "!save <url>") or Cron (daily article scan)
**n8n handles:** Fetch URL -> sanitize content (strip scripts, ads) -> quarantine scan -> chunk text -> embed locally (Nomic or ChromaDB default) -> store in knowledge base DB -> cross-reference with CRM contacts
**OpenClaw handles:** Evaluating relevance to GuardSpine, tagging with topics, writing summary, identifying cross-pollination opportunities with outreach prospects
**Output:** Article in knowledge base, cross-links to CRM, team notified if relevant

### P10: CRM Contact Research

**Trigger:** n8n Schedule (3:30 AM EST)
**n8n handles:** Query CRM for contacts updated in last 7 days -> for each, search web for recent news about their company -> check LinkedIn for role changes -> store findings
**OpenClaw handles:** Interpreting career changes (did they leave their company? new role = new archetype?), updating outreach strategy, flagging stale emails
**Output:** CRM enriched, stale contacts flagged, outreach adjustments queued

### P11: Meeting Intelligence

**Trigger:** n8n Webhook (calendar event ended) or Cron (check Fathom API after meetings)
**n8n handles:** Pull transcript from Fathom/Otter -> match attendees to CRM -> store transcript -> extract action items (regex + structured prompts)
**OpenClaw handles:** Interpreting nuanced action items, assigning ownership, updating deal stage, drafting follow-up emails
**Output:** Action items in task tracker, CRM updated, follow-up drafted

### P12: Prompt Drift Detection

**Trigger:** n8n Cron (5:30 AM EST)
**n8n handles:** Hash all workspace files -> compare to previous hashes -> detect changes -> extract "canonical facts" (version numbers, team roster, counts) -> check for contradictions across files
**OpenClaw handles:** Resolving contradictions, trimming duplicate content, updating stale data, ensuring operational facts stay consistent
**Output:** Drift report, auto-fixes applied, size reduction logged

---

## n8n Design Rules

1. **Every pipeline is a separate n8n workflow.** No mega-workflows. One trigger, one purpose.
2. **AI calls are HTTP Request nodes to OpenClaw.** Not inline code. This lets us swap models, add governance, and track costs.
3. **All data passes through GuardSpine before external sends.** n8n calls GuardSpine gate before email/Discord/webhook sends.
4. **Store everything.** Every pipeline writes to a log DB. Morning self-heal reads from it.
5. **Cron jobs spread overnight.** Heavy (council) runs 2-4 AM. Light (metrics) runs 5-7 AM. Interactive reserved for daytime.
6. **Error handling is a first-class n8n branch.** Every workflow has an error output that writes to the error log and optionally escalates.
7. **Rubrics are YAML files, not prompts.** Scoring criteria stored in version-controlled YAML. n8n reads them. OpenClaw updates them based on feedback.

## Cron Schedule (n8n)

| Time (EST)   | Pipeline                        | Weight |
| ------------ | ------------------------------- | ------ |
| 1:00 AM      | P2: Outreach signal scan        | Light  |
| 1:30 AM      | P3: Landing page traction       | Light  |
| 2:00 AM      | P5: Platform council            | Heavy  |
| 3:00 AM      | P4: Security council            | Heavy  |
| 3:30 AM      | P10: CRM contact research       | Medium |
| 4:00 AM      | P6: Innovation scout (3x/week)  | Heavy  |
| 4:30 AM      | P9: Knowledge base daily scan   | Medium |
| 5:00 AM      | DB backup (SQLite -> encrypted) | Light  |
| 5:30 AM      | P12: Prompt drift detection     | Medium |
| 6:00 AM      | Daily metrics snapshot          | Light  |
| 7:00 AM      | P8: Morning brief               | Medium |
| Every 10m    | P1: Inbound email scoring       | Light  |
| Every 15m    | P7: Notification batcher        | Light  |
| Post-meeting | P11: Meeting intelligence       | Medium |

## Notification Batching

| Priority | Delivery                        | Examples                                               |
| -------- | ------------------------------- | ------------------------------------------------------ |
| Critical | Immediate                       | L4 approval requests, security alerts, system failures |
| High     | Hourly batch                    | CRM updates, outreach responses, cron failures         |
| Medium   | Every 3 hours                   | Routine status, knowledge base additions               |
| Low      | Daily digest (in morning brief) | Analytics, non-urgent summaries                        |

## Data Classification Tiers

| Tier         | Who Can See                  | Examples                                                                    |
| ------------ | ---------------------------- | --------------------------------------------------------------------------- |
| Confidential | David only (DM)              | Financial figures, CRM contact details, deal values, lawsuit info, API keys |
| Internal     | Team only (private channels) | Strategic notes, council recommendations, outreach metrics, cap table       |
| Restricted   | External with approval       | General knowledge, public-facing content, marketing materials               |

**Deterministic enforcement (n8n Function node, not AI):**

- Redact API keys, passwords, tokens from ALL outbound messages
- Redact PII (emails, phone numbers) from non-DM channels
- Never include financial figures in group channels

## LLM Usage Tracking

Central LLM router logs every call:

```json
{
  "timestamp": "2026-03-05T14:30:00Z",
  "model": "kimi-k2",
  "provider": "openrouter",
  "input_tokens": 4500,
  "output_tokens": 1200,
  "cost_estimate": 0.0039,
  "caller": "pipeline/P4-security-council",
  "latency_ms": 3400,
  "cache_hit": true
}
```

LiteLLM already tracks this at litellm.railway.internal:4000. n8n pipeline P-METRICS queries LiteLLM's /spend/logs endpoint daily and stores summaries.

---

## Implementation Priority

Start with the pipelines that are closest to working:

1. **P2 (Outreach Signal Monitor)** -- outreach.db already exists, just needs n8n workflow
2. **P7 (Notification Batcher)** -- reduces noise immediately
3. **P8 (Morning Brief)** -- ties everything together daily
4. **P4 (Security Council)** -- automated version of what we did manually today
5. **P5 (Platform Council)** -- catches drift and failures overnight
6. **P1 (Inbound Email Scoring)** -- when inbound starts coming in

Everything else builds on these foundations.
