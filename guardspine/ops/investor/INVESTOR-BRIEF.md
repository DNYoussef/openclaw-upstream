# GuardSpine: Angel Investor Brief

## AI-Mediated Work Governance Platform

**Prepared for: Kristen Hengst Smith & Associates**
**Date: February 13, 2026**
**Author: David Youssef, Founder & CEO**

---

## The Problem

Every enterprise uses AI to generate code, documents, spreadsheets, and images.
None of them can prove what the AI did, who approved it, or whether it was safe.

- **$15B+ TAM** in AI governance (code-only); **$51B** across all artifact types
- **No competitor we've identified** governs documents, spreadsheets, and images -- only code (based on 9-dimension analysis of 10 named competitors, Feb 2026)
- Regulatory pressure accelerating: EU AI Act, DORA, FDA 21 CFR Part 11, SOX

## The Solution

GuardSpine is the governance spine for AI-mediated work. It answers one question:
**"Are we in control?"** -- with cryptographic proof, not trust.

### How It Works

1. **AI reviews every change** (code PR, PDF revision, spreadsheet edit, image swap)
2. **Risk tier assigned** (L0 auto-pass through L4 executive approval required)
3. **Evidence bundle created** with hash-chained audit trail
4. **Decision card posted** (APPROVED / CONDITIONAL / BLOCKED)
5. **Escalation policies enforce SLAs** per risk tier

### Four Guard Lanes

| Lane       | What It Guards         | File Types        | Status          |
| ---------- | ---------------------- | ----------------- | --------------- |
| CodeGuard  | Pull requests, commits | Any code          | Live            |
| PDFGuard   | Document revisions     | .pdf              | Roadmap H2 2026 |
| SheetGuard | Spreadsheet changes    | .xlsx, .xlsm      | Roadmap H2 2026 |
| ImageGuard | Visual asset changes   | .png, .jpg, .tiff | Roadmap H2 2026 |

## Traction

- **737 tests passing** across 5 repos (verified February 23, 2026)
- **codeguard-action** live on GitHub Marketplace
- **85-sample eval harness**: 100% detection rate, 0% false negatives
- **3 compliance packs** shipping: Finance (SOX), Health (HIPAA), SaaS (SOC2)
- **Deliberation protocol**: Multi-round AI cross-checking for high-risk reviews
- **PII-Shield integration**: Entropy-based secret detection with whitelist

## Business Model: BYOK (Bring Your Own Key)

Customers supply their own LLM API keys. GuardSpine pays **zero inference costs**.

| Tier       | Price/mo | Annual   | Gross Margin |
| ---------- | -------- | -------- | ------------ |
| Starter    | $499     | $4,788   | 87-91%       |
| Team       | $2,000   | $19,200  | 87-91%       |
| Org        | $12,000  | $120,000 | 87-91%       |
| Enterprise | Custom   | Custom   | 87-91%       |

**Open-core model**: 8 Apache 2.0 repos (codeguard-action, guardspine-kernel, guardspine-kernel-py, guardspine-verify, guardspine-local-council, guardspine-spec, pii-shield, guardspine-rubric-packs). UI dashboard, multi-lane guards, approval workflows, and enterprise integrations are proprietary.

## Revenue Projections

| Scenario | Year 1 ARR | Year 3 ARR |
| -------- | ---------- | ---------- |
| Bear     | $228K      | $1.4M      |
| Base     | $1.28M     | $36.8M     |
| Bull     | $6.7M      | $535M\*    |

\*Bull Y3 assumes 20% monthly compounding for 36 months. Base case is the planning scenario.

### Why These Numbers Are Achievable

Four tailwinds compound in our favor:

1. **EU AI Act enforcement (Aug 2, 2026)**: 7% of global annual turnover in fines for non-compliance. Thousands of EU companies must have AI governance tooling by this date. Converts governance from "nice to have" to "must have," compressing sales cycles from 6-9 months to 2-4 months.

2. **AI adoption acceleration**: 80%+ of enterprises using GenAI by end of 2026 (Gartner). Every AI-generated artifact -- code, document, spreadsheet, image -- is an ungoverned liability. The volume of changes needing governance grows 3-5x annually.

3. **Multi-lane expansion (NRR 120-130%)**: Customers start with CodeGuard ($2K/mo) and expand to PDFGuard, SheetGuard, ImageGuard. Each lane addition increases ACV 50-100%, driving organic revenue growth from the existing customer base without adding new logos.

4. **Zero-friction pricing (BYOK)**: No compute cost debates during procurement. Flat subscription, not metered API. Customers use their own LLM keys, eliminating the biggest objection in enterprise AI tool sales.

## Competitive Moat (Three Layers)

1. **Multi-artifact governance**: Only platform we've found guarding code + docs + sheets + images
2. **Hash-chained evidence bundles**: Cryptographic proof of every decision (not just logs)
3. **Model-neutral BYOK architecture**: Works with any LLM provider. No vendor lock-in. Supports airgapped/offline deployments via Ollama for regulated environments.

## Strategic Partnerships

| Partner                                       | Value                                                     | Status               |
| --------------------------------------------- | --------------------------------------------------------- | -------------------- |
| **Ishwar Chandrasekharan (IBM/Z-Inspection)** | Enterprise validation methodology                         | Active collaboration |
| **Jacob Friedman (G7 AI governance)**         | Standards credibility + gov channels                      | Active collaboration |
| **Chris Hood (Noematic AI)**                  | Advisor; co-marketing via Noematic book launch (Apr 2026) | Active               |

## The Team

| Person             | Role            | Background                                                                                                                    |
| ------------------ | --------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **David Youssef**  | CEO / Architect | AI systems engineering, full-stack platform design, 12-repo ecosystem architect                                               |
| **Igor Malovitsa** | CTO             | 8+ years Senior Eng at DataArt, CTO obox.systems (Rust), MSc Experimental Nuclear Physics, cryptography, blockchain/Substrate |

**Advisor:** Chris Hood (ex-Google 7yr, Noematic AI) -- co-marketing and endorsement via Noematic book launch (April 2026).

## The Ask

**$1M angel round at $9M pre-money (10% dilution)** to fund 2 years of runway:

| Category                   | Amount | Details                                                      |
| -------------------------- | ------ | ------------------------------------------------------------ |
| Founder compensation (2yr) | $480K  | Core team (David, Igor, Kristen)                             |
| Engineering hire           | $200K  | 1 senior engineer for multi-lane build                       |
| Legal & compliance         | $120K  | SOC 2 Type I certification, IP protection, corporate counsel |
| Infrastructure + sales     | $160K  | Cloud hosting, CI/CD, conferences, enterprise outreach       |
| Contingency                | $40K   | Buffer for timeline shifts                                   |

**Milestones this funds:**

- First 5 enterprise design partners (target: IBM via Ishwar channel)
- SOC 2 Type I certification
- AWS/Azure Marketplace listings
- Platform One (US gov) Docker compliance

## What You Get

- Working product: Full-stack platform with 13+ screens, live CI pipeline
- Open-source credibility: 12 public repos, Apache 2.0 kernel
- Enterprise-ready auth: SSO (Okta, Entra ID, Google), SCIM provisioning, RBAC
- Compliance packs: SOX, HIPAA, SOC2 ready
- Model-neutral architecture: Works with any LLM provider, including airgapped Ollama deployments

## Platform Demo

**Attached:**

- **Platform Walkthrough GIF** -- Animated demo of the full UI flow covering dashboard, guard lanes, evidence bundles, policy packs, escalation policies, and approval workflows
- **Key Figures** -- TAM/SAM/SOM sizing, revenue scenarios, competitive radar, four-lane architecture, and growth trajectory charts

## Contact

David Youssef
david@guardspine.ai
GitHub: github.com/DNYoussef

---

_This document is confidential and intended for the named recipient only._
