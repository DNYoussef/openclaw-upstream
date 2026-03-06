# GuardSpine Pricing Bridge -- Starter Tier Spec

**Version:** 1.0
**Date:** February 21, 2026
**Authors:** David Youssef, Igor Malovitsa
**Source:** Kristen meeting Feb 19 (pricing gap at 13:07), competitive research, financial model

---

## The Problem

Free ($0) to Team ($2,000/mo) is a cliff. Nobody jumps it without evidence.

> "Our first tier is 2,000 bucks a month... it feels like a big jump from
> free to $2,000 a month." -- David, Feb 19

> "Yep." -- Kristen, Feb 19

Without a bridge tier, GuardSpine cannot:

1. Prove willingness to pay (zero conversion data for investors)
2. Give developers ammunition to "ask their CISO" (the pharma model)
3. Generate revenue before enterprise sales cycles close (3-6 months)
4. Show Kristen and Eric a path to first dollar

---

## The Decision: $499/mo Starter Tier

### Why $499

| Factor                          | $199           | $499             | $625+                |
| ------------------------------- | -------------- | ---------------- | -------------------- |
| Category signal                 | Dev tool       | Entry governance | Full governance      |
| CISO perception                 | Toy            | Credible         | Expected             |
| Developer accessibility         | Easy           | Justifiable      | Needs approval chain |
| vs Drata Foundation ($625/mo)   | Way below      | Just below       | Parity               |
| vs Vanta Core ($833/mo)         | Way below      | Below            | Approaching          |
| vs CodeRabbit 10 devs ($120/mo) | Dev tool range | Above            | Way above            |
| vs Snyk Team 10 devs ($250/mo)  | Dev tool range | Above            | Way above            |
| Margin at 98% COGS              | $195/mo profit | $489/mo profit   | $613/mo profit       |

**$499 is the Goldilocks number:**

- Below compliance tool entry points (signals "we're new, try us")
- Above developer tool pricing (signals "this is governance, not a linter")
- Psychologically below $500 (common expense-without-approval threshold)
- Annual option at $399/mo ($4,788/yr) undercuts Drata by 36%

### Why Not Per-Seat Pricing

GuardSpine is BYOK. Customers bring their own API keys, pick their own models,
pay their own inference costs. We do not meter model usage.

Per-seat pricing ($25/dev/mo) positions us as a dev tool. Kristen explicitly
said we are governance, not coding. Platform fee pricing matches Vanta, Drata,
and the compliance category we compete in.

Per-seat also creates the wrong incentive: companies limit seats to save money,
which means fewer PRs governed, which defeats the purpose. Platform fee means
"govern everything" from day one.

### Why Not Usage-Based (Per-PR)

Per-PR pricing ($3/PR) is interesting for conversion but fails three tests:

1. VCs hate unpredictable revenue at pre-seed
2. CISOs cannot budget variable costs
3. It does not prove subscription willingness-to-pay

However: usage-based can work as an OVERAGE model within Starter (see caps below).

---

## Architecture: What Is Free vs Paid

The open-source GitHub Action (codeguard-action) IS the review engine. It runs
in the customer's CI/CD pipeline. The risk-based model escalation (L0-L4),
multi-model deliberation, cross-check rounds, consensus voting, and evidence
bundle generation all happen in the open-source core.

**Every customer -- free or paid -- gets the same review engine.**

The paid tiers sell the PLATFORM LAYER on top:

```
ENTERPRISE  |  White-glove, airgap/on-prem, custom integrations, SLA
   ORG      |  Multi-team, RBAC, compliance dashboards, ServiceNow
  TEAM      |  Custom rubrics, Jira, Teams, escalation workflows
 STARTER    |  Dashboard, Slack, evidence management, analytics
  FREE      |  Open-source GitHub Action (self-managed, no cloud)
            +-------------------------------------------------------
               codeguard-action (OSS review engine -- same for all)
```

This is the open-core model done right. The engine is free and trustworthy
(open source = independently verifiable governance). The platform is where
the business lives.

---

## Revised Tier Ladder

### Free -- $0/mo

**What it is:** The open-source GitHub Action, self-managed.

| Feature          | Detail                                                                               |
| ---------------- | ------------------------------------------------------------------------------------ |
| Review engine    | Full codeguard-action: risk-tiered L0-L4, multi-model deliberation, consensus voting |
| Models           | BYOK -- customer configures any models (Claude, GPT, Gemini, Ollama)                 |
| Evidence bundles | Generated locally as signed JSON per PR                                              |
| Rubric packs     | Community rubrics (open-source YAML templates)                                       |
| Dashboard        | None (JSON output only)                                                              |
| Notifications    | None (GitHub PR comments only)                                                       |
| Repos            | Unlimited (it is a GH Action the customer installs)                                  |
| Contributors     | Unlimited                                                                            |
| Support          | Community (GitHub Issues)                                                            |

**Who it is for:** Individual developers, open-source projects, small teams
evaluating GuardSpine before committing. The adoption wedge.

---

### Starter -- $499/mo ($399/mo annual, $4,788/yr)

**What it is:** GuardSpine Cloud -- the managed platform on top of the
open-source engine.

| Feature             | Detail                                                            |
| ------------------- | ----------------------------------------------------------------- |
| Review engine       | Same full codeguard-action (unchanged from Free)                  |
| Models              | BYOK -- same as Free                                              |
| Dashboard           | PR history, risk distribution, finding trends, team activity      |
| Slack integration   | Approve/reject notification cards, finding alerts                 |
| Evidence management | Search, filter, export (JSON + CSV), share via link               |
| Rubric packs        | Standard library (pre-built industry rubrics -- not customizable) |
| Connected repos     | Up to 10                                                          |
| Contributors        | Up to 25                                                          |
| Audit log           | 90-day retention, searchable                                      |
| Support             | Email (48-hour SLA)                                               |

**Who it is for:** Teams of 5-25 developers at companies starting to formalize
governance. The team that wants visibility into what the open-source engine is
finding, without building their own dashboard.

**The "ask your CISO" moment:** Developer installs free GitHub Action, sees
value, wants the dashboard and Slack cards. Goes to CISO: "We need Starter,
it is $499/mo and gives us audit evidence for compliance." CISO approves
because $499/mo is a rounding error in a $500K+ compliance budget.

---

### Team -- $2,000/mo ($1,600/mo annual, $19,200/yr)

**What it is:** Full platform with custom governance rules and enterprise
integrations.

| Feature                     | Everything in Starter, plus:                        |
| --------------------------- | --------------------------------------------------- |
| Custom rubric builder       | Write, test, and deploy custom governance rules     |
| Jira integration            | Create tickets from findings, link to evidence      |
| Microsoft Teams             | Notification cards (in addition to Slack)           |
| Custom escalation workflows | Route findings by severity, team, file path         |
| Compliance report templates | Pre-built SOC2, DORA, HIPAA evidence exports        |
| Connected repos             | Unlimited                                           |
| Contributors                | Unlimited                                           |
| Audit log                   | 1-year retention                                    |
| Support                     | Priority email + Slack (4-hour SLA, business hours) |

**Who it is for:** Teams of 25-100 developers with formal governance
requirements. The team that needs custom rules for their industry and
integration into their existing workflow tools.

---

### Org -- $12,000/mo ($10,000/mo annual, $120,000/yr)

**What it is:** Multi-team governance platform for mid-market organizations.

| Feature                        | Everything in Team, plus:                   |
| ------------------------------ | ------------------------------------------- |
| Multi-lane guards              | Code + documents + images (as lanes mature) |
| RBAC                           | Role-based access, team-scoped dashboards   |
| ServiceNow integration         | Incident and change management linking      |
| Custom escalation daemon       | Auto-route by org policy, SLA enforcement   |
| Advanced compliance dashboards | Real-time posture view across all teams     |
| SSO/SAML                       | Enterprise identity provider integration    |
| Audit log                      | 3-year retention, tamper-proof export       |
| Support                        | Dedicated CSM, 2-hour SLA                   |

---

### Enterprise -- $50,000/mo (Custom)

**What it is:** White-glove deployment for Tier 1 regulated institutions.

| Feature                     | Everything in Org, plus:                                   |
| --------------------------- | ---------------------------------------------------------- |
| On-prem / airgap deployment | Self-hosted with Ollama models, no data leaves the network |
| Custom integrations         | Bespoke connectors (internal tools, legacy systems)        |
| SLA                         | 99.9% uptime, 1-hour response, named support engineer      |
| Compliance consulting       | Quarterly reviews, audit prep assistance                   |
| Custom training             | Team onboarding, rubric development workshops              |

---

## Upgrade Triggers

Each tier has natural moments where a customer outgrows it:

| Trigger                                 | From    | To         |
| --------------------------------------- | ------- | ---------- |
| "I want a dashboard"                    | Free    | Starter    |
| "I need Slack notifications"            | Free    | Starter    |
| Hit 10-repo cap                         | Starter | Team       |
| Hit 25-contributor cap                  | Starter | Team       |
| Need custom rubric rules                | Starter | Team       |
| Need Jira/ServiceNow integration        | Starter | Team       |
| Need compliance report templates        | Starter | Team       |
| Multiple teams need separate dashboards | Team    | Org        |
| Need SSO/SAML                           | Team    | Org        |
| Need RBAC and org-wide policies         | Team    | Org        |
| Airgap / on-prem requirement            | Org     | Enterprise |
| Need SLA and named support              | Org     | Enterprise |

---

## 30-Day Free Trial of Starter

Both landing pages offer a 30-day free trial of Starter. No credit card required.

**Why:** Eliminates all friction for the first conversion. Creates usage data
for investor conversations. At day 30, features downgrade to Free unless
the customer converts. Industry standard (CodeRabbit: 14 days, Greptile: 14 days,
Snyk: free tier then upgrade).

**Landing page CTA:**

- Developer page: "Start your 30-day free trial"
- CISO page: "Request a demo" (leads to trial after demo call)

---

## Landing Page Pricing Display

### Developer Page (guardspine.ai/dev)

```
FREE                    STARTER                 TEAM
$0/mo                   $499/mo                 $2,000/mo
                        $399/mo billed annually

Open-source GH Action   Everything in Free,     Everything in Starter,
Full review engine       plus:                   plus:
Evidence bundles         - Cloud dashboard       - Custom rubric builder
Community rubrics        - Slack notifications   - Jira + Teams
                         - Evidence search       - Compliance reports
[Install now]            - 10 repos, 25 devs     - Unlimited repos
                         - Email support         - Priority support
                        [Start free trial]       [Talk to us]
```

### CISO Page (guardspine.ai/security)

```
STARTER                 TEAM                    ORG
$499/mo                 $2,000/mo               $12,000/mo
$4,788/yr               $19,200/yr              $120,000/yr

Tamper-proof audit       Everything in Starter,  Everything in Team,
trail for every PR       plus:                   plus:
Cloud dashboard          - Custom governance     - Multi-team RBAC
Slack alerts              rules                  - ServiceNow
Evidence management      - Jira integration      - SSO/SAML
90-day audit log         - Compliance reports    - Dedicated CSM
                          (SOC2, DORA, HIPAA)
[Request a demo]         - 1-year audit log      [Request a demo]
                        [Request a demo]

                    ENTERPRISE: Custom pricing. On-prem. SLA. [Contact us]
```

Note: The developer page leads with Free (adoption wedge). The CISO page
leads with Starter (minimum viable governance purchase). Same product,
different entry point.

---

## Financial Impact

### Breakeven Scenarios (at $26,500/mo burn)

| Scenario                    | Customers | Monthly Revenue |
| --------------------------- | --------- | --------------- |
| Starter only                | 55        | $27,445         |
| 30 Starter + 3 Team         | 33        | $20,970         |
| 20 Starter + 5 Team + 1 Org | 26        | $21,980         |
| Team only (old model)       | 14        | $28,000         |

Starter creates MORE PATHS to breakeven. Instead of needing 14 Team customers
(hard pre-PMF), you can get there with a blend of 20-30 Starter and a few
Team upgrades.

### Year 1 Projections (with Starter)

| Quarter | Starter | Team | Org | MRR     | ARR Run Rate |
| ------- | ------- | ---- | --- | ------- | ------------ |
| Q1      | 5       | 0    | 0   | $2,495  | $29,940      |
| Q2      | 15      | 2    | 0   | $11,485 | $137,820     |
| Q3      | 25      | 5    | 1   | $34,475 | $413,700     |
| Q4      | 30      | 8    | 2   | $54,970 | $659,640     |

Assumptions: 30-day trial -> 8% conversion. 15% quarterly Starter->Team upgrade.
1 Org deal per quarter starting Q3.

### Landing Page Conversion Math

| Metric                          | Value                         |
| ------------------------------- | ----------------------------- |
| 100 email signups               | Baseline                      |
| 30-day trial starts             | ~40% of signups = 40 trials   |
| Trial -> Starter conversion     | 8-12% = 3-5 paying customers  |
| Revenue from 100 signups        | $1,497-$2,495/mo              |
| Reportable to Kristen by Feb 26 | "X signups, Y trials started" |

---

## Competitive Positioning

| Product                | Entry Tier       | Annual Cost (10 devs) | Category              |
| ---------------------- | ---------------- | --------------------- | --------------------- |
| CodeRabbit Lite        | $12/dev/mo       | $1,440                | Code review           |
| Greptile Cloud         | $30/dev/mo       | $3,600                | Code review           |
| Snyk Team              | $25/dev/mo       | $3,000                | Developer security    |
| Semgrep Teams          | $40/dev/mo       | $4,800                | Static analysis       |
| **GuardSpine Starter** | **$499/mo flat** | **$4,788 (annual)**   | **Code governance**   |
| Drata Foundation       | ~$625/mo flat    | $7,500                | Compliance automation |
| Vanta Core             | ~$833/mo flat    | $10,000               | Compliance automation |

GuardSpine Starter sits between the dev tool tier and the compliance tool tier.
This is intentional: governance-grade product at a below-compliance price point.
As the product matures and market validates, Starter price can increase.

---

## What This Changes in Existing Docs

The following documents reference the old 4-tier pricing (Free/Team/Org/Enterprise)
and need the Starter tier added:

- [ ] A2-product-definition.md (Section 4: Pricing Tiers table)
- [ ] 01-product-definition.md (eric-prep copy)
- [ ] 04-financial-math.md (breakeven scenarios, customer count matrix)
- [ ] 05-vc-objections.md (Q2 "why should I invest" -- add Starter conversion data)
- [ ] 09-landing-page-plan.md (pricing display sections)
- [ ] Messaging reframe docs (add Starter framing for both personas)

---

## Decision Log

| Option Considered              | Rejected Because                                                 |
| ------------------------------ | ---------------------------------------------------------------- |
| Per-seat $25/dev/mo            | Positions as dev tool. Kristen said "governance, not coding."    |
| Flat $199/mo                   | CISOs read $199 as a toy. Below dev tool pricing for 10 devs.    |
| Flat $625/mo                   | Parity with Drata -- too high for unproven product.              |
| Hybrid $299 + $29/dev          | Too complex for a landing page. Pricing model change on upgrade. |
| Per-PR $3/review               | VCs hate variable revenue. CISOs cannot budget it.               |
| $499/mo with model count gates | BYOK means we do not control or pay for models. Fake scarcity.   |

**Selected: $499/mo flat platform fee with repo and contributor caps.**

Caps create natural upgrade triggers. Platform features (dashboard, integrations,
rubric management, compliance reporting) create real value differentiation.
The open-source review engine remains the same for everyone.

---

_This document is part of the Eric intro prep package (eric-prep/).
Review with Igor before sending to Kristen._
