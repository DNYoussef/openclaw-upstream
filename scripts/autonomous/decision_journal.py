#!/usr/bin/env python
"""Decision Journal & Exception Harvesting for GuardSpine autonomous ops.

Every manual decision, override, or edge case gets logged, clustered,
and eventually becomes a candidate for automation or policy.

DB: ~/.claude/autonomous/ops.db
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

DB_PATH = os.path.join(
    os.path.expanduser("~"), ".claude", "autonomous", "ops.db"
)

VALID_CATEGORIES = (
    "outreach",
    "architecture",
    "product",
    "strategy",
    "governance",
    "hiring",
    "exception",
    "override",
)

AUTOMATION_STATUSES = ("candidate", "implemented", "deferred", "rejected")

# -- stop words for clustering --
STOP_WORDS = frozenset(
    "a an the is was were be been being have has had do does did "
    "will would shall should may might must can could to of in for "
    "on with at by from as into through during before after above "
    "below between and but or nor not no so if then than that this "
    "it its they them their he she his her we our you your i my me".split()
)


# ============================================================
# Database setup
# ============================================================

def _get_conn():
    """Return a connection to the ops database, creating tables if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS decisions (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp            TEXT NOT NULL,
            category             TEXT NOT NULL,
            decision             TEXT NOT NULL,
            context              TEXT NOT NULL,
            alternatives         TEXT,
            outcome              TEXT,
            automation_candidate INTEGER DEFAULT 0,
            cluster_id           TEXT
        );

        CREATE TABLE IF NOT EXISTS exceptions (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp         TEXT NOT NULL,
            workflow          TEXT NOT NULL,
            description       TEXT NOT NULL,
            resolution        TEXT NOT NULL,
            should_automate   INTEGER,
            occurrence_count  INTEGER DEFAULT 1,
            cluster_id        TEXT,
            policy_created    INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS clusters (
            id                   TEXT PRIMARY KEY,
            category             TEXT NOT NULL,
            pattern_description  TEXT NOT NULL,
            occurrence_count     INTEGER DEFAULT 0,
            first_seen           TEXT NOT NULL,
            last_seen            TEXT NOT NULL,
            automation_status    TEXT DEFAULT 'candidate'
        );

        CREATE INDEX IF NOT EXISTS idx_decisions_category
            ON decisions(category);
        CREATE INDEX IF NOT EXISTS idx_decisions_ts
            ON decisions(timestamp);
        CREATE INDEX IF NOT EXISTS idx_exceptions_workflow
            ON exceptions(workflow);
        CREATE INDEX IF NOT EXISTS idx_exceptions_ts
            ON exceptions(timestamp);
    """)
    conn.commit()


# ============================================================
# Clustering helpers
# ============================================================

def _significant_words(text):
    """Extract significant (non-stop) words from text, lowercased."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def _exception_cluster_key(workflow, description):
    """Build a cluster key from workflow + first 5 significant words."""
    sig = _significant_words(description)[:5]
    slug = "_".join(sig) if sig else "unknown"
    wf = re.sub(r"[^a-z0-9]+", "_", workflow.lower()).strip("_")
    return f"{wf}_{slug}"


def _decision_cluster_key(category, decision):
    """Build a cluster key from category + first 5 significant words."""
    sig = _significant_words(decision)[:5]
    slug = "_".join(sig) if sig else "unknown"
    return f"{category}_{slug}"


# ============================================================
# Core API
# ============================================================

def log_decision(category, decision, context, alternatives=None,
                 outcome=None, automation_candidate=False):
    """Log a manual decision for future analysis."""
    if category not in VALID_CATEGORIES:
        print(f"ERROR: Invalid category '{category}'. "
              f"Valid: {', '.join(VALID_CATEGORIES)}")
        return None

    now = datetime.now(timezone.utc).isoformat() + "Z"
    alt_json = json.dumps(alternatives) if alternatives else None
    auto = 1 if automation_candidate else 0
    cluster_id = _decision_cluster_key(category, decision)

    conn = _get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO decisions
               (timestamp, category, decision, context, alternatives,
                outcome, automation_candidate, cluster_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (now, category, decision, context, alt_json, outcome,
             auto, cluster_id),
        )
        row_id = cur.lastrowid

        # Upsert cluster
        conn.execute(
            """INSERT INTO clusters (id, category, pattern_description,
                   occurrence_count, first_seen, last_seen, automation_status)
               VALUES (?, ?, ?, 1, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                   occurrence_count = occurrence_count + 1,
                   last_seen = excluded.last_seen""",
            (cluster_id, category, decision, now, now,
             "candidate" if auto else "deferred"),
        )
        conn.commit()
        print(f"Logged decision #{row_id} [{category}] cluster={cluster_id}")
        return row_id
    finally:
        conn.close()


def log_exception(workflow, description, resolution, should_automate=None):
    """Log a workflow exception for pattern analysis."""
    now = datetime.now(timezone.utc).isoformat() + "Z"
    auto_val = None
    if should_automate is True:
        auto_val = 1
    elif should_automate is False:
        auto_val = 0

    cluster_id = _exception_cluster_key(workflow, description)

    conn = _get_conn()
    try:
        # Check for existing exceptions in same cluster
        existing = conn.execute(
            "SELECT id, occurrence_count FROM exceptions "
            "WHERE cluster_id = ? ORDER BY timestamp DESC LIMIT 1",
            (cluster_id,),
        ).fetchone()

        if existing:
            # Increment occurrence count on the latest row in this cluster
            conn.execute(
                "UPDATE exceptions SET occurrence_count = occurrence_count + 1 "
                "WHERE id = ?",
                (existing["id"],),
            )
            new_count = existing["occurrence_count"] + 1
        else:
            new_count = 1

        cur = conn.execute(
            """INSERT INTO exceptions
               (timestamp, workflow, description, resolution,
                should_automate, occurrence_count, cluster_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (now, workflow, description, resolution, auto_val,
             new_count, cluster_id),
        )
        row_id = cur.lastrowid

        # Upsert cluster
        conn.execute(
            """INSERT INTO clusters (id, category, pattern_description,
                   occurrence_count, first_seen, last_seen, automation_status)
               VALUES (?, 'exception', ?, ?, ?, ?, 'candidate')
               ON CONFLICT(id) DO UPDATE SET
                   occurrence_count = occurrence_count + 1,
                   last_seen = excluded.last_seen""",
            (cluster_id, description, new_count, now, now),
        )
        conn.commit()
        print(f"Logged exception #{row_id} [{workflow}] "
              f"cluster={cluster_id} (count={new_count})")
        return row_id
    finally:
        conn.close()


# ============================================================
# Analysis
# ============================================================

def analyze_patterns(days=30):
    """Analyze logged decisions and exceptions for patterns.

    Returns the report as a string and prints it.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat() + "Z"
    conn = _get_conn()
    try:
        # -- decision summary --
        rows = conn.execute(
            "SELECT category, COUNT(*) as cnt, "
            "SUM(automation_candidate) as auto "
            "FROM decisions WHERE timestamp >= ? "
            "GROUP BY category ORDER BY cnt DESC",
            (cutoff,),
        ).fetchall()

        lines = []
        lines.append(f"# Decision & Exception Analysis -- Last {days} Days")
        lines.append("")

        if rows:
            lines.append("## Decision Summary")
            lines.append("| Category      | Count | Auto-Candidates |")
            lines.append("|---------------|-------|-----------------|")
            for r in rows:
                lines.append(
                    f"| {r['category']:<13} | {r['cnt']:<5} | {r['auto']:<15} |"
                )
        else:
            lines.append("## Decision Summary")
            lines.append("No decisions logged in this period.")
        lines.append("")

        # -- repeated exceptions (policy gap candidates) --
        exc_rows = conn.execute(
            "SELECT workflow, cluster_id, description, "
            "MAX(occurrence_count) as max_count "
            "FROM exceptions WHERE timestamp >= ? "
            "GROUP BY cluster_id "
            "HAVING max_count >= 3 "
            "ORDER BY max_count DESC",
            (cutoff,),
        ).fetchall()

        lines.append("## Repeated Exceptions (Policy Gap Candidates)")
        if exc_rows:
            lines.append(
                "| Workflow          | Pattern"
                "                         | Count | Status    |"
            )
            lines.append(
                "|-------------------|-------"
                "--------------------------|-------|-----------|"
            )
            for r in exc_rows:
                cluster = conn.execute(
                    "SELECT automation_status FROM clusters WHERE id = ?",
                    (r["cluster_id"],),
                ).fetchone()
                status = cluster["automation_status"] if cluster else "unknown"
                pat = r["description"][:35]
                lines.append(
                    f"| {r['workflow']:<17} | {pat:<33} "
                    f"| {r['max_count']:<5} | {status:<9} |"
                )
        else:
            lines.append("No repeated exceptions (3+) in this period.")
        lines.append("")

        # -- automation candidates --
        cand_rows = conn.execute(
            "SELECT category, decision, cluster_id "
            "FROM decisions "
            "WHERE automation_candidate = 1 AND timestamp >= ? "
            "ORDER BY timestamp DESC",
            (cutoff,),
        ).fetchall()

        # Deduplicate by cluster, count occurrences
        cluster_counts = Counter()
        cluster_examples = {}
        for r in cand_rows:
            cid = r["cluster_id"]
            cluster_counts[cid] += 1
            if cid not in cluster_examples:
                cluster_examples[cid] = (r["category"], r["decision"])

        lines.append("## Top Automation Candidates")
        if cluster_counts:
            for i, (cid, count) in enumerate(
                cluster_counts.most_common(10), start=1
            ):
                cat, desc = cluster_examples[cid]
                short = desc[:60]
                lines.append(f"{i}. [{cat}] {short} (seen {count}x)")
        else:
            lines.append("No automation candidates in this period.")
        lines.append("")

        report = "\n".join(lines)
        print(report)
        return report
    finally:
        conn.close()


def list_decisions(days=7, category=None):
    """List recent decisions, optionally filtered by category."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat() + "Z"
    conn = _get_conn()
    try:
        if category:
            if category not in VALID_CATEGORIES:
                print(f"ERROR: Invalid category '{category}'. "
                      f"Valid: {', '.join(VALID_CATEGORIES)}")
                return
            rows = conn.execute(
                "SELECT * FROM decisions "
                "WHERE timestamp >= ? AND category = ? "
                "ORDER BY timestamp DESC",
                (cutoff, category),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM decisions WHERE timestamp >= ? "
                "ORDER BY timestamp DESC",
                (cutoff,),
            ).fetchall()

        if not rows:
            print(f"No decisions in the last {days} days"
                  + (f" for category '{category}'" if category else "")
                  + ".")
            return

        print(f"# Decisions -- Last {days} Days"
              + (f" [{category}]" if category else ""))
        print("")
        print("| # | Timestamp           | Category   | Decision"
              "                              | Auto |")
        print("|---|---------------------|------------|-------"
              "-------------------------------|------|")
        for r in rows:
            ts = r["timestamp"][:19]
            dec = r["decision"][:40]
            auto = "Y" if r["automation_candidate"] else ""
            print(f"| {r['id']:<1} | {ts} | {r['category']:<10} "
                  f"| {dec:<37} | {auto:<4} |")
        print("")
    finally:
        conn.close()


def list_candidates():
    """Show all clusters marked as automation candidates."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM clusters "
            "WHERE automation_status = 'candidate' "
            "ORDER BY occurrence_count DESC",
        ).fetchall()

        if not rows:
            print("No automation candidates found.")
            return

        print("# Automation Candidates")
        print("")
        print("| Cluster ID                        | Category   "
              "| Count | First Seen          | Last Seen           |")
        print("|-----------------------------------|------------|"
              "-------|---------------------|---------------------|")
        for r in rows:
            cid = r["id"][:35]
            fs = r["first_seen"][:19]
            ls = r["last_seen"][:19]
            print(f"| {cid:<33} | {r['category']:<10} "
                  f"| {r['occurrence_count']:<5} | {fs} | {ls} |")
        print("")
        print(f"Total: {len(rows)} candidates")
    finally:
        conn.close()


def update_outcome(decision_id, outcome):
    """Update the outcome field of a logged decision."""
    conn = _get_conn()
    try:
        cur = conn.execute(
            "UPDATE decisions SET outcome = ? WHERE id = ?",
            (outcome, decision_id),
        )
        conn.commit()
        if cur.rowcount:
            print(f"Updated outcome for decision #{decision_id}")
        else:
            print(f"ERROR: Decision #{decision_id} not found")
    finally:
        conn.close()


def mark_policy_created(exception_id):
    """Mark an exception as having led to a policy."""
    conn = _get_conn()
    try:
        cur = conn.execute(
            "UPDATE exceptions SET policy_created = 1 WHERE id = ?",
            (exception_id,),
        )
        conn.commit()
        if cur.rowcount:
            print(f"Marked exception #{exception_id} as policy-created")
        else:
            print(f"ERROR: Exception #{exception_id} not found")
    finally:
        conn.close()


def update_cluster_status(cluster_id, status):
    """Update automation status of a cluster."""
    if status not in AUTOMATION_STATUSES:
        print(f"ERROR: Invalid status '{status}'. "
              f"Valid: {', '.join(AUTOMATION_STATUSES)}")
        return
    conn = _get_conn()
    try:
        cur = conn.execute(
            "UPDATE clusters SET automation_status = ? WHERE id = ?",
            (status, cluster_id),
        )
        conn.commit()
        if cur.rowcount:
            print(f"Updated cluster '{cluster_id}' -> {status}")
        else:
            print(f"ERROR: Cluster '{cluster_id}' not found")
    finally:
        conn.close()


# ============================================================
# CLI
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(
        description="Decision Journal & Exception Harvesting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python decision_journal.py log --category outreach "
            '--decision "Skipped X" --context "ARR too low"\n'
            "  python decision_journal.py exception "
            '--workflow compose_messages --description "No LinkedIn" '
            '--resolution "Used Twitter"\n'
            "  python decision_journal.py analyze --days 30\n"
            "  python decision_journal.py list --days 7 --category outreach\n"
            "  python decision_journal.py candidates\n"
        ),
    )
    sub = parser.add_subparsers(dest="command")

    # -- log --
    p_log = sub.add_parser("log", help="Log a manual decision")
    p_log.add_argument("--category", required=True,
                       choices=VALID_CATEGORIES)
    p_log.add_argument("--decision", required=True)
    p_log.add_argument("--context", required=True)
    p_log.add_argument("--alternatives", nargs="*", default=None,
                       help="Alternative options considered")
    p_log.add_argument("--outcome", default=None)
    p_log.add_argument("--auto", action="store_true",
                       help="Mark as automation candidate")

    # -- exception --
    p_exc = sub.add_parser("exception", help="Log a workflow exception")
    p_exc.add_argument("--workflow", required=True)
    p_exc.add_argument("--description", required=True)
    p_exc.add_argument("--resolution", required=True)
    p_exc.add_argument("--should-automate", choices=["yes", "no"],
                       default=None)

    # -- analyze --
    p_az = sub.add_parser("analyze", help="Analyze patterns")
    p_az.add_argument("--days", type=int, default=30)

    # -- list --
    p_ls = sub.add_parser("list", help="List recent decisions")
    p_ls.add_argument("--days", type=int, default=7)
    p_ls.add_argument("--category", choices=VALID_CATEGORIES, default=None)

    # -- candidates --
    sub.add_parser("candidates", help="Show automation candidates")

    # -- update-outcome --
    p_uo = sub.add_parser("update-outcome",
                          help="Set outcome on a decision")
    p_uo.add_argument("--id", type=int, required=True)
    p_uo.add_argument("--outcome", required=True)

    # -- mark-policy --
    p_mp = sub.add_parser("mark-policy",
                          help="Mark exception as policy-created")
    p_mp.add_argument("--id", type=int, required=True)

    # -- cluster-status --
    p_cs = sub.add_parser("cluster-status",
                          help="Update cluster automation status")
    p_cs.add_argument("--cluster-id", required=True)
    p_cs.add_argument("--status", required=True,
                       choices=AUTOMATION_STATUSES)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "log":
        log_decision(
            category=args.category,
            decision=args.decision,
            context=args.context,
            alternatives=args.alternatives,
            outcome=args.outcome,
            automation_candidate=args.auto,
        )
    elif args.command == "exception":
        sa = None
        if args.should_automate == "yes":
            sa = True
        elif args.should_automate == "no":
            sa = False
        log_exception(
            workflow=args.workflow,
            description=args.description,
            resolution=args.resolution,
            should_automate=sa,
        )
    elif args.command == "analyze":
        analyze_patterns(days=args.days)
    elif args.command == "list":
        list_decisions(days=args.days, category=args.category)
    elif args.command == "candidates":
        list_candidates()
    elif args.command == "update-outcome":
        update_outcome(args.id, args.outcome)
    elif args.command == "mark-policy":
        mark_policy_created(args.id)
    elif args.command == "cluster-status":
        update_cluster_status(args.cluster_id, args.status)

    return 0


# Adapter alias for run_autonomous_ops.py runner
analyze = analyze_patterns


if __name__ == "__main__":
    sys.exit(main())
