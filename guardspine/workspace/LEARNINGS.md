# LEARNINGS.md - Patterns Discovered & Mistakes Not to Repeat

## Format: [DATE] CATEGORY: Learning

### Architecture

- [2026-03-05] SECURITY: Always run quarantine scan BEFORE council review, not after. Council is expensive (30-120s). Cheap deterministic scan first eliminates obvious bad inputs.
- [2026-03-05] SECURITY: HMAC nonce replay detection needs threading lock. Check-then-act on a set is a TOCTOU race.
- [2026-03-05] SECURITY: Substring matching for allowlists is exploitable. Always use exact key/value or recursive prefix matching.
- [2026-03-05] IMPORTS: Relative imports (.module) for intra-package, absolute (package.module) for cross-package. Mixing causes circular import failures depending on invocation path.
- [2026-03-05] WINDOWS: chmod 0o600 may silently fail. Always wrap in try/except OSError.

### Prompting

- [2026-03-05] DRIFT: Workspace files drift when updated independently. Facts (version numbers, team roster, repo counts) must have ONE canonical source. Other files reference it.
- [2026-03-05] CONTEXT: Loading all 8+ workspace files into every call wastes tokens. Load SOUL + TOOLS always, others on demand.

### Operations

- [2026-03-05] BACKUP: sqlite3 .backup command is hot-safe. cp is not. Always prefer .backup for live databases.
- [2026-03-05] RAILWAY: Volumes mount as root:root. Non-root containers cannot write. Fix with custom entrypoint that chowns then drops privileges.
- [2026-03-05] RAILWAY: MSYS_NO_PATHCONV=1 required for ALL Railway CLI commands with Unix-style paths on Windows Git Bash.

### Business

- [2026-03-05] OUTREACH: Prospect emails go stale when people change companies. Cross-check send target against DB before logging.
- [2026-03-05] OUTREACH: channel='bounced' is not permanent exclusion. If valid email found and message sent, reset to channel='email'.

### Strategic (Miessler "Great Transition" analysis, 2026-03-05)

- [2026-03-05] POSITIONING: GuardSpine's moat is NOT knowledge (that gets commoditized via skills). It's OPERATIONAL INFRASTRUCTURE + EVIDENCE TRAILS. Anyone can know what to check. The value is continuous verification with tamper-evident proof.
- [2026-03-05] MESSAGING: Karpathy insight -- "Previous software: make anything. Next software: verify anything." GuardSpine IS verification infrastructure. Use this in every pitch.
- [2026-03-05] MESSAGING: "CFOs want zero employees AND zero software costs. They CANNOT have zero governance. Governance is the last thing you cut." This is the core sales argument.
- [2026-03-05] MESSAGING: Custom software audit problem -- AI-generated code has no vendor, no CVE database, no security patches. GuardSpine fills that vacuum.
- [2026-03-05] GTM: Agent-first distribution matters more than human-facing marketing. MCP server, GitHub Marketplace, npm package > Google Ads, SEO blogs, webinar funnels.
- [2026-03-05] PRICING: Seat-based pricing fights the transition. Node/workflow/evidence-based pricing rides it. Explore before locking in with first enterprise customers.
- [2026-03-05] RISK: If companies build operation graphs (Miessler's lattice), and we bet only on n8n, we're locked to one substrate. Keep evidence pack format substrate-agnostic.
- [2026-03-05] RISK: Governance knowledge will be commoditized (free skills). Defense: infrastructure beats knowledge. You can't replace a running system with a markdown file.
- [2026-03-05] VISION: We're not "security software." We're the governance substrate the enterprise operation graph runs on. Today: code. Tomorrow: everything.
