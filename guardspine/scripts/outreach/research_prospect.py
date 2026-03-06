#!/usr/bin/env python
"""
DB helper for prospect research pipeline.

Usage:
    python research_prospect.py --list <segment> <batch>     List prospects for batch (0-4)
    python research_prospect.py --write <id> <notes_file>    Write research_notes from file
    python research_prospect.py --stats                      Show research coverage stats
    python research_prospect.py --audit                      Audit research quality
"""

import sqlite3
import os
import sys
import json

DB_PATH = os.path.expanduser("~/.claude/outreach/outreach.db")
CAMPAIGN = "landing_page_200_feb26"
BATCH_SIZE = 20


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def list_batch(segment, batch_num):
    """List prospects for a given segment and batch number."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT id, name, title, company, industry, notes, linkedin_url,
           target_segment, channel, utm_content
           FROM prospects
           WHERE campaign = ? AND target_segment = ?
           ORDER BY name
           LIMIT ? OFFSET ?""",
        (CAMPAIGN, segment, BATCH_SIZE, batch_num * BATCH_SIZE)
    )
    rows = cur.fetchall()
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "name": row["name"],
            "title": row["title"] or "",
            "company": row["company"] or "",
            "industry": row["industry"] or "",
            "notes": row["notes"] or "",
            "linkedin_url": row["linkedin_url"] or "",
            "segment": row["target_segment"],
            "channel": row["channel"] or "",
            "utm_content": row["utm_content"] or "",
        })
    conn.close()
    print(json.dumps(result, indent=2))
    return result


def write_research(prospect_id, notes_file):
    """Write research_notes from a file to the DB."""
    with open(notes_file, "r", encoding="utf-8") as f:
        notes = f.read().strip()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE prospects SET research_notes = ? WHERE id = ?",
        (notes, prospect_id)
    )
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if affected:
        print(f"OK: wrote research_notes for {prospect_id}")
    else:
        print(f"WARN: no row matched id {prospect_id}")


def show_stats():
    """Show research coverage stats."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT target_segment,
            COUNT(*) as total,
            SUM(CASE WHEN research_notes IS NOT NULL AND research_notes != '' THEN 1 ELSE 0 END) as researched,
            SUM(CASE WHEN research_notes LIKE '%CONFIDENCE: HIGH%' THEN 1 ELSE 0 END) as high,
            SUM(CASE WHEN research_notes LIKE '%CONFIDENCE: MEDIUM%' THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN research_notes LIKE '%CONFIDENCE: LOW%' THEN 1 ELSE 0 END) as low
        FROM prospects
        WHERE campaign = ?
        GROUP BY target_segment
    """, (CAMPAIGN,))
    for row in cur.fetchall():
        print(f"{row['target_segment']}: {row['researched']}/{row['total']} researched "
              f"(HIGH={row['high']}, MEDIUM={row['medium']}, LOW={row['low']})")
    conn.close()


def audit_quality():
    """Audit research quality - find LOW confidence and missing research."""
    conn = get_conn()
    cur = conn.cursor()

    # Missing research
    cur.execute("""
        SELECT name, company, target_segment FROM prospects
        WHERE campaign = ? AND (research_notes IS NULL OR research_notes = '')
        ORDER BY target_segment, name
    """, (CAMPAIGN,))
    missing = cur.fetchall()
    if missing:
        print(f"\n=== MISSING RESEARCH ({len(missing)}) ===")
        for row in missing:
            print(f"  [{row['target_segment']}] {row['name']} @ {row['company']}")

    # LOW confidence
    cur.execute("""
        SELECT name, company, target_segment FROM prospects
        WHERE campaign = ? AND research_notes LIKE '%CONFIDENCE: LOW%'
        ORDER BY target_segment, name
    """, (CAMPAIGN,))
    low = cur.fetchall()
    if low:
        print(f"\n=== LOW CONFIDENCE ({len(low)}) ===")
        for row in low:
            print(f"  [{row['target_segment']}] {row['name']} @ {row['company']}")

    if not missing and not low:
        print("All prospects researched with HIGH/MEDIUM confidence.")

    conn.close()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "--list" and len(sys.argv) == 4:
        segment = sys.argv[2]
        batch_num = int(sys.argv[3])
        list_batch(segment, batch_num)

    elif cmd == "--write" and len(sys.argv) == 4:
        prospect_id = sys.argv[2]
        notes_file = sys.argv[3]
        write_research(prospect_id, notes_file)

    elif cmd == "--stats":
        show_stats()

    elif cmd == "--audit":
        audit_quality()

    else:
        print(__doc__)


if __name__ == "__main__":
    main()
