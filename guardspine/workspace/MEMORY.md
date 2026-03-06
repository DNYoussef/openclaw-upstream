# MEMORY.md - Long-Term Memory

**SECURITY: Only load in main session (direct chats with David). Do NOT load in shared contexts.**

## System Architecture (Updated 2026-03-05)

- Running OpenClaw v2026.3.2 on Windows (rebased to upstream with 40+ security patches)
- Primary model: Kimi K2 via OpenRouter (openrouter/moonshotai/kimi-k2)
- Escalation model: Claude Opus 4.5 via OpenRouter (after 2 failures, 5-min window)
- Fallback models: 3 Ollama models on localhost:11434 (qwen3-coder:30b, gpt-oss:20b, qwen3:8b) stored at D:\ollama
- GuardSpine governance plugin: mode=enforce, 4 hooks + 4 tools, L0-L4 risk tiers
- Memory MCP triple-layer: ChromaDB (vector) + NetworkX (graph) + pgmpy (bayesian)
- Sequential Thinking MCP: reasoning chain tool
- SearXNG search plugin: web_search tool
- RLM-docsync plugin: rlm_read, rlm_security_audit, rlm_introspect
- Local AI models: Whisper (STT), SDXL 1.0 (image gen), yt-dlp (audio extraction)
- GPU: NVIDIA GeForce RTX 4060 Ti (15.99 GB VRAM, CUDA 12.7, driver 566.36)
- Gateway: WebSocket on port 18789, loopback only, token auth
- Railway deployment: guardspine-ai-ops (OpenClaw + LiteLLM + n8n)
- LiteLLM budget: $10/day
- Council signing: GUARDSPINE_COUNCIL_KEY set, GUARDSPINE_REQUIRE_COUNCIL_KEY=1

## Railway Services

| Service  | Internal URL                    | Status  |
| -------- | ------------------------------- | ------- |
| OpenClaw | openclaw.railway.internal:18789 | Running |
| LiteLLM  | litellm.railway.internal:4000   | Running |
| n8n      | n8n.railway.internal:5678       | Running |

## Installed OpenClaw Extensions

7 extensions loaded at gateway startup:

| Extension           | Priority | Hooks                                                            | Tools                                                                                                                                                              |
| ------------------- | -------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| guardspine          | -500     | before_tool_call, before_agent_start, after_tool_call, agent_end | guardspine_status, guardspine_audit_log, guardspine_approve, memory_status                                                                                         |
| n8n-pipeline        | 10       | before_agent_start                                               | n8n_list_workflows, n8n_get_workflow, n8n_create_workflow, n8n_update_workflow, n8n_activate_workflow, n8n_execute_workflow, n8n_get_executions, n8n_get_execution |
| rlm-docsync         | -200     | before_tool_call                                                 | rlm_read, rlm_security_audit, rlm_introspect                                                                                                                       |
| sequential-thinking | DISABLED | --                                                               | --                                                                                                                                                                 |
| searxng-search      | --       | --                                                               | web_search                                                                                                                                                         |
| local-ai-models     | --       | --                                                               | model_status, download_youtube, transcribe_audio, generate_image                                                                                                   |

Hook execution order (lower priority number = runs first):
guardspine (-500) -> rlm-docsync (-200) -> default (0)

## Security Audit Status (2026-03-05)

Major audit completed. 11 Critical, 14 High, 9 Medium findings.

- All 5 Critical findings FIXED (C1-C5)
- 6 High findings FIXED/RESOLVED (H2, H3, H6, H9, H10, M8)
- 5 Medium findings FIXED (M1, M2, M3, M7, M9)
- Remaining: H1 (Gmail gating), H4 (internal TLS), H5 (Memory MCP auth), H7 (SQLCipher), H8 (namespace segmentation)
- New: Quarantine scanner system (prompt injection + static analysis + scan_runner)

## Council Configuration

- CodeForge: qwen3-coder:30b (weight 0.40, primary lead)
- ReasonForge: gpt-oss:20b (weight 0.35, adversarial verification)
- SentinelForge: qwen3:8b (weight 0.25, fast reasoning, fallback)
- All models: reasoning=false (Ollama does not support the think parameter)
- Council runs sequentially (VRAM constraint) with unload between models

## Known Issues

- Ollama qwen3:8b does NOT support the `think` parameter. Keep reasoning:false.
- Discord groupPolicy must be "open" for the bot to respond in servers.
- OpenClaw `--force` flag requires `lsof` which doesn't exist on Windows. Kill node processes manually.
- OpenClaw cron fails on Railway (EACCES on /data/.openclaw volume). Non-blocking for MVP.
- openclaw.json config validation warns about guardspine config keys but plugin loads fine (cosmetic).
- L4 approval is non-blocking: action blocked immediately, user approves, then retried.

## Key Paths

| Component            | Path                                                 |
| -------------------- | ---------------------------------------------------- |
| OpenClaw config      | C:\Users\17175\.openclaw\openclaw.json               |
| Workspace            | C:\Users\17175\.openclaw\workspace\                  |
| Extensions           | C:\Users\17175\.openclaw\extensions\                 |
| GuardSpine logs      | C:\Users\17175\.openclaw\guardspine-logs\            |
| GuardSpine dev_inbox | C:\Users\17175\.openclaw\guardspine-logs\dev_inbox\  |
| Memory MCP data      | C:\Users\17175\.claude\memory-mcp-data\              |
| Outreach DB          | C:\Users\17175\.claude\outreach\outreach.db          |
| Landing page DB      | D:\Projects\guardspine-landing\data\guardspine.db    |
| Gateway restart      | C:\Users\17175\.openclaw\restart-gateway.ps1         |
| GuardSpine plugin    | D:\Projects\guardspine-openclaw\                     |
| GuardSpine monorepo  | D:\Projects\GuardSpine\                              |
| Memory MCP repo      | D:\Projects\memory-mcp-triple-system\                |
| OpenClaw upstream    | D:\Projects\openclaw-upstream\                       |
| OpenClaw hardening   | D:\Projects\openclaw-hardening\                      |
| n8n nodes            | D:\Projects\n8n-nodes-guardspine\                    |
| DB backups           | C:\Users\17175\.claude\backups\db\                   |

## Decisions Log

- 2026-01-31: Set all models reasoning:false to avoid Ollama 400 errors
- 2026-01-31: Workspace files populated with full infrastructure awareness
- 2026-01-31: Fixed L4 approval from blocking 5-min poll to non-blocking immediate-abort
- 2026-02-01: Built Beads task management extension (4 tools)
- 2026-02-01: Switched GuardSpine from audit mode to enforce mode
- 2026-02-03: GuardSpine V2.1 upgrade - L3.5 Opus tie-breaker, pattern authorization, memory_status
- 2026-02-03: Added reaction-based L4 approval
- 2026-02-25: Cleaned 48 -> 31 projects in D:\Projects
- 2026-02-25: Deleted AI Exoskeleton workspace (Beads DB moved)
- 2026-02-28: Deployed Railway project guardspine-ai-ops (OpenClaw + LiteLLM + n8n)
- 2026-03-05: Security audit: 11C/14H/9M findings. All critical fixed.
- 2026-03-05: OpenClaw rebased to v2026.3.2 (ClawJacked + 40 patches)
- 2026-03-05: Set GUARDSPINE_COUNCIL_KEY + GUARDSPINE_REQUIRE_COUNCIL_KEY=1
- 2026-03-05: Built quarantine scanner system (prompt injection + static analysis)
- 2026-03-05: GuardSpineTrigger webhook now requires HMAC signature verification
- 2026-03-05: Created SQLite backup script (3 DBs, 14-day retention)
- 2026-03-05: Workspace docs major rewrite (IDENTITY, TOOLS, USER, MEMORY, BUSINESS)
- 2026-03-05: Built n8n-pipeline extension (8 tools for AI-driven workflow management)
- 2026-03-05: Added n8n tools to GuardSpine RISK_RULES (L1 reads, L2 writes)
- 2026-03-05: Miessler "Great Transition" analysis: 12 transitions, 10 gaps, 5 compound insights
- 2026-03-05: Applied ideal state management pattern across all workspace docs
- 2026-03-05: Reframed positioning: "code governance" -> "continuous verification infrastructure"
- 2026-03-05: Added The Algorithm axiom to SOUL.md (ideal state + verification criteria)
- 2026-03-05: HEARTBEAT.md now includes daily ideal state gap report (14 dimensions)
