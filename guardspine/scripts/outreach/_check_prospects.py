import sqlite3, os

db = os.path.expanduser("~/.claude/outreach/outreach.db")
conn = sqlite3.connect(db)
c = conn.cursor()

# Task 2: Investor targets
investors = [
    "Caleb Sima", "Guy Podjarny", "David B. Cross", "Frederic Kerrest",
    "Mohamed Nanabhay", "Sam Kassoumeh", "Jon Oberheide", "Solomon Hykes",
    "Jake Bernardes", "Andrew Peterson"
]

# Task 3: Buyer targets
buyers = [
    "Adam Hamm", "Akiko Amakawa", "Alemayehu Molla", "Amit Gupta",
    "Amy Friend", "Bea von Seckendorff", "Berta Rodriguez-Hervas",
    "Bonnie Boles", "Brian Cincera", "Carolina Garcia Rizo"
]

print("=" * 60)
print("TASK 2: INVESTOR PROSPECTS")
print("=" * 60)
for name in investors:
    # Use LIKE for partial matching
    c.execute("SELECT id, name, company, lane, channel, message_sent_at, signal_type, archetype, investor_score, linkedin_url, email FROM prospects WHERE name LIKE ?", (f"%{name}%",))
    rows = c.fetchall()
    if rows:
        for r in rows:
            status = "SENT" if r[5] else "UNSENT"
            print(f"  [DB:{r[0]}] {r[1]} @ {r[2]} | lane={r[3]} ch={r[4]} | {status} | signal={r[6]} | arch={r[7]} score={r[8]}")
            print(f"    LinkedIn: {r[9]}")
            print(f"    Email: {r[10]}")
    else:
        print(f"  [NOT IN DB] {name}")

print()
print("=" * 60)
print("TASK 3: BUYER PROSPECTS")
print("=" * 60)
for name in buyers:
    c.execute("SELECT id, name, company, lane, channel, message_sent_at, signal_type, linkedin_url, email FROM prospects WHERE name LIKE ?", (f"%{name}%",))
    rows = c.fetchall()
    if rows:
        for r in rows:
            status = "SENT" if r[5] else "UNSENT"
            print(f"  [DB:{r[0]}] {r[1]} @ {r[2]} | lane={r[3]} ch={r[4]} | {status} | signal={r[5]} | LI: {r[7]} | email: {r[8]}")
    else:
        print(f"  [NOT IN DB] {name}")

print()
print("=" * 60)
print("PROOF POINTS (green signals)")
print("=" * 60)
c.execute("SELECT name, company, lane, signal_type, signal_notes FROM prospects WHERE signal_type = 'green' ORDER BY name")
for r in c.fetchall():
    print(f"  {r[0]} ({r[1]}) - {r[2]} | {r[4][:80] if r[4] else 'no notes'}")

print()
print("=" * 60)
print("EXISTING VELOCITY/BUILDER PROSPECTS (for task 5 baseline)")
print("=" * 60)
c.execute("SELECT COUNT(*) FROM prospects WHERE lane = 'builder'")
print(f"  Builder lane total: {c.fetchone()[0]}")
c.execute("SELECT campaign, COUNT(*) FROM prospects WHERE campaign IS NOT NULL GROUP BY campaign ORDER BY COUNT(*) DESC LIMIT 10")
print("  Campaigns:")
for r in c.fetchall():
    print(f"    {r[0]}: {r[1]}")

conn.close()
