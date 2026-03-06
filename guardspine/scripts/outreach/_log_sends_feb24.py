"""Log all 9 outreach sends from Feb 24, 2026 session."""
import sqlite3
from datetime import datetime

db = sqlite3.connect('C:/Users/17175/.claude/outreach/outreach.db')
cur = db.cursor()
now = datetime.now().isoformat()

sends = [
    # (name, channel, notes)
    ('Dennis Chornenky', 'linkedin_connect', 'Feb 24: Connect request already pending from prior session. Full DM not sent (2nd-degree, no free message). Will send DM once connect accepted.'),
    ('Ely Kahn', 'linkedin_dm', 'Feb 24: Sent full DM via Message button (moved to Okta Jan 2026). Also sent connect invite. DB corrected: company->Okta, title->CPO Okta Platform.'),
    ('Pat Opet', 'linkedin_dm', 'Feb 24: Sent full DM via Message button (personalized note limit exhausted). Also sent connect request without note. DB corrected: company->State Street (ex-JPMorgan Chase).'),
    ('Drew Bomett', 'email', 'Feb 24: Email sent via Gmail to drew.bomett@bsci.com (Gmail ID: 19c8ff94ce0b436a). Corrected email after prior bounce.'),
    ('Sanjeev Sah', 'email', 'Feb 24: Email sent via Gmail to ssah@novanthealth.org (Gmail ID: 19c8ff95f6fa0655). Corrected email after prior bounce.'),
    ('Brent Foster', 'linkedin_dm', 'Feb 24: Follow-up DM sent (1st-degree). Referenced SLSA-compatible provenance metadata.'),
    ('Paulo Marques', 'linkedin_dm', 'Feb 24: Follow-up DM sent (1st-degree). Referenced evidence bundle spec.'),
    ('Yvonne Zhu', 'linkedin_dm', 'Feb 24: Follow-up DM sent (1st-degree). Referenced her Anthropic work on constitutional AI alignment.'),
    ('Tiffany Masson', 'linkedin_dm', 'Feb 24: Follow-up DM sent (1st-degree). Referenced Falkovia advisory + GuardSpine enforcement complementarity. G.U.A.R.D Protocol NOT referenced (unverified).'),
]

updated = 0
for name, channel, notes in sends:
    cur.execute("""UPDATE prospects SET
        message_sent_at = ?,
        channel = ?,
        signal_type = CASE WHEN signal_type IS NULL OR signal_type = 'none' THEN 'none' ELSE signal_type END,
        next_action = 'await_response',
        notes = COALESCE(notes, '') || ' | ' || ?
        WHERE name = ? AND (message_sent_at IS NULL OR message_sent_at < '2026-02-24')""",
        (now, channel, notes, name))
    if cur.rowcount > 0:
        updated += cur.rowcount
        print('LOGGED: {} -> {} ({})'.format(name, channel, cur.rowcount))
    else:
        # Already had a recent send - just update notes and next_action
        cur.execute("""UPDATE prospects SET
            next_action = 'await_response',
            notes = COALESCE(notes, '') || ' | ' || ?
            WHERE name = ?""", (notes, name))
        print('UPDATED (already sent): {} -> {} ({})'.format(name, channel, cur.rowcount))

# Log to activity_log
for name, channel, notes in sends:
    cur.execute("""INSERT INTO activity_log (action, details, timestamp)
        VALUES ('message_sent', ?, ?)""",
        ('Feb 24 batch: {} via {} -- {}'.format(name, channel, notes[:80]), now))

db.commit()
print()
print('=== BATCH SEND LOG COMPLETE ===')
print('Updated: {} prospect rows'.format(updated))
print('Activity log: {} entries added'.format(len(sends)))
db.close()
