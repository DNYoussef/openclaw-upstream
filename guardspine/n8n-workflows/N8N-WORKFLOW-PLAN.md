# n8n Workflow Plan -- Agent-to-Workflow Mapping

## Principle

Each agent has a corresponding n8n workflow that handles 90% of deterministic work.
Agents wake only for edge cases that require LLM judgment.

## Status

| #   | Workflow                    | Agent            | Base Template                        | Status                 |
| --- | --------------------------- | ---------------- | ------------------------------------ | ---------------------- |
| W1  | CMO Outreach Pipeline       | CMO              | Custom built                         | DEPLOYED (active)      |
| W2  | Narrowcast Scanner          | Narrowcast Scout | n8n #13527 (RSS/Reddit/HN + AI)      | EXISTS (inactive)      |
| W3  | Service Health Dashboard    | COO Workflow     | n8n #8130 (Double-verify + Slack)    | PARTIAL (soak-monitor) |
| W4  | Pipeline Metrics Reporter   | CRO              | KDnuggets SQL Report pattern         | NOT BUILT              |
| W5  | Content Scheduling Pipeline | Content Director | n8n #4005 (AI Posts + Approval)      | NOT BUILT              |
| W6  | Data Sync Pipeline          | Memory Curator   | Postgres-to-Postgres ETL pattern     | PARTIAL (SQL function) |
| W7  | GitHub PR Monitor           | CTO              | n8n #13652 (AI PR Review + Postgres) | NOT BUILT              |
| W8  | Notification Router         | Chief of Staff   | n8n #12890 (Severity-based routing)  | NOT BUILT              |
| W9  | Partner Ecosystem Scanner   | BizDev Scout     | n8n #13839 (Tech Trend RSS)          | NOT BUILT              |
| W10 | Agent Performance Tracker   | Model Lab        | Custom SQL queries                   | NOT BUILT              |
| W11 | Daily CEO Briefing          | CEO              | Combines W3+W4+W6 outputs            | NOT BUILT              |

## Template Sources + Modification Plan

### W2: Narrowcast Scanner (activate existing + enhance)

Base: n8n #13527 "Summarize AI News from RSS, Reddit and HN with Claude"
Modifications (~20 min):

- Already exists in n8n as "GuardSpine Narrowcast Scanner (W1) - RSS" (id: CVFHEFsM81v3XVw0)
- Add keyword filter: "code review", "AI governance", "PR approval", "evidence", "audit"
- Add Paperclip issue creation for relevant threads (assignee: Narrowcast Scout)
- Replace Claude with Gemini Flash via LiteLLM proxy
- Add telemetry event emission

### W3: Service Health Dashboard (enhance soak-monitor)

Base: n8n #8130 "Service Health with Double-Verification & Slack Alerts"
Modifications (~15 min):

- Soak-monitor already checks all services every 15 min
- Add: n8n workflow that queries telemetry_events for health_check results
- Add: kpi_automation view query for override rates
- Add: Slack/email alert on failure (when we re-enable Slack)
- Add: cost tracking from LiteLLM budget data

### W4: Pipeline Metrics Reporter

Base: KDnuggets "Scheduled SQL Report via Email" pattern
Modifications (~20 min):

- Schedule: Monday 9 AM ET
- Queries: kpi_outreach, kpi_content, kpi_automation views
- Format: HTML table with week-over-week trends
- Output: Post to Paperclip as CRO issue, emit telemetry
- Code node: compute response_rate, conversion_rate, pipeline_growth

### W5: Content Scheduling Pipeline

Base: n8n #4005 "AI-Generated LinkedIn Posts with Approval"
Modifications (~30 min):

- Replace Google Sheets with Postgres content queue
- Inject writing style guide into OpenAI prompt
- Add anti-slop word filter (Code node)
- Push drafts to Notion via Notion API
- Post to Paperclip as Content Director issue for review
- Track engagement via LinkedIn API polling

### W6: Data Sync Pipeline (enhance existing SQL)

Base: Postgres-to-Postgres ETL pattern
Modifications (~25 min):

- Already have sync_paperclip_telemetry() SQL function
- Add: n8n Schedule Trigger (every 6 hours)
- Add: weekly_snapshots computation
- Add: old data pruning (>90 days)
- Add: telemetry event for sync completion

### W7: GitHub PR Monitor

Base: n8n #13652 "Review GitHub PRs with AI, Log to PostgreSQL and Slack"
Modifications (~20 min):

- GitHub Webhook on DNYoussef repos
- Trigger codeguard-action results processing
- Log evidence bundle metadata to telemetry_events
- Track PR governance rate (prs_governed_per_day KPI)
- Alert CTO on high-risk PRs (create Paperclip issue)

### W8: Notification Router

Base: n8n #12890 "Severity-Based Error Alerts"
Modifications (~20 min):

- Webhook trigger from telemetry-api
- Switch on event severity: critical -> Slack+email, high -> email, medium -> log only
- Route agent failures to Chief of Staff
- Route cost spikes to COO Workflow
- Route pipeline anomalies to CRO

### W9: Partner Ecosystem Scanner

Base: n8n #13839 "Aggregate Tech Trend Signals from RSS"
Modifications (~25 min):

- RSS feeds: GitHub Marketplace, Product Hunt, competitor blogs
- Keyword groups: SBOM, CI/CD, compliance, AppSec
- Score and rank by relevance
- Create Paperclip issue for BizDev Scout (top 3 per week)

### W10: Agent Performance Tracker

Base: Custom SQL queries
Build (~20 min):

- Schedule: weekly
- Query decision_journal for override rates per agent
- Query heartbeat_runs for success rates per agent
- Compute cost per agent from LiteLLM data
- Format performance report
- Create Paperclip issue for Model Lab

### W11: Daily CEO Briefing

Base: Combines outputs from W3, W4, W6
Build (~15 min):

- Schedule: daily 8 AM ET
- Query: kpi_health (service status), kpi_automation (heartbeat success)
- Query: kpi_outreach (pipeline movement), kpi_content (engagement)
- Query: decision_journal (recent decisions)
- Format: bullet-point briefing
- Create Paperclip issue for CEO

## Build Priority (by agent impact)

1. W2 Narrowcast Scanner -- ACTIVATE existing (5 min, highest leverage for lead gen)
2. W4 Pipeline Metrics Reporter -- new build (20 min, CRO needs data)
3. W6 Data Sync Pipeline -- enhance existing (15 min, Memory Curator needs fresh data)
4. W5 Content Scheduling -- new from template (30 min, Content Director needs queue)
5. W8 Notification Router -- new from template (20 min, Chief of Staff needs alerts)
6. W7 GitHub PR Monitor -- new from template (20 min, CTO needs PR tracking)
7. W9 Partner Scanner -- new from template (25 min, BizDev needs leads)
8. W10 Performance Tracker -- custom build (20 min, Model Lab needs metrics)
9. W11 CEO Briefing -- combine others (15 min, CEO needs daily summary)
10. W3 Health Dashboard -- enhance soak-monitor (15 min, COO needs dashboard)

Total estimated build time: ~3 hours for all 10 remaining workflows.
