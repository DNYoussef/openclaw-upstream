# GuardSpine Execution Plan

## Methodology

This plan follows one rule: dependency order determines execution order.
No work starts until its blockers are resolved. No phase begins until
its gate is passed. Every item traces back to a concrete file or
deliverable.

---

## Current State (Verified 2026-02-11)

### What's Done

| Item                                       | Evidence                                                         |
| ------------------------------------------ | ---------------------------------------------------------------- |
| 302-464 tests passing, 0 failing           | `pytest tests/ backend/tests/`                                   |
| Self-approval bypass closed                | `governance.py`, `escalation/workflow.py`, `approval_service.py` |
| verify_bundle_chain import fixed           | `codeguard/evidence.py:26`                                       |
| Slack webhook uses signature auth, not JWT | `backend/app/routers/slack.py:30`                                |
| Backend tests in pytest gate               | `pytest.ini` testpaths includes `backend/tests`                  |
| Action interface consistent                | `action.yml` + `entrypoint.py` use GitHub convention             |
| Health endpoint pathing correct            | `api-client.ts:168` resolves to `/api/v1/health`                 |
| Financial model parameterized              | `generate_model.py` RISK_FACTORS dict, no hard-coded values      |
| Y1 ARR numbers aligned                     | $1.28M (precise) = $1.3M (rounded), same scenario                |
| Auditor pack export fully implemented      | `codeguard/auditor_pack.py`, 13 tests passing                    |
| Slack integration working                  | Router + service + interactive buttons                           |
| guardspine-kernel-py on PyPI               | Published as `guardspine-kernel`                                 |
| 13 builtin rubrics shipping                | SOC2, HIPAA, PCI-DSS, NASA, Six Sigma, etc.                      |
| 3 policy packs                             | finance-v0.9, health-v0.9, saas-v0.9                             |

### What's Broken or Missing

| #   | Item                                                 | Status           | Blocks                                |
| --- | ---------------------------------------------------- | ---------------- | ------------------------------------- |
| A   | Spec README says 0.2.1, kernels enforce 0.2.0        | OPEN             | External docs, integrator trust       |
| B   | No LICENSE file at GuardSpine repo root              | OPEN             | Open-source credibility, distribution |
| C   | Frontend placeholder pages (BundleDetail, Coverage)  | OPEN             | Pilot demos                           |
| D   | Router hard-codes "api_user" instead of auth context | OPEN             | Self-approval enforcement in prod     |
| E   | Demo/in-memory code paths in backend services        | OPEN (env-gated) | Production deployment                 |
| F   | No SBOM field in evidence bundle spec                | MISSING          | EU CRA compliance positioning         |
| G   | No Sigstore/in-toto attestation format               | MISSING          | CNCF ecosystem, supply chain story    |
| H   | No DORA rubric pack                                  | MISSING          | EU financial sector sales             |
| I   | No VS Code extension                                 | MISSING          | Developer adoption funnel             |
| J   | No Teams bot                                         | MISSING          | Enterprise communication channel      |
| K   | No cloud marketplace listings                        | MISSING          | Enterprise procurement                |
| L   | No ServiceNow integration                            | MISSING          | Compliance budget access              |
| M   | No OPA/Rego rubric runtime                           | MISSING          | IaC governance market                 |
| N   | No ML model governance                               | MISSING          | MLOps market                          |
| O   | No Rubric Hub / marketplace                          | MISSING          | Community lock-in, recurring revenue  |
| P   | No certification program                             | MISSING          | Talent ecosystem, switching costs     |
| Q   | No public validation dashboard                       | MISSING          | Transparency credibility              |
| R   | No standards body submission                         | MISSING          | "The standard" positioning            |
| S   | No Compliance-as-a-Service offering                  | MISSING          | High-margin services revenue          |
| T   | No IaC/Terraform guard lane                          | MISSING          | $2.2B adjacent market                 |

---

## Dependency Graph

```
PHASE 0 (Credibility Reset)
  A: Fix spec docs --------+
  B: Add LICENSE file ------+---> Gate 0: "No self-inflicted wounds"
  C: Fix placeholder pages -+
  D: Auth context in router +

PHASE 1 (Standard Formation)   [requires Gate 0]
  1a: Spec v1.0 freeze --------+
  1b: SBOM field in spec ------+---> Gate 1: "Spec v1.0 GA"
  1c: in-toto attestation fmt -+
  1d: Sigstore signing --------+
  1e: Rubric Hub scaffold -----+

PHASE 2 (Compliance Lanes)     [requires Gate 1]
  2a: DORA rubric pack --------+
  2b: CMMC rubric pack --------+---> Gate 2: "3+ regulated frameworks"
  2c: FDA 21 CFR Part 11 ------+
  2d: OPA/Rego runtime ---------\
  2e: IaC guard lane prototype --+-> Gate 2b: "IaC story works"

PHASE 3 (Distribution)         [requires Gate 1, parallel with Phase 2]
  3a: VS Code extension -------+
  3b: Teams bot ---------------+---> Gate 3: "Developer touchpoints exist"
  3c: AWS Marketplace listing -+
  3d: Public status dashboard --+

PHASE 4 (Revenue Expansion)    [requires Gate 2 + Gate 3]
  4a: Rubric marketplace ------+
  4b: CaaS packages -----------+---> Gate 4: "Revenue diversified"
  4c: Certification program ---+
  4d: Audit export pricing ----+
  4e: ServiceNow integration --+

PHASE 5 (Standards Credibility) [requires Gate 1, long-lead]
  5a: OASIS spec submission ---+
  5b: CNCF sandbox proposal ---+---> Gate 5: "Standards body recognition"
  5c: Reference architectures -+
```

---

## PHASE 0: Credibility Reset

**Duration**: 1-2 days. This is cleanup, not features.
**Gate**: Zero known contradictions, zero missing legal artifacts.

### 0A: Fix Spec Version Documentation

**Problem**: `guardspine-spec/README.md` and `GuardSpine/open-source/guardspine-spec/README.md`
both say version 0.2.1. The TS kernel (`guardspine-kernel`) and Python kernel
(`guardspine-kernel-py`) both enforce version 0.2.0. The Codex audit already removed
phantom 0.2.1 from the schema (commit `4b564e6`), but the README files were not updated.

**Fix**:

- `D:\Projects\guardspine-spec\README.md` line 3: change 0.2.1 to 0.2.0
- `D:\Projects\GuardSpine\open-source\guardspine-spec\README.md` line 3: change 0.2.1 to 0.2.0
- Verify no other files reference 0.2.1 as current (grep all repos)

**Acceptance**: `grep -r "0\.2\.1" D:\Projects\guardspine-spec` returns zero matches
outside of CHANGELOG entries.

### 0B: Add LICENSE File

**Problem**: GuardSpine monorepo has no LICENSE file at root. README claims proprietary.
Open-source components (spec, kernels, rubrics) are Apache 2.0. This creates legal
ambiguity that any diligence review will flag.

**Fix**:

- Add `D:\Projects\GuardSpine\LICENSE` with proprietary license text
- Add `D:\Projects\GuardSpine\open-source\LICENSE` with Apache 2.0
- Verify README license badge matches actual LICENSE file

**Acceptance**: `ls D:\Projects\GuardSpine\LICENSE` exists. Content matches README claim.

### 0C: Frontend Placeholder Pages

**Problem**: `BundleDetailPage.tsx:14`, `CoveragePage.tsx:19`, and `ApprovalDetailPage.tsx:48`
show placeholder text. If shown in a pilot demo, this kills credibility.

**Fix options** (pick one per page):

1. Replace with real data binding (if backend endpoint exists)
2. Replace with "Coming in next release" messaging with release date
3. Remove from navigation entirely and gate behind feature flag

**Acceptance**: No page reachable from the main nav shows `[placeholder]` text.

### 0D: Auth Context in Approval Router

**Problem**: `backend/app/routers/approvals.py` hard-codes `decided_by = "api_user"`
at lines 76, 107, and 134. The self-approval guard we just built in `approval_service.py`
depends on `decided_by` being a real user identifier. With the placeholder, every user
looks like the same person, making the guard inert.

**Fix**:

- Extract user identity from the FastAPI dependency injection (`request.state.user`
  or equivalent from the auth middleware)
- If auth middleware doesn't exist yet: add a `get_current_user` dependency that
  reads from JWT claims or API key lookup
- Fallback: if no auth token present, return 401, not "api_user"

**Dependency**: This requires the auth service to actually set user identity. Check
`backend/app/services/auth_service.py` for current state. If auth is demo-only,
this becomes a Phase 1 item (hardening for pilot) rather than Phase 0.

**Acceptance**: `grep -r "api_user" backend/app/routers/` returns zero matches.

---

## PHASE 1: Standard Formation

**Duration**: Weeks 1-4.
**Gate**: Spec v1.0 published. Evidence bundles are Sigstore-signed in-toto
attestations with optional SBOM field. Rubric Hub scaffold deployed.
**Thesis**: You are not selling a tool. You are selling a standard. Everything
in this phase makes the spec the artifact that matters.

### 1A: Spec v1.0 Freeze

**What**: Promote the current v0.2.0 spec to v1.0.0 with these additions:

- `sbom` field (optional, see 1B)
- `attestation_format` field indicating in-toto compatibility (see 1C)
- `signature` field for Sigstore/Cosign detached signatures (see 1D)
- Formal CHANGELOG with migration notes from 0.2.0
- JSON Schema updated to v1.0.0

**Files**:

- `D:\Projects\guardspine-spec\schemas\evidence-bundle-v1.0.0.schema.json` (new)
- `D:\Projects\guardspine-spec\README.md` (version bump)
- `D:\Projects\guardspine-spec\CHANGELOG.md` (migration notes)
- `D:\Projects\guardspine-kernel\src\schema.ts` (accept v1.0.0)
- `D:\Projects\guardspine-kernel-py\src\guardspine_kernel\schema.py` (accept v1.0.0)

**Backwards compatibility (R3)**: Kernels MUST accept both v0.2.0 and v1.0.0
bundles. v0.2.0 bundles without the new fields remain valid. New fields are
optional with sensible defaults.

**Acceptance**: Both kernels pass existing tests AND new tests for v1.0.0 bundles.

### 1B: SBOM Field in Evidence Bundle

**What**: Add an optional `sbom` object to the evidence bundle schema:

```json
{
  "sbom": {
    "format": "cyclonedx|spdx",
    "version": "1.5",
    "content_hash": "sha256:...",
    "location": "inline|ref:url"
  }
}
```

**Why**: EU Cyber Resilience Act (2027) mandates SBOMs. EU AI Act mandates
governance evidence. A single artifact satisfying both is unique in the market.
Jacob co-authored "SBOM for AI" -- this is his language.

**Files**:

- Schema: `evidence-bundle-v1.0.0.schema.json`
- TS kernel: `src/types.ts` (add SBOMInfo interface)
- Py kernel: `src/guardspine_kernel/types.py` (add sbom dataclass)
- Both kernels: seal/verify ignore sbom field (it's metadata, not hashed content)

**Acceptance**: Bundle with SBOM field validates. Bundle without SBOM field validates.
Round-trip test: create bundle with SBOM, verify, export, re-verify.

### 1C: in-toto Attestation Format

**What**: Evidence bundles can be wrapped as in-toto attestation predicates.
The bundle becomes the `predicate` inside a DSSE envelope.

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{ "name": "artifact.py", "digest": { "sha256": "..." } }],
  "predicateType": "https://guardspine.ai/evidence/v1",
  "predicate": {
    /* existing evidence bundle */
  }
}
```

**Why**: in-toto is CNCF graduated (April 2025). Adopted by PyPI, Maven, NVIDIA NGC,
SolarWinds, Palantir, Autodesk. This format makes evidence bundles consumable by the
entire CNCF supply chain security ecosystem. Kelsey literally said "attestations."

**Files**:

- New: `D:\Projects\guardspine-kernel\src\intoto.ts` (~100 lines)
- New: `D:\Projects\guardspine-kernel-py\src\guardspine_kernel\intoto.py` (~80 lines)
- Functions: `wrap_as_attestation(bundle) -> Statement`, `unwrap_attestation(statement) -> bundle`
- Tests for round-trip, tests for compliance with in-toto spec

**Dependency**: Requires 1A (v1.0 schema) because the predicateType URL includes version.

**Acceptance**: Output validates against in-toto Statement v1 schema.
`cosign verify-attestation` can parse the output (once signed in 1D).

### 1D: Sigstore Signing

**What**: Evidence bundles (in in-toto format) can be signed using Sigstore's
keyless signing via Cosign. This produces a detached signature bundle (.sigstore).

**Why**: Keyless signing means no key management burden on users. The signature
proves WHO created the evidence, WHEN, and that it hasn't been tampered with.
This is the "trust anchor" that makes evidence bundles tamper-evident without
requiring users to manage PKI.

**Files**:

- New: `D:\Projects\guardspine-kernel\src\signing.ts` (shell out to cosign)
- New: `D:\Projects\guardspine-kernel-py\src\guardspine_kernel\signing.py` (subprocess cosign)
- Update: `codeguard-action` to optionally sign bundles in CI

**Dependency**: Requires 1C (in-toto format) because Sigstore signs DSSE envelopes.

**Acceptance**: `cosign verify-attestation --type https://guardspine.ai/evidence/v1`
succeeds on a signed bundle.

### 1E: Rubric Hub Scaffold

**What**: A simple registry for discovering and installing rubrics.
Not a marketplace yet -- just a Git-backed index with metadata.

```
guardspine-rubrics/
  index.json          # registry of all rubrics
  frameworks/
    dora-v1.0.yaml
    cmmc-v2.0.yaml
    fda-21cfr11-v1.0.yaml
  community/
    # empty, ready for contributions
  README.md           # contribution guide
```

**Why**: This is the Terraform Registry pattern. Once compliance teams write
rubrics in GuardSpine's YAML format, switching costs are enormous. The hub
is the moat, not the engine.

**Files**:

- New repo: `guardspine-rubrics` (public, Apache 2.0)
- Seed with existing 13 builtin rubrics from `codeguard/rubrics/builtin/`
- Add `codeguard rubric install <name>` CLI command
- Add `codeguard rubric search <query>` CLI command

**Dependency**: None. Can start immediately, parallel with 1A-1D.

**Acceptance**: `codeguard rubric install soc2` downloads and activates the rubric.

---

## PHASE 2: Compliance Lanes

**Duration**: Weeks 5-12.
**Gate**: 3+ regulated framework rubric packs shipping. IaC prototype working.
**Thesis**: Every new rubric pack opens a new market segment with zero
engine changes. The rubric is the product; the engine is the platform.

### 2A: DORA Rubric Pack

**What**: Rubric pack for Digital Operational Resilience Act compliance.

DORA requires (relevant to GuardSpine):

- ICT risk management with documented change governance (Pillar 1)
- ICT incident reporting with evidence trails (Pillar 2)
- Operational resilience testing with audit artifacts (Pillar 3)

**Rubric rules** (~30 rules covering):

- Change classification against ICT risk framework
- Mandatory review for changes to critical ICT systems
- Evidence of testing before production deployment
- Incident response documentation requirements
- Third-party ICT service provider change governance

**Why**: DORA is enforceable NOW (January 2025). EU AI Act doesn't fully
enforce until August 2026. DORA buyers are spending money today. Germany
alone estimated EUR 2.3B + EUR 2.2B one-time compliance costs.

**Files**:

- `guardspine-rubrics/frameworks/dora-v1.0.yaml`
- Tests validating all rules fire on synthetic DORA scenarios
- Documentation: which DORA articles map to which rules

**Dependency**: Requires 1E (rubric hub) for distribution.

**Acceptance**: Running `codeguard audit --rubric dora` on a sample repo
produces evidence bundles with DORA-specific risk signals.

### 2B: CMMC Rubric Pack

**What**: Cybersecurity Maturity Model Certification (US DoD supply chain).
CMMC 2.0 became enforceable December 2024 for new DoD contracts.
300,000+ defense contractors need compliance tooling.

**Files**: `guardspine-rubrics/frameworks/cmmc-v2.0.yaml` (~40 rules)

### 2C: FDA 21 CFR Part 11 Rubric Pack

**What**: Electronic records and signatures for FDA-regulated industries.
Pharma, biotech, medical devices. Massive market, terrible existing tooling.

**Files**: `guardspine-rubrics/frameworks/fda-21cfr11-v1.0.yaml` (~25 rules)

### 2D: OPA/Rego Rubric Runtime

**What**: Allow rubrics to be written as OPA/Rego policies in addition
to YAML. This opens the IaC governance market where Rego is the lingua franca.

**Implementation**:

- Add `format: rego` option to rubric loader
- Shell out to `opa eval` for Rego policy evaluation
- Convert Rego output to standard rubric result format

**Files**:

- `codeguard/rubrics/rego_evaluator.py` (~150 lines)
- Update `codeguard/rubrics/loader.py` to detect `.rego` files
- Tests with sample Rego policies

**Dependency**: None for the runtime. But unlocks 2E.

### 2E: IaC Guard Lane Prototype

**What**: A guard lane that evaluates Terraform plan JSON against rubrics.

```bash
terraform plan -out=plan.bin
terraform show -json plan.bin > plan.json
codeguard audit --lane iac --input plan.json --rubric cis-aws
```

**Why**: IaC market $2.22B in 2025, projected $12.86B by 2032. HashiCorp
Sentinel is proprietary. OPA produces pass/fail, not evidence bundles.
GuardSpine produces auditable evidence for every infrastructure change.

**Files**:

- `codeguard/guards/iac_guard.py` (~200 lines)
- `codeguard/rubrics/builtin/cis-aws-benchmark.yaml` (seed rubric)
- Tests with sample Terraform plan JSON

**Dependency**: Requires 2D (Rego runtime) for CIS benchmark evaluation.

---

## PHASE 3: Distribution

**Duration**: Weeks 8-16 (parallel with Phase 2).
**Gate**: Developers can discover, install, and use GuardSpine without
leaving their existing tools.
**Thesis**: If you're not in the developer's editor and the enterprise's
communication tool, you don't exist.

### 3A: VS Code Extension

**What**: Extension showing governance status inline:

- Gutter icons for governed files (like GitLens blame)
- Status bar showing current risk tier
- Problems panel integration for rubric violations
- Quick actions: "Create approval request", "View evidence bundle"
- Tree view: open approvals, recent bundles, rubric coverage

**Why**: 42M+ monthly active VS Code users. Every competitor has one
(SonarQube, Snyk, GitGuardian). The VS Code Private Marketplace
(November 2025) lets enterprises curate approved extensions.

**Tech**: VS Code Extension API + Language Server Protocol for
real-time rubric evaluation. Talks to `codeguard` CLI for data.

**Files**:

- New repo: `guardspine-vscode`
- `package.json` with vscode engine
- `src/extension.ts` (activation, commands, tree views)
- `src/providers/` (gutter, status bar, problems)

**Dependency**: Requires `codeguard` CLI to be installable (pip or binary).

**Acceptance**: Install from `.vsix`, open a governed repo, see risk tier
in status bar, see rubric violations in problems panel.

### 3B: Microsoft Teams Bot

**What**: Teams bot for approval notifications and L2+ review workflows.
Same functionality as existing Slack integration.

**Why**: Teams has 320M+ monthly active users. Regulated enterprises
(banking, healthcare, government) standardize on Teams, not Slack.

**Files**:

- `backend/app/routers/teams.py` (webhook handler)
- `backend/app/services/teams_integration.py` (card builder, auth)
- Adaptive Cards for approval requests and decisions
- Bot Framework registration

**Dependency**: None (the approval workflow already exists).

**Acceptance**: Approval request in GuardSpine sends Teams notification
with Approve/Reject buttons. Clicking button updates approval state.

### 3C: AWS Marketplace Listing

**What**: List GuardSpine on AWS Marketplace as a SaaS product.
Enables procurement through existing AWS agreements (EDP, PPA).

**Why**: Many regulated enterprises can ONLY purchase through their
cloud marketplace. This is a procurement unlocker, not a technical feature.

**Steps**:

1. Create AWS Marketplace seller account
2. Package as SaaS with metering API integration
3. Submit listing for review
4. Set up billing integration (AWS Marketplace Metering Service)

**Dependency**: Requires a hosted SaaS version (not just self-hosted CLI).

### 3D: Public Validation Dashboard

**What**: Public-facing page showing:

- Test pass rate (currently 302-464/302-464)
- Rubric coverage metrics
- Spec compliance rate
- FP/FN rates for code analysis
- Version compatibility matrix

**Why**: For a trust product, transparency about quality IS the product.
Dennis requires FP <15% before engagement. Show it publicly.

**Files**:

- `D:\Projects\GuardSpine\frontend\src\pages\PublicDashboardPage.tsx`
- Backend endpoint: `/api/v1/public/metrics` (no auth required)
- Automated data collection from CI runs

**Dependency**: Requires CI pipeline to publish metrics (GitHub Actions artifact).

---

## PHASE 4: Revenue Expansion

**Duration**: Weeks 12-20 (after Phase 2 + 3 gates pass).
**Gate**: Revenue comes from more than one source.

### 4A: Rubric Marketplace

**What**: Extend the Rubric Hub (1E) into a paid marketplace:

- Free tier: all framework rubrics (SOC2, HIPAA, DORA, etc.)
- Premium tier: domain expert rubrics ($50-500 each)
- Enterprise tier: custom rubric development ($5K-25K per engagement)
- Commission model: 70/30 creator/platform split

**Dependency**: Requires 1E (Rubric Hub) + 2A-2C (enough rubrics to
demonstrate the pattern).

### 4B: Compliance-as-a-Service Packages

**What**: Managed governance services at premium pricing:

| Package              | Price       | Deliverables                                 |
| -------------------- | ----------- | -------------------------------------------- |
| EU AI Act compliance | $8K-15K/mo  | Rubric config, quarterly reports, audit prep |
| DORA compliance      | $6K-12K/mo  | ICT change governance, incident evidence     |
| SOX IT controls      | $5K-10K/mo  | Continuous evidence, auditor-ready exports   |
| Multi-framework      | $15K-25K/mo | All of the above                             |

**Dependency**: Requires 2A-2C (framework rubrics exist).

### 4C: Certification Program

**What**: Professional certification for GuardSpine administrators:

| Offering                    | Price       | Volume target |
| --------------------------- | ----------- | ------------- |
| Online course               | $499        | 400-800/year  |
| Certification exam          | $299        | 300-600/year  |
| Enterprise workshop (2-day) | $5,000/seat | 20-40/year    |
| Annual recertification      | $149        | Recurring     |

Year 1 target: $200K-$500K.

**Dependency**: Product must be stable (Gate 1 passed). Need course content.

### 4D: Audit Export Pricing

**What**: Per-transaction revenue for formatted audit evidence packages.
$50-$200 per export depending on framework and format.

At 1,000 customers doing quarterly exports at $100: $400K/year.

**Dependency**: Auditor pack already exists. Need payment integration
and framework-specific export templates.

### 4E: ServiceNow Integration

**What**: ServiceNow GRC integration that:

- Creates change requests from GuardSpine approval workflows
- Pulls evidence bundles into ServiceNow audit records
- Maps rubric violations to ServiceNow controls
- Syncs approval state bidirectionally

**Why**: ServiceNow GRC is where the compliance budget lives ($3B+ subscription
revenue). Compliance departments, not engineering teams, hold the budget.

**Dependency**: Requires stable approval API (Phase 0 auth fix).

---

## PHASE 5: Standards Credibility

**Duration**: Long-lead, start in Phase 1, mature over 6-12 months.
**Gate**: External recognition that the spec is a real standard.

### 5A: OASIS Spec Submission

**What**: Submit GuardSpine Evidence Bundle Specification to OASIS as a
Committee Specification Draft. Route through Jacob (G7/NIST connections).

**Timeline**: 3-6 months from submission to committee vote.

**Why**: "Submitted to OASIS" is a fundamentally different positioning than
"we wrote a JSON schema." It signals industry legitimacy.

**Dependency**: Requires 1A (Spec v1.0 GA).

### 5B: CNCF Sandbox Proposal

**What**: Submit guardspine-spec + guardspine-kernel as a CNCF Sandbox project.
The in-toto attestation format (1C) and Sigstore signing (1D) make this natural
since both are already CNCF projects.

**Why**: CNCF Sandbox signals to cloud-native buyers that this is real
infrastructure, not a startup toy.

**Dependency**: Requires 1C + 1D (in-toto + Sigstore integration).

### 5C: Reference Architectures

**What**: Published reference architectures for each major regulation:

- "GuardSpine for DORA: Reference Architecture"
- "GuardSpine for EU AI Act: Reference Architecture"
- "GuardSpine for SOX Section 404: Reference Architecture"
- "GuardSpine for HIPAA: Reference Architecture"

Each is a 10-20 page document with architecture diagrams, rubric mapping,
deployment guide, and evidence bundle examples.

**Why**: Reference architectures are what enterprise architects share internally
to justify adoption. They are the sales document that you don't write yourself --
the customer's architect writes the internal proposal using YOUR reference architecture.

**Dependency**: Requires corresponding rubric packs (Phase 2).

---

## Execution Schedule

```
Week  1-2:  PHASE 0 (credibility reset) ---------> Gate 0
Week  2-4:  PHASE 1 (spec v1.0, Sigstore, hub) --> Gate 1
Week  5-8:  PHASE 2a (DORA, CMMC, FDA rubrics)
            PHASE 3a (VS Code extension start)
            PHASE 5a (OASIS submission start)
Week  8-12: PHASE 2b (OPA/Rego, IaC lane) -------> Gate 2
            PHASE 3b (Teams bot, AWS Marketplace)
            PHASE 3d (public dashboard) ----------> Gate 3
Week 12-16: PHASE 4a (rubric marketplace)
            PHASE 4b (CaaS packages)
            PHASE 4c (certification content)
Week 16-20: PHASE 4d (audit export pricing)
            PHASE 4e (ServiceNow integration) ----> Gate 4
Ongoing:    PHASE 5 (standards body recognition) -> Gate 5
```

---

## Non-Negotiable Gates Before Enterprise Push

From the critique document, validated and updated:

1. One canonical spec version (v1.0.0), no contradictions -- Phase 0 + 1A
2. Zero known P0 verification/test defects -- DONE (302-464 tests passing)
3. Pilot UI/API flows non-placeholder for promised scope -- Phase 0C
4. Model deck internally consistent with auditable sources -- DONE (parameterized)
5. One reproducible E2E pilot reference workflow -- exists (ingest -> review -> approve -> export)
6. Self-approval bypass closed -- DONE (this session)
7. LICENSE file at repo root -- Phase 0B
8. Auth context in approval router -- Phase 0D

Items 2, 4, 5, 6 are done. Items 1, 3, 7, 8 are Phase 0 (1-2 days).

---

## What This Plan Does NOT Include

These were considered and deliberately excluded:

- **ML model governance (full implementation)**: Too early. The MLOps market needs
  model cards and lineage tracking which requires a different engine architecture.
  Revisit after Phase 2 gate. For now, the rubric system can evaluate model deployment
  artifacts (Dockerfiles, config files) without a dedicated lane.

- **Gemini/multi-model routing**: Internal development tooling, not customer-facing.
  Does not move revenue or credibility needles.

- **Mobile app**: Enterprise governance is a desktop workflow. No mobile app needed.

- **Blockchain/web3 attestation**: Urbit integration was correctly assessed as low
  value. On-chain attestation adds complexity without buyer demand.

---

## Risk Register

| Risk                                   | Probability | Impact | Mitigation                                          |
| -------------------------------------- | ----------- | ------ | --------------------------------------------------- |
| Spec v1.0 breaks existing integrations | Medium      | High   | R3: accept both v0.2.0 and v1.0.0                   |
| OASIS submission stalls in committee   | High        | Medium | CNCF Sandbox as parallel path (5B)                  |
| VS Code extension takes 8+ weeks       | Medium      | Medium | Ship MVP (status bar + problems panel only)         |
| Sigstore dependency on external infra  | Low         | High   | Support optional self-hosted Fulcio/Rekor           |
| DORA rubric accuracy challenged        | Medium      | High   | Validate with EU compliance counsel before shipping |
| AWS Marketplace listing delayed        | High        | Low    | Direct sales not blocked by marketplace             |
| Triangle relationship stalls           | Medium      | High   | Parallelize 6-10 pipeline accounts (critique rec)   |

---

## Measuring Progress

Weekly check:

1. How many Gate items remain open?
2. How many new rubric rules shipped?
3. Test count trend (should only go up)
4. Number of external-facing integration points

Monthly check:

1. Which gate passed this month?
2. Pipeline account count (target: 6-10 by month 3)
3. Community rubric contributions (target: first external contribution by month 4)
4. Standards body progress (target: OASIS submission by month 2)
