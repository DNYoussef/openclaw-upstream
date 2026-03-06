import sqlite3, os

db = os.path.expanduser("~/.claude/outreach/outreach.db")
conn = sqlite3.connect(db)
c = conn.cursor()

names = [
    "Hameed Raza",
    "Matthew Scholz",
    "Johann Sutherland",
    "Josiah Nicely",
    "Anthony Arranaga",
    "Justin Somaini",
    "Fletcher Hillier",
    "Sergi Herrero",
    "Brandon Bichler",
    "Ramya Rajendran",
    "Vanessa",  # VENCO GROUP
    "Pascale",  # VENCO GROUP
    "Matt Dziedzic",
    "Jefferson Liu",
    "Nir Polak",
    "Ely Kahn",
    "Andreas Freund",
    "Erick Antezana",
    "Faisal ALFadialy",
    "Bandar Alqurashi",
    "Aaron Bennett",
]

print("DB MATCHES:")
print("=" * 60)
for name in names:
    c.execute("SELECT id, name, title, company, lane, channel, message_sent_at, signal_type, message_draft FROM prospects WHERE name LIKE ?", (f"%{name}%",))
    rows = c.fetchall()
    if rows:
        for r in rows:
            sent = "SENT" if r[6] else "UNSENT"
            print(f"  [IN DB] {r[1]} | {r[2]} @ {r[3]}")
            print(f"    lane={r[4]} ch={r[5]} | {sent} | signal={r[7]}")
            print(f"    draft={'YES' if r[8] else 'NO'}")
    else:
        print(f"  [NOT IN DB] {name}")
    print()

conn.close()
