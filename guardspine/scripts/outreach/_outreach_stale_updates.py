"""
Stale prospect triage - Feb 24, 2026
Mark cold prospects, set follow-up actions for Tier A.
"""
import sqlite3
from datetime import datetime

db = sqlite3.connect('C:/Users/17175/.claude/outreach/outreach.db')
cur = db.cursor()
now = datetime.now().isoformat()

updates = []

# Tier C: Mark as cold (40+ days, no response)
cold_names = [
    'Bulent Kiziltan', 'Netsai Massetti', 'Kim LaBarbiera',
    'Dr. Brian Anderson', 'Taylor Kull', 'Nevenka Micev',
    'Brian Riehle', 'Matt R Cole', 'Dr. Sonia Gupta',
    'Amit Gupta', 'Velmurugan Kandasamy', 'Monique Howard',
    'Rebeca Rodriguez Feria', 'Brian Blackner', 'Aly Budny'
]
for name in cold_names:
    cur.execute("""UPDATE prospects SET next_action = 'cold_no_followup'
        WHERE name = ? AND (signal_type IS NULL OR signal_type = 'none')
        AND next_action IS NULL""", (name,))
    if cur.rowcount > 0:
        updates.append('COLD: {}'.format(name))

# Jennifer Borrer (both entries) - deprioritize
cur.execute("""UPDATE prospects SET next_action = 'deprioritized_not_icp'
    WHERE name LIKE '%Jennifer Borrer%' AND (signal_type IS NULL OR signal_type = 'none')""")
updates.append('DEPRIORITIZE: Jennifer Borrer ({} rows)'.format(cur.rowcount))

# Tier A: Set follow-up actions
tier_a = [
    ('Paulo Marques', 'followup_value_add_feb26'),
    ('Tiffany Masson', 'followup_value_add_feb26'),
    ('James Moore', 'followup_value_add_feb26'),
    ('Marcin Klecha', 'followup_value_add_feb26'),
    ('Yvonne Zhu', 'followup_value_add_feb26'),
    ('Priti Sinha', 'followup_value_add_feb26'),
]
for name, action in tier_a:
    cur.execute("""UPDATE prospects SET next_action = ?
        WHERE name = ? AND (signal_type IS NULL OR signal_type = 'none')""",
        (action, name))
    if cur.rowcount > 0:
        updates.append('FOLLOWUP: {} -> {}'.format(name, action))

# Log
for u in updates:
    cur.execute("""INSERT INTO activity_log (action, details, timestamp)
        VALUES ('stale_triage', ?, ?)""", (u, now))

db.commit()
print('=== STALE TRIAGE APPLIED ===')
for u in updates:
    print('  ' + u)
print()
print('Total: {} updates'.format(len(updates)))
db.close()
