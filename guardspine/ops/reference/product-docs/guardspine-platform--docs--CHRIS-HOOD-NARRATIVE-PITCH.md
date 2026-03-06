# The Office of the Future: A Day in Governed Work

**A narrative pitch for Chris Hood**

---

## The Scene

It's Tuesday morning at a mid-size biotech. Sarah, the VP of Commercial Operations, needs to prepare materials for Thursday's board meeting.

She has three artifacts to finalize:

- A **slide deck** with updated market projections
- An **Excel model** with revised revenue assumptions
- A **policy PDF** with compliance language for their new AI drug discovery platform

All three have been touched by AI assistants. All three will be seen by the board. All three could create liability if something goes wrong.

In most companies, this is where governance ends. Sarah emails the files, someone clicks "approve" in DocuSign, and everyone hopes nothing was hallucinated or silently changed.

**Not here.**

---

## 9:14 AM: The Slide Deck (ImageGuard + PDFGuard)

Sarah opens the deck. Her AI assistant suggested edits to three slides overnight - updated charts, reworded bullet points, a new graph on page 12.

She clicks "Ready for Review."

**Nomotic fires.**

The system recognizes: _external-facing content + AI-suggested changes + board-level visibility._

Three things happen instantly:

1. **ImageGuard** captures pixel-level diffs of every changed slide. The new chart on page 12 gets flagged: it contains data from an external API link that wasn't there yesterday.

2. **PDFGuard** extracts the slide notes and compares them to the previous version. One note says "Source: internal model v3.2" but the chart actually pulls from a different source.

3. **A Conditional Request fires**: "External data source added. Requires L3 review before board distribution."

Sarah doesn't need to remember the policy. The policy remembers itself.

She tags Michael from Data Science. He reviews, confirms the source is valid, and approves with a note: "Verified against Q4 actuals. Safe to present."

**Evidence bundle created:** What changed, who approved, why, with hashes.

---

## 10:47 AM: The Revenue Model (SheetGuard)

The CFO's team updated the Excel model. AI suggested formula optimizations - some cells now reference a new lookup table that didn't exist last quarter.

Sarah opens the file to spot-check.

**Nomotic fires.**

The system recognizes: _financial model + formula changes + CFO domain._

1. **SheetGuard** diffs every cell. It flags:
   - 14 formula changes
   - 1 new external link (to a shared Drive folder)
   - 3 cells where the AI replaced a hardcoded value with a VLOOKUP

2. A **visual heatmap** shows which cells changed, color-coded by risk. The external link glows red.

3. **An Authority Rule fires**: "Finance formula changes require Finance approver. External links require IT Security review."

Two approval requests go out automatically. Sarah doesn't chase anyone. The system knows who needs to sign off.

By 11:30, both approvals are in. The CFO added a note: "Validated against FP&A model. Approved for board."

**Evidence bundle created:** Cell-by-cell diff, formula lineage, approval chain.

---

## 2:15 PM: The Compliance Policy (PDFGuard)

Legal sent an updated compliance policy for the AI drug discovery platform. It's 47 pages. The AI assistant summarized the changes in a 2-page memo.

Sarah needs to confirm nothing critical was missed.

**Nomotic fires.**

The system recognizes: _regulatory document + AI-summarized content + compliance domain._

1. **PDFGuard** computes a deterministic diff between the old and new policy. It highlights:
   - 12 clause changes
   - 2 new liability sections
   - 1 deleted paragraph about data retention

2. The AI summary is attached as a **sidecar annotation** - it never touched the original document. The summary is traceable but clearly marked as AI-generated.

3. **An Interrupt Rule fires**: "Liability clause changes require General Counsel review before distribution."

Legal gets notified. They confirm the changes are intentional and add a note explaining the regulatory context.

**Evidence bundle created:** Clause-level diff, AI summary with provenance marker, legal sign-off.

---

## 4:30 PM: The Board Packet Goes Out

Sarah clicks "Finalize Board Packet."

The system assembles everything:

- Slide deck with ImageGuard evidence
- Excel model with SheetGuard evidence
- Policy PDF with PDFGuard evidence

All three bundles are **hash-chained**. Each one links to the previous. The entire packet has a single integrity hash that proves nothing was changed after approval.

Sarah exports the packet. The board receives:

- The documents
- A one-page evidence summary
- A QR code that links to the verification page

If anyone ever asks "How do we know this was reviewed?", the answer isn't "Trust us."

The answer is **cryptographic proof**.

---

## What Just Happened

In one afternoon, Sarah moved three high-stakes artifacts through a governed workflow without:

- Chasing approvers manually
- Wondering what AI changed
- Hoping someone read the fine print
- Creating compliance risk by accident

Every decision was justified. Every change was traceable. Every approval was recorded.

**This is the office of the future.**

Not because AI did more.

Because AI was **governed by design**.

---

## Where Competitors Fail

Every vendor in this space does _part_ of this. None of them do _all_ of it.

### GitHub / GitLab / Version Control

**What they do well:**

- Code diffs
- PR approvals
- Audit logs for code changes

**Where they fail:**

- No governance for documents, spreadsheets, or images
- No AI-specific provenance tracking
- No cross-artifact evidence bundles
- Assumes everything is code

**The gap:** Sarah's slide deck and Excel model aren't in Git. Her board packet doesn't have a PR workflow.

---

### DocuSign / Adobe Sign / E-Signature Platforms

**What they do well:**

- Signature capture
- Audit trail for "who signed when"
- Legal validity for contracts

**Where they fail:**

- No diff visibility (they capture _that_ you signed, not _what_ changed)
- No AI provenance (if AI edited the doc before signing, there's no record)
- No conditional logic based on content
- Approval is binary, not risk-graduated

**The gap:** Sarah can DocuSign a document that AI hallucinated into. DocuSign won't tell her.

---

### GRC Platforms (ServiceNow, OneTrust, Archer)

**What they do well:**

- Policy management
- Control mapping
- Compliance workflows

**Where they fail:**

- Evidence is collected _after the fact_
- No real-time gating on artifacts
- No deterministic diffs at the artifact level
- No AI-specific governance

**The gap:** GRC tells you "control 4.2.1 was attested." It doesn't tell you what changed in the spreadsheet or whether AI touched it.

---

### AI Observability Tools (LangSmith, Weights & Biases, Arize)

**What they do well:**

- LLM call tracing
- Prompt/response logging
- Model performance monitoring

**Where they fail:**

- Track the _model_, not the _work_
- No governance of documents, spreadsheets, images
- No approval workflows
- No evidence bundles for auditors

**The gap:** They know Claude was called 47 times. They don't know what Claude changed in the board deck or whether anyone approved it.

---

### SharePoint / Google Drive / Box

**What they do well:**

- Version history
- Sharing permissions
- Collaboration features

**Where they fail:**

- Version history is not audit-grade (no deterministic diffs)
- No risk-based gating
- No AI provenance
- No approval workflows with evidence capture

**The gap:** Sarah can see "Version 12" vs "Version 13." She can't see what formula changed or why.

---

### DLP / Data Security Tools (Netskope, Zscaler, Symantec)

**What they do well:**

- Detect sensitive data in transit
- Block unauthorized sharing
- Classify documents

**Where they fail:**

- Reactive, not proactive (they catch _after_ the data moves)
- No content-level governance
- No AI-aware policies
- No evidence bundling

**The gap:** DLP might block Sarah from emailing the spreadsheet to a personal account. It won't tell her the spreadsheet's revenue formula was changed by AI.

---

## The Competitive Truth

| Competitor Category | Code    | Docs    | Sheets  | Images  | AI Provenance | Risk Gating | Evidence Bundles |
| ------------------- | ------- | ------- | ------- | ------- | ------------- | ----------- | ---------------- |
| GitHub/GitLab       | Yes     | No      | No      | No      | No            | Partial     | No               |
| DocuSign/Adobe      | No      | Partial | No      | No      | No            | No          | No               |
| GRC Platforms       | No      | Partial | No      | No      | No            | Partial     | Partial          |
| AI Observability    | No      | No      | No      | No      | Yes           | No          | No               |
| SharePoint/Drive    | No      | Partial | Partial | No      | No            | No          | No               |
| DLP Tools           | No      | No      | No      | No      | No            | Partial     | No               |
| **GuardSpine**      | **Yes** | **Yes** | **Yes** | **Yes** | **Yes**       | **Yes**     | **Yes**          |

Every competitor solves **one slice**. GuardSpine is the **spine** that connects them all.

---

## The Nomotic Layer

Here's where Chris's framework becomes essential.

All of the above - the diffs, the approvals, the bundles - could be built as features.

But without **Nomotic**, you're just building another compliance tool. You're governing _reactively_.

Nomotic gives us the **semantics**:

| Nomotic Concept          | What It Means in Practice                                 |
| ------------------------ | --------------------------------------------------------- |
| **Authority Layer**      | Who delegated the rule? Human policy, not AI suggestion.  |
| **Conditional Requests** | "Only valid if these approvals are attached."             |
| **Interrupt Rights**     | Humans can stop the workflow. The system can't override.  |
| **Governed Adaptation**  | When we change the rules, those changes are governed too. |
| **Evidence & Trust**     | The bundle proves what happened. No SaaS trust required.  |

GuardSpine implements these. Nomotic **names** them.

Together: _"Governance you can actually deploy."_

---

## The Ask

Chris has built the language.

We've built the plumbing.

The question is whether we ship Nomotic Mode together - a versioned rubric pack that makes this governance portable, auditable, and real.

Not education. Not consulting.

**Infrastructure.**

---

## One Image to Leave Behind

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOMOTIC AUTHORITY LAYER                      │
│            (Human-delegated rules, not AI opinions)             │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │
│  │ CodeGuard │  │ PDFGuard  │  │SheetGuard │  │ImageGuard │    │
│  │   (PRs)   │  │  (Docs)   │  │  (XLSX)   │  │  (Visuals)│    │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘    │
│        │              │              │              │           │
│        └──────────────┴──────────────┴──────────────┘           │
│                               │                                 │
│                    ┌──────────▼──────────┐                      │
│                    │   EVIDENCE BUNDLE   │                      │
│                    │  (Hash-chained,     │                      │
│                    │   offline-verified) │                      │
│                    └─────────────────────┘                      │
│                                                                 │
│                         GUARDSPINE                              │
└─────────────────────────────────────────────────────────────────┘
```

---

_The office of the future isn't about AI doing more._

_It's about humans staying accountable for what AI does._

_That's what we're building._

---

**Document type:** Narrative pitch for partnership meeting
**Created:** 2026-01-20
