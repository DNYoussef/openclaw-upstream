# GuardSpine - Consolidated Desktop Index

Last updated: 2026-02-17

## Directory Structure

| Directory   | Purpose                                      | File Count |
| ----------- | -------------------------------------------- | ---------- |
| strategy/   | Vision, positioning, execution plans         | 7          |
| assessment/ | Build status, audits, remediation            | 20         |
| investor/   | External-facing materials, demos, pitches    | 35         |
| financial/  | Market model, projections                    | 4          |
| reference/  | Technical docs, rubric packs, evidence packs | 115        |

## Files by Directory

### strategy/

| File                      | Status    | Source                      | Description                |
| ------------------------- | --------- | --------------------------- | -------------------------- |
| CONTEXT-AND-STRATEGY.md   | [CURRENT] | guardspine-market-analysis/ | Core strategic positioning |
| EXECUTION-PLAN.md         | [CURRENT] | guardspine-market-analysis/ | Implementation roadmap     |
| build-plan.md             | [CURRENT] | Desktop standalone          | Task swim lanes            |
| mece-synthesis.md         | [CURRENT] | GuardSpine-Audit-Latest/    | MECE analysis synthesis    |
| bplus-plan.md             | [CURRENT] | GuardSpine-Audit-Latest/    | B+ improvement plan        |
| CRITIQUE-AND-PREMORTEM.md | [CURRENT] | guardspine-market-analysis/ | Pre-mortem risk analysis   |
| MARKET-ANALYSIS.md        | [CURRENT] | guardspine-market-analysis/ | Market landscape analysis  |

### assessment/

| File                         | Status    | Source                   | Description                              |
| ---------------------------- | --------- | ------------------------ | ---------------------------------------- |
| 4tier-pricing-v3.md          | [CURRENT] | Desktop standalone       | v3 build status (AUTHORITATIVE)          |
| linus-remediation.md         | [CURRENT] | GuardSpine-Audit-Latest/ | Linus-standard remediation plan          |
| audit-validation.md          | [CURRENT] | GuardSpine-Audit-Latest/ | Audit validation results                 |
| audit-verification-report.md | [CURRENT] | GuardSpine-Audit-Latest/ | Verification report                      |
| execution-plan-2026-02-03.md | [CURRENT] | GuardSpine-Audit-Latest/ | Execution plan (distinct from strategy/) |
| audits-2026-02-03/           | [CURRENT] | GuardSpine-Audit-Latest/ | 15 component audit files                 |

### investor/

| File                       | Status    | Source                         | Description                           |
| -------------------------- | --------- | ------------------------------ | ------------------------------------- |
| INVESTOR-BRIEF.md          | [CURRENT] | Deck-Package/strategy/         | Investor-facing brief                 |
| outreach-batch1.md         | [CURRENT] | Desktop standalone             | Outreach batch 1 contacts             |
| GuardSpine-Pitch-Deck.pptx | [CURRENT] | guardspine-investor-brief/     | Pitch deck                            |
| figures/                   | [CURRENT] | Deck-Package + market-analysis | 18 visualization images               |
| code-samples/              | [CURRENT] | Deck-Package/                  | 6 code examples                       |
| screenshots/               | [CURRENT] | guardspine-screenshots/        | 4 dashboard PNGs                      |
| demo/                      | [CURRENT] | investor-brief + Desktop       | 4 demo assets (GIF, MP4, Slack cards) |

### financial/

| File                                   | Status    | Source                        | Description                       |
| -------------------------------------- | --------- | ----------------------------- | --------------------------------- |
| market-model.xlsx                      | [CURRENT] | guardspine-market-analysis/   | Financial projections spreadsheet |
| generate_model.py                      | [CURRENT] | guardspine-market-analysis/   | Model generation script           |
| GuardSpine-Market-Analysis-2026-Q1.pdf | [CURRENT] | guardspine-market-analysis/   | Q1 2026 market analysis PDF       |
| NOTE-FOR-CONSULTANT.md                 | [CURRENT] | Deck-Package/financial-model/ | Notes for financial consultant    |

### reference/

| Subdirectory    | Contents                                                   |
| --------------- | ---------------------------------------------------------- |
| product-docs/   | 74 files: READMEs, LICENSEs, configs, platform docs, specs |
| rubric-packs/   | 14 YAML rubric templates                                   |
| evidence-packs/ | 26 files: example JSON bundles + golden vectors            |
| NEEDED.md       | Screenshot todo list (from Deck-Package/screenshots/)      |

## Deduplication Log

| Duplicate Found                        | Kept From                           | Removed From                  |
| -------------------------------------- | ----------------------------------- | ----------------------------- |
| 11 audit .md files                     | GuardSpine-Audit-Latest-2026-02-03/ | Deck-Package/strategy/        |
| guardspine-4tier-pricing-assessment.md | Desktop standalone                  | Deck-Package/strategy/        |
| guardspine-build-plan.md               | Desktop standalone                  | Deck-Package/strategy/        |
| CONTEXT-AND-STRATEGY.md                | guardspine-market-analysis/         | Deck-Package/strategy/        |
| EXECUTION-PLAN.md                      | guardspine-market-analysis/         | Deck-Package/strategy/        |
| market-model.xlsx                      | guardspine-market-analysis/         | Deck-Package/financial-model/ |
| MECE-SYNTHESIS                         | GuardSpine-Audit-Latest/            | Deck-Package/strategy/        |
| Bplus-Plan                             | GuardSpine-Audit-Latest/            | Deck-Package/strategy/        |

## Original Source Mapping

Consolidated from:

- Desktop/guardspine-4tier-pricing-assessment.md (standalone)
- Desktop/guardspine-build-plan.md (standalone)
- Desktop/guardspine-investor-outreach-batch1.md (standalone)
- Desktop/guardspine-slack-dm-approval-card.gif (standalone)
- Desktop/guardspine-slack-channel-approval-card.gif (standalone)
- Desktop/GuardSpine-Audit-Latest-2026-02-03/ (21 files)
- Desktop/guardspine-investor-brief/ (GIF, PPTX, MP4)
- Desktop/guardspine-market-analysis/ (8 content files)
- Desktop/GuardSpine-Deck-Package/ (150+ files across 6 subdirs)
- Desktop/guardspine-screenshots/ (4 PNGs)
