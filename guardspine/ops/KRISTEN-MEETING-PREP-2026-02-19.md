# GuardSpine x Kristen -- Meeting Prep (v2 -- UPDATED)

## Thu Feb 19, 3:00-4:00 PM EST

## Attendees: David, Igor, Kristen

---

## POSITIONING (Read This First)

GuardSpine is NOT "AI governance." It is ARTIFACT GOVERNANCE.

The distinction matters:

- "AI governance" = watching the model work. That's observability. That's Galileo, Arthur AI, Arize. It assumes the interesting thing is the AI.
- "Artifact governance" = proving the output is good. The interesting thing is the WORK, not who made it.

GuardSpine does not care whether a human, Cursor, Claude, or a junior dev wrote the PR. It proves the artifact was reviewed, deliberated, and cryptographically signed. Origin is irrelevant. Governance is the point.

The vision: tools so good that nobody asks "did a human write this?" The question becomes irrelevant. The evidence bundle proves governance happened. Period.

The first wedge artifact is CODE -- not because AI code is scary, but because code changes are the highest-friction governance gap in regulated enterprises right now. The cryptographic spine is artifact-agnostic by design. Code today. Documents, spreadsheets, images tomorrow. Same evidence trail.

This is NOT about babysitting AI. That's a failure of imagination. This is about making governance invisible and proving the work is good regardless of origin.

---

## SECTION 1: EMAIL DIGEST (What Kristen Has Said)

### Email 1 -- Feb 18, 7:40 PM (Main Assessment)

Kristen sent a comprehensive pre-meeting brief. Key points:

**She validated the tech:**

> "What you've built is serious. The architecture is thoughtful, the
> cryptographic spine concept is coherent, and the implementation depth
> is well beyond what most early-stage projects look like."

**Her core concern -- horizontal = liability at early stage:**

- GuardSpine reads as a horizontal platform (code + docs + spreadsheets + images across all industries)
- At earliest stage, horizontal positioning is a liability, not an advantage
- Enterprise software gets purchased through: (1) identifiable buyer, (2) defined budget line, (3) concrete internal trigger
- If product doesn't map to an existing budget bucket, it requires political capital and new budget creation -- dramatically longer sales cycles

**What VCs evaluate (her framework):**

1. Clear, painful problem
2. Defined buyer with authority to spend
3. Identifiable budget inside the org's P&L
4. Short, repeatable sales motion
5. Evidence of willingness to pay

**Her recommended path:**

1. Choose ONE vertical or high-friction workflow where AI artifacts create audit risk
2. Identify exactly who owns that risk internally and what budget line funds it
3. Validate urgency through 10-15 target buyer conversations
4. Secure 1-3 design partners or paid pilots at meaningful ACV
5. Expand outward from that foothold

**Bottom line:** "Dominate a wedge first, then broaden. Not the reverse."

### Email 2 -- Feb 19, 7:09 AM (YC Suggestion)

- Sent a link to ycombinator.com with "This may be an interesting option for you guys"
- Worth discussing: YC S26 deadline, pros/cons, dilution (7% standard)

### Email 3 -- Feb 19, 7:56 AM (Two Validation Questions)

She wants concrete answers to:

**Q1: Is the EU AI Act a real forcing function?**

> "Or are 2026 governance companies simply hoping for this because it
> theoretically anchors their pitch? CCPA absolutely did not have the
> impact that it was said to. GDPR kind of did, but it was a mixed bag.
> Regulatory tailwinds tend to help incumbents more than startups."

**Q2: Is there a real budget line for AI artifact governance OUTSIDE of code?**

> "Otherwise, you get bucketed into 'developer tools,' which you are not."

### David's Reply -- Feb 18, 8:59 PM

- VP Engineering and CTO at regulated enterprises -- fintech, banking, insurance, biotech
- DORA enforceable since Jan 2025, EU AI Act rolling, NIS2 live
- Secondary: CISO/Head of AppSec where AI agents ship code to production

---

## SECTION 2: ANSWERS TO KRISTEN'S TWO QUESTIONS

### Q1: Is the EU AI Act a real forcing function?

**Honest answer: Yes, but not for the reason most governance startups think.**

The forcing function is not "AI is scary and regulators are coming." The forcing function is: code changes are ICT changes, and regulated enterprises already must govern ICT changes. DORA has been enforceable since Jan 17, 2025. This is not theoretical.

The shift happening right now: more and more code changes are being produced by AI agents. But the governance requirement is the SAME whether a human or AI wrote the code. The gap is that nobody is producing cryptographic evidence that changes were reviewed and approved -- regardless of origin.

Evidence FOR:

- DORA Article 6a: ICT change management controls required for financial entities (live since Jan 2025)
- EU AI Act Articles 9 and 17: risk management and quality management for AI systems (rolling out through Aug 2026)
- NIS2: expanded scope to 18 sectors since Oct 2024
- Jacob Friedman (G7/NIST advisor) independently confirmed the SBOM+governance gap
- Phil Venables (ex-CISO Google Cloud, Ballistic Ventures) engaged with DD questions -- he wouldn't if the thesis was thin

Evidence AGAINST (be honest about these):

- CCPA analogy is valid -- regulation alone doesn't create buying urgency
- Enforcement timelines are uncertain
- Incumbents (ServiceNow, Wiz, Snyk) could add governance features

**Framing for the meeting:**
We don't pitch "the EU AI Act is coming, be scared." We pitch: "You already must govern code changes. More of those changes are AI-generated. Nobody is producing evidence. We do."

### Q2: Budget line for artifact governance outside code?

**This is where the positioning shift matters.**

Kristen's question assumes we're in the "AI governance" category. We're not. We're in ARTIFACT GOVERNANCE. The first artifact is code.

Where does code artifact governance sit in a buyer's P&L?

- **DevSecOps tooling** -- already a recognized budget line
- **Change management / audit evidence** -- every regulated enterprise has this budget
- **GRC (Governance, Risk, Compliance) software** -- established category, growing fast

We are NOT asking a buyer to create a new budget category. We map to existing ones:

- VP Engineering buys DevSecOps tools. We're a DevSecOps tool that produces cryptographic evidence.
- CTO/CISO funds change management controls. We automate those controls.
- Compliance Officer needs audit evidence. We generate it automatically.

The multi-artifact expansion (documents, spreadsheets, images) comes AFTER we own the code wedge. When it does, it maps to:

- Document lifecycle management (existing budget)
- Data governance / DLP (existing budget)
- Audit/compliance tooling (existing budget)

**Key point: we never need a "new" budget line. Artifact governance maps to existing categories at every stage.**

---

## SECTION 3: FINANCIAL MODEL QUICK REFERENCE

| Metric              | Value                                     |
| ------------------- | ----------------------------------------- |
| Round               | $1M angel at $9M pre-money (10% dilution) |
| Monthly burn        | $27.5-35.5K/mo                            |
| Runway (post-raise) | 28-36 months                              |
| Y1 revenue target   | $650K                                     |
| Y1 ending ARR       | $1.3M                                     |
| Breakeven           | Near Y1 end                               |
| Gross margins       | 85-89% (BYOK = zero LLM costs)            |
| Hire plan           | Engineer #1 (M3-M4), outsourced legal     |
| David + Igor salary | $10K/mo each ($120K/yr)                   |

### Key Model Issues to Be Aware Of

- All unit economics (CAC, LTV, NRR, churn) are assumed, not measured
- No PLG conversion funnel exists in the product yet
- Enterprise revenue assumptions have no validation
- Round terms in generate_model.py are STALE (still shows $300K/3%)

### Kristen's Equity -- MUST CLARIFY TODAY

- Model shows Kristen at 10% equity
- Role is unclear: advisor vs partner vs co-founder
- If advisor: 0.5-2% is standard (4yr vest, 1yr cliff)
- If partner/co-founder: 5-15% is reasonable
- If cash retainer: $8K/mo ($96K/yr) + lower equity
- This MUST be resolved before angel introductions

---

## SECTION 4: TRACTION TO REFERENCE

### Green Signals (bring these up as evidence of pull)

1. **Phil Venables** (Ballistic Ventures, ex-CISO Google Cloud) -- replied with DD questions about team, pipeline, ICP. Awaiting next response.
2. **Brent Foster** (TD Bank, VP Engineering) -- replied Feb 17 via LinkedIn
3. **Logan Napolitano** (Proprioceptive AI) -- NDA/MOU active
4. **Jacob Friedman** (G7/NIST, Permion) -- confirmed SBOM+governance gap, wants offline/airgap support
5. **Ishwar Chavhan** (IBM, Z-Inspection) -- connected with Igor, interviewing IBM engineers

### Product Evidence

- 428 tests passing across repos
- codeguard-action v1.0.1 live on GitHub Marketplace
- Full UI dashboard (24 pages), Slack integration, evidence bundles
- PII-Shield WASM integration (4 PRs merged)
- OSS contributor (Ilya) actively submitting PRs

---

## SECTION 5: MEETING AGENDA (Recommended)

| Time      | Topic                                                                  | Lead              |
| --------- | ---------------------------------------------------------------------- | ----------------- |
| 0-5 min   | Introductions -- Igor and Kristen                                      | David facilitates |
| 5-15 min  | Reframe: artifact governance, not AI governance -- agree on code wedge | David             |
| 15-25 min | Answer the two validation questions with the corrected framing         | David + Igor      |
| 25-35 min | Traction signals + what we're hearing from buyers                      | David             |
| 35-45 min | Kristen's role -- clarify advisor vs partner vs co-founder             | David + Kristen   |
| 45-50 min | YC -- discuss pros/cons                                                | All               |
| 50-55 min | Next steps -- angel intro timeline, what Kristen needs from us         | Kristen           |
| 55-60 min | Buffer / overflow                                                      | --                |

### Key Stance for the Meeting

- **Lead with the reframe.** "We're not AI governance. We're artifact governance. Code is the first artifact."
- **Origin-agnostic is the differentiator.** We don't care if a human or AI wrote the code. We prove the work is governed.
- **Invisible tooling is the vision.** The goal is governance so seamless nobody thinks about it. Not "watch the AI" -- that's a failure of imagination.
- **Agree with the wedge strategy.** Code first. Expand to other artifacts from a position of strength.
- **Map to existing budgets.** DevSecOps, change management, GRC. No new category needed.
- **Be honest about what's unmeasured.** Kristen will respect it more than inflated claims.
- **Resolve the equity question.** Can't intro to angels with this ambiguous.

---

## SECTION 6: WHAT NOT TO DO

- Do NOT say "AI governance." Say "artifact governance."
- Do NOT position as "monitoring AI." Position as "proving work is governed."
- Do NOT demo features. She's past that. She cares about business definition.
- Do NOT defend horizontal positioning. Agree: code first, expand later.
- Do NOT oversell regulatory certainty. Be honest about CCPA/GDPR mixed record.
- Do NOT bring up competitor features. She cares about buyer and budget, not features.
- Do NOT dodge the equity question. If she's introducing you to her angel network, her role and compensation must be defined.

---

# IGOR'S GUIDE -- First Meeting with Kristen

## Who is Kristen Hengst Smith?

- **Company**: Dark Pilot (darkpilot.com, kristensmith.design)
- **Background**: First UX designer at Barbarian (employee #8). Built award-winning work for Fortune 500. Running her own consultancy since 2010.
- **Expertise**: Helping businesses raise funding, acquire users, and grow revenue. She's a GTM and product-to-market specialist.
- **Why she matters**: She has an angel investor network and has offered to introduce us. She can open doors we can't open ourselves.

## Her Communication Style

- **Direct.** No small talk in the first meeting. She came prepared and expects you to be prepared.
- **Strategic, not technical.** She does not care about hash algorithms or WASM. She cares about: who buys this, where does the money come from, and can you sell it repeatably.
- **Experienced.** She's advised dozens of founders at this exact stage. She's seen the "great tech, no business definition" pattern many times and she'll call it out.
- **Respect-based.** She already said the architecture is "serious" and "well beyond most early-stage projects." She respects the engineering. Now she wants to see business acumen.

## The Key Positioning (Critical for This Meeting)

GuardSpine is ARTIFACT GOVERNANCE, not AI governance.

- We don't babysit AI. We prove work is governed -- regardless of whether a human or AI produced it.
- The first artifact is code. Not because "AI code is scary" but because code changes are the highest-friction governance gap in regulated enterprises.
- The vision: governance so invisible that nobody asks "who wrote this?" The evidence bundle answers the only question that matters: "was this governed?"
- The cryptographic spine is artifact-agnostic by design. Code today, everything else tomorrow. Same evidence trail.

When David talks about this in the meeting, support it with concrete examples:

- "The GitHub Action doesn't check whether the code was written by a human or AI. It reviews the artifact, runs multi-model deliberation, and produces a signed evidence bundle. Origin doesn't matter."
- "The hash chain signs the artifact and the review -- not the author. That's the point."

## Your Role in This Meeting

1. **Introduction (5 min)**: Be yourself. Brief background -- nuclear physics MSc, 13 years commercial engineering, Rust/crypto/distributed systems, why GuardSpine matters to you. 30 seconds, not 5 minutes.

2. **Technical credibility anchor**: When David discusses the wedge or buyer conversations, you provide the "we built X" confirmation. Short, specific, concrete. Example: "We already have the GitHub Action live -- it reviews PRs with multi-model consensus and produces cryptographically signed evidence bundles. 428 tests pass."

3. **Reinforce origin-agnostic**: If the conversation touches on "AI code" vs "human code," make the point: "Our system doesn't distinguish. Governed is governed."

4. **Honest about unknowns**: If she asks about scale, enterprise readiness, or measured metrics -- be honest. "We haven't measured that yet" is better than guessing. She will respect honesty.

5. **Listen more than talk**: This meeting is about business strategy, not architecture. Your most important job is to listen to her framework and internalize it. Ask one or two sharp questions. Don't lecture.

## What She Already Knows About You

From David's introduction email:

> "Igor Malovitsa, our CTO. Igor brings 13 years of commercial engineering
> across Rust, cryptography, and distributed systems, with a physics MSc
> to back it up. He's the one who built the hash-chaining engine and the
> cryptographic evidence bundles that make GuardSpine's audit trail
> tamper-proof."

She knows you're technically strong. You don't need to prove it again.

## Key Things She Said (Read Before the Meeting)

1. "What you've built is serious." -- She respects the work.
2. "Horizontal positioning is usually a liability at earliest stage." -- She wants you to narrow.
3. "Dominate a wedge first, then broaden." -- This is her strategy.
4. "CCPA did not have the impact it was said to. GDPR was a mixed bag." -- She's skeptical of regulatory-tailwind narratives.
5. "Is there a real budget line for AI artifact governance outside of code?" -- This is the critical question. Our answer: we map to EXISTING budgets (DevSecOps, change management, GRC), not a new one.

## Good Questions for Igor to Ask

- "When you've seen founders successfully narrow from a horizontal platform, what did the first 90 days look like?"
- "In your experience, what's the strongest signal that a wedge is working before revenue comes in?"
- "For the angel introductions -- what do your investors typically want to see at this stage?"

## Things to Avoid

- Don't say "AI governance" -- say "artifact governance"
- Don't explain cryptographic primitives unless directly asked
- Don't compare to competitors on features (she doesn't care)
- Don't say "we can build that" -- she wants to hear "we chose NOT to build that because..."
- Don't interrupt -- she's the expert in this room on GTM and fundraising
- Don't oversell. Undersell and let her be surprised by depth.

---

_File: Desktop/guardspine/KRISTEN-MEETING-PREP-2026-02-19.md_
_Generated: Feb 19, 2026 (v2 -- updated with artifact governance positioning)_
