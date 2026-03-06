# GuardSpine Ecosystem -- Master Consolidation

Last updated: 2026-03-02
Covers: all code, websites, strategy docs, outreach, and portfolio

---

## 1. WHERE EVERYTHING LIVES

### Code Repositories (14 GuardSpine-scoped projects out of 37 total repos on D:\Projects\)

| #   | Project                       | Path                                         | Lang        | Purpose                                                           | Last Modified |
| --- | ----------------------------- | -------------------------------------------- | ----------- | ----------------------------------------------------------------- | ------------- |
| 1   | **GuardSpine** (monorepo)     | `D:\Projects\GuardSpine\`                    | Py+TS+React | Platform: backend, frontend dashboard, connectors, evidence packs | Feb 16        |
| 2   | guardspine-kernel             | `D:\Projects\guardspine-kernel\`             | TypeScript  | Canonical trust anchor, bundle seal/verify                        | Feb 11        |
| 3   | guardspine-kernel-py          | `D:\Projects\guardspine-kernel-py\`          | Python      | Python port, byte-identical hashes                                | Feb 11        |
| 4   | codeguard-action              | `D:\Projects\codeguard-action\`              | Python      | GitHub Action, multi-model review, L0-L4 risk                     | Feb 17        |
| 5   | guardspine-spec               | `D:\Projects\guardspine-spec\`               | TS/JSON     | Bundle spec v0.2.1, golden vectors, schemas                       | Feb 13        |
| 6   | guardspine-verify             | `D:\Projects\guardspine-verify\`             | Python      | CLI verification tool (PyPI)                                      | Feb 13        |
| 7   | guardspine-product            | `D:\Projects\guardspine-product\`            | Python      | Code/PDF/Image/Sheet Guards, decision engine                      | Feb 12        |
| 8   | guardspine-local-council      | `D:\Projects\guardspine-local-council\`      | Python      | Ollama-based local AI review council                              | Feb 13        |
| 9   | guardspine-openclaw           | `D:\Projects\guardspine-openclaw\`           | JavaScript  | OpenClaw integration plugin                                       | Feb 12        |
| 10  | guardspine-adapter-webhook    | `D:\Projects\guardspine-adapter-webhook\`    | TypeScript  | Webhook adapter, PII-Shield WASM                                  | Feb 13        |
| 11  | guardspine-connector-template | `D:\Projects\guardspine-connector-template\` | TS+Py       | Template for custom connectors                                    | Feb 6         |
| 12  | guardspine-quickstart-test    | `D:\Projects\guardspine-quickstart-test\`    | Python      | Quick-start integration test app                                  | Feb 17        |
| 13  | guardspine-landing            | `D:\Projects\guardspine-landing\`            | Next.js 16  | A/B landing pages (dev vs CISO)                                   | **Feb 22**    |
| 14  | n8n-nodes-guardspine          | `D:\Projects\n8n-nodes-guardspine\`          | TypeScript  | 7 n8n custom nodes + credentials                                  | Feb 15        |

### Websites (3 live sites)

| Site                   | Domain                         | Framework       | Path                               | Purpose                                         | Last Commit |
| ---------------------- | ------------------------------ | --------------- | ---------------------------------- | ----------------------------------------------- | ----------- |
| **Landing Pages**      | guardspine.ai / guardspine.com | Next.js 16      | `D:\Projects\guardspine-landing\`  | A/B test: /dev (developers) + /security (CISOs) | Feb 22      |
| **Platform Dashboard** | Internal (Railway)             | React 19 + Vite | `D:\Projects\GuardSpine\frontend\` | SaaS product UI for Starter+ tiers              | Feb 16      |
| **Portfolio**          | dnyoussef.com                  | Astro 4         | `D:\Projects\dnyoussef-portfolio\` | Personal brand + GuardSpine showcase            | Feb 10      |

### Strategy & Business Docs (Desktop)

| Directory      | Path                             | Files               | Last Modified |
| -------------- | -------------------------------- | ------------------- | ------------- |
| **eric-prep/** | `Desktop\guardspine\eric-prep\`  | 17 docs             | **Feb 22**    |
| strategy/      | `Desktop\guardspine\strategy\`   | 7 docs              | Feb 12        |
| assessment/    | `Desktop\guardspine\assessment\` | 20 docs             | Feb 13        |
| financial/     | `Desktop\guardspine\financial\`  | 13 files            | Feb 19        |
| investor/      | `Desktop\guardspine\investor\`   | 35 files (17MB)     | Feb 19        |
| reference/     | `Desktop\guardspine\reference\`  | 115 files           | Feb 17        |
| research/      | `Desktop\guardspine\research\`   | 11 files            | Feb 13        |
| Root files     | `Desktop\guardspine\`            | 8 files + 7 subdirs | Feb 21        |

### Outreach Pipeline

| Component        | Path                                                                   | Description                                                        |
| ---------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Pipeline scripts | `C:\Users\17175\scripts\content-pipeline\`                             | 25 Python scripts (outreach_pipeline.py = 2595 lines)              |
| Database         | `C:\Users\17175\.claude\outreach\outreach.db`                          | SQLite: 358 prospects, 173 sent, 15 responded (queried 2026-03-02) |
| Campaign data    | `C:\Users\17175\data\content-pipeline\`                                | CSVs, JSON batches, LinkedIn batches                               |
| Narrowcast plan  | `C:\Users\17175\.claude\outreach\NARROWCAST-UNIFIED-EXECUTION-PLAN.md` | 12-week strategic plan                                             |
| Learned patterns | `C:\Users\17175\scripts\content-pipeline\OUTREACH-LEARNED-PATTERNS.md` | v1.3.0, 10 patterns                                                |
| Lib modules      | `C:\Users\17175\scripts\content-pipeline\lib\`                         | 9 reusable libraries                                               |

---

## 2. TIMELINE (Recent Activity, Reverse Chronological)

### Week of Mar 2 (CURRENT)

| Date      | What                          | Where                    | Detail                                                                                                      |
| --------- | ----------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------- |
| **Mar 2** | Kristen Team Sync #2 (1hr)    | Desktop/guardspine/      | Full transcript. Kristen: 2% equity (no cash). HumanX April. Netflix pilot. Pitch deck Apr 1.               |
| **Mar 2** | Signal tracker updated        | eric-prep/07             | 358 prospects, 173 sent, 15 responded, 13 green. 6 new entries.                                             |
| **Mar 2** | Financial models updated      | eric-prep/04, financial/ | Burn: $26.5K (Kristen equity-only, no AI budget). Runway: 37+ months. Cap table: 40/40/2/10/8 (post-raise). |
| **Mar 2** | Follow-ups sent               | email + LinkedIn         | Brent Foster (LinkedIn DM), Phil Venables (email), Andy Ellis (email re: Mar 9 trial).                      |
| **Mar 2** | Eric Skiff meeting booked     | email                    | Tue Mar 3, 4-5pm ET. Igor CC'd.                                                                             |
| **Mar 2** | Business formation calendared | Google Calendar          | Wed Mar 4. LLC/C-Corp, EIN, operating agreement, cap table, bank.                                           |

### Week of Feb 17-23

| Date       | What                                             | Where               | Detail                                                           |
| ---------- | ------------------------------------------------ | ------------------- | ---------------------------------------------------------------- |
| **Feb 22** | UI/UX spec, compliance checklist, exec summary   | eric-prep/          | A11 docs: compliance, ROI (developer + compliance), exec summary |
| **Feb 22** | Landing page ROI fixes                           | guardspine-landing  | Fixed fabricated ROI numbers, dev ROI reframed to time-saved     |
| **Feb 21** | Eric-prep package complete                       | eric-prep/          | README, product definition, pricing bridge, LP content finalized |
| **Feb 21** | Product definition v2                            | Desktop/guardspine/ | A2-product-definition.md refinement                              |
| **Feb 20** | Messaging reframe + outreach drafts              | Desktop/guardspine/ | A13-messaging-reframe.md + investor outreach templates           |
| **Feb 20** | Competitive landscape, demo script, Seven Powers | eric-prep/          | Docs 03, 06, 07, 08 completed                                    |
| **Feb 19** | Kristen meeting (1hr 20min)                      | Desktop/guardspine/ | Full transcript, action items, prep docs                         |
| **Feb 19** | Financial model update                           | financial/          | SaaS model v2, benchmark research                                |

### Week of Feb 10-16

| Date       | What                            | Where                          | Detail                                                              |
| ---------- | ------------------------------- | ------------------------------ | ------------------------------------------------------------------- |
| **Feb 16** | Christopher Catoya meeting      | Desktop/guardspine/            | Open-core advisor, Gene Lens interest, Sybil-resistant ID crossover |
| **Feb 16** | Outreach patterns v1.3 CRITICAL | OUTREACH-LEARNED-PATTERNS.md   | Pre-flight checklist for external sends (Pattern #10)               |
| **Feb 16** | Igor follow-up emails           | --                             | Sent PR example + evidence bundle to Ishwar and Jacob               |
| **Feb 15** | GuardSpine monorepo updates     | D:\Projects\GuardSpine\        | Backend, frontend, security hardening                               |
| **Feb 13** | v3 tier assessment              | Desktop/guardspine/assessment/ | FREE 100%, TEAM 1-2wk, ORG 2-3wk, ENT 8-12wk                        |
| **Feb 13** | CI pipeline fix (3 PRs merged)  | codeguard-action               | 428 tests pass, v1.0.1 shipped                                      |
| **Feb 13** | PII-Shield integration          | 4 repos                        | 4 PRs merged (Ilya), WASM-first mode                                |
| **Feb 12** | Strategy docs consolidation     | Desktop/guardspine/strategy/   | CONTEXT-AND-STRATEGY, EXECUTION-PLAN finalized                      |
| **Feb 11** | Kernel updates                  | guardspine-kernel, kernel-py   | CodeGuard workflow dogfooding                                       |
| **Feb 10** | "$285B Crash" blog post         | dnyoussef-portfolio            | Blog + banner image                                                 |

### Week of Feb 3-9

| Date      | What                      | Where               | Detail                                           |
| --------- | ------------------------- | ------------------- | ------------------------------------------------ |
| **Feb 9** | Narrowcast execution plan | outreach DB         | 12-week plan, 6 design principles, Schematron-3B |
| **Feb 4** | Portfolio accuracy fixes  | dnyoussef-portfolio | Open-core repo map corrections                   |
| **Feb 3** | Portfolio v0.2.0 update   | dnyoussef-portfolio | 9 GuardSpine pages, header fix                   |

---

## 3. WORKSTREAM STATUS

### A. Code Platform (14 repos)

**Overall**: 737 tests across 5 repos (172 codeguard-action, 489 backend, 32 kernel-ts, 29 kernel-py, 15 local-council). v0.2.1 bundle spec stable. Open-core model shipping. (Verified 2026-02-23)

| Tier       | Done         | Time to Ship | Blockers                |
| ---------- | ------------ | ------------ | ----------------------- |
| FREE       | 7/7 (100%)   | SHIPPING     | None -- live on GitHub  |
| TEAM       | 8-9/11 (80%) | 1-2 weeks    | Integration + QA only   |
| ORG        | 8-9/10 (85%) | 2-3 weeks    | PDF export + polish     |
| ENTERPRISE | 2-3/7 (35%)  | 8-12 weeks   | Airgap deployment, SAML |

**Open PRs**: codeguard-action #6 (Ilya, PII exception handling), local-council #2 (Ilya, fail-closed)

### B. Landing Pages (guardspine.ai)

**Status**: LIVE. Deployed on Railway via GitHub auto-deploy.

| Page      | URL                    | Audience          | CTA                                | Analytics           |
| --------- | ---------------------- | ----------------- | ---------------------------------- | ------------------- |
| Developer | guardspine.ai/dev      | CTOs, engineers   | Install GitHub Action / Free trial | Plausible + Clarity |
| Security  | guardspine.ai/security | CISOs, compliance | Request demo (email+company+title) | Plausible + Clarity |

**Tech**: Next.js 16, Tailwind 4, SQLite for email capture, host-based middleware routing.
**Domains**: guardspine.ai (primary, CISO default), guardspine.com (dev default). DNS on Namecheap.
**Recent fixes**: ROI calculator numbers corrected (Feb 22), domain refs consolidated to .ai.

### C. Platform Dashboard (GuardSpine/frontend)

**Status**: Active development. React 19 + Vite + TypeScript.

**Components**: Dashboard analytics, guard lane visualization, evidence search/export, compliance reports (SOC2/DORA/HIPAA), rubric builder, SSO/SAML auth, Slack/Jira/Teams integrations.

**Backend**: FastAPI at `D:\Projects\GuardSpine\backend\`. 210 API routes, 9 DB tables with Alembic migrations. (Verified 2026-02-23)

### D. Portfolio Website (dnyoussef.com)

**Status**: 75% complete. Astro 4, Railway deployment.

**GuardSpine content** (9 pages):

- /product (main), /product/install, /product/docs, /product/open-core
- /guardspine/artifacts, /guardspine/assess, /guardspine/insights
- /assess (assessment wizard), /demo

**Blog**: 19 posts. Most recent: "$285B Crash Predicted Our Product" (Feb 10).

**Interactive components**: ProductAssessmentWizard, ROICalculator, ExploreChat, DiagnosticWizard.

### E. Eric Prep Package (Desktop/guardspine/eric-prep/)

**Status**: COMPLETE. Used for Eric Skiff intro (Feb 24) and meeting prep (Mar 3).

| #   | Doc                             | Status                                                          |
| --- | ------------------------------- | --------------------------------------------------------------- |
| 01  | Product definition              | DONE                                                            |
| 02  | Messaging reframe               | DONE                                                            |
| 03  | Competitive landscape           | DONE                                                            |
| 04  | Financial math                  | DONE (updated Mar 2: Kristen equity, burn rate)                 |
| 05  | VC objections                   | DONE                                                            |
| 06  | Seven Powers                    | DONE                                                            |
| 07  | Signal tracker                  | **LIVE** (updated Mar 2: 358 prospects, 15 responded, 13 green) |
| 08  | Demo script                     | TODO (Igor)                                                     |
| 09  | Landing page plan               | DONE (pages are live)                                           |
| 10  | Pricing bridge spec             | DONE                                                            |
| 11  | Landing page content            | DONE                                                            |
| 12  | UI/UX spec                      | DONE                                                            |
| A11 | Compliance + ROI + Exec summary | DONE                                                            |

**Next use**: Investor pitch deck (outline Mar 3, final Apr 1). Eric-prep package feeds directly into deck content.

### F. Outreach Pipeline

**Status**: Active. Campaign "landing_page_200_feb26" in execution.

> DB snapshot: 2026-03-02. Query: `SELECT ... FROM prospects` on `~/.claude/outreach/outreach.db`

| Metric                                      | Value         |
| ------------------------------------------- | ------------- |
| Total prospects                             | **358**       |
| Messages sent (message_sent_at IS NOT NULL) | **173** (48%) |
| Responses (response_received=1)             | **15**        |
| Green signals (signal_type='green')         | **13**        |
| Yellow signals                              | **2**         |
| investor_score >= 75                        | **44**        |
| Response rate                               | **8.7%**      |

**Lane breakdown** (all 358):

| Lane      | Count |
| --------- | ----- |
| buyer     | 178   |
| builder   | 125   |
| investor  | 42    |
| connector | 13    |

**Segment breakdown** (all 358):

| Segment         | Count |
| --------------- | ----- |
| ciso            | 117   |
| developer       | 107   |
| (uncategorized) | 134   |

**Channel breakdown** (173 sent):

| Channel          | Sent |
| ---------------- | ---- |
| email            | 111  |
| linkedin_dm      | 29   |
| linkedin_connect | 6    |
| other            | 27   |

**Landing pages** (live since Feb 20):

- 1 signup (Andy Ellis, dev-page Starter trial)
- 0 demo requests
- 74 unique humans (30d, Clarity)
- /security outperforming /dev by 33% (validates CISO-first hypothesis)

**DB tables**: prospects, weekly_metrics, activity_log, narrowcast_threads, narrowcast_scans, sqlite_sequence

**Infrastructure**: outreach_pipeline.py (2595 lines), 9 lib modules, SQLite DB, 6 JSON batch files.
**Quality gates**: Swap test, slop audit (26 banned terms), coherence evaluation, industry framework mapping.
**Critical guardrail**: Pattern #10 -- pre-flight checklist mandatory before any external send.

---

## 4. HOW SYSTEMS CONNECT

```
Portfolio (dnyoussef.com)
  |-- 9 GuardSpine pages (product showcase)
  |-- ProductAssessmentWizard -> cal.com/davidyoussef/guardspine
  |-- Blog posts (thought leadership -> outreach content)
  |
Landing Pages (guardspine.ai)
  |-- /dev -> Free trial signup (email capture -> SQLite)
  |-- /security -> Demo request (email+company+title -> SQLite)
  |-- UTM tracking -> campaign attribution
  |
Outreach Pipeline
  |-- Messages link to guardspine.ai/dev OR guardspine.ai/security
  |-- UTM params: source, campaign (landing_page_200_feb26), content (unique per prospect)
  |-- Portfolio artifacts referenced: vision-brief.pdf, platform-strategy.pdf
  |
Platform Dashboard (GuardSpine/frontend + backend)
  |-- The actual SaaS product visitors sign up for
  |-- Evidence bundles from codeguard-action flow here
  |
Eric Prep Package
  |-- Landing page content (doc 11) -> implemented in guardspine-landing
  |-- Demo script (doc 08) -> uses guardspine-quickstart-test repo
  |-- Financial math (doc 04) -> feeds investor conversations
  |-- Signal tracker (doc 07) -> tracks TD Bank, Phil Venables, etc.
  |
Code Repos (14 projects)
  |-- codeguard-action: ships as GitHub Action (FREE tier, self-serve)
  |-- guardspine-landing: marketing site
  |-- GuardSpine monorepo: platform product (TEAM+ tiers)
  |-- Kernels + spec + verify: open-source trust layer
```

---

## 5. ACTION ITEMS (Consolidated, Prioritized)

### TIER 1 -- This Week (Mar 3-9)

| #   | Action                                                                    | Owner      | Source             | Status                             |
| --- | ------------------------------------------------------------------------- | ---------- | ------------------ | ---------------------------------- |
| 1   | Eric Skiff meeting (Tue Mar 3, 4pm ET)                                    | David+Igor | Kristen intro      | SCHEDULED                          |
| 2   | Christopher Catoya follow-up (Tue Mar 3, 9am)                             | David      | Back from Ecuador  | TODO                               |
| 3   | Pitch deck outline -- Word/bullets, 10 slides max                         | David      | Mar 2 Kristen sync | TODO (Mar 3, 11am)                 |
| 4   | Business formation: LLC/C-Corp, EIN, operating agreement, cap table, bank | David      | Mar 2 Kristen sync | TODO (Mar 4)                       |
| 5   | Formalize Kristen advisor agreement (2% equity, no cliff, no cash)        | David      | Mar 2 Kristen sync | PENDING (after business formation) |
| 6   | **Andy Ellis trial access ready (Mon Mar 9 HARD DEADLINE)**               | Igor+David | Email commitment   | CRITICAL                           |
| 7   | Brent Foster follow-up (sent Mar 2 via LinkedIn)                          | David      | Ongoing            | SENT, MONITORING                   |
| 8   | Phil Venables follow-up (sent Mar 2 via email)                            | David      | Ongoing            | SENT, MONITORING                   |

### TIER 2 -- Next 2 Weeks (Mar 10-21)

| #   | Action                                                                  | Owner       | Source             |
| --- | ----------------------------------------------------------------------- | ----------- | ------------------ |
| 9   | Collect engineer feedback + testimonials (Eric, Mark, Andy Ellis, Ilya) | David       | Mar 2 Kristen sync |
| 10  | Kristen sync #3 (Tue Mar 10, 2pm ET)                                    | All 3       | Mar 2 meeting      |
| 11  | Netflix pilot follow-up (target: pilot this month)                      | Via Kristen | Mar 2 meeting      |
| 12  | Pitch deck pressure test with AI personas (Mar 20)                      | David+Igor  | Mar 2 Kristen sync |
| 13  | Ilya fixes codeguard-action PR #6 (PII exception handling)              | Ilya        | Known Issues       |
| 14  | Ilya fixes local-council PR #2 (fail-closed)                            | Ilya        | Known Issues       |

### TIER 3 -- Pre-HumanX (Mar 22 - Apr 1)

| #   | Action                                              | Owner      | Source             |
| --- | --------------------------------------------------- | ---------- | ------------------ |
| 15  | HumanX conference prep -- all materials due Mar 27  | David+Igor | Mar 2 Kristen sync |
| 16  | **Investor pitch deck FINAL -- Apr 1 deadline**     | David+Igor | Mar 2 Kristen sync |
| 17  | Docker image for Platform One (Jacob)               | Igor       | Jacob meeting      |
| 18  | Demonstrate offline mode with Ollama probes (Jacob) | Igor       | Jacob meeting      |

### TIER 4 -- Long-term

| #   | Action                                                             | Owner  | Source                        |
| --- | ------------------------------------------------------------------ | ------ | ----------------------------- |
| 19  | ENTERPRISE tier (airgap, SAML, custom rubrics)                     | Both   | assessment/4tier-pricing-v3   |
| 20  | Ishwar: interviews IBM engineers re governance tool friction       | Ishwar | Ishwar meeting                |
| 21  | PE portfolio distribution channel activation (post first customer) | David  | Strategic Synthesis Thread 11 |

---

## 6. KEY DATES (updated Mar 2)

| Date                       | Event                                      | Notes                                                         |
| -------------------------- | ------------------------------------------ | ------------------------------------------------------------- |
| ~~Thu Feb 26~~             | ~~Kristen Sync #2~~                        | DONE                                                          |
| **Tue Mar 3, 9:00 AM**     | Christopher Catoya follow-up               | Back from Ecuador. Open-core, Andy Mac, SF network            |
| **Tue Mar 3, 11:00 AM**    | Pitch deck outline session                 | Word/bullet outline, 10 slides max (Kristen's direction)      |
| **Tue Mar 3, 4:00 PM ET**  | Eric Skiff meeting (Tanooki Labs)          | Advisory, accelerator intros, trial-to-paid advice. Igor CC'd |
| **Wed Mar 4, 9:00 AM**     | Business formation (LLC/C-Corp)            | EIN, operating agreement, cap table, bank, 83(b), trademark   |
| **Fri Mar 7**              | Kristen advisor agreement formalization    | 2% equity, no cliff, no cash. Depends on business formation   |
| **Mon Mar 9**              | **HARD DEADLINE: Andy Ellis trial access** | Committed in email. First customer. Cannot slip.              |
| **Tue Mar 10, 2:00 PM ET** | Kristen + Igor + David Sync #3             | Deck progress, Eric debrief, Netflix pilot, advisor agreement |
| **Sun Mar 15**             | Netflix pilot status check                 | Kristen's contact re-emerged. Target: pilot THIS month        |
| **Fri Mar 20**             | Pitch deck pressure test (AI personas)     | VC, CISO, CFO personas                                        |
| **Fri Mar 27**             | HumanX conference prep -- materials due    | Deck, one-pager, signal tracker, demo script                  |
| **Wed Apr 1**              | **DEADLINE: Investor pitch deck ready**    | Kristen on VC track at HumanX early April                     |
| Mar 2 (approx)             | CNPD acknowledgment expected               | Luxembourg DPA complaint (lawsuit)                            |
| Jun 30                     | EEOC intake                                | Youssef v. Eurofins (separate from GuardSpine)                |

---

## 7. PEOPLE

| Person                 | Role                             | Compensation                      | Status                           | Key Connection                     |
| ---------------------- | -------------------------------- | --------------------------------- | -------------------------------- | ---------------------------------- |
| David Youssef          | CEO, vision, architecture, IP    | 40% equity (post-raise) + $10K/mo | Full-time                        | --                                 |
| Igor Malovitsa         | CTO, technical co-builder        | 40% equity (post-raise) + $10K/mo | Full-time                        | GitHub: m1el                       |
| Kristen Hengst Smith   | GTM advisor, angel network       | **2% equity, no cliff, no cash**  | Active, sync Mar 10              | HumanX VC track, Netflix contact   |
| Eric Skiff             | Advisory prospect (Tanooki Labs) | TBD                               | Meeting Mar 3 4pm ET             | Kristen intro, accelerator network |
| Phil Venables          | Ballistic Ventures VP            | --                                | Follow-up sent Mar 2             | Awaiting next response             |
| Chris Hood             | Noematic AI, Google connections  | TBD                               | Advisor                          | Cognitive attestation              |
| Christopher Catoya     | cadCAD/BlockScience, open-core   | TBD                               | Follow-up Mar 3                  | Andy Mac intro, SF network         |
| Andy Macintosh         | Enterprise GTM (Lucky Juicebox)  | --                                | Contact via Catoya               | Snyk pincher strategy thesis       |
| Ishwar Chandrasekharan | IBM Z-Inspection                 | --                                | Active                           | Interviewing IBM engineers         |
| Jacob Friedman         | G7/NIST, Permion                 | --                                | **Active -- gov specs provided** | SBOM + P1 + SAM.gov + CSE intro    |
| Logan Napolitano       | Proprioceptive AI                | Revenue share (MOU)               | MOU signed, awaiting countersign | 55 patents, cognitive probes       |
| Ilya Ploskovitov       | PII-Shield WASM contributor      | Volunteer                         | OSS contributor                  | 2 open PRs                         |
| Brent Foster           | TD Bank VP Eng                   | --                                | Follow-up sent Mar 2 (LinkedIn)  | Pilot target (gold signal)         |
| Andy Ellis             | YL Ventures, ex-CSO Akamai       | --                                | **Product signup** Feb 23        | Trial access due Mar 9             |

---

## 8. FINANCIAL SNAPSHOT (updated Mar 2)

- **Angel round target**: $1M (3yr+ runway at $26.5K burn, 3 hires: engineer, lawyer, finance)
- **Monthly burn**: $26.5K (Kristen = 2% equity, no cash, no AI budget -- agreed Mar 2)
- **Runway**: 37+ months at $1M raise
- **BYOK model**: 97-99% gross margins (see 04-financial-math.md)
- **Pricing**: Free / Starter $499/mo / Team $2K/mo / Org $12K/mo / Enterprise custom
- **Breakeven**: M4-M11 depending on scenario (modeled at $35.5K burn, actually faster at $26.5K)
- **Cap table (post-raise)**: David 40% / Igor 40% / Kristen 2% / Angel 10% / Pool 8%
- **Probability**: 57-63% (base 46-49% + AI tailwinds 1.5x)
- **Conditional**: Phil call -> ~0.67 | First customer -> ~0.70 | Ballistic term sheet -> ~0.80

---

## 9. EXISTING INDEXES (Cross-Reference)

| Index                 | Path                                                      | Covers                        |
| --------------------- | --------------------------------------------------------- | ----------------------------- |
| Desktop consolidation | `Desktop\guardspine\00-INDEX.md`                          | Desktop folders only (Feb 17) |
| Eric prep checklist   | `Desktop\guardspine\eric-prep\README.md`                  | Eric prep docs only (Feb 21)  |
| Narrowcast plan       | `~\.claude\outreach\NARROWCAST-UNIFIED-EXECUTION-PLAN.md` | Outreach strategy (Feb 9)     |
| Outreach patterns     | `scripts\content-pipeline\OUTREACH-LEARNED-PATTERNS.md`   | Pipeline guardrails (Feb 16)  |
| **THIS FILE**         | `Desktop\guardspine\MASTER-CONSOLIDATION.md`              | Everything (Feb 23)           |

---

## 10. VERIFICATION METHOD

This document contains metrics from live systems. To prevent drift, every quantitative claim
must be reproducible. When updating this doc, re-run the queries below and stamp the date.

### Outreach DB (most volatile)

```sql
-- Run via: python -c "import sqlite3; ..."
-- DB: C:\Users\17175\.claude\outreach\outreach.db
SELECT COUNT(*) FROM prospects;                                    -- total
SELECT COUNT(*) FROM prospects WHERE campaign='landing_page_200_feb26'; -- in campaign
SELECT COUNT(*) FROM prospects WHERE message_sent_at IS NOT NULL;  -- sent
SELECT COUNT(*) FROM prospects WHERE response_received=1;          -- responded
SELECT COUNT(*) FROM prospects WHERE investor_score >= 75;         -- high-score
SELECT signal_type, COUNT(*) FROM prospects WHERE signal_type != 'none' GROUP BY signal_type;
SELECT lane, COUNT(*) FROM prospects GROUP BY lane;
SELECT target_segment, COUNT(*) FROM prospects GROUP BY target_segment;
SELECT channel, COUNT(*) FROM prospects WHERE message_sent_at IS NOT NULL GROUP BY channel;
```

Last verified: **2026-03-02** (results in Section 3F above)

### Git timestamps

```bash
# Monorepo HEAD
cd /d/Projects/GuardSpine && git log -1 --format="%ai %s"
# Landing pages HEAD
cd /d/Projects/guardspine-landing && git log -1 --format="%ai %s"
# Portfolio HEAD
cd /d/Projects/dnyoussef-portfolio && git log -1 --format="%ai %s"
```

Last verified: **2026-02-23**

### File counts

```bash
ls -1 Desktop/guardspine/research/ | wc -l    # research dir
ls -1 Desktop/guardspine/ | wc -l             # root items (files + dirs)
wc -l scripts/content-pipeline/outreach_pipeline.py  # pipeline LOC
ls -1 scripts/content-pipeline/*.py | wc -l    # pipeline script count
```

Last verified: **2026-02-23**

### Inclusion criteria

- **"14 GuardSpine-scoped repos"**: Any repo in D:\Projects\ where the project name
  contains "guardspine", "codeguard", or "n8n-nodes-guardspine". D:\Projects\ contains
  37 total git repos; only 14 are GuardSpine-scoped.
- **Outreach pipeline scripts**: Python files in `scripts/content-pipeline/*.py` (not lib/).
