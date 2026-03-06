#!/usr/bin/env python3
"""
Update outreach message signatures and developer CTA tone.

CISO: Replace "- David" sign-off with 3-link signature.
Developer: Rewrite CTA line to humble/helpful tone, replace UTM URLs
           with GitHub repo + guardspine.ai/dev, update sign-off.

Safe: reads DB, shows preview, requires --apply to write.
"""

import sqlite3
import re
import sys
from pathlib import Path

DB_PATH = Path.home() / ".claude" / "outreach" / "outreach.db"

CISO_SIGNOFF = """- David

guardspine.ai | dnyoussef.com
linkedin.com/in/davidyoussef"""

DEV_SIGNOFF = """- David

github.com/DNYoussef/codeguard-action
guardspine.ai/dev"""

# Patterns to match the existing CTA line in dev messages
# These are lines containing guardspine.ai/dev URLs (with optional UTM params)
UTM_URL_RE = re.compile(
    r'https?://guardspine\.ai/\S*'
)

# Match CTA lines that contain ROI/calculator/hours language
ROI_CTA_RE = re.compile(
    r'.*(calculator|roi|hours lost|hours saved|review hours|cost model).*guardspine\.ai.*',
    re.IGNORECASE
)

# Match CTA lines that are just a URL or have guardspine.ai/dev link
GUARDSPINE_DEV_LINE_RE = re.compile(
    r'^.*https?://guardspine\.ai/dev\S*.*$',
    re.IGNORECASE
)


def rewrite_dev_cta_line(line):
    """Rewrite a dev CTA line to humble/helpful tone with correct links."""
    stripped = line.strip()

    # If it's just a bare URL, replace entirely
    if stripped.startswith("http"):
        return "Happy to help if useful: https://github.com/DNYoussef/codeguard-action"

    # If it mentions calculator/ROI/hours -- rewrite
    if ROI_CTA_RE.match(stripped):
        return "Happy to help if useful: https://github.com/DNYoussef/codeguard-action"

    # If it contains a guardspine.ai/dev URL (with context around it)
    if "guardspine.ai/dev" in stripped or "guardspine.ai/security" in stripped:
        # Keep the descriptive prefix, replace the URL
        prefix = UTM_URL_RE.sub("", stripped).rstrip(": ").rstrip()
        if prefix and len(prefix) > 10:
            return f"{prefix}: https://github.com/DNYoussef/codeguard-action"
        return "Happy to help if useful: https://github.com/DNYoussef/codeguard-action"

    return line


def update_ciso_message(msg):
    """Replace CISO sign-off with 3-link signature."""
    # Remove trailing whitespace/newlines
    msg = msg.rstrip()

    # Replace "- David" at the end with the full signature
    if msg.endswith("- David"):
        msg = msg[:-len("- David")].rstrip()
        return msg + "\n\n" + CISO_SIGNOFF
    return msg + "\n\n" + CISO_SIGNOFF


def update_dev_message(msg):
    """Rewrite dev CTA line and sign-off."""
    lines = msg.split("\n")
    new_lines = []
    skip_old_signoff = False

    for i, line in enumerate(lines):
        # Rewrite CTA lines containing guardspine.ai URLs
        if GUARDSPINE_DEV_LINE_RE.match(line):
            new_lines.append(rewrite_dev_cta_line(line))
            continue

        # Also catch calculator/ROI lines without guardspine URL
        if ROI_CTA_RE.match(line.strip()) and "guardspine" not in line:
            new_lines.append(rewrite_dev_cta_line(line))
            continue

        new_lines.append(line)

    # Rejoin and handle sign-off
    result = "\n".join(new_lines).rstrip()

    # Replace "- David" at the end with dev signature
    if result.endswith("- David"):
        result = result[:-len("- David")].rstrip()
        return result + "\n\n" + DEV_SIGNOFF

    return result + "\n\n" + DEV_SIGNOFF


def preview_changes(conn):
    """Show what will change without writing."""
    cur = conn.cursor()

    # CISOs
    cur.execute(
        "SELECT id, name, company, message_draft FROM prospects "
        "WHERE target_segment='ciso' AND message_draft IS NOT NULL"
    )
    ciso_rows = cur.fetchall()

    # Devs
    cur.execute(
        "SELECT id, name, company, message_draft FROM prospects "
        "WHERE target_segment='developer' AND message_draft IS NOT NULL"
    )
    dev_rows = cur.fetchall()

    print(f"=== CISO Messages: {len(ciso_rows)} ===")
    for pid, name, company, msg in ciso_rows[:3]:
        updated = update_ciso_message(msg)
        # Show last 5 lines
        tail = "\n".join(updated.split("\n")[-5:])
        print(f"\n  {name} @ {company}:")
        print(f"  ...{tail}")

    print(f"\n\n=== Developer Messages: {len(dev_rows)} ===")
    for pid, name, company, msg in dev_rows[:3]:
        updated = update_dev_message(msg)
        # Show last 7 lines
        tail = "\n".join(updated.split("\n")[-7:])
        print(f"\n  {name} @ {company}:")
        print(f"  ...{tail}")

    print(f"\n\nTotal: {len(ciso_rows)} CISOs + {len(dev_rows)} devs = {len(ciso_rows) + len(dev_rows)} messages")
    return ciso_rows, dev_rows


def apply_changes(conn):
    """Write updated messages to DB."""
    cur = conn.cursor()

    # CISOs
    cur.execute(
        "SELECT id, message_draft FROM prospects "
        "WHERE target_segment='ciso' AND message_draft IS NOT NULL"
    )
    ciso_count = 0
    for pid, msg in cur.fetchall():
        updated = update_ciso_message(msg)
        conn.execute(
            "UPDATE prospects SET message_draft = ? WHERE id = ?",
            (updated, pid)
        )
        ciso_count += 1

    # Devs
    cur.execute(
        "SELECT id, message_draft FROM prospects "
        "WHERE target_segment='developer' AND message_draft IS NOT NULL"
    )
    dev_count = 0
    for pid, msg in cur.fetchall():
        updated = update_dev_message(msg)
        conn.execute(
            "UPDATE prospects SET message_draft = ? WHERE id = ?",
            (updated, pid)
        )
        dev_count += 1

    conn.commit()
    print(f"Updated {ciso_count} CISO messages + {dev_count} dev messages = {ciso_count + dev_count} total")


def main():
    if not DB_PATH.exists():
        print(f"ERROR: DB not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))

    if "--apply" in sys.argv:
        apply_changes(conn)
    else:
        preview_changes(conn)
        print("\nDry run. Use --apply to write changes.")

    conn.close()


if __name__ == "__main__":
    main()
