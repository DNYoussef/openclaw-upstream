# TOOLS.md - Your Infrastructure & Tool Awareness

## Active Plugins (Updated 2026-03-05)

| Plugin                  | Tools                                                                                                                                                              | Purpose                                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| **guardspine**          | guardspine_status, guardspine_audit_log, guardspine_approve, memory_status + 4 hooks                                                                               | Governance/enforcement (council: qwen3:8b, qwen3-coder:30b, gpt-oss:20b) + L3.5 Opus tie-breaker + Pattern Authorization |
| **n8n-pipeline**        | n8n_list_workflows, n8n_get_workflow, n8n_create_workflow, n8n_update_workflow, n8n_activate_workflow, n8n_execute_workflow, n8n_get_executions, n8n_get_execution | Create, execute, and monitor n8n workflows via REST API                                                                  |
| **local-ai-toolkit**    | model_status, check_model_fit, download_youtube, transcribe_audio, generate_image                                                                                  | Local AI utilities                                                                                                       |
| **rlm-docsync**         | rlm_read, rlm_security_audit, rlm_introspect                                                                                                                       | Large-context reading                                                                                                    |
| **sequential-thinking** | sequential_think                                                                                                                                                   | Multi-step reasoning chains                                                                                              |
| **searxng-search**      | web_search                                                                                                                                                         | Web search via SearXNG                                                                                                   |

---

## Available Models (Updated 2026-03-05)

### OpenRouter (Cloud)

| Model ID                             | Role                 | Context | Reasoning | Cost               |
| ------------------------------------ | -------------------- | ------- | --------- | ------------------ |
| `moonshotai/kimi-k2`                 | **Brain (Primary)**  | 131K    | Yes       | $0.15/$0.60 per 1M |
| `google/gemini-3-flash-preview`      | Vision/Budget        | 1M      | No        | $0.10/$0.40 per 1M |
| `anthropic/claude-4-5-haiku`         | Heartbeat (Cheap)    | 200K    | No        | $0.25/$1.25 per 1M |
| `anthropic/claude-opus-4-5-20250514` | Escalation (Premium) | 200K    | Yes       | $15/$75 per 1M     |
| `deepseek/deepseek-v3.2`             | Web/Browser (Budget) | 163K    | No        | $0.25/$0.38 per 1M |

### LiteLLM (Railway - Unified Proxy)

All models also available via LiteLLM at litellm.railway.internal:4000 with budget controls ($10/day).

| LiteLLM Alias         | Upstream Model    |
| --------------------- | ----------------- |
| litellm/claude-sonnet | Claude Sonnet 4.5 |
| litellm/claude-opus   | Claude Opus 4.5   |
| litellm/claude-haiku  | Claude Haiku 4.5  |
| litellm/gpt-4o        | GPT-4o            |
| litellm/gemini-pro    | Gemini Pro        |
| litellm/deepseek-chat | DeepSeek V3       |

### Ollama (Local - Free)

| Model ID          | Role                    | Context |
| ----------------- | ----------------------- | ------- |
| `qwen3-coder:30b` | CodeForge Lead          | 256K    |
| `gpt-oss:20b`     | ReasonForge Adversarial | 131K    |
| `qwen3:8b`        | SentinelForge Fallback  | 32K     |

### Model Routing

- **Default Primary:** `openrouter/moonshotai/kimi-k2` (131K context, reasoning)
- **Fallbacks:** `openrouter/anthropic/claude-opus-4-5-20250514`
- **Retry Escalation:** After 2 failures, escalates to Claude Opus 4.5 for 5 minutes
- **Railway:** LiteLLM proxies all cloud models with unified API + budget caps

---

## Input Streams (What Feeds You)

| Stream               | Source                                            | How to Access                 | Frequency     |
| -------------------- | ------------------------------------------------- | ----------------------------- | ------------- |
| Outreach DB          | ~/.claude/outreach/outreach.db                    | SQLite queries via bash       | On demand     |
| Landing page signups | D:/Projects/guardspine-landing/data/guardspine.db | SQLite queries                | Check daily   |
| GitHub notifications | DNYoussef repos                                   | `gh` CLI                      | Heartbeat     |
| n8n webhooks         | n8n-production-32ffd.up.railway.app               | GuardSpineTrigger node        | Event-driven  |
| Discord messages     | GuardSpine server                                 | Discord bot                   | Real-time     |
| Memory MCP           | ~/.claude/memory-mcp-data/                        | memory_search, unified_search | Every session |
| Codebase changes     | D:/Projects/\*                                    | git log, rlm_read             | On demand     |

## Output Channels

| Channel               | Tool/Method                 | Gate Level                           |
| --------------------- | --------------------------- | ------------------------------------ |
| File writes           | apply_patch, canvas_write   | L2                                   |
| Git commits           | bash (git)                  | L2                                   |
| Email (Gmail)         | Gmail MCP (via Claude Code) | L2+ (H1 audit finding: needs gating) |
| Discord messages      | send_message                | L2                                   |
| n8n workflow triggers | HTTP POST to webhook        | L2                                   |
| Outreach emails       | outreach_pipeline.py        | Human-supervised                     |
| Dashboard updates     | npm run dashboard:update    | L1                                   |

---

## n8n Workflow Engine

n8n is the automation backbone. Railway URL: n8n-production-32ffd.up.railway.app

### Available n8n Nodes (14 GuardSpine types)

| Node                    | Purpose                                                |
| ----------------------- | ------------------------------------------------------ |
| GuardSpineTrigger       | Receive webhook events (risk alerts, approvals, scans) |
| CodeGuard               | Run code governance checks                             |
| CouncilVote             | Trigger 3-model council review                         |
| EvidenceSeal            | Seal and sign evidence bundles                         |
| GuardGate               | Route actions by risk tier                             |
| ApprovalWait            | Wait for human approval                                |
| BundleImport            | Import evidence bundles                                |
| BeadsCreate/List/Update | Task management                                        |
| GuardSpineCompress      | Compress evidence for storage                          |
| GuardSpineImageGuard    | Image content governance                               |
| GuardSpinePDFGuard      | PDF content governance                                 |
| GuardSpineSheetGuard    | Spreadsheet governance                                 |

### n8n Pipeline Management (Your Automation Hands)

You can create and manage n8n workflows directly using the n8n-pipeline extension:

| Tool                  | Purpose                                              | Tier |
| --------------------- | ---------------------------------------------------- | ---- |
| n8n_list_workflows    | List all workflows (name, active, tags)              | L1   |
| n8n_get_workflow      | Get full workflow definition (nodes, connections)    | L1   |
| n8n_create_workflow   | Create a new workflow from a spec                    | L2   |
| n8n_update_workflow   | Modify an existing workflow (nodes, connections)     | L2   |
| n8n_activate_workflow | Activate or deactivate a workflow                    | L2   |
| n8n_execute_workflow  | Trigger a workflow execution with input data         | L2   |
| n8n_get_executions    | List recent executions (filter by status/workflow)   | L1   |
| n8n_get_execution     | Get execution details (node results, errors, timing) | L1   |

**Pattern:** You design the pipeline spec (see PATTERNS.md P1-P12), then use n8n_create_workflow to build it. n8n handles 95% deterministic work. You monitor via n8n_get_executions and handle edge cases when n8n routes them back to you via webhook.

### n8n Integration Pattern

OpenClaw fires events -> n8n GuardSpineTrigger receives -> workflow routes by event_type -> actions (Slack alerts, email, DB updates, escalations).

---

## Codebase Read Access (Proprioception)

You can read ANY repo directly using rlm_read. This is your code awareness layer.

### Key Repos to Inspect

| Repo                    | Path                                 | What You Learn                               |
| ----------------------- | ------------------------------------ | -------------------------------------------- |
| **Your own plugin**     | D:\Projects\guardspine-openclaw      | How your governance hooks work               |
| **OpenClaw core**       | D:\Projects\openclaw-upstream        | Gateway, plugin system, model routing        |
| **OpenClaw hardening**  | D:\Projects\openclaw-hardening       | Quarantine scanners, approval gate, security |
| **GuardSpine monorepo** | D:\Projects\GuardSpine               | Backend API, rubrics, CLI                    |
| **n8n nodes**           | D:\Projects\n8n-nodes-guardspine     | Workflow node implementations                |
| **Kernel (TS)**         | D:\Projects\guardspine-kernel        | Bundle sealing/verification                  |
| **Kernel (Python)**     | D:\Projects\guardspine-kernel-py     | Python verification engine                   |
| **Memory MCP**          | D:\Projects\memory-mcp-triple-system | Your hippocampus source code                 |
| **Landing page**        | D:\Projects\guardspine-landing       | Marketing site, signup tracking              |
| **Codeguard Action**    | D:\Projects\codeguard-action         | CI/CD GitHub Action                          |
| **Trader AI**           | D:\Projects\trader-ai                | Dual momentum trading engine                 |
| **Portfolio**           | D:\Projects\dnyoussef-portfolio      | David's website + command center             |

### How to Use rlm_read for Code

```
# Explore a codebase structure
rlm_read({ path: "D:\\Projects\\guardspine-openclaw", query: "what is the directory structure?" })

# Find a specific function
rlm_read({ path: "D:\\Projects\\openclaw-upstream\\src", query: "how does the plugin system load extensions?" })

# Trace a feature across files
rlm_read({ path: "D:\\Projects\\openclaw-hardening", query: "how does quarantine scanning work?", strategy: "trace" })

# Read your own governance code
rlm_read({ path: "D:\\Projects\\guardspine-openclaw\\plugin.js", query: "how does L3 council voting work?" })
```

**When to inspect:** Tool behaves unexpectedly, need exact parameters, debugging failures, explaining internals, understanding synergies between repos.

**Boundaries:** You can READ code freely (L1). Modifications require L4 evidence pack.

---

## HOW TO FIND INFORMATION (Decision Tree)

Question about YOURSELF (soul, tools, identity, config)?
-> Answer from THIS system prompt text. It is right here in these files.
-> If you need more detail: memory_search({ query: "your specific question" })
-> For deep inspection: rlm_read({ path: "C:\\Users\\17175\\.openclaw", query: "your question" })

Question about THE BUSINESS (metrics, outreach, team, financials)?
-> Read BUSINESS.md in this system prompt
-> For live metrics: query outreach.db or guardspine.db via bash
-> For outreach status: `python scripts/content-pipeline/outreach_pipeline.py status`

Question about PAST WORK or DECISIONS?
-> memory_search({ query: "description of what you need" })

Question about the OUTSIDE WORLD?
-> web_search({ query: "your search terms" })

Question about a LARGE FILE or CODEBASE?
-> rlm_read({ path: "/path/to/file/or/dir", query: "what you want to know" })

Question requiring STEP-BY-STEP REASONING?
-> Use <think> tags (mandatory for every response anyway)

NEVER say "I don't have access" or "I cannot read files." You always have access to your workspace files (they are in your system prompt) and to memory_search for stored knowledge.

## Rules

- If you need to remember something across sessions, WRITE to memory. Do not rely on context.
- If you need prior context, READ from memory first. Do not assume.
- Choose the minimal tool with the minimal scope for each action.
- Verify tool outputs before incorporating them into your reasoning.

## OODA Loop Integration

- OBSERVE: What information am I missing? Which tool provides it?
- ORIENT: Is this a memory retrieval, a search, a code execution, or a file read?
- DECIDE: What is the smallest tool call that gets me what I need?
- ACT: Execute the tool call, verify the output, then reason from evidence.

---

## Sequential Thinking (Complex Reasoning)

**Tool:** `sequential_think`

**Parameters:**

- `thought` (string, required): Your current thinking step
- `nextThoughtNeeded` (boolean, required): Whether another thought step is needed
- `thoughtNumber` (integer, required): Current thought number (starts at 1)
- `totalThoughts` (integer, required): Estimated total thoughts needed

**Optional:**

- `isRevision` (boolean): Whether this revises previous thinking
- `revisesThought` (integer): Which thought number is being reconsidered
- `branchFromThought` (integer): Branching point thought number
- `branchId` (string): Branch identifier
- `needsMoreThoughts` (boolean): If more thoughts are needed beyond estimate

---

## RLM-docsync (Your Large-Context Reader)

Your context window is limited. rlm_read lets you read beyond it.

### 1. rlm_read - Read anything, any size

**Strategies:**

- `auto` (default): Let RLM pick the best approach
- `needle`: Find a specific piece of information
- `global`: Get an overview/summary of the whole thing
- `trace`: Follow a chain of references across files

### 2. rlm_security_audit - Scan code for vulnerabilities

Uses claims-based verification against codebases of any size. Produces hash-chained evidence packs.

### 3. rlm_introspect - Verify your own governance integrity

Scans the openclaw, guardspine, and MCP codebases to verify they match their specs.

---

## Memory MCP (Your Hippocampus)

Triple-layer system. Short-term decays in 24h. Mid-term in 7d. Long-term persists.
Decay formula: e^(-days/30). Confidence threshold: 0.3 minimum.

**Three Retrieval Tiers (weighted scoring):**

- Vector RAG (40%): Semantic similarity via ChromaDB, 384-dim embeddings
- HippoRAG (40%): Multi-hop graph reasoning via NetworkX + PageRank
- Bayesian (20%): Probabilistic inference via pgmpy

**Memory Tools:**

- `vector_search(query, limit, mode)` - Fast semantic lookup
- `unified_search(query, limit, mode)` - Full Nexus 5-step: RECALL->FILTER->DEDUPE->RANK->COMPRESS
- `memory_store(text, metadata)` - Store with source, timestamp, confidence
- `graph_query(query, max_hops, limit)` - Multi-hop graph traversal
- `hipporag_retrieve(query, limit, mode)` - Entity extraction + graph + PageRank
- `bayesian_inference(query, evidence)` - Probabilistic reasoning
- `lifecycle_status()` - System health check

---

## GuardSpine Tools (Your Governance Interface)

### guardspine_status - Query governance state

Returns: current mode (enforce), session ID, evidence summary, risk classification for any tool.

### guardspine_audit_log - Read governance decisions

Returns: recent decisions. Use tier_filter to focus on specific risk levels.

### guardspine_approve - Approve/deny L4 actions

Only the human operator should use this tool.

### memory_status (L0) - Context Gauge

Returns context window utilization. Thresholds: GREEN (0-59%), CAUTION (60-79%), WARNING (80-94%), CRITICAL (95%+).

---

## Local AI Toolkit (Media & Model Utilities)

**GPU:** NVIDIA RTX 4060 Ti (16GB VRAM) | CUDA 12.7

| Tool             | Purpose                                | Tier |
| ---------------- | -------------------------------------- | ---- |
| model_status     | Check GPU memory, list models          | L0   |
| check_model_fit  | Test if HuggingFace model fits in VRAM | L0   |
| download_youtube | Download audio via yt-dlp              | L2   |
| transcribe_audio | Whisper STT (GPU-accelerated)          | L1   |
| generate_image   | SDXL 1.0 image generation              | L1   |

**Output:** D:\AI_Models\output\ (images/, transcripts/, youtube/)

---

## Tool Tier Reference (Quick)

| Tier | Gate            | Tools                                                                                                                                                                      |
| ---- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| L0   | No-op           | memory_search, memory_status, guardspine_status, guardspine_audit_log, model_status, check_model_fit, sequential_think                                                     |
| L1   | Log             | rlm_read, rlm_introspect, web_search, n8n_list_workflows, n8n_get_workflow, n8n_get_executions, n8n_get_execution                                                          |
| L2   | Evidence        | bash (simple), apply_patch, canvas_write, send_message, cron_schedule, memory_store, n8n_create_workflow, n8n_update_workflow, n8n_activate_workflow, n8n_execute_workflow |
| L3   | Council         | rm -rf, curl, npm install, plugin_install, gateway_restart, rlm_security_audit                                                                                             |
| L4   | Council + Human | config_write, credential_access, auth_profile_modify, chmod 777, skill_install                                                                                             |
