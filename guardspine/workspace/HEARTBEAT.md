# HEARTBEAT.md - Periodic Checks + Ideal State Gap Tracking

On heartbeat, rotate through these checks (every 20 minutes):

1. **Memory MCP** -- `lifecycle_status()` -- system health OK?
2. **GuardSpine** -- `guardspine_status()` -- governance mode and session integrity
3. **GuardSpine** -- `guardspine_audit_log(limit: 5)` -- any recent blocks or escalations?
4. **dev_inbox** -- Check ~/.openclaw/guardspine-logs/dev_inbox/ for pending L4 approvals
5. **Outreach signals** -- Check outreach.db for new responses:
   ```sql
   SELECT name, company, signal_type FROM prospects
   WHERE signal_type != 'none' AND signal_type IS NOT NULL
   ORDER BY message_sent_at DESC LIMIT 5
   ```
6. **Landing page** -- Check guardspine.db for new signups:
   ```sql
   SELECT * FROM signups ORDER BY created_at DESC LIMIT 3
   ```
7. **GitHub** -- `gh notification list --repo DNYoussef/codeguard-action --since "24 hours ago"` -- any new issues/PRs?
8. **n8n pipelines** -- `n8n_get_executions(limit: 5, status: "error")` -- any failed workflows?

If nothing needs attention, reply HEARTBEAT_OK.

Quiet hours: 23:00-08:00 EST unless urgent.

## Ideal State Gap Check (Daily, first heartbeat)

The Algorithm: Define ideal. Snapshot current. Close the gap. Every day.

### Business Ideal State vs Current

| Dimension              | Ideal State                  | How to Measure Current                                    | Verification      |
| ---------------------- | ---------------------------- | --------------------------------------------------------- | ----------------- |
| Free users (WAU)       | 100 GitHub Action users/week | `gh api repos/DNYoussef/codeguard-action` download stats  | yes/no: >= 100?   |
| Trial signups          | 50 on landing page           | Query guardspine.db signups table                         | yes/no: >= 50?    |
| Demo requests          | 10 pending                   | Query guardspine.db demo_requests table                   | yes/no: >= 10?    |
| MRR                    | $3,000 (breakeven)           | Manual / Stripe (when live)                               | yes/no: >= $3K?   |
| Outreach response rate | 15% green signals / sent     | Query outreach.db                                         | yes/no: >= 15%?   |
| Evidence bundles/day   | 100 in production            | Query codeguard-action telemetry                          | yes/no: >= 100?   |
| CI health              | 100% pass rate               | `gh run list --repo DNYoussef/codeguard-action --limit 5` | yes/no: all pass? |

### Operational Ideal State vs Current

| Dimension                | Ideal State                 | How to Measure Current                 | Verification             |
| ------------------------ | --------------------------- | -------------------------------------- | ------------------------ |
| All 12 pipelines active  | P1-P12 running in n8n       | `n8n_list_workflows(active: true)`     | yes/no: 12 active?       |
| Nightly councils running | P4 + P5 producing reports   | Check n8n executions for P4/P5         | yes/no: ran last night?  |
| Morning brief delivered  | P8 fires at 7 AM EST daily  | Check n8n execution history            | yes/no: delivered today? |
| DB backups current       | All 3 DBs backed up < 24h   | Check ~/.claude/backups/db/ timestamps | yes/no: fresh?           |
| Memory MCP healthy       | lifecycle_status returns OK | `lifecycle_status()`                   | yes/no: healthy?         |
| Governance enforcing     | GuardSpine mode = enforce   | `guardspine_status()`                  | yes/no: enforce?         |
| Zero unresolved L4s      | dev_inbox empty             | Check dev_inbox directory              | yes/no: empty?           |

### Gap Report Format

When running the daily gap check, produce a brief report:

```
IDEAL STATE GAP REPORT - [date]
Business: [N/7] dimensions at ideal | Top gap: [dimension] ([current] vs [ideal])
Operations: [N/7] dimensions at ideal | Top gap: [dimension] ([current] vs [ideal])
Priority action: [one sentence describing the highest-leverage gap to close today]
```

Store in Memory MCP with tags: source=heartbeat, type=ideal_state_gap

## Proactive Tasks (No Permission Needed)

- Distill recent Memory MCP entries into long-term knowledge
- Update MEMORY.md decisions log if significant events occurred
- Check git status on active projects
- Run `rlm_introspect()` weekly for governance integrity verification
- Monitor outreach.db for stale follow-ups (sent > 7 days, no signal)
- Check n8n pipeline execution health via `n8n_get_executions`
- Identify highest-leverage gap from ideal state report and suggest action
