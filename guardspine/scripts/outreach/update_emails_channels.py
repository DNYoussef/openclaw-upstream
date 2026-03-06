#!/usr/bin/env python3
"""Update emails from GitHub discovery and set channel for all prospects."""

import sqlite3
import os
import hashlib

DB_PATH = os.path.expanduser("~/.claude/outreach/outreach.db")
CAMPAIGN = "landing_page_200_feb26"

# Verified emails from GitHub commits
NEW_EMAILS = {
    "James Ives": "iam@jamesiv.es",
    "Varun Sharma": "varunsh@stepsecurity.io",
    "Markus Wolf": "mail@markus-wolf.de",
}

# LinkedIn URLs from GitHub profiles
LINKEDIN_URLS = {
    "Ville Saukkonen": "https://www.linkedin.com/in/villesaukkonen/",
}


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Update newly discovered emails
    email_updated = 0
    for name, email in NEW_EMAILS.items():
        cur.execute(
            "UPDATE prospects SET email = ? WHERE name = ? AND campaign = ? AND (email IS NULL OR email = '')",
            (email, name, CAMPAIGN)
        )
        if cur.rowcount > 0:
            email_updated += 1
            print(f"  Email updated: {name} -> {email}")

    # 2. Update LinkedIn URLs where known
    for name, url in LINKEDIN_URLS.items():
        cur.execute(
            "UPDATE prospects SET linkedin_url = ? WHERE name = ? AND campaign = ? AND (linkedin_url IS NULL OR linkedin_url = '')",
            (url, name, CAMPAIGN)
        )

    # 3. Set channel for all prospects:
    #    - Has email -> "email" (primary), can also DM on LinkedIn
    #    - Has LinkedIn URL but no email -> "linkedin_dm"
    #    - Neither -> "linkedin_connect" (need to connect first)
    cur.execute("""
        UPDATE prospects SET channel = 'email'
        WHERE campaign = ? AND email IS NOT NULL AND email != ''
        AND (channel IS NULL OR channel = '')
    """, (CAMPAIGN,))
    email_ch = cur.rowcount

    cur.execute("""
        UPDATE prospects SET channel = 'linkedin_dm'
        WHERE campaign = ? AND linkedin_url IS NOT NULL AND linkedin_url != ''
        AND (channel IS NULL OR channel = '') AND (email IS NULL OR email = '')
    """, (CAMPAIGN,))
    li_ch = cur.rowcount

    cur.execute("""
        UPDATE prospects SET channel = 'linkedin_connect'
        WHERE campaign = ? AND (channel IS NULL OR channel = '')
    """, (CAMPAIGN,))
    connect_ch = cur.rowcount

    # 4. Generate utm_content for all prospects (8-char hash of name)
    cur.execute("SELECT id, name FROM prospects WHERE campaign = ? AND (utm_content IS NULL OR utm_content = '')", (CAMPAIGN,))
    rows = cur.fetchall()
    for pid, name in rows:
        utm = hashlib.sha256(name.encode()).hexdigest()[:8]
        cur.execute("UPDATE prospects SET utm_content = ? WHERE id = ?", (utm, pid))

    conn.commit()

    # Summary
    print(f"\nEmails updated: {email_updated}")
    print(f"Channel assignments: {email_ch} email, {li_ch} linkedin_dm, {connect_ch} linkedin_connect")
    print(f"UTM codes generated: {len(rows)}")

    # Final email coverage
    cur.execute("""SELECT target_segment,
        SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END) as has_email,
        COUNT(*) as total
        FROM prospects WHERE campaign = ? GROUP BY target_segment""", (CAMPAIGN,))
    print("\nEmail coverage:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}/{row[2]} have email")

    # Channel breakdown
    cur.execute("""SELECT channel, COUNT(*) FROM prospects WHERE campaign = ? GROUP BY channel""", (CAMPAIGN,))
    print("\nChannel breakdown:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()


if __name__ == "__main__":
    main()
