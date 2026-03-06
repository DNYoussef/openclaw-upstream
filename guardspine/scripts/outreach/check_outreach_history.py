#!/usr/bin/env python
"""Check outreach history for campaign prospects."""
import sqlite3
import os

DB_PATH = os.path.expanduser("~/.claude/outreach/outreach.db")
CAMPAIGN = "landing_page_200_feb26"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Activity log entries for campaign prospects
cur.execute("""SELECT a.timestamp, a.action, a.details, p.name, p.company
    FROM activity_log a
    JOIN prospects p ON a.prospect_id = p.id
    WHERE p.campaign = ?
    ORDER BY p.name, a.timestamp""", (CAMPAIGN,))
rows = cur.fetchall()
print("Activity entries for campaign prospects:", len(rows))
current = ""
for r in rows:
    label = "%s @ %s" % (r[3], r[4])
    if label != current:
        current = label
        print("\n=== %s ===" % label)
    det = (r[2] or "")[:150]
    print("  %s | %s | %s" % (r[0][:10], r[1], det))

# Summary of all contacted prospects
print("\n\n========== CONTACTED SUMMARY ==========")
cur.execute("""SELECT id, name, company, target_segment, message_sent_at,
    response_received, signal_type, signal_notes, artifact_sent, notes, channel
    FROM prospects WHERE campaign = ?
    AND (message_sent_at IS NOT NULL OR response_received = 1
         OR signal_type != 'none' OR artifact_sent IS NOT NULL)
    ORDER BY target_segment, name""", (CAMPAIGN,))
for r in cur.fetchall():
    pid, name, company, seg, sent, resp, sig, sig_notes, artifact, notes, channel = r
    print("\n--- [%s] %s @ %s (id: %s) ---" % (seg, name, company, pid))
    if sent:
        print("  SENT: %s" % sent)
    if resp:
        print("  RESPONSE: YES")
    if sig and sig != "none":
        print("  SIGNAL: %s" % sig)
    if sig_notes:
        print("  SIGNAL NOTES: %s" % sig_notes[:200])
    if artifact:
        print("  ARTIFACT: %s" % artifact)
    if channel:
        print("  CHANNEL: %s" % channel)

# Connection requests from notes
print("\n\n========== CONNECTION REQUESTS (from notes) ==========")
cur.execute("""SELECT id, name, company, target_segment, notes, channel
    FROM prospects WHERE campaign = ?
    AND notes LIKE '%connection sent%' OR notes LIKE '%Connection request sent%'
    AND campaign = ?
    ORDER BY name""", (CAMPAIGN, CAMPAIGN))
for r in cur.fetchall():
    pid, name, company, seg, notes, channel = r
    # Extract connection date
    for line in (notes or "").split("."):
        line = line.strip()
        if "connection" in line.lower() and "sent" in line.lower():
            print("[%s] %s @ %s -- %s" % (seg, name, company, line))

# DMs drafted pending send
print("\n\n========== DMs DRAFTED (pending send) ==========")
cur.execute("""SELECT id, name, company, target_segment, notes
    FROM prospects WHERE campaign = ?
    AND notes LIKE '%pending send%'
    ORDER BY name""", (CAMPAIGN,))
for r in cur.fetchall():
    print("[%s] %s @ %s" % (r[3], r[1], r[2]))

conn.close()
