#!/usr/bin/env python3
"""Import LEAD_ANGEL_EXTENDED prospects into campaign DB."""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.claude/outreach/outreach.db")
CAMPAIGN = "landing_page_200_feb26"
NOW = datetime.now().isoformat()

PROSPECTS = [
    # CISOs (archetype A - security leaders)
    {"name": "Karl Mattson", "title": "CISO", "company": "Noname Security", "industry": "cybersecurity", "segment": "ciso", "lane": "buyer"},
    {"name": "John Brennan", "title": "VP Security", "company": "", "industry": "cybersecurity", "segment": "ciso", "lane": "buyer"},
    {"name": "Mandy Andress", "title": "CISO", "company": "Elastic", "industry": "tech", "segment": "ciso", "lane": "buyer"},
    {"name": "Al Ghous", "title": "CISO", "company": "", "industry": "cybersecurity", "segment": "ciso", "lane": "buyer"},
    {"name": "Kathy Wang", "title": "CISO", "company": "", "industry": "cybersecurity", "segment": "ciso", "lane": "buyer"},
    {"name": "Justin Somaini", "title": "CISO", "company": "Unity", "industry": "gaming", "segment": "ciso", "lane": "buyer"},
    {"name": "Alex Tosheff", "title": "VP CISO", "company": "Salesforce", "industry": "tech", "segment": "ciso", "lane": "buyer"},
    {"name": "Neil Daswani", "title": "Co-director Stanford AIS; ex-Snap CISO", "company": "Stanford", "industry": "academia", "segment": "ciso", "lane": "buyer"},
    {"name": "Jim Routh", "title": "Former CISO", "company": "MassMutual/Aetna/CVS", "industry": "insurance", "segment": "ciso", "lane": "buyer"},
    {"name": "Jerry Perullo", "title": "CISO", "company": "ICE/Intercontinental Exchange", "industry": "finance", "segment": "ciso", "lane": "buyer"},
    {"name": "Michael Weider", "title": "Security + DevTools", "company": "", "industry": "cybersecurity", "segment": "ciso", "lane": "buyer"},
    {"name": "Barmak Meftah", "title": "Co-Founder/CEO Ballistic Ventures; ex-AT&T CISO", "company": "Ballistic Ventures", "industry": "vc", "segment": "ciso", "lane": "investor"},
    {"name": "Andy Ellis", "title": "Operating Partner; ex-CSO Akamai", "company": "YL Ventures", "industry": "vc", "segment": "ciso", "lane": "investor"},

    # Developers / DevTools (archetype B)
    {"name": "Nat Friedman", "title": "ex-GitHub CEO", "company": "AI Fund", "industry": "tech", "segment": "developer", "lane": "builder"},
    {"name": "Ben Mann", "title": "ex-Anthropic", "company": "Anthropic (former)", "industry": "ai", "segment": "developer", "lane": "builder"},
    {"name": "Tom Drummond", "title": "ex-Docker", "company": "Docker (former)", "industry": "devtools", "segment": "developer", "lane": "builder"},
    {"name": "Stephen Blum", "title": "PubNub Founder", "company": "PubNub", "industry": "devtools", "segment": "developer", "lane": "builder"},
    {"name": "Christina Cacioppo", "title": "CEO", "company": "Vanta", "industry": "compliance", "segment": "developer", "lane": "builder"},
    {"name": "Bret Taylor", "title": "ex-Salesforce Co-CEO", "company": "Sierra AI", "industry": "ai", "segment": "developer", "lane": "builder"},

    # Investors/Connectors (classified by primary audience fit)
    {"name": "Joel Fulton", "title": "Co-founder", "company": "Lucidum", "industry": "cybersecurity", "segment": "ciso", "lane": "investor"},
    {"name": "Oren Yunger", "title": "GGV Capital, ex-CISO", "company": "GGV Capital", "industry": "vc", "segment": "ciso", "lane": "investor"},
    {"name": "Jay Leek", "title": "Managing Partner", "company": "SYN Ventures", "industry": "vc", "segment": "ciso", "lane": "investor"},
    {"name": "Chenxi Wang", "title": "Founder", "company": "Rain Capital", "industry": "vc", "segment": "ciso", "lane": "investor"},
    {"name": "Ted Schlein", "title": "Partner", "company": "Ballistic Ventures", "industry": "vc", "segment": "ciso", "lane": "investor"},
    {"name": "Nicole Perlroth", "title": "Cybersecurity Journalist/Author", "company": "Independent", "industry": "media", "segment": "ciso", "lane": "connector"},
    {"name": "Joseph Ruscio", "title": "Partner", "company": "Heavybit", "industry": "vc", "segment": "developer", "lane": "investor"},
    {"name": "Dana Oshiro", "title": "Partner", "company": "Heavybit", "industry": "vc", "segment": "developer", "lane": "investor"},
    {"name": "Jacob Jofe", "title": "DevTools Investor", "company": "", "industry": "vc", "segment": "developer", "lane": "investor"},
    {"name": "Marius Luther", "title": "EU Regulatory Expert", "company": "", "industry": "regulatory", "segment": "ciso", "lane": "connector"},
    {"name": "Elad Gil", "title": "Angel Investor", "company": "Color Health", "industry": "vc", "segment": "developer", "lane": "investor"},
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check existing names for dedup
    cur.execute("SELECT LOWER(name) FROM prospects")
    existing = set(r[0] for r in cur.fetchall())

    inserted = 0
    skipped = 0
    for p in PROSPECTS:
        if p["name"].lower() in existing:
            print(f"  SKIP (exists): {p['name']}")
            skipped += 1
            continue
        cur.execute(
            """INSERT INTO prospects (name, title, company, industry, lane, source, created_at, campaign, target_segment)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (p["name"], p["title"], p["company"], p["industry"], p["lane"],
             "lead_angel_extended", NOW, CAMPAIGN, p["segment"])
        )
        inserted += 1

    conn.commit()

    # Summary
    cur.execute("SELECT target_segment, COUNT(*) FROM prospects WHERE campaign = ? GROUP BY target_segment", (CAMPAIGN,))
    print(f"\nCampaign totals:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")
    cur.execute("SELECT COUNT(*) FROM prospects WHERE campaign = ?", (CAMPAIGN,))
    print(f"  TOTAL: {cur.fetchone()[0]}/200")
    print(f"\nInserted: {inserted}, Skipped: {skipped}")
    conn.close()

if __name__ == "__main__":
    main()
