# GuardSpine Alignment Audit (Combined MECE)

Date: 2026-02-23
Sources: Claude Opus audit (5 parallel agents) + Codex audit (cross-system scan)
Scope: Landing pages, portfolio, outreach pipeline, eric-prep, code repos, backend
Method: Deduplicated, organized MECE (Mutually Exclusive, Collectively Exhaustive)

Total findings: 8 categories, 33 unique issues
Severity: 6 Critical, 8 High, 12 Medium, 7 Low

---

## CATEGORY 1: PRICING & TIERS

### [C-PR1] CRITICAL: Three pricing ladders coexist

| Source                           | Free | Starter | Team      | Org          | Enterprise      |
| -------------------------------- | ---- | ------- | --------- | ------------ | --------------- |
| Landing page (live code)         | $0   | $499/mo | $2,000/mo | $12,000/mo   | Custom          |
| eric-prep/10-pricing-bridge-spec | $0   | $499/mo | $2,000/mo | $12,000/mo   | $50,000/mo      |
| CONTEXT-AND-STRATEGY.md (Feb 12) | $0   | --      | $2,000/mo | $5,000/mo    | $12,000/mo      |
| INVESTOR-BRIEF.md                | $0   | --      | Pro $2K   | Business $5K | Enterprise $12K |
| MASTER-CONSOLIDATION.md:338      | $0   | $499/mo | $2K/mo    | $5K/mo       | $12K/mo         |

Refs: SecurityPageContent.tsx:61,78 | 10-pricing-bridge-spec.md:174,191 | MASTER-CONSOLIDATION.md:338

**Root cause**: Starter tier added Feb 19 (Kristen meeting). Old docs not updated.
MASTER-CONSOLIDATION.md was written from memory, not live code.

**Fix**: Pick canonical ladder (landing page = source of truth). Update MASTER-CONSOLIDATION,
INVESTOR-BRIEF, CONTEXT-AND-STRATEGY (stamp as "pre-Starter pivot"). Tier names:
Free / Starter $499 / Team $2K / Org $12K / Enterprise custom.

### [M-PR2] MEDIUM: Annual pricing display ambiguous

Team tier dev page shows "$1,600/mo" for annual which reads as $1,600/year.
Should display "$19,200/yr ($1,600/mo equivalent)".

### [L-PR3] LOW: Platform fee messaging absent from landing page pricing section

eric-prep/02-messaging-reframe says "Platform fee -- govern everything from day one."
Landing page pricing section doesn't mention this differentiator.

---

## CATEGORY 2: NUMBERS & METRICS

### [C-NM1] CRITICAL: Test count -- three different numbers

| Source                                                           | Claims    | Verified?                                       |
| ---------------------------------------------------------------- | --------- | ----------------------------------------------- |
| Landing pages (DevPageContent:35, SecurityPageContent:610)       | 172 tests | YES -- codeguard-action pytest = 172 passed     |
| Outreach CSV, MASTER-CONSOLIDATION.md:107, outreach-batch1.md:14 | 428 tests | NO -- stale, origin unclear                     |
| INVESTOR-BRIEF.md:43                                             | 758 tests | NO -- claimed "full CI pipeline" but unverified |

**Fix**: 172 is the verified codeguard-action number. For full ecosystem, run all test suites
and document: "172 in codeguard-action, X in backend, Y in kernel = Z total." Use verified
total everywhere. Remove 428 and 758 claims immediately.

### [H-NM2] HIGH: Backend route count is 210+, not "149+"

Docs claim "149+ API endpoints" (MASTER-CONSOLIDATION:137, GuardSpine README:359,392,
outreach pipeline lines 79,1034,1046,1076). Actual `@router.` decorator count in
backend/app/routers/: **210**. Plus routes in services and main.

**Fix**: Update to "210+ API routes" everywhere, or re-count precisely and use exact number.

### [H-NM3] HIGH: Gross margins swing 6-12%

| Source                                 | Claims                             |
| -------------------------------------- | ---------------------------------- |
| eric-prep/01-product-definition.md:104 | 87-91% BYOK margins                |
| A2-product-definition.md:104           | 97-99% BYOK margins                |
| eric-prep/04-financial-math.md         | 98%+ gross margin, 97.99% at scale |

**Root cause**: 87-91% likely includes opex allocation; 97-99% is gross margin only.
**Fix**: Reconcile. Use "97%+ gross margins (BYOK model)" for investor pitch. Note
"87-91% fully loaded" if asked about total company margins.

### [H-NM4] HIGH: Outreach KPIs stale in decision docs

MASTER-CONSOLIDATION updated (300/127/10). Still stale (139/42) in:

- eric-prep/07-signal-tracker.md:18
- financial/GuardSpine-SaaS-PnL-Model.md:514-515

**Fix**: Update both files. Add "last verified" date stamp.

### [M-NM5] MEDIUM: "8 Apache 2.0 packages" never enumerated

Claimed 8x in outreach pipeline. Actual OSS repos: guardspine-spec, guardspine-kernel,
guardspine-kernel-py, codeguard-action, guardspine-verify, guardspine-local-council,
guardspine-adapter-webhook, guardspine-connector-template = **8 repos**.
But codeguard-action is MIT, not Apache (see C-LI1).

**Fix**: After resolving license (C-LI1), enumerate the 8 explicitly in a footnote.

### [M-NM6] MEDIUM: ROI calculator sources not linked

DevROICalculator cites CodeRabbit study, Stripe tech debt, NIST multiplier.
ComplianceROICalculator uses Ponemon/GlobalScape, max penalty figures.
No URLs provided for any source. Not independently auditable.

**Fix**: Add source URLs. Frame penalty figures as "maximum" not "expected."

### [M-NM7] MEDIUM: 34 sent prospects have null campaign + null target_segment

DB has 127 sent total: 93 in landing_page_200_feb26, 34 with null campaign.
Contaminates campaign reporting and cohort analysis.

**Fix**: Backfill campaign/segment for 34 uncampaigned records based on send date.

---

## CATEGORY 3: PRODUCT SCOPE CLAIMS

### [C-PS1] CRITICAL: Four guard lanes claimed as shipped -- only CodeGuard exists

| Source                                   | Claims                                                   |
| ---------------------------------------- | -------------------------------------------------------- |
| Portfolio /product/index.astro:9-13      | CodeGuard + PDFGuard + SheetGuard + ImageGuard (current) |
| Outreach messages                        | "PDF, Sheet, Image governance" as shipped                |
| eric-prep/01-product-definition.md:85-86 | "Code governance only" (Phase 1)                         |
| 4tier-pricing-v3.md                      | PDF/Sheet/Image 90% complete, NOT shipped                |

**Fix**: Portfolio: "CodeGuard available now. PDFGuard, SheetGuard, ImageGuard coming H2 2026."
Outreach: remove multi-lane claims from current batch.

### [H-PS2] HIGH: Compliance framework overclaiming

| Framework | In codeguard-action docs | On landing page | In outreach       |
| --------- | ------------------------ | --------------- | ----------------- |
| SOC2      | YES                      | Badge           | Claimed           |
| HIPAA     | YES                      | Badge           | Claimed           |
| PCI-DSS   | YES                      | Badge           | Claimed           |
| DORA      | NO                       | Badge           | "Satisfies Art.6" |
| EU AI Act | NO                       | Badge           | Not claimed       |
| ISO 27001 | NO                       | Badge           | Not claimed       |

**Fix**: Show SOC2/HIPAA/PCI-DSS as "supported". DORA/EU AI Act/ISO 27001 as "roadmap".
Change outreach from "satisfies DORA Art.6" to "designed to support DORA Art.6 evidence
collection." Get external counsel review.

### [H-PS3] HIGH: Integration claims lack free/paid boundary

Landing page claims Jira, Teams, ServiceNow. Backend routes exist. But these are
paid-cloud-only features unavailable in free GitHub Action. No docs clarify boundary.

**Fix**: Add tier labels "(Team)" or "(Org)" next to integration names on landing page.

### [M-PS4] MEDIUM: "Install in 10 minutes" only true for basic Action

Full platform deployment: 1-2 weeks TEAM, 4-6 weeks Enterprise.

**Fix**: "CodeGuard Action: 5 minutes. Full platform: contact us for deployment support."

### [L-PS5] LOW: Real evidence bundle on landing page is truncated stub

JudgmentReceipt shows minimal 3-event bundle, not full multi-model consensus.

### [L-PS6] LOW: Target company size (500+ engineers) missing from portfolio

Eric-prep and A2 both specify 500+ engineers. Portfolio omits it.

---

## CATEGORY 4: DOMAINS & URLs

### [C-DU1] CRITICAL: Dead domains hardcoded in runtime code

guardspine.io and guardspine.dev do not resolve. Still emitted by backend code:

| File                                                 | Line        | URL                                                         |
| ---------------------------------------------------- | ----------- | ----------------------------------------------------------- |
| backend/app/routers/connectors.py                    | 217         | https://guardspine.io{connector.webhook_url}                |
| backend/app/services/connector_service.py            | 232         | https://guardspine.io/api/v1/connectors/                    |
| backend/app/services/export_service.py               | 380         | https://guardspine.io                                       |
| backend/app/services/sarif_exporter.py               | 504         | https://guardspine.io                                       |
| backend/app/models/policy_schemas.py                 | 415         | https://guardspine.io                                       |
| backend/codeguard/intoto.py                          | 13          | guardspine.dev                                              |
| backend/codeguard/sigstore.py                        | 78          | guardspine.dev                                              |
| backend/app/db/seed.py                               | 374,406,437 | admin@guardspine.io, legal@guardspine.io, cfo@guardspine.io |
| backend/app/services/auth_service.py                 | 238,249,262 | admin/approver/viewer@guardspine.io                         |
| backend/app/core/schemas/evidence-bundle.schema.json | 3           | https://guardspine.dev/schemas/...                          |

**Fix**: Replace all with env-driven `GUARDSPINE_BASE_URL` defaulting to `https://guardspine.ai`.
For email addresses, use `@guardspine.ai`. For schema $id, use `https://guardspine.ai/schemas/...`.

### [M-DU2] MEDIUM: Domain references in docs not normalized

Live routing uses guardspine.ai and guardspine.com. Planning docs still reference .dev/.io:

- eric-prep/09-landing-page-plan.md:14
- eric-prep/11-landing-page-content.md:93
- investor/INVESTOR-BRIEF.md:143
- eric-prep/08-demo-script.md (references guardspine.dev/security)

**Fix**: Find/replace guardspine.dev and guardspine.io -> guardspine.ai in all docs.

### [M-DU3] MEDIUM: CalCom URLs use different user IDs

Portfolio: cal.com/davidyoussef/guardspine
Insights page: cal.com/dyoussef/guardspine-consult
(dnyoussef vs dyoussef)

**Fix**: Verify which CalCom account is correct, standardize everywhere.

---

## CATEGORY 5: CAMPAIGN & ATTRIBUTION

### [C-CA1] CRITICAL: Campaign ID fragmentation -- DB != UTM params

| System                              | Campaign identifier          |
| ----------------------------------- | ---------------------------- |
| DB (200 records)                    | landing_page_200_feb26       |
| campaign_200.py:36 constant         | landing_page_200_feb26       |
| compose_messages.py:26 constant     | landing_page_200_feb26       |
| campaign_200.py:109 URL builder     | dev100_feb26 / ciso100_feb26 |
| compose_messages.py:396 URL builder | dev100_feb26 / ciso100_feb26 |
| update_contacted_messages.py:25     | ciso100_feb26                |

**Impact**: Analytics dashboard will show dev100_feb26 and ciso100_feb26 as UTM campaigns,
but DB tracks everything under landing_page_200_feb26. Conversion attribution is broken.

**Fix**: Normalize. Either UTM campaign = landing_page_200_feb26 (match DB),
or use sub-campaigns: landing_page_200_feb26_dev / landing_page_200_feb26_ciso.
Update URL builders in campaign_200.py, compose_messages.py, update_contacted_messages.py.

---

## CATEGORY 6: LICENSING & LEGAL

### [C-LI1] CRITICAL: MIT vs Apache 2.0 license contradiction

| Source                               | Says                    |
| ------------------------------------ | ----------------------- |
| codeguard-action repo LICENSE        | MIT                     |
| All other 13 repos                   | Apache 2.0              |
| Landing page SecurityPageContent.tsx | MIT                     |
| Outreach pipeline (line 1012)        | MIT                     |
| Outreach pipeline (lines 79, 942)    | "8 Apache 2.0 packages" |
| INVESTOR-BRIEF.md                    | Apache 2.0              |

**Fix**: Either move codeguard-action to Apache 2.0, or explicitly document the split.
Update landing page and outreach to match. If dual-license, document clearly.

### [M-LI2] MEDIUM: DORA compliance claims without legal validation

Outreach says bundles "satisfy DORA Art.6 ICT risk management." No external counsel review.

**Fix**: Revise to "designed to support" not "satisfies." Get counsel review.

### [L-LI3] LOW: Copyright years range 2024-2026 across repos

Not functional but looks unprofessional in enterprise audits.
**Fix**: Batch update to 2026 in next coordinated release.

---

## CATEGORY 7: MESSAGING & TERMINOLOGY

### [M-MS1] MEDIUM: "Evidence bundle" vs "Judgment receipt"

Portfolio uses "evidence bundle" externally. eric-prep/02-messaging-reframe says use
"judgment receipt" for CISOs. Landing security page correctly uses "judgment receipt."

**Fix**: Portfolio CISO-facing pages -> "judgment receipt." Keep "evidence bundle" for
technical/developer contexts only.

### [M-MS2] MEDIUM: Buyer persona split -- portfolio builder-first, strategy says CISO

Portfolio product page CTAs are builder-focused ("Install", "Read Docs").
Eric-prep explicitly says CISO is primary buyer ("follow the money").

**Fix**: Add CISO-specific CTA to portfolio product page.

### [L-MS3] LOW: Guard lane naming inconsistent

CodeGuard vs Code Guard vs code_guard vs code-guard across systems.
**Fix**: Standardize to CamelCase product names (CodeGuard, PDFGuard, etc.).

### [L-MS4] LOW: "Tamper-proof" vs "tamper-evident"

Marketing uses "tamper-proof." Technically correct term is "tamper-evident."
**Fix**: Use "tamper-proof" for marketing (per 02-messaging-reframe). Note "tamper-evident"
only in technical specs.

### [L-MS5] LOW: Igor tenure "8 years" vs "8.5 years" at DataArt

**Fix**: Standardize to "8+ years at DataArt."

---

## CATEGORY 8: DOCUMENTATION FRESHNESS

### [H-DF1] HIGH: Signal tracker 3 days stale

eric-prep/07-signal-tracker.md dated Feb 20. Current date Feb 23.
Phil Venables, Brent Foster, Catoya status may have changed.

**Fix**: Update before Feb 26 meeting.

### [M-DF2] MEDIUM: PII-Shield docs duplicated across 4 READMEs

codeguard-action, verify, local-council, adapter-webhook all describe PII-Shield
independently. Will drift.

**Fix**: Create canonical PII-Shield integration guide, link from all.

### [L-DF3] LOW: Spec version header says v0.2.0 "canonical" but v0.2.1 is latest

**Fix**: Update spec README header to "v0.2.1."

### [L-DF4] LOW: CONTEXT-AND-STRATEGY.md uses pre-Starter pricing model

**Fix**: Add header: "CAUTION: Pre-Starter pivot (Feb 12). Current pricing in eric-prep/10."

---

## WHAT IS ALIGNED (Verified Clean)

1. Live two-page routing (/dev, /security) implemented and consistent
2. MASTER-CONSOLIDATION outreach DB metrics match live DB (300/127/10)
3. Repo-scope wording explicit (14 GuardSpine-scoped / 37 total)
4. Bundle spec v0.2.0/v0.2.1 consistent across all kernel/verify repos
5. Cross-language parity (byte-identical hashes) verified via golden vectors
6. Error codes consistent across TS and Python kernels
7. README install instructions valid (npm/pip commands correct)
8. Portfolio blog posts accurate (19 posts, last commit Feb 10)
9. Pipeline script count accurate (25 Python scripts)

---

## FIX PRIORITY (Before Feb 26 Eric Intro)

| Priority  | ID          | Fix                                                                     | Est. Time  |
| --------- | ----------- | ----------------------------------------------------------------------- | ---------- |
| 1         | C-PR1       | Canonical pricing ladder -> update MASTER-CONSOLIDATION, INVESTOR-BRIEF | 30 min     |
| 2         | C-NM1       | Verify test count, pick one number, update all refs                     | 1 hr       |
| 3         | C-PS1       | Add "coming H2 2026" to PDFGuard/SheetGuard/ImageGuard everywhere       | 30 min     |
| 4         | C-LI1       | Standardize license claim in landing page + outreach                    | 30 min     |
| 5         | C-DU1       | Replace dead domains in backend code with env-driven URL                | 2 hr       |
| 6         | C-CA1       | Normalize campaign IDs (DB = UTM)                                       | 1 hr       |
| 7         | C-NM3/H-NM3 | Reconcile gross margins, pick one investor number                       | 15 min     |
| 8         | H-PS2       | Fix compliance badges (3 supported, 3 roadmap)                          | 30 min     |
| 9         | H-NM2       | Update route count 149 -> 210+                                          | 15 min     |
| 10        | H-NM4       | Update stale KPIs in signal-tracker + financial model                   | 30 min     |
| 11        | M-DU2       | Find/replace dead domains in docs                                       | 30 min     |
| 12        | H-DF1       | Update signal tracker to Feb 23                                         | 30 min     |
| **Total** |             |                                                                         | **~8 hrs** |

---

## RECOMMENDED PROCESS CHANGE

Create a **CLAIMS-REGISTRY.md** file (single source of truth for all quantitative claims):

- Pricing tiers + amounts
- Test count + scope + last-run date
- Route/endpoint count + count method + last-verified date
- License per repo
- Compliance frameworks + status (supported/roadmap)
- Canonical domain
- Campaign ID policy
- Gross margin definition

All generators, docs, and outreach templates reference this file.
Prevents drift by design.
