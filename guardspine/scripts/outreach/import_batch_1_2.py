#!/usr/bin/env python3
"""Import Batch 1 (developers) and Batch 2 (CISOs) into campaign DB."""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.claude/outreach/outreach.db")
CAMPAIGN = "landing_page_200_feb26"
NOW = datetime.now().isoformat()

BATCH_1_DEVS = [
    {"name": "Casey Lee", "title": "Software Engineer, Cloud Architect", "company": "AWS / nektos", "industry": "devtools", "email": "cplee@nektos.com", "source": "github_api", "notes": "Creator of act (run GH Actions locally, 69K stars)"},
    {"name": "Sarah Drasner", "title": "Engineering Director", "company": "Google", "industry": "tech", "email": "sarah.drasner@gmail.com", "source": "github_api", "notes": "Curator of awesome-actions (27K stars). Comprehension over configuration."},
    {"name": "Orta Therox", "title": "Co-founder", "company": "Puzzmo", "industry": "devtools", "email": "git@orta.io", "source": "github_api", "notes": "Created Danger-JS (5.4K stars). OG code review automation."},
    {"name": "Bo-Yi Wu", "title": "Software Engineer", "company": "Mediatek", "industry": "tech", "email": "appleboy.tw@gmail.com", "source": "github_api", "notes": "Created CodeGPT (1.5K stars). Golang GDE. 7.4K GitHub followers."},
    {"name": "William Woodruff", "title": "Security Engineer", "company": "Astral", "industry": "devtools", "email": "william@yossarian.net", "source": "github_api", "notes": "Created zizmor (GH Actions static analysis, 3.7K stars). Homebrew + PyPA member."},
    {"name": "Ville Saukkonen", "title": "Developer", "company": "Independent", "industry": "devtools", "email": "", "source": "github_api", "notes": "Built ai-codereviewer (1K stars). Directly in AI code review space."},
    {"name": "Varun Sharma", "title": "CEO/Co-Founder", "company": "StepSecurity", "industry": "devsecops", "email": "", "source": "github_api", "notes": "StepSecurity: supply chain security for GH Actions. Direct overlap."},
    {"name": "Markus Wolf", "title": "Developer", "company": "Statista", "industry": "data", "email": "", "source": "github_api", "notes": "Active Danger-JS contributor. Platform engineer at major data company."},
    {"name": "Rhysd", "title": "Developer", "company": "Independent", "industry": "devtools", "email": "", "source": "github_api", "notes": "Created actionlint (GH Actions linter, 3.6K stars). Deep GH Actions expertise."},
    {"name": "David Garcia Ortega", "title": "ML Engineer / Founder", "company": "Iterative", "industry": "mlops", "email": "", "source": "github_api", "notes": "CML creator (CI/CD for ML, 4.2K stars). Techstars alum."},
    {"name": "Sourcery AI", "title": "AI Code Review Platform", "company": "Sourcery", "industry": "devtools", "email": "hello@sourcery.ai", "source": "github_api", "notes": "Direct competitor. Instant AI code reviews. 1.8K stars."},
    {"name": "Kodus AI", "title": "AI Engineering Assistants", "company": "Kodus", "industry": "devtools", "email": "questions@kodus.io", "source": "github_api", "notes": "AI Assistants for Engineering Teams. 926 stars."},
    {"name": "Daniel Barnes", "title": "Engineer", "company": "Weights & Biases", "industry": "mlops", "email": "dabarnes2b@gmail.com", "source": "github_api", "notes": "ML infra + GH Actions contributor."},
    {"name": "Travis Howerton", "title": "Co-founder & CEO", "company": "RegScale", "industry": "compliance", "email": "", "source": "secureframe_list", "notes": "Compliance automation for code. Direct synergy with evidence bundles."},
    {"name": "David Brumley", "title": "CEO & Professor", "company": "Mayhem / CMU", "industry": "security", "email": "", "source": "secureframe_list", "notes": "Code security researcher + entrepreneur. Academic credibility."},
    {"name": "Zane Lackey", "title": "General Partner", "company": "Andreessen Horowitz", "industry": "vc", "email": "", "source": "secureframe_list", "notes": "a16z security investor. Ex-product security. Dual dev/investor angle."},
    {"name": "Brandon Dixon", "title": "Security Technologist", "company": "Microsoft Research", "industry": "tech", "email": "", "source": "secureframe_list", "notes": "Security researcher at MSFT. AI + security intersection."},
    {"name": "Katie Moussouris", "title": "Founder & CEO", "company": "Luta Security", "industry": "security", "email": "", "source": "secureframe_list", "notes": "Bug bounty pioneer. Vulnerability disclosure expert. High profile."},
    {"name": "Rachel Tobac", "title": "CEO", "company": "SocialProof Security", "industry": "security", "email": "", "source": "secureframe_list", "notes": "Social engineering expert. Huge LinkedIn following. Amplification potential."},
    {"name": "Lena Smart", "title": "Head of Trust", "company": "SecurityPal", "industry": "compliance", "email": "", "source": "secureframe_list", "notes": "Trust/compliance role. Direct overlap with evidence bundle value prop."},
]

BATCH_2_CISOS = [
    {"name": "Frank Aiello", "title": "SVP & CISO", "company": "Maximus", "industry": "government", "email": "", "source": "c100_2026", "notes": "C100 Visionary Award. Gov services. AI governance for federal contracts."},
    {"name": "Margarita Rivera", "title": "SVP & Global CISO", "company": "Carnival Corporation", "industry": "hospitality", "email": "", "source": "c100_2026", "notes": "C100 Trailblazer. Global ops, multi-jurisdiction compliance."},
    {"name": "Hussein Syed", "title": "SVP & CISO", "company": "RWJBarnabas Health", "industry": "healthcare", "email": "", "source": "c100_2026", "notes": "C100 Champion. Healthcare HIPAA compliance."},
    {"name": "David Cass", "title": "President & CISO", "company": "Keyrock", "industry": "crypto", "email": "", "source": "c100_2026", "notes": "Crypto/fintech. Highest regulatory scrutiny."},
    {"name": "Angela Williams", "title": "SVP & Global CISO", "company": "UL Solutions", "industry": "testing", "email": "", "source": "c100_2026", "notes": "Testing/certification. Audit evidence is their product."},
    {"name": "Brett Conlon", "title": "CISO", "company": "American Century Investments", "industry": "finance", "email": "", "source": "c100_2026", "notes": "Financial services. SOC2 + SEC requirements."},
    {"name": "Ryan Field", "title": "CISO", "company": "Bank of Hawaii", "industry": "finance", "email": "", "source": "c100_2026", "notes": "Banking. Regulatory audit pressure."},
    {"name": "Nashira Spencer", "title": "CISO", "company": "Stitch Fix", "industry": "ecommerce", "email": "", "source": "c100_2026", "notes": "E-commerce + AI-heavy engineering team."},
    {"name": "Tomas Maldonado", "title": "CISO", "company": "NFL", "industry": "sports", "email": "", "source": "c100_2026", "notes": "High-profile org. Massive attack surface."},
    {"name": "Erik Decker", "title": "CISO", "company": "Intermountain Health", "industry": "healthcare", "email": "", "source": "beckers_2026", "notes": "Major health system. HIPAA + AI governance."},
    {"name": "Jack Kufahl", "title": "CISO", "company": "Michigan Medicine", "industry": "healthcare", "email": "", "source": "beckers_2026", "notes": "Academic medical center. Research + clinical AI."},
    {"name": "Kim Sassaman", "title": "CISO", "company": "Universal Health Services", "industry": "healthcare", "email": "", "source": "beckers_2026", "notes": "400+ facilities. Massive scale compliance."},
    {"name": "Deneen DeFiore", "title": "VP & Global CISO", "company": "United Airlines", "industry": "aviation", "email": "", "source": "secureframe_50", "notes": "Critical infrastructure. SOC2 + DOT compliance."},
    {"name": "Jamil Farshchi", "title": "EVP & CISO", "company": "Equifax", "industry": "finance", "email": "", "source": "secureframe_50", "notes": "Post-breach transformation. Knows audit pain deeply."},
    {"name": "Deborah Wheeler", "title": "CISO", "company": "Delta Air Lines", "industry": "aviation", "email": "", "source": "secureframe_50", "notes": "Major airline. Regulatory + AI governance."},
    {"name": "Nasrin Rezai", "title": "SVP & Global CISO", "company": "Verizon", "industry": "telecom", "email": "", "source": "secureframe_50", "notes": "Telecom giant. 25yr career across Fortune 100."},
    {"name": "Kayla Williams", "title": "Field CISO", "company": "Cyera", "industry": "cybersecurity", "email": "", "source": "secureframe_50", "notes": "Data security company. Deep compliance expertise."},
    {"name": "Adam Marre", "title": "CISO & SVP", "company": "Arctic Wolf", "industry": "cybersecurity", "email": "", "source": "secureframe_50", "notes": "Security vendor CISO. Understands tooling gaps."},
    {"name": "Sherron Burgess", "title": "Global CISO", "company": "BCD Travel", "industry": "travel", "email": "", "source": "c100_2026", "notes": "Global travel company. Multi-jurisdiction compliance."},
    {"name": "Stephen Bennett", "title": "Group CISO", "company": "Dominos Pizza Enterprises", "industry": "food", "email": "", "source": "c100_2026", "notes": "Global franchise. PCI DSS + supply chain security."},
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT LOWER(name) FROM prospects")
    existing = set(r[0] for r in cur.fetchall())

    inserted = 0
    skipped = 0

    for p in BATCH_1_DEVS:
        if p["name"].lower() in existing:
            print(f"  SKIP: {p['name']}")
            skipped += 1
            continue
        cur.execute(
            """INSERT INTO prospects (name, title, company, industry, email, source, notes, created_at, campaign, target_segment, batch_number, lane)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'developer', 1, 'builder')""",
            (p["name"], p["title"], p["company"], p["industry"], p["email"], p["source"], p["notes"], NOW, CAMPAIGN)
        )
        inserted += 1

    for p in BATCH_2_CISOS:
        if p["name"].lower() in existing:
            print(f"  SKIP: {p['name']}")
            skipped += 1
            continue
        cur.execute(
            """INSERT INTO prospects (name, title, company, industry, email, source, notes, created_at, campaign, target_segment, batch_number, lane)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ciso', 2, 'buyer')""",
            (p["name"], p["title"], p["company"], p["industry"], p["email"], p["source"], p["notes"], NOW, CAMPAIGN)
        )
        inserted += 1

    conn.commit()

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
