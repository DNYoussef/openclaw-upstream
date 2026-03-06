"""Log Tier 2 LinkedIn DM sends to outreach DB - Feb 24, 2026.
Run AFTER confirming all sends completed via browser automation."""
import sqlite3
from datetime import datetime

db = sqlite3.connect('C:/Users/17175/.claude/outreach/outreach.db')
cur = db.cursor()
now = datetime.now().isoformat()

# All 20 Tier 2 targets
tier2_sent = [
    'Steve Messina',
    'Tim Wedande',
    'Berta Rodriguez-Hervas',
    'Leo Cullen',
    'Erick Antezana',
    'Richard Schaefer',
    'Christos Varsakelis',
    'Aaron Bennett',
    'Varun Chhibber',
    'Andreas Freund',
    'Dan McInerney',
    'Lucas Walter',
    'Iannis Drakos',
    'Casey Fleming',
    'Tarek Ahmad',
    'Craig Schmitz',
    'Matt Schmid',
    'Travis Lee',
    'Doug Hubbard',
    'Andrew Penner',
]

updated = 0
for name in tier2_sent:
    row = cur.execute("SELECT id, message_sent_at FROM prospects WHERE name = ?", (name,)).fetchone()
    if not row:
        print('NOT FOUND: {}'.format(name))
        continue
    pid, already_sent = row
    if already_sent:
        print('SKIP (already sent): {} at {}'.format(name, already_sent))
        continue
    cur.execute("""UPDATE prospects SET
        message_sent_at = ?,
        channel = 'linkedin_dm',
        signal_type = 'none',
        next_action = 'await_response'
    WHERE id = ?""", (now, pid))
    cur.execute("""INSERT INTO activity_log (action, details, timestamp)
        VALUES ('message_sent', ?, ?)""",
        ('Tier 2 LinkedIn DM to {} (Feb 24 sweep)'.format(name), now))
    updated += 1
    print('LOGGED: {}'.format(name))

db.commit()
print()
print('Total logged: {}'.format(updated))
db.close()
