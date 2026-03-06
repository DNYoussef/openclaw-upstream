import sqlite3, os

db = os.path.expanduser("~/.claude/outreach/outreach.db")
conn = sqlite3.connect(db)
c = conn.cursor()

# Get unsent buyer prospects not in the original batch, with LinkedIn URLs
c.execute("""
    SELECT id, name, title, company, linkedin_url, channel, notes, research_notes
    FROM prospects
    WHERE lane = 'buyer'
      AND message_sent_at IS NULL
      AND (channel IS NULL OR channel NOT IN ('bounced', 'removed_wrong_role'))
      AND linkedin_url IS NOT NULL
      AND name NOT IN (
        'Adam Hamm', 'Akiko Amakawa', 'Alemayehu Molla', 'Amit Gupta',
        'Amy Friend', 'Bea von Seckendorff', 'Berta Rodriguez-Hervas',
        'Bonnie Boles', 'Brian Cincera', 'Carolina Garcia Rizo'
      )
    ORDER BY investor_score DESC NULLS LAST
    LIMIT 10
""")
rows = c.fetchall()
print(f"REPLACEMENT BUYER CANDIDATES ({len(rows)} found):")
print("=" * 60)
for r in rows:
    print(f"  [{r[0][:8]}] {r[1]}")
    print(f"    Title: {r[2]}")
    print(f"    Company: {r[3]}")
    print(f"    LinkedIn: {r[4]}")
    print(f"    Channel: {r[5]}")
    print(f"    Notes: {(r[6] or '')[:100]}")
    print()

conn.close()
