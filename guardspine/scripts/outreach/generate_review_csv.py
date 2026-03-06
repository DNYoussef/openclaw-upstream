#!/usr/bin/env python3
"""
Generate pre-send review CSV for David's approval.

Output: data/content-pipeline/outreach-review-feb26.csv

Columns:
  name, company, segment, channel, email, email_confidence,
  message_preview (first 100 chars), full_message

NOTHING IS SENT. This is for review only.
"""

import sqlite3
import csv
import re
import sys
from pathlib import Path

DB_PATH = Path.home() / ".claude" / "outreach" / "outreach.db"
OUTPUT_DIR = Path.home() / "data" / "content-pipeline"
OUTPUT_FILE = OUTPUT_DIR / "outreach-review-feb26.csv"


def extract_confidence(notes):
    """Extract email confidence from notes field. LOW wins over earlier tags."""
    if not notes:
        return "UNKNOWN"
    # Check LOW first -- a downgrade overrides earlier HIGH/MEDIUM
    for conf in ["LOW", "HIGH", "MEDIUM"]:
        if f"[EMAIL {conf}]" in notes:
            return conf
    return "UNKNOWN"


def main():
    if not DB_PATH.exists():
        print(f"ERROR: DB not found at {DB_PATH}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        "SELECT name, company, target_segment, channel, email, notes, message_draft "
        "FROM prospects WHERE message_draft IS NOT NULL "
        "ORDER BY target_segment, name"
    )
    rows = cur.fetchall()
    conn.close()

    with open(str(OUTPUT_FILE), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name", "company", "segment", "channel",
            "email", "email_confidence",
            "message_preview", "full_message"
        ])

        stats = {
            "total": 0,
            "with_email": 0,
            "ciso": 0,
            "developer": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "no_email": 0,
        }

        for name, company, segment, channel, email, notes, message in rows:
            confidence = extract_confidence(notes) if email else "NONE"
            preview = (message or "")[:100].replace("\n", " ")

            writer.writerow([
                name,
                company or "",
                segment or "",
                channel or "",
                email or "",
                confidence,
                preview,
                message or ""
            ])

            stats["total"] += 1
            if segment == "ciso":
                stats["ciso"] += 1
            else:
                stats["developer"] += 1

            if email:
                stats["with_email"] += 1
                if confidence == "HIGH":
                    stats["high"] += 1
                elif confidence == "MEDIUM":
                    stats["medium"] += 1
                elif confidence == "LOW":
                    stats["low"] += 1
            else:
                stats["no_email"] += 1

    print(f"Review CSV written to: {OUTPUT_FILE}")
    print(f"\nStats:")
    print(f"  Total prospects: {stats['total']}")
    print(f"  CISOs: {stats['ciso']}  |  Developers: {stats['developer']}")
    print(f"  With email: {stats['with_email']}")
    print(f"    HIGH confidence: {stats['high']}")
    print(f"    MEDIUM confidence: {stats['medium']}")
    print(f"    LOW confidence: {stats['low']}")
    print(f"  No email: {stats['no_email']}")
    print(f"\n** NOTHING HAS BEEN SENT. Review the CSV and approve before any sending. **")


if __name__ == "__main__":
    main()
