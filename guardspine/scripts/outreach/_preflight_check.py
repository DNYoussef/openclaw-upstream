"""Pre-flight checklist for 9 outreach messages - Feb 24, 2026"""
import sqlite3

db = sqlite3.connect('C:/Users/17175/.claude/outreach/outreach.db')
cur = db.cursor()

targets = [
    'Dennis Chornenky',
    'Ely Kahn',
    'Pat Opet',
    'Drew Bomett',
    'Sanjeev Sah',
    'Brent Foster',
    'Paulo Marques',
    'Tiffany Masson',
    'Yvonne Zhu',
]

print('=== PRE-FLIGHT CHECKLIST ===')
print()
for name in targets:
    rows = cur.execute("""SELECT name, email, channel, linkedin_url, company, title,
        signal_type, message_sent_at, lane, investor_score, next_action
        FROM prospects WHERE name = ? ORDER BY signal_type DESC LIMIT 1""", (name,)).fetchall()
    if rows:
        r = rows[0]
        print('--- {} ---'.format(r[0]))
        print('  Title: {} @ {}'.format(r[1+4] or '?', r[1+3] or '?'))
        print('  Email: {}'.format(r[1] or '(NONE)'))
        print('  LinkedIn: {}'.format(r[3] or '(NONE)'))
        print('  Channel (DB): {}'.format(r[2] or '(UNSET)'))
        print('  Signal: {} | Sent: {} | Score: {}'.format(r[6] or 'none', r[7] or 'never', r[9]))
        print('  Next action: {}'.format(r[10] or '(none)'))
        print()
    else:
        print('--- {} --- NOT FOUND'.format(name))
        print()

# Also check: any prior messages to these emails
print('=== EMAIL DUPLICATE CHECK ===')
emails_to_check = ['drew.bomett@bsci.com', 'ssah@novanthealth.org']
for em in emails_to_check:
    sent = cur.execute("""SELECT name, message_sent_at, signal_type FROM prospects
        WHERE email = ? AND message_sent_at IS NOT NULL""", (em,)).fetchall()
    if sent:
        for s in sent:
            print('  {} -> already sent {} (signal: {})'.format(em, s[1], s[2]))
    else:
        print('  {} -> no prior send recorded'.format(em))

db.close()
