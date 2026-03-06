# GuardSpine Messaging Discipline - v1

**What we say, what we DON'T say, and why**

Source: Kristen sync #2, Feb 19 2026 (David, Igor, Kristen)

---

## VC PITCH FRAMING

The macro narrative for investors:

> SaaS is getting squeezed. Every category is being compressed by AI.
> The ONLY category that grows when AI accelerates is governance --
> someone has to verify what AI produces. GuardSpine is the one bet
> that benefits from the same force that's killing everything else.

Three sentences. That's the opener. Everything else is detail.

---

## MESSAGING TABLE -- ALL CONTEXTS

### Category & Positioning

| Context         | SAY THIS                            | NOT THIS                 | Why                                                                                                                                                                                              |
| --------------- | ----------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Category        | Code governance                     | Code review              | Code review = Greptile, CodeRabbit, Beezy, Linear B. They exist. They're further along. Governance is the growing category; review is the shrinking one.                                         |
| What we govern  | Artifact governance                 | AI governance            | AI governance has no budget line. We govern artifacts -- code, docs, images -- regardless of who or what produced them. Don't create a category that doesn't exist yet.                          |
| What we are     | Insurance against AI-generated risk | AI tool                  | We are not an AI tool. We are a governance tool that happens to use AI. This is the key differentiator.                                                                                          |
| Technical moat  | Tamper-proof audit trail            | Cryptographic primitives | Enterprise buyers (banks, law, insurance, healthcare) don't know what cryptographic proof is. They understand "tamper-proof" and "admissible in court." Sell the end benefit, not the mechanism. |
| Output artifact | Judgment receipt                    | Evidence bundle          | "Evidence bundle" is internal jargon. "Judgment receipt" is what landed with Brent Foster at TD Bank. Use it with non-technical buyers.                                                          |

### Budget & Buyer

| Context       | SAY THIS                                 | NOT THIS                | Why                                                                                                                        |
| ------------- | ---------------------------------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Budget line   | DevSecOps / Compliance audit             | Engineering tools       | VPs of Engineering don't have budget authority. CISOs do. The money lives in compliance/audit, not developer productivity. |
| Buyer persona | CISO / Chief Compliance Officer          | VP of Engineering       | Follow the money. Who signs the check? Not the person who writes the code.                                                 |
| ROI framing   | Reduces audit prep from weeks to minutes | Makes developers faster | Developer speed is table stakes. Audit cost reduction is a line item a CFO can see.                                        |

---

## BUYER CONVERSATIONS (CISO / Compliance / Legal)

| SAY THIS                                                         | NOT THIS                                   | Why                                                                      |
| ---------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------ |
| Every AI-generated artifact gets a tamper-proof judgment receipt | We run multi-model consensus on your PRs   | They don't care how. They care that it's defensible.                     |
| Admissible audit trail, chain of custody built in                | Cryptographic hash signatures with SHA-256 | Court-admissible is the magic word. SHA-256 is noise.                    |
| Deploys in your existing GitHub Actions pipeline                 | We integrate with your CI/CD               | "GitHub Actions" is concrete. "CI/CD" is abstract.                       |
| Offline-capable, air-gapped environments supported               | We support Ollama models                   | Air-gapped = government/defense signal. Ollama is implementation detail. |

---

## DEVELOPER OUTREACH (Builder Lane)

| SAY THIS                                                     | NOT THIS                       | Why                                                                                           |
| ------------------------------------------------------------ | ------------------------------ | --------------------------------------------------------------------------------------------- |
| Open-source action, 5-minute install                         | Enterprise governance platform | Developers run from enterprise language. They adopt tools that are easy.                      |
| Catches what your linter can't -- logic risks, not syntax    | AI code reviewer               | "AI code reviewer" = commodity. Logic risk detection = differentiated.                        |
| Works with your existing models (Claude, GPT, Gemini, local) | Multi-model consensus engine   | Model-agnostic is the feature. Consensus engine is the how.                                   |
| Free tier, no credit card                                    | Contact sales                  | Developers don't contact sales. Ever.                                                         |
| Starter at $499/mo, 30-day free trial                        | $2,000/mo minimum              | $499 is justifiable to a manager. $2K requires a procurement cycle. Land first, expand later. |

---

## PRICING CONVERSATIONS

| Context                    | SAY THIS                                                                                        | NOT THIS                                  | Why                                                                                                           |
| -------------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Tier naming                | Free -> Starter -> Team -> Org -> Enterprise                                                    | Free -> Team (skip)                       | The cliff from $0 to $2K killed conversion. Starter at $499 is the bridge.                                    |
| Starter framing (to devs)  | "Dashboard, Slack alerts, evidence search -- $499/mo, 30-day free trial"                        | "$499 platform fee"                       | Lead with what they get, not what they pay.                                                                   |
| Starter framing (to CISOs) | "Tamper-proof audit trail with cloud dashboard -- starts at $499/mo, less than your Drata bill" | "Our cheapest paid tier"                  | Anchor to Drata/Vanta pricing. $499 sounds like a bargain vs $625-$833.                                       |
| Why not per-seat           | "Platform fee -- govern everything from day one"                                                | "$25/developer/month"                     | Per-seat penalizes adoption. Platform fee means every PR is governed. BYOK means we do not meter model usage. |
| Upgrade trigger            | "When you hit 10 repos or need custom rubrics, Team unlocks that"                               | "You should upgrade to get more features" | Natural growth triggers, not upsell pressure.                                                                 |

## COMMON TRAPS

Things that sound good but hurt us:

| Trap                                | Why it hurts                                                                                    | Fix                                                                        |
| ----------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| "We're like CodeRabbit but better"  | Anchors us to a category we lose. They have more users, more funding, more runway.              | "We're in a different category. They review code. We govern artifacts."    |
| "AI governance platform"            | No one has budget for this. It's a category that doesn't exist.                                 | "Artifact governance" -- fits existing compliance budget lines.            |
| "Our cryptographic proof system..." | Eyes glaze over in 3 seconds. Technical buyers already get it; non-technical buyers never will. | "Tamper-proof audit trail, admissible in court."                           |
| Leading with features               | Features don't close. Problems close.                                                           | Lead with the risk: "Who's liable when AI-generated code causes a breach?" |
| Pitching to the wrong person        | VP Eng says "cool" and nothing happens.                                                         | Find the CISO or CCO. Follow the money.                                    |
| "We use AI to review AI"            | Sounds circular. Sounds like a gimmick.                                                         | "Independent verification layer -- like an auditor for your AI output."    |

---

## KRISTEN'S RULE

**Follow the money.** Every outbound message must answer two questions:

1. Which person has budget authority?
2. Which line item does this come from?

If you can't answer both, don't send the message.

---

Updated after Kristen sync #2, Feb 19 2026
