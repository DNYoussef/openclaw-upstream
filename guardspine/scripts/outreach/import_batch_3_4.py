#!/usr/bin/env python3
"""Import Batch 3 (developers) and Batch 4 (CISOs) into campaign DB."""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.claude/outreach/outreach.db")
CAMPAIGN = "landing_page_200_feb26"
NOW = datetime.now().isoformat()

BATCH_3_DEVS = [
    # GitHub Actions ecosystem maintainers
    {"name": "Shohei Ueda", "title": "Developer", "company": "CyberAgent / Abema", "industry": "tech", "email": "", "source": "github_api", "notes": "Creator of actions-gh-pages (5.2K stars). GH Actions ecosystem."},
    {"name": "Doug Tangren", "title": "Developer", "company": "MongoDB", "industry": "tech", "email": "d.tangren@gmail.com", "source": "github_api", "notes": "Creator of action-gh-release (5.4K stars). 953 GitHub followers."},
    {"name": "James Ives", "title": "Lead Software Engineer", "company": "Blizzard", "industry": "gaming", "email": "", "source": "github_api", "notes": "Creator of github-pages-deploy-action (4.5K stars). Design systems lead."},
    {"name": "Shivam Mathur", "title": "Developer", "company": "Codementor", "industry": "devtools", "email": "contact@shivammathur.com", "source": "github_api", "notes": "Creator of setup-php (3.2K stars). 1.1K GitHub followers."},
    # DevSecOps leaders with public profiles
    {"name": "Liran Tal", "title": "Developer Advocate", "company": "Snyk", "industry": "devsecops", "email": "liran.tal@gmail.com", "source": "github_api", "notes": "GitHub Star. OpenJS Pathfinder Security Award. Node.js secure coding. 2.4K followers. Hacking AI Agents."},
    # Secureframe list -- dev-facing security leaders
    {"name": "Allan Friedman", "title": "SBOM Lead", "company": "CISA", "industry": "government", "email": "", "source": "secureframe_50", "notes": "SBOM pioneer at CISA. Direct SBOM+GuardSpine complementarity angle (Jacob Friedman connection)."},
    {"name": "Allison Miller", "title": "Security & Risk Executive", "company": "Independent Advisor", "industry": "fintech", "email": "", "source": "secureframe_50", "notes": "Ex-Reddit, Google, PayPal, Visa, BofA. Fraud prevention + product security."},
    # Gracker directory -- dev-leaning CISOs and security engineers
    {"name": "Josh Lemos", "title": "CISO", "company": "GitLab", "industry": "devtools", "email": "", "source": "gracker_directory", "notes": "CISO of GitLab. Deeply understands code governance from the platform side."},
    {"name": "Matt Hillary", "title": "CISO", "company": "Drata", "industry": "compliance", "email": "", "source": "gracker_directory", "notes": "CISO of Drata (compliance automation competitor). Knows the evidence gap."},
    {"name": "Jack Naglieri", "title": "Founder & CTO", "company": "Panther", "industry": "security", "email": "", "source": "gracker_directory", "notes": "Security detection-as-code. Builder + security intersection."},
    {"name": "Heather Adkins", "title": "Security Engineering", "company": "Google", "industry": "tech", "email": "", "source": "gracker_directory", "notes": "Google security engineering. Foundational security infrastructure."},
    {"name": "Wendy Nather", "title": "Senior Research Initiatives Director", "company": "1Password", "industry": "security", "email": "", "source": "gracker_directory", "notes": "Ex-Duo/Cisco. Research-focused security leader. High influence."},
    {"name": "Lesley Carhart", "title": "Director of Incident Response", "company": "Dragos", "industry": "ics_security", "email": "", "source": "gracker_directory", "notes": "ICS incident response. High-profile security voice."},
    {"name": "Anton Chuvakin", "title": "Security Advisor", "company": "Google Cloud", "industry": "tech", "email": "", "source": "gracker_directory", "notes": "Google Cloud security advisor. Ex-Gartner analyst. Huge blog following."},
    # BSides/conference speakers with dev angle
    {"name": "Maya Kaczorowski", "title": "Security Product Manager", "company": "Google", "industry": "tech", "email": "", "source": "bsides_2025", "notes": "BSidesSF 2025 speaker. Supply chain security at Google."},
    # More from Secureframe -- builder archetype
    {"name": "Eva Galperin", "title": "Director of Cybersecurity", "company": "EFF", "industry": "nonprofit", "email": "", "source": "secureframe_50", "notes": "EFF cybersecurity director. Privacy + open source advocate. High amplification."},
    {"name": "Runa Sandvik", "title": "Founder", "company": "Granitt", "industry": "security", "email": "", "source": "secureframe_50", "notes": "Security researcher. Founder of Granitt. High profile in security community."},
    {"name": "Tarah Wheeler", "title": "CEO", "company": "Red Queen Dynamics", "industry": "security", "email": "", "source": "secureframe_50", "notes": "CEO Red Queen Dynamics. Cyber policy expert. Author."},
    {"name": "Javvad Malik", "title": "Lead Security Awareness Advocate", "company": "KnowBe4", "industry": "security", "email": "", "source": "secureframe_50", "notes": "Security awareness leader. Blogger. High LinkedIn following."},
    {"name": "Camille Stewart Gloster", "title": "AI & Resilience Services Lead", "company": "CrowdStrike", "industry": "security", "email": "", "source": "secureframe_50", "notes": "AI + resilience at CrowdStrike. Ex-White House cyber policy."},
]

BATCH_4_CISOS = [
    # C100 + Gracker directory -- enterprise CISOs
    {"name": "Tim Held", "title": "EVP & CISO", "company": "U.S. Bank", "industry": "finance", "email": "", "source": "gracker_directory", "notes": "Major US bank. SOC2 + OCC regulatory requirements."},
    {"name": "Susan Koski", "title": "EVP & CISO", "company": "PNC Financial Services", "industry": "finance", "email": "", "source": "gracker_directory", "notes": "Top 10 US bank. Heavy regulatory compliance."},
    {"name": "Christopher Porter", "title": "SVP & CSO", "company": "Fannie Mae", "industry": "finance", "email": "", "source": "gracker_directory", "notes": "Government-sponsored enterprise. Federal audit requirements."},
    {"name": "Tim McKnight", "title": "EVP & CISO", "company": "UnitedHealth Group", "industry": "healthcare", "email": "", "source": "gracker_directory", "notes": "Largest US health insurer. HIPAA + AI governance at massive scale."},
    {"name": "Andrew Coyne", "title": "CISO", "company": "Mayo Clinic", "industry": "healthcare", "email": "", "source": "gracker_directory", "notes": "Premier academic medical center. Research AI + clinical data governance."},
    {"name": "Carrie Mills", "title": "CISO", "company": "Southwest Airlines", "industry": "aviation", "email": "", "source": "gracker_directory", "notes": "Major airline. Operational technology + compliance."},
    {"name": "Sebastian Lange", "title": "Global CISO", "company": "SAP", "industry": "tech", "email": "", "source": "gracker_directory", "notes": "SAP global CISO. Enterprise software security at scale."},
    {"name": "Harold Rivas", "title": "Global CISO", "company": "Trellix", "industry": "cybersecurity", "email": "", "source": "gracker_directory", "notes": "Security vendor CISO. Understands tooling landscape."},
    {"name": "Hemangini Thakkar", "title": "CISO", "company": "HSBC", "industry": "finance", "email": "", "source": "gracker_directory", "notes": "Major global bank. DORA + multi-jurisdiction compliance."},
    {"name": "Cezary Piekarski", "title": "Group CISO", "company": "Standard Chartered", "industry": "finance", "email": "", "source": "gracker_directory", "notes": "Global bank. DORA + APAC regulatory requirements."},
    {"name": "Christophe Gabioud", "title": "Group Chief Security Officer", "company": "AXA", "industry": "insurance", "email": "", "source": "gracker_directory", "notes": "Global insurer. DORA + EU AI Act compliance."},
    {"name": "Rich Baich", "title": "VP & CISO", "company": "AT&T", "industry": "telecom", "email": "", "source": "gracker_directory", "notes": "Major telecom. Critical infrastructure + FCC compliance."},
    {"name": "Shamla Naidoo", "title": "CISO", "company": "Netskope", "industry": "cybersecurity", "email": "", "source": "gracker_directory", "notes": "Cloud security vendor CISO. Thought leader on zero trust."},
    {"name": "Lakshmi Hanspal", "title": "CISO", "company": "Box", "industry": "tech", "email": "", "source": "gracker_directory", "notes": "Cloud content management. Data governance overlap."},
    {"name": "Eric Boateng", "title": "CISO", "company": "MassMutual", "industry": "insurance", "email": "", "source": "gracker_directory", "notes": "Major insurer. Jim Routh's successor. SOC2 + insurance regulations."},
    {"name": "Ben de Bont", "title": "CISO", "company": "ServiceNow", "industry": "tech", "email": "", "source": "gracker_directory", "notes": "ServiceNow CISO. IT workflow platform -- direct integration angle."},
    {"name": "Lenny Zeltser", "title": "CISO", "company": "Axonius", "industry": "cybersecurity", "email": "", "source": "gracker_directory", "notes": "Asset management security. SANS instructor. Educational influence."},
    {"name": "Rinki Sethi", "title": "Advisor / Ex-CISO", "company": "ForgeRock", "industry": "identity", "email": "", "source": "gracker_directory", "notes": "Identity security. Ex-Twitter, IBM, Palo Alto. Board-level influence."},
    {"name": "Dawn Cappelli", "title": "CEO & Co-Founder", "company": "Dragos", "industry": "ics_security", "email": "", "source": "gracker_directory", "notes": "ICS security leader. Ex-Rockwell Automation CISO."},
    {"name": "Malcolm Harkins", "title": "CSO", "company": "Epiphany Systems", "industry": "cybersecurity", "email": "", "source": "gracker_directory", "notes": "Ex-Intel CISO. Author. Risk management thought leader."},
    {"name": "Marnie Wilking", "title": "CISO", "company": "Booking.com", "industry": "travel", "email": "", "source": "gracker_directory", "notes": "Major travel platform. EU data protection + DORA."},
    {"name": "Jason Shockey", "title": "CISO", "company": "Cenlar FSB", "industry": "finance", "email": "", "source": "secureframe_50", "notes": "Mortgage servicing. Financial regulatory compliance."},
    # Healthcare CISOs from Becker's
    {"name": "Jeffrey Aguilar", "title": "CISO", "company": "Hoag", "industry": "healthcare", "email": "", "source": "beckers_2026", "notes": "Healthcare system in Newport Beach. HIPAA compliance."},
    {"name": "Brad Carvellas", "title": "CISO", "company": "Guthrie", "industry": "healthcare", "email": "", "source": "beckers_2026", "notes": "Regional healthcare. HIPAA + rural health IT."},
    {"name": "Sahan Fernando", "title": "CISO", "company": "Rady Childrens Health", "industry": "healthcare", "email": "", "source": "beckers_2026", "notes": "Pediatric healthcare. Sensitive population data governance."},
    {"name": "Randall Frietzsche", "title": "CISO", "company": "Denver Health", "industry": "healthcare", "email": "", "source": "beckers_2026", "notes": "Safety-net hospital. HIPAA + public health compliance."},
    {"name": "Steven Ramirez", "title": "CISO", "company": "Renown Health", "industry": "healthcare", "email": "", "source": "beckers_2026", "notes": "Regional healthcare system. HIPAA + operational security."},
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT LOWER(name) FROM prospects")
    existing = set(r[0] for r in cur.fetchall())

    inserted = 0
    skipped = 0

    for p in BATCH_3_DEVS:
        if p["name"].lower() in existing:
            print(f"  SKIP: {p['name']}")
            skipped += 1
            continue
        cur.execute(
            """INSERT INTO prospects (name, title, company, industry, email, source, notes, created_at, campaign, target_segment, batch_number, lane)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'developer', 3, 'builder')""",
            (p["name"], p["title"], p["company"], p["industry"], p["email"], p["source"], p["notes"], NOW, CAMPAIGN)
        )
        inserted += 1

    for p in BATCH_4_CISOS:
        if p["name"].lower() in existing:
            print(f"  SKIP: {p['name']}")
            skipped += 1
            continue
        cur.execute(
            """INSERT INTO prospects (name, title, company, industry, email, source, notes, created_at, campaign, target_segment, batch_number, lane)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ciso', 4, 'buyer')""",
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
    print(f"Remaining: {200 - total} ({100 - sum(1 for p in BATCH_3_DEVS if p['name'].lower() not in existing) - 75} devs, {100 - sum(1 for p in BATCH_4_CISOS if p['name'].lower() not in existing) - 63} CISOs)")
    conn.close()


if __name__ == "__main__":
    main()
