"""
Signal review updates - Feb 24, 2026
Apply DB updates for signal triage decisions.
"""
import sqlite3
from datetime import datetime

db = sqlite3.connect('C:/Users/17175/.claude/outreach/outreach.db')
cur = db.cursor()
now = datetime.now().isoformat()

updates = []

# 1. Hemangini Thakkar - deprioritize (left HSBC)
cur.execute("""UPDATE prospects SET next_action = 'deprioritized_left_company',
    signal_notes = signal_notes || ' | Feb 24: Deprioritized - left HSBC, no current employer found.'
    WHERE name = 'Hemangini Thakkar'""")
updates.append('Hemangini Thakkar: deprioritized (left HSBC)')

# 2. Erik Decker - switch to LinkedIn
cur.execute("""UPDATE prospects SET next_action = 'linkedin_connect', channel = 'linkedin_connect',
    signal_notes = signal_notes || ' | Feb 24: Switched to LinkedIn connect (email bounced, Outlook blocks).'
    WHERE name = 'Erik Decker'""")
updates.append('Erik Decker: switched to LinkedIn connect')

# 3. Sune Wettersteen - switch to LinkedIn
cur.execute("""UPDATE prospects SET next_action = 'linkedin_connect', channel = 'linkedin_connect',
    signal_notes = signal_notes || ' | Feb 24: Switched to LinkedIn (both email formats bounced).'
    WHERE name = 'Sune Wettersteen'""")
updates.append('Sune Wettersteen: switched to LinkedIn connect')

# 4. Brent Foster - mark follow-up needed
cur.execute("""UPDATE prospects SET next_action = 'send_value_add_followup_feb26'
    WHERE name = 'Brent Foster'""")
updates.append('Brent Foster: next_action -> send value-add follow-up by Feb 26')

# 5. Clean Kelsey Hightower duplicate signal note
# Find the duplicate (the one in stale list with score=None and sent 15d ago)
dupes = cur.execute("""SELECT id, name, signal_type FROM prospects
    WHERE name LIKE '%Kelsey Hightower%' ORDER BY id""").fetchall()
if len(dupes) > 1:
    # Keep the one with GREEN signal, mark other as duplicate
    for d in dupes:
        if d[2] != 'green':
            cur.execute("""UPDATE prospects SET next_action = 'DUPLICATE_REMOVE',
                signal_type = 'none',
                signal_notes = 'DUPLICATE of green-signal entry. Do not contact.'
                WHERE id = ?""", (d[0],))
            updates.append('Kelsey Hightower duplicate: marked for removal (id={})'.format(d[0]))

# 6. Clean Ishwar duplicate
ishwar_dupes = cur.execute("""SELECT id, name, signal_type, notes FROM prospects
    WHERE name LIKE '%Ishwar%' ORDER BY id""").fetchall()
if len(ishwar_dupes) > 1:
    for d in ishwar_dupes:
        if 'Duplicate' in str(d[3] or ''):
            cur.execute("""UPDATE prospects SET next_action = 'DUPLICATE_REMOVE',
                signal_type = 'none',
                signal_notes = 'DUPLICATE of primary Ishwar entry. Do not contact.'
                WHERE id = ?""", (d[0],))
            updates.append('Ishwar duplicate: marked for removal (id={})'.format(d[0]))

# Log all updates to activity_log
for u in updates:
    cur.execute("""INSERT INTO activity_log (action, details, timestamp)
        VALUES ('signal_review', ?, ?)""", (u, now))

db.commit()
print('=== SIGNAL REVIEW UPDATES APPLIED ===')
for u in updates:
    print('  ' + u)
print()
print('Total: {} updates'.format(len(updates)))

db.close()
