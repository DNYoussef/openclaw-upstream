"""
Workflow Health Monitor and Maturity Tracker for GuardSpine autonomous ops.

Checks health of all automation systems and tracks workflow maturity stages.

Usage:
    python workflow_health.py check       # Run all health checks
    python workflow_health.py maturity    # Show maturity report
    python workflow_health.py promote --workflow NAME --stage N --reason "why"
    python workflow_health.py report      # Full report (health + maturity)
    python workflow_health.py alerts      # Show only WARN/CRIT
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
OPS_DB = os.path.join(os.path.expanduser("~"), ".claude", "autonomous", "ops.db")
OUTREACH_DB = os.path.join(os.path.expanduser("~"), ".claude", "outreach", "outreach.db")
MEMORY_DB = os.path.join(os.path.expanduser("~"), ".claude", "memory-mcp-data", "agent_kv.db")
GUARDSPINE_REPO = r"D:\Projects\GuardSpine"

RAILWAY_ENDPOINTS = {
    "railway_litellm": "https://litellm-production-f6f2.up.railway.app",
    "railway_n8n": "https://n8n-production-32ffd.up.railway.app",
    "railway_openclaw": "https://openclaw-production-4349.up.railway.app",
}

HTTP_TIMEOUT = 5  # seconds

# ---------------------------------------------------------------------------
# Maturity stage definitions
# ---------------------------------------------------------------------------
STAGES = {
    0: "Manual",
    1: "Agent-Assisted",
    2: "Supervised",
    3: "Bounded Autonomy",
    4: "Governed Autonomy",
    5: "Optimized",
}

DEFAULT_WORKFLOWS = [
    ("prospect_research",    1, "AI researches, human reviews"),
    ("message_composition",  1, "AI drafts, human approves"),
    ("message_sending",      0, "Human clicks send"),
    ("response_detection",   2, "Script detects, human verifies"),
    ("follow_up",            1, "AI drafts, human sends"),
    ("narrowcast_monitoring", 2, "Script scans, human reviews"),
    ("code_review",          1, "CodeGuard evaluates, human merges"),
    ("evidence_bundling",    3, "Auto-creates on commit"),
    ("daily_synthesis",      0, "Being built now"),
    ("decision_journal",     0, "Being built now"),
    ("content_creation",     1, "AI drafts, human publishes"),
    ("deployment",           0, "Human runs railway up"),
]

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

def _get_conn():
    """Return a connection to ops.db, creating schema if needed."""
    db_dir = os.path.dirname(OPS_DB)
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(OPS_DB)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS health_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            check_name TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT NOT NULL,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS workflow_maturity (
            workflow_name TEXT PRIMARY KEY,
            current_stage INTEGER NOT NULL DEFAULT 0,
            stage_name TEXT NOT NULL DEFAULT 'Manual',
            updated_at TEXT NOT NULL,
            notes TEXT,
            promoted_from INTEGER,
            promotion_reason TEXT
        );

        CREATE TABLE IF NOT EXISTS maturity_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_name TEXT NOT NULL,
            from_stage INTEGER NOT NULL,
            to_stage INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            reason TEXT
        );
    """)
    conn.commit()
    return conn


def _seed_workflows(conn):
    """Insert default workflows if table is empty."""
    count = conn.execute("SELECT count(*) FROM workflow_maturity").fetchone()[0]
    if count > 0:
        return
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    for name, stage, notes in DEFAULT_WORKFLOWS:
        conn.execute(
            "INSERT INTO workflow_maturity (workflow_name, current_stage, stage_name, updated_at, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, stage, STAGES[stage], now, notes),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------

def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _hours_ago(iso_ts):
    """Return hours since the given ISO timestamp."""
    try:
        # Handle fractional seconds
        ts = iso_ts.split(".")[0]
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt
        return delta.total_seconds() / 3600.0
    except Exception:
        return None


def _format_age(hours):
    """Human-readable age string."""
    if hours is None:
        return "unknown"
    if hours < 1:
        minutes = int(hours * 60)
        return "%dm ago" % minutes
    if hours < 48:
        return "%dh ago" % int(hours)
    days = hours / 24.0
    return "%.1fd ago" % days


def check_outreach_db_freshness():
    """Check when the last activity_log entry was created."""
    name = "outreach_db_freshness"
    if not os.path.exists(OUTREACH_DB):
        return (name, "ERROR", "DB not found: %s" % OUTREACH_DB, None)
    try:
        conn = sqlite3.connect(OUTREACH_DB)
        row = conn.execute(
            "SELECT timestamp FROM activity_log ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if row is None:
            return (name, "CRIT", "No entries in activity_log", "0")
        hours = _hours_ago(row[0])
        age_str = _format_age(hours)
        if hours is None:
            return (name, "ERROR", "Could not parse timestamp: %s" % row[0], row[0])
        if hours > 168:  # 7 days
            return (name, "CRIT", "Last activity: %s" % age_str, row[0])
        if hours > 72:  # 3 days
            return (name, "WARN", "Last activity: %s" % age_str, row[0])
        return (name, "OK", "Last activity: %s" % age_str, row[0])
    except Exception as e:
        return (name, "ERROR", str(e), None)


def check_memory_mcp_freshness():
    """Check when the last observation was recorded."""
    name = "memory_mcp_freshness"
    if not os.path.exists(MEMORY_DB):
        return (name, "ERROR", "DB not found: %s" % MEMORY_DB, None)
    try:
        conn = sqlite3.connect(MEMORY_DB)
        row = conn.execute(
            "SELECT created_at FROM observations ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if row is None:
            return (name, "CRIT", "No entries in observations", "0")
        hours = _hours_ago(row[0])
        age_str = _format_age(hours)
        if hours is None:
            return (name, "ERROR", "Could not parse timestamp: %s" % row[0], row[0])
        if hours > 72:  # 3 days
            return (name, "CRIT", "Last observation: %s" % age_str, row[0])
        if hours > 24:  # 1 day
            return (name, "WARN", "Last observation: %s" % age_str, row[0])
        return (name, "OK", "Last observation: %s" % age_str, row[0])
    except Exception as e:
        return (name, "ERROR", str(e), None)


def check_outreach_db_integrity():
    """Sanity check: sent <= prospects, responded <= sent."""
    name = "outreach_db_integrity"
    if not os.path.exists(OUTREACH_DB):
        return (name, "ERROR", "DB not found: %s" % OUTREACH_DB, None)
    try:
        conn = sqlite3.connect(OUTREACH_DB)
        total = conn.execute("SELECT count(*) FROM prospects").fetchone()[0]
        sent = conn.execute(
            "SELECT count(*) FROM prospects WHERE message_sent_at IS NOT NULL"
        ).fetchone()[0]
        responded = conn.execute(
            "SELECT count(*) FROM prospects WHERE response_received = 1"
        ).fetchone()[0]
        conn.close()
        detail = "%d prospects, %d sent, %d resp" % (total, sent, responded)
        value = json.dumps({"total": total, "sent": sent, "responded": responded})
        if sent > total:
            return (name, "CRIT", "sent > prospects: %s" % detail, value)
        if responded > sent:
            return (name, "WARN", "responded > sent: %s" % detail, value)
        return (name, "OK", detail, value)
    except Exception as e:
        return (name, "ERROR", str(e), None)


def check_railway_service(check_name, url):
    """HEAD request to a Railway service endpoint."""
    try:
        req = Request(url, method="HEAD")
        t0 = time.monotonic()
        resp = urlopen(req, timeout=HTTP_TIMEOUT)
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        code = resp.getcode()
        if code < 400:
            return (check_name, "OK", "HTTP %d (%dms)" % (code, elapsed_ms), str(code))
        return (check_name, "WARN", "HTTP %d (%dms)" % (code, elapsed_ms), str(code))
    except URLError as e:
        reason = str(e.reason) if hasattr(e, "reason") else str(e)
        # Check for timeout
        if "timed out" in reason.lower() or "timeout" in reason.lower():
            return (check_name, "WARN", "HTTP timeout (%dms)" % (HTTP_TIMEOUT * 1000), "timeout")
        return (check_name, "CRIT", "HTTP error: %s" % reason, None)
    except Exception as e:
        return (check_name, "ERROR", str(e), None)


def check_guardspine_repo_clean():
    """Check if GuardSpine repo has uncommitted changes."""
    name = "guardspine_repo"
    if not os.path.isdir(GUARDSPINE_REPO):
        return (name, "ERROR", "Repo not found: %s" % GUARDSPINE_REPO, None)
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=GUARDSPINE_REPO,
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        count = len(lines)
        if count == 0:
            return (name, "OK", "Working tree clean", "0")
        if count > 10:
            return (name, "WARN", "%d uncommitted changes" % count, str(count))
        return (name, "OK", "%d uncommitted changes" % count, str(count))
    except subprocess.TimeoutExpired:
        return (name, "ERROR", "git status timed out", None)
    except Exception as e:
        return (name, "ERROR", str(e), None)


def check_stale_follow_ups():
    """Count prospects needing follow-up (sent >5 biz days ago, no response, <2 follow-ups)."""
    name = "stale_follow_ups"
    if not os.path.exists(OUTREACH_DB):
        return (name, "ERROR", "DB not found: %s" % OUTREACH_DB, None)
    try:
        # 5 business days ~ 7 calendar days as a simple approximation
        cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
        conn = sqlite3.connect(OUTREACH_DB)
        count = conn.execute(
            "SELECT count(*) FROM prospects "
            "WHERE message_sent_at IS NOT NULL "
            "AND message_sent_at < ? "
            "AND (response_received IS NULL OR response_received = 0) "
            "AND (follow_up_count IS NULL OR follow_up_count < 2)",
            (cutoff,),
        ).fetchone()[0]
        conn.close()
        if count == 0:
            return (name, "OK", "No stale follow-ups", "0")
        if count > 20:
            return (name, "CRIT", "%d prospects need follow-up" % count, str(count))
        if count > 0:
            return (name, "WARN", "%d prospects need follow-up" % count, str(count))
        return (name, "OK", "No stale follow-ups", "0")
    except Exception as e:
        return (name, "ERROR", str(e), None)


def check_all_health():
    """Run all health checks, return list of (name, status, message, value) tuples."""
    results = []
    results.append(check_outreach_db_freshness())
    results.append(check_memory_mcp_freshness())
    results.append(check_outreach_db_integrity())
    for check_name, url in RAILWAY_ENDPOINTS.items():
        results.append(check_railway_service(check_name, url))
    results.append(check_guardspine_repo_clean())
    results.append(check_stale_follow_ups())
    return results


def persist_health_results(conn, results):
    """Write health check results to ops.db."""
    now = _now_iso()
    for name, status, message, value in results:
        conn.execute(
            "INSERT INTO health_checks (timestamp, check_name, status, message, value) "
            "VALUES (?, ?, ?, ?, ?)",
            (now, name, status, message, value),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# Maturity tracking
# ---------------------------------------------------------------------------

def get_maturity_rows(conn):
    """Return all workflow maturity rows sorted by stage desc, then name."""
    _seed_workflows(conn)
    rows = conn.execute(
        "SELECT workflow_name, current_stage, stage_name, updated_at, notes "
        "FROM workflow_maturity ORDER BY current_stage DESC, workflow_name"
    ).fetchall()
    return rows


def promote_workflow(conn, workflow, new_stage, reason):
    """Promote a workflow to a new maturity stage."""
    if new_stage not in STAGES:
        print("ERROR: Stage must be 0-5, got %d" % new_stage)
        return False
    row = conn.execute(
        "SELECT current_stage FROM workflow_maturity WHERE workflow_name = ?",
        (workflow,),
    ).fetchone()
    if row is None:
        print("ERROR: Unknown workflow '%s'" % workflow)
        print("Known workflows:")
        for r in conn.execute("SELECT workflow_name FROM workflow_maturity ORDER BY workflow_name"):
            print("  - %s" % r[0])
        return False
    old_stage = row[0]
    if new_stage == old_stage:
        print("Workflow '%s' is already at stage %d (%s)" % (workflow, old_stage, STAGES[old_stage]))
        return False
    now = _now_iso()
    conn.execute(
        "UPDATE workflow_maturity SET current_stage=?, stage_name=?, updated_at=?, "
        "promoted_from=?, promotion_reason=? WHERE workflow_name=?",
        (new_stage, STAGES[new_stage], now, old_stage, reason, workflow),
    )
    conn.execute(
        "INSERT INTO maturity_history (workflow_name, from_stage, to_stage, timestamp, reason) "
        "VALUES (?, ?, ?, ?, ?)",
        (workflow, old_stage, new_stage, now, reason),
    )
    conn.commit()
    direction = "Promoted" if new_stage > old_stage else "Demoted"
    print("%s '%s': %d (%s) -> %d (%s)" % (
        direction, workflow, old_stage, STAGES[old_stage], new_stage, STAGES[new_stage]
    ))
    print("Reason: %s" % reason)
    return True


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _pad(text, width):
    """Left-align text in a field of given width."""
    s = str(text)
    if len(s) >= width:
        return s[:width]
    return s + " " * (width - len(s))


def _render_table(headers, rows, widths=None):
    """Render a markdown-style table."""
    if not widths:
        widths = []
        for i, h in enumerate(headers):
            col_max = len(h)
            for row in rows:
                val = str(row[i]) if i < len(row) else ""
                col_max = max(col_max, len(val))
            widths.append(min(col_max + 1, 40))

    header_line = "| " + " | ".join(_pad(h, widths[i]) for i, h in enumerate(headers)) + " |"
    sep_line = "|-" + "-|-".join("-" * widths[i] for i in range(len(headers))) + "-|"
    lines = [header_line, sep_line]
    for row in rows:
        cells = []
        for i in range(len(headers)):
            val = str(row[i]) if i < len(row) else ""
            cells.append(_pad(val, widths[i]))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_health_table(results):
    """Render health check results as a markdown table."""
    headers = ["Check", "Status", "Details"]
    rows = []
    for name, status, message, _value in results:
        status_tag = "[%s]" % status
        rows.append((name, status_tag, message))
    return _render_table(headers, rows, widths=[24, 8, 38])


def render_maturity_table(maturity_rows):
    """Render maturity report as a markdown table."""
    headers = ["Workflow", "Stage", "Level", "Updated"]
    rows = []
    for wf_name, stage, stage_name, updated_at, _notes in maturity_rows:
        date_part = updated_at[:10] if updated_at else ""
        rows.append((wf_name, str(stage), stage_name, date_part))
    return _render_table(headers, rows, widths=[24, 6, 20, 12])


def render_maturity_summary(maturity_rows):
    """Render maturity stage counts and average."""
    counts = {}
    total_stage = 0
    for _name, stage, _sname, _updated, _notes in maturity_rows:
        counts[stage] = counts.get(stage, 0) + 1
        total_stage += stage
    n = len(maturity_rows) or 1
    avg = total_stage / n

    lines = []
    for s in sorted(counts.keys()):
        lines.append("- Stage %d (%s): %d workflows" % (s, STAGES[s], counts[s]))
    lines.append("- Average maturity: %.1f / 5.0" % avg)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_check(_args):
    """Run all health checks and display results."""
    results = check_all_health()
    conn = _get_conn()
    persist_health_results(conn, results)
    conn.close()

    print("\n# System Health -- %s\n" % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"))
    print(render_health_table(results))
    print()

    # Return exit code based on worst status
    statuses = [r[1] for r in results]
    if "CRIT" in statuses or "ERROR" in statuses:
        return 2
    if "WARN" in statuses:
        return 1
    return 0


def cmd_maturity(_args):
    """Show maturity report."""
    conn = _get_conn()
    _seed_workflows(conn)
    rows = get_maturity_rows(conn)
    conn.close()

    print("\n# Workflow Maturity -- %s\n" % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"))
    print(render_maturity_table(rows))
    print()
    print("## Summary")
    print(render_maturity_summary(rows))
    print()
    return 0


def cmd_promote(args):
    """Promote a workflow to a new maturity stage."""
    conn = _get_conn()
    _seed_workflows(conn)
    ok = promote_workflow(conn, args.workflow, args.stage, args.reason)
    conn.close()
    return 0 if ok else 1


def cmd_report(_args):
    """Full report: health + maturity."""
    results = check_all_health()
    conn = _get_conn()
    persist_health_results(conn, results)
    _seed_workflows(conn)
    maturity_rows = get_maturity_rows(conn)
    conn.close()

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    print("\n# Workflow Health Report -- %s\n" % now_str)
    print("## System Health")
    print(render_health_table(results))
    print()
    print("## Workflow Maturity")
    print(render_maturity_table(maturity_rows))
    print()
    print("## Maturity Summary")
    print(render_maturity_summary(maturity_rows))
    print()

    statuses = [r[1] for r in results]
    if "CRIT" in statuses or "ERROR" in statuses:
        return 2
    if "WARN" in statuses:
        return 1
    return 0


def cmd_alerts(_args):
    """Show only WARN/CRIT/ERROR results."""
    results = check_all_health()
    conn = _get_conn()
    persist_health_results(conn, results)
    conn.close()

    filtered = [r for r in results if r[1] in ("WARN", "CRIT", "ERROR")]
    if not filtered:
        print("\nAll systems OK -- no alerts.\n")
        return 0

    print("\n# Alerts -- %s\n" % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"))
    print(render_health_table(filtered))
    print()

    statuses = [r[1] for r in filtered]
    if "CRIT" in statuses or "ERROR" in statuses:
        return 2
    return 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Workflow Health Monitor and Maturity Tracker"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("check", help="Run all health checks")
    sub.add_parser("maturity", help="Show maturity report")

    promote_p = sub.add_parser("promote", help="Update maturity for a workflow")
    promote_p.add_argument("--workflow", required=True, help="Workflow name")
    promote_p.add_argument("--stage", type=int, required=True, help="Target stage (0-5)")
    promote_p.add_argument("--reason", required=True, help="Reason for promotion")

    sub.add_parser("report", help="Full report (health + maturity)")
    sub.add_parser("alerts", help="Show only warnings/critical")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    dispatch = {
        "check": cmd_check,
        "maturity": cmd_maturity,
        "promote": cmd_promote,
        "report": cmd_report,
        "alerts": cmd_alerts,
    }
    return dispatch[args.command](args)


# ---------------------------------------------------------------------------
# Adapter functions for run_autonomous_ops.py runner
# ---------------------------------------------------------------------------

def run_health_check():
    """Run all checks and return rendered table string."""
    results = check_all_health()
    conn = _get_conn()
    persist_health_results(conn, results)
    conn.close()
    return render_health_table(results)


def run_maturity_report():
    """Return rendered maturity table + summary string."""
    conn = _get_conn()
    rows = get_maturity_rows(conn)
    conn.close()
    table = render_maturity_table(rows)
    summary = render_maturity_summary(rows)
    return table + "\n" + summary


def run_health_summary():
    """Return dict with ok/total counts for quick status."""
    results = check_all_health()
    ok = sum(1 for _, s, _, _ in results if s == "OK")
    return {"ok": ok, "total": len(results)}


def get_avg_maturity():
    """Return average maturity stage as float."""
    conn = _get_conn()
    rows = get_maturity_rows(conn)
    conn.close()
    if not rows:
        return 0.0
    total = sum(stage for _, stage, _, _, _ in rows)
    return total / len(rows)


if __name__ == "__main__":
    sys.exit(main() or 0)
