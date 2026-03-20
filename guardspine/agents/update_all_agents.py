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
    "CFO":              "openai-codex/gpt-5.4",            # Financial model governance, cost tracking
    "Chief of Staff":   "openai-codex/gpt-5.4",            # Task routing, coordination, ops
    "Narrowcast Scout": "openai-codex/gpt-5.4-mini",       # Thread scoring, keyword analysis
}

# Load role-specific prompts from .md files (if they exist)
def load_prompt(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None

ROLE_PROMPTS = {
    "CEO":              load_prompt("ceo-system-prompt.md"),
    "CTO":              load_prompt("cto-system-prompt.md"),
    "CMO":              load_prompt("cmo-system-prompt.md"),
    "CFO":              load_prompt("cfo-system-prompt.md"),
    "Content Director": load_prompt("content-system-prompt.md"),
    "Chief of Staff":   load_prompt("cos-system-prompt.md"),
    "Narrowcast Scout": load_prompt("narrowcast-system-prompt.md"),
}

PROMPTS = {
    "CEO": {
        "prompt": ROLE_PROMPTS.get("CEO"),
        "heartbeat_sec": 86400,
        "kpis": {"system_uptime_pct": {"target": 99, "dir": "max"}, "decision_reversal_rate": {"target": 0, "dir": "min"}},
    },
    "CFO": {
        "prompt": ROLE_PROMPTS.get("CFO"),
        "heartbeat_sec": 86400,
        "kpis": {"financial_model_review_coverage": {"target": 100, "dir": "max"}, "false_positive_rate": {"target": 10, "dir": "min"}, "cost_anomaly_detection_time_hours": {"target": 2, "dir": "min"}},
    },
    "Chief of Staff": {
        "prompt": ROLE_PROMPTS.get("Chief of Staff"),
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
        "prompt": ROLE_PROMPTS.get("CTO"),
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
        "prompt": ROLE_PROMPTS.get("Narrowcast Scout"),
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
