"""
GuardSpine Autonomous Operations Runner

Orchestrates daily synthesis, decision journal, and workflow health
into unified operational reports.

Usage:
    python run_autonomous_ops.py morning    # Daily synthesis + health + recent decisions
    python run_autonomous_ops.py health     # Health checks only
    python run_autonomous_ops.py report     # Full report (all modules + maturity)
    python run_autonomous_ops.py status     # Quick one-liner status
    python run_autonomous_ops.py help       # Show this help
"""

import importlib
import json
import os
import sys
import traceback
import urllib.request
from datetime import datetime


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTREACH_DB = os.path.join(os.path.expanduser("~"), ".claude", "outreach", "outreach.db")
OPS_DB = os.path.join(os.path.expanduser("~"), ".claude", "autonomous", "ops.db")


# ---------------------------------------------------------------------------
# Module loading -- graceful failure if subscripts not yet created
# ---------------------------------------------------------------------------

def _load_module(name):
    """Import a sibling module by name. Returns None if not available."""
    try:
        spec_path = os.path.join(SCRIPT_DIR, name + ".py")
        if not os.path.exists(spec_path):
            return None
        spec = importlib.util.spec_from_file_location(name, spec_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as exc:
        print("[WARN] Failed to load %s: %s" % (name, exc))
        return None


def _try_call(mod, func_name, *args, **kwargs):
    """Call mod.func_name(*args, **kwargs), return result or error string."""
    if mod is None:
        return None
    fn = getattr(mod, func_name, None)
    if fn is None:
        return "[WARN] Module %s has no function %s" % (mod.__name__, func_name)
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        return "[ERROR] %s.%s failed: %s" % (mod.__name__, func_name, exc)


# ---------------------------------------------------------------------------
# Outreach stats -- direct DB query (no module dependency)
# ---------------------------------------------------------------------------

def _outreach_stats():
    """Return (total, sent, responded) from outreach DB, or None."""
    try:
        import sqlite3
        if not os.path.exists(OUTREACH_DB):
            return None
        conn = sqlite3.connect(OUTREACH_DB)
        cur = conn.cursor()
        total = cur.execute("SELECT COUNT(*) FROM prospects").fetchone()[0]
        sent = cur.execute(
            "SELECT COUNT(*) FROM prospects WHERE message_sent_at IS NOT NULL"
        ).fetchone()[0]
        responded = cur.execute(
            "SELECT COUNT(*) FROM prospects WHERE response_received = 1"
        ).fetchone()[0]
        conn.close()
        return (total, sent, responded)
    except Exception:
        return None


def _git_commit_count(days=7):
    """Count git commits in the last N days. Returns int or None."""
    try:
        import subprocess
        since = datetime.now().strftime("%Y-%m-%d")
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=%d days ago" % days],
            capture_output=True, text=True, cwd=os.path.expanduser("~"),
            timeout=10,
        )
        if result.returncode == 0:
            lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
            return len(lines)
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Slack webhook posting
# ---------------------------------------------------------------------------

def _post_slack(text):
    """Post text to Slack webhook if SLACK_WEBHOOK_URL is set."""
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url:
        return
    try:
        payload = json.dumps({"text": text}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
        print("[INFO] Posted briefing to Slack")
    except Exception as exc:
        print("[WARN] Slack post failed: %s" % exc)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _header(title):
    sep = "=" * 60
    return "\n".join([sep, "  %s  --  %s" % (title, datetime.now().strftime("%Y-%m-%d %H:%M")), sep])


def cmd_morning():
    """Morning briefing: synthesis + health + recent decisions."""
    sections = [_header("GuardSpine Morning Briefing")]

    # 1. Daily synthesis
    synth = _load_module("daily_synthesis")
    if synth is None:
        sections.append("\n[SKIP] daily_synthesis.py not yet available")
    else:
        result = _try_call(synth, "run_synthesis")
        if result is not None:
            sections.append("\n--- Daily Synthesis ---")
            sections.append(str(result))

    # 2. Health check
    health = _load_module("workflow_health")
    if health is None:
        sections.append("\n[SKIP] workflow_health.py not yet available")
    else:
        result = _try_call(health, "run_health_check")
        if result is not None:
            sections.append("\n--- Health Check ---")
            sections.append(str(result))

    # 3. Recent decisions (last 7 days)
    journal = _load_module("decision_journal")
    if journal is None:
        sections.append("\n[SKIP] decision_journal.py not yet available")
    else:
        result = _try_call(journal, "analyze", days=7)
        if result is not None:
            sections.append("\n--- Recent Decisions (7d) ---")
            sections.append(str(result))

    # 4. Quick outreach stats (always available)
    stats = _outreach_stats()
    if stats:
        sections.append(
            "\n--- Outreach Pipeline ---\n"
            "Total: %d | Sent: %d | Responded: %d" % stats
        )

    briefing = "\n".join(sections)
    print(briefing)
    _post_slack(briefing)
    return briefing


def cmd_health():
    """Health checks only."""
    sections = [_header("GuardSpine Health Check")]

    health = _load_module("workflow_health")
    if health is None:
        sections.append("\n[SKIP] workflow_health.py not yet available")
        print("\n".join(sections))
        return

    result = _try_call(health, "run_health_check")
    if result is not None:
        sections.append(str(result))

    print("\n".join(sections))


def cmd_report():
    """Full report: synthesis + health + maturity + decisions."""
    sections = [_header("GuardSpine Full Operations Report")]

    # Synthesis
    synth = _load_module("daily_synthesis")
    if synth is None:
        sections.append("\n[SKIP] daily_synthesis.py not yet available")
    else:
        result = _try_call(synth, "run_synthesis")
        if result is not None:
            sections.append("\n--- Daily Synthesis ---")
            sections.append(str(result))

    # Health
    health = _load_module("workflow_health")
    if health is None:
        sections.append("\n[SKIP] workflow_health.py not yet available")
    else:
        check_result = _try_call(health, "run_health_check")
        if check_result is not None:
            sections.append("\n--- Health Check ---")
            sections.append(str(check_result))

        maturity_result = _try_call(health, "run_maturity_report")
        if maturity_result is not None:
            sections.append("\n--- Maturity Report ---")
            sections.append(str(maturity_result))

    # Decisions
    journal = _load_module("decision_journal")
    if journal is None:
        sections.append("\n[SKIP] decision_journal.py not yet available")
    else:
        result = _try_call(journal, "analyze", days=30)
        if result is not None:
            sections.append("\n--- Decision Analysis (30d) ---")
            sections.append(str(result))

    # Outreach
    stats = _outreach_stats()
    if stats:
        sections.append(
            "\n--- Outreach Pipeline ---\n"
            "Total: %d | Sent: %d | Responded: %d" % stats
        )

    print("\n".join(sections))


def cmd_status():
    """Quick one-liner status."""
    parts = ["GuardSpine Status:"]

    # Outreach
    stats = _outreach_stats()
    if stats:
        parts.append("Pipeline %d/%d/%d" % stats)
    else:
        parts.append("Pipeline N/A")

    # Git
    commits = _git_commit_count(7)
    if commits is not None:
        parts.append("Git %d commits/7d" % commits)

    # Health
    health = _load_module("workflow_health")
    if health is not None:
        result = _try_call(health, "run_health_summary")
        if result and isinstance(result, dict):
            ok = result.get("ok", "?")
            total = result.get("total", "?")
            parts.append("Health %s/%s OK" % (ok, total))
        else:
            parts.append("Health N/A")
    else:
        parts.append("Health N/A")

    # Maturity
    if health is not None:
        result = _try_call(health, "get_avg_maturity")
        if result is not None and isinstance(result, (int, float)):
            parts.append("Maturity avg %.1f/5" % result)
        else:
            parts.append("Maturity N/A")
    else:
        parts.append("Maturity N/A")

    print(" | ".join(parts))


def cmd_help():
    """Print usage."""
    print(__doc__)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

COMMANDS = {
    "morning": cmd_morning,
    "health": cmd_health,
    "report": cmd_report,
    "status": cmd_status,
    "help": cmd_help,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        cmd_help()
        if len(sys.argv) >= 2:
            print("\n[ERROR] Unknown command: %s" % sys.argv[1])
            print("Available: %s" % ", ".join(sorted(COMMANDS.keys())))
        sys.exit(1 if len(sys.argv) >= 2 else 0)

    COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    main()
