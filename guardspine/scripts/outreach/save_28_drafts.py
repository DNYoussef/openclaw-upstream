#!/usr/bin/env python3
"""Save all 28 corrected message drafts to outreach DB."""
import sqlite3, os, uuid, datetime

db = os.path.expanduser("~/.claude/outreach/outreach.db")
conn = sqlite3.connect(db)
c = conn.cursor()
now = datetime.datetime.now().isoformat()

# ── INVESTOR DRAFTS ──
investor_drafts = {
    "Caleb Sima": 'Caleb -- your CSA AI Safety work and the Helmet Security investment tell me you\'re watching the same gap I am: AI agents are writing production code, but nobody\'s governing the judgment calls those agents make.\n\nGuardSpine is an open-source engine (Apache 2.0) that generates tamper-proof "judgment receipts" for every AI code change -- mapping each decision to SOC 2, DORA, and EU AI Act controls. Ships as a GitHub Action, 5-minute install. Andy Ellis (ex-CSO Akamai) signed up for trial within 48 hours of seeing it.\n\nCSA\'s AI governance working group makes this directly relevant -- we\'re building the piece between "AI wrote the code" and "we can prove it was reviewed."\n\nHappy to send a 5-page brief, or grab 20 minutes: cal.com/davidyoussef/guardspine-demo\n\ngithub.com/guardspine | guardspine.ai/security\n\n-- David',

    "Guy Podjarny": 'Guy -- your "vibe coding to viable code" piece nailed something we\'re building for: when agents act as developers, someone has to hold the receipt.\n\nGuardSpine is the governance layer for AI-generated code. Open-source engine (Apache 2.0, BYOK) that creates tamper-proof evidence bundles per code change -- mapped to SOC 2, DORA, EU AI Act. Deploys as a GitHub Action in 5 minutes.\n\nYou built Snyk by giving developers security they\'d actually adopt. We\'re doing the same for governance -- developer-first, not compliance-first. 55 provisionally patented methods licensed exclusively, early traction from enterprise security teams.\n\n20 minutes or a 5-page brief? cal.com/davidyoussef/guardspine-demo\n\ngithub.com/guardspine | guardspine.ai/security\n\n-- David',

    "David B. Cross": 'David -- congrats on the ONCON Top 100 nod. Your podcast comments on CISOs needing to stay technical while AI reshapes security ops resonate with exactly what we\'re building.\n\nGuardSpine creates tamper-proof "judgment receipts" for every AI-generated code change. Each receipt maps the agent\'s decision to SOC 2, DORA, and EU AI Act controls -- giving CISOs an evidence trail, not just a review checkbox. Open-source core, GitHub Action, 5-minute deploy.\n\nJacob Friedman (G7/NIST advisor) is exploring our government procurement channel, and we\'re seeing early pull from enterprise security teams who need audit-grade proof that AI-written code was governed.\n\nWith 30+ patents in security tech and the Rain Capital lens, you\'d have sharp feedback. 20 minutes: cal.com/davidyoussef/guardspine-demo\n\ngithub.com/guardspine | guardspine.ai/security\n\n-- David',

    "Frederic Kerrest": 'Frederic -- you built the identity layer that enterprises can\'t operate without. The same gap now exists for AI-generated code: who made the change, what model decided, and can you prove it to an auditor?\n\nGuardSpine is an open-source governance engine that generates tamper-proof evidence bundles for every AI code change, mapped to SOC 2, DORA, EU AI Act. Apache 2.0, BYOK models, 97-99% margins. Ships as a GitHub Action.\n\nEU AI Act enforcement starts August 2026. DORA is already live. Every enterprise running AI dev tools will need this trail -- the same way they needed Okta for identity. Andy Ellis (ex-CSO Akamai) trialed within 48 hours.\n\n20 minutes to walk through the architecture: cal.com/davidyoussef/guardspine-demo\n\ngithub.com/guardspine | guardspine.ai/security\n\n-- David',

    "Mohamed Nanabhay": 'Mohamed -- your MozFest convening writeup highlighted founders building tech "in service of people." That framing maps to what we\'re doing with AI code governance.\n\nGuardSpine is an open-source engine (Apache 2.0) that creates tamper-proof evidence bundles proving how AI-generated code was reviewed and governed. Maps to SOC 2, DORA, EU AI Act. The open-source core means no vendor lock-in -- any team can audit the governance logic itself.\n\nMozilla\'s mission is keeping the internet open and accountable. AI is writing a growing share of production code, and right now there\'s no transparent, auditable record of those decisions. We\'re building that layer.\n\nEU AI Act enforcement starts August 2026. Kelsey Hightower (Google) offered ongoing involvement after seeing the architecture.\n\n5-page brief or 20 minutes -- happy either way: cal.com/davidyoussef/guardspine-demo\n\ngithub.com/guardspine | guardspine.ai/security\n\n-- David',

    "Sam Kassoumeh": 'Sam -- you built SecurityScorecard to make third-party risk measurable. The same measurement gap now exists for AI-generated code: enterprises can\'t score what they can\'t see.\n\nGuardSpine creates tamper-proof "judgment receipts" for every AI code change -- each one maps the model\'s decision to SOC 2, DORA, and EU AI Act controls. Open-source core (Apache 2.0), GitHub Action, 5-minute install. BYOK model architecture gives 97-99% margins.\n\nYour angel portfolio (Olympix, Vicarius, Corgea) shows you\'re already tracking the AI-security intersection. We provide the governance and evidence trail that makes AI code auditable.\n\n20 minutes or a 5-page brief: cal.com/davidyoussef/guardspine-demo\n\ngithub.com/guardspine | guardspine.ai/security\n\n-- David',

    "Jon Oberheide": 'Jon -- Duo proved that security adoption scales when you remove friction for the developer. We\'re applying that same principle to AI code governance.\n\nGuardSpine generates tamper-proof evidence bundles for every AI-generated code change, mapped to SOC 2, DORA, EU AI Act. Open-source core (Apache 2.0), deploys as a GitHub Action in 5 minutes. No agents to install, no workflow changes.\n\nYour Corridor and Sublime investments show you\'re still backing security infrastructure at the foundation layer. We sit right there -- between the AI writing code and the audit that proves it was governed. 55 provisionally patented methods, licensed exclusively via MOU.\n\nTD Bank\'s security team expressed interest, and Andy Ellis (ex-CSO Akamai) trialed within 48 hours.\n\n5-page brief or 20 minutes: cal.com/davidyoussef/guardspine-demo\n\ngithub.com/guardspine | guardspine.ai/security\n\n-- David',

    "Solomon Hykes": 'Solomon -- your "agentic CI/CD" thesis nails the speed problem. But when agents submit PRs 100x faster, who governs the judgment calls? That\'s the piece we\'re building.\n\nGuardSpine generates tamper-proof evidence bundles for every AI code change -- mapping each agent decision to SOC 2, DORA, EU AI Act controls. Open-source (Apache 2.0), ships as a GitHub Action. The governance layer that plugs into the pipeline Dagger is making programmable.\n\nYou containerized the build. We\'re containerizing the proof that the build was governed. Kelsey Hightower offered ongoing involvement after seeing the architecture.\n\nThere\'s a natural integration story here. 20 minutes to explore it: cal.com/davidyoussef/guardspine-demo\n\ngithub.com/guardspine | guardspine.ai/security\n\n-- David',

    "Andrew Peterson": 'Andrew -- congrats on the DryRun board seat. You\'re clearly tracking the AI code security shift -- DryRun does the review intelligence, but who holds the governance receipt?\n\nGuardSpine generates tamper-proof evidence bundles for every AI-generated code change, mapped to SOC 2, DORA, EU AI Act. Open-source core (Apache 2.0), GitHub Action, 5-minute install. BYOK models, 97-99% margins.\n\nYour Aviso portfolio (Protect AI -> Palo Alto, SGNL -> CrowdStrike) shows you pick infrastructure that becomes acquisition-grade. We sit at the same layer -- the evidence trail between "AI wrote this" and "we can prove it was governed." 55 provisionally patented methods, exclusively licensed.\n\n20 minutes or a 5-page brief -- happy either way: cal.com/davidyoussef/guardspine-demo\n\ngithub.com/guardspine | guardspine.ai/security\n\n-- David',
}

# ── BUYER DRAFTS ──
buyer_drafts = {
    "Akiko Amakawa": 'Hi Akiko,\n\nI saw your comment about Takeda needing a prioritization framework for digital investments -- and noticed the FY2026 restructure consolidates strategy and governance under your office.\n\nOne gap we keep hearing from pharma teams: AI-generated code changes ship without auditable evidence of human review. That creates risk under FDA/GxP and EU AI Act.\n\nGuardSpine is an open-source engine that creates tamper-proof evidence bundles for every AI code change -- maps to SOC 2, HIPAA, EU AI Act. GitHub Action install, 5 minutes, BYOK model. Andy Ellis (ex-CSO Akamai) is in active trial.\n\nWould a 20-minute walkthrough be useful? cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/security\n\nDavid',

    "Amit Gupta": 'Hi Amit,\n\nCongrats on the IDEXX CDO/CIO role -- joining a regulated diagnostics company with a fresh mandate is a compelling setup.\n\nOne challenge we hear from new tech leaders: dev teams are already using AI code tools, but there\'s no audit trail proving those changes were reviewed and governed. That\'s a gap in SOC 2 and FDA QSR.\n\nGuardSpine creates tamper-proof evidence bundles for every AI code change. Open-source engine, GitHub Action install in 5 minutes, BYOK model. Complements Vanta/Drata -- they prove infra config, we prove code changes were governed.\n\nWould 20 minutes be worth it to see how it fits IDEXX\'s stack? cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/security\n\nDavid',

    "Amy Friend": 'Hi Amy,\n\nFinRegLab\'s agentic AI market scan flagged a real tension -- AI adoption in financial services is accelerating, but explainability and audit trail gaps slow responsible deployment.\n\nWe built GuardSpine to close that specific gap. It creates tamper-proof "judgment receipts" for every AI-generated code change -- what the model proposed, what the reviewer accepted, what policy it mapped to. Evidence bundles that satisfy OCC examiners and SOC 2 auditors.\n\nOpen-source, Apache 2.0, GitHub Action install. Andy Ellis (ex-CSO Akamai, YL Ventures) is in active trial.\n\nGiven your work bridging innovation and regulation, I\'d value 20 minutes of your perspective -- and happy to demo: cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/security\n\nDavid',

    "Bonnie Boles, MD": 'Dr. Boles,\n\nYour point in Becker\'s stuck with me -- the CMIO role shifting from EHR optimization to AI governance, but community hospitals can\'t staff teams of AI scientists to do it.\n\nThat\'s exactly the problem we built for. GuardSpine creates tamper-proof evidence bundles for every AI-generated code change -- automated governance without adding headcount. Maps to HIPAA, SOC 2, and clinical compliance workflows.\n\nOpen-source engine, GitHub Action install in 5 minutes, BYOK model. No AI scientist team required.\n\nWould a 20-minute demo be useful? I\'d like to show how it fits a community health system\'s resource constraints: cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/security\n\nDavid',

    "Brian Cincera": 'Hi Brian,\n\nLeading security at Cargill\'s scale -- 70 countries, complex supply chain software, and a global dev org -- means AI code tools are probably already in use across teams.\n\nThe gap we keep seeing: no tamper-proof record that AI-generated code changes were reviewed and governed before shipping. That creates audit exposure under SOC 2 and supply chain security frameworks.\n\nGuardSpine creates evidence bundles for every AI code change. Open-source engine, GitHub Action install, BYOK model. Complements existing AppSec -- we prove the governance decision, not just the scan result.\n\nAndy Ellis (ex-CSO Akamai) is in active trial. Would 20 minutes be worth a look? cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/security\n\nDavid',

    "Carolina Garcia Rizo, PhD, MBA": 'Hi Carolina,\n\nYour board seat at QuantPi caught my attention -- AI governance at the model level is one piece of the puzzle. We\'re solving the adjacent gap: governance at the code change level.\n\nGuardSpine creates tamper-proof evidence bundles proving every AI-generated code change was reviewed and governed. Maps to SOC 2, EU AI Act, HIPAA. Open-source, Apache 2.0.\n\nFor your biotech portfolio companies (Transcripta, Oisin), this means FDA/GxP audit readiness without slowing dev teams. Andy Ellis (ex-CSO Akamai) is in active trial.\n\nWould 20 minutes be useful? Happy to walk through how it complements QuantPi\'s model-level governance: cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/security\n\nDavid',

    "Todd Lukens": 'Hi Todd,\n\nCongrats on the CSO Hall of Fame -- well deserved given the scope you carry at Nationwide across cybersecurity, architecture, and dev platforms.\n\nI noticed Nationwide is taking a "proactive but thoughtful" approach to Gen AI deployment. One blind spot we see in insurance: dev teams adopt AI code tools fast, but there\'s no evidence trail proving those changes were governed. That\'s a gap in SOC 2 and state regulatory exams.\n\nGuardSpine creates tamper-proof evidence bundles for every AI code change. Open-source, GitHub Action install, BYOK model. Complements existing tools -- Vanta proves infra config, we prove the code decision.\n\nWorth 20 minutes? cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/security\n\nDavid',

    "Sandip Wadje": 'Hi Sandip,\n\nYour Black Hat MEA session on quantum readiness for financial systems was well-timed -- but there\'s a nearer-term gap you\'ll recognize.\n\nDORA is live. AI code tools are spreading across dev orgs. But most banks have no tamper-proof evidence that AI-generated code changes were reviewed before production. That\'s a second-line-of-defense gap for Cloud, AI, and API risks -- exactly your remit.\n\nGuardSpine creates evidence bundles for every AI code change. Maps to DORA, SOC 2, EU AI Act. Open-source, Apache 2.0, GitHub Action install.\n\nGiven your EFR and EC3 work, I\'d value your perspective. 20 minutes? cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/security\n\nDavid',

    "Kieran Norton": 'Hi Kieran,\n\nYour Unite.AI interview on MCP as the TCP/IP stack for AI models resonated -- especially the point about enterprises needing governance processes that span business, IT, risk, and cybersecurity.\n\nWe built GuardSpine for the code layer of that governance stack. Tamper-proof evidence bundles for every AI-generated code change -- what the model proposed, what was accepted, what policy it mapped to. SOC 2, DORA, EU AI Act.\n\nOpen-source, Apache 2.0, GitHub Action install. We complement Deloitte\'s existing cyber AI practice -- you advise on governance frameworks, we produce the auditable evidence.\n\nWorth a conversation? Happy to explore channel fit: cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/security\n\nDavid',

    "Gil Danziger": 'Hi Gil,\n\nCongrats on the $116M debt round -- strong signal for Mondu\'s B2B BNPL model. Scaling across EU markets means DORA compliance is already on your plate, and CCD2 hits Nov 2026.\n\nAs CTO, you probably see this firsthand: devs adopting AI code tools fast, but no audit trail proving those changes were governed before production. That\'s a regulatory gap for EU fintech.\n\nGuardSpine creates tamper-proof evidence bundles for every AI code change. Open-source engine, GitHub Action install in 5 minutes, BYOK model. Maps to DORA and EU AI Act.\n\nWould 20 minutes be worth it? cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/security\n\nDavid',
}

# ── VELOCITY PROSPECTS ──
velocity_prospects = [
    ("Nik Koblov", "EVP of Engineering", "Ramp", "https://www.linkedin.com/in/koblov/", "linkedin_connect",
     "Nik -- saw Inspect is generating 30% of Ramp's merged PRs. We built an open-source GitHub Action that auto-creates signed evidence bundles for every AI code review. 5 min install. Runs in CI. github.com/guardspine guardspine.ai/dev"),
    ("Sanjay Nagaraj", "SVP Global Engineering", "Harness", "https://www.linkedin.com/in/sanjaynagaraj/", "linkedin_dm",
     "Sanjay -- Jyoti's quote about AI coding not helping teams ship faster hit a nerve with me. We were living that exact problem: more AI-generated code, same review and compliance capacity.\n\nSo we built GuardSpine. Open-source GitHub Action. Every AI code change gets reviewed by an LLM panel, and the output is a cryptographically signed evidence bundle -- who reviewed it, what was flagged, what was accepted.\n\nWhen your auditor asks \"how are AI code changes governed?\", the answer is a verifiable artifact, not \"we do manual review.\"\n\nRuns in CI. 5-minute install. Free tier.\n\nThe code and docs are at github.com/guardspine. If you want to see it run against a live repo: cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/dev"),
    ("Lindsey Simon", "VP of Engineering", "Vercel", "https://www.linkedin.com/in/lindseysimon", "linkedin_connect",
     "Lindsey -- your point about AI increasing throughput without changing who performs resonated. We built an open-source governance layer for AI code changes: signed evidence bundles in CI. No new dashboard. github.com/guardspine guardspine.ai/dev"),
    ("Mike Curtis", "VP of Engineering (Cloud)", "Vercel", "https://www.linkedin.com/in/mikecurtis123/", "linkedin_dm",
     "Mike -- I saw you're building out the SRE team at Vercel. Quick question: how are you handling governance for AI-assisted code changes that flow through CI/CD?\n\nWe built GuardSpine because the answer at most companies is still \"manual review\" or \"we trust the developer.\" Neither holds up under audit.\n\nIt's a GitHub Action. Runs in the pipeline. Every AI code change gets an LLM review panel, and the output is a cryptographically signed evidence bundle. Your CISO gets compliance artifacts. Your engineers keep shipping.\n\n5-minute install. Free tier. Open source.\n\nWhen the auditor asks how AI code changes were governed, you hand them a signed bundle instead of a Confluence page.\n\ngithub.com/guardspine\ncal.com/davidyoussef/guardspine-demo\nguardspine.ai/dev"),
    ("Andrew Mitchell", "VP of Engineering", "Tailscale", "https://www.linkedin.com/in/andrew-mitchell-257a8a25/", "linkedin_connect",
     "Andrew -- from Terraform to Tailscale, you've seen infrastructure-as-code eat the world. We applied the same principle to AI code governance: evidence bundles generated in CI, signed, verifiable. Open source GitHub Action. guardspine.ai/dev"),
    ("Adam Berman", "VP of Engineering", "Semgrep", "https://www.linkedin.com/in/adam-berman-75485829/", "linkedin_dm",
     "Adam -- I've been following Semgrep Supply Chain since launch. Your team has the scanning side nailed. Here's the gap I kept running into: scanning tells you what's in the code. It doesn't produce a signed record that a specific AI-generated change was reviewed, by whom, and what was accepted.\n\nGuardSpine sits downstream of tools like Semgrep. It's a GitHub Action that runs an LLM review panel on every AI code change and produces a cryptographically signed evidence bundle.\n\nSemgrep finds vulnerabilities. GuardSpine proves the change was governed. Together, your CISO gets a complete chain of evidence.\n\nWe're open source: github.com/guardspine. Happy to walk through how it fits with your existing pipeline: cal.com/davidyoussef/guardspine-demo\n\nguardspine.ai/dev"),
    ("Ori Keren", "CEO & Co-Founder", "LinearB", "https://www.linkedin.com/in/ori-keren-8254965/", "linkedin_dm",
     "Ori -- your prediction about productivity declining in 2025 landed. The LinearB data showing 91% longer review times at high AI adoption teams matched what we were seeing firsthand.\n\nSo we built the missing piece: governance that runs in CI, not in a dashboard.\n\nGuardSpine is a GitHub Action. Every AI code change gets an automated LLM review. The output is a cryptographically signed evidence bundle -- who reviewed it, what was flagged, what passed.\n\nFor your engineering leader customers, this is the answer to \"we adopted AI coding tools and now review is the bottleneck.\" The review still happens, but it produces a verifiable artifact instead of eating senior engineer time.\n\nOpen source: github.com/guardspine\nDemo: cal.com/davidyoussef/guardspine-demo\nguardspine.ai/dev"),
    ("Rohini Pradeep", "VP, Product Engineering", "Gusto", "https://www.linkedin.com/in/rohinipradeep/", "linkedin_connect",
     "Rohini -- modernizing payroll engineering under SOC 2/PCI while teams adopt AI coding tools is a hard governance problem. We built an open-source GitHub Action that produces signed evidence bundles per PR. guardspine.ai/dev"),
    ("Rakesh Rajan", "SVP of Engineering", "Rippling", "https://www.linkedin.com/in/rakeshxp", "linkedin_dm",
     "Rakesh -- scaling Rippling's engineering org across HR, IT, and Finance products means every team faces different compliance requirements. As AI coding tools increase throughput, the governance burden multiplies.\n\nWe built GuardSpine to solve this. It's an open-source GitHub Action that runs in your existing CI pipeline. Every AI code change gets an automated review panel, and the output is a cryptographically signed evidence bundle.\n\nNo new dashboard. No new headcount. The CISO gets compliance evidence. The dev team keeps shipping.\n\nFor someone who spent years at Goldman and Affirm, this is the \"prove it was governed\" layer that regulated engineering orgs need but don't have yet.\n\ngithub.com/guardspine\ncal.com/davidyoussef/guardspine-demo\nguardspine.ai/dev"),
    ("Lior Solomon", "VP of Engineering, Data & AI", "Drata", "https://www.linkedin.com/in/liorsolomon/", "linkedin_dm",
     "Lior -- I read your piece on compliance automation and data at Drata. You're building the compliance platform for thousands of companies. Quick question: how does your own engineering team prove AI code changes were governed?\n\nWe built GuardSpine because the answer for most teams is still manual review or trust. Neither produces audit-ready evidence.\n\nIt's a GitHub Action. Runs in CI. Every AI code change gets an automated LLM review, and the output is a cryptographically signed evidence bundle. The CI/CD equivalent of what Drata does for SOC 2 -- but for code governance.\n\nYour team would get it instantly. And your customers might want it too.\n\nOpen source: github.com/guardspine\nDemo: cal.com/davidyoussef/guardspine-demo\nguardspine.ai/dev"),
]

velocity_extras = [
    ("Dan Lines", "COO & Co-Founder", "LinearB", "https://www.linkedin.com/in/dan-lines/"),
    ("Cole Goeppinger", "Senior Director of Engineering", "Rippling", "https://www.linkedin.com/in/colegoeppinger/"),
    ("Matt Daley", "Director of Engineering", "Rippling", "https://www.linkedin.com/in/daleysoftware/"),
    ("Varun Badhwar", "CEO & Co-Founder", "Endor Labs", "https://www.linkedin.com/in/vbadhwar/"),
    ("Dan Lorenc", "CEO & Co-Founder", "Chainguard", "https://www.linkedin.com/in/danlorenc/"),
    ("Jonathan Nolen", "VP of Engineering", "Cortex", "https://www.linkedin.com/in/jnolen/"),
    ("Itamar Friedman", "CEO & Co-Founder", "Qodo", "https://www.linkedin.com/in/itamarf/"),
    ("Merrill Lutsky", "CEO & Co-Founder", "Graphite (Cursor)", "https://www.linkedin.com/in/merrill-lutsky/"),
    ("Jyoti Bansal", "CEO & Co-Founder", "Harness", "https://www.linkedin.com/in/jyotibansal"),
    ("Greg Foster", "CTO & Co-Founder", "Graphite (Cursor)", "https://www.linkedin.com/in/gregmfoster/"),
]

# ── UPDATE INVESTORS ──
inv_ok = 0
inv_fail = []
for name, draft in investor_drafts.items():
    rows = c.execute("UPDATE prospects SET message_draft=?, channel='linkedin_dm' WHERE name=? AND message_sent_at IS NULL", (draft, name)).rowcount
    if rows: inv_ok += rows
    else: inv_fail.append(name)
print(f"INVESTORS: {inv_ok} updated, not found: {inv_fail}")

# ── UPDATE BUYERS ──
buy_ok = 0
buy_fail = []
for name, draft in buyer_drafts.items():
    rows = c.execute("UPDATE prospects SET message_draft=?, channel='linkedin_dm' WHERE name=? AND message_sent_at IS NULL", (draft, name)).rowcount
    if rows == 0:
        # Try inserting new
        pid = uuid.uuid4().hex[:12]
        try:
            c.execute("INSERT INTO prospects (id, name, lane, channel, message_draft, created_at, landing_url, campaign) VALUES (?,?,?,?,?,?,?,?)",
                      (pid, name, "buyer", "linkedin_dm", draft, now, "guardspine.ai/security", "buyer_pharma_finance_feb26"))
            buy_ok += 1
            print(f"  Inserted new buyer: {name}")
        except Exception as e:
            buy_fail.append(f"{name}: {e}")
    else:
        buy_ok += rows
print(f"BUYERS: {buy_ok} updated/inserted, fail: {buy_fail}")

# ── INSERT VELOCITY PROSPECTS ──
vel_ok = 0
for name, title, company, url, channel, draft in velocity_prospects:
    existing = c.execute("SELECT id FROM prospects WHERE name=?", (name,)).fetchone()
    if existing:
        c.execute("UPDATE prospects SET message_draft=?, channel=?, linkedin_url=?, title=?, company=? WHERE name=?",
                  (draft, channel, url, title, company, name))
        vel_ok += 1
    else:
        pid = uuid.uuid4().hex[:12]
        c.execute("INSERT INTO prospects (id, name, title, company, linkedin_url, lane, channel, message_draft, created_at, landing_url, campaign) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (pid, name, title, company, url, "builder", channel, draft, now, "guardspine.ai/dev", "velocity_feb26"))
        vel_ok += 1
print(f"VELOCITY: {vel_ok} prospects saved")

# ── INSERT VELOCITY EXTRAS (no drafts) ──
vel_extra = 0
for name, title, company, url in velocity_extras:
    existing = c.execute("SELECT id FROM prospects WHERE name=?", (name,)).fetchone()
    if not existing:
        pid = uuid.uuid4().hex[:12]
        c.execute("INSERT INTO prospects (id, name, title, company, linkedin_url, lane, channel, created_at, landing_url, campaign) VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (pid, name, title, company, url, "builder", "linkedin_connect", now, "guardspine.ai/dev", "velocity_feb26"))
        vel_extra += 1
print(f"VELOCITY EXTRAS: {vel_extra} inserted")

# ── LOG ACTIVITY ──
c.execute("INSERT INTO activity_log (action, details, timestamp) VALUES (?,?,?)",
          ("draft_saved", f"Saved 28 corrected drafts: {inv_ok} investors, {buy_ok} buyers, {vel_ok} velocity. {vel_extra} velocity extras added.", now))

conn.commit()
total = c.execute("SELECT COUNT(*) FROM prospects").fetchone()[0]
drafts = c.execute("SELECT COUNT(*) FROM prospects WHERE message_draft IS NOT NULL AND message_draft != ''").fetchone()[0]
print(f"\nDB: {total} total prospects, {drafts} with drafts")
conn.close()
print("DONE")
