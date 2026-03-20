"""Update all Paperclip agent prompts with model routing + ecosystem context.

Model routing strategy (all flat-rate subscriptions, $0 marginal cost):
  CREATIVE agents (originality, writing, strategy) -> Anthropic Claude (subscription)
  CRITIC agents (rigor, rules, analysis)            -> OpenAI Codex GPT-5.4 (subscription)
"""
import psycopg2
import json
import os

DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:xvbPziICZaZqxHmtALnHZqXQQBlLIaUA@interchange.proxy.rlwy.net:14013/railway")

# Read shared context
with open(os.path.join(os.path.dirname(__file__), "SHARED-CONTEXT.md")) as f:
    SHARED = f.read()

# Model routing: creative vs critic
# Creative = needs originality, human-like output, strategic synthesis
# Critic = needs rigor, rules enforcement, systematic analysis
MODELS = {
    # CREATIVE tier (Anthropic subscription)
    "CEO":              "anthropic/claude-sonnet-4-6",     # Strategic synthesis, daily briefing
    "CMO":              "anthropic/claude-sonnet-4-6",     # Outreach drafting, messaging hooks
    "Content Director": "anthropic/claude-sonnet-4-6",     # Blog posts, LinkedIn content
    # CRITIC tier (OpenAI Codex subscription)
    "CTO":              "openai-codex/gpt-5.4",            # Code review, engineering standards
    "Chief of Staff":   "openai-codex/gpt-5.4",            # Task routing, coordination, ops
    "Narrowcast Scout": "openai-codex/gpt-5.4-mini",       # Thread scoring, keyword analysis
}

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
        "prompt": None,
        "heartbeat_sec": 0,
        "deactivate": True,
    },
    "CTO": {
        "prompt": "# Your Role: CTO\n\nTechnical quality, CI/CD health, code governance infrastructure.\n\n## n8n handles\nGitHub PR webhook monitoring, codeguard-action result tracking, deployment status, evidence bundle creation rate.\n\n## You handle (technical judgment)\nIncident root cause analysis, architecture decisions, evidence verification disputes, pilot repo assessment, agent prompt code review.\n\n## KPIs\nPrimary: prs_governed_per_day | Counter: false_positive_rate\n\n## Heartbeat: every 2 hours\nCheck for issues tagged 'needs_cto'. Review CI/CD health dashboard.",
        "heartbeat_sec": 7200,
        "kpis": {"prs_governed_per_day": {"target": 10, "dir": "max"}, "false_positive_rate": {"target": 10, "dir": "min"}},
    },
    "BizDev Scout": {
        "prompt": None,
        "heartbeat_sec": 0,
        "deactivate": True,
    },
    "COO Workflow": {
        "prompt": None,
        "heartbeat_sec": 0,
        "deactivate": True,
    },
    "Memory Curator": {
        "prompt": None,
        "heartbeat_sec": 0,
        "deactivate": True,
    },
    "Model Lab": {
        "prompt": None,
        "heartbeat_sec": 0,
        "deactivate": True,
    },
    "Narrowcast Scout": {
        "prompt": "# Your Role: Narrowcast Scout (Lead Intelligence)\n\nFind prospects by monitoring public discussions about code governance.\n\n## n8n handles (Narrowcast Scanner workflow)\nRSS feed scanning, Reddit/HN keyword monitoring, thread extraction, basic filtering.\n\n## You handle (relevance judgment)\nIs this thread about our pain? Is this person a real prospect? Which pain bucket? Engage or observe? Extract prospect data for CMO pipeline.\n\n## KPIs\nPrimary: qualified_signals_per_week (10) | Counter: false_positive_rate (<30%)\n\n## Heartbeat: every 6 hours\nReview threads flagged by n8n. Classify relevance. Extract prospects.",
        "heartbeat_sec": 21600,
        "kpis": {"qualified_signals_per_week": {"target": 10, "dir": "max"}, "false_positive_rate": {"target": 30, "dir": "min"}},
    },
    "OpenClaw": {
        "prompt": None,
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

    # Set model routing via /model command prefix in prompt
    model = MODELS.get(name)
    model_prefix = f"/model {model}\n\n" if model else ""
    tier = "CREATIVE (Claude)" if model and "anthropic" in model else "CRITIC (GPT)" if model else "DEFAULT"

    # Update prompt (keep existing if None, but still prepend /model)
    if spec["prompt"] is not None:
        full_prompt = model_prefix + SHARED + "\n\n---\n\n" + spec["prompt"]
        config["payloadTemplate"] = {"text": full_prompt}
    elif model:
        # For agents with existing prompts (CMO, Content Director),
        # prepend /model to existing prompt
        existing = config.get("payloadTemplate", {}).get("text", "")
        # Remove any existing /model prefix
        if existing.startswith("/model "):
            existing = existing.split("\n", 1)[1] if "\n" in existing else existing
        config["payloadTemplate"] = {"text": model_prefix + existing}

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

    # Update metadata with KPIs and model routing info
    meta = spec.get("kpis", {})
    metadata = json.dumps({"kpis": meta, "model": model, "tier": tier})

    cur.execute(
        """UPDATE agents SET
            adapter_config = %s::jsonb,
            runtime_config = %s::jsonb,
            metadata = %s::jsonb,
            status = 'idle',
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
        print(f"UPDATED: {row[0]:20s} | {tier:18s} | model={model or 'default':35s} | prompt={row[1] or 0:5d} chars | hb={il}")

print(f"\nTotal updated: {updated}")

# Final roster
cur.execute(
    """SELECT name, status, budget_monthly_cents,
       runtime_config->'heartbeat'->>'intervalSec',
       LENGTH(adapter_config->'payloadTemplate'->>'text'),
       metadata->>'model',
       metadata->>'tier'
    FROM agents ORDER BY name"""
)
print("\nFinal roster:")
print(f"  {'Name':20s} | {'Status':8s} | {'Model':35s} | {'Tier':18s} | HB   | Prompt")
print(f"  {'-'*20} | {'-'*8} | {'-'*35} | {'-'*18} | ---- | ------")
for r in cur.fetchall():
    interval = int(r[3]) if r[3] else 0
    il = f"{interval}s" if interval < 3600 else f"{interval//3600}h" if interval < 86400 else f"{interval//86400}d" if interval < 604800 else f"{interval//604800}w"
    print(f"  {r[0]:20s} | {r[1]:8s} | {(r[5] or 'default'):35s} | {(r[6] or '-'):18s} | {il:4s} | {r[4] or 0:5d} chars")

cur.close()
conn.close()
