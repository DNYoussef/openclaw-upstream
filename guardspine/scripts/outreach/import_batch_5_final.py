#!/usr/bin/env python3
"""Import final Batch 5 to reach 200 prospects."""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.claude/outreach/outreach.db")
CAMPAIGN = "landing_page_200_feb26"
NOW = datetime.now().isoformat()

BATCH_5_DEVS = [
    {"name": "Liran Tal", "title": "Developer Advocate, AI Agent Security", "company": "Snyk", "industry": "devsecops", "email": "liran.tal@gmail.com", "source": "github_api", "notes": "GitHub Star. Node.js secure coding. Hacking AI Agents. 2.4K followers."},
    {"name": "Doug Tangren", "title": "Developer", "company": "MongoDB", "industry": "tech", "email": "d.tangren@gmail.com", "source": "github_api", "notes": "Creator of action-gh-release (5.4K stars). 953 followers."},
    {"name": "James Ives", "title": "Lead Software Engineer", "company": "Blizzard", "industry": "gaming", "email": "", "source": "github_api", "notes": "Creator of github-pages-deploy-action (4.5K stars). Design systems."},
    {"name": "Shivam Mathur", "title": "Developer", "company": "Codementor", "industry": "devtools", "email": "contact@shivammathur.com", "source": "github_api", "notes": "Creator of setup-php (3.2K stars). 1.1K followers."},
    {"name": "Jason Lengstorf", "title": "Creator / Developer", "company": "CodeTV", "industry": "devtools", "email": "jason@codetv.dev", "source": "github_api", "notes": "Web Dev Challenge creator. 4.5K followers. 20yr web dev. High amplification."},
]

BATCH_5_CISOS = [
    # HealthSec summit speakers -- healthcare CISOs
    {"name": "Nick Sturgeon", "title": "VP CISO", "company": "Community Health Network", "industry": "healthcare", "email": "", "source": "healthsec_2026", "notes": "HealthSec 2026 speaker. Healthcare HIPAA compliance."},
    {"name": "Anahi Santiago", "title": "CISO", "company": "Christiana Care Health System", "industry": "healthcare", "email": "", "source": "healthsec_2026", "notes": "HealthSec 2026 speaker. Major health system in Delaware."},
    {"name": "Monique St John", "title": "VP CISO", "company": "Childrens Hospital of Philadelphia", "industry": "healthcare", "email": "", "source": "healthsec_2026", "notes": "HealthSec 2026 speaker. Pediatric healthcare. Sensitive data governance."},
    {"name": "John Frushour", "title": "VP and CISO", "company": "New York-Presbyterian Hospital", "industry": "healthcare", "email": "", "source": "healthsec_2026", "notes": "HealthSec 2026 speaker. Top-ranked hospital. HIPAA at scale."},
    {"name": "Salman Khan", "title": "CISO", "company": "Harris Health System", "industry": "healthcare", "email": "", "source": "healthsec_2026", "notes": "HealthSec 2026 speaker. Public health system. HIPAA + government compliance."},
    # Finance CISOs from Gracker directory (not yet imported)
    {"name": "James Shira", "title": "CIO & CISO", "company": "PwC", "industry": "consulting", "email": "", "source": "gracker_directory", "notes": "PwC CIO+CISO. Dual role. Audit firm -- deeply understands evidence requirements."},
    {"name": "Joe Martinez", "title": "Global CISO", "company": "Aon", "industry": "insurance", "email": "", "source": "gracker_directory", "notes": "Global insurance/risk company. Multi-jurisdiction compliance."},
    {"name": "Bala Sathiamurthy", "title": "CISO", "company": "Atlassian", "industry": "tech", "email": "", "source": "gracker_directory", "notes": "Atlassian CISO. Jira/Bitbucket -- code governance from the platform side."},
    {"name": "David Bradbury", "title": "Chief Security Officer", "company": "Okta", "industry": "identity", "email": "", "source": "gracker_directory", "notes": "Okta CSO. Identity + access management. Post-breach transformation."},
    {"name": "Tim Brown", "title": "CISO", "company": "SolarWinds", "industry": "tech", "email": "", "source": "gracker_directory", "notes": "SolarWinds CISO. Post-breach transformation. Knows supply chain security deeply."},
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT LOWER(name) FROM prospects")
    existing = set(r[0] for r in cur.fetchall())

    inserted = 0
    skipped = 0

    for p in BATCH_5_DEVS:
        if p["name"].lower() in existing:
            print(f"  SKIP: {p['name']}")
            skipped += 1
            continue
        cur.execute(
            """INSERT INTO prospects (name, title, company, industry, email, source, notes, created_at, campaign, target_segment, batch_number, lane)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'developer', 5, 'builder')""",
            (p["name"], p["title"], p["company"], p["industry"], p["email"], p["source"], p["notes"], NOW, CAMPAIGN)
        )
        inserted += 1

    for p in BATCH_5_CISOS:
        if p["name"].lower() in existing:
            print(f"  SKIP: {p['name']}")
            skipped += 1
            continue
        cur.execute(
            """INSERT INTO prospects (name, title, company, industry, email, source, notes, created_at, campaign, target_segment, batch_number, lane)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ciso', 5, 'buyer')""",
            (p["name"], p["title"], p["company"], p["industry"], p["email"], p["source"], p["notes"], NOW, CAMPAIGN)
        )
        inserted += 1

    conn.commit()

    cur.execute("SELECT target_segment, COUNT(*) FROM prospects WHERE campaign = ? GROUP BY target_segment", (CAMPAIGN,))
    print(f"\nCampaign totals:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")
    cur.execute("SELECT COUNT(*) FROM prospects WHERE campaign = ?", (CAMPAIGN,))
    total = cur.fetchone()[0]
    print(f"  TOTAL: {total}/200")
    print(f"\nInserted: {inserted}, Skipped: {skipped}")

    if total >= 200:
        print("\n=== TARGET REACHED: 200 PROSPECTS ===")
    else:
        print(f"\n  Still need: {200 - total} more")

    conn.close()


if __name__ == "__main__":
    main()
