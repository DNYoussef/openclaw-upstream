"""Pre-send DB corrections - Feb 24, 2026"""
import sqlite3
from datetime import datetime

db = sqlite3.connect('C:/Users/17175/.claude/outreach/outreach.db')
cur = db.cursor()
now = datetime.now().isoformat()

# Ely Kahn - update company and title
cur.execute("""UPDATE prospects SET company = 'Okta', title = 'Chief Product Officer, Okta Platform; Angel Investor'
    WHERE name = 'Ely Kahn'""")
print('Updated Ely Kahn: company -> Okta, title -> CPO Okta Platform')

# Pat Opet - update company
cur.execute("""UPDATE prospects SET company = 'State Street (ex-JPMorgan Chase)',
    notes = notes || ' | Feb 24: Transitioning to State Street as Deputy CISO & Head of Fusion/Security Ops.'
    WHERE name = 'Pat Opet'""")
print('Updated Pat Opet: company -> State Street (ex-JPMorgan Chase)')

# Log corrections
for detail in ['Ely Kahn: company SentinelOne->Okta, title updated (moved Jan 2026)',
               'Pat Opet: company JPMorgan->State Street (transitioning)']:
    cur.execute("INSERT INTO activity_log (action, details, timestamp) VALUES ('db_correction', ?, ?)", (detail, now))

db.commit()
db.close()
print('Done.')
