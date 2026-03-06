import sqlite3, os
from datetime import datetime

db = os.path.expanduser("~/.claude/outreach/outreach.db")
conn = sqlite3.connect(db)
c = conn.cursor()
now = datetime.now().isoformat()

# 1. Fix Justin Somaini: buyer -> investor, add score
c.execute("""UPDATE prospects SET lane = 'investor', investor_score = 92,
    channel = 'linkedin_dm',
    notes = 'YL Ventures Partner ($800M AUM, cybersecurity-focused). 5x CISO (Symantec, Yahoo, SAP, Unity, Box). Advises Cycode, Valence Security, Qualys, Palo Alto Networks. Latest investment: Minimus (Apr 2025). HIGHEST PRIORITY -- accepted connection Feb 25.'
    WHERE name LIKE '%Justin Somaini%'""")
print(f"Updated Justin Somaini: {c.rowcount} rows")

# 2. Update Erick Antezana
c.execute("""UPDATE prospects SET
    company = 'Bayer CropScience',
    research_notes = 'Senior Data Governance at Bayer CropScience (Belgium). PhD Bioinformatics. Semantic tech + ontology + MDM expertise. Governance is literally his title. Connected Feb 25.'
    WHERE name LIKE '%Erick Antezana%'""")
print(f"Updated Erick Antezana: {c.rowcount} rows")

# 3. Update Andreas Freund
c.execute("""UPDATE prospects SET
    research_notes = 'ZK proofs + GenAI intersection. Could advise on cryptographic evidence bundle architecture. Expert witness experience. Managing Principal Exp Technology Consultants. Connected Feb 24.'
    WHERE name LIKE '%Andreas Freund%'""")
print(f"Updated Andreas Freund: {c.rowcount} rows")

# 4. Add new prospects
new_prospects = [
    {
        "name": "Nir Polak",
        "title": "Security Entrepreneur, Investor, Board Member",
        "company": "Exabeam / SignalFire",
        "lane": "investor",
        "channel": "linkedin_dm",
        "investor_score": 90,
        "archetype": "A/B",
        "linkedin_url": "https://www.linkedin.com/in/nir-polak-1564934",
        "notes": "Co-founder/Chairman Exabeam ($2.4B SIEM). VP at SignalFire. YL Ventures Advisory Board (same firm as Somaini). Founding Investor Clutch Security. Portfolio: Protect AI, runZero, Dig Security (acq Palo Alto). 18yr infosec. Connected Feb 24.",
    },
    {
        "name": "Johann Sutherland",
        "title": "Senior Product Manager",
        "company": "Snyk",
        "lane": "buyer",
        "channel": "linkedin_dm",
        "investor_score": 82,
        "notes": "Senior PM at Snyk ($343M ARR developer security). Adjacent/complementary to GuardSpine. Integration partner opportunity. Connected Feb 25.",
        "linkedin_url": None,
    },
    {
        "name": "Sergi Herrero",
        "title": "CEO",
        "company": "Mangopay",
        "lane": "buyer",
        "channel": "linkedin_dm",
        "investor_score": 75,
        "notes": "CEO Mangopay (Advent-backed, EUR 100B+ processed). Ex-Meta Global Payments, ex-Square, ex-VEON co-CEO. DORA/PCI DSS compliance use case. Connected Feb 24.",
        "linkedin_url": None,
    },
    {
        "name": "Anthony Arranaga",
        "title": "Sr. Manager, Services Training",
        "company": "Intuitive",
        "lane": "buyer",
        "channel": "linkedin_dm",
        "investor_score": 60,
        "notes": "Intuitive (da Vinci surgical robots). FDA 21 CFR Part 11 / IEC 62304 use case. 15yr surgical robotics. Connected Feb 25.",
        "linkedin_url": None,
    },
    {
        "name": "Jefferson Liu",
        "title": "Enterprise Machine Learning Platforms, AI Delivery & Execution",
        "company": None,
        "lane": "builder",
        "channel": "linkedin_dm",
        "investor_score": 65,
        "notes": "Enterprise ML platform builder. Governance of ML model outputs and AI-generated code. Need to learn current company. Connected Feb 24.",
        "linkedin_url": None,
    },
    {
        "name": "Fletcher Hillier",
        "title": "Multi-Model Agnostic AI Systems & Agent Frameworks",
        "company": None,
        "lane": "builder",
        "channel": "linkedin_dm",
        "investor_score": 55,
        "notes": "Building multi-model AI agent systems. Potential user/evangelist for governance in agentic coding pipelines. Connected Feb 25.",
        "linkedin_url": None,
    },
    {
        "name": "Brandon Bichler",
        "title": "Partner",
        "company": "Elixirr",
        "lane": "connector",
        "channel": "linkedin_dm",
        "investor_score": 55,
        "notes": "Partner at Elixirr consulting. Manufacturing practice lead. Channel referral potential. Connected Feb 24.",
        "linkedin_url": None,
    },
    {
        "name": "Matthew Scholz",
        "title": "Founder and CEO",
        "company": "Oisin Biotechnologies",
        "lane": "connector",
        "channel": "linkedin_dm",
        "investor_score": 40,
        "notes": "CEO Oisin Biotechnologies. Network overlap via Carolina Garcia Rizo (board member). Biotech, not direct fit. Connected Feb 25.",
        "linkedin_url": None,
    },
]

for p in new_prospects:
    # Check if already exists
    c.execute("SELECT id FROM prospects WHERE name = ?", (p["name"],))
    if c.fetchone():
        print(f"  SKIP (exists): {p['name']}")
        continue
    c.execute("""INSERT INTO prospects (name, title, company, lane, channel, investor_score, archetype, linkedin_url, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (p["name"], p["title"], p["company"], p["lane"], p["channel"],
         p.get("investor_score"), p.get("archetype"), p.get("linkedin_url"),
         p["notes"], now))
    print(f"  ADDED: {p['name']} ({p['lane']})")

# 5. Log activity
c.execute("""INSERT INTO activity_log (timestamp, action, details) VALUES (?, ?, ?)""",
    (now, "db_update", "Triaged 20 new LinkedIn connections (Feb 24-25). Added 8 new prospects. Fixed Somaini lane buyer->investor. Updated Antezana (Bayer), Freund (ZK). 12 relevant, 8 skipped."))

conn.commit()
print("\nDone. All updates committed.")

# Verify
c.execute("SELECT name, lane, investor_score FROM prospects WHERE name LIKE '%Somaini%'")
print(f"\nVerify Somaini: {c.fetchone()}")
c.execute("SELECT COUNT(*) FROM prospects")
print(f"Total prospects: {c.fetchone()[0]}")

conn.close()
