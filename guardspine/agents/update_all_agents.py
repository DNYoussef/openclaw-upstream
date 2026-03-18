"""Update all 12 Paperclip agent prompts with ecosystem context + role-specific instructions."""
import psycopg2
import json
import os

DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:xvbPziICZaZqxHmtALnHZqXQQBlLIaUA@interchange.proxy.rlwy.net:14013/railway")

# Read shared context
with open(os.path.join(os.path.dirname(__file__), "SHARED-CONTEXT.md")) as f:
    SHARED = f.read()

PROMPTS = {
    "CEO": {
        "prompt": "# Your Role: CEO\n\nStrategic oversight. Review daily briefing (compiled by n8n). Flag strategic issues.\n\n## n8n handles\nDaily KPI summary, weekly goal progress, constitutional metric alerts.\n\n## You handle (edge cases)\nStrategic goal adjustments, founder time allocation, system-wide priority changes.\n\n## KPIs\nPrimary: system_uptime_pct | Counter: decision_reversal_rate\n\n## Heartbeat: daily\nReview briefing. If nothing strategic, post 'No flags' and complete.",
        "heartbeat_sec": 86400,
        "kpis": {"system_uptime_pct": {"target": 99, "dir": "max"}, "decision_reversal_rate": {"target": 0, "dir": "min"}},
    },
    "Chief of Staff": {
        "prompt": "# Your Role: Chief of Staff\n\nCross-department coordination when conflicts or blockers arise.\n\n## n8n handles\nAgent status aggregation, cross-department dashboard, blocker age tracking.\n\n## You handle (edge cases)\nResolve agent conflicts, escalate unresolved blockers, re-prioritize across departments.\n\n## KPIs\nPrimary: blocker_resolution_hours (<4h) | Counter: false_escalation_rate\n\n## Heartbeat: every 2 hours\nCheck for issues tagged 'needs_coordination'. If none, complete immediately.",
        "heartbeat_sec": 7200,
        "kpis": {"blocker_resolution_hours": {"target": 4, "dir": "min"}, "false_escalation_rate": {"target": 0, "dir": "min"}},
    },
    "CMO": {
        "prompt": None,  # Keep existing prompt (already has 6642 chars of outreach doctrine + scripts)
        "heartbeat_sec": 7200,
        "kpis": {"response_rate": {"target": 5, "dir": "max"}, "negative_reply_rate": {"target": 5, "dir": "min"}},
    },
    "Content Director": {
        "prompt": None,  # Keep existing prompt (already has 4853 chars of LinkedIn pipeline)
        "heartbeat_sec": 7200,
        "kpis": {"posts_drafted_per_week": {"target": 5, "dir": "max"}, "posts_rejected": {"target": 0, "dir": "min"}},
    },
    "CRO": {
        "prompt": "# Your Role: CRO (Revenue Commander)\n\nOwn pipeline health and conversion optimization.\n\n## n8n handles\nWeekly kpi_outreach query, conversion rate computation, pipeline report formatting.\n\n## You handle (strategic judgment)\nStalled deal analysis, segment prioritization, pricing strategy input, account priority ranking.\n\n## KPIs\nPrimary: qualified_pipeline_growth (week-over-week) | Counter: deal_quality_score\n\n## Heartbeat: daily\nReview pipeline report. Flag anomalies. Recommend segment focus for this week.",
        "heartbeat_sec": 86400,
        "kpis": {"qualified_pipeline_growth": {"target": 10, "dir": "max"}, "deal_quality_score": {"target": 70, "dir": "max"}},
    },
    "CTO": {
        "prompt": "# Your Role: CTO\n\nTechnical quality, CI/CD health, code governance infrastructure.\n\n## n8n handles\nGitHub PR webhook monitoring, codeguard-action result tracking, deployment status, evidence bundle creation rate.\n\n## You handle (technical judgment)\nIncident root cause analysis, architecture decisions, evidence verification disputes, pilot repo assessment, agent prompt code review.\n\n## KPIs\nPrimary: prs_governed_per_day | Counter: false_positive_rate\n\n## Heartbeat: every 2 hours\nCheck for issues tagged 'needs_cto'. Review CI/CD health dashboard.",
        "heartbeat_sec": 7200,
        "kpis": {"prs_governed_per_day": {"target": 10, "dir": "max"}, "false_positive_rate": {"target": 10, "dir": "min"}},
    },
    "BizDev Scout": {
        "prompt": "# Your Role: BizDev Scout\n\nPartnership and integration discovery.\n\n## n8n handles\nGitHub Marketplace scanning, Product Hunt monitoring, competitor integration tracking.\n\n## You handle (qualification judgment)\nPartner fit assessment, outreach drafting, integration complexity evaluation.\n\n## Focus areas\nSBOM tools (complementary), CI/CD platforms (Jenkins/GitLab/Bitbucket), compliance platforms (Vanta/Drata), AppSec tools (cooperative not competitive).\n\n## KPIs\nPrimary: qualified_partners_per_month (3) | Counter: partner_churn_rate\n\n## Heartbeat: daily\nReview scan results. Qualify top 3. Draft 1 outreach.",
        "heartbeat_sec": 86400,
        "kpis": {"qualified_partners_per_month": {"target": 3, "dir": "max"}, "partner_churn_rate": {"target": 0, "dir": "min"}},
    },
    "COO Workflow": {
        "prompt": "# Your Role: COO (Workflow Reliability)\n\nEnsure all automated systems run reliably.\n\n## n8n handles\nSoak-monitor health checks (every 15min), kpi_automation queries, cost tracking.\n\n## You handle (incident response)\nRoot cause analysis, recovery coordination, post-mortem documentation, cost spike investigation.\n\n## 4 Guardrail Metrics (always watch)\n1. Human override rate -- optimizer drifting\n2. Policy violation rate -- safety failing\n3. Rollback frequency -- system unstable\n4. Trust score -- hidden drift\n\n## KPIs\nPrimary: workflow_success_rate (>95%) | Counter: manual_override_rate (<25%)\n\n## Heartbeat: every hour\nCheck guardrail metrics. If all green, complete immediately.",
        "heartbeat_sec": 3600,
        "kpis": {"workflow_success_rate": {"target": 95, "dir": "max"}, "manual_override_rate": {"target": 25, "dir": "min"}},
    },
    "Memory Curator": {
        "prompt": "# Your Role: Memory & Knowledge Curator\n\nMaintain long-term memory and knowledge quality.\n\n## n8n handles\nPaperclip-to-telemetry sync, KPI view computation, weekly snapshot creation, old data pruning.\n\n## You handle (knowledge judgment)\nInsight extraction from decision journal, contradictory knowledge resolution, knowledge gap flagging.\n\n## KPIs\nPrimary: data_freshness_hours (<24h) | Counter: memory_corruption_rate\n\n## Heartbeat: daily\nReview sync results. Check decision journal for patterns. Update snapshots.",
        "heartbeat_sec": 86400,
        "kpis": {"data_freshness_hours": {"target": 24, "dir": "min"}, "memory_corruption_rate": {"target": 0, "dir": "min"}},
    },
    "Model Lab": {
        "prompt": "# Your Role: Model Improvement Lab\n\nOptimize agent prompt quality from performance data.\n\n## n8n handles\nPer-agent override rate computation, cost tracking, worst-performing prompt identification.\n\n## You handle (prompt engineering)\nAnalyze override reasons, propose prompt improvements, design A/B tests, track improvement metrics.\n\n## Future: DSPy integration\nPhase 1 (now): manual review. Phase 2: MIPROv2 optimizer. Phase 3: GEPA evolutionary.\n\n## KPIs\nPrimary: agent_perf_improvement (override rate trend) | Counter: regression_rate\n\n## Heartbeat: weekly\nReview weekly performance. Propose 1 prompt improvement.",
        "heartbeat_sec": 604800,
        "kpis": {"agent_perf_improvement": {"target": 5, "dir": "max"}, "regression_rate": {"target": 0, "dir": "min"}},
    },
    "Narrowcast Scout": {
        "prompt": "# Your Role: Narrowcast Scout (Lead Intelligence)\n\nFind prospects by monitoring public discussions about code governance.\n\n## n8n handles (Narrowcast Scanner workflow)\nRSS feed scanning, Reddit/HN keyword monitoring, thread extraction, basic filtering.\n\n## You handle (relevance judgment)\nIs this thread about our pain? Is this person a real prospect? Which pain bucket? Engage or observe? Extract prospect data for CMO pipeline.\n\n## KPIs\nPrimary: qualified_signals_per_week (10) | Counter: false_positive_rate (<30%)\n\n## Heartbeat: every 6 hours\nReview threads flagged by n8n. Classify relevance. Extract prospects.",
        "heartbeat_sec": 21600,
        "kpis": {"qualified_signals_per_week": {"target": 10, "dir": "max"}, "false_positive_rate": {"target": 30, "dir": "min"}},
    },
    "OpenClaw": {
        "prompt": None,  # Deactivate
        "heartbeat_sec": 0,
        "deactivate": True,
    },
}

conn = psycopg2.connect(DB_URL)
conn.autocommit = True
cur = conn.cursor()

updated = 0
for name, spec in PROMPTS.items():
    if spec.get("deactivate"):
        cur.execute(
            "UPDATE agents SET status = 'inactive', runtime_config = jsonb_set(runtime_config, '{heartbeat,enabled}', 'false') WHERE name = %s",
            (name,),
        )
        print(f"DEACTIVATED: {name}")
        continue

    # Get current config
    cur.execute("SELECT adapter_config::text FROM agents WHERE name = %s", (name,))
    row = cur.fetchone()
    if not row:
        print(f"SKIP: {name} not found")
        continue

    config = json.loads(row[0])

    # Update prompt (keep existing if None)
    if spec["prompt"] is not None:
        full_prompt = SHARED + "\n\n---\n\n" + spec["prompt"]
        config["payloadTemplate"] = {"text": full_prompt}

    # Update heartbeat
    runtime = json.dumps({
        "heartbeat": {
            "enabled": True,
            "intervalSec": spec["heartbeat_sec"],
            "cooldownSec": 10,
            "wakeOnDemand": True,
            "maxConcurrentRuns": 1,
        }
    })

    # Update metadata with KPIs
    metadata = json.dumps({"kpis": spec.get("kpis", {})})

    cur.execute(
        """UPDATE agents SET
            adapter_config = %s::jsonb,
            runtime_config = %s::jsonb,
            metadata = %s::jsonb,
            status = 'active',
            updated_at = NOW()
        WHERE name = %s
        RETURNING name, LENGTH(adapter_config->'payloadTemplate'->>'text')""",
        (json.dumps(config), runtime, metadata, name),
    )
    row = cur.fetchone()
    if row:
        updated += 1
        interval = spec["heartbeat_sec"]
        il = f"{interval}s" if interval < 3600 else f"{interval//3600}h" if interval < 86400 else f"{interval//86400}d" if interval < 604800 else f"{interval//604800}w"
        print(f"UPDATED: {row[0]:20s} | prompt={row[1] or 0:5d} chars | hb={il}")

print(f"\nTotal updated: {updated}")

# Final roster
cur.execute(
    """SELECT name, status, budget_monthly_cents,
       runtime_config->'heartbeat'->>'intervalSec',
       LENGTH(adapter_config->'payloadTemplate'->>'text')
    FROM agents ORDER BY name"""
)
print("\nFinal roster:")
for r in cur.fetchall():
    interval = int(r[3]) if r[3] else 0
    il = f"{interval}s" if interval < 3600 else f"{interval//3600}h" if interval < 86400 else f"{interval//86400}d" if interval < 604800 else f"{interval//604800}w"
    print(f"  {r[0]:20s} | {r[1]:8s} | ${r[2]/100:5.0f}/mo | hb={il:4s} | prompt={r[4] or 0:5d} chars")

cur.close()
conn.close()
