# GuardSpine Landing Page Content -- Full Buildable Spec

**Version:** 1.1 (audit fixes applied)
**Date:** February 21, 2026
**Authors:** David Youssef, Igor Malovitsa
**Purpose:** Complete copy for both landing pages, ready to implement.
**Method:** Psychological extrapolated volition -- every word choice maps to the target persona's internal motivational architecture.

---

## Persona Psychology (Read This First)

### Persona A: The Developer / Engineering Lead

**Who they are:** Senior Engineer, Staff Engineer, Engineering Manager, DevOps Lead. 28-42 years old. 5-15 years in industry. Manages a team or leads technical decisions for a team.

**Internal state:** Guilt + resignation. They know code reviews are inadequate. PRs get rubber-stamped. "LGTM" is a reflex, not a review. Junior developers and AI copilots produce code that nobody truly evaluates before merge. They have rationalized this as "that is just how it works" because there is no time and no better option.

**Pain points we address:**

1. Review fatigue -- approving PRs they did not fully read
2. AI copilot code (Cursor, Copilot, Claude) shipping without real review
3. Compliance requests from security teams that interrupt real engineering work
4. Post-deploy findings that should have been caught in review
5. The "LGTM" shame -- everyone does it, nobody admits it

**What annoys them:**

1. "Schedule a demo" as a CTA (they will not call sales)
2. Tools requiring org-wide buy-in before they can try them
3. Per-seat pricing that punishes adoption
4. Marketing that says "AI-powered" without showing what the AI actually does
5. Vendor lock-in and proprietary systems they cannot inspect
6. Enterprise language ("leverage", "synergize", "transform")

**What signals trust:**

1. Open source (they can read the code before installing)
2. GitHub Action (their native workflow -- not another platform to log into)
3. BYOK (they pick the models, not the vendor)
4. Fast install (5 minutes or they bounce)
5. Works on the first PR (immediate value, not "onboard for 3 weeks")
6. Specific numbers over vague claims (737 tests, L0-L4 risk tiers, 5 models)
7. No forced login or credit card for the free tier
8. A real GitHub repo link, prominently displayed

**Emotional arc of the page:** GUILT -> RELIEF -> AGENCY

- "You know reviews are broken" (guilt acknowledged, not judged)
- "This catches what you miss" (relief -- someone built the thing)
- "Install it in your pipeline, your way" (agency -- they control everything)

---

### Persona B: The CISO / Chief Compliance Officer

**Who they are:** CISO, VP Security, Chief Risk Officer, Head of GRC, Director of Compliance. 38-55 years old. 15-25 years in industry. Rose through either technical security or audit/compliance tracks.

**Internal state:** Fear + frustration + isolation. They are personally accountable for everything engineering ships. They do not write code. They do not review PRs. But when AI-generated code causes a breach, it is their signature on the compliance report. Engineers move fast and treat governance as a speed bump. The CISO is the "no" person nobody invites to architecture reviews.

**Pain points we address:**

1. "Who approved this code?" -- they cannot answer for AI-generated changes
2. Audit prep takes weeks -- chasing email chains, Slack threads, Jira tickets to reconstruct who reviewed what
3. AI adoption is accelerating and they have zero visibility into what ships
4. Board asks "Are we compliant with the EU AI Act?" and they have no evidence
5. Existing tools (Vanta, Drata) track infrastructure compliance but NOT code-level governance
6. SOC2 auditors ask for code review evidence and all they can show is a GitHub "Approved" click
7. They know rubber-stamping happens but cannot prove proper review occurred

**What annoys them:**

1. Developer tools that claim to solve governance (different problem)
2. "Open source" pitched without a clear business model (who maintains this in 3 years?)
3. Startups with no track record asking for enterprise trust
4. Products that require engineers to change their workflow (adoption resistance becomes the CISO's problem)
5. Opaque pricing ("contact us for pricing" means "we will charge whatever we can")
6. Tools that produce data without producing structured EVIDENCE

**What signals trust:**

1. "Tamper-proof" and "court-ready" (legal defensibility language without making a legal claim)
2. Compliance framework names in the first fold (SOC2, DORA, HIPAA, EU AI Act)
3. Comparison to tools they already know (Vanta, Drata pricing as anchors)
4. Evidence they can hand directly to auditors (not raw logs, structured bundles)
5. Zero workflow disruption for engineers (adoption without resistance)
6. Open source = independently verifiable (not trusting vendor claims on faith)
7. Named founders with security and cryptography credentials
8. Pricing anchored below what they already pay for compliance tools

**Emotional arc of the page:** FEAR -> RECOGNITION -> CONTROL

- "AI is writing your code and nobody can prove it was reviewed" (fear named)
- "We built the evidence layer that is missing" (recognition -- someone understands)
- "Your engineers install it. You get the dashboard." (control -- no adoption battle)

---

# PAGE A: DEVELOPER-FACING

**URL:** guardspine.ai/dev
**Tone:** Direct, builder-friendly, slightly irreverent. Show the code. No enterprise speak.

---

## Section 1: Hero

**Headline:**
Stop satisfying governance with a rubber stamp.

**Subhead:**
Open-source GitHub Action. AI-powered code governance with tamper-proof audit trails. Install in 5 minutes. Works with your models.

**Primary CTA button:** Install the GitHub Action
**Secondary CTA link:** or try the Starter dashboard free for 30 days

**Design note:** Dark background, monospace headline font. No stock imagery. The hero should feel like a terminal, not a marketing page. Show a miniature PR comment screenshot or ASCII-art evidence bundle inline.

---

## Section 2: The Problem

**Section headline:** You know how code reviews actually work.

**Body copy:**

The PR lands. You scan the title. Maybe the diff. You click Approve.

You tell yourself you will come back and read it properly. You will not. Neither will anyone else. This is how most code reviews work at every company shipping software today.

Now multiply that by AI. Cursor, Copilot, and Claude are generating code faster than any team can review it. The PR queue grows. The rubber-stamping accelerates. The governance gap widens.

Nobody talks about it because everyone does it.

GuardSpine does not judge you for it. It catches what you miss.

**Design note:** This section should breathe. Short paragraphs. No icons or illustrations. Just text on a clean background. The reader should feel seen, not sold to.

---

## Section 3: How It Works

**Section headline:** Three steps. Five minutes. Every PR governed.

**Step 1: Install**

```yaml
# .github/workflows/guardspine.yml
name: GuardSpine Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: DNYoussef/codeguard-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

Add one YAML file to your repo. That is the entire install.

**Step 2: Every PR gets risk-tiered and reviewed**

When a PR opens, GuardSpine analyzes the changed files and assigns a risk tier (L0 through L4) based on file patterns and content sensitivity. Higher-risk changes get reviewed by more models. Each model reviews independently, then cross-checks the others anonymously. Consensus determines the verdict.

**Step 3: Judgment receipt on every PR**

The output is a signed evidence bundle: which models reviewed, what they found, how they voted, and a tamper-evident hash chain. It appears as a PR comment. Your compliance team can verify it offline.

**Design note:** Show the actual YAML. Show a real (or realistic) PR comment screenshot. Show a JSON snippet of the evidence bundle. Developers trust what they can read, not what they are told.

---

## Section 4: What Makes This Different

**Section headline:** Not another AI code review tool.

**Body copy:**

Code review tools suggest changes. GuardSpine creates proof.

Every PR produces a judgment receipt -- a cryptographically signed record of who reviewed it, what was found, and what was decided. That record cannot be altered after the fact. Your compliance team, your auditors, and (if it ever comes to it) a court can verify it independently.

This is governance, not code review. The distinction matters when the question is "who approved the code that caused the breach?"

**Four trust pillars (shown as a grid or horizontal bar):**

| Open Source                                                                    | BYOK                                                                                                | No Lock-In                                                                            | Offline-Capable                                                           |
| ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Read every line of the review engine on GitHub. 737 tests. Apache 2.0 license. | Bring your own API keys. Claude, GPT, Gemini, or local Ollama. Your models, your cost, your choice. | It is a GitHub Action. No platform to depend on. Remove the YAML file and it is gone. | Runs with Ollama in air-gapped environments. No data leaves your network. |

**Design note:** The trust pillars should look like a technical spec, not marketing badges. Monospace text. No gradient backgrounds. The GitHub repo link should be a prominent button: "View source on GitHub."

---

## Section 5: What You Get

**Section headline:** Free. Or $499/mo if you want the dashboard.

**Two-column comparison:**

### Free -- $0/mo forever

- Full review engine (risk-tiered L0-L4, multi-model deliberation, consensus voting)
- Evidence bundles as signed JSON on every PR
- Community rubric packs (open-source YAML templates)
- Works with any model (BYOK)
- Unlimited repos, unlimited contributors
- Self-managed. No cloud. No account needed.

[Install the GitHub Action]

### Starter -- $499/mo (or $399/mo annual)

Everything in Free, plus:

- Cloud dashboard (PR history, risk analytics, finding trends)
- Slack notification cards (approve/reject alerts, finding summaries)
- Evidence management (search, filter, export JSON + CSV)
- Standard rubric library (pre-built industry templates)
- Up to 10 connected repos, 25 contributors
- Email support (48-hour SLA)
- 30-day free trial. No credit card.

[Start your 30-day free trial]

### Need more?

Team at $2,000/mo adds custom rubric builder, Jira + Microsoft Teams, compliance report templates (SOC2, DORA, HIPAA), unlimited repos, and priority support.

[Talk to us about Team and Org tiers]

**Design note:** Lead with Free. The developer's first instinct is "let me try it for free." Starter is the upsell they discover after they see value. Do NOT hide Free below the fold.

---

## Section 6: For Your Compliance Team

**Section headline:** Your CISO will thank you.

**Body copy:**

GuardSpine produces exactly what compliance teams need: structured evidence that code review happened, who did it, what was found, and what was decided. Every PR. Automatically.

Instead of scrambling to reconstruct audit trails before SOC2 or DORA deadlines, your compliance team gets a searchable evidence library that updates with every merge.

You install a GitHub Action. They get audit evidence. Nobody changes workflow.

[Send this page to your CISO]

**Mailto pre-fill:**

- To: (empty -- user fills in)
- Subject: "Code governance tool worth 5 minutes -- GuardSpine"
- Body: "Hey -- we have been using an open-source GitHub Action called GuardSpine that creates tamper-proof audit trails for every PR. It produces structured evidence bundles that map to SOC2/DORA/HIPAA. Thought this might help with our compliance reporting. The security-focused overview is here: https://guardspine.ai/security"

**Design note:** This section exists because of the pharmaceutical model -- "ask your CISO about GuardSpine." It should feel like a helpful bridge, not a corporate upsell. Light background, minimal styling.

---

## Section 7: Email Capture / CTA

**Headline:** Start governing code in 5 minutes.

**Two paths:**

**Path 1:** Install the free GitHub Action now.
[View on GitHub] -> links to github.com/DNYoussef/codeguard-action

**Path 2:** Try the Starter dashboard free for 30 days.
[Email input field] [Start free trial]

"No credit card required. Cancel anytime. Your models, your pipeline, your data."

---

## Section 8: Footer

- GitHub: github.com/DNYoussef/codeguard-action
- Documentation: (link)
- Pricing: guardspine.ai/pricing
- Security page: guardspine.ai/security
- Privacy Policy: guardspine.ai/privacy
- Terms of Service: guardspine.ai/terms
- Founded by David Youssef and Igor Malovitsa. Built for engineers who ship.

---

---

# PAGE B: CISO-FACING

**URL:** guardspine.ai/security
**Tone:** Professional, risk-focused, compliance-aware. No humor. Numbers and frameworks. Every claim backed by a mechanism.

---

## Section 1: Hero

**Headline:**
Every AI-generated code change. Reviewed. Logged. Court-ready.

**Subhead:**
Tamper-proof governance for every pull request. Starts at $499/mo -- less than your Drata bill.

**Benefit bar (below subhead, above CTA):**
Judgment receipts for every PR | Deploys as a GitHub Action | Works with your existing pipeline

**Primary CTA button:** Request a demo
**Secondary CTA link:** See a sample judgment receipt

**Design note:** Light professional background. Clean serif or sans-serif headline. Compliance framework logos in a subtle bar below the hero: SOC2, DORA, HIPAA, EU AI Act, ISO 27001. These logos signal "this is our world" to the CISO before they read a single word.

---

## Section 2: The Risk

**Section headline:** AI is writing your code. Who is proving it was reviewed?

**Body copy:**

Your engineering teams adopted AI code generation. Cursor, Copilot, Claude, and internal agents produce an increasing share of every deployment. Development velocity has never been higher.

But governance has not kept up.

When an auditor asks "show me the review trail for this deployment," your team produces a GitHub approval click -- a single button press with no evidence of what was actually evaluated. That is not governance. That is a checkbox.

When AI-generated code causes a data breach, a compliance failure, or a regulatory violation, the question will not be "did someone click Approve?" The question will be "can you prove the change was properly reviewed, by whom, and what they found?"

If you cannot answer that question with structured, tamper-proof evidence, you have a liability gap.

**Design note:** No fear-mongering. State facts. CISOs respect peers who name risks precisely without exaggerating. The tone should read like an internal risk assessment memo, not a sales page.

---

## Section 3: The Evidence Layer

**Section headline:** Judgment receipts: structured proof that governance happened.

**Body copy:**

GuardSpine produces a signed evidence bundle for every code change that passes through your CI/CD pipeline. Each bundle contains:

**What is in a judgment receipt:**

- **Risk tier assigned** (L0-L4) based on file sensitivity and change scope
- **Models that reviewed** -- which AI models evaluated the change, identified by provider, model ID, and version
- **Independent findings** -- what each model found, categorized by severity
- **Cross-check results** -- whether models agreed or disagreed after anonymous review of each other's findings
- **Consensus decision** -- the final verdict (merge, conditions, or block) with agreement score
- **Hash chain** -- SHA-256 signatures linking every element. If any component is altered after the fact, the chain breaks and verification fails.

**Why it matters:**

The hash chain makes the evidence tamper-evident. An offline verifier can confirm that the receipt has not been modified since generation. This is the same cryptographic principle used in financial audit trails and legal chain-of-custody systems.

This is not a log file. It is structured, signed, independently verifiable proof.

[See a sample judgment receipt] (link to example JSON or rendered view)

**Design note:** Show a real evidence bundle -- either a formatted JSON snippet or a clean rendered view. CISOs need to see the OUTPUT, not the architecture. The sample receipt is the most important visual on this page.

---

## Section 4: Compliance Mapping

**Section headline:** Maps to the frameworks you are already audited against.

**Grid layout (5 cards):**

### SOC 2

GuardSpine evidence bundles satisfy CC6.1 (logical access), CC8.1 (change management), and CC7.2 (monitoring) control requirements. Export evidence directly in the format your auditor expects.

### DORA (Digital Operational Resilience Act)

Article 6a requires ICT change management controls for financial entities. GuardSpine produces the governance evidence that proves every code change was reviewed and approved -- the requirement that has been enforceable since January 2025.

### HIPAA Security Rule

Section 164.312(b) requires audit controls for information systems containing ePHI. GuardSpine generates tamper-proof audit records for every code change touching healthcare systems.

### EU AI Act

Articles 9 and 17 require risk management and quality management for AI systems. GuardSpine produces the artifact-level governance evidence these requirements demand -- rolling out through August 2026.

### ISO 27001

Annex A.12.1.2 (change management) and A.14.2.2 (secure development policy) require documented change control procedures. GuardSpine provides automated, tamper-proof change governance records that satisfy these controls without manual documentation overhead.

**Below the grid:**

"GuardSpine does not replace your compliance platform. Vanta and Drata prove your infrastructure is configured correctly. GuardSpine proves your code changes were governed. They are complementary."

**Design note:** Compliance framework names should be visually prominent -- large text, icon or shield graphic for each. CISOs scan for framework names before reading paragraphs. The Vanta/Drata complement framing is critical: it positions GuardSpine as additive, not competitive, which reduces objection friction.

---

## Section 5: How It Deploys

**Section headline:** Your engineers install a GitHub Action. You get the dashboard.

**Body copy:**

GuardSpine deploys as a single GitHub Action in your existing CI/CD pipeline. There is no infrastructure to provision, no agents to install on developer machines, and no workflow changes required.

**For your engineering team:**

- One YAML file added to the repository
- Reviews trigger automatically on every pull request
- Models run in the pipeline using the team's own API keys (BYOK)
- Results appear as PR comments -- no new tool to learn

**For you:**

- Cloud dashboard with PR history, risk distribution, and finding trends
- Slack notifications for high-risk findings and approval requests
- Evidence management: search, filter, export (JSON + CSV) for audit prep
- Audit log with 90-day retention (1-year on Team, 3-year on Org)

**The adoption problem is solved by design.** Your engineers do not need to learn a new tool or change their workflow. They add a YAML file and keep working the way they already work. You get structured evidence without creating organizational friction.

**Design note:** Split layout. Left column: what engineers see (terminal/code aesthetic). Right column: what the CISO sees (dashboard screenshot, Slack card screenshot). The visual contrast reinforces the message: "two views of the same system."

---

## Section 6: Why Open Source

**Section headline:** You should not trust a proprietary tool to audit your code.

**Body copy:**

The GuardSpine review engine is open source (Apache 2.0 license). Every line of code that evaluates your pull requests, assigns risk tiers, runs model deliberation, and generates evidence bundles is publicly auditable.

This is a structural decision, not a marketing tactic.

A governance tool that cannot be independently verified is asking you to trust the vendor's word that governance happened. That defeats the purpose. Open source means your security team, your auditors, or any third party can read the code and confirm it does what it claims.

The business is built on the platform layer above the engine: dashboard, integrations, compliance reporting, rubric management, and support. The engine is free and open. The platform is where the subscription lives.

**Trust signals (horizontal bar):**

- GitHub: github.com/DNYoussef/codeguard-action
- 428 automated tests
- Apache 2.0 license
- Used by (number) organizations (update when data exists)

**Design note:** This section directly addresses the CISO objection "why would I trust a startup?" The answer is: you do not have to trust us, you can verify us. This is the strongest argument for open-core governance and should be visually prominent.

---

## Section 7: Pricing

**Section headline:** Starts at less than your Drata bill.

**Pricing cards (4 tiers):**

### Starter -- $499/mo

$4,788/yr (save 20% annual)

- Tamper-proof audit trail for every PR
- Cloud dashboard with risk analytics
- Slack alerts for findings and approvals
- Evidence management (search, export)
- Standard rubric library
- Up to 10 repos, 25 contributors
- Email support (48-hour SLA)

[Request a demo]

30-day free trial available.

### Team -- $2,000/mo

$19,200/yr

Everything in Starter, plus:

- Custom governance rules (rubric builder)
- Jira integration (tickets from findings)
- Microsoft Teams notifications
- Compliance report templates (SOC2, DORA, HIPAA)
- Unlimited repos and contributors
- Priority support (4-hour SLA)

[Request a demo]

### Org -- $12,000/mo

$115,200/yr (save 20% annual)

Everything in Team, plus:

- Multi-team RBAC
- ServiceNow integration
- SSO/SAML
- Advanced compliance dashboards
- Dedicated CSM
- 3-year audit log retention

[Request a demo]

### Enterprise -- Custom

On-prem and air-gapped deployment. Custom integrations. 99.9% SLA. Compliance consulting.

[Contact us]

**Below pricing:**

"All tiers include the same open-source review engine. Customers bring their own model API keys (BYOK) -- GuardSpine never touches your AI inference costs. Platform fee, not per-seat. Govern every PR from day one."

**Design note:** Starter should be visually highlighted (border, "Most Popular" badge, or slight elevation). Annual pricing shown. The "less than your Drata bill" framing is the CISO-specific anchor -- Drata Foundation is ~$625/mo, Vanta Core is ~$833/mo. $499 is a deliberate undercut.

---

## Section 8: FAQ (CISO-Specific)

**Q: How is this different from Vanta or Drata?**
Vanta and Drata automate compliance evidence for infrastructure (cloud config, access controls, policy documents). GuardSpine produces governance evidence for code changes -- the artifact-level audit trail that compliance platforms do not cover. They are complementary. Many organizations will use both.

**Q: Do my engineers have to change their workflow?**
No. GuardSpine runs as a GitHub Action in the existing CI/CD pipeline. Engineers add one YAML file to their repo. Reviews happen automatically on every PR. Results appear as PR comments. There is nothing new to learn.

**Q: What models does it use? Do we pay for inference?**
BYOK -- your team configures their own API keys for Claude, GPT, Gemini, or local Ollama models. GuardSpine orchestrates the review but never touches inference costs. You control model selection, spend, and data residency.

**Q: Can this run in air-gapped environments?**
Yes. GuardSpine works with Ollama models running locally. No data leaves your network. This is designed for the security requirements of government, defense, and financial institutions.

**Q: Is the evidence actually court-admissible?**
The evidence bundles use SHA-256 hash chains that make them tamper-evident. An offline verifier can confirm no component has been modified since generation. This is the same cryptographic standard used in digital forensics and legal chain-of-custody systems. Whether specific evidence is admitted in a specific proceeding depends on jurisdiction and context, but the technical standard meets the bar.

**Q: What happens if GuardSpine shuts down?**
The review engine is open source (Apache 2.0 license). Your organization can fork it and continue running it independently. Evidence bundles generated to date remain valid -- the hash chain verification is self-contained and does not depend on GuardSpine infrastructure.

---

## Section 9: Email Capture / CTA

**Headline:** See how GuardSpine produces audit-ready evidence for every code change.

**CTA form:**

- Work email [input]
- Company [input]
- Title / Role [input]
- [Request a demo]

"We will schedule a 20-minute walkthrough showing a live PR review, the evidence bundle it produces, and how it maps to your compliance requirements."

**Below the form:**

Or explore on your own:

- [View the open-source engine on GitHub]
- [Read the documentation]
- [See a sample judgment receipt]

---

## Section 10: Footer

- About: Founded by David Youssef and Igor Malovitsa. Built to close the governance gap between AI velocity and compliance requirements.
- GitHub: github.com/DNYoussef/codeguard-action
- Documentation: (link)
- Developer page: guardspine.ai/dev
- Security: security@guardspine.ai
- Privacy Policy: guardspine.ai/privacy
- Terms of Service: guardspine.ai/terms
- SOC 2 | DORA | HIPAA | EU AI Act | ISO 27001

---

---

# SHARED ELEMENTS

## Email Capture Backend

Both pages capture email signups into the same system. Fields differ by page:

**Developer page:** Email only (minimal friction). Tag: source=dev-page.
**CISO page:** Email + Company + Title. Tag: source=security-page.

Signups trigger:

1. Confirmation email with next steps
2. Starter trial activation link (30-day, no credit card)
3. Entry into CRM for follow-up (Kristen's network, Eric intro evidence)

## Demo Request Workflow (CISO Page)

Demo request form submissions (email + company + title) follow a separate path:

1. Instant email notification to David (david@guardspine.ai) with all form fields
2. Slack notification to #leads channel (company name, title, timestamp)
3. Auto-reply to requester: "Thank you. We will schedule a 20-minute walkthrough within 24 hours."
4. David sends Cal.com booking link within 24 hours
5. Entry into CRM tagged source=security-page, type=demo-request

## Analytics (Both Pages)

Track per Kristen's experiment design (09-landing-page-plan.md):

- Email signups per page (raw count)
- Title/role of signups (are we getting CISOs or developers?)
- Time on page
- Which page gets shared more (UTM tracking)
- Trial activations from each page
- Free GH Action installs from dev page

## Social Proof Strategy

We have zero paying customers. Handle this honestly:

1. **Developer page:** The open-source repo IS the social proof. Link it prominently. "737 tests passing" and "Apache 2.0 license" signal engineering discipline. If/when stars accumulate, show them.

2. **CISO page:** Compliance framework logos (SOC2, DORA, HIPAA, EU AI Act) signal the category. The Vanta/Drata comparison signals market awareness. The open-source verification angle ("you do not have to trust us, you can verify us") turns the lack of logos into a strength.

3. **Neither page:** Do NOT fabricate testimonials, imply customers we do not have, or use "trusted by" language without real logos. Honesty at this stage is a trust signal, not a weakness.

## Design System Notes

- **Developer page:** Dark mode. Monospace fonts for headlines and code. Minimal color -- white/gray text on dark background with one accent color for CTAs. Should feel like a well-designed README or developer documentation site.

- **CISO page:** Light mode. Professional sans-serif (Source Sans 3, DM Sans, or similar -- NOT Inter, which is an AI slop tell). White background with dark text. Subtle blue accents for trust. Should feel like a Vanta or Drata marketing page -- the CISO should recognize the visual language of their existing tool landscape.

- **Both pages:** No stock photography. No "diverse team at whiteboard" images. Use screenshots of actual product output (PR comments, dashboard, Slack cards, evidence bundles). If screenshots are not ready, use realistic mockups that match the actual data structures.

---

## SEO and Meta Tags

**Developer page (guardspine.ai/dev):**

- Title: "GuardSpine -- Open-Source Code Governance for Engineering Teams"
- Meta description: "AI-powered code governance with tamper-proof audit trails. GitHub Action installs in 5 minutes. BYOK. Free forever, or $499/mo for the dashboard."
- OG image: Dark card with headline text + YAML snippet preview (1200x630)
- Canonical: https://guardspine.ai/dev

**CISO page (guardspine.ai/security):**

- Title: "GuardSpine -- Tamper-Proof Code Governance for Compliance Teams"
- Meta description: "Judgment receipts for every pull request. Maps to SOC2, DORA, HIPAA, and EU AI Act. Starts at $499/mo. Request a demo."
- OG image: Light card with headline text + compliance framework logos (1200x630)
- Canonical: https://guardspine.ai/security

**Both pages:**

- robots: index, follow
- JSON-LD: Organization schema (name, url, logo, founders)
- favicon: GuardSpine logo (SVG preferred, with PNG fallback)

## Error and Edge States

**Form submission failure:**

- Show inline error toast: "Something went wrong. Please try again." (red, auto-dismiss 5s)
- Retry automatically once after 2s before showing error
- Never lose the user's input -- keep form fields populated on error

**JS disabled:**

- Forms degrade to mailto: links (email to david@guardspine.ai)
- Code blocks render as plain `<pre>` tags (no syntax highlighting, but readable)
- Pricing cards render as static HTML (no toggle, show monthly by default)

**Font loading failure:**

- Dev page fallback: monospace system stack for headlines, system-ui for body
- CISO page fallback: system-ui for all text
- Use `font-display: swap` to prevent invisible text during load

**404 page:**

- Simple page with nav, "Page not found", and links to both landing pages
- Match the theme of whichever page the user was likely trying to reach (dark for /dev/_, light for /security/_)

**GDPR email consent:**

- Both email capture forms include a checkbox: "I agree to receive product updates. See our privacy policy."
- Checkbox must be unchecked by default (GDPR requirement)
- Form does not submit without consent checked

## Tech Stack (decided)

- Hosting: Vercel (free tier)
- Framework: Next.js (App Router) -- handles frontend AND API routes (no separate backend)
- Email capture: Resend (API via Next.js API routes)
- Analytics: Plausible (privacy-friendly, no cookie banner needed)
- Domain: guardspine.ai
- Note: FastAPI/Express components from the library are for the dashboard backend, NOT the landing pages. Landing page API routes use Next.js API routes (TypeScript).

---

_This document is the complete content spec for both landing pages._
_Implements: 09-landing-page-plan.md (strategy), 10-pricing-bridge-spec.md (pricing), 02-messaging-reframe.md (SAY THIS / NOT THIS)._
_Review with Igor before building._
