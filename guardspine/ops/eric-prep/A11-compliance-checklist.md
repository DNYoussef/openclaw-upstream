# GuardSpine Compliance Checklist

**Which frameworks does GuardSpine produce evidence for?**

Hand this to your CISO. Takes 2 minutes to read.

---

## What GuardSpine Does

GuardSpine runs as a GitHub Action in your CI/CD pipeline. Every pull request gets risk-tiered (L0-L4), reviewed by AI models, and produces a tamper-proof judgment receipt -- a signed evidence bundle proving what was reviewed, by whom, and what was decided.

This evidence maps directly to the compliance frameworks below.

---

## Framework Coverage

### SOC 2 Type II

| Control | Requirement             | GuardSpine Evidence                                                                 |
| ------- | ----------------------- | ----------------------------------------------------------------------------------- |
| CC6.1   | Logical access controls | Signed record of which models and humans reviewed each change                       |
| CC8.1   | Change management       | Tamper-proof judgment receipt for every PR: risk tier, findings, consensus decision |
| CC7.2   | System monitoring       | Continuous automated governance via CI/CD -- every PR, not spot checks              |

**Auditor deliverable:** Export evidence bundles as JSON or CSV. Searchable by date, repo, risk tier, decision.

---

### DORA (Digital Operational Resilience Act)

| Article | Requirement                    | GuardSpine Evidence                                                                          |
| ------- | ------------------------------ | -------------------------------------------------------------------------------------------- |
| 6a      | ICT change management controls | Every code change to financial systems produces a governance record with risk classification |

**Effective:** January 17, 2025 (already enforceable)
**Penalty:** Up to 2% of global annual turnover or EUR 10M (whichever is higher)

---

### HIPAA Security Rule

| Section    | Requirement                     | GuardSpine Evidence                                                          |
| ---------- | ------------------------------- | ---------------------------------------------------------------------------- |
| 164.312(b) | Audit controls for ePHI systems | Tamper-proof audit records for every code change touching healthcare systems |

**Penalty:** $145 to $2.19M per violation category (2026 OCR-adjusted amounts)

---

### PCI DSS v4.0

| Requirement | Description               | GuardSpine Evidence                                                      |
| ----------- | ------------------------- | ------------------------------------------------------------------------ |
| 6.5.1       | Change control procedures | Documented, signed review process for every code change                  |
| 6.2.3       | Code review requirements  | Evidence of security-focused review by independent reviewers (AI models) |

---

### EU AI Act

| Article | Requirement                    | GuardSpine Evidence                                                |
| ------- | ------------------------------ | ------------------------------------------------------------------ |
| 9       | Risk management for AI systems | Risk-tiered review (L0-L4) with model-specific findings per change |
| 17      | Quality management systems     | Continuous quality governance with structured evidence output      |

**Enforcement:** Rolling out through August 2026
**Penalty:** Up to 7% of worldwide annual turnover or EUR 35M

---

### ISO 27001:2022

| Control  | Requirement               | GuardSpine Evidence                                             |
| -------- | ------------------------- | --------------------------------------------------------------- |
| A.12.1.2 | Change management         | Automated, tamper-proof change governance records               |
| A.14.2.2 | Secure development policy | Verified secure development lifecycle evidence for every change |

---

## What GuardSpine Is NOT

- **Not a replacement for Vanta or Drata.** They prove your infrastructure is configured correctly (cloud, access controls, policies). GuardSpine proves your code changes were governed. They are complementary.
- **Not a code review tool.** Code review suggests fixes. GuardSpine creates proof that review happened.
- **Not an AI governance platform.** GuardSpine governs artifacts (code, eventually docs and images) regardless of who produced them -- human or AI.

---

## How It Deploys

1. Engineer adds a YAML file to the repository (5 minutes)
2. Every PR triggers automatic risk-tiered review
3. AI models review using the team's own API keys (BYOK -- no data leaves your pipeline)
4. Judgment receipt appears as a PR comment
5. Evidence is searchable, exportable, and verifiable offline

**Zero workflow disruption. Zero new tools for engineers to learn.**

---

## Pricing

| Tier    | Monthly | Annual   | What You Get                                              |
| ------- | ------- | -------- | --------------------------------------------------------- |
| Free    | $0      | $0       | Full review engine, evidence as JSON, unlimited repos     |
| Starter | $499    | $4,788   | Cloud dashboard, Slack alerts, evidence management        |
| Team    | $2,000  | $19,200  | Custom rubrics, Jira + Teams, compliance report templates |
| Org     | $12,000 | $120,000 | Multi-team RBAC, ServiceNow, SSO/SAML, dedicated CSM      |

All tiers use the same open-source review engine. BYOK = zero AI inference cost to you.

---

[Request a demo](https://guardspine.ai/security) | [View source on GitHub](https://github.com/DNYoussef/codeguard-action)

_GuardSpine. Governance that proves it happened._
