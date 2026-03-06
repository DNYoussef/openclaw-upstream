# Morning Brief Skill

## Purpose

Generate a daily operations summary for David (founder, GuardSpine).
Run at first interaction each day or on explicit request.
Output a structured brief suitable for Discord/Slack posting.

---

## Data Sources

Query these in parallel where possible. If a source is unavailable,
note it as "[UNAVAILABLE]" and continue with the rest.

### 1. Outreach Pipeline (SQLite)

DB path (try in order):

- `~/.claude/outreach/outreach.db`
- `/data/outreach.db`

```sql
-- New responses (last 24h)
SELECT name, company, signal_type, lane, message_sent_at
FROM prospects
WHERE signal_type IS NOT NULL AND signal_type != 'none'
  AND message_sent_at >= datetime('now', '-24 hours')
ORDER BY message_sent_at DESC;

-- Pipeline totals
SELECT
  COUNT(*) AS total_prospects,
  SUM(CASE WHEN message_sent_at IS NOT NULL THEN 1 ELSE 0 END) AS sent,
  SUM(CASE WHEN signal_type = 'green' THEN 1 ELSE 0 END) AS green,
  SUM(CASE WHEN signal_type = 'yellow' THEN 1 ELSE 0 END) AS yellow,
  SUM(CASE WHEN signal_type = 'red' THEN 1 ELSE 0 END) AS red
FROM prospects;

-- Follow-ups due (sent > 7 days ago, no signal)
SELECT name, company, lane, message_sent_at
FROM prospects
WHERE message_sent_at IS NOT NULL
  AND signal_type IS NULL
  AND message_sent_at <= datetime('now', '-7 days')
ORDER BY message_sent_at ASC
LIMIT 10;
```

### 2. Landing Page (SQLite)

DB path: `D:\Projects\guardspine-landing\data\guardspine.db`
(Railway: check LANDING_DB_PATH env var)

```sql
-- New signups (last 24h)
SELECT * FROM signups
WHERE created_at >= datetime('now', '-24 hours')
ORDER BY created_at DESC;

-- New demo requests (last 24h)
SELECT * FROM demo_requests
WHERE created_at >= datetime('now', '-24 hours')
ORDER BY created_at DESC;

-- Totals
SELECT
  (SELECT COUNT(*) FROM signups) AS total_signups,
  (SELECT COUNT(*) FROM demo_requests) AS total_demos;
```

### 3. GitHub Activity

Use `gh` CLI. Cover these repos:

- DNYoussef/codeguard-action
- DNYoussef/guardspine-kernel
- DNYoussef/guardspine-spec

```bash
# Recent PRs (last 48h)
gh pr list --repo DNYoussef/codeguard-action --state all --limit 5

# Recent issues
gh issue list --repo DNYoussef/codeguard-action --state open --limit 5

# CI status (last 5 runs)
gh run list --repo DNYoussef/codeguard-action --limit 5

# Notifications
gh notification list --since "24 hours ago" 2>/dev/null || echo "No notifications"
```

### 4. Railway Services

Check health of guardspine-ai-ops project services:

| Service  | Public URL                              | Expected                                                |
| -------- | --------------------------------------- | ------------------------------------------------------- |
| LiteLLM  | litellm-production-f6f2.up.railway.app  | 200 on /health/readiness (unauthenticated readiness ep) |
| n8n      | n8n-production-32ffd.up.railway.app     | 200 on /                                                |
| OpenClaw | openclaw-production-4349.up.railway.app | 200 on /health                                          |

```bash
# Health checks (timeout 10s each)
# NOTE: LiteLLM /health requires auth. Use /health/readiness for unauthenticated checks.
curl -s -o /dev/null -w "%{http_code}" --max-time 10 https://litellm-production-f6f2.up.railway.app/health/readiness
curl -s -o /dev/null -w "%{http_code}" --max-time 10 https://n8n-production-32ffd.up.railway.app/
curl -s -o /dev/null -w "%{http_code}" --max-time 10 https://openclaw-production-4349.up.railway.app/health
```

### 5. Calendar

If google-calendar MCP is available:

```
list-events for today (start of day to end of day)
```

If unavailable, output "[Calendar: MCP not connected]".

### 6. Open Tasks

Check these sources:

- `~/.openclaw/guardspine-logs/dev_inbox/` for pending L4 approvals
- n8n failed executions: `n8n_get_executions(limit: 5, status: "error")`
- Memory MCP for recent action items tagged with `type=task`

---

## Brief Template

Output the brief in this exact structure. Use plain ASCII only.
Wrap at 80 characters for readability.

```
================================================================
  MORNING BRIEF -- [YYYY-MM-DD] ([Day of Week])
================================================================

--- CRITICAL (needs attention NOW) ---

[Items here or "Nothing critical."]

--- PIPELINE (outreach + sales) ---

Outreach: [sent]/[total] sent | [green] green | [yellow] yellow | [red] red
Response rate: [green/sent as %]%
New signals (24h): [count]
  [- Name @ Company: signal_type (lane)]
Follow-ups due: [count]
  [- Name @ Company: sent [date], no response (lane)]

Landing page: [total_signups] signups | [total_demos] demo requests
New (24h): [signup_count] signups, [demo_count] demos

--- ENGINEERING (code + infra) ---

GitHub:
  PRs open: [count] | Merged (48h): [count]
  Issues open: [count]
  CI: [pass/fail status of last 5 runs]

Railway:
  LiteLLM:  [status code] [OK/DOWN]
  n8n:      [status code] [OK/DOWN]
  OpenClaw: [status code] [OK/DOWN]

GuardSpine: mode=[enforce/audit] | L4 pending: [count]

--- CALENDAR ---

[List of today's events with times, or "No meetings today."]

--- ACTION ITEMS (prioritized) ---

1. [Highest priority item]
2. [Next item]
3. [Next item]
...

================================================================
```

---

## Priority Rules (What Counts as CRITICAL)

An item goes in the CRITICAL section if ANY of these are true:

1. **Revenue signal**: A green or yellow outreach response in the last 24h
   from an INVESTOR or BUYER lane prospect.
2. **Service down**: Any Railway service returning non-200 or unreachable.
3. **CI broken**: Last codeguard-action CI run failed.
4. **Security**: Any L4 approval pending in dev_inbox (blocked action).
5. **Demo request**: Any new demo request on the landing page.
6. **Meeting prep**: A meeting with an investor, advisor, or partner is
   scheduled for today (needs prep).
7. **Stale follow-up**: A green-signal prospect has not been followed up
   within 48h.

Items NOT critical (go in their normal section):

- Routine heartbeat checks passing
- PRs from known contributors on schedule
- Yellow signals from BUILDER lane (informational)

---

## Output Format

- Plain text, no markdown rendering needed (Discord/Slack compatible)
- ASCII only -- no unicode, no emoji
- Lines wrapped at 80 characters
- Use `===` and `---` for section dividers
- Timestamps in ET (Eastern Time)
- Numbers always concrete (never "some" or "several")
- If a data source fails, say "[SOURCE]: unavailable" and move on
- End with the single most important thing David should do first

---

## Ideal State Reference (from HEARTBEAT.md)

Compare current numbers against these targets and flag gaps:

| Metric                   | Target     | Source                |
| ------------------------ | ---------- | --------------------- |
| WAU (free GitHub Action) | 100/week   | gh api download stats |
| Trial signups            | 50 total   | guardspine.db         |
| Demo requests            | 10 pending | guardspine.db         |
| MRR                      | $3,000     | Manual/Stripe         |
| Outreach response rate   | 15% green  | outreach.db           |
| Evidence bundles/day     | 100        | codeguard telemetry   |
| CI pass rate             | 100%       | gh run list           |

If any metric is below 25% of its target, flag it in CRITICAL as a
strategic gap.

---

## Invocation

This skill activates when:

- The user says "morning brief", "daily brief", or "brief me"
- It is the first interaction of the day (check last brief timestamp)
- An n8n pipeline triggers it (P8 morning brief pipeline)

Store the generated brief in Memory MCP with tags:
source=morning-brief, type=daily_brief, date=[YYYY-MM-DD]

---

## Example Output

```
================================================================
  MORNING BRIEF -- 2026-03-06 (Friday)
================================================================

--- CRITICAL (needs attention NOW) ---

[REVENUE] Phil Venables @ Ballistic Ventures responded (green, INVESTOR)
  -> Follow up within 24h. Draft reply before 10am ET.

[INFRA] n8n returning 502 -- check Railway dashboard.

--- PIPELINE (outreach + sales) ---

Outreach: 173/358 sent | 13 green | 2 yellow | 0 red
Response rate: 7.5%
New signals (24h): 1
  - Phil Venables @ Ballistic Ventures: green (INVESTOR)
Follow-ups due: 8
  - Jane Doe @ Acme Corp: sent 2026-02-25, no response (BUYER)
  - John Smith @ DevTools Inc: sent 2026-02-26, no response (BUILDER)

Landing page: 1 signup | 0 demo requests
New (24h): 0 signups, 0 demos

--- ENGINEERING (code + infra) ---

GitHub:
  PRs open: 2 | Merged (48h): 1
  Issues open: 3
  CI: 5/5 passing

Railway:
  LiteLLM:  200 OK
  n8n:      502 DOWN
  OpenClaw: 200 OK

GuardSpine: mode=enforce | L4 pending: 0

--- CALENDAR ---

10:00 ET - Sync with Igor (30min)
14:00 ET - Kristen advisor check-in (30min)

--- ACTION ITEMS (prioritized) ---

1. Reply to Phil Venables (green signal, investor lane)
2. Investigate n8n 502 on Railway
3. Follow up with 3 oldest stale BUYER prospects
4. Review open codeguard-action PRs

================================================================
```
