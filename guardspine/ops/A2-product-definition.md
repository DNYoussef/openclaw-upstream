# GuardSpine -- Product Definition (Draft v1)

**Prepared by:** David Youssef, CEO / Igor Malovitsa, CTO
**Date:** February 20, 2026
**Purpose:** One round of refinement before Kristen's intro to Eric's firm and angel investors
**Source:** Feb 19, 2026 meeting (David, Igor, Kristen Hengst Smith)

---

## 1. What Is It?

**GuardSpine is an open-core governance layer that creates tamper-proof audit trails for every code change -- whether written by humans or AI.**

This is not an AI tool. This is a governance tool that happens to use AI.

The distinction matters. Code review tools (Greptile, CodeRabbit, Linear B) help developers write better code. GuardSpine does something different: it produces a cryptographic judgment receipt -- a tamper-proof record proving that every change was reviewed, evaluated, and logged. That record is admissible as evidence because it is mathematically impossible to alter after the fact.

> "You are governance, not coding. You sit with engineering but only because engineering happens to be the thing that needs the governance." -- Kristen Hengst Smith, Feb 19 2026

> "A proprietary auditing infrastructure doesn't make sense. It almost needs to be open source." -- David Youssef
> "It needs to be a third party." -- Kristen Hengst Smith

The open-source core is a structural moat, not a liability. A governance tool that audits code must be independently verifiable. Proprietary audit trails defeat the purpose. Open source makes the audit trustworthy. The business is built on the layers above: multi-model AI deliberation, enterprise integrations, compliance reporting, and white-glove support.

---

## 2. Who Is It For?

**Primary buyer: CISO or Chief Compliance Officer at mid-market to enterprise companies (500+ engineers) in regulated industries -- finance, healthcare, insurance, legal.**

The buyer is NOT the developer. Developers experience the pain, but CISOs hold the budget.

> "VP of Engineering doesn't necessarily have a budget. [...] You have to be able to point to the stack of cash at someone's office and say, that would be for us." -- Kristen Hengst Smith

This follows the pharmaceutical model: developers are the patients, CISOs are the doctors. The CTA to developers is "ask your CISO about GuardSpine." The CTA to CISOs is "here's proof your AI-generated code is governed."

**Why this buyer:**

- CISOs exist at every regulated company
- They control compliance/audit budgets ($500K-$5M/yr at Tier 1 banks)
- Their budgets are growing, not shrinking (EU AI Act, DORA, SOC2, HIPAA)
- The line item already exists -- DevSecOps tooling or GRC/compliance software
- The purchase trigger is concrete: audit finding, regulatory deadline, board mandate

**End users:** Developers, DevOps engineers, platform engineering teams. They install the GitHub Action. They see the results. They experience the value daily. But they do not sign the check.

**Target company profile:**

- 500+ engineers (enough code volume that manual review is failing)
- Regulated industry (external compliance pressure creates urgency)
- Active AI adoption (AI-generated code accelerates the governance gap)
- Existing DevSecOps budget line (budget exists, not creating new category)

---

## 3. What Does It Do?

**It gives CISOs proof that every code change was reviewed, approved, and logged in a way that cannot be tampered with -- without slowing down engineering.**

The outcome is insurance. GuardSpine is insurance against the question: "Who is liable when AI-generated code causes a breach?"

> "Someone needs to take accountability for decisions. There needs to be an audit trail. [...] If you try to edit any of the audit logs, there's a verifier that's completely offline. You can prove that this happened and no one has messed with the logs. It is literally mathematically impossible, which is why it's admissible in court." -- David Youssef

**What the CISO gets:**

- Tamper-proof audit trail for every code change (human or AI-authored)
- Judgment receipts that prove review happened, who/what reviewed it, and what was decided
- Compliance evidence that maps to DORA, SOC2, HIPAA, and EU AI Act requirements
- Audit prep reduced from weeks to minutes (evidence bundles are pre-generated)

**What the developer gets:**

- AI-powered code review that catches logic risks, not just syntax errors
- Works with their existing models -- Claude, GPT, Gemini, or local Ollama
- 5-minute install as a GitHub Action in their existing CI/CD pipeline
- No workflow disruption -- sits in the pipeline they already use

**What it is NOT:**

- Not a code review tool (it governs; it does not write or fix code)
- Not an AI governance platform (it governs artifacts, regardless of who produced them)
- Not a replacement for Vanta/Drata (it produces evidence; they aggregate compliance)

---

## 4. What Is the Initial Offering?

### The Wedge: Code Governance Only

Start with one lane: code changes via GitHub Actions. Other artifact types (documents, images, design files) come 6 months later, once the code governance wedge is established.

> "When it starts to overwhelm everyone else, the programmers in the company can already say, oh, we've been using this system for six months." -- David Youssef
> "I think that's fantastic. Because basically what you're describing, if you're doing everything, you're describing a category that doesn't exist." -- Kristen Hengst Smith

### Pricing Tiers

The open-source review engine (risk-tiered L0-L4 deliberation, multi-model consensus, evidence bundles) is the same for every customer -- free or paid. It runs in the customer's own CI/CD pipeline with their own API keys (BYOK). The paid tiers sell the **platform layer**: dashboard, integrations, rubric management, compliance reporting, and support.

| Tier           | Price                  | What You Get                                                                                                                                                                                                                    | Target Buyer                                                       |
| -------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| **FREE**       | $0/mo                  | Open-source GitHub Action. Full review engine (risk-based model escalation, deliberation, consensus). Judgment receipts. Community rubric packs. Self-managed, no cloud.                                                        | Individual developers, small teams. Adoption wedge.                |
| **STARTER**    | $499/mo ($4,788/yr)    | GuardSpine Cloud: dashboard (PR history, risk analytics), Slack notifications, evidence management (search, export JSON+CSV), standard rubric library. Up to 10 repos, 25 contributors. Email support. 30-day free trial.       | Teams of 5-25 devs exploring governance. The "ask your CISO" tier. |
| **TEAM**       | $2,000/mo ($19,200/yr) | Everything in Starter, plus: custom rubric builder, Jira + Microsoft Teams integration, custom escalation workflows, SOC2/DORA/HIPAA compliance report templates, unlimited repos and contributors, priority support (4hr SLA). | Teams of 25-100 devs with formal governance requirements.          |
| **ORG**        | $12,000/mo ($120K/yr)  | Everything in Team, plus: multi-lane guards (code + docs + images), RBAC, ServiceNow integration, SSO/SAML, advanced compliance dashboards, dedicated CSM.                                                                      | Mid-market companies with compliance requirements.                 |
| **ENTERPRISE** | $50,000/mo (Custom)    | Everything in Org, plus: on-prem/airgap deployment with Ollama models, custom integrations, 99.9% SLA, compliance consulting, custom training.                                                                                  | Tier 1 banks, insurance, healthcare systems.                       |

### Pricing Context

The BYOK (Bring Your Own Keys) model means customers use their own LLM API keys. GuardSpine never touches AI inference costs. This produces structural gross margins of 97%+ at the BYOK headline level -- significantly better than most SaaS companies that carry compute costs.

> **Fully loaded margin note**: 87-91% after infrastructure, hosting, CI/CD, and operational overhead allocation. The 97%+ figure reflects pure BYOK unit economics before platform opex.

**Competitive pricing position:** Starter at $4,788/yr sits just below Drata Foundation ($7,500/yr) and Vanta Core ($10,000/yr). Team at $19,200/yr sits at the low end of DevSecOps tooling (Snyk $24-100K, Checkmarx $50-200K). Easy budget fit.

### Bridging the Gap

The Starter tier at $499/mo bridges the free-to-Team cliff. It sits just below compliance tool entry points while positioning above developer tool pricing (CodeRabbit $120/mo, Greptile $300/mo for 10 devs). Platform fee (not per-seat) signals governance category, consistent with Vanta/Drata pricing model. BYOK means we do not meter model usage -- gating by model count would be fake scarcity.

The two-website experiment (developer-facing vs CISO-facing landing pages) will validate which buyer persona converts first. Both pages show the same pricing with different framing. See `eric-prep/10-pricing-bridge-spec.md` for the full rationale.

---

## 5. Where Does the Money Come From?

**Primary budget line: DevSecOps Tooling / Compliance Audit**

Two possible homes in the buyer's P&L:

| Budget Line                                | Department                 | Owner                          | When This Fits                                                                    |
| ------------------------------------------ | -------------------------- | ------------------------------ | --------------------------------------------------------------------------------- |
| **DevSecOps Tooling** (COGS)               | Engineering / Platform Eng | VP DevSecOps, Head of Platform | GuardSpine is part of the product delivery pipeline -- every PR passes through it |
| **GRC / Compliance Software** (Admin/OpEx) | Risk / Compliance / Legal  | CISO, Chief Risk Officer       | GuardSpine is audit/compliance infrastructure -- governance overhead              |

> "Two options. The company can choose to declare it as COGS or administrative. Both make sense." -- Igor Malovitsa

**Recommended lead:** Compliance/audit budget line, because:

1. CISOs control this budget (the buyer we're targeting)
2. It exists at every regulated company (repeatable sales motion)
3. It is growing -- regulatory pressure from DORA, EU AI Act, SOC2, HIPAA
4. DevOps tool budgets are getting squeezed by AI; compliance budgets are expanding

**The pitch to the CFO:** GuardSpine reduces audit preparation from weeks to minutes. The evidence bundles are pre-generated with every code change. When the auditor asks "show me the governance trail for this deployment," the answer is one API call, not three weeks of forensic archaeology.

---

## Competitive Positioning

### What We Are Not

GuardSpine is NOT competing in code review. Code review is a shrinking category being compressed by AI. Every code review tool (Greptile, CodeRabbit, Linear B) is racing to the bottom as AI makes basic review a commodity.

### Where We Sit

GuardSpine competes adjacent to governance and compliance:

| Category                        | Players                        | GuardSpine Relationship                                                 |
| ------------------------------- | ------------------------------ | ----------------------------------------------------------------------- |
| Code Review (shrinking)         | Greptile, CodeRabbit, Linear B | NOT competing. Different category entirely.                             |
| Compliance Automation (growing) | Vanta, Drata                   | Complementary. We produce evidence; they aggregate compliance posture.  |
| Endpoint Security (large)       | CrowdStrike                    | Adjacent. Similar buyer (CISO), similar budget line, different problem. |
| AppSec Testing                  | Snyk, Checkmarx, Veracode      | Parallel. They find vulnerabilities; we prove governance happened.      |

### Moats (Seven Powers Framework)

1. **Network effect:** Every participant in the governance network makes the audit trail more valuable. More reviewers, more rubric packs, more evidence patterns.
2. **Counter-positioning:** Incumbents cannot open-source their audit trail without cannibalizing their proprietary model. Open-core governance is structurally impossible for them to copy.
3. **Switching costs:** Once an organization builds 6+ months of audit history on GuardSpine, switching means abandoning the evidence trail. Compliance teams will not accept that.
4. **Cornered resource (potential):** Exclusive partnership with Proprioceptive AI (Logan) for model confidence scoring. Provisional patents with a 9-month window. Meta is next in line if the partnership doesn't close. This is the only moat Kristen got genuinely excited about.
5. **Process power:** AI-native compound automation loop. $1K/month API budget per team member produces 3-4x output multiplier. This compounds over time in ways traditional teams cannot match.

---

## The Wedge Strategy

**Phase 1 (Now -- Month 6): Code governance only**

- GitHub Action for PR review and judgment receipts
- Single artifact type: code
- Single platform: GitHub
- Free tier drives adoption; Team/Org tiers drive revenue

**Phase 2 (Month 6-12): Multi-artifact expansion**

- Document governance (contracts, policies, SOPs)
- Image/design governance (creative assets, marketing materials)
- By this point, code governance customers are locked in and expanding naturally

**Phase 3 (Month 12-18): Platform**

- Full artifact governance across code, docs, images, and more
- Enterprise compliance reporting (SOC2, HIPAA, DORA dashboards)
- Integration marketplace (community-built connectors)

The sequence matters. Start narrow, prove the model, expand from strength.

---

## Proof of Interest

### Current Signals

| Signal                           | Who                               | Status                                                                                  | Significance                                                                                                                                                         |
| -------------------------------- | --------------------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| VP Eng response to cold outreach | Brent Foster, TD Bank             | Asked technical differentiation question (in-toto vs GuardSpine). David replied Feb 17. | A VP of Engineering at a Tier 1 bank responded to a cold email from an unknown founder. That does not happen without real pain.                                      |
| VC due diligence questions       | Phil Venables, Ballistic Ventures | Asked 3 DD questions (team, pipeline, ICP). David replied same day.                     | Ballistic is a cybersecurity-focused VC. Phil was 17yr CISO at Goldman Sachs, then CISO of Google Cloud. He asked DD questions -- not "interesting, keep me posted." |
| Abnormal cold response rate      | Multiple                          | 4.8% response rate on cold outreach (42 sent, 2 substantive responses)                  | Industry average for cold outreach to executives is 1-3%. 4.8% from unknown founders selling a pre-revenue product is a market signal.                               |

> "The fact that they're answering is a sign of desperation in the market." -- David Youssef
> "If you could penetrate TD Bank at all at any scale, you go from -- like a thousandfold more desirable to investors." -- Kristen Hengst Smith

### What's Missing

- Zero paying customers
- Zero pilots installed at external companies
- No email signup data (landing pages not yet built)
- No documented sales cycle (no prospect has gone through demo -> eval -> close)

This is the gap. Everything else -- the product, the tech, the moats, the positioning -- is strong. The proof of interest is the bridge between "interesting project" and "investable business."

---

## Financial Snapshot (from R5 Analysis)

| Metric                     | Value                                                 | Source                                                 |
| -------------------------- | ----------------------------------------------------- | ------------------------------------------------------ |
| Gross margins              | 97-99% by tier (BYOK model)                           | P&L Sheet 3 + pricing bridge spec                      |
| Monthly burn (post-raise)  | $26.5K/mo                                             | Burn decomposition (Kristen equity-only, no AI budget) |
| Runway at $1M raise        | 37+ months                                            | Cash flow model                                        |
| Breakeven point            | 55 Starter OR 30 Starter + 3 Team OR 14 Team OR 3 Org | Breakeven analysis                                     |
| Y1 realistic target (Base) | 30 Starter + 8 Team + 2 Org = $55K MRR, $660K ARR     | Revenue build-up                                       |
| Y1 realistic target (Bear) | 10 Starter + 2 Team = $9K MRR, $108K ARR              | Scenario bounds                                        |
| Founder salaries           | $10K/mo each (agreed)                                 | Burn decomposition                                     |
| AI agent APIs              | $2K/mo (2 people x $1K/mo -- Claude/GPT/Gemini)       | R&D infra line                                         |

**The strongest number:** BYOK means zero LLM inference cost. The single largest expense for AI-powered SaaS companies does not exist for GuardSpine. This is structural, not temporary.

**The most important number:** Breakeven at 55 Starter customers, or a blend of 30 Starter + 3 Team. The Starter tier creates more paths to breakeven than the old 4-tier model. With $1M raised and $26.5K/mo burn, the company has 37+ months of runway.

---

## Next Steps (From Feb 19 Meeting)

1. **Refine this product definition** -- this document (send to Kristen by Feb 23)
2. **Build two landing pages** with email capture -- developer-facing vs CISO-facing (A/B test to validate buyer persona)
3. **Get proof of interest** -- push for pilots, email signups, logos
4. **Kristen intro to Eric's firm** -- zero-to-one technical mentorship and potential pilot connections
5. **Research funding options** -- VC, PE distribution hack, crowdsource, deferred equity, YC

---

## Ready for Eric -- Pre-Intro Checklist

Before Kristen makes the introduction to Eric's firm, the following should be true:

- [x] Product definition document written (this document)
- [x] Pricing bridge tier designed (Starter $499/mo -- see eric-prep/10-pricing-bridge-spec.md)
- [ ] Product definition reviewed and approved by Kristen
- [ ] Two landing pages live with email capture, pricing, and analytics
- [ ] Initial signup data (even 3-5 days of data is a signal)
- [ ] Competitive landscape one-pager with numbers (Vanta, Drata, CrowdStrike ARR, customer counts, funding history)
- [ ] Seven Powers mapped to GuardSpine (moat framework Eric's firm will recognize)
- [ ] Back-of-napkin math internalized (breakeven = 55 Starter or 30 Starter + 3 Team; $1B = 7,000 Org customers)
- [ ] Crisp 2-sentence answers to the 10 VC objections from Kristen's list
- [ ] TD Bank / Phil Venables status update (any forward motion is gold)
- [ ] Demo that runs cleanly in under 5 minutes (install GitHub Action, trigger PR, show judgment receipt)

**The bar is not perfection. The bar is:** Can David and Igor walk Eric through what GuardSpine is, who buys it, why they buy it, how much they pay, and where the money comes from -- without hesitating? If yes, the intro is ready.

---

_Generated: February 20, 2026. Updated February 21, 2026 (Starter tier added)._
_Source: Kristen meeting transcript (Feb 19, 2026), action items analysis, P&L model (Feb 18, 2026), pricing bridge spec (Feb 21, 2026)_
_Document ID: A2 (per action items index)_
