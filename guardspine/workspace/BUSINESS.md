# BUSINESS.md - What We're Building and Why

## GuardSpine: The Business

**One-liner:** Continuous verification infrastructure for AI operations -- evidence bundles, compliance trails, risk-tiered approvals.

**The Great Transition framing:** Previous software: you can MAKE anything. Next software: you can VERIFY anything. GuardSpine is the verification layer. (Karpathy insight)

**Problem (3 layers):**

1. **Today (code governance):** Companies adopting AI coding assistants (Copilot, Cursor, Claude Code) have zero governance over what AI writes, approves, and deploys. Existing code review tools review code. GuardSpine GOVERNS the process.

2. **Tomorrow (custom software audit):** CFOs want to replace SaaS with AI-built custom software. Custom code has no vendor, no CVE database, no security patches, no community review. GuardSpine fills that vacuum.

3. **Next (operation verification):** Companies become graphs of algorithms run by AI (Miessler's lattice model). Every operation is a node. Every node needs metrics and governance. GuardSpine provides verifiable evidence at every node in the operation graph.

**The core argument:** The ideal number of human employees inside any company is zero. That is the number they're trying to get to. When AI does all the work, who governs the AI? That's GuardSpine. Zero employees is possible. Zero governance is catastrophic.

**Differentiator vs cubic.dev and others:** They review code. We govern the pipeline. Evidence bundles + hash-chained audit trails + compliance rubrics = the difference between "we checked the code" and "we can prove to auditors we checked the code."

**Moat:** Knowledge gets commoditized (skills, open-source models, distillation). Our moat is NOT knowing what to check -- it's the OPERATIONAL INFRASTRUCTURE that does it continuously with tamper-evident evidence chains. You can't replace infrastructure with a markdown file.

## Open-Core Model

| Tier           | What                                                                 | License     | Price   |
| -------------- | -------------------------------------------------------------------- | ----------- | ------- |
| Free           | guardspine-spec, guardspine-kernel, codeguard-action, GitHub Action  | Apache 2.0  | $0      |
| Team ($299/mo) | Dashboard, rubric customization, Slack/Teams alerts                  | Proprietary | $299/mo |
| Org ($999/mo)  | SSO/SAML, compliance packs (SOC2, DORA, EU AI Act), priority support | Proprietary | $999/mo |
| Enterprise     | Custom rubrics, on-prem, SLA, dedicated CSM                          | Proprietary | Custom  |

## GTM Strategy (Pincher Model + Agent-First)

**Bottom-up (Andy's lane):** Engineering managers adopt the free GitHub Action to unblock velocity-crushed teams. PLG flywheel.
**Top-down (Kristen's lane):** CISOs formalize the tool that's already adopted. Enterprise sales.
**Agent-first (emerging lane):** AI agents discover GuardSpine via MCP server, npm package, GitHub Marketplace. Products become APIs consumed by agents, not humans. Agent-discoverable surface matters more than website SEO.

**Distribution priority:** MCP server > GitHub Marketplace > npm package > landing page > Google Ads. Agents find and adopt tools. Humans approve budgets.

**Regulatory catalysts:** EU AI Act (Aug 2025), DORA (Jan 2025), NIS2, SOC2 AI addendums. Each creates compliance demand that GuardSpine fills.

**Insurance catalyst:** As AI replaces human judgment, insurers will require AI governance as a condition of coverage. "Show us your AI governance framework" = "show us your SOC2 report." Evidence bundles ARE this.

## Outreach Pipeline

- **DB:** ~/.claude/outreach/outreach.db
- **Script:** scripts/content-pipeline/outreach_pipeline.py
- **358 prospects**, 173 sent, 15 responded, 13 green signals
- **Three lanes:** INVESTOR (angel fundraising), BUILDER (engineers/platform teams), BUYER (executives/CISOs)
- **Landing pages:** guardspine-landing (Next.js on Railway)
- **Cal.com booking:** cal.com/davidyoussef/guardspine

## Financial Model

- **Cap table (post-raise):** David 40% / Igor 40% / Kristen 2% / Angel 10% / Pool 8%
- **Monthly burn:** $26.5K (David $10K + Igor $10K + ops $6.5K)
- **Runway at $1M raise:** 37+ months
- **Breakeven:** 3 Org customers or 14 Team customers
- **Exit math:** 30x strategic acquirer. David $100M target = $8.33M ARR.

## North Star Metrics (7 KPIs)

| Metric               | What                                | Current | Target          |
| -------------------- | ----------------------------------- | ------- | --------------- |
| WAU (free)           | Weekly active GitHub Action users   | 0       | 100             |
| Trial signups        | guardspine-landing form submissions | 1       | 50              |
| Demo requests        | guardspine-landing demo form        | 0       | 10              |
| MRR                  | Monthly recurring revenue           | $0      | $3K (breakeven) |
| Response rate        | Outreach green signals / sent       | 8.7%    | 15%             |
| Evidence bundles/day | Production governance throughput    | 0       | 100             |
| Test pass rate       | codeguard-action CI health          | 737/737 | 100%            |

## Key Partnerships

| Partner                   | Status      | Value                                       |
| ------------------------- | ----------- | ------------------------------------------- |
| Proprioceptive AI (Logan) | MOU signed  | 55 provisional patents, hardware governance |
| Chris Hood (Noematic AI)  | Advisor     | Google connections                          |
| Christopher Catoya        | Advisor     | open-core strategy, cadCAD/BlockScience     |
| Andy "Mac" Macintosh      | GTM advisor | enterprise sales, Lucky Juicebox CEO        |

## Investor Archetypes

**A - Compliance-Scarred Operator:** Ex-CISO who lived through audit hell. Lead with evidence gap + regulatory clock.
**B - DevTools Founder:** Built and exited dev infra. Lead with architecture + open-core model.
**C - Regulatory-Thesis Investor:** Invests on regulatory catalysts. Lead with compliance calendar + market timing.

## Competitive Landscape

| Company   | What They Do               | Our Edge                                                   |
| --------- | -------------------------- | ---------------------------------------------------------- |
| cubic.dev | AI code review (YC-backed) | We GOVERN, they review. Evidence bundles vs code comments. |
| Snyk      | Security scanning          | We're governance, not scanning. Complementary.             |
| Vanta     | Compliance automation      | We're code-level, they're org-level. Integration target.   |

## Vision: Today -> Tomorrow -> Next

**Today (2026):** Code governance. Free GitHub Action -> paid dashboard + compliance packs. Prove the model.
**Tomorrow (2027):** Operation verification. Govern any AI workflow node, not just code. n8n pipelines, API calls, data transforms -- every node gets evidence.
**Next (2028+):** Governance substrate. The layer under the enterprise operation graph. Financial transactions, hiring decisions, customer support -- all verified. Like a credit score, but for AI governance maturity.

We're not "security software." We're the governance substrate the enterprise operation graph runs on.

## Ideal State (The Algorithm)

This is how we manage ourselves and how our product works for customers:

1. **Define ideal state** -- What does perfect look like? (KPIs, metrics, policies, architecture)
2. **Snapshot current state** -- Where are we right now? (Morning brief, heartbeat checks, DB queries)
3. **Continuous gap closure** -- AI + n8n pipelines migrate current toward ideal, every day
4. **Verification at every step** -- Ideal state criteria ARE verification criteria. Each is discrete, yes/no

The smarter the AI gets, the better it closes gaps. But without ideal state definition, there's nothing to hill-climb against. Without verification criteria, there's no way to measure progress. This is Karpathy's insight applied to business operations.

---

You are not just a chatbot. You are running the operational intelligence layer of this business.
When you check metrics, draft outreach, review repos, or build skills -- you are doing the work of a founding team member.
When you close gaps between current and ideal state -- you are doing the work of a CEO.
