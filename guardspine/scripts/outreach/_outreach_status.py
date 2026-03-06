import sqlite3

db = sqlite3.connect('C:/Users/17175/.claude/outreach/outreach.db')
cur = db.cursor()

total = cur.execute('SELECT COUNT(*) FROM prospects').fetchone()[0]
sent = cur.execute("SELECT COUNT(*) FROM prospects WHERE message_sent_at IS NOT NULL").fetchone()[0]
unsent = total - sent

signals = cur.execute("SELECT signal_type, COUNT(*) as c FROM prospects WHERE signal_type IS NOT NULL AND signal_type != 'none' GROUP BY signal_type").fetchall()

lanes = cur.execute('SELECT lane, COUNT(*) as c FROM prospects GROUP BY lane').fetchall()

stale = cur.execute("SELECT COUNT(*) FROM prospects WHERE message_sent_at IS NOT NULL AND (signal_type IS NULL OR signal_type = 'none') AND julianday('now') - julianday(message_sent_at) > 7").fetchone()[0]

hot = cur.execute("SELECT name, investor_score, lane, target_segment FROM prospects WHERE message_sent_at IS NULL AND investor_score >= 75 ORDER BY investor_score DESC LIMIT 10").fetchall()

recent = cur.execute('SELECT action, details, timestamp FROM activity_log ORDER BY timestamp DESC LIMIT 5').fetchall()

# Campaigns
campaigns = cur.execute("SELECT campaign, COUNT(*) as c FROM prospects WHERE campaign IS NOT NULL GROUP BY campaign").fetchall()

# Response rate
responded = cur.execute("SELECT COUNT(*) FROM prospects WHERE signal_type IS NOT NULL AND signal_type != 'none'").fetchone()[0]

print('=== OUTREACH PIPELINE LIVE STATUS ===')
print()
print('TOTALS: {} prospects | {} sent | {} unsent | {} stale (>7d no reply)'.format(total, sent, unsent, stale))
if sent > 0:
    print('RESPONSE RATE: {}/{} = {:.1f}%'.format(responded, sent, responded/sent*100))
print()
print('SIGNALS:')
for s in signals:
    print('  {}: {}'.format(s[0], s[1]))
if not signals:
    print('  (none)')
print()
print('LANES:')
for l in lanes:
    print('  {}: {}'.format(l[0], l[1]))
print()
print('CAMPAIGNS:')
for c in campaigns:
    print('  {}: {}'.format(c[0] if c[0] else '(none)', c[1]))
print()
print('HOT UNCONTACTED (score>=75):')
for h in hot:
    print('  {} | score={} | {} | {}'.format(h[0], h[1], h[2], h[3]))
if not hot:
    print('  (none remaining)')
print()
print('RECENT ACTIVITY:')
for r in recent:
    ts = r[2] if r[2] else '?'
    det = str(r[1])[:90] if r[1] else ''
    print('  [{}] {}: {}'.format(ts, r[0], det))
if not recent:
    print('  (none)')

db.close()
