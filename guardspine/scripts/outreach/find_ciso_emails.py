#!/usr/bin/env python3
"""
CISO email discovery helper.
Stores results in outreach.db email column with confidence in notes.

Usage: Called by agents, not directly. Each agent handles a batch.
"""

import sqlite3
import re
from pathlib import Path

DB_PATH = Path.home() / ".claude" / "outreach" / "outreach.db"


def get_cisos_without_email():
    """Return list of (id, name, company) for CISOs without email."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, company FROM prospects "
        "WHERE target_segment='ciso' AND (email IS NULL OR email = '') "
        "ORDER BY name"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def store_email(prospect_id, email, confidence, source):
    """Store discovered email in DB.

    confidence: HIGH, MEDIUM, LOW
    source: e.g. 'conference bio', 'pattern guess', 'company page'
    """
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Get existing notes
    cur.execute("SELECT notes FROM prospects WHERE id = ?", (prospect_id,))
    row = cur.fetchone()
    existing_notes = row[0] if row and row[0] else ""

    # Append email source info
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


def validate_email_format(email):
    """Basic email format validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def guess_corporate_email(name, company_domain):
    """Generate common corporate email patterns."""
    parts = name.lower().split()
    if len(parts) < 2:
        return []

    first = parts[0]
    last = parts[-1]

    # Remove common suffixes
    for suffix in [',', 'jr', 'jr.', 'sr', 'sr.', 'iii', 'ii', 'phd', 'md', 'mba']:
        last = last.rstrip(suffix).rstrip(',').rstrip('.')

    patterns = [
        f"{first}.{last}@{company_domain}",
        f"{first[0]}{last}@{company_domain}",
        f"{first}{last[0]}@{company_domain}",
        f"{first}_{last}@{company_domain}",
        f"{first}@{company_domain}",
        f"{last}@{company_domain}",
    ]
    return patterns


if __name__ == "__main__":
    cisos = get_cisos_without_email()
    print(f"CISOs without email: {len(cisos)}")
    for pid, name, company in cisos:
        print(f"  {name} @ {company}")
