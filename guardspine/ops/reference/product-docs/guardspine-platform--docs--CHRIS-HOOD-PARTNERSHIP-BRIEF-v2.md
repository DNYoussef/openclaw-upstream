# GuardSpine x Nomotic AI Partnership Brief (v2)

**Prepared for:** Meeting with Chris Hood (CH Digital)
**Date:** 2026-01-20
**Context:** Follow-up to 1-hour call (2026-01-15) - GREEN signal, PEER positioning established
**Document Type:** Internal meeting notes (verify before external sharing)

---

## Executive Summary

GuardSpine is the **evidence + gating substrate** for Nomotic AI principles. Chris has created the philosophical framework and control-plane semantics. GuardSpine provides the **working audit spine** that makes Nomotic governance operational across artifacts.

**The pitch:** _"Nomotic is the control-plane semantics. GuardSpine is the evidence + gating substrate. Together: governance you can actually deploy."_

---

## Nomotic Architecture to GuardSpine Mapping (Corrected)

| Nomotic Layer                | GuardSpine Implementation (What Ships)                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Nomotic Authority Layer**  | Policy Packs + Rubrics + Authority Model (roles, escalation rules, interruption rights)                                  |
| **Action Planning**          | Beads Work Spine (intent, dependencies, scope metadata)                                                                  |
| **Request Analysis**         | Artifact Diffs + Risk Classifier + Rule Evaluation (code/PDF/XLSX/image)                                                 |
| **Nomotic Control Plane**    | Gates + Approvals + "Stop-the-line" enforcement (block merge/export/share until satisfied)                               |
| **Conditional Requests**     | Approval objects + conditions ("only valid if approvals attached")                                                       |
| **Governed Adaptation**      | **Governance-change workflow** (rubric versioning, threshold updates, approvals for governance changes, signed releases) |
| **Evidence & Trust Records** | Hash-chained Evidence Bundles + Offline Verification (no SaaS trust required)                                            |
| **Authorized Execution**     | Post-approval actions (publish, deploy, export, share)                                                                   |

---

## Nomotic 5 Principles to GuardSpine Features

| Nomotic Principle                 | GuardSpine Mechanism                          | Notes                                               |
| --------------------------------- | --------------------------------------------- | --------------------------------------------------- |
| **Governance as architecture**    | Governance gates are in-path, not retroactive | "Default path is governed path."                    |
| **Pre-action authorization**      | L0-L4 escalation + required approvers         | Explicit interruptions are first-class.             |
| **Explicit authority boundaries** | Versioned policy packs + role-based rules     | Authority model is auditable and change-controlled. |
| **Verifiable trust**              | Bundle hashes + offline verifier              | Auditors can validate without trusting vendor.      |
| **Ethical justification**         | Sidecar rationale + multi-model review logs   | AI can suggest, never directly edits artifacts.     |

---

## Nomotic Mode (Productization Proposal)

**Nomotic Mode** = a versioned rubric pack + bundle schema fields that make Nomotic governance machine-auditable.

### What Ships (v1)

- `nomotic-core.yaml` rubric pack (authority, interruptions, conditional requests)
- Bundle fields: `authority_basis`, `constraints_applied`, `interrupts_triggered`, `approvals_required`, `approvals_received`
- Release process: versioned, signed, human-approved (governed adaptation)

**Scope limitation:** Nomotic Mode governs authorization and evidence, not model behavior or optimization logic.

### Partner Controls (Chris)

- Review/approve rubric releases (optional: "Nomotic Certified" tier)
- Attribution rules (what counts as "Nomotic" vs "GuardSpine opinion")
- Update cadence + deprecation policy

### Trust Separation (Critical for Partner Comfort)

| Layer                                              | Control               | Source of Truth                                  |
| -------------------------------------------------- | --------------------- | ------------------------------------------------ |
| **OSS Layer** (guardspine-spec, guardspine-verify) | GuardSpine-controlled | Open schemas, anyone can verify                  |
| **Nomotic Layer** (nomotic-core.yaml)              | Partner-controlled    | Direct citation to Chris-provided materials only |
| **Implementation Layer**                           | GuardSpine-controlled | How gates + bundles work                         |

**Key commitment:** All Nomotic references are direct-citation to partner-provided materials. No derivative paraphrase treated as source-of-truth. No AI summarization of Nomotic rules without explicit approval.

---

## Joint Wedge Workflow: Board Packet

**Use case:** Quarterly deck + KPI spreadsheet + policy appendix PDF

### Flow

1. **Draft artifacts** move through Drive/SharePoint (human + AI-assisted)

2. **GuardSpine emits diffs + risk classification** across:
   - Slides: layout + charts changed
   - XLSX: formula deltas, external links, pivot outputs
   - PDF: clause diffs, signature blocks, external links

3. **Nomotic Mode triggers**:
   - Conditional Request: "External link added -> requires L3 review"
   - Authority Rule: "Finance KPI formulas -> requires Finance approver"
   - Interrupt right: block "ready-for-board" marker until satisfied

4. **Evidence bundle exported** for audit record:
   - "what changed" + "who approved" + "why approved" + hashes

5. **Offline verifier** proves integrity + approvals without SaaS trust

### Why This Workflow Wins

- Every public company does this quarterly
- It's multi-artifact (slides + XLSX + PDF) - plays to GuardSpine's strength
- High stakes, high visibility, compliance-adjacent
- Natural enterprise wedge

---

## Alignment Points (From Jan 15 Call)

| Theme                    | Chris's View                                                                   | GuardSpine Answer                                                      |
| ------------------------ | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| "Governed by accident"   | Most AI deployments stumble into governance retroactively                      | Governance is in-path - every artifact change goes through the spine   |
| Linguistics precision    | Language matters for governance (hence "Nomotic" from Greek _nomos_)           | Deterministic diffs, hash-verified claims, auditability as first-class |
| Unaccountable automation | Silent failures before regulatory/political problems                           | L0-L4 graduated risk, automatic escalation, approval workflows         |
| Fiduciary obligation     | "AI governance is no longer a technology issue - it is a fiduciary obligation" | Audit-ready evidence bundles, offline verification                     |

---

## Partnership Options (Lead with Mode)

### Option A: "Nomotic Mode" (Fast)

- Co-branded rubric pack
- GuardSpine ships, Chris reviews informally
- Attribution in docs + CLI output
- **Timeline:** 4-6 weeks to v1

### Option B: "Nomotic Certified" (Premium)

- Chris formally approves releases + brand usage rules
- "Certified" badge in UI and bundles
- Review cadence agreement
- **Timeline:** 8-12 weeks with legal review
- **Note:** Certified is opt-in and may remain limited to specific verticals or customers.

### Option C: Co-Development (Deep)

- Joint IP on Nomotic Evidence Bundle Specification
- Co-authored white paper
- Joint enterprise sales motion
- **Timeline:** Ongoing relationship

**Meeting Goal:** Get Chris to say yes to Option A or B. Don't lead with "education licensing" - lead with Mode.

**GTM Flywheel:** Nomotic creates governance demand; GuardSpine satisfies it at the artifact level.

---

## What Each Party Brings

### Chris Brings

| Asset                    | Value                                                                   |
| ------------------------ | ----------------------------------------------------------------------- |
| Nomotic AI framework     | Established governance brand with trademark (filed Jan 8, 2026)         |
| Academic credibility     | PhilArchive paper, framework rigor                                      |
| Book launch (April 2026) | Distribution channel (verify title + timeline)                          |
| Audience                 | LinkedIn followers + podcast reach (verify numbers before external use) |
| Enterprise credibility   | Former Google, 35yr experience                                          |

### GuardSpine Brings

| Asset                  | Value                                                  |
| ---------------------- | ------------------------------------------------------ |
| Working implementation | Theory becomes operational                             |
| Four Guard Lanes       | Code, PDF, Sheets, Images - complete artifact coverage |
| Evidence Bundles       | Audit-ready trails with offline verification           |
| Open Source Components | guardspine-spec, guardspine-verify, connector template |
| GitHub Action          | Instant CI/CD adoption                                 |

---

## Meeting Strategy

### Opening (2 min)

_"Last time we discovered strong alignment on linguistics, governance, and the 'governed by accident' problem. I've since mapped GuardSpine directly to your Nomotic architecture. I want to propose something concrete: Nomotic Mode."_

### Present Nomotic Mode (5 min)

- Show the mapping table
- Walk through Board Packet workflow
- Emphasize: "You control the Nomotic layer. We control the implementation."

### Ask for Decision (5 min)

_"Do you want to start with informal review (Mode) or formal approval rights (Certified)?"_

### Next Steps (3 min)

- If Mode: Draft nomotic-core.yaml, send for review
- If Certified: Schedule legal/brand discussion
- Either way: Offer to support book launch

---

## Likely Objections (Prepare Counters)

| Objection                                                 | Counter                                                                                               |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| "GuardSpine is post-hoc audit, not real-time enforcement" | Show Approval Inbox + policy checklist firing. We block merge/export/share.                           |
| "Nomotic might be misrepresented by AI summarization"     | Partner-provided sources only. Direct citation. Separation of "Nomotic rule" vs "GuardSpine opinion." |
| "Governed adaptation is hand-wavy"                        | Policy pack updates require approvals + signed releases + bundle output. It's governed governance.    |
| "What about offline artifacts reintroduced?"              | Connector catch-up + provenance merge. "Unmanaged change detected" gate.                              |

---

## Assumptions to Verify (Before External Sharing)

- [ ] Audience numbers (LinkedIn followers, podcast reach)
- [ ] Trademark status and co-branding implications
- [ ] PhilArchive paper license for reuse/embedding
- [ ] Book title and timeline confirmation
- [ ] His appetite for formal vs informal partnership

---

## Edge Cases to Be Ready For

1. **Offline artifacts** (email attachments) reintroduced into Drive
   - Need: connector catch-up + provenance merge

2. **Human edits outside guarded workflow**
   - Need: "unmanaged change detected" gate

3. **"AI suggested change" vs "human authored change" attribution**
   - Need: sidecar + actor identity model (already have this)

---

## One-Liner (Meeting Close)

> "Let's define Nomotic Mode v1 as a rubric pack + bundle schema, and co-market it as governance you can actually deploy."

---

_Document version: v2 (revised with partner-lens improvements)_
_Created: 2026-01-20_
_Status: Internal meeting notes - verify assumptions before external sharing_
