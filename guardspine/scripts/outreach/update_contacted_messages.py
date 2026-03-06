#!/usr/bin/env python
"""
Update message_draft for prospects with prior outreach history.

Categories:
1. GREEN SIGNALS (active relationships) - follow-up, not cold outreach
2. MESSAGES SENT (no response) - follow-up referencing prior touch
3. LINKEDIN CONNECTIONS SENT (DORA campaign) - reference the connection
4. LINKEDIN CONNECTIONS SENT (general) - reference the connection
5. DMs DRAFTED (pending send) - keep research-driven message, just note status
"""
import sqlite3
import os
import hashlib

DB_PATH = os.path.expanduser("~/.claude/outreach/outreach.db")
CAMPAIGN = "landing_page_200_feb26"

DEV_LANDING = "https://guardspine.ai/dev"
CISO_LANDING = "https://guardspine.ai/security"


def make_utm_url(segment, channel, utm_content):
    base = DEV_LANDING if segment == "developer" else CISO_LANDING
    campaign = "dev100_feb26" if segment == "developer" else "ciso100_feb26"
    ch = channel or "linkedin_connect"
    return "%s?utm_source=%s&utm_campaign=%s&utm_content=%s#roi" % (base, ch, campaign, utm_content)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def update_prospect(conn, prospect_id, hook, message):
    cur = conn.cursor()
    cur.execute("UPDATE prospects SET hook_text = ?, message_draft = ? WHERE id = ?",
                (hook, message, prospect_id))


def main():
    conn = get_conn()
    cur = conn.cursor()
    updated = 0

    # ===== CATEGORY 1: GREEN SIGNALS (active partners - DO NOT cold outreach) =====
    # These people are already engaged. Messages should be relationship-appropriate.

    # Kelsey Hightower (Google retired) - offered advisory role
    hook = "Follow-up: Kelsey offered advisory involvement on Feb 9. Do NOT send cold outreach."
    msg = """Hi Kelsey,

Following up on our conversation from Feb 9 -- your insight that attestations during code review "is a good idea" and the comparison to Google's LGTM gating process was exactly the validation I needed.

You mentioned you'd be happy to provide feedback, and I'd like to take you up on that. We've shipped 428 tests and the evidence bundle schema is stable. I'd value 20 minutes to walk you through where the attestation model landed and get your take on two architectural decisions.

Would a quick call work sometime this week?

- David"""
    update_prospect(conn, "a5fd2b211425", hook, msg)
    updated += 1

    # Kelsey Hightower (Independent - duplicate) - sent message, same person
    hook = "DUPLICATE of a5fd2b211425. Same person. Message sent Feb 9."
    msg = """[DUPLICATE ENTRY - see Kelsey Hightower @ Google (retired)]

Prior outreach: Message sent 2026-02-09 with github_action artifact.
Kelsey responded substantively, validated attestation concept, offered advisory involvement.
Use the other entry (a5fd2b211425) for follow-up.

- David"""
    update_prospect(conn, "303ab8629fce", hook, msg)
    updated += 1

    # Ilya Ploskovitov - active integration partner
    hook = "ACTIVE PARTNER. Do NOT cold outreach. PII-Shield integration in progress."
    msg = """[ACTIVE PARTNER - NOT A COLD OUTREACH TARGET]

Ilya is building PII-Shield v1.2.0 with features specifically for GuardSpine:
- PII_SAFE_REGEX_LIST for hash field whitelisting
- 80% memory allocation reduction for high-volume diff scanning
- Confirmed determinism with PII_SALT pinning

4 PRs merged across GuardSpine repos. 2 pending (codeguard-action #6, local-council #2).
Communication channel: LinkedIn DM + GitHub PRs.

Next action: Review his pending PRs, not send marketing messages.

- David"""
    update_prospect(conn, "e1e6f88d3b63", hook, msg)
    updated += 1

    # Ishwar Chavhan (IBM) - active partner, had meeting
    hook = "ACTIVE PARTNER. Triangle Strategy. Meeting held Feb 13. Igor sent follow-up Feb 16."
    msg = """[ACTIVE PARTNER - NOT A COLD OUTREACH TARGET]

Ishwar is Z-Inspection scientific advisor + IBM Senior Analyst.
Meeting held Feb 13 10AM ET with David and Igor.
Igor sent follow-up email Feb 16 with PR example, workflow config, and evidence bundle.

Triangle Strategy: Z-Inspection report -> G7 reference -> IBM compliance -> Ishwar as internal champion.
Timeline: Formalize scope by Feb 28, draft criteria March 15, run assessment March-April.

Next action: Follow up on Z-Inspection assessment scope, NOT send cold outreach.

- David"""
    update_prospect(conn, "ec8153d19e49", hook, msg)
    updated += 1

    # Ishwar Chavhan (Z-Inspection - duplicate)
    hook = "DUPLICATE of ec8153d19e49. Same person. Active partner."
    msg = """[DUPLICATE ENTRY - see Ishwar Chavhan @ IBM (ec8153d19e49)]

Same person, duplicate DB entry. All outreach tracked on primary entry.
Meeting held Feb 13. Igor sent follow-up Feb 16.

- David"""
    update_prospect(conn, "f834c7c2b451", hook, msg)
    updated += 1

    # ===== CATEGORY 2: MESSAGES SENT (no response yet) =====
    # These need follow-up messages that reference the prior touch.

    # Rock Lambros - sent competitive_matrix Feb 9, connection sent Feb 6
    cur.execute("SELECT research_notes FROM prospects WHERE id = ?", ("71cc75a80bb9",))
    row = cur.fetchone()
    research = (row["research_notes"] if row else "") or ""
    hook = "Follow-up to Feb 9 DM (competitive_matrix artifact). OWASP AI governance + CARE framework."
    msg = """Hi Rock,

I sent you a competitive matrix a couple weeks ago -- wanted to follow up with something more specific to your work.

Your CARE framework (Create, Adapt, Run, Evolve) for AI governance is the strategic layer. What's missing is the operational enforcement in CI/CD -- something that automatically generates the audit evidence your framework calls for.

I built that missing piece. Open-source GitHub Action, 428 tests, works offline with your own models. Maps your OWASP AI Exchange work to actual PR-level governance decisions with tamper-proof receipts.

Worth a 15-minute look? https://guardspine.ai/security?utm_source=linkedin_dm&utm_campaign=ciso100_feb26&utm_content=e7cf4004#roi

- David"""
    update_prospect(conn, "71cc75a80bb9", hook, msg)
    updated += 1

    # Andrea Abell - sent Feb 20
    hook = "Follow-up to Feb 20 DM. Eli Lilly CISO, CES 2026 AI agents quote."
    msg = """Hi Andrea,

Following up on my message from a few days ago. I noticed your CES 2026 comments about wanting AI agents to help close the cybersecurity talent gap -- that's exactly the problem I built GuardSpine to solve.

Instead of hiring more reviewers, GuardSpine uses multiple AI models to risk-tier every PR and generate tamper-proof audit trails. It maps directly to HIPAA and SOC 2 evidence requirements that Eli Lilly's audit teams need.

428 automated tests, open-source, works with your own models. Here's a cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_dm&utm_campaign=ciso100_feb26&utm_content=e827a66d#roi

- David"""
    update_prospect(conn, "5ff0f6fe6e39", hook, msg)
    updated += 1

    # Sanjeev Sah - sent Feb 20
    hook = "Follow-up to Feb 20 DM. Novant Health CISO, 2025 ORBIE winner."
    msg = """Hi Sanjeev,

Following up on my message from a few days ago. Congratulations again on the 2025 CarolinaCISO ORBIE -- building the security program at Novant from your dual SVP/CISO seat is exactly the kind of leadership that sees this blind spot clearly.

The governance gap around AI-generated code changes is especially acute in healthcare -- HIPAA auditors need evidence of what was reviewed, not just that a process existed.

I built an open-source tool that generates that evidence automatically. 428 tests, maps to HIPAA and SOC 2. Here's what it saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_dm&utm_campaign=ciso100_feb26&utm_content=1b259780#roi

- David"""
    update_prospect(conn, "2be4ae03643d", hook, msg)
    updated += 1

    # Devansh Bordia - sent github_action Feb 9
    hook = "Follow-up to Feb 9 DM (github_action artifact). AppSec/DevSecOps at People Interactive."
    msg = """Hi Devansh,

I shared the GitHub Action with you a couple weeks ago -- wanted to follow up. Your HackerOne pod lead experience means you've seen how code review breaks down at scale. The gap between "code was reviewed" and "here is tamper-proof evidence of what was decided" is what I built GuardSpine to close.

We've shipped 428 tests since then and the evidence bundle schema is stable. Would be great to get your AppSec perspective on the approach.

Quick look: https://guardspine.ai/dev?utm_source=linkedin_dm&utm_campaign=dev100_feb26&utm_content=a2f73eaa#roi

- David"""
    update_prospect(conn, "1fc56760a9f8", hook, msg)
    updated += 1

    # James Moore - sent DM Feb 16
    hook = "Follow-up to Feb 16 DM. Nova Jema AI governance frameworks."
    msg = """Hi James,

Following up on my DM from Feb 16 about Nova Jema's governance-first approach. Your work on high-risk decision systems in healthcare and public infrastructure overlaps directly with what I've built.

GuardSpine generates the tamper-proof audit evidence your governance frameworks call for -- automatically, at the PR level, with multi-model AI consensus. Open-source, 428 tests, works offline.

Would love to explore integration. Quick look: https://guardspine.ai/dev?utm_source=linkedin_connect&utm_campaign=dev100_feb26&utm_content=f1f4fae5#roi

- David"""
    update_prospect(conn, "bf06ccfb3269", hook, msg)
    updated += 1

    # Kayla Britt - sent guardspine_verify Feb 4
    hook = "Follow-up to Feb 4 DM (guardspine_verify artifact). Validation architect."
    msg = """Hi Kayla,

I shared guardspine-verify with you back on Feb 4 -- wanted to check if you had a chance to look at it. Your validation architecture background at Britt Biocomputing is exactly the lens I'd value on the evidence bundle approach.

We've added 428 tests and the schema is stable. The tamper-proof audit trail maps directly to FDA/HIPAA evidence requirements for AI-assisted code changes in biotech.

Quick refresher on the approach: https://guardspine.ai/dev?utm_source=linkedin_dm&utm_campaign=dev100_feb26&utm_content=35588bbf#roi

- David"""
    update_prospect(conn, "44cbc3b518b3", hook, msg)
    updated += 1

    # Yvonne Zhu - sent competitive_matrix Feb 9
    hook = "Follow-up to Feb 9 DM (competitive_matrix artifact). EY AI Assurance Leader."
    msg = """Hi Yvonne,

I sent you a competitive landscape overview a couple weeks ago -- wanted to follow up with a more specific angle. As EY's Americas AI Assurance Leader, you're literally writing the frameworks (NIST, EU AI Act) that GuardSpine maps to.

The gap I keep seeing: companies can demonstrate they have a code review process, but cannot produce tamper-proof evidence of what AI actually changed and whether a human meaningfully reviewed it. Your assurance teams need that evidence.

428 tests, open-source, maps to the frameworks you advise on: https://guardspine.ai/dev?utm_source=linkedin_dm&utm_campaign=dev100_feb26&utm_content=55042832#roi

- David"""
    update_prospect(conn, "a9607749cbc2", hook, msg)
    updated += 1

    # ===== CATEGORY 3: DORA CAMPAIGN - LinkedIn connections + emails sent Feb 12 =====
    dora_prospects = {
        "43a6ce41a6d0": ("Alex Korotkikh", "Pliant", "developer", "CTO of DORA-regulated EU fintech"),
        "4aa00cd58b0d": ("Boyko Karadzhov", "Payhawk", "developer", "Co-Founder CTO, EU spend management"),
        "68733ed7e609": ("Eric Pantera", "Swile", "developer", "CTPO of EU employee benefits fintech"),
        "67e2621809c6": ("Harald Wendel", "Moss", "developer", "CTO of EU spend management fintech"),
        "df967f28265a": ("Joao Cerdeira", "LOQR", "developer", "Left LOQR for SEI, DORA background"),
        "0514a0b69b22": ("Karin Nygard Hoijer", "Brocc", "developer", "20yr compliance, CCO at Brocc"),
        "cacc40094fdf": ("Kimberly Mattheys", "Solaris", "developer", "Head of AppSec, DORA BaaS platform"),
        "95f36b54216c": ("Konstantin Stiskin", "Finom", "developer", "Engineering Leader, Dutch fintech"),
        "101e454755c2": ("Marcin Klecha", "Ohpen", "developer", "VP Eng, now at HERE Technologies"),
        "84a35dc943cc": ("Mark OMeagher", "Navro", "developer", "CTO, cross-border payments"),
        "de78984f9197": ("Michel Andre", "Banking Circle", "developer", "Senior Exec Advisor/CIO"),
        "dfbb7bd5f2b5": ("Paul Jay", "Skaleet", "developer", "CTO, French core banking"),
        "c971a7120246": ("Ralph Post", "Fourthline", "developer", "CTO, KYC/identity verification"),
        "40a93d868df9": ("Rolf Njor Jensen", "Lunar", "developer", "VP Tech, Danish digital bank"),
        "cd59f37ff006": ("Ronen Benchetrit", "Mangopay", "developer", "CTO, payment infrastructure"),
        "8512d1344447": ("Sune Wettersteen", "Kompasbank", "developer", "Co-Founder CTO, Danish bank"),
    }

    for pid, (name, company, segment, context) in dora_prospects.items():
        first = name.split()[0]
        utm = cur.execute("SELECT utm_content FROM prospects WHERE id = ?", (pid,)).fetchone()
        utm_val = (utm["utm_content"] if utm else None) or hashlib.sha256(name.encode()).hexdigest()[:8]
        url = make_utm_url(segment, "linkedin_dm", utm_val)

        # Check what was sent
        sent_type = ""
        cur.execute("""SELECT action FROM activity_log WHERE prospect_id = ?
            AND action IN ('linkedin_connection_sent', 'email_sent', 'email_resent')
            ORDER BY timestamp""", (pid,))
        actions = [r["action"] for r in cur.fetchall()]
        if "email_sent" in actions:
            sent_type = "email and LinkedIn connection"
        elif "linkedin_connection_sent" in actions:
            sent_type = "LinkedIn connection request"

        hook = "Follow-up to DORA campaign (%s sent Feb 12). %s." % (sent_type, context)
        msg = """Hi %s,

I reached out in February as part of our DORA compliance research -- following up because the Jan 17 enforcement deadline makes this increasingly urgent for EU fintechs.

DORA Article 9 requires ICT change management with audit trails. Most teams can show they have a review process but cannot produce tamper-proof evidence of what was actually reviewed and decided at the code level. That gap is where regulatory exposure lives.

I built an open-source GitHub Action that generates exactly that evidence. 428 tests, works with your own models, maps to DORA ICT risk requirements. Here's the cost model: %s

- David""" % (first, url)
        update_prospect(conn, pid, hook, msg)
        updated += 1

    # ===== CATEGORY 4: LINKEDIN CONNECTIONS SENT (general, Feb 6) =====
    connection_prospects = {
        "21012caa6484": ("Arpit Dave", "BioMarin Pharmaceutical", "developer",
                         "CDIO at BioMarin. LinkedIn connection sent Feb 6."),
        "241b178b2b9f": ("Charity Majors", "Honeycomb.io", "developer",
                         "CTO Honeycomb, observability leader. Connection sent Feb 6."),
        "ffa49d9a6be5": ("Joseph Pearce", "RecordPoint", "developer",
                         "AI Governance head. Connection sent Feb 6."),
        "aa601bdcc350": ("Liz Rice", "Isovalent", "developer",
                         "Chief OSS Officer, CNCF board, eBPF pioneer. Connection sent Feb 6."),
        "65aaad136273": ("Mitchell Hashimoto", "HashiCorp", "developer",
                         "HashiCorp co-founder, created Terraform/Vault/Ghostty. Connection sent Feb 6."),
        "1de02bb18022": ("Samir Passi", "Kforce", "developer",
                         "R&D Engineer, Cornell background. Connection sent Feb 6."),
    }

    for pid, (name, company, segment, context) in connection_prospects.items():
        first = name.split()[0]
        utm = cur.execute("SELECT utm_content FROM prospects WHERE id = ?", (pid,)).fetchone()
        utm_val = (utm["utm_content"] if utm else None) or hashlib.sha256(name.encode()).hexdigest()[:8]

        # Get research notes for personalized hook
        cur.execute("SELECT research_notes FROM prospects WHERE id = ?", (pid,))
        row = cur.fetchone()
        research = (row["research_notes"] if row else "") or ""

        # Extract first fact for the hook
        facts = []
        for line in research.split("\n"):
            if line.strip().startswith("- ") and "FACTS:" not in line:
                facts.append(line.strip()[2:])

        if facts:
            fact_hook = facts[0][:120].rstrip(".,;")
        else:
            fact_hook = "your work at %s" % company

        url = make_utm_url(segment, "linkedin_dm", utm_val)
        hook = "Follow-up to Feb 6 connection request. %s" % context

        msg = """Hi %s,

Thanks for connecting. I've been following your work -- %s.

I built an open-source GitHub Action that risk-tiers every PR and generates tamper-proof audit trails. The gap between "code was reviewed" and "here is proof of what was reviewed and decided" is what this solves. 428 tests, MIT license, works with your own models.

Here's a calculator for what this saves your team: %s

- David""" % (first, fact_hook.lower() if fact_hook[0].isupper() else fact_hook, url)
        update_prospect(conn, pid, hook, msg)
        updated += 1

    # Naveen Kumar - special case, connection sent Jan 12 (oldest)
    hook = "Follow-up to Jan 12 connection request. TD Bank insider risk, AI governance podcast."
    msg = """Hi Naveen,

Thanks for connecting. Your podcast appearance on AI governance for fraud and compliance at scale caught my attention -- especially the point about traceability being the foundation of AI governance.

I built something that makes traceability operational at the code level. An open-source GitHub Action that risk-tiers every PR and generates tamper-proof audit trails. Maps directly to the SOC 2 and banking compliance evidence TD Bank's audit teams need.

428 tests, works with your own models. Here's the cost model: https://guardspine.ai/dev?utm_source=linkedin_dm&utm_campaign=dev100_feb26&utm_content=4c9e71aa#roi

- David"""
    update_prospect(conn, "210bf904b776", hook, msg)
    updated += 1

    conn.commit()
    print("Updated %d prospect messages with outreach history context." % updated)

    # Print summary
    print("\nUpdated categories:")
    print("  GREEN SIGNALS (do not cold outreach): 5")
    print("  MESSAGES SENT (follow-up): 7")
    print("  DORA CAMPAIGN (follow-up): %d" % len(dora_prospects))
    print("  CONNECTION REQUESTS (follow-up): %d" % (len(connection_prospects) + 1))
    print("  TOTAL: %d" % updated)

    conn.close()


if __name__ == "__main__":
    main()
