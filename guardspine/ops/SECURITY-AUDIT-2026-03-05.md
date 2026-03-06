# GuardSpine AI-Native Infrastructure Security Audit

# Date: 2026-03-05 | Auditor: Claude Opus 4.6 (4 parallel agents)

## EXECUTIVE SUMMARY

5-layer AI agent infrastructure audited across 4 parallel investigations:
OpenClaw connection surfaces, existing hardening code, Railway/n8n attack
surface, and full STRIDE threat model. 410K+ tokens of analysis.

**Bottom line: 11 Critical findings, 14 High, 9 Medium. The system is NOT
safe to run autonomous agents until the 5 Critical-immediate items are fixed.**

---

## CRITICAL FINDINGS (fix before ANY agent runs)

### C1: OpenClaw 4 weeks behind on security patches

- **Current**: v2026.1.30. **Upstream**: v2026.3.2
- Missing: ClawJacked WebSocket hijack fix (v2026.2.25)
- Missing: 40+ vulnerability patches (v2026.2.12)
- Missing: HSTS + session hardening (v2026.2.23)
- Missing: Gateway vulnerability fix (v2026.2.26)
- **Action**: Merge upstream to v2026.3.2, rebuild Railway image

### C2: OpenClaw runs --allow-unconfigured on public Railway URL

- OpenClaw docs explicitly say: "Never expose Gateway unauthenticated on 0.0.0.0"
- Our deployment violates this: public URL, LAN binding, no auth enforced
- **Action**: Remove --allow-unconfigured, add gateway token auth

### C3: n8n JWT hardcoded in plaintext .mcp.json

- Full JWT visible in config file, no expiry claim
- Grants complete n8n MCP server access (workflow CRUD, code execution)
- **Action**: Rotate JWT, move to env var, add expiry

### C4: Dev council signing key "guardspine-dev-council-key" in production

- Hardcoded fallback in approval_gate.py:33-57
- Anyone knowing this string can forge HMAC-signed council results
- Bypasses ALL L3+ governance gates
- **Action**: Set GUARDSPINE_COUNCIL_KEY env var, set GUARDSPINE_REQUIRE_COUNCIL_KEY=1

### C5: Discord L4 approval accepts any reactor

- Emoji reaction approval has no identity binding
- Anyone in the Discord channel can approve L4 actions
- **Action**: Switch to guardspine_approve tool (identity-bound), not reactions

---

## HIGH FINDINGS

### H1: Gmail MCP has no secondary auth

- Any agent can send emails to 175+ real prospect email addresses
- No GuardSpine gating on send_email
- **Action**: Gate email sends at L2+ with evidence pack

### H2: Response signature verification is OPTIONAL (approval_gate.py:373)

- Attacker can supply L4 response without signature and it passes
- **Action**: Make signature mandatory on all L4 responses

### H3: Allowlist bypass via substring matching (plugin.js:226)

- paramsStr.includes(pattern.param_match) is too loose
- Attacker can craft params containing approved substrings
- **Action**: Switch to exact key/value matching

### H4: Railway inter-service traffic is unencrypted HTTP

- OpenClaw -> LiteLLM -> OpenRouter: internal network, no TLS
- API keys sent in Authorization headers in plaintext
- **Action**: Enable Railway internal TLS or add HMAC request signing

### H5: Memory MCP HTTP server has no authentication

- If deployed to Railway, any request accepted (CORS allows localhost only now)
- No Bearer token, no rate limiting
- **Action**: Add auth middleware before Railway deployment

### H6: n8n GuardSpineTrigger webhook has no authentication

- Anyone can POST forged events to /webhook/guardspine-event
- No HMAC signature, no bearer token, no IP whitelist
- **Action**: Add HMAC signature verification

### H7: PII in outreach.db unencrypted

- 359 prospects: names, emails, LinkedIn URLs, companies, titles, research notes
- Plain SQLite, no encryption at rest, no access controls
- **Action**: SQLCipher or column-level encryption

### H8: Memory MCP has no access segmentation

- All agents share one memory store
- Outreach agent can retrieve lawsuit details, trading strategies
- **Action**: Add namespace/tenant tagging per domain

### H9: LiteLLM API key baked into Docker config

- railway-config.json uses env var substitution but key visible in image layers
- **Action**: Load at runtime only, never bake into config

### H10: Elevated mode bypasses tool approvals

- If elevatedMode="full", agent runs commands with NO approval check
- **Action**: Set to "ask" or "off" in production

---

## MEDIUM FINDINGS

### M1: Race condition in nonce replay detection (approval_gate.py:202-216)

- No threading lock on \_used_nonces check-then-act
- **Action**: Add threading.Lock

### M2: Missing input validation on evidence pack metrics (approval_gate.py:278)

- rubric_score not type-checked, negative failed counts accepted
- **Action**: Add isinstance checks and bounds validation

### M3: File permissions world-readable on sensitive files

- Nonce store, quarantine manifests, evidence packs at default umask
- **Action**: chmod 0o600 on sensitive files

### M4: Token in query string accepted by webhook system

- Tokens in URLs logged in proxies, browser history, referrer headers
- **Action**: Accept tokens in headers only

### M5: Obsidian sync path traversal risk

- vault_path parameter not validated against whitelist
- **Action**: Whitelist allowed vault paths

### M6: No monitoring or alerting

- No uptime monitoring, no error tracking, no budget alerts
- **Action**: Deploy external monitoring

### M7: No automated backup of SQLite databases

- outreach.db, crm.db, agent_kv.db have no backup
- **Action**: Daily backup to cloud storage

### M8: GuardSpine plugin may be in "audit" mode not "enforce"

- In audit mode, actions execute without governance
- **Action**: Verify and switch to enforce mode

### M9: Dashboard PIN "2026" hardcoded in SKILL.md

- **Action**: Move to env var

---

## EXISTING SECURITY CONTROLS (what we have)

### Strong (keep and extend)

- L0-L4 risk tier classification (guardspine_policy.yaml)
- SHA-256 hash-chained evidence packs (chain.py)
- 3-model council with HMAC signing (council_runner.py)
- Guarded exec/write/download wrappers (guarded\_\*.py)
- Quarantine system with source validation (quarantine_manager.py)
- Frozen paths enforcement (safe_path.py)
- Red team harness with 310+ attacks (redteam/)
- OpenClaw plugin hooks for tool gating (plugin.js)
- Shell injection prevention (blocks ;, &&, ||, backticks, $())
- Command allowlist + blocklist
- Rate limiting on L4 requests (5/hour)
- L3.5 Opus tie-breaker for council deadlocks
- Dual L4 approval channels (Discord + file fallback)

### Needs hardening

- Quarantine: has intake/promote but no content scanning
- Council key: needs production key, not fallback
- Evidence packs: need PII scrubbing
- Approval flow: needs mandatory response signatures
- Allowlist: needs exact matching, not substring

---

## SOC 2 TRUST SERVICE CRITERIA GAP ANALYSIS

### Security (CC6: Logical Access)

- EXISTS: L0-L4 tiers, evidence packs, council reviews
- MISSING: MFA on services, RBAC for agents, secrets manager, key rotation

### Availability (A1)

- EXISTS: Railway deployment, Docker containers
- MISSING: Uptime monitoring, backup/recovery, incident response plan

### Processing Integrity (PI1)

- EXISTS: Hash chains, slop audit, swap test
- MISSING: Hash chains on activity_log, input validation on DB mutations

### Confidentiality (C1)

- EXISTS: L0-L4 classification for actions
- MISSING: Encryption at rest, PII scrubbing in evidence packs, data classification policy

### Privacy (P1)

- EXISTS: red signal = do-not-contact
- MISSING: CAN-SPAM unsubscribe, GDPR DSAR process, privacy notice, consent management

---

## QUARANTINE + AGENT SANDBOX ARCHITECTURE

### Existing quarantine system (openclaw-hardening/quarantine/)

- Source validation (pypi, npm, github, huggingface only)
- Extension blocking (.exe, .dll, .bat, .ps1, etc.)
- UUID-prefixed filenames prevent collisions
- Council-gated promotion (min score 4.0/5.0, signed verdict)
- Auto-purge after 7 days
- Manifest tracking with metadata

### What needs to be ADDED for agent sandbox

```
Agent wants to download/create/test something
    |
    v
+------------------------+
| QUARANTINE INTAKE      |  <-- EXISTS: quarantine_manager.receive()
| incoming/              |
+--------+---------------+
         |
    +----+----+----+----+
    |              |         |
    v              v         v
+----------+  +----------+  +----------+
| Static   |  | Prompt   |  | AI Deep  |
| Analysis |  | Injection|  | Review   |
| (semgrep,|  | Scanner  |  | (Opus    |
| bandit,  |  | (regex + |  | 4.6 via  |
| eslint)  |  | pattern) |  | LiteLLM) |
+----+-----+  +----+-----+  +----+-----+
     |              |              |
     v              v              v
+-----------------------------------+
| SCANNER RESULTS AGGREGATION       |
| All 3 must pass. Any fail = block |
+--------+--------------------------+
         |
         v
+------------------------+
| COUNCIL VOTE           |  <-- EXISTS: council_runner.py
| 3-model review of      |
| scanner results +      |
| original content       |
+--------+---------------+
         |
    pass? ---- no ----> REJECT + alert + quarantine retain
         |
        yes
         |
         v
+------------------------+
| PROMOTION              |  <-- EXISTS: quarantine_manager.promote()
| to active skills/      |
| pipelines/tools        |
| (frozen path check)    |
+------------------------+
```

### Scanner specifications

1. STATIC ANALYSIS (deterministic, no tokens)
   - Python: bandit (security), semgrep (patterns), ast-based checks
   - JavaScript: eslint-plugin-security, semgrep
   - YAML/JSON: schema validation, no eval() in templates
   - Shell: shellcheck
   - Exit criteria: 0 high/critical findings

2. PROMPT INJECTION SCANNER (deterministic, no tokens)
   - Regex patterns for known injection techniques:
     - "ignore previous instructions"
     - "you are now", "new persona", "roleplay as"
     - Base64-encoded instructions
     - Unicode homoglyph substitution
     - Markdown/HTML injection
   - SKILL.md structure validation (valid YAML frontmatter, no script tags)
   - System prompt extraction attempts
   - Exit criteria: 0 pattern matches

3. AI DEEP REVIEW (separate Opus 4.6 instance, budget-capped)
   - Reviews code for: backdoors, data exfiltration, credential harvesting
   - Reviews prompts for: hidden instructions, persona manipulation
   - Reviews n8n flows for: dangerous nodes, external calls, infinite loops
   - Budget: max $0.50 per review (tracked via LiteLLM daily spend)
   - Exit criteria: explicit PASS verdict with reasoning

### Sandbox directory structure

```
~/.openclaw/sandbox/
  incoming/          # Raw downloads land here (UUID-prefixed)
  scanning/          # Currently being scanned (locked)
  approved/          # Passed all gates, ready for promotion
  rejected/          # Failed, retained for forensics
  experiments/       # Agent testing area (isolated, no prod access)
    agent-{id}/      # Per-agent workspace
      tools/         # Tools being tested
      skills/        # Skills being evaluated
      pipelines/     # n8n pipeline drafts
      results/       # Test outputs
  manifests/         # Scan results + council verdicts
```

---

## PRIORITY REMEDIATION SEQUENCE

### Phase 0: Emergency (do NOW, before anything else)

1. Merge OpenClaw upstream to v2026.3.2
2. Remove --allow-unconfigured from Railway
3. Set GUARDSPINE_COUNCIL_KEY production key
4. Rotate n8n JWT, move to env var
5. Set LiteLLM cost ceiling ($10/day)

### Phase 1: Before outreach pipeline (Week 1)

6. Gate Gmail sends at L2+ with evidence pack
7. Make L4 response signature mandatory
8. Fix allowlist substring matching
9. Add HMAC to n8n webhook triggers
10. Encrypt outreach.db (SQLCipher or column-level)

### Phase 2: Before autonomous agents (Week 2)

11. Build quarantine scanners (static + prompt injection)
12. Deploy sandbox directory structure
13. Add Memory MCP auth + namespace segmentation
14. Switch GuardSpine plugin to enforce mode
15. Add monitoring/alerting

### Phase 3: Before pilot customers (Month 1)

16. Railway internal TLS or HMAC signing
17. PII scrubbing in evidence packs
18. CAN-SPAM compliance (unsubscribe links)
19. Automated DB backups
20. Red team harness in CI

### Phase 4: Before SOC 2 (Month 3)

21. Formal security policy document
22. Change management process
23. Incident response plan
24. Data classification policy
25. Annual penetration test
26. DSAR handling process

---

## SOURCES

- Dark Reading: Critical OpenClaw Vulnerability
- Hacker News: ClawJacked Flaw
- Reco.ai: OpenClaw Security Crisis
- PYMNTS: OpenClaw Patch
- Cisco Blog: AI Agent Security Nightmare
- Kaspersky: OpenClaw Vulnerabilities
- Security Boulevard: OpenClaw Attack Surface Analysis
- Oasis Security: ClawJacked Vulnerability Details
