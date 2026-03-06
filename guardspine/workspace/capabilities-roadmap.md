# AEGIS Relationship & CRM Capability Roadmap

## 1. Reverse Dependency Tree (backward-traced)

**🎯 Target: Strategic Loop Closure**
↑ [AEGIS-OUTREACH] Sends SendRequest
↑ [Human Gate] David approves via Discord/CLI
↑ [AEGIS-OUTREACH] Context Assembly (2 anchors + history)
↑ [AEGIS-CORE] Lead Ledger Promotion (signal qualified)
↑ [AEGIS-CORE] Signal Intake (extracting intent from raw data)
↑ [Inbound/Monitoring] Surface Watchers (Moltbook, GitHub, Web Search)

## 2. Identified Gaps & Bootstrap Strategy

| Gap                         | Capability Required                          | Bootstrap Source                                                |
| :-------------------------- | :------------------------------------------- | :-------------------------------------------------------------- |
| **Identity Resolution**     | Map Moltbook user → GitHub/Personal Data     | Custom `identity-mapper` (using `github` + `searxng` tools)     |
| **Logic: Intent Detection** | Quantify signal confidence (0-100)           | Logic implementation in `aegis-intent-detector.skill`           |
| **Data: Lead Ledger**       | Immutable SQLite storage for leads & signals | `sqlite-mcp` (staged to quarantine) or direct `beads` expansion |
| **Approval Interface**      | Formal "SendRequest" payload for David       | Custom OpenClaw `approval-skill` using `message` target         |

## 3. Sequential Action Plan

1. **[AEGIS-CORE] Ledger Design**: Initialize `~/.openclaw/ledger/aegis_crm.db` with schema for: `leads`, `signals`, `outreach_history`.
2. **[AEGIS-CORE] Import Identity Tools**: Research and Stage the **GitHub MCP Server** to quarantine for inventorying personal data of leads.
3. **[AEGIS-CORE] Build Intent Skill**: Use `skill-creator` to package `aegis-intent-detector`. This skill will analyze Moltbook posts found during heartbeats and flag them as "Qualified Leads" in the Ledger.
4. **[AEGIS-OUTREACH] SendRequest Standard**: Define the markdown template for approval requests in `#dropbox`.

## 4. First Research Mission (Gaps Only)

- [ ] Audit the **GitHub MCP Server** for identity resolution.
- [ ] Investigate **n8n OpenClaw nodes** for potential automated ingest from external webhooks.
- [ ] Verify if David's **Obsidian Vault** has identifying context for old real estate/consulting contacts to seed the ledger.
