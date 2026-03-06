#!/usr/bin/env python
"""Audit contact data for the 200 campaign prospects."""
import sqlite3
import os

DB_PATH = os.path.expanduser("~/.claude/outreach/outreach.db")
CAMPAIGN = "landing_page_200_feb26"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Email counts
print("=== EMAIL DATA ===")
cur.execute("""SELECT target_segment, COUNT(*) as total,
    SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END) as has_email
    FROM prospects WHERE campaign = ? GROUP BY target_segment""", (CAMPAIGN,))
for r in cur.fetchall():
    print("%s: %d total, %d have email" % (r["target_segment"], r["total"], r["has_email"]))

# CISOs with emails
print("\n=== CISOs WITH EMAIL ===")
cur.execute("""SELECT name, company, email FROM prospects
    WHERE campaign = ? AND target_segment = 'ciso' AND email IS NOT NULL AND email != ''
    ORDER BY name""", (CAMPAIGN,))
for r in cur.fetchall():
    print("  %s @ %s: %s" % (r["name"], r["company"], r["email"]))

# Devs with emails
print("\n=== DEVELOPERS WITH EMAIL ===")
cur.execute("""SELECT name, company, email FROM prospects
    WHERE campaign = ? AND target_segment = 'developer' AND email IS NOT NULL AND email != ''
    ORDER BY name""", (CAMPAIGN,))
for r in cur.fetchall():
    print("  %s @ %s: %s" % (r["name"], r["company"], r["email"]))

# Check research_notes for github profiles (devs)
print("\n=== GITHUB PROFILES IN RESEARCH (developers) ===")
cur.execute("""SELECT id, name, company, research_notes, linkedin_url FROM prospects
    WHERE campaign = ? AND target_segment = 'developer'
    ORDER BY name""", (CAMPAIGN,))
for r in cur.fetchall():
    rn = r["research_notes"] or ""
    github_lines = []
    for line in rn.split("\n"):
        ll = line.lower()
        if "github.com/" in ll or "github profile" in ll or "github:" in ll:
            github_lines.append(line.strip()[:150])
    if github_lines:
        print("  %s @ %s:" % (r["name"], r["company"]))
        for gl in github_lines:
            print("    %s" % gl)

# Check research_notes for emails (CISOs)
print("\n=== EMAILS IN RESEARCH NOTES (CISOs) ===")
cur.execute("""SELECT id, name, company, research_notes FROM prospects
    WHERE campaign = ? AND target_segment = 'ciso'
    AND (email IS NULL OR email = '')
    ORDER BY name""", (CAMPAIGN,))
import re
for r in cur.fetchall():
    rn = r["research_notes"] or ""
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', rn)
    if emails:
        print("  %s @ %s: %s" % (r["name"], r["company"], ", ".join(emails)))

# Channel distribution excluding already-contacted
print("\n=== NON-CONTACTED CHANNEL DISTRIBUTION ===")
contacted_ids = (
    'a5fd2b211425','303ab8629fce','e1e6f88d3b63','ec8153d19e49','f834c7c2b451',
    '71cc75a80bb9','5ff0f6fe6e39','2be4ae03643d','1fc56760a9f8','bf06ccfb3269',
    '44cbc3b518b3','a9607749cbc2','43a6ce41a6d0','4aa00cd58b0d','68733ed7e609',
    '67e2621809c6','df967f28265a','0514a0b69b22','cacc40094fdf','95f36b54216c',
    '101e454755c2','84a35dc943cc','de78984f9197','dfbb7bd5f2b5','c971a7120246',
    '40a93d868df9','cd59f37ff006','8512d1344447','21012caa6484','241b178b2b9f',
    'ffa49d9a6be5','aa601bdcc350','65aaad136273','1de02bb18022','210bf904b776'
)
placeholders = ",".join(["?" for _ in contacted_ids])
cur.execute("""SELECT target_segment, channel, COUNT(*) as cnt FROM prospects
    WHERE campaign = ? AND id NOT IN (%s)
    GROUP BY target_segment, channel
    ORDER BY target_segment, channel""" % placeholders,
    (CAMPAIGN,) + contacted_ids)
for r in cur.fetchall():
    print("  %s | %s: %d" % (r["target_segment"], r["channel"], r["cnt"]))

conn.close()
