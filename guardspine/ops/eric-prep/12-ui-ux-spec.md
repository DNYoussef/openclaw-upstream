# GuardSpine Landing Pages -- UI/UX Design Spec

**Version:** 1.1 (audit fixes applied)
**Date:** February 21, 2026
**Purpose:** Anti-slop visual design spec for both landing pages. Every decision justified.
**Method:** Psychological extrapolated volition (visual preferences) + AI slop research + component library mapping.
**Implements:** 11-landing-page-content.md (copy), 09-landing-page-plan.md (strategy), 10-pricing-bridge-spec.md (pricing)

---

## Part 1: AI Slop Anti-Pattern Checklist

Every choice in this spec was made to avoid the following converged AI outputs. If you catch yourself building any of these, stop and redesign.

### Layout Slop

- [ ] NO Holy Trinity Grid (3 equal feature cards with icons below hero)
- [ ] NO uniform section padding (every section `py-16` or `py-24`)
- [ ] NO perfect centering of everything (body text must be left-aligned)
- [ ] NO canonical SaaS section order (Hero > Logo Bar > Features > Testimonials > Pricing > FAQ > CTA)

### Typography Slop

- [ ] NO Inter/Roboto/System-UI as sole typeface (pair display + body fonts)
- [ ] NO Space Grotesk (second-tier convergence font)
- [ ] NO timid typographic scale (hero headline must be 2.5x+ body size)

### Color Slop

- [ ] NO indigo-500 / purple-to-blue gradient (the #1 AI slop tell)
- [ ] NO beige-teal "calm SaaS" palette (#faf5f0 + #008275)
- [ ] NO gradient mesh blobs behind content
- [ ] NO glassmorphism (backdrop-blur-xl on translucent cards)
- [ ] NO evenly-distributed palette (use 60-30-10 rule)

### Imagery Slop

- [ ] NO AI-generated hero illustrations
- [ ] NO generic SVG illustrations (Undraw, Storyset)
- [ ] NO floating angled dashboard screenshots with drop shadows
- [ ] NO stock photography of any kind
- [ ] NO Lucide/Heroicons as sole icon set (at minimum, customize)

### Copy Slop

- [ ] NO "Revolutionize/Transform/Unlock/Supercharge/Empower/Leverage" verbs
- [ ] NO "Lightning Fast / Secure by Default / Easy to Use" value props
- [ ] NO "In today's ever-evolving digital landscape..." filler
- [ ] NO fake testimonials or fabricated social proof
- [ ] NO "Get Started" as CTA text (be specific to the action)

### Component Slop

- [ ] NO universal rounded-2xl on everything (vary border-radius by component)
- [ ] NO whisper-thin shadows at 0.1 opacity (commit to visible shadows or remove them)
- [ ] NO uniform fade-in-on-scroll applied to every section (selective opacity transitions on specific components are acceptable when purpose-driven)
- [ ] NO three-tier pricing with middle highlighted unless that reflects reality

### Technical Slop

- [ ] NO hardcoded Tailwind color classes (use CSS custom properties / theme config)
- [ ] NO missing error states on forms
- [ ] NO missing ARIA labels and keyboard navigation
- [ ] NO missing prefers-reduced-motion media queries

---

## Part 2: Visual Psychology by Persona

### Developer (Page A) -- Visual Trust Model

**Daily visual environment:** GitHub (dark), VS Code (dark), terminals, Hacker News, Stripe/Vercel/Tailwind docs.

**What pleases them visually:**

| Signal                       | Why It Works                                           | Implementation                                   |
| ---------------------------- | ------------------------------------------------------ | ------------------------------------------------ |
| Dark mode                    | Matches their IDE/terminal/GitHub -- feels "home"      | Dark backgrounds, light text                     |
| Monospace type               | Signals "this is technical, not marketing"             | Use for headlines and code                       |
| Code examples above the fold | Proves the product is real and technical               | YAML snippet in hero                             |
| High information density     | They are used to dense terminal output                 | Shorter section padding, more content per screen |
| Copy-paste ready code blocks | Signals engineering discipline                         | Syntax highlighted with copy button              |
| Fast page load               | They notice page weight; 3MB hero = instant skepticism | Target < 200KB total page weight                 |
| Real product output          | Screenshots of actual PR comments, not mockups         | Use codeguard-action output                      |
| Prominent GitHub link        | "We have nothing to hide"                              | In nav and hero                                  |

**What annoys them visually:**

| Anti-Signal               | Why It Fails                           | Avoidance                                       |
| ------------------------- | -------------------------------------- | ----------------------------------------------- |
| Gradient blob backgrounds | "AI startup aesthetic"                 | Flat solid dark backgrounds only                |
| Generic illustrations     | "Designed by someone who doesn't code" | Zero illustrations -- screenshots and code only |
| Excessive white space     | "Hiding lack of substance"             | Dense, information-rich layout                  |
| Auto-playing anything     | "This site doesn't respect me"         | No video, no carousel, no auto-scroll           |
| Enterprise language       | "This wasn't built for me"             | No "leverage", "synergy", "solution"            |
| Sticky CTAs               | "Desperate"                            | CTAs at natural decision points only            |
| Background video          | Bandwidth waste, mobile killer         | Static content only                             |
| Cookie modal              | First-impression destroyer             | Small bottom bar if legally required            |

**Reference sites:** stripe.com/docs, tailwindcss.com, linear.app, vercel.com

---

### CISO (Page B) -- Visual Trust Model

**Daily visual environment:** Vanta/Drata dashboards, executive reports, Outlook email, Gartner PDFs, CrowdStrike/Palo Alto marketing.

**What pleases them visually:**

| Signal                          | Why It Works                                           | Implementation                           |
| ------------------------------- | ------------------------------------------------------ | ---------------------------------------- |
| Light professional layout       | Matches compliance tool landscape (Vanta, Drata)       | White/light gray backgrounds             |
| Compliance framework logos      | Instant category recognition before reading text       | SOC2, DORA, HIPAA, EU AI Act in hero bar |
| Structured data (tables, grids) | They THINK in structured data                          | Comparison tables, feature matrices      |
| Clear visible pricing           | Respects their time; they need numbers for procurement | All tiers with annual pricing shown      |
| Conservative color palette      | Signals stability, not "founded last Tuesday"          | Navy/teal accent on white, minimal color |
| Dashboard screenshots           | Proof the product exists beyond a landing page         | Real or high-fidelity dashboard mockup   |
| Evidence output sample          | They need to see WHAT they get, not HOW it works       | Rendered judgment receipt (not raw JSON) |
| Human contact path              | CISOs validate through conversation before buying      | "Request a demo" with calendar booking   |

**What annoys them visually:**

| Anti-Signal                 | Why It Fails                              | Avoidance                                        |
| --------------------------- | ----------------------------------------- | ------------------------------------------------ |
| Dark mode                   | Reads as "developer tool" -- not for them | Light/white backgrounds only                     |
| Trendy startup aesthetics   | "Will this company exist next year?"      | No neon, no glassmorphism, no animated gradients |
| Code snippets in hero       | "This is for engineers, not me"           | No YAML/terminal output on CISO page             |
| Missing pricing             | "Either too expensive or too early-stage" | Pricing visible without scrolling                |
| "Join our Slack" as contact | "Not a real sales motion"                 | Demo request form with human follow-up           |
| Excessive scrolling         | Busy executives bounce after 3 folds      | Key info in first 2-3 screens                    |
| No product evidence         | "This doesn't exist yet"                  | Screenshots or mockups mandatory                 |
| Chat widget popup           | "Cheap and desperate"                     | No chat widget                                   |

**Reference sites:** vanta.com, drata.com, crowdstrike.com, snyk.io, wiz.io

---

## Part 3: Design System Specifications

### Page A (Developer) -- Dark Technical

**Layout:**

- Content max-width: 960px (documentation-width, not full-bleed marketing)
- Section padding: varies intentionally (hero 80px, dense sections 40px, breathing sections 64px)
- Grid: 12-column base, but most content in 8-column center block
- Code blocks: full content-width, with 16px padding, copy button top-right

**Typography:**

- Headlines: JetBrains Mono (monospace -- "this is for builders"). ONE font, not "or Fira Code."
- Body: system-ui stack (-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif). Zero additional font load.
- Code: Same JetBrains Mono as headlines (consistent technical voice)
- Scale: Hero 56-64px / H2 32-36px / H3 24px / Body 16px / Small 14px
- Line height: 1.2 headlines, 1.6 body, 1.5 code blocks
- Weight: Headlines 700, body 400, links 500
- Font loading: JetBrains Mono Regular (400) + Bold (700) only, WOFF2 format, Latin subset. Budget: ~60KB total. Use `font-display: swap`.

**Color (custom hex -- NOT Tailwind defaults):**

```css
:root[data-page="dev"] {
  /* Backgrounds */
  --bg-primary: #0c0c0c; /* Near-black (not pure #000) */
  --bg-elevated: #161618; /* Slightly lifted surfaces */
  --bg-code: #1c1c2e; /* Code block bg (dark navy tint) */

  /* Text */
  --text-primary: #e0e0e0; /* Warm white (not pure #fff) */
  --text-secondary: #9ca3af; /* Muted gray for secondary content */
  --text-code: #d4d4d8; /* Slightly brighter for code */

  /* Accent -- ONE color only */
  --accent: #22c55e; /* Green ("tests passing", "install", "go") */
  --accent-hover: #16a34a; /* Darker on hover */
  --accent-muted: rgba(34, 197, 94, 0.12); /* Subtle accent backgrounds */

  /* Borders */
  --border-subtle: #27272a; /* Barely visible section dividers */
  --border-default: #3f3f46; /* Card/code block borders */

  /* Semantic */
  --risk-low: #22c55e;
  --risk-medium: #eab308;
  --risk-high: #f97316;
  --risk-critical: #ef4444;
}
```

**Borders and Radius:**

- Cards: 4px radius (sharp, technical -- NOT rounded-2xl)
- Buttons: 6px radius (slightly softer than cards)
- Code blocks: 4px radius with 1px solid var(--border-default)
- Input fields: 4px radius

**Shadows:**

- None. Use border-subtle to separate elements. Flat design. Shadows read as marketing site; borders read as documentation site.

**Imagery:**

- Zero illustrations. Zero stock photos.
- Screenshots: codeguard-action PR comment output
- Code: syntax-highlighted YAML install snippet (the hero visual)
- Evidence bundle: formatted JSON with syntax coloring
- Dashboard: real screenshot if available, otherwise skip (do NOT mock up a fake dashboard)

**Animations:**

- Page load: content visible immediately. No entrance animations.
- Code block copy button: brief "Copied!" toast (200ms fade, 1.5s display)
- Pricing toggle (monthly/annual): instant state change, no transition
- Hover on CTA buttons: background color shift (100ms ease), no transform
- prefers-reduced-motion: disable all transitions

---

### Page B (CISO) -- Light Professional

**Layout:**

- Content max-width: 1120px (wider for comparison tables and pricing grids)
- Section padding: 64px standard, 80px for major section breaks
- Grid: 12-column, using 3 and 4-column grids for compliance cards and pricing
- Above-the-fold must contain: headline, subhead, CTA button, compliance framework logo bar

**Typography:**

- Headlines: DM Sans Bold (professional, not decorative, not monospace). ONE font, not "or Source Sans 3."
- Body: Same family (DM Sans), Regular weight, 16-17px
- Subheads: Same family, Medium weight (subtle hierarchy, not bold)
- Scale: Hero 48-56px / H2 28-32px / H3 22px / Body 16px / Small 14px
- Line height: 1.2 headlines, 1.65 body
- Weight: Headlines 700, subheads 500, body 400
- Font loading: DM Sans Regular (400) + Medium (500) + Bold (700), WOFF2, Latin subset. Budget: ~70KB total. Use `font-display: swap`. Fallback: system-ui.

**Color (custom hex -- NOT Tailwind defaults):**

```css
:root[data-page="security"] {
  /* Backgrounds */
  --bg-primary: #ffffff;
  --bg-elevated: #f8fafc; /* Very light gray for alternate sections */
  --bg-accent-subtle: #eff6ff; /* Barely-blue for highlighted sections */

  /* Text */
  --text-primary: #111827; /* Near-black */
  --text-secondary: #4b5563; /* Medium gray */
  --text-muted: #9ca3af; /* Light gray for captions */

  /* Accent -- deep institutional blue */
  --accent: #1e40af; /* Deep blue (trust, authority, institution) */
  --accent-hover: #1e3a8a;
  --accent-light: #dbeafe; /* Light blue for badges/tags */

  /* Borders */
  --border-subtle: #e5e7eb; /* Light gray section dividers */
  --border-default: #d1d5db; /* Card borders */

  /* Semantic */
  --success: #059669;
  --warning: #d97706;
  --error: #dc2626;

  /* Framework badge colors (must contrast with --accent, not match it) */
  --badge-soc2: #2563eb; /* Lighter blue than accent -- visually distinct */
  --badge-dora: #7c3aed;
  --badge-hipaa: #059669;
  --badge-euai: #0369a1;
  --badge-iso27001: #b45309; /* Amber -- distinct from all other badges */
}
```

**Borders and Radius:**

- Cards: 8px radius (softer than dev page, but NOT rounded-2xl)
- Buttons: 8px radius (matching cards)
- Input fields: 6px radius
- Compliance badges: pill shape (fully rounded) -- intentional contrast
- Pricing cards: 8px radius, 1px border, highlighted card gets 2px accent border

**Shadows:**

- Pricing cards: visible shadow on hover (0 4px 12px rgba(0,0,0,0.08)) -- signals interactivity
- Elevated cards (compliance mapping): subtle shadow (0 1px 3px rgba(0,0,0,0.06))
- Hero: no shadow
- Everything else: no shadow (use background color shifts instead)

**Imagery:**

- Compliance framework logos: SOC2, DORA, HIPAA, EU AI Act as outlined shield/badge icons (not filled -- subtle, professional)
- Dashboard screenshot: real or high-fidelity mockup showing PR history and risk distribution
- Evidence bundle: rendered as a structured document view (NOT raw JSON -- render it like a PDF report)
- Slack notification card: screenshot of the actual Slack approve/reject card
- NO stock photography. NO illustrations. Product output only.

**Animations:**

- Page load: content visible immediately
- Compliance cards: subtle fade-in on scroll (200ms opacity only, no movement, staggered 50ms per card)
- Pricing cards: box-shadow increase on hover (150ms ease)
- FAQ accordion: height transition (200ms ease)
- prefers-reduced-motion: disable all transitions, expand all FAQ items by default

---

## Part 4: Component Library Mapping

### Components to Reuse (from ~/.claude/library/)

| Component            | Path                  | Use On   | Purpose                                                                  |
| -------------------- | --------------------- | -------- | ------------------------------------------------------------------------ |
| **Design System**    | ui/design_system      | Both     | Card, Input, Badge, MetricCard for pricing cards and form inputs         |
| **Radix Dialog**     | ui/radix_dialog       | Both     | Demo request modal (CISO page), trial signup modal (dev page)            |
| **React Hooks**      | react_hooks           | Both     | useDebounce (form input), useLocalStorage (persist pricing toggle state) |
| **React Auth**       | react_auth            | Both     | AuthProvider + useAuth for trial signup/login flow                       |
| **Fetch API Client** | http/fetch_api_client | Both     | Email capture API calls with retry logic                                 |
| **Jest Setup**       | testing/jest_setup    | Frontend | Pre-built mocks for API calls in tests                                   |

**Backend note:** Landing pages use Next.js API routes (TypeScript), NOT Express or FastAPI. The Python/Express components (Express Middleware, Pydantic Base, FastAPI CRUD Router, FastAPI JWT Auth) belong in the dashboard backend and are NOT used on the landing pages. The following library components remain useful for the landing page backend (via Next.js API routes):

| Component              | Path                        | Purpose (adapted for Next.js API routes)                             |
| ---------------------- | --------------------------- | -------------------------------------------------------------------- |
| **Stripe Integration** | payments/stripe             | Starter tier payment processing (TS client works in Next.js)         |
| **Circuit Breaker**    | utilities/circuit_breaker   | Protect against Resend email service failures (port pattern to TS)   |
| **Audit Logging**      | observability/audit_logging | Track trial signups, conversions, demo requests (port pattern to TS) |

### Component Customization Notes

**Design System (ui/design_system):**

- Ships with SolarArcana theme (dark green/gold). Must override CSS variables.
- Dev page: swap to custom dark theme vars (see Part 3 color spec above)
- CISO page: swap to custom light theme vars (see Part 3 color spec above)
- Card component: use for pricing tiers. Set variant="outlined" for standard, variant="elevated" for highlighted tier.
- Input component: use for email capture form. Attach leftIcon for email icon.
- Badge component: use for compliance framework badges on CISO page (variant="info" for SOC2, etc.)
- MetricCard: use for financial proof points ("97% margins", "5-min install", etc.)

**React Auth (react_auth):**

- Use for Starter trial signup and dashboard access control
- Configure: storage='localStorage', autoRefresh=true
- ProtectedRoute wraps the trial dashboard
- Login flow: email signup -> verification email -> trial activation -> dashboard access

**Fetch API Client (http/fetch_api_client):**

- Use restClient for signup form submissions
- Configure retry logic: 2 retries, 1s backoff for email capture (do not lose signups to transient failures)
- Use quickClient for analytics event firing (fire-and-forget, no retry)

### Components NOT to Use

| Component            | Why Not                                                   |
| -------------------- | --------------------------------------------------------- |
| Kanban Store         | No kanban UI on landing pages                             |
| LLM Council Display  | Too technical for landing pages (save for docs/dashboard) |
| Content Pipeline     | Not needed for static landing pages                       |
| Multi-Model Router   | Backend AI routing -- not relevant to landing pages       |
| Trading components   | Wrong domain entirely                                     |
| Banking components   | No bank account linking on landing pages                  |
| AST Visitor          | Code analysis -- not relevant                             |
| Cognitive components | Agent system -- not relevant                              |

---

## Part 5: Gaps Identified (Must Add to Specs)

The component library and slop research revealed these gaps in our landing page plan that need to be addressed:

### Gap 1: No Email Service Integration

The library has no email component. We need:

- Transactional email for signup confirmation and trial activation
- **Recommendation:** Use Resend (recommended in 09-landing-page-plan.md). Build a thin wrapper, not a library component.

### Gap 2: No Analytics Component

The library has metric_collector (backend telemetry) but no frontend analytics tracking.

- Need: Page views, button clicks, scroll depth, UTM parameter capture
- **Recommendation:** Plausible or PostHog (privacy-friendly, as specified in 09-landing-page-plan.md). Add script tag, no component needed.

### Gap 3: No Pricing Toggle Component

The design system has Card, Input, Badge, MetricCard but no pricing-specific components.

- Need: Monthly/Annual toggle switch, highlighted tier card, pricing comparison table
- **Recommendation:** Build a PricingCard component extending Card with: price display, annual/monthly toggle state, feature list, CTA button. Use React Hooks useLocalStorage to persist toggle state across page navigations.

### Gap 4: No Syntax Highlighting Component

Code blocks are central to the developer page but the library has no syntax highlighting.

- Need: YAML, JSON, and shell command highlighting
- **Recommendation:** Use Shiki (SSR-compatible, used by Vercel/Astro) or Prism.js. Build a CodeBlock component with copy button.

### Gap 5: No FAQ Accordion Component

The Radix Dialog exists but no accordion/disclosure component.

- Need: Expandable FAQ items for CISO page
- **Recommendation:** Use Radix Accordion primitive (@radix-ui/react-accordion). Same pattern as Radix Dialog -- headless, style yourself.

### Gap 6: No Compliance Badge Component

The Badge component exists but is generic. Need compliance-specific badges.

- Need: SOC2, DORA, HIPAA, EU AI Act badges with framework-specific icons
- **Recommendation:** Extend Badge with a ComplianceBadge variant. Use outlined shield SVGs (custom, not from an icon library -- to avoid the generic icon feel).

### Gap 7: No Evidence Bundle Renderer

The LLM Council Consensus Display exists but is too complex for a landing page.

- Need: A simplified, read-only view of a judgment receipt for the CISO page "sample receipt" CTA
- **Recommendation:** Build a JudgmentReceipt component that renders a static evidence bundle as a structured document (risk tier, reviewer models, findings, consensus, hash chain). Two variants: JSON view (dev page), document view (CISO page).

### Gap 8: No Form Validation (Frontend)

Design System Input has error states but no validation logic.

- Need: Email validation on signup form, company name validation on demo request form
- **Recommendation:** Use React Hook Form (lightweight) or build minimal validation inline. The library's Spec Validation Framework is Python-only (backend); frontend needs its own.

### Gap 9: No Toast/Notification Component

Need for: "Copied!" on code blocks, "Signup successful!" on form submit, error notifications.

- **Recommendation:** Use Radix Toast (@radix-ui/react-toast) or build a minimal toast with CSS animation. Keep it simple -- 3 states (success, error, info), auto-dismiss after 3s.

---

## Part 6: Page-Specific Layout Wireframes

### Page A (Developer) -- Section Flow

```
+--------------------------------------------------+
|  NAV: Logo | Docs | Pricing | GitHub [icon]      |
|            (fixed, transparent bg, border-bottom) |
+--------------------------------------------------+
|                                                    |
|  HERO (80px top padding)                          |
|  [H1] Stop satisfying governance with a           |
|       rubber stamp.                               |
|  [sub] Open-source GitHub Action. AI-powered...   |
|                                                    |
|  [=== Install the GitHub Action ===]               |
|  [or try the Starter dashboard free for 30 days]  |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  THE PROBLEM (40px padding -- dense)              |
|  [H2] You know how code reviews actually work.    |
|  [left-aligned body text, 3 short paragraphs]     |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  HOW IT WORKS (64px padding)                      |
|  [H2] Three steps. Five minutes.                  |
|                                                    |
|  Step 1: [full-width code block -- YAML]          |
|  Step 2: [left text + right: risk tier diagram]   |
|  Step 3: [left text + right: PR comment screenshot]|
|                                                    |
+--------------------------------------------------+
|                                                    |
|  WHAT MAKES THIS DIFFERENT (48px padding)         |
|  [H2] Not another AI code review tool.             |
|  [body: "Code review tools suggest changes.        |
|   GuardSpine creates proof." + governance vs       |
|   review positioning paragraph]                    |
|                                                    |
|  TRUST BAR (below, compact horizontal, 24px gap)  |
|  [Open Source] [BYOK] [No Lock-In] [Offline]      |
|  (4 columns, monospace labels, 1-sentence each)   |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  PRICING (64px padding)                           |
|  [H2] Free. Or $499/mo if you want the dashboard. |
|  [Monthly|Annual toggle]                          |
|                                                    |
|  +----------+ +----------+ +----------+           |
|  | FREE     | | STARTER  | | TEAM     |           |
|  | $0/mo    | | $499/mo  | | $2,000/mo|           |
|  | features | | features | | features |           |
|  | [Install]| | [Trial]  | | [Talk]   |           |
|  +----------+ +----------+ +----------+           |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  FOR YOUR CISO (40px padding)                     |
|  [H2] Your CISO will thank you.                   |
|  [body] + [Send this page to your CISO] link      |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  FINAL CTA (64px padding)                         |
|  [H2] Start governing code in 5 minutes.          |
|  [Two paths: GitHub install OR trial signup]       |
|                                                    |
+--------------------------------------------------+
|  FOOTER: GitHub | Docs | Pricing | Security       |
+--------------------------------------------------+
```

**Key layout decisions:**

- 7 sections (not the standard 10+ SaaS bloat)
- Section padding VARIES (40/64/80) -- breaks the AI metronomic rhythm
- Code block is the visual centerpiece, not a dashboard screenshot
- "For Your CISO" section breaks the developer-only voice -- pharmaceutical model bridge
- No testimonials section (we have none -- honest)
- No logo bar (we have no customer logos -- honest)

---

### Page B (CISO) -- Section Flow

```
+--------------------------------------------------+
|  NAV: Logo | How It Works | Pricing | Demo [button]|
|            (fixed, white bg, subtle border)       |
+--------------------------------------------------+
|                                                    |
|  HERO (80px top padding)                          |
|  [H1] Every AI-generated code change.             |
|       Reviewed. Logged. Court-ready.               |
|  [sub] Tamper-proof governance for every pull      |
|       request. Starts at $499/mo.                  |
|  [benefit bar: Judgment receipts | GitHub Action   |
|   | Works with your existing pipeline]             |
|                                                    |
|  [=== Request a Demo ===] [See sample receipt]     |
|                                                    |
|  [SOC2] [DORA] [HIPAA] [EU AI Act] [ISO 27001]   |
|  (compliance badge bar -- immediately below hero)  |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  THE RISK (64px padding, bg-elevated)             |
|  [H2] AI is writing your code. Who is proving     |
|       it was reviewed?                             |
|  [left-aligned body, 3 paragraphs]                |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  THE EVIDENCE LAYER (64px padding)                |
|  [H2] Judgment receipts: structured proof.         |
|                                                    |
|  [left: what's in a receipt (structured list)]     |
|  [right: rendered evidence bundle visual]          |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  COMPLIANCE MAPPING (64px padding, bg-elevated)   |
|  [H2] Maps to your existing frameworks.            |
|                                                    |
|  +-------+ +-------+ +-------+ +-------+ +-------+|
|  | SOC 2 | | DORA  | | HIPAA | | EU AI | |ISO    ||
|  | CC6.1 | | Art6a | | 164   | | Art 9 | |27001  ||
|  | CC8.1 | |       | | .312  | | Art17 | |A.12/14||
|  +-------+ +-------+ +-------+ +-------+ +-------+|
|                                                    |
|  "Complementary to Vanta and Drata" note          |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  DEPLOYMENT (64px padding)                        |
|  [H2] Your engineers install it. You get the      |
|       dashboard.                                   |
|                                                    |
|  [left column: engineer experience]                |
|  [right column: CISO experience]                   |
|  (split layout -- different visual treatment)      |
|                                                    |
|  "Share with your engineering team:                |
|   guardspine.ai/dev" (subtle inline link)         |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  WHY OPEN SOURCE (64px padding, bg-elevated)      |
|  [H2] You should not trust a proprietary tool     |
|       to audit your code.                          |
|                                                    |
|  [body: structural decision, not marketing tactic] |
|  [Trust bar: GitHub | 737 tests | Apache 2.0]     |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  PRICING (64px padding)                           |
|  [H2] Starts at less than your Drata bill.         |
|                                                    |
|  (Show annual by default -- CISOs think in annual  |
|   budgets. Monthly price in smaller text below.)   |
|                                                    |
|  +----------+ +----------+ +----------+ +--------+ |
|  | STARTER  | | TEAM     | | ORG      | |ENTERP. | |
|  | $4,788/yr| | $19.2K/yr| | $115K/yr | |Custom  | |
|  | ($499/mo)| |($2K/mo)  | |($12K/mo) | |        | |
|  | features | | features | | features | |features | |
|  | [Demo]   | | [Demo]   | | [Demo]   | |[Contact]| |
|  +----------+ +----------+ +----------+ +--------+ |
|                                                    |
|  "All tiers include the same OSS review engine."   |
|  "BYOK -- no AI inference costs."                  |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  FAQ (64px padding)                               |
|  [H2] Common questions                             |
|  [6 accordion items -- CISO-specific]              |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  DEMO CTA (80px padding, bg-accent-subtle)        |
|  [H2] See how GuardSpine produces audit-ready      |
|       evidence for every code change.              |
|                                                    |
|  [email] [company] [title] [Request a demo]        |
|                                                    |
|  Or: [GitHub] [Docs] [Sample receipt]              |
|                                                    |
+--------------------------------------------------+
|  FOOTER: About | GitHub | Docs | Dev page |        |
|          Security | SOC2 | DORA | HIPAA           |
+--------------------------------------------------+
```

**Key layout decisions:**

- 9 sections (more than dev page -- CISOs need more structured information)
- Compliance badges in hero bar (above the fold, before any reading)
- Alternating bg-primary / bg-elevated backgrounds break monotony without using gradients
- Split layout in Deployment section visually separates "engineer view" from "CISO view"
- Pricing leads with Starter (not Free) -- CISO page is about the paid product
- FAQ exists because CISOs have real objections that must be answered on-page (they will not click through to docs)
- Demo CTA has 3 form fields (email, company, title) -- enough for lead qualification, not so many it creates friction
- Footer includes compliance framework names (SEO + category signal)

---

## Part 7: New Components to Build

Based on gaps identified in Part 5, these custom components are needed:

### 1. CodeBlock

```
Purpose: Syntax-highlighted code with copy button
Tech: React + Shiki (SSR) or Prism.js
Used on: Dev page (hero YAML, evidence JSON, install commands)
Props: language, code, showLineNumbers, copyable
```

### 2. PricingCard

```
Purpose: Tier display with price, feature list, CTA
Tech: React + Design System Card extension
Used on: Both pages (different tier selections)
Props: name, price, annualPrice, features[], ctaText, ctaUrl, highlighted
```

### 3. PricingToggle

```
Purpose: Monthly/Annual switch
Tech: React + useLocalStorage (from library)
Used on: Both pages
Props: onChange, defaultValue
State: persisted to localStorage
```

### 4. ComplianceBadge

```
Purpose: Framework-specific badge with icon
Tech: React + Design System Badge extension
Used on: CISO page (hero bar, compliance mapping section)
Props: framework ('soc2' | 'dora' | 'hipaa' | 'euai' | 'iso27001'), size
Icons: Custom outlined shield SVGs per framework (5 total)
```

### 5. JudgmentReceipt

```
Purpose: Render an evidence bundle in structured document format
Tech: React
Used on: CISO page (sample receipt CTA), Dev page (JSON view variant)
Props: data (evidence bundle JSON), variant ('document' | 'json')
```

### 6. FAQAccordion

```
Purpose: Expandable question/answer pairs
Tech: React + @radix-ui/react-accordion
Used on: CISO page
Props: items[{question, answer}], defaultOpen?
Accessibility: Keyboard nav, aria-expanded, prefers-reduced-motion
```

### 7. Toast

```
Purpose: Transient notifications (copy confirmation, form success/error)
Tech: React + @radix-ui/react-toast or custom CSS
Used on: Both pages
Props: message, variant ('success' | 'error' | 'info'), duration
```

### 8. DemoRequestForm

```
Purpose: CISO lead capture form with validation
Tech: React + Design System Input + React Hook Form or inline validation
Used on: CISO page (final CTA section, also in modal via Radix Dialog)
Props: onSubmit, fields (email, company, title)
Validation: email format, required company, optional title
```

### 9. TrialSignupForm

```
Purpose: Developer email capture with minimal friction
Tech: React + Design System Input
Used on: Dev page (final CTA, also inline in pricing section)
Props: onSubmit
Validation: email format only
```

---

## Part 8: Mobile Responsive Spec

### Breakpoints

| Breakpoint | Width      | Behavior                         |
| ---------- | ---------- | -------------------------------- |
| Mobile     | < 768px    | Single column, stacked layout    |
| Tablet     | 768-1023px | 2-column where applicable        |
| Desktop    | >= 1024px  | Full layout per wireframes above |

### Mobile-Specific Rules

**Navigation (both pages):**

- Hamburger menu icon replaces horizontal nav links
- Logo + hamburger left/right aligned
- Menu opens as full-width dropdown (not slide-out)
- Primary CTA button remains visible in nav (not hidden in hamburger)

**Dev page mobile:**

- Code blocks: horizontal scroll with visible scrollbar, 14px font size (not 16px)
- Trust bar: 2x2 grid instead of 4-column horizontal
- Pricing cards: vertically stacked, full-width
- Section padding: 48px max (compress from 64/80)

**CISO page mobile:**

- Compliance badge bar: horizontal scroll or 3+2 wrap (not 5-across)
- Compliance mapping cards: vertically stacked, full-width
- Split layout (Deployment section): stacked -- engineer experience first, CISO experience second
- Pricing cards: vertically stacked, Starter card first with "Most Popular" badge
- FAQ accordion: full-width, touch target minimum 44px height

**Forms (both pages):**

- Input fields: full-width, minimum 44px height (touch target)
- CTA buttons: full-width on mobile
- GDPR checkbox: label text wraps, checkbox stays left-aligned

**Typography scaling:**

- Hero headline: 36-40px on mobile (down from 48-64px)
- H2: 24-28px on mobile (down from 28-36px)
- Body: stays 16px (minimum readable on mobile)

**Images:**

- Dashboard screenshots: full-width with pinch-to-zoom
- Evidence bundle renderer: simplified view on mobile (collapsible sections)

**Page weight:**

- Dev page: < 200KB total (unchanged -- mobile is the constraint)
- CISO page: < 300KB total (dashboard screenshots add weight)
- Lazy-load images below the fold

---

## Part 9: Implementation Priority

Build order optimized for "something live ASAP" per Kristen's timeline:

| Priority | What                           | Time Est | Why First                               |
| -------- | ------------------------------ | -------- | --------------------------------------- |
| P0       | Theme CSS vars (both pages)    | 30 min   | Every component depends on these        |
| P0       | CodeBlock component            | 45 min   | Hero visual for dev page                |
| P0       | PricingCard + PricingToggle    | 1 hr     | Pricing is on both pages                |
| P0       | TrialSignupForm + email API    | 1 hr     | Primary conversion mechanism            |
| P1       | Dev page complete              | 2 hr     | Assemble sections with above components |
| P1       | ComplianceBadge                | 30 min   | Hero bar for CISO page                  |
| P1       | JudgmentReceipt                | 1 hr     | "See a sample receipt" CTA              |
| P1       | DemoRequestForm                | 45 min   | CISO conversion mechanism               |
| P2       | CISO page complete             | 2 hr     | Assemble sections with above components |
| P2       | FAQAccordion                   | 30 min   | CISO-only section                       |
| P2       | Toast                          | 20 min   | Copy confirmation, form feedback        |
| P2       | Mobile responsive (both pages) | 2 hr     | 50%+ of traffic is mobile               |
| P3       | Analytics integration          | 30 min   | Plausible script tag + UTM capture      |
| P3       | SEO meta tags + OG images      | 30 min   | Social sharing, search visibility       |
| P3       | Deploy to Vercel               | 20 min   | Go live                                 |

**Total estimated build time: ~14-16 hours** for both pages, including API routes, mobile, and SEO. Previous estimate of 10-11 hours excluded mobile responsive and SEO work.

---

_This spec is the visual and technical companion to 11-landing-page-content.md (copy)._
_Together, they form a complete, buildable specification for both landing pages._
_Review with Igor before building._
