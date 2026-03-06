#!/usr/bin/env python3
"""
Developer GitHub email discovery helper.
Uses gh API to find public emails from GitHub profiles.

Usage: Called by agents, not directly. Each agent handles a batch.
"""

import sqlite3
import re
from pathlib import Path

DB_PATH = Path.home() / ".claude" / "outreach" / "outreach.db"


def get_devs_without_email():
    """Return list of (id, name, company, research_notes) for devs without email."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, company, research_notes FROM prospects "
        "WHERE target_segment='developer' AND (email IS NULL OR email = '') "
        "ORDER BY name"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def extract_github_username(research_notes):
    """Try to extract GitHub username from research notes."""
    if not research_notes:
        return None
    match = re.search(r'github\.com/([a-zA-Z0-9_-]+)', research_notes)
    if match:
        return match.group(1)
    return None


def store_email(prospect_id, email, confidence, source):
    """Store discovered email in DB."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("SELECT notes FROM prospects WHERE id = ?", (prospect_id,))
    row = cur.fetchone()
    existing_notes = row[0] if row and row[0] else ""

    email_note = f"[EMAIL {confidence}] {email} via {source}"
    if existing_notes:
        new_notes = f"{existing_notes}\n{email_note}"
    else:
        new_notes = email_note

    cur.execute(
        "UPDATE prospects SET email = ?, notes = ? WHERE id = ?",
        (email, new_notes, prospect_id)
    )
    conn.commit()
    conn.close()


def store_github_username(prospect_id, username):
    """Store GitHub username in research_notes."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("SELECT research_notes FROM prospects WHERE id = ?", (prospect_id,))
    row = cur.fetchone()
    existing = row[0] if row and row[0] else ""

    if f"github.com/{username}" not in existing:
        note = f"GitHub: github.com/{username}"
        if existing:
            new_notes = f"{existing}\n{note}"
        else:
            new_notes = note
        cur.execute(
            "UPDATE prospects SET research_notes = ? WHERE id = ?",
            (new_notes, prospect_id)
        )
        conn.commit()

    conn.close()


if __name__ == "__main__":
    devs = get_devs_without_email()
    print(f"Devs without email: {len(devs)}")
    for pid, name, company, notes in devs:
        gh = extract_github_username(notes)
        gh_str = f" [GH: {gh}]" if gh else ""
        print(f"  {name} @ {company}{gh_str}")
