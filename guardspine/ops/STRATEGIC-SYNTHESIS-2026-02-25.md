# GuardSpine Strategic Synthesis -- Single Vision

Date: 2026-02-25 (updated 2026-03-02 -- Kristen equity, Eric meeting, HumanX, Netflix pilot)
Author: David Youssef + Claude (comprehensive analysis)
Sources: All conversations, meetings, CRM, financial models, competitive research, Clarity analytics

---

## WHERE WE ARE RIGHT NOW

**One sentence:** GuardSpine is a technically complete, zero-revenue artifact governance platform with 15 warm relationships, a signed technology MOU, regulatory tailwinds, and 97-99% gross margins -- needing $1M to cross the valley from project to business.

### The Numbers That Matter

| Metric                    | Value                                                         | Source                                                    |
| ------------------------- | ------------------------------------------------------------- | --------------------------------------------------------- |
| Paying customers          | **0**                                                         | --                                                        |
| Revenue                   | **$0**                                                        | --                                                        |
| Product signups           | **1** (Andy Ellis, dev-page Starter trial)                    | /api/admin/signups                                        |
| Trial-to-paid pipeline    | **1** (Andy Ellis -- YL Ventures Partner, ex-CSO Akamai 20yr) | outreach.db                                               |
| Prospects in CRM          | 330                                                           | outreach.db                                               |
| Messages sent             | 144 (43.6%)                                                   | outreach.db                                               |
| Responses                 | 15 (10.4% of sent)                                            | outreach.db                                               |
| Green signals             | 15                                                            | outreach.db                                               |
| Yellow signals            | 2                                                             | outreach.db                                               |
| Website visitors (30d)    | 74 unique humans                                              | Clarity                                                   |
| LinkedIn DM response rate | **50%** (8/16)                                                | outreach.db                                               |
| Email response rate       | 4.2% (4/95)                                                   | outreach.db                                               |
| Government response rate  | **100%** (3/3)                                                | outreach.db                                               |
| Tests passing             | 428+                                                          | codeguard-action CI                                       |
| Gross margins (BYOK)      | 97-99%                                                        | 04-financial-math.md                                      |
| Monthly burn              | **$26,500**                                                   | Kristen = 2% equity, no cash, no AI budget (agreed Mar 2) |
| Runway at $1M raise       | **37+ months**                                                | $1M / $26.5K                                              |

### The Team

| Person               | Role                                       | Compensation                                    | Status                                    |
| -------------------- | ------------------------------------------ | ----------------------------------------------- | ----------------------------------------- |
| David Youssef        | CEO, vision, sales, strategy               | 40% equity (post-raise) + $10K/mo               | Full-time                                 |
| Igor Malovitsa       | CTO, technical co-builder (Rust/TS/Crypto) | 40% equity (post-raise) + $10K/mo               | Full-time                                 |
| Kristen Hengst Smith | GTM advisor, angel network                 | **2% equity, no cliff, no cash** (agreed Mar 2) | Active, next sync Mar 10                  |
| Chris Hood           | Advisor, Noematic AI, Google connections   | TBD                                             | Active                                    |
| Logan Napolitano     | Technology partner (Proprioceptive AI)     | Revenue share (MOU)                             | MOU signed by David, awaiting countersign |
| Ilya Ploskovitov     | OSS contributor (PII-Shield)               | Volunteer                                       | Active, 4 PRs merged                      |
| Eric Skiff           | Advisory prospect (Tanooki Labs)           | TBD                                             | Meeting Mar 3 4pm ET                      |

---

## ALL THE THREADS, WOVEN TOGETHER

### Thread 1: Kristen (The Money Person)

Kristen gave us the operating system for GTM. Her rules:

1. **Follow the money.** CISO buys, not VP Eng. Budget line = DevSecOps / compliance audit.
2. **Dominate a wedge first.** Horizontal positioning is a liability at pre-revenue.
3. **Two-website experiment.** guardspine.ai (CISO) vs guardspine.com (dev). See who bites.
4. **Bridge the $0-to-$499 gap.** Can't prove willingness-to-pay without a path from free to paid.
5. **TD Bank is the holy grail.** "If you could penetrate TD Bank at all at any scale, you go from -- like a thousandfold become more desirable to investors."

**Mar 2 sync outcomes (Team Sync #2):**

- **Compensation agreed:** 2% equity, no cliff, no cash. David and Igor both agreed.
- **HumanX conference (early April, SF):** Kristen on VC track, will pitch GuardSpine. Deck must be ready by Apr 1.
- **Netflix pilot:** Contact re-emerged after 3 weeks (Paramount chaos). Target: pilot this month.
- **Eric Skiff:** Meeting scheduled Mar 3. Kristen pushing him to test product + her CTO "Mark" to kick tires.
- **Pitch deck approach:** Start with Word/bullets outline, pressure test with AI (VC/CISO/CFO personas), 10 slides max.
- **$499 Starter confirmed:** Fits expense-account range, no procurement needed.
- **Business formation needed:** LLC/C-Corp, EIN, operating agreement, cap table, bank account.
- **Dismissed Andy Mac's marketing team pivot** -- stay focused on governance.
- **Engineer testimonials required:** "Without them, it's a conversation killer with investors."
- **Next sync: Tue Mar 10, 2pm ET** (Kristen cannot do Mondays -- doctor's appointment)

### Thread 2: Logan / Proprioceptive AI (The Moat)

MOU signed by David Feb 25. 55 provisional patents on cognitive probes.

**What this changes:** Every competitor treats AI output as a black box. GuardSpine + Proprioceptive AI can prove whether the model was confident or guessing. This is the difference between governance theater and governance evidence.

**Integration:** Evidence bundles gain three new fields:

- `probe_confidence` (measured from hidden states, not self-reported)
- `hallucination_risk` (probe-detected)
- `drift_score` (deviation from training distribution)

**Constraint:** Only works with self-hosted models (Ollama). Fine for airgapped/gov/defense. Not yet for OpenAI/Anthropic API users.

**Competitive matrix after integration:**

| Capability       | Vanta | Drata | Snyk    | CodeRabbit | GuardSpine              |
| ---------------- | ----- | ----- | ------- | ---------- | ----------------------- |
| Evidence trail   | YES   | YES   | no      | no         | **YES**                 |
| Crypto proof     | no    | no    | no      | no         | **YES**                 |
| AI-native        | no    | no    | partial | YES        | **YES**                 |
| Offline/airgap   | no    | no    | no      | no         | **YES**                 |
| Cognitive probes | no    | no    | no      | no         | **YES (3yr exclusive)** |

### Thread 3: Igor (The Builder)

Igor independently sends technical follow-ups with PR examples, workflow configs, and evidence bundles. He sent technical artifacts to both Ishwar AND Jacob on Feb 16 -- concrete demonstrations, not abstract pitches.

His CFO Justification Kit idea: developers get the tool free, but we hand them a package to sell it up to their CISO. ROI calculator + compliance checklist + exec summary + sample evidence bundle. The developer becomes the internal champion; the CISO writes the check.

### Thread 4: Chris Catoya (The Network Multiplier)

Catoya validated our open-core model in the Feb 16 meeting. He then introduced us to Andy Macintosh through the Product G2M Signal group (Grey Tribe Conclave).

**The Catoya chain:**
Catoya -> Andy Mac (enterprise GTM expert) -> C Neill (Texas enterprise) + Chris Forrester (Hypernym.ai)
Catoya -> bio-hacking partner -> Gene Lens standalone business opportunity

### Thread 5: Andy Macintosh (The GTM Thesis)

Andy is ex-Niantic (6yr Pokemon GO), ex-EA (FIFA), ex-IDEO. Called "enterprise whisperer" by the group.

**His thesis for GuardSpine:** Target "velocity-crushed engineering managers" -- EMs blocked by security/compliance review processes. They'll pay $499/mo to unblock their team, then the CISO formalizes the purchase at Team/Org tier.

**This validates the Snyk model (pincher strategy):**

1. Bottom-up: Developer installs free Action -> proves value -> EM pays for Starter
2. Top-down: CISO sees evidence in their compliance workflow -> buys Org tier
3. Both lanes converge inside the same enterprise

**Andy also brought competitive intel:**

- cubic.dev (YC-backed, micro-agent architecture, 51% fewer false positives) -- they REVIEW code, we GOVERN artifacts
- Hypernym.ai (compression tech, future crossover)
- Palantir ontology narrative: "governance = version control for the real world"

### Thread 6: Jacob Friedman (The Government Channel)

G7 Cybersecurity Working Group contributor. Co-authored "SBOM for AI" paper with Italy's ACN + Germany's BSI.

**His framing:** "Sovereign backbone" -- GuardSpine as national infrastructure, not developer tooling.

SBOM tells you WHAT is in the system. GuardSpine proves WHAT HAPPENED to it. Natural complement. Treasury boards need something testable.

**UPDATE Feb 25 -- Jacob replied with concrete action items:**

1. Add CMMC/CPCSC Level 1 compliance mapping (3rd party partner needed for L2/3)
2. Platform One container: RHEL9 or Ubuntu Pro CIS FIPS STIG 22.04 at `repo1.dso.mil`
3. Offered to recommend GuardSpine to P1 helpdesk for registry access
4. Flagged SAM.gov opportunity: `sam.gov/opp/f36d565bb941494c8e40a331836bca52/view`
5. Meeting Sam McNaull at IronFort tomorrow (goironfort.com)
6. Meeting CSE contact next month -- will share GuardSpine

**Why this matters:** This is not "I'll think about it." This is "here is the technical spec, here is the procurement URL, let me introduce you to the right people." Government channel moved from warm to active.

### Thread 7: Ishwar Chavhan (The Regulatory Bridge)

IBM + Z-Inspection (EU framework for AI trustworthiness assessment per EU Ethics Guidelines).

Evidence bundles could automate 4 of 7 ALTAI requirements. Converts Z-Inspection from point-in-time manual audits to continuous machine-verifiable evidence trails.

Jacob pushes from the top (G7 policy). Ishwar validates from the bottom (assessment methodology). Both converge on GuardSpine as reference implementation.

### Thread 8: Phil Venables + Andy Ellis (The Investor-Customer Overlap)

Phil Venables (ex-CISO Google Cloud, Ballistic Ventures) engaged with DD questions. This is RARE for a pre-revenue startup. Ballistic is a cybersecurity-specialist VC.

Andy Ellis (YL Ventures) **signed up on the dev-page Starter trial Feb 23** -- 48 hours after landing pages went live. This is not a passive signal. A cybersecurity VC partner who built Akamai's security org from 1 person to 90+ proactively entered his email to trial the product. He used `andy+guards@directmessage.tech` (the +guards tag = intentional tracking, not accidental).

**Why this matters for probability:** Andy Ellis is simultaneously a potential customer, investor, and amplifier (CISO Series podcast co-host reaching thousands of security leaders). One conversion touches three gates at once.

Warm follow-up sent Feb 24 with evidence bundle + cal.com link + Phil Venables traction signal.

### Thread 9: Brent Foster (The Enterprise Proof Point)

VP Engineering at TD Bank. Replied Feb 17 with technical question about in-toto differentiation. David answered same day. If Brent converts to a pilot -- even unpaid -- it transforms the entire fundraise narrative. Kristen said this explicitly.

### Thread 10: Eric Skiff / Tanooki Labs (The Advisory Bridge)

Kristen's introduction. "Better for the stage you are at than I am."

**Who Eric is:** Co-founder of Tanooki Labs (2012-present), a product dev agency
that has built 160+ products and helped clients raise $100M+ collectively.
Co-founded NYC Resistor (the Brooklyn hackerspace that incubated MakerBot,
sold to Stratasys for ~$400M). Previously at AOL/QLabs (innovation lab) and
Drop.io (acquired by Facebook). BS in CS from Wagner College.

**What Tanooki Labs does:** "Technical co-founders for hire." Sprint Zero
methodology (2-5 week kickoff producing clickable prototypes). Development
pods (1 CTO + 1 PM + 1-3 devs). Built tools for Dapper Labs (Flow blockchain),
Heat Seek NYC (legally admissible sensor evidence for courts). $390K-$600K
typical engagement.

**What Eric can actually do for GuardSpine:**

- Advisory-tier pattern matching from 160+ zero-to-one products (not a paid engagement)
- Warm intros to accelerator networks: YC, Techstars, Interplay Ventures
- UX/onboarding critique from someone who has seen hundreds of trial-to-paid conversions
- NYC tech community connections (NYC Resistor alumni network)
- Product/market fit gut-check from a deeply technical builder

**What Eric is NOT:**

- Not a cybersecurity domain expert (no security products in Tanooki portfolio)
- Not a sales team (will not sell for us)
- Not a cost-effective dev shop ($390-600K per engagement -- we have Igor)
- No visible connections to cybersecurity-focused VCs (Ballistic, YL, ForgePoint)

**Best framing for the call:** Advisory relationship + introduction exchange.
Ask for: accelerator intros, trial-to-paid conversion advice, NYC founder network.
Do NOT pursue a paid dev engagement (wrong spend at this stage).

Intro reply sent with 5 PDFs + 6 links. **Meeting scheduled: Tue Mar 3, 4-5pm ET.**
Eric replied Mar 2 with availability. Igor CC'd on confirmation email.
Kristen pushing Eric to test product + her CTO "Mark" to kick tires as well.

### Thread 11: PE Portfolio Distribution (The Scale Engine)

**This is the single most important growth lever we have not yet activated.**

Three research reports (Desktop/guardspine/research/) map a distribution model
where PE firms deploy preferred vendors across their entire portfolio. The thesis:

1. PE-backed companies outnumber public companies 4:1 in the US (14,300 vs 3,550)
2. 52% of PE firms with >$25B AUM maintain mandatory preferred vendor programs
3. 95% of PE firms require basic technical controls across portfolios
4. 97% require ongoing visibility into portfolio company cybersecurity incidents
5. Vanta only began hiring for PE partnerships in 2025 -- the window is OPEN
6. No compliance platform has been purpose-built for PE portfolio deployment

**How the model works (not "invest-then-deploy" but "partner-then-deploy"):**

- PE firm selects a preferred vendor for compliance/governance
- Vendor gets deployed across 20-250+ portfolio companies
- Entry point is the Operating Partner (not the investment team)
- The pitch: "We save your portfolio $50K/company/year on compliance costs
  while reducing cyber risk by 60%"
- Land with 2-3 pilot portcos, prove value, expand across portfolio in 12-18mo

**Tier 1 PE targets (formalized portfolio tech programs):**

| Firm         | AUM    | Portfolio                      | Why GuardSpine Fits                                                                                                            |
| ------------ | ------ | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| Hg Capital   | $100B+ | 58+ companies                  | Acquired AuditBoard ($3B), invested in A-LIGN. Direct compliance appetite. 60 operating professionals incl. cyber specialists. |
| Vista Equity | $101B+ | 90+ companies                  | Most systematized tech deployment in PE. VSOPs mandate standardization. "Agentic AI Factory" deploying AI across portfolio.    |
| KKR          | $686B  | 100+ portcos                   | Capstone team saved $700M+ via centralized procurement. Dedicated cyber centers of excellence.                                 |
| Thoma Bravo  | $181B+ | 75+ companies                  | Cyber Consortium (30 experts). Owns SailPoint, Proofpoint, Darktrace. Compliance/GRC is a stated theme.                        |
| Blackstone   | $1T+   | 250+ companies, 700K employees | Portfolio Cybersecurity Team. Standardized assessments. THL deployed single MDR across 35+ portcos.                            |

**Tier 2 targets (mid-market, more realistic for early-stage):**

- Audax Private Equity ($19B AUM, 175+ platforms)
- Accel-KKR ($23B+, mid-market software focus)
- Francisco Partners ($45-50B AUM, owns Forcepoint, Jamf, BeyondTrust)

**The CMMC angle (highest urgency):** PE firms acquiring defense contractors
face CMMC 2.0 enforcement with penalties up to $100M. Summit 7 and PreVeil
already market CMMC compliance to PE firms. Jacob Friedman's CMMC/CPCSC
recommendations align perfectly with this channel. One PE firm with 10 defense
portcos = 10 Org-tier contracts at $12K/mo each = $1.44M ARR from one deal.

**Entry strategy (from research):**

1. Build multi-tenant "Fund Manager View" dashboard (sponsor sees green/yellow/red across all portcos)
2. Enter through vCISO firms (Emergent Security, Fractional CISO, Ankura) -- they select tools for portfolio deployment
3. Apply to GetProven platform (60% of Tier 1 PE firms use it for vendor discovery, $58M+ in deals/year)
4. Land 2-3 pilot portcos at steep discount, prove 80% reduction in audit prep time
5. Pitch Operating Partner with portfolio-wide economics
6. Structure as MSA: $5-10K/company/year, 30-50% portfolio discount for 10+ companies

**Why this matters for the probability model:** The PE channel is a THIRD
independent path to customers alongside:

- Path A: Bottom-up developer adoption (Andy Ellis / Starter tier)
- Path B: Government contracts (Jacob Friedman / CMMC / Platform One)
- Path C: PE portfolio distribution (NEW -- one deal = 20-50 customers)

**What we need to build for PE readiness (beyond PR #10):**

- Multi-tenant sponsor console with portfolio-wide compliance dashboard
- SOC 2 Type II for GuardSpine itself (eat your own dogfood)
- "100-day playbook" integration (PE sacred timeline)
- CMMC Level 1 rubric (already in PR #10 P1 tasks -- dual purpose)

### Thread 12: Angel/PE Investor Pipeline (The Raise Accelerator)

CRM contains 98 investor-lane prospects. 23 high-priority unsent (TIER1+TIER2).
Calendar event created for Feb 26 8:30-9:00 AM: "Angel/PE Investor Outreach:
10 TIER1+TIER2 LinkedIn DMs."

Key reframe from the PE research: **Do not conflate the angel raise with the PE
distribution channel.** These are two separate motions:

1. **Angel raise ($1M):** Traditional angel investors for capital. Use Kristen's
   network, Andy Ellis/Phil Venables traction, YL Ventures connection.
2. **PE distribution (post-first-customer):** Preferred vendor partnerships for
   customer acquisition. Target Operating Partners, not investment teams.
   PE firms invest in companies with proven revenue, not pre-seed startups.

The angel investors in the CRM are for motion #1. PE distribution is motion #2,
to be activated after Andy Ellis converts and we have proof of value.

---

## THE UNIFIED NARRATIVE

> SaaS is getting squeezed. Every category is being compressed by AI. The ONLY category that grows when AI accelerates is governance -- someone has to verify what AI produces. GuardSpine is the one bet that benefits from the same force that is killing everything else.

**What we are:** Insurance against AI-generated risk. A governance tool that happens to use AI. Not an AI tool.

**What we produce:** Tamper-proof judgment receipts. Court-admissible proof of what was reviewed, by whom, and what they found.

**Who buys (three channels):**

1. **CISOs / CCOs** at 500+ engineer companies in regulated industries (finance, healthcare, insurance, defense, government)
2. **Government / Defense** via CMMC/CPCSC compliance and Platform One containers
3. **PE Operating Partners** deploying compliance automation across 20-250+ portfolio companies

**Why now:** DORA enforceable since Jan 2025. **EU AI Act full enforcement Aug 2, 2026** --
every company deploying high-risk AI in Europe must produce compliance evidence.
65% of PRs ship unreviewed. AI-generated code has 1.7x more defects. Nobody is
producing evidence. We do. And we will ship the compliance release in **June 2026**
-- two months before enforcement -- so customers are ready on day one.

**The moat:**

1. Open-core (developers adopt free, CISOs pay for dashboard)
2. BYOK (97-99% margins, competitors run inference at 70-80%)
3. Cryptographic proof chain (nobody else has this)
4. 3-year exclusive cognitive probe license (55 patents, proves model was confident or guessing)

---

## FINANCIAL MODEL: PATH FROM $0 TO EXIT

### The Plan (No Further Dilution)

```
CAP TABLE (post-raise, updated Mar 2):
  David Youssef    40.0%   (co-founder, vision/sales/strategy)
  Igor Malovitsa   40.0%   (co-founder, CTO/engineering)
  Kristen H Smith   2.0%   (GTM advisor, no cliff, no cash)
  Angel investor   10.0%   ($1M raise)
  Hire pool         8.0%   (future hires, ~1.5% each via staircase model)
                  ------
                  100.0%

  Pre-raise (founding): David 44.4% / Igor 44.4% / Kristen 2.2% / Pool 8.9%
  Pool funds 5-6 hires at ~1.5% each. Hires gated by MRR thresholds (staircase model).

RAISE $1M angel round (10% for $1M)
  |
  v
SURVIVE: $26,500/mo burn = 37+-month runway
  |
  v
BREAKEVEN: 14-22 customers (M4-M11 per model, conservative -- modeled at $35.5K burn)
  At $26.5K burn, breakeven is FASTER:
  - 55 Starter-only, OR
  - 30 Starter + 3 Team, OR
  - 3 Org customers
  |
  v
REINVEST: Every post-breakeven dollar goes into marketing/growth
  - No further rounds
  - No further dilution
  - David and Igor stay at 40% each through exit (no further dilution)
  |
  v
GROW: Hire as P&L permits (CSM, Sales Eng, Compliance Counsel, PM, SDR)
  |
  v
EXIT: Sale or acquisition at target valuation
```

**Note on co-founder alignment:** Near-equal equity between David and Igor
is a strong signal to investors. Misaligned cap tables are a top-5
reason angels pass. 40/40 (post-dilution) = both founders fully committed.
Kristen's 2% advisor allocation is clean and standard for the role.
8% hire pool enables staircase growth without further fundraising.

### Breakeven Scenarios (from 04-financial-math.md)

| Scenario | Breakeven Month | Cash Burned | Cash Preserved | Customers |
| -------- | --------------- | ----------- | -------------- | --------- |
| BEAR     | M11             | $206K       | 79% ($794K)    | 22        |
| BASE     | M5              | $82K        | 92% ($918K)    | 14        |
| BULL     | M4              | $29K        | 97% ($971K)    | 15        |

### Growth Trajectory (BASE Scenario, Post-Breakeven Reinvestment)

| Month         | Customers | MRR    | ARR    | Bank Balance |
| ------------- | --------- | ------ | ------ | ------------ |
| 5 (breakeven) | 14        | $39K   | $467K  | $918K        |
| 8             | 29        | $85K   | $1.0M  | $956K        |
| 12            | 51        | $159K  | $1.9M  | $1.1M        |
| 18            | 95        | $314K  | $3.8M  | $1.6M        |
| 24            | 135       | $486K  | $5.8M  | $2.5M        |
| 30            | 174       | $672K  | $8.1M  | $3.8M        |
| 36            | 210       | $871K  | $10.4M | $5.6M        |
| 48 (hiring)   | 507       | $2.48M | $29.8M | $42.8M       |

### What David's 45% Is Worth at Exit

#### CORRECTED: Cybersecurity SaaS Multiples

Generic SaaS trades at 6-10x. Cybersecurity SaaS trades at 13-22x.
Category-creating cybersecurity with unique IP commands 15-25x+.
Reference: CrowdStrike ~22x, cloud security average 21.7x,
Wiz acquired at 45-65x (strategic premium).

GuardSpine-specific premium drivers:

- 97-99% gross margins (vs 70-80% industry average)
- Regulatory forcing function (DORA, EU AI Act, CMMC)
- Cornered resource: 3yr exclusive cognitive probes (55 patents)
- Cryptographic proof chain (no competitor has this)
- Government + defense channel (CMMC/P1 = sticky, large contracts)

Multiple trajectory: **15x at early stage -> 20x at growth -> 25x+ at scale**

David's stake = **40%** post-raise (44.4% pre-raise, 10% dilution to angel, 8% hire pool)

| ARR at Exit | Multiple | Exit Valuation | David's 40% | Igor's 40% | Kristen's 2% | Angel 10% | Staircase Timing |
| ----------- | -------- | -------------- | ----------- | ---------- | ------------ | --------- | ---------------- |
| $1.67M      | 15x      | $25M           | **$10M**    | $10M       | $500K        | $2.5M     | M12              |
| $2.5M       | 15x      | $37.5M         | **$15M**    | $15M       | $750K        | $3.75M    | M14              |
| $3.33M      | 15x      | $50M           | **$20M**    | $20M       | $1M          | $5M       | M17              |
| $6.25M      | 20x      | $125M          | **$50M**    | $50M       | $2.5M        | $12.5M    | M18              |
| $8.33M      | 30x      | $250M          | **$100M**   | $100M      | $5M          | $25M      | M20 (base)       |
| $10M        | 25x      | $250M          | **$100M**   | $100M      | $5M          | $25M      | M23              |
| $25M        | 25x      | $625M          | **$250M**   | $250M      | $12.5M       | $62.5M    | M40              |

**ARR thresholds at cybersecurity multiples (40% stake):**

| Target         | ARR needed | Multiple                               | Staircase Timing (Bear/Base/Bull) |
| -------------- | ---------- | -------------------------------------- | --------------------------------- |
| $10M to David  | **$1.67M** | 15x                                    | M12                               |
| $50M to David  | **$6.25M** | 20x                                    | M18                               |
| $100M to David | **$8.33M** | 30x (strategic: Vanta/ServiceNow/MSFT) | M40 / M20 / M14                   |
| $100M to David | **$10M**   | 25x (organic)                          | M23                               |

_Note: 30x multiple assumes strategic acquisition (Vanta, ServiceNow, Microsoft). Staircase model (revenue-gated hiring from 8% pool) accelerates timelines vs static team._

All targets fall within the staircase BASE model timeline (M20 = 1.7 years for $100M).
These are "execute the plan" problems, not "become a unicorn" problems.

**Bonus: Igor gets the same numbers.** Equal founders, equal upside.
$100M exit to David = $100M exit to Igor. Alignment is total.
Angel investor at $250M exit: $25M (25x return on $1M).

---

## BAYESIAN PROBABILITY ANALYSIS

### Methodology

Gate-based conditional probability decomposition. Each gate must be passed sequentially. Probabilities incorporate ALL available evidence from conversations, pipeline data, competitive research, and financial models.

### The Five Gates

#### ORIGINAL ESTIMATES (pre-Ellis signup, pre-Friedman reply)

```
GATE 1: Raise      = 55%
GATE 2: Customer   = 65%
GATE 3: Breakeven  = 60%
GATE 4: No Dilute  = 70%
GATE 5: ARR Target = 65% / 35% / 16%

P($10M)  = 9.8%    P($50M)  = 3.4%    P($100M) = 1.5%
```

#### REVISED ESTIMATES (Feb 25 evening -- Andy Ellis trial + Jacob Friedman reply)

**GATE 1: Raise $1M** -- P = 55% -> **62%** (+7 pts)

| Evidence                                                                  | Direction | Weight                |
| ------------------------------------------------------------------------- | --------- | --------------------- |
| Phil Venables (Ballistic VC) engaged with DD questions                    | +         | Strong                |
| Andy Ellis (YL Ventures) **signed up for trial** -- not just warm, active | +         | **Strong** (upgraded) |
| Kristen's angel network (not yet activated)                               | +         | Moderate              |
| Eric Skiff's zero-to-one firm (intro sent)                                | +         | Moderate              |
| 15 green signals from quality people                                      | +         | Moderate              |
| Jacob Friedman pointed to **SAM.gov contract opportunity**                | +         | **New**               |
| Zero revenue, zero customers                                              | -         | Strong                |
| Two-person team                                                           | -         | Moderate              |
| No proven sales motion                                                    | -         | Moderate              |

_Rationale: Andy Ellis converting from passive to active changes the fundraise dynamic. A YL Ventures partner using the product is a referenceability event for other cybersecurity VCs. Jacob's SAM.gov opportunity could yield non-dilutive government revenue, reducing dependence on the raise._

**GATE 2: First Paying Customer within 12 months** -- P = 65% -> **78%** (+13 pts)

| Evidence                                                                         | Direction | Weight                          |
| -------------------------------------------------------------------------------- | --------- | ------------------------------- |
| **Andy Ellis on Starter trial** -- 48hr after launch, specific +guards email tag | +         | **Strong (NEW)**                |
| Brent Foster (TD Bank) technical engagement                                      | +         | Strong                          |
| Government vertical 100% response rate (3/3)                                     | +         | Strong                          |
| **Jacob Friedman: SAM.gov opportunity + CSE intro + P1 path**                    | +         | **Strong (NEW)**                |
| LinkedIn DM 50% response rate (8/16)                                             | +         | Moderate                        |
| 18 high-score prospects un-contacted                                             | +         | Moderate                        |
| Product works (428 tests, live on Marketplace)                                   | +         | Moderate                        |
| $499 Starter bridges $0-$2K gap                                                  | +         | Moderate                        |
| **Delivery plan scoped** (PR #10, tasks assigned to Igor)                        | +         | **New**                         |
| ~~Zero willingness-to-pay evidence~~ **One trial signup from a domain expert**   | ~~        | **(Flipped from - to neutral)** |
| Enterprise sales cycle 3-6 months                                                | -         | Moderate                        |

_Rationale: This is the biggest shift. The previous model had "zero willingness-to-pay evidence" as a strong negative. Andy Ellis proactively signing up for a trial flips that. It is not yet payment, but it is demonstrated product interest from exactly the persona we target. Combined with Jacob's government contract path (government buyers can move faster than enterprise on small contracts), the customer gate probability jumps significantly. The delivery plan (PR #10) also matters -- we now have a scoped path to deliver what the Starter tier promises._

**GATE 3: Breakeven within 18 months** -- P = 60% -> **65%** (+5 pts)

| Evidence                                         | Direction | Weight              |
| ------------------------------------------------ | --------- | ------------------- |
| 97-99% margins = low breakeven threshold         | +         | Strong              |
| Model shows M4-M11 breakeven in all scenarios    | +         | Moderate            |
| $800K+ preserved even in bear case               | +         | Moderate            |
| **Government contract path = larger deal sizes** | +         | **New**             |
| Sales velocity completely unproven               | -         | Strong (still true) |
| Churn rate unknown                               | -         | Moderate            |

_Rationale: Modest upgrade. Government contracts (Jacob's path) typically have larger deal sizes and longer retention than startup SaaS. One government Org contract at $12K/mo = 24 Starter customers. But sales velocity remains unproven so the upgrade is conservative._

**GATE 4: No Further Dilution** -- P = 70% -> **72%** (+2 pts)

| Evidence                                | Direction | Weight   |
| --------------------------------------- | --------- | -------- |
| Breakeven preserves $700-900K of raise  | +         | Strong   |
| Reinvestment funds growth organically   | +         | Strong   |
| **SAM.gov = non-dilutive revenue path** | +         | **New**  |
| May need bridge if breakeven delayed    | -         | Moderate |

_Rationale: SAM.gov and government contracts are non-dilutive revenue. If Jacob's path converts, it reduces the need for a bridge round. Small upgrade._

**GATE 5: Reach Target ARR** (CORRECTED for cybersecurity multiples)

The corrected multiples (15x early -> 20x growth -> 25x scale) mean
the ARR thresholds for each exit target are 2-2.5x lower than
the original generic-SaaS estimates.

_NOTE (Mar 2): Updated to 40% stake (post-raise). 8% hire pool enables staircase growth (revenue-gated hiring). 30x strategic acquirer multiple added._

| Target                             | ARR Needed (40% stake)      | P (given Gates 1-4)                                                                                                                                                                                                                                                               | Reasoning |
| ---------------------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| $1.67M ARR = $10M to David at 15x  | **75%**                     | Staircase BASE model hits this by M12. If you passed Gates 1-4, reaching $1.67M is nearly a consequence. Three independent pipelines (enterprise + government + PE portfolio).                                                                                                    |
| $6.25M ARR = $50M to David at 20x  | **52%** given $10M achieved | Staircase BASE model reaches ~$6.25M by M18. Government contracts + PE distribution provide large batch deals. One PE firm with 20 portcos at $10K/yr = $200K ARR from a single relationship. UPGRADED from 48% -- PE distribution channel adds a third independent scaling path. |
| $8.33M ARR = $100M to David at 30x | **60%** given $50M achieved | Strategic acquirer (Vanta/ServiceNow/MSFT) pays 30x. Staircase BASE model hits $8.33M by M20. Bear case M40. Revenue-gated hiring from 8% pool means no further dilution.                                                                                                         |

### Revised Composite Probabilities (v3 -- corrected multiples)

```
ORIGINAL (generic SaaS multiples):
P($10M to David)  = 0.55 x 0.65 x 0.60 x 0.70 x 0.65 = 9.8%
P($50M to David)  = 9.8% x 0.35                        = 3.4%
P($100M to David) = 3.4% x 0.45                        = 1.5%

v2 (Ellis signup + Friedman reply, still wrong multiples):
P($10M to David)  = 0.62 x 0.78 x 0.65 x 0.72 x 0.68 = 15.4%
P($50M to David)  = 15.4% x 0.38                       = 5.9%
P($100M to David) = 5.9% x 0.48                        = 2.8%

v3 (corrected multiples, 45% stake -- SUPERSEDED):
P($10M)  = 0.62 x 0.78 x 0.65 x 0.72 x 0.78 = 17.6%
P($50M)  = 17.6% x 0.52                       = 9.2%
P($100M) = 9.2% x 0.65                        = 6.0%

v4 (corrected multiples, 37.5% stake -- SUPERSEDED):
P($10M to David)  = 0.62 x 0.78 x 0.65 x 0.72 x 0.75 = 16.9%
P($50M to David)  = 16.9% x 0.48                       = 8.1%
P($100M to David) = 8.1% x 0.58                        = 4.7%

v5 CURRENT (+ PE distribution channel as third scaling path):
P($10M to David)  = 0.62 x 0.78 x 0.65 x 0.72 x 0.75 = 16.9%
                    Raise  Cust   B/E    NoDil  ARR($1.78M@15x)
                    (Gates 1-4 unchanged, Gate 5a unchanged)

P($50M to David)  = 16.9% x 0.52                       = 8.8%
                    ($10M path) x (scale $1.78M -> $6.67M ARR)
                    (UPGRADED from 0.48 -- PE distribution adds
                     batch customer acquisition path)

P($100M to David) = 8.8% x 0.60                        = 5.3%
                    ($50M path) x (scale $6.67M -> $10.67M ARR)
                    (UPGRADED from 0.58 -- at this scale PE
                     distribution is a proven growth engine)

Note: v5 upgrades are concentrated in Gate 5b/5c (scaling
probabilities) because the PE distribution channel primarily
affects growth velocity, not the initial customer/raise gates.
Gates 1-4 are unchanged from v4.

The PE channel does NOT help Gates 1-2 (PE firms invest in
proven revenue, not pre-seed startups). It helps Gates 5b/5c
because one PE deal = 20-50 customers in a batch. This is
the difference between linear sales and batch distribution.
```

### Revised Probability Ranges (v5)

| Outcome            | Original | v2 (signals) | v3 (multiples) | v4 (37.5%) | **v5 (+PE channel)**     | vs Base Rate      |
| ------------------ | -------- | ------------ | -------------- | ---------- | ------------------------ | ----------------- |
| **$10M to David**  | 9.8%     | 15.4%        | 17.6%          | 16.9%      | **16.9%** (range 12-22%) | 6-7x base rate    |
| **$50M to David**  | 3.4%     | 5.9%         | 9.2%           | 8.1%       | **8.8%** (range 6-13%)   | 9-13x base rate   |
| **$100M to David** | 1.5%     | 2.8%         | 6.0%           | 4.7%       | **5.3%** (range 3-9%)    | 11-30x base rate  |
| **$0 to David**    | ~85%     | ~78%         | ~75%           | ~76%       | **~76%** (range 70-82%)  | Base rate: 90-95% |

### Why the Scaling Probabilities Keep Improving

Five compounding updates across v1-v5:

| Outcome | Original -> v5 | Total Improvement  |
| ------- | -------------- | ------------------ |
| $10M    | 9.8% -> 16.9%  | **+72%** relative  |
| $50M    | 3.4% -> 8.8%   | **+159%** relative |
| $100M   | 1.5% -> 5.3%   | **+253%** relative |

The $100M scenario improved the most because it benefits from ALL FOUR
compounding factors:

1. Lower ARR threshold (25x vs 10x = 2.5x less revenue needed)
2. Growth from $6.67M to $10.67M is only 1.6x (was $11M -> $22M = 2x)
3. PE distribution provides batch customer acquisition (20-50 per deal)
4. Three independent scaling paths (enterprise + gov + PE portfolio)

**What changed and why (v1 through v5):**

1. Andy Ellis trial signup flipped "zero WTP evidence" (Gate 2: +13 pts)
2. Jacob Friedman's government path added independent customer channel (Gates 2,3)
3. Corrected cybersecurity multiples (15-25x vs 6-10x) halved the ARR thresholds (Gate 5a)
4. Equal co-founder equity (37.5/37.5) strengthens investor confidence (Gates 1-3)
5. PE distribution channel adds batch scaling path (Gate 5b/5c: +4/+2 pts)

**What did NOT change:** Andy Ellis has not paid. Sales velocity unproven.
Churn unknown. Product gaps need shipping (PR #10). PE channel requires
first customer proof before activation. The probability of $0 is still the
single most likely outcome at ~76%. These are honest odds, not certainties.

**Key insight:** The zero-customer gap is now a trial-to-conversion gap.
The ARR targets at 15-25x multiples are achievable within the BASE model
timeline. The single highest-leverage action: **deliver PR #10 so Andy
Ellis converts from trial to paid.** That one event triggers a cascade:
customer proof -> investor credibility -> raise velocity -> PE channel
activation -> batch growth -> everything else.

### Alternative Path: Strategic Acquisition Premium (Wiz-Class Event)

The base model already uses cybersecurity multiples (15-25x).
But strategic acquisitions (Wiz by Google = 45-65x) show that
category-defining cybersecurity with unique IP can command 2-3x
the market multiple. If a Vanta, Drata, Palo Alto, or Google
decides to BUY artifact governance rather than build it:

| Outcome        | Market Multiple (base)    | Strategic Premium (35-45x)  | Adjusted P |
| -------------- | ------------------------- | --------------------------- | ---------: |
| $10M to David  | 16.9% at 15x ($1.78M ARR) | Need only $0.76M ARR at 35x |    **20%** |
| $50M to David  | 8.1% at 20x ($6.67M ARR)  | Need only $3.33M ARR at 40x |    **12%** |
| $100M to David | 4.7% at 25x ($10.67M ARR) | Need only $5.93M ARR at 45x |     **8%** |

This is the "Wiz scenario" -- a strategic buyer pays a premium for
the cognitive probe IP, the crypto proof chain, and the compliance
mappings, rather than building them in-house. At $5.93M ARR with 45x,
David nets $100M. The BASE model hits $5.8M ARR by M24.

---

## CATALYSTS: EU AI ACT + CHRIS HOOD BOOK + JUNE RELEASE

### The Regulatory Forcing Function

The EU AI Act enforcement timeline creates a hard deadline that converts
"nice to have" governance into "must have" compliance:

```
ALREADY IN FORCE:
  Feb 2, 2025   -- Prohibited AI practices banned
  Aug 2, 2025   -- GPAI model obligations (transparency, copyright)

COMING:
  Aug 2, 2026   -- HIGH-RISK AI SYSTEMS must comply (Article 6)
                    This is the BIG one. Affects: hiring AI, credit scoring,
                    law enforcement, critical infrastructure, medical devices,
                    autonomous vehicles, education assessment systems.
  Aug 2, 2027   -- Remaining provisions (AI in regulated products)
```

**What Aug 2, 2026 requires for high-risk AI deployers:**

- Risk management system (Article 9)
- Data governance and management (Article 10)
- Technical documentation (Article 11)
- Record-keeping / logging (Article 12)
- Transparency and provision of information to deployers (Article 13)
- Human oversight measures (Article 14)
- Accuracy, robustness, and cybersecurity (Article 15)

**What this means for GuardSpine:** Evidence bundles are EXACTLY what
Articles 11-13 require -- tamper-proof documentation of what the AI
reviewed, what it found, what risk tier it assigned, and who approved it.
Cognitive probes (Logan's 55 patents) address Article 15 directly --
proving the model was confident, not guessing. No competitor produces
this level of machine-verifiable evidence.

### The June 2026 Release Plan

**Target: Ship EU AI Act compliance release in June 2026 -- two months
before Aug 2 enforcement.** This gives customers time to deploy and
configure before the deadline hits.

June release must include:

- [ ] **EU AI Act rubric** (map Articles 9-15 to guard lane checks)
- [ ] **Risk classification helper** (is this deployment "high-risk" per Annex III?)
- [ ] **Compliance evidence export** (Articles 11-13 formatted for EU regulators)
- [ ] **DORA + EU AI Act cross-mapping** (companies subject to both get unified evidence)
- [ ] **Landing page: EU AI Act compliance page** (SEO play -- capture search traffic as Aug 2 approaches)
- [ ] **Blog/content: "EU AI Act Compliance Checklist" gated content** (lead magnet)

**Why June, not August:** First-mover advantage. Every competitor will
ship something in July/August. We ship in June, capture early press
coverage, rank in search before the rush, and give customers 60 days
of runway. The company that helps you prepare beats the one that shows
up on deadline day.

**Marketing timeline:**

```
Apr 2026  -- EU AI Act content starts (blog posts, LinkedIn, SEO)
May 2026  -- Preview/beta of EU AI Act rubric to existing users
Jun 2026  -- SHIP: Full EU AI Act compliance release
Jul 2026  -- PR push: "Are you ready for Aug 2?" campaign
Aug 2, 2026 -- Enforcement day. Capture inbound demand.
```

### Chris Hood Book Release Coordination

Chris Hood's book launches ~April 2026 (exact date TBD from Chris).
Chris is advisor to GuardSpine, connected to Google, runs Noematic AI.

**Coordination plan:**

- GuardSpine featured as a case study or reference in the book (confirm with Chris)
- Co-promoted launch event: Chris presents, GuardSpine demo shown
- LinkedIn amplification: both networks cross-promote
- Chris's audience = enterprise decision-makers = our buyer persona
- Timeline aligns perfectly: book launch (April) -> EU AI Act content (May) -> June release

**The narrative arc (Apr-Aug 2026):**

```
April    -- Chris Hood book launch + GuardSpine mention
           = credibility signal to enterprise buyers
May      -- EU AI Act content + early access to compliance rubric
           = thought leadership + lead generation
June     -- BIG RELEASE: EU AI Act compliance features ship
           = product launch event, press coverage
July     -- "60 days to compliance" campaign
           = urgency-driven demand generation
August   -- EU AI Act enforcement
           = inbound capture, late adopters scrambling
```

This is a four-month coordinated campaign where each event amplifies
the next. Chris Hood provides the enterprise credibility. The EU AI Act
provides the urgency. The June release provides the product. The timing
is natural, not forced.

### Impact on Probability Model

The EU AI Act enforcement does not change Gates 1-4 (those are near-term
actions happening in the next 90 days). It changes **Gate 5** (scaling to
target ARR) because it creates a regulatory forcing function that
converts the governance market from voluntary to mandatory.

After Aug 2, 2026, every company deploying high-risk AI in Europe MUST
produce the kind of evidence GuardSpine generates. This is not "might
buy" -- it is "must buy or face penalties." The European AI Office can
impose fines of up to 35M EUR or 7% of global turnover.

This is not reflected in the current v5 probabilities because the June
release has not shipped yet and the compliance features are not built.
Once the EU AI Act rubric ships, Gate 5 probabilities should be
re-evaluated upward. Estimated impact:

| Gate 5 scenario   | v5 current | Post-June-release estimate | Reasoning                                             |
| ----------------- | ---------- | -------------------------- | ----------------------------------------------------- |
| $1.78M ARR (15x)  | 75%        | 80-85%                     | Mandatory compliance creates pull demand              |
| $6.67M ARR (20x)  | 52%        | 58-62%                     | EU enforcement + PE defense portcos + gov channel     |
| $10.67M ARR (25x) | 60%        | 65-68%                     | At scale, regulatory forcing function is the tailwind |

**But we do not update the composite until the release ships.** Projecting
a release we have not built would be the same error as counting Andy
Ellis as a paying customer before he pays. Ship first, update second.

---

## WHAT MOVES THE NEEDLE MOST

### Sensitivity Analysis: Impact of Each Gate on Probabilities

(Updated from v5 baseline: $10M=16.9%, $50M=8.8%, $100M=5.3%)

| If This Improves...                 | From -> To                               | $10M P Becomes   | Delta                |
| ----------------------------------- | ---------------------------------------- | ---------------- | -------------------- |
| P(raise)                            | 62% -> 80%                               | 21.8%            | +4.9 pts             |
| P(first customer)                   | 78% -> 90%                               | 19.5%            | +2.6 pts             |
| P(breakeven)                        | 65% -> 80%                               | 20.8%            | +3.9 pts             |
| P(no dilution)                      | 72% -> 90%                               | 21.1%            | +4.2 pts             |
| P(reach $1.78M ARR)                 | 75% -> 90%                               | 20.3%            | +3.4 pts             |
| **Andy Ellis converts to paid**     | Gate 2: 78% -> 90%, Gate 1: 62% -> 70%   | **24.2%**        | **+7.3 pts**         |
| **Gov contract lands (Jacob)**      | Gate 2: 78% -> 88%, Gate 3: 65% -> 75%   | **22.6%**        | **+5.7 pts**         |
| **Both Ellis + Gov land**           | G1:70%, G2:92%, G3:75%                   | **30.1%**        | **+13.2 pts**        |
| **PE preferred vendor deal (M12+)** | Gate 5b: 52% -> 65%, Gate 5c: 60% -> 70% | $50M: **11.4%**  | **+2.6 pts on $50M** |
| **Ellis + Gov + PE all land**       | G1:70%, G2:92%, G3:75%, G5b:65%, G5c:70% | $100M: **10.5%** | **doubles $100M P**  |

**Highest-leverage actions (REVISED, next 90 days):**

1. **CONVERT ANDY ELLIS FROM TRIAL TO PAID** (+7.3 pts on $10M -- touches Gates 1 AND 2)
   - Deliver Starter experience: dashboard + Slack + CSV export + PDF reports (PR #10)
   - This is no longer "get a customer someday" -- it is "deliver for the person already in the door"
   - Andy Ellis paying = YL Ventures partner vouching for product = cascade to raise
   - One action, two gates. Highest leverage in the model.
   - ALSO unlocks PE channel: first paying customer = proof of value for operating partners

2. **CLOSE THE RAISE** (+4.5 pts to every scenario)
   - Activate Kristen's angel network (Feb 26 sync)
   - Get Eric Skiff advisory relationship (Mar 2-3 call)
   - LinkedIn DM 10 TIER1+TIER2 investor prospects (Feb 26 8:30 AM)
   - Andy Ellis paying + Phil Venables DD = strong close conditions

3. **LAND GOVERNMENT CONTRACT** (+5.7 pts via breakeven gate)
   - Jacob Friedman: SAM.gov opportunity + CSE contact + P1 access
   - Government Org at $12K/mo = replaces 24 Starters
   - Requires: CMMC/CPCSC rubrics + RHEL9 container (PR #10 P1 tasks)
   - Non-dilutive revenue reduces bridge risk (Gate 4)
   - CMMC rubric also feeds PE defense portco channel (dual purpose)

4. **CLOSE LOGAN MOU** (shifts acquisition premium path)
   - Countersign pending
   - 3-way call with Igor for schema integration
   - Cognitive probes in evidence bundles = category-defining feature

5. **ACTIVATE PE DISTRIBUTION CHANNEL** (M6-M12, +2.6 pts on $50M)
   - Requires: first paying customer + multi-tenant sponsor dashboard
   - Entry: Apply to GetProven, target vCISO firms (Emergent Security)
   - First pitch to mid-market PE operating partners (Audax, Accel-KKR)
   - One PE deal with 20 portcos at $10K/yr = $200K ARR from one relationship
   - CMMC angle: defense PE firms have the most urgent need ($100M penalties)
   - This is the growth accelerator that transforms Gate 5b/5c

---

## THE HONEST PICTURE

### What Is Working

1. **Messaging landed.** "Artifact governance, not AI governance" resonates. Kristen approved. Andy Mac validated.
2. **Product is real.** 428 tests, live GitHub Action, full UI dashboard, evidence bundles work.
3. **Quality of signals is high.** Phil Venables, Kelsey Hightower, Brent Foster at TD Bank. These are not random people.
4. **Margins are structural.** 97-99% BYOK is not a projection -- it is the architecture. Competitors cannot match this without rebuilding.
5. **Regulatory tailwind is real and has a hard deadline.** DORA enforceable since Jan 2025. **EU AI Act high-risk enforcement Aug 2, 2026** -- 5 months away. Fines up to 35M EUR or 7% of global turnover. Jacob confirms the gap from G7. Ishwar confirms from Z-Inspection. June release plan preempts enforcement by 60 days.
6. **Cognitive probes are a cornered resource.** 55 patents, 3yr exclusive. Nobody else has this.
7. **LinkedIn DM is the channel.** 50% response rate vs 4.2% email. This is the growth engine.
8. **Two catalysts are on the calendar.** Chris Hood book launch (~April) provides enterprise credibility. EU AI Act enforcement (Aug 2) creates mandatory demand. June release preempts both.

### What Is Not Working

1. **Zero paying customers.** Andy Ellis is on a free trial, not paying. This remains the single biggest risk until payment clears.
2. **Starter tier not fully deliverable.** Andy Ellis signed up for a product that is missing CSV export, PDF reports, and trend analytics. PR #10 scopes the fix -- but it is not shipped yet.
3. **No proven sales motion.** We don't know: CAC, sales cycle, close rate, churn rate. All are assumptions.
4. **Campaign attribution was broken.** dev100_feb26 UTMs weren't in messages until today's fix. 54 already-sent messages are untrackable. 46 unsent now fixed.
5. **18.75% dead clicks on site.** Something looks clickable but is not. UX friction losing visitors.
6. **Alignment audit: 33 issues, 6 critical.** Pricing ladders conflict, test counts conflict, guard lanes overclaimed, dead domains in code.
7. **Two-person team.** David + Igor cannot sell, build, support, and grow simultaneously. Hire #1 (after breakeven) is critical.

### What We Don't Know Yet

1. Is there a real buyer at $499/mo? (**Partially validated** -- Andy Ellis signed up for free trial, hasn't paid yet)
2. Will CISOs buy from a two-person startup? (Unknown, but Andy Ellis IS the CISO persona)
3. What is actual churn? (No customers = no data)
4. Does the Snyk pincher model work for governance? (Hypothesis only)
5. Can Logan's cognitive probes deliver on claims? (Unverified until live demo)
6. Will Vanta/Drata add governance features and eat our market? (Unknown timeline)
7. Can we deliver the Starter experience before Andy Ellis's interest cools? (**NEW** -- trial-to-paid window is weeks, not months)

---

## 90-DAY DECISION GATES

### Month 1 (Feb 26 - Mar 26)

| Action                                           | Owner | Success Criteria                           | Impact                                       |
| ------------------------------------------------ | ----- | ------------------------------------------ | -------------------------------------------- |
| Kristen sync #2 (Feb 26)                         | David | Share data, get angel intro timeline       | Raise probability                            |
| Reply Andy Mac (Feb 26)                          | David | C Neill intro, velocity test               | New channel                                  |
| Build 20 velocity prospects (Feb 26)             | David | Test "blocked EM" thesis                   | GTM validation                               |
| Fix pricing C-PR1 (Feb 26)                       | David | Single canonical pricing ladder            | Investor credibility                         |
| Logan MOU countersign                            | Logan | Signed MOU in hand                         | Moat locked                                  |
| 3-way call David/Igor/Logan                      | All 3 | Evidence bundle schema agreed              | Integration starts                           |
| Christopher Catoya follow-up (Mar 3)             | David | Share progress, get bio partner intro      | Network expansion                            |
| Eric Skiff call (Mar 2-3)                        | David | Advisory relationship + accelerator intros | Trial-to-paid conversion advice, NYC network |
| LinkedIn DM 10 TIER1+TIER2 investors (Feb 26 AM) | David | 5+ responses                               | Angel raise pipeline                         |
| LinkedIn DM 18 high-score unsent prospects       | David | 9+ responses (50% rate)                    | Customer pipeline growth                     |
| Apply to GetProven platform                      | David | Listed as vendor                           | PE distribution channel entry point          |

### Month 2 (Mar 26 - Apr 26)

| Action                                             | Owner       | Success Criteria                              | Impact                                              |
| -------------------------------------------------- | ----------- | --------------------------------------------- | --------------------------------------------------- |
| Angel intro from Kristen                           | Kristen     | 2-3 warm intros                               | Raise velocity                                      |
| TD Bank pilot conversation                         | David/Igor  | Brent agrees to test                          | Proof point                                         |
| Government pilot (via Jacob)                       | David/Igor  | 1 gov contract                                | Revenue + credibility                               |
| Cognitive probe demo (Logan)                       | Igor/Logan  | Live demo, verify claims                      | Moat validation                                     |
| Chris Hood book launch coordination                | David/Chris | GuardSpine in book + co-promoted launch event | Enterprise credibility + EU AI Act campaign kickoff |
| Multi-tenant sponsor dashboard spec                | Igor        | Wireframe + DB schema                         | PE channel readiness                                |
| Target 2-3 vCISO firms (Emergent, Fractional CISO) | David       | 1 conversation started                        | PE side-door entry                                  |

### Month 3 (Apr 26 - May 26)

| Action                             | Owner         | Success Criteria                                | Impact                           |
| ---------------------------------- | ------------- | ----------------------------------------------- | -------------------------------- |
| Close $1M raise                    | David/Kristen | Term sheet signed                               | Everything unlocked              |
| First paying customer              | David/Igor    | $499+/mo contract signed                        | Willingness-to-pay proven        |
| Landing page conversion fix        | David         | >2% signup rate (vs current 0%)                 | Funnel unblocked                 |
| First PE operating partner meeting | David         | 1 meeting with mid-market PE firm               | Distribution channel seeded      |
| GuardSpine SOC 2 Type II started   | David/Igor    | Audit process initiated                         | PE credibility + eat own dogfood |
| EU AI Act content plan finalized   | David         | Blog calendar, SEO keywords, gated content spec | Lead gen pipeline for Jun-Aug    |

### Month 4 (May 26 - Jun 26) -- EU AI ACT RELEASE SPRINT

| Action                                                            | Owner      | Success Criteria                         | Impact                                 |
| ----------------------------------------------------------------- | ---------- | ---------------------------------------- | -------------------------------------- |
| EU AI Act rubric (Articles 9-15 mapped to guard lanes)            | Igor       | YAML rubric complete, tested             | Core compliance feature                |
| Risk classification helper (Annex III high-risk check)            | Igor       | In dashboard, user-facing                | Differentiator vs Vanta/Drata          |
| Compliance evidence export (EU regulator format)                  | Igor       | PDF + JSON export with Article refs      | Audit-ready output                     |
| DORA + EU AI Act cross-mapping rubric                             | Igor       | Unified evidence for dual-regulated orgs | Cross-sell to finance                  |
| Landing page: EU AI Act compliance                                | David      | Live, indexed, ranking                   | SEO capture                            |
| Gated content: "EU AI Act Compliance Checklist"                   | David      | Published, email capture working         | Lead magnet                            |
| **SHIP JUNE RELEASE**                                             | David/Igor | All above deployed to production         | **Biggest product event since launch** |
| Press push: "GuardSpine ships EU AI Act compliance 60 days early" | David      | 3+ press mentions or podcasts            | Awareness spike                        |

### Month 5-6 (Jun 26 - Aug 2) -- EU AI ACT ENFORCEMENT WAVE

| Action                                        | Owner | Success Criteria                       | Impact                    |
| --------------------------------------------- | ----- | -------------------------------------- | ------------------------- |
| "60 days to compliance" campaign              | David | LinkedIn, email, content series        | Urgency-driven demand     |
| PE defense portco outreach (CMMC + EU AI Act) | David | 3 meetings with operating partners     | Batch customer path       |
| Aug 2 enforcement day: capture inbound        | David | Landing page converting, trial signups | Regulatory pull demand    |
| Re-evaluate Gate 5 probabilities              | David | v6 synthesis update if warranted       | Honest probability update |

---

## THE BOTTOM LINE

GuardSpine is a 3-5x better bet than the average pre-seed startup, but it is still a bet. The product works. The people responding are real and senior. The regulatory tailwind is genuine. The margin structure is a permanent advantage.

The single thing that transforms every probability in this document: **one paying customer.**

Everything before that is positioning. Everything after is execution.

| Outcome           | Original | v2 (signals) | v3 (multiples) | v4 (37.5%) | v5 (+PE) | **v6 CURRENT (40%, staircase)** | What It Requires                                            |
| ----------------- | -------- | ------------ | -------------- | ---------- | -------- | ------------------------------- | ----------------------------------------------------------- |
| David nets $0     | ~85%     | ~78%         | ~75%           | ~76%       | ~76%     | **~76%**                        | Fail to raise, or fail to find customers                    |
| David nets $10M+  | ~10%     | ~15%         | ~18%           | ~17%       | ~17%     | **~17%**                        | Raise + breakeven + $1.67M ARR at 15x (M12)                 |
| David nets $50M+  | ~3-5%    | ~6%          | ~9%            | ~8%        | ~9%      | **~9%**                         | All above + scale to $6.25M ARR at 20x (M18)                |
| David nets $100M+ | ~1.5-3%  | ~3%          | ~6%            | ~5%        | ~5%      | **~5%**                         | All above + scale to $8.33M ARR at 30x (M20 base, M40 bear) |

The expected value of David's stake (probability-weighted, v6 -- 40% stake, staircase model):

- 75% x $0 = $0
- 4% x $5M (small exit at 15x) = $200K
- 4% x $10M = $400K
- 4% x $20M (M17 at 15x) = $800K
- 4% x $50M = $2.0M
- 4% x $100M = $4.0M
- 3% x $120M (M23 at 25x) = $3.6M
- 2% x $250M (M40 at 25x) = $5.0M
- **Expected value: ~$16.0M**

**Igor gets the same expected value.** Combined founder EV = ~$32.0M.

Note: v6 stake decreased from 44.1% to 40% (8% allocated to hire pool), but
staircase model accelerates timelines. The 30x strategic acquirer multiple
means David $100M at only $8.33M ARR (vs $9.07M at 25x with old cap table).
Net effect: slightly lower per-dollar ownership, faster path to target ARR.

### What Changed Across Five Revisions

```
                Original    v2 (signals)    v3 (multiples)   v4 (37.5%)   v5 (+PE)    v6 (40%+staircase)
David's stake   45%         45%             45%              37.5%        37.5%       40%
P($10M)         9.8%        15.4%           17.6%            16.9%        16.9%
P($50M)         3.4%         5.9%            9.2%             8.1%         8.8%
P($100M)        1.5%         2.8%            6.0%             4.7%         5.3%
P($0)          ~85%         ~78%            ~75%             ~76%         ~76%
EV (David)     $6.25M       $16.4M          $14.2M           $13.1M      $17.2M
EV (Igor)       --           --              --              $13.1M      $17.2M
EV (combined)  $6.25M       $16.4M          $14.2M           $26.2M      $34.4M
```

v5 adds the PE portfolio distribution channel as a third independent
scaling path. This primarily affects Gate 5b/5c (growth from $1.78M
to $6.67M to $10.67M ARR) because PE deals provide batch customer
acquisition: one operating partner relationship = 20-50 portfolio
company deployments. The research (3 PDFs in Desktop/guardspine/research/)
confirms this is a real but early-stage distribution model -- 52% of
large PE firms have mandatory preferred vendor programs, but execution
takes 12-18 months and requires proof of value first.

**The distribution is still skewed: most likely outcome is still $0.**
But the probability mass shifted meaningfully toward the upside
scenarios for five compounding reasons:

1. **Operational risk reduced** -- Andy Ellis trial + Jacob Friedman
   government path = two independent channels to first customer
2. **Exit thresholds halved** -- 15-25x cybersecurity multiples mean
   $1.78M ARR (not $3.7M) delivers $10M to David
3. **Scaling risk reduced** -- $100M requires $10.67M ARR (not $22M),
   which the BASE model reaches by M36
4. **Team alignment maximized** -- Equal co-founder equity eliminates
   a top-5 reason angel investors pass
5. **Distribution channel identified** -- PE portfolio deployment provides
   batch customer acquisition (20-50 per deal) that no competitor has
   built for yet. Vanta only started hiring for PE partnerships in 2025.

The zero-customer gap is now a trial-to-conversion gap.
The ARR targets are achievable within the BASE model timeline.
Three independent scaling paths exist (enterprise + gov + PE portfolio).

**Next move: Ship PR #10 (Starter MVP) so Andy Ellis converts
from trial to paid. That single event is worth +7.3 percentage
points on the $10M probability AND unlocks the PE distribution
channel (operating partners need proof of value before deploying
across their portfolio). Everything cascades from first customer.**

---

## APPENDIX: PE DISTRIBUTION RESEARCH SOURCES

Three research documents in `Desktop/guardspine/research/`:

1. **"Private Equity as a Distribution Channel for Cybersecurity and Compliance Automation"** (10 pages)
   Key findings: Blackstone, THL, Vista, Thoma Bravo, Hg all have portfolio-scale
   deployment machinery. Partner-then-deploy is the dominant model (not equity
   investment). Sponsor buys standardized governance reporting, not feature-by-feature tools.

2. **"PE as a Distribution Channel: What a Compliance Startup Needs to Know"** (8 pages)
   Key findings: 52% of PE firms >$25B AUM have mandatory preferred vendor programs.
   95% require basic technical controls. Vanta only began PE partnerships hiring in 2025.
   CMMC creates most urgent PE compliance need. Entry through vCISO firms + GetProven.

3. **"The Private Equity Distribution Engine"** (13 pages)
   Key findings: PE-backed companies outnumber public 4:1 (14,300 vs 3,550).
   Cybersecurity breach reduces deal value by $2.1-10M. RegScale deployed to PE firm
   in "mere weeks." X-Analytics deployed across 150+ portcos reducing $1B in cyber risk.
   Hg acquired AuditBoard for $3B. Vista's OneVista program cross-sells across 90+ portcos.
