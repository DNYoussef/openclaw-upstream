# Landing Page A/B Test Plan

**Kristen's Two-Website Experiment** | Feb 20, 2026

---

## The Question

"Are you a developer who needs to make your governance people happy?
Or are you a CISO looking for a tool because your engineers are giving you heartburn?"
-- Kristen, Feb 19

## Two Pages, One Domain

### Page A: Developer-Facing (guardspine.ai/dev)

- **Headline:** "Stop rubber-stamping PRs. Get governance that actually works."
- **Subhead:** Open-source GitHub Action. 2-minute install. AI-powered code governance with tamper-proof audit trail.
- **Primary CTA:** "Start your 30-day free trial" (email capture -> Starter trial)
- **Secondary CTA:** "Install the free GitHub Action" (links to codeguard-action repo)
- **Proof points:** Works with GitHub Actions, BYOK (no vendor lock-in), judgment receipts on every PR
- **Tone:** Builder-friendly, no-BS, show-the-code
- **Pricing display:** Free ($0) | Starter ($499/mo, 30-day trial) | Team ($2K/mo) | [Talk to us]

### Page B: CISO-Facing (guardspine.ai/security)

- **Headline:** "Every AI-generated code change. Reviewed. Logged. Court-admissible."
- **Subhead:** Tamper-proof governance for engineering teams shipping AI-written code. Starts at $499/mo -- less than your Drata bill.
- **Primary CTA:** "Request a demo" (email + company + title capture -> demo call -> Starter trial)
- **Proof points:** DORA-ready, SOC2 evidence generation, offline verification, audit trail
- **Tone:** Professional, risk-focused, compliance language
- **Pricing display:** Starter ($499/mo) | Team ($2K/mo) | Org ($12K/mo) | Enterprise (custom)

## What We Measure

- Email signups per page (raw count)
- Title/role of signups (are we getting CISOs or developers?)
- Time on page
- Which page gets shared more (UTM tracking)

## Minimum Viable Signal

- 3-5 days of data
- 20+ signups on either page = strong signal
- 5+ Starter trial activations = proof of willingness to engage
- 1+ trial-to-paid conversion within 30 days = proof of willingness to pay
- If Page A wins: we're a developer tool that makes compliance easy
- If Page B wins: we're a governance tool that developers adopt
- If both win: we're both (and the messaging reframe doc A13 tells us how to talk to each)

## Tech Stack (Keep It Simple)

- Hosting: Vercel or Netlify (free tier)
- Framework: Next.js or plain HTML (speed over features)
- Email capture: Resend or Mailchimp free tier
- Analytics: Plausible or PostHog (privacy-friendly)
- Domain: guardspine.ai (existing) or guardspine.ai

## Timeline

- Day 1: Build both pages (Igor or David, ~4 hours total)
- Day 2: Deploy, test email capture flow
- Day 3-7: Run traffic (share on LinkedIn, HN, Reddit r/devops, r/security)
- Day 8: Analyze results, report to Kristen before Eric intro

## Pricing Section (Both Pages)

Both pages include a pricing comparison. Same tiers, different lead:

**Developer page** leads with Free (adoption) then Starter (conversion):

- Free: open-source GH Action, full review engine, community rubrics
- Starter $499/mo: cloud dashboard, Slack alerts, evidence search, 10 repos, 25 devs
- Team $2K/mo: custom rubrics, Jira + Teams, compliance reports, unlimited
- [Talk to us] for Org/Enterprise

**CISO page** leads with Starter (minimum viable purchase):

- Starter $499/mo: tamper-proof audit trail, dashboard, Slack, evidence management
- Team $2K/mo: custom governance rules, Jira, compliance reports (SOC2, DORA, HIPAA)
- Org $12K/mo: multi-team RBAC, ServiceNow, SSO/SAML, dedicated CSM
- Enterprise: custom pricing, on-prem, SLA

Annual pricing shown on both: 20% discount ($399/mo Starter, $1,600/mo Team).

Full pricing rationale: see `10-pricing-bridge-spec.md`.

---

_Source: Kristen meeting Feb 19, 2026 -- "Make two websites... see who's biting."_
_Updated Feb 21, 2026 with Starter tier pricing and CTAs._
