import sqlite3
from datetime import datetime
db = sqlite3.connect('C:/Users/17175/.claude/outreach/outreach.db')
cur = db.cursor()
now = datetime.now().isoformat()

cur.execute("""UPDATE prospects SET
    linkedin_url = 'https://www.linkedin.com/in/tiffanymasson',
    notes = notes || ' | Feb 24: LinkedIn confirmed. Psy.D. Also President of Kansas Health Science Center. Falkovia = AI advisory for education/healthcare. G.U.A.R.D Protocol unverified externally -- do not reference.'
    WHERE name = 'Tiffany Masson'""")
cur.execute("INSERT INTO activity_log (action, details, timestamp) VALUES ('db_correction', 'Tiffany Masson: added LinkedIn URL linkedin.com/in/tiffanymasson', ?)", (now,))
db.commit()
print('Tiffany Masson updated. Rows:', cur.rowcount)
db.close()
