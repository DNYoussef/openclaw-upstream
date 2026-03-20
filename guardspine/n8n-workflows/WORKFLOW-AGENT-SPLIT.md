# n8n Workflow + Agent Split Architecture

## The Rule

n8n handles deterministic operations (90% of work, zero LLM cost).
Agents handle judgment calls, edge cases, and creative work (10%, cheap model).

## Why This Matters

- n8n workflow step: $0.00 (API calls, DB queries, template rendering)
- Agent LLM call (Gemini Flash): ~$0.001 per call
- Agent LLM call (Claude Sonnet): ~$0.02 per call

Running everything through agents = $1,255/mo.
Running deterministic work through n8n = $53/mo.

## Per-Agent Workflow Split

### CMO Outreach Pipeline (n8n)

Deterministic (n8n):

- Fetch assigned issues from Paperclip API
- Parse prospect JSON from issue description
- Check suppression list / do_not_contact flag
- Check followup_count < 2
- Query prospect company context (web search node)
- Select message template by pain_bucket
- Fill template with prospect data
- Post draft as issue comment
- Update issue status to in_progress
- Emit telemetry event

Agent edge cases (LLM):

- Prospect doesn't match any pain bucket template
- Company context reveals unexpected info (acquisition, layoff, pivot)
- Previous draft was rejected -- needs creative re-approach
- Prospect responded -- needs judgment on follow-up

### Content Director Pipeline (n8n)

Deterministic:

- Fetch content issues from Paperclip
- Query trending topics (RSS, Reddit API, HN API)
- Select content template by type (hot_take, educational, lead_magnet)
- Fill template structure (hook, body, CTA)
- Apply anti-slop word filter
- Post draft to Notion via MCP
- Update issue status

Agent edge cases:

- No template matches the topic
- Slop filter flags borderline phrases that need judgment
- Topic requires original insight, not template fill

### CRO Revenue Pipeline (n8n)

Deterministic:

- Query telemetry_events for outreach metrics weekly
- Query Paperclip issues for deal status
- Compute pipeline KPIs (response rate, conversion, cycle time)
- Format weekly report
- Post to decision journal

Agent edge cases:

- Pipeline metric anomaly (sudden drop/spike)
- Deal strategy recommendation needed
- Pricing objection from prospect needs response guidance

### COO Workflow Monitor (n8n)

Deterministic:

- Query all Railway service health endpoints
- Query kpi_automation view for override rates
- Query heartbeat success rates
- Format status dashboard
- Alert if any metric exceeds threshold

Agent edge cases:

- Service crash root cause analysis
- Workflow failure that automated restart can't fix
- Cost spike investigation

### Chief of Staff Coordinator (n8n)

Deterministic:

- Query all agent statuses from Paperclip
- Query all heartbeat runs
- Compile cross-department status
- Format daily briefing

Agent edge cases:

- Agents producing conflicting recommendations
- Blocker that requires human escalation judgment

### Memory Curator (n8n)

Deterministic:

- Sync Paperclip heartbeat_runs to telemetry_events
- Sync activity_log to telemetry_events
- Compute weekly_snapshots from KPI views
- Prune telemetry older than 90 days

Agent edge cases:

- Contradictory insights in decision journal
- Knowledge gap identified from failed simulations

## Model Routing

| Work type          | Handler            | Model           | Cost/call |
| ------------------ | ------------------ | --------------- | --------- |
| Deterministic ops  | n8n                | None            | $0.00     |
| Simple agent tasks | OpenClaw           | Gemini 3 Flash  | ~$0.001   |
| Complex reasoning  | OpenClaw           | DeepSeek V3.2   | ~$0.003   |
| Critical decisions | OpenClaw           | Claude Sonnet   | ~$0.02    |
| L3+ governance     | GuardSpine council | 3x local models | $0.00     |
| L4 tie-breaker     | GuardSpine         | Claude Opus     | ~$0.05    |

## Monthly Cost Estimate (Corrected)

| Component                         | Cost                           |
| --------------------------------- | ------------------------------ |
| n8n deterministic workflows       | $0 (free, included in Railway) |
| Agent edge cases (~100 calls/mo)  | $0.10 - $1.00                  |
| GuardSpine council (local Ollama) | $0                             |
| LiteLLM proxy overhead            | $0                             |
| Railway hosting (13 services)     | ~$25-40/mo                     |
| OpenRouter LLM credits            | $5-15/mo                       |
| **Total**                         | **$30-55/mo**                  |

## Next Step

Build the first n8n workflow: CMO Outreach Pipeline.
This replaces the CMO agent's heartbeat-driven LLM calls with
deterministic template-based drafting, with LLM fallback only for edge cases.
