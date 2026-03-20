# GuardSpine Growth Engine Specification

Extracted from marketing strategy sessions. This is the operational playbook.

## 1. The Free Wedge (Lead Magnet = Product)

codeguard-action (free GitHub Action) + guardspine-verify (free offline verifier)

The free tool creates the problem the paid dashboard solves:

- Free: "Do I have governance?" (evidence bundles generated)
- Paid: "Can I prove governance at scale?" (dashboard to search, correlate, present)

## 2. PR Comment Template (the growth engine)

Every PR analyzed by codeguard-action gets a comment with 5 sections:

### Section A: Executive Risk Header

```
Risk: L2 (Medium) | Confidence: High | Evidence: Complete | Policy: Compliant
Recommendation: MERGE with conditions
```

### Section B: Findings (max 3, never more)

```
1. Auth logic changed without corresponding test evidence
2. Privilege-sensitive path modified; reviewer signoff missing
3. Runtime-impacting change lacks rollback signal
```

### Section C: Governance Language (NOT static-analysis language)

Bad: "Possible null dereference" / "Potential auth bug"
Good: "Auth logic changed without corresponding test evidence"
Good: "Security-relevant diff without traceable approval artifact"

### Section D: Merge Posture

```
Safe to merge: Yes (with conditions above addressed)
```

### Section E: CTA (viral install loop)

```
This PR was analyzed by GuardSpine CodeGuard.
Your repo has X unresolved governance gaps.
Install for your repo: [link]
```

### Three PR Comment Variants by Org Maturity:

1. Individual/OSS: risk + evidence + merge guidance
2. Startup team: review bottleneck + audit-readiness + multi-repo visibility
3. Regulated org: approval traceability + policy conformance + evidence retention

## 3. Dashboard Conversion Escalator (4 screens)

Screen 1: **Repo Summary** -- PRs analyzed, risk distribution, incomplete evidence count, policy exceptions. "Audit exposure" mandatory, "time saved" optional.

Screen 2: **Governance Gap View** -- "If audited today" status. THIS IS THE CONVERSION PAGE.

Screen 3: **Evidence Bundle Preview** -- partial bundle with gated full export.

Screen 4: **Org Policy Control Panel** -- premium future-state preview.

## 4. Five Paid Trigger Events

1. Second repo connected
2. First "high-risk merge without complete evidence"
3. First team invite
4. First export attempt
5. First policy-rule creation attempt

## 5. Pricing Ladder

| Tier             | Price                  | Trigger                            |
| ---------------- | ---------------------- | ---------------------------------- |
| Free (CodeGuard) | $0                     | Install action                     |
| Team             | $99-299/repo/month     | Second repo + team invite          |
| Growth           | $1,500-5,000/org/month | Multi-repo + policy enforcement    |
| Enterprise       | $15,000-75,000+ ACV    | Org-wide governance + integrations |

Org pricing over per-seat: "the pain is governance exposure across repos, not individual user productivity."

## 6. Year 1 Revenue Model

```
2,000 installs
  -> 20% create accounts (400)
  -> 20% connect second repo (80)
  -> 20% convert paid (16 orgs)
Blended ACV $6,000 = ~$96K ARR
+ 3 enterprise deals at $25K = $75K
= $171K ARR Year 1
```

Year 2: 10,000 installs, 100-200 paid orgs, 10-20 enterprise accounts.

## 7. Lead Capture from GitHub Actions (3 mechanisms)

GitHub Actions don't naturally capture leads. Solutions:

1. Install -> prompt "Register to view full report" / "Enable dashboard"
2. PR comment output includes link to dashboard with account creation
3. Email/org capture required for history/compliance reports/team view

Qualification signals: repo size, PR volume, AI usage signals, tech stack, org domain.

## 8. Four Cold Outreach Scripts

### Script 1: Direct Problem Framing

Subject angle: "AI PR volume vs review capacity"
Lead: Your team ships X PRs/week. How many get real scrutiny?

### Script 2: Compliance Framing

Subject angle: "Review proof for AI-generated code"
Lead: When your auditor asks how you governed AI-generated changes, what do you show them?

### Script 3: Platform Engineering Framing

Subject angle: "A GitHub Action for high-risk PR governance"
Lead: A free action that risk-classifies every PR and produces evidence bundles.

### Script 4: Consultant/vCISO

Subject angle: "Free PR governance action for client repos"
Lead: Install on client repos. Evidence bundles make your compliance work defensible.

Positioning rule: "Do not sell better scanning. Sell: provable governance for AI-speed pull requests."

## 9. Champion/Referral Leaderboard

### Scoring

- Successful install = 1 point
- Activated account = 3 points
- Second repo connected = 5 points
- Paid org conversion = 15 points

### Anti-Gaming

- Count install only when workflow runs successfully AND report is viewed AND account created
- Dedupe self-installs by org/domain/repo fingerprint

### Four-Tier Incentives

- Tier 1 (3 installs): "Governance Black Book," early access, badge
- Tier 2 (10 installs): private office hours, premium analytics for 1 repo, "Founding Champion"
- Tier 3 (25 installs): advisory council, co-marketing, featured case study, partner referral path
- Tier 4 (consultant/agency): multi-client dashboard preview, white-label reports, revenue share later

### Monthly Ritual

Publish leaderboard, announce winners, share best-performing copy, share one case study, run one private Q&A.

## 10. Core Internal Prediction Model

"Risk events per repo per month -> probability of paid conversion"

This is the most important model to track. If a repo generates high-risk findings, the probability of the org paying for dashboard access increases.

## 11. PR Comment KPIs

- Comment CTR to full report
- Click-to-signup rate
- Click-to-org-connect rate
- Merges blocked after high-risk flag
- % of comments triggering repeat usage
- North-star: "% of high-risk PRs that convert into 'view full governance report'"

## 12. Target Wedge Characteristics (all 5 required)

1. GitHub-centered workflow
2. Meaningful PR volume
3. AI-assisted coding adoption (Copilot/Cursor)
4. Compliance or audit pressure
5. Enough engineering maturity to install GitHub Actions

## 13. What NOT To Do

- Don't start with giant enterprise platform story
- Don't position as generic "AI safety for devs"
- Don't feature-compare against every scanner
- Don't price based on seats only
- Don't do broad SMB spray

## 14. Two Positioning One-Liners

1. "GuardSpine is the system that turns every pull request into audit-ready evidence."
2. "GuardSpine proves whether AI-speed pull requests were governed well enough to merge -- and to defend later."
