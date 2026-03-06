"""Add new LinkedIn connections to outreach DB - Feb 24, 2026."""
import sqlite3
from datetime import datetime

db = sqlite3.connect('C:/Users/17175/.claude/outreach/outreach.db')
cur = db.cursor()
now = datetime.now().isoformat()

# Get column list for prospects table
cols = [r[1] for r in cur.execute("PRAGMA table_info(prospects)").fetchall()]
print('Columns:', cols)

# Tier 1 - CISO/Security/Investor
tier1 = [
    ('Jake Bernardes', 'Field CISO at Anecdotes; Investor at Squared Circle Ventures', 'Anecdotes', 'buyer', 'ciso', 'linkedin_dm', 85),
    ('Ash Hunt', 'VP EMEA Strategy at Cyera; Ex-FTSE 250 Global CISO; Board & VC Advisor', 'Cyera', 'buyer', 'ciso', 'linkedin_dm', 82),
    ('Lavy Stokhamer', 'MD, Global Head of Cybersecurity & Financial Crime Technology', 'Standard Chartered', 'buyer', 'ciso', 'linkedin_dm', 78),
    ('Michael Sinno', 'Director, Detection and Response at Google', 'Google', 'buyer', 'ciso', 'linkedin_dm', 76),
    ('Zeshan Saghir', 'Senior Audit Group Manager, TD Securities Compliance', 'TD Securities', 'buyer', 'ciso', 'linkedin_dm', 77),
    ('Kenneth Jones', 'Governance & Assurance, Automated Decision Systems, GRC Strategy, Founder Zerisk', 'Zerisk', 'buyer', 'ciso', 'linkedin_dm', 75),
    ('Anand Shah', 'Privacy & Confidentiality Program Officer at KPMG', 'KPMG', 'buyer', 'ciso', 'linkedin_dm', 74),
    ('Nigel Gooding', 'Chair DPAS, Data Protection Cyber Technology & Information Rights Law', 'DPAS', 'buyer', 'ciso', 'linkedin_dm', 73),
    ('Jerry Perullo', None, None, None, None, None, None),  # already in DB
    ('Dawn Cappelli', None, None, None, None, None, None),  # already in DB
    ('Karl Mattson', None, None, None, None, None, None),   # already in DB
    ('Nick Galbreath', None, None, None, None, None, None), # already in DB
]

# Tier 2 - AI/Engineering leadership
tier2 = [
    ('Steve Messina', 'Founder macleodlabs.ai, ex AWS CTO/IBM Tech Leader', 'macleodlabs.ai', 'builder', 'developer', 'linkedin_dm', 72),
    ('Tim Wedande', 'SVP, Field CTO at Saviynt', 'Saviynt', 'buyer', 'ciso', 'linkedin_dm', 71),
    ('Leo Cullen', 'Enterprise AI: Governance, Interoperability and Accountability', None, 'buyer', 'ciso', 'linkedin_dm', 70),
    ('Andreas Freund', 'Managing Principal, Zero-Knowledge Tech, Expert Witness, Web3, GenAI', 'Exp Technology Consultants', 'builder', 'developer', 'linkedin_dm', 68),
    ('Erick Antezana', 'Senior Data Governance and Strategy Officer', None, 'buyer', 'ciso', 'linkedin_dm', 70),
    ('Aaron Bennett', 'Product strategy and innovation, partnerships in platform, technology, cybersecurity', None, 'buyer', 'ciso', 'linkedin_dm', 67),
    ('Richard Schaefer', 'CTO Lunar Analytics, Retired Federal Health Clinical AI Architect and Chief AI Officer', 'Lunar Analytics', 'buyer', 'ciso', 'linkedin_dm', 72),
    ('Christos Varsakelis', 'Associate Director AI/ML at J&J Janssen Pharmaceuticals', 'Johnson & Johnson', 'buyer', 'ciso', 'linkedin_dm', 70),
    ('Varun Chhibber', 'Staff VP Engineering at Elevance Health, HBS Alum', 'Elevance Health', 'builder', 'developer', 'linkedin_dm', 69),
    ('Lucas Walter', 'CTO at Calico AI', 'Calico AI', 'builder', 'developer', 'linkedin_dm', 65),
    ('Dan McInerney', 'AI threat researcher, ML engineer, Agent engineer', None, 'builder', 'developer', 'linkedin_dm', 66),
    ('Iannis Drakos', 'Enterprise AI, Agentic AI, FAIR data, Board Member', None, 'buyer', 'ciso', 'linkedin_dm', 68),
    ('Craig Schmitz', 'Partner at Goodwin Procter LLP', 'Goodwin Procter', 'connector', None, 'linkedin_dm', 60),
    ('Matt Schmid', 'AI-First Product Marketing Leader, AI Council Founder', None, 'builder', 'developer', 'linkedin_dm', 64),
    ('Travis Lee', 'AI & Autonomous Systems Executive, Founder HumanSovereigntyAI', 'HumanSovereigntyAI', 'builder', 'developer', 'linkedin_dm', 63),
    ('Casey Fleming', 'CEO, Strategic Risk, National Security, Counterintelligence', None, 'buyer', 'ciso', 'linkedin_dm', 66),
    ('Tarek Ahmad', 'Executive, Cyber Security Risk Management', None, 'buyer', 'ciso', 'linkedin_dm', 65),
    ('Doug Hubbard', 'Measure What Matters, Decision Analysis', None, 'connector', None, 'linkedin_dm', 62),
    ('Andrew Penner', 'VP Software Engineering at TriZetto', 'TriZetto', 'builder', 'developer', 'linkedin_dm', 60),
    ('Berta Rodriguez-Hervas', None, None, None, None, None, None),  # already in DB
]

added = 0
for prospects in [tier1, tier2]:
    for p in prospects:
        name, title, company, lane, segment, channel, score = p
        if title is None:  # already in DB
            continue
        # Check if already exists
        existing = cur.execute("SELECT id FROM prospects WHERE name = ?", (name,)).fetchone()
        if existing:
            print('SKIP (exists): {}'.format(name))
            continue
        cur.execute("""INSERT INTO prospects (name, title, company, lane, target_segment, channel, investor_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, title, company, lane, segment, channel, score,
             'Feb 24: Added from LinkedIn connections. 1st-degree.'))
        added += 1
        print('ADDED: {} ({} @ {}) lane={} score={}'.format(name, title[:40] if title else '', company or '?', lane, score))

# Log
cur.execute("""INSERT INTO activity_log (action, details, timestamp)
    VALUES ('bulk_import', ?, ?)""",
    ('Feb 24: Added {} new prospects from LinkedIn connections (Tier 1 + Tier 2)'.format(added), now))

db.commit()
print()
print('Total added: {}'.format(added))
db.close()
