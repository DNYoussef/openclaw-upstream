import sqlite3, os

db = os.path.expanduser("~/.claude/outreach/outreach.db")
conn = sqlite3.connect(db)
c = conn.cursor()

total = c.execute("SELECT COUNT(*) FROM prospects").fetchone()[0]
sent = c.execute("SELECT COUNT(*) FROM prospects WHERE message_sent_at IS NOT NULL").fetchone()[0]
uncontacted = c.execute("SELECT COUNT(*) FROM prospects WHERE message_sent_at IS NULL").fetchone()[0]

signals = dict(c.execute(
    "SELECT signal_type, COUNT(*) FROM prospects WHERE signal_type IS NOT NULL AND signal_type != 'none' GROUP BY signal_type"
).fetchall())

lanes = c.execute(
    "SELECT lane, COUNT(*), SUM(CASE WHEN message_sent_at IS NOT NULL THEN 1 ELSE 0 END) FROM prospects GROUP BY lane"
).fetchall()

responded = c.execute(
    "SELECT name, company, lane, signal_type FROM prospects WHERE signal_type IN ('green','positive','yellow','neutral','replied') ORDER BY signal_type"
).fetchall()

recent = c.execute(
    "SELECT action, details, timestamp FROM activity_log ORDER BY timestamp DESC LIMIT 8"
).fetchall()

# This week's sends
weekly = c.execute(
    "SELECT COUNT(*) FROM prospects WHERE message_sent_at >= date('now', '-7 days')"
).fetchone()[0]

print(f"TOTAL: {total} | SENT: {sent} | UNCONTACTED: {uncontacted} | THIS WEEK: {weekly}")
print(f"SIGNALS: {signals}")
print()
print("BY LANE:")
for lane, count, s in lanes:
    print(f"  {lane}: {count} total, {int(s)} sent")
print()
print("RESPONDED:")
if responded:
    for name, company, lane, sig in responded[:15]:
        print(f"  [{sig}] {name} ({company}) - {lane}")
else:
    print("  (none)")
print()
print("RECENT ACTIVITY:")
for action, detail, ts in recent:
    print(f"  [{ts}] {action}: {detail[:100]}")

conn.close()
