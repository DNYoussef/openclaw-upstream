import sqlite3

db = sqlite3.connect('C:/Users/17175/.claude/outreach/outreach.db')
cur = db.cursor()

print('=== 1. ALL SIGNALS (responded prospects) ===')
print()
rows = cur.execute("""
    SELECT name, title, company, signal_type, signal_notes, channel, message_sent_at, lane, investor_score, next_action, email
    FROM prospects
    WHERE signal_type IS NOT NULL AND signal_type != 'none'
    ORDER BY signal_type, message_sent_at DESC
""").fetchall()
for r in rows:
    print('  [{signal}] {name} | {title} @ {company}'.format(
        signal=r[3].upper(), name=r[0], title=r[1] or '?', company=r[2] or '?'))
    print('    Lane: {} | Score: {} | Channel: {} | Sent: {}'.format(r[7], r[8], r[5], r[6]))
    print('    Notes: {}'.format((r[4] or '')[:120]))
    print('    Next: {}'.format(r[9] or '(none set)'))
    print('    Email: {}'.format(r[10] or '(none)'))
    print()

print()
print('=== 2. STALE PROSPECTS (sent >7d, no signal) ===')
print()
stale = cur.execute("""
    SELECT name, title, company, message_sent_at, channel, lane, investor_score, email, next_action, hook_text
    FROM prospects
    WHERE message_sent_at IS NOT NULL
    AND (signal_type IS NULL OR signal_type = 'none')
    AND julianday('now') - julianday(message_sent_at) > 7
    ORDER BY investor_score DESC
""").fetchall()
for r in stale:
    days = 'unknown'
    if r[3]:
        d = cur.execute("SELECT CAST(julianday('now') - julianday(?) AS INTEGER)", (r[3],)).fetchone()[0]
        days = str(d) + 'd ago'
    print('  {name} | {title} @ {company} | score={score} | {lane} | sent {days} via {ch}'.format(
        name=r[0], title=r[1] or '?', company=r[2] or '?',
        score=r[6], lane=r[5], days=days, ch=r[4] or '?'))
    print('    Email: {} | Next: {}'.format(r[7] or '(none)', r[8] or '(none set)'))
    if r[9]:
        print('    Hook: {}'.format(r[9][:100]))
    print()

print()
print('=== 3. HOT UNCONTACTED (score >= 75, full details) ===')
print()
hot = cur.execute("""
    SELECT name, title, company, lane, investor_score, archetype, target_segment,
           email, linkedin_url, notes, research_notes, intro_paths, next_action
    FROM prospects
    WHERE message_sent_at IS NULL AND investor_score >= 75
    ORDER BY investor_score DESC LIMIT 15
""").fetchall()
for r in hot:
    print('  {name} | {title} @ {company}'.format(name=r[0], title=r[1] or '?', company=r[2] or '?'))
    print('    Score: {} | Lane: {} | Archetype: {} | Segment: {}'.format(r[4], r[3], r[5] or '?', r[6] or '?'))
    print('    Email: {} | LinkedIn: {}'.format(r[7] or '(none)', r[8] or '(none)'))
    if r[9]:
        print('    Notes: {}'.format(str(r[9])[:150]))
    if r[10]:
        print('    Research: {}'.format(str(r[10])[:150]))
    if r[11]:
        print('    Intro paths: {}'.format(str(r[11])[:120]))
    print('    Next: {}'.format(r[12] or '(none set)'))
    print()

print()
print('=== 4. WEEKLY METRICS HISTORY ===')
print()
try:
    metrics = cur.execute("""
        SELECT week_start, messages_sent, responses, green_signals, yellow_signals, red_signals
        FROM weekly_metrics ORDER BY week_start DESC LIMIT 6
    """).fetchall()
    for m in metrics:
        print('  Week {}: sent={} resp={} green={} yellow={} red={}'.format(
            m[0], m[1], m[2], m[3], m[4], m[5]))
except:
    print('  (no weekly_metrics table)')

print()
print('=== 5. BOUNCED PROSPECTS ===')
print()
bounced = cur.execute("""
    SELECT name, company, email, channel, signal_notes, next_action
    FROM prospects WHERE signal_type = 'bounced'
""").fetchall()
for b in bounced:
    print('  {} @ {} | email: {} | ch: {}'.format(b[0], b[1] or '?', b[2] or '?', b[3] or '?'))
    print('    Notes: {} | Next: {}'.format((b[4] or '')[:100], b[5] or '(none)'))
    print()

db.close()
