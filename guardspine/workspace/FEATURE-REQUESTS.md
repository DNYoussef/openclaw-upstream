# FEATURE-REQUESTS.md - Ideas for Future Implementation

## Format: [PRIORITY] CATEGORY: Idea (source)

### P0 - Implement Next

- [ ] CRON: Nightly security council (automated scan of file permissions, gateway config, secrets) (video: Burman)
- [ ] LOGGING: Unified event log (every LLM call, tool call, error, cron result in one JSONL + DB) (video: Burman)
- [ ] MORNING: Self-heal routine (read overnight error log, fix what's fixable, escalate rest) (video: Burman)
- [ ] NOTIFY: Notification batching (critical=immediate, high=hourly, medium=3hr) (video: Burman)
- [ ] MESSAGING: Add Karpathy verification line + custom software audit argument to all pitch materials (video: Miessler "Great Transition")
- [ ] IDEAL-STATE: Create explicit ideal-state document for GuardSpine company operations -- dimensions, current state, gaps, actions (video: Miessler)

### P1 - High Value

- [ ] CRM: Cross-pollinate outreach DB with knowledge base (articles about prospects' companies auto-linked) (video: Burman)
- [ ] RUBRIC: Editable inbound email scoring rubric with feedback loop (video: Burman)
- [ ] METRICS: LLM usage/cost tracking dashboard with per-caller breakdown (video: Burman)
- [ ] DRIFT: Nightly prompt drift detection across workspace files (video: Burman)
- [ ] BACKUP: Encrypted DB backup to Google Drive/cloud (we have local backup, need cloud) (video: Burman)
- [ ] MCP-SERVER: Standalone GuardSpine MCP server (npm package, no OpenClaw dependency). Agent-first distribution channel. `npx guardspine-mcp` (video: Miessler -- products become APIs/MCPs)
- [ ] GOV-SCORE: Governance Score concept -- single 0-100 number from evidence data (coverage, severity, response time, false positive rate). Badge for READMEs. Signal for insurers/auditors/investors (video: Miessler -- function-node metrics)
- [ ] COMPLIANCE-MAP: Compliance matrix mapping GuardSpine features to SOC2/HIPAA/PCI-DSS/ISO27001 requirements. Sales enablement doc (video: Miessler -- who governs the AI?)

### P2 - Nice to Have

- [ ] DUAL-STACK: Model-specific prompt versions (Claude vs GPT/Codex) with nightly sync (video: Burman)
- [ ] KNOWLEDGE: Article/web ingestion pipeline (save link -> sanitize -> chunk -> embed -> cross-reference) (video: Burman)
- [ ] MEETING: Fathom/Otter transcript ingestion -> action items -> CRM/task tracker (video: Burman)
- [ ] CONTENT: Video idea pipeline from Slack/Discord threads -> outline + packaging (video: Burman)
- [ ] FINANCIAL: QuickBooks CSV import -> natural language financial queries (video: Burman)
- [ ] HEALTH: Wearable data ingestion (Oura/Apple Health) -> daily summary + coaching (video: Burman)
- [ ] VOICE: Two-way synchronous voice conversation with OpenClaw (video: Burman)
- [ ] IDENTITY: Dedicated Gmail account for OpenClaw (Digital David) as full employee (video: Burman)
- [ ] NODE-PRICING: Explore node/workflow/evidence-based pricing instead of seat-based. Aligns with graph-of-algorithms model (video: Miessler -- function-node metrics)
- [ ] SKILL-MARKETPLACE: Prepare 3-5 governance skills for public skill marketplace when one emerges (video: Miessler -- knowledge goes public)
- [ ] AGENT-DOCS: Machine-readable API specs (OpenAPI/MCP tool descriptions) optimized for agent discovery (video: Miessler -- SEO targets AI not humans)

### P3 - Research

- [ ] AGENTS-SDK: Convert to Anthropic Agents SDK for subscription-based usage (video: Burman)
- [ ] LOCAL-EMBED: Switch to Nomic embeddings on-device for zero-cost vectorization (video: Burman)
- [ ] INNOVATION-SCOUT: Nightly council that searches web for new use cases and competitor news (video: Burman)
- [ ] GOV-MATURITY: Governance maturity dashboard showing customers their journey from current to ideal state (Level 1-5) (video: Miessler -- ideal state management)
- [ ] EVIDENCE-GENERALIZE: Extend evidence bundle format beyond code to financial transactions, hiring decisions, customer support. Generic operation verification (video: Miessler -- graph of algorithms)
- [ ] RED-TEAM-GOV: Systematic adversarial testing of governance system itself. Can council be tricked? Can evidence packs be forged? (video: Miessler -- attacker world models)
