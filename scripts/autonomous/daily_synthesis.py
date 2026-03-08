"""
Daily Business State Synthesis for GuardSpine autonomous operations.

Aggregates pipeline metrics, code velocity, session history, and system
health into a single markdown briefing. Stores each run as a snapshot
in ops.db for longitudinal tracking.

Usage:
    python scripts/autonomous/daily_synthesis.py
"""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
OUTREACH_DB = Path(r"C:\Users\17175\.claude\outreach\outreach.db")
MEMORY_DB = Path(r"C:\Users\17175\.claude\memory-mcp-data\agent_kv.db")
OPS_DIR = Path(r"C:\Users\17175\.claude\autonomous")
OPS_DB = OPS_DIR / "ops.db"
GUARDSPINE_REPO = Path(r"D:\Projects\GuardSpine")

RAILWAY_URLS = {
    "LiteLLM": "https://litellm-production-f6f2.up.railway.app",
    "n8n": "https://n8n-production-32ffd.up.railway.app",
    "OpenClaw": "https://openclaw-production-4349.up.railway.app",
}

NOW = datetime.now(tz=None)  # local time; DB timestamps are also local
NOW_ISO = NOW.strftime("%Y-%m-%dT%H:%M:%SZ")
TODAY = NOW.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _connect(path):
    """Open a read-only sqlite3 connection. Returns None if file missing."""
    if not path.exists():
        return None
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def _days_ago(n):
    return (NOW - timedelta(days=n)).strftime("%Y-%m-%dT00:00:00")


def _relative_time(iso_str):
    """Return a short human string like '2h ago' or '3d ago'."""
    if not iso_str:
        return "unknown"
    try:
        # handle both with and without microseconds / timezone
        clean = iso_str.replace("Z", "").split(".")[0]
        dt = datetime.fromisoformat(clean)
        delta = NOW - dt
        secs = int(delta.total_seconds())
        if secs < 0:
            return "just now"
        if secs < 3600:
            return f"{secs // 60}m ago"
        if secs < 86400:
            return f"{secs // 3600}h ago"
        return f"{secs // 86400}d ago"
    except Exception:
        return iso_str[:16]


# ---------------------------------------------------------------------------
# 1. Pipeline State
# ---------------------------------------------------------------------------
def gather_pipeline():
    result = {
        "available": False,
        "error": None,
        "total": 0,
        "sent": 0,
        "responded": 0,
        "green": 0,
        "yellow": 0,
        "red": 0,
        "bounced": 0,
        "sent_7d": 0,
        "responses_7d": 0,
        "followups_due": 0,
        "stale": 0,
        "last_activity": None,
        "last_activity_age": None,
    }
    conn = _connect(OUTREACH_DB)
    if conn is None:
        result["error"] = f"DB not found: {OUTREACH_DB}"
        return result

    try:
        cur = conn.cursor()

        # Totals
        cur.execute("SELECT count(*) FROM prospects")
        result["total"] = cur.fetchone()[0]

        cur.execute(
            "SELECT count(*) FROM prospects WHERE message_sent_at IS NOT NULL"
        )
        result["sent"] = cur.fetchone()[0]

        cur.execute(
            "SELECT count(*) FROM prospects WHERE response_received = 1"
        )
        result["responded"] = cur.fetchone()[0]

        # Signal breakdown
        for signal in ("green", "yellow", "red", "bounced"):
            cur.execute(
                "SELECT count(*) FROM prospects WHERE signal_type = ?",
                (signal,),
            )
            result[signal] = cur.fetchone()[0]

        # Last 7 days activity
        cutoff_7d = _days_ago(7)
        cur.execute(
            "SELECT count(*) FROM prospects WHERE message_sent_at >= ?",
            (cutoff_7d,),
        )
        result["sent_7d"] = cur.fetchone()[0]

        cur.execute(
            "SELECT count(*) FROM prospects "
            "WHERE last_response_at IS NOT NULL AND last_response_at >= ?",
            (cutoff_7d,),
        )
        result["responses_7d"] = cur.fetchone()[0]

        # Follow-ups due: sent >5 business days ago, no response, no follow-up
        # Approximate 5 business days as 7 calendar days
        cutoff_followup = _days_ago(7)
        cur.execute(
            "SELECT count(*) FROM prospects "
            "WHERE message_sent_at IS NOT NULL "
            "AND message_sent_at < ? "
            "AND response_received = 0 "
            "AND (last_follow_up_at IS NULL OR last_follow_up_at < message_sent_at)",
            (cutoff_followup,),
        )
        result["followups_due"] = cur.fetchone()[0]

        # Stale: sent >14 days ago, no response, no follow-up
        cutoff_stale = _days_ago(14)
        cur.execute(
            "SELECT count(*) FROM prospects "
            "WHERE message_sent_at IS NOT NULL "
            "AND message_sent_at < ? "
            "AND response_received = 0 "
            "AND (last_follow_up_at IS NULL OR last_follow_up_at < message_sent_at)",
            (cutoff_stale,),
        )
        result["stale"] = cur.fetchone()[0]

        # Last activity_log entry
        cur.execute(
            "SELECT timestamp FROM activity_log ORDER BY timestamp DESC LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            result["last_activity"] = row[0]
            result["last_activity_age"] = _relative_time(row[0])

        result["available"] = True
    except Exception as exc:
        result["error"] = str(exc)
    finally:
        conn.close()

    return result


# ---------------------------------------------------------------------------
# 2. Code Velocity
# ---------------------------------------------------------------------------
def gather_velocity():
    result = {
        "available": False,
        "error": None,
        "branch": None,
        "commits_7d": 0,
        "recent_commits": [],
        "files_changed_7d": 0,
        "uncommitted": 0,
    }
    if not GUARDSPINE_REPO.exists():
        result["error"] = f"Repo not found: {GUARDSPINE_REPO}"
        return result

    repo = str(GUARDSPINE_REPO)
    try:
        # Current branch
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        result["branch"] = branch

        # Commits in last 7 days
        since = (NOW - timedelta(days=7)).strftime("%Y-%m-%d")
        log_out = subprocess.check_output(
            [
                "git", "log", f"--since={since}",
                "--pretty=format:%H|%ai|%s",
                "--no-merges",
            ],
            cwd=repo,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()

        commits = []
        if log_out:
            for line in log_out.splitlines():
                parts = line.split("|", 2)
                if len(parts) == 3:
                    commits.append({
                        "hash": parts[0][:8],
                        "date": parts[1].strip(),
                        "subject": parts[2].strip(),
                    })
        result["commits_7d"] = len(commits)
        result["recent_commits"] = commits[:5]  # top 5 most recent

        # Files changed in last 7 days
        if commits:
            oldest = commits[-1]["hash"]
            try:
                diff_stat = subprocess.check_output(
                    ["git", "diff", "--stat", "--name-only", f"{oldest}~1..HEAD"],
                    cwd=repo,
                    stderr=subprocess.DEVNULL,
                    text=True,
                ).strip()
                result["files_changed_7d"] = len(
                    [f for f in diff_stat.splitlines() if f.strip()]
                )
            except subprocess.CalledProcessError:
                # oldest commit might be the first; fall back
                diff_stat = subprocess.check_output(
                    ["git", "diff", "--stat", "--name-only", f"{oldest}..HEAD"],
                    cwd=repo,
                    stderr=subprocess.DEVNULL,
                    text=True,
                ).strip()
                result["files_changed_7d"] = len(
                    [f for f in diff_stat.splitlines() if f.strip()]
                )

        # Uncommitted changes
        status_out = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=repo,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if status_out:
            result["uncommitted"] = len(status_out.splitlines())

        result["available"] = True
    except Exception as exc:
        result["error"] = str(exc)

    return result


# ---------------------------------------------------------------------------
# 3. Session History
# ---------------------------------------------------------------------------
def gather_sessions():
    result = {
        "available": False,
        "error": None,
        "recent_sessions": [],
        "total_observations": 0,
        "total_sessions": 0,
        "tools_24h": 0,
        "top_tools": [],
    }
    conn = _connect(MEMORY_DB)
    if conn is None:
        result["error"] = f"DB not found: {MEMORY_DB}"
        return result

    try:
        cur = conn.cursor()

        # Last 3 sessions with summaries
        cur.execute(
            "SELECT session_id, started_at, tool_count, summary "
            "FROM sessions ORDER BY started_at DESC LIMIT 3"
        )
        for row in cur.fetchall():
            summary_text = row["summary"] or ""
            # Truncate to first meaningful line (skip "Request:" prefix noise)
            short = summary_text[:120].replace("\n", " ").strip()
            result["recent_sessions"].append({
                "started_at": row["started_at"],
                "tool_count": row["tool_count"] or 0,
                "summary": short,
            })

        # Totals
        cur.execute("SELECT count(*) FROM observations")
        result["total_observations"] = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM sessions")
        result["total_sessions"] = cur.fetchone()[0]

        # Tool use in last 24h
        cutoff_24h = _days_ago(1)
        cur.execute(
            "SELECT count(*) FROM observations "
            "WHERE tool_name IS NOT NULL AND tool_name != '' "
            "AND created_at >= ?",
            (cutoff_24h,),
        )
        result["tools_24h"] = cur.fetchone()[0]

        # Most used tools (all time, top 5)
        cur.execute(
            "SELECT tool_name, count(*) as cnt FROM observations "
            "WHERE tool_name IS NOT NULL AND tool_name != '' "
            "GROUP BY tool_name ORDER BY cnt DESC LIMIT 5"
        )
        result["top_tools"] = [
            {"tool": row["tool_name"], "count": row["cnt"]}
            for row in cur.fetchall()
        ]

        result["available"] = True
    except Exception as exc:
        result["error"] = str(exc)
    finally:
        conn.close()

    return result


# ---------------------------------------------------------------------------
# 4. System Health
# ---------------------------------------------------------------------------
def check_health(pipeline, sessions):
    checks = []

    # outreach.db freshness
    if pipeline["available"] and pipeline["last_activity"]:
        age = pipeline["last_activity_age"]
        # Parse to see if older than 7 days
        try:
            clean = pipeline["last_activity"].replace("Z", "").split(".")[0]
            dt = datetime.fromisoformat(clean)
            days_old = (NOW - dt).days
            if days_old > 7:
                checks.append(("WARN", f"outreach.db: last activity {age} (stale)"))
            else:
                checks.append(("OK", f"outreach.db: last activity {age}"))
        except Exception:
            checks.append(("OK", f"outreach.db: last activity {age}"))
    elif pipeline["available"]:
        checks.append(("WARN", "outreach.db: no activity_log entries"))
    else:
        checks.append(("FAIL", f"outreach.db: {pipeline.get('error', 'unavailable')}"))

    # Memory MCP
    if sessions["available"]:
        checks.append((
            "OK",
            f"Memory MCP: {sessions['total_observations']} observations, "
            f"{sessions['total_sessions']} sessions",
        ))
    else:
        checks.append(("FAIL", f"Memory MCP: {sessions.get('error', 'unavailable')}"))

    # Railway services
    for name, url in RAILWAY_URLS.items():
        try:
            req = Request(url, method="HEAD")
            resp = urlopen(req, timeout=8)
            code = resp.getcode()
            checks.append(("OK", f"Railway {name}: {code}"))
        except URLError as exc:
            reason = getattr(exc, "reason", str(exc))
            checks.append(("WARN", f"Railway {name}: {reason}"))
        except Exception as exc:
            checks.append(("WARN", f"Railway {name}: {exc}"))

    return checks


# ---------------------------------------------------------------------------
# 5. Build markdown briefing
# ---------------------------------------------------------------------------
def build_briefing(pipeline, velocity, sessions, health):
    lines = []
    lines.append(f"# GuardSpine Daily State -- {TODAY}")
    lines.append("")

    # -- Pipeline --
    lines.append("## Pipeline")
    if pipeline["available"]:
        lines.append(
            f"- {pipeline['total']} prospects | "
            f"{pipeline['sent']} sent | "
            f"{pipeline['responded']} responded"
        )
        lines.append(
            f"- Last 7 days: {pipeline['sent_7d']} sent, "
            f"{pipeline['responses_7d']} responses"
        )
        lines.append(
            f"- Follow-ups due: {pipeline['followups_due']} prospects "
            f"(>5 business days, no response)"
        )
        lines.append(
            f"- Stale: {pipeline['stale']} prospects "
            f"(>14 days, no follow-up)"
        )
        lines.append(
            f"- Signal breakdown: {pipeline['green']} green | "
            f"{pipeline['yellow']} yellow | "
            f"{pipeline['red']} red | "
            f"{pipeline['bounced']} bounced"
        )
    else:
        lines.append(f"- UNAVAILABLE: {pipeline.get('error', 'unknown')}")
    lines.append("")

    # -- Code Velocity --
    lines.append(f"## Code Velocity ({GUARDSPINE_REPO})")
    if velocity["available"]:
        lines.append(f"- Branch: {velocity['branch']}")
        lines.append(f"- Last 7 days: {velocity['commits_7d']} commits, "
                      f"{velocity['files_changed_7d']} files changed")
        for c in velocity["recent_commits"][:3]:
            age = _relative_time(c["date"])
            subj = c["subject"][:72]
            lines.append(f'- Recent: "{subj}" ({age})')
        if velocity["uncommitted"]:
            lines.append(
                f"- Uncommitted changes: {velocity['uncommitted']} files modified"
            )
        else:
            lines.append("- Working tree clean")
    else:
        lines.append(f"- UNAVAILABLE: {velocity.get('error', 'unknown')}")
    lines.append("")

    # -- Sessions --
    lines.append("## Recent Sessions")
    if sessions["available"]:
        for s in sessions["recent_sessions"]:
            ts = s["started_at"][:16].replace("T", " ")
            tools = s["tool_count"]
            summary = s["summary"][:80] if s["summary"] else "(no summary)"
            lines.append(f"- [{ts}] {tools} tools -- {summary}")
        lines.append(f"- Tools used in last 24h: {sessions['tools_24h']}")
        if sessions["top_tools"]:
            top = ", ".join(
                f"{t['tool']}({t['count']})" for t in sessions["top_tools"][:5]
            )
            lines.append(f"- Top tools (all time): {top}")
    else:
        lines.append(f"- UNAVAILABLE: {sessions.get('error', 'unknown')}")
    lines.append("")

    # -- Health --
    lines.append("## System Health")
    for status, msg in health:
        lines.append(f"- [{status}] {msg}")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 6. Store snapshot in ops.db
# ---------------------------------------------------------------------------
def store_snapshot(pipeline, velocity, health, briefing_text):
    OPS_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(OPS_DB))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS daily_state ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  timestamp TEXT NOT NULL,"
        "  pipeline_json TEXT,"
        "  velocity_json TEXT,"
        "  health_json TEXT,"
        "  briefing_text TEXT"
        ")"
    )
    health_serializable = [{"status": s, "message": m} for s, m in health]
    conn.execute(
        "INSERT INTO daily_state "
        "(timestamp, pipeline_json, velocity_json, health_json, briefing_text) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            NOW_ISO,
            json.dumps(pipeline, default=str),
            json.dumps(velocity, default=str),
            json.dumps(health_serializable, default=str),
            briefing_text,
        ),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    pipeline = gather_pipeline()
    velocity = gather_velocity()
    sessions = gather_sessions()
    health = check_health(pipeline, sessions)
    briefing = build_briefing(pipeline, velocity, sessions, health)

    print(briefing)

    try:
        store_snapshot(pipeline, velocity, health, briefing)
        print(f"[Snapshot stored in {OPS_DB}]")
    except Exception as exc:
        print(f"[WARN] Failed to store snapshot: {exc}", file=sys.stderr)

    return 0


# ---------------------------------------------------------------------------
# Adapter functions for run_autonomous_ops.py runner
# ---------------------------------------------------------------------------

def run_synthesis():
    """Run full synthesis pipeline and return briefing text (no print)."""
    pipeline = gather_pipeline()
    velocity = gather_velocity()
    sessions = gather_sessions()
    health = check_health(pipeline, sessions)
    briefing = build_briefing(pipeline, velocity, sessions, health)
    try:
        store_snapshot(pipeline, velocity, health, briefing)
    except Exception:
        pass
    return briefing


if __name__ == "__main__":
    sys.exit(main())
