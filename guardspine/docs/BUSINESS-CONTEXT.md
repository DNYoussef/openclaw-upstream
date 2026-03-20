# GuardSpine Business Context

> For agents that need to understand what this company does, who it serves, and where it stands.
> Updated: 2026-03-18

---

## The Company

**GuardSpine Inc** -- AI code governance.
Delaware C-Corp (in formation via Stripe Atlas).
Website: guardspine.com (email capture live).
Open source: github.com/DNYoussef/codeguard-action

---

## The Product

**codeguard-action** (free GitHub Action):

- Risk-classifies every pull request (L0-L4) based on file patterns, sensitive zones, and change size
- Runs AI code review via multiple models in parallel (Claude, GPT, Gemini, Ollama)
- Produces signed evidence bundles proving the review happened, what was found, and what was decided
- Posts a governance comment on the PR with risk tier, findings (max 3), and merge posture

**Dashboard** (paid, not yet launched):

- Search, correlate, and present evidence bundles to auditors
- "If audited today" governance gap view -- this is the conversion page
- Org-wide policy controls, multi-repo visibility, evidence export

The free tool creates the problem the paid dashboard solves. Free answers "do I have governance?" Paid answers "can I prove governance at scale?"

---

## Positioning

The one lens, applied to everything:

**"Approved is not governed. Your auditor knows the difference."**

### Say This

- "code governance" (not "code review")
- "evidence" (not "audit trail")
- "risky changes" (not "all changes")
- "proportional" -- different risk levels get different treatment
- "partnership" (not "pilot program")

### Never Say This

- "AI governance platform"
- "semantic artifact governance"
- "secure SDLC platform"
- "code review assistant"
- "compliance automation"
- "pilot program"

### Approved Lines

- "GitHub tells you what changed. GuardSpine tells you what it means that it changed."
- "Evidence over opinions. Every time."
- "GuardSpine makes every risky code change provably governed without slowing the team to pre-AI velocity."
- "When AI accelerates code changes and auditors demand proof, help me govern risky changes at the point of change -- not after the fact."

---

## Target ICP

**Primary**: CISOs and VPs of Engineering at regulated companies (finance, health, government).

### Five Required Characteristics (all must be true)

1. GitHub-centered workflow
2. Meaningful PR volume
3. AI-assisted coding adoption (Copilot, Cursor, etc.)
4. Compliance or audit pressure
5. Enough engineering maturity to install GitHub Actions

### Pain Buckets (assign exactly one per prospect)

- **review_velocity_gap**: PR volume outpaces review capacity
- **evidence_chain_gap**: approval trail won't survive an auditor
- **semantic_governance_gap**: risky changes get the same treatment as typo fixes
- **authorization_provenance_gap**: can't prove who authorized what change
- **regulatory_readiness_gap**: can't answer auditor questions under time pressure

---

## Team

| Person                 | Role                                                             | Status      |
| ---------------------- | ---------------------------------------------------------------- | ----------- |
| David Youssef          | CEO/Founder. Vision, 1:1 sales, domain expertise.                | Full-time   |
| Igor Malovitsa         | CTO. Technical co-builder. GitHub: m1el.                         | Full-time   |
| Kristen Hengst Smith   | GTM advisor (darkpilot.com). Driving validation mode strategy.   | Advisor     |
| Chris Hood             | Advisor. Noematic AI, Google connections.                        | Advisor     |
| Ishwar Chandrasekharan | Scientific Advisor, Z-Inspection. Senior Technical Analyst, IBM. | Advisor     |
| Christopher Catoya     | Open-core advisor. cadCAD/BlockScience, SF network.              | Advisor     |
| Ilya Ploskovitov       | OSS contributor (PII-Shield WASM, 4 PRs merged).                 | Contributor |

This is NOT a solo founder operation. Complementary skills across technical + sales + GTM + advisory.

---

## Current Phase: VALIDATION MODE

Per Kristen's directive (Mar 11, 2026):

- NOT fundraising
- NOT modeling pricing
- NOT doing investor prep
- FOCUS: signal density -- conversations, product on real repos, "caught it" case studies
- TARGET: ~20 meaningful conversations + 3-5 real repo proof points
- THEN: re-evaluate fundraising posture

---

## Pipeline (as of 2026-03-18)

| Metric          | Count  |
| --------------- | ------ |
| Total prospects | 386    |
| Contacted       | 247    |
| Responded       | 31     |
| Green signals   | 18     |
| Yellow signals  | varies |

### Key Warm Leads

| Name           | Company            | Status                                         | Next Step                             |
| -------------- | ------------------ | ---------------------------------------------- | ------------------------------------- |
| Sanjay Nagaraj | Harness            | Discovery conversation                         | Meeting Mar 30                        |
| Phil Venables  | Ballistic Ventures | Engaged -- asked 3 DD questions, David replied | Awaiting Phil's next response         |
| Brent Foster   | TD Bank            | Warm                                           | Follow up on codeguard-action install |
| Eric Skiff     | (paused)           | Mother in hospital                             | Kristen monitoring                    |
| Jason Sznol    | Nimbus             | Feedback source only (not decision-maker)      | Kristen getting CTO call              |

---

## Pricing Direction (deferred per Kristen)

| Tier             | Price                  | Trigger                            |
| ---------------- | ---------------------- | ---------------------------------- |
| Free (CodeGuard) | $0                     | Install GitHub Action              |
| Team             | $99-299/repo/month     | Second repo + team invite          |
| Growth           | $1,500-5,000/org/month | Multi-repo + policy enforcement    |
| Enterprise       | $15,000-75,000+ ACV    | Org-wide governance + integrations |

Org pricing, not per-seat. The pain is governance exposure across repos, not individual user productivity.

---

## Revenue

**Current**: $0.

**Target**: First paying customer, then $3K MRR.

**Year 1 model** (from growth engine spec):

```
2,000 installs
  -> 400 accounts (20%)
  -> 80 second-repo connects (20%)
  -> 16 paid orgs (20%)
Blended ACV $6,000 = ~$96K ARR
+ 3 enterprise deals at $25K = $75K
= $171K ARR Year 1
```

---

## Competition

| Competitor            | What They Do                  | What They Don't Do                                 |
| --------------------- | ----------------------------- | -------------------------------------------------- |
| Sourcery AI           | Automated code review         | No evidence bundles, no risk tiers, no audit proof |
| Kodus AI              | AI code review                | No governance framing, no signed artifacts         |
| GitHub native reviews | CODEOWNERS + required reviews | Approval is not governance. No evidence chain.     |

None of them produce evidence bundles. None do risk-tiered proportional governance. None frame the problem as "governance" vs "review."

---

## Growth Engine

The viral loop:

1. Developer installs codeguard-action (free)
2. Every PR gets a governance comment with risk tier + findings + CTA
3. Comment links to dashboard ("view full governance report")
4. Dashboard shows "if audited today" gap view -- this converts
5. Second repo connected -> team invite -> paid trigger

Five paid trigger events:

1. Second repo connected
2. First "high-risk merge without complete evidence"
3. First team invite
4. First export attempt
5. First policy-rule creation attempt

---

## Key Links

- Calendar: cal.com/david-youssef
- Landing: guardspine.com
- GitHub Action: github.com/DNYoussef/codeguard-action
- David LinkedIn: post hot takes 8-9am ET
- GuardSpine LinkedIn: educational posts 11am-12pm ET
