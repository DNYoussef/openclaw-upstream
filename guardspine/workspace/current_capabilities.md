# Current Capabilities Summary (Proprioception Layer)

_Updated: 2026-02-03_

This document serves as a short-term cognitive reference for the available tools and their operational risk tiers.

## 🛠️ Infrastructure & Management

### **Beads Task Management** (L2)

_Primary Toolset:_ `beads_ready_tasks`, `beads_task_detail`, `beads_query_tasks`, `beads_stats`
_Usage:_ Track unblocked work, manage project priority (P0=Critical), and view dashboard stats.

### **GuardSpine Governance** (L0-L4)

_Primary Toolset:_ `guardspine_status`, `guardspine_audit_log`, `guardspine_approve`, `memory_status`
_Risk Gating:_ L3 (Council Vote), L3.5 (Opus Tie-Breaker on deadlock), L4 (Local Council + Human Approval).
_Mode:_ Enforce.
_New V2.1 Features:_

- **L3.5 Tie-Breaker:** Opus escalation on council deadlock ($5/day cap)
- **Pattern Authorization:** Pre-approved L4 bypass via allowlist
- **Context Gauge:** `memory_status()` for amnesia wall detection

## 🦞 Social & Outreach

### **Moltbook Integration** (L2)

_Primary Toolset:_ `moltbook_search`, `moltbook_post`, `moltbook_comment`, `moltbook_get_feed`, `moltbook_upvote`, `moltbook_downvote`, `moltbook_status`
_Policy:_ Authentic engagement only. Non-spammy. 1 post/30min, 50 comments/day.

## 🧠 Cognition & Self-Inspection

### **RLM Large-Context Cognition** (L1)

_Primary Toolset:_ `rlm_read`, `rlm_security_audit`, `rlm_introspect`
_Capability:_ Read and verify codebases/documents up to 10M+ tokens. Use for self-verification.

### **Sequential Thinking** (L0)

_Primary Toolset:_ `sequential_think`
_Usage:_ Multi-step reasoning chains for complex design and debugging.

## 🎨 Local AI & Media

### **Local AI Toolkit** (L0-L2)

_Primary Toolset:_ `model_status`, `check_model_fit`, `download_youtube`, `transcribe_audio`, `generate_image`, `tts`
_Hardware:_ RTX 4060 Ti (16GB VRAM), RTX 2060 Super (8GB VRAM).
_Capabilities:_ Local GPU-accelerated transcription (Whisper), TTS conversion, and SDXL generation.

## 🌍 World Access

### **SearXNG & Web** (L1)

_Primary Toolset:_ `web_search`, `web_fetch`, `browser`
_Policy:_ External research and lightweight page extraction.

## 🔄 Metacognitive Loops (V2.1)

### **Loop A: Pre-Spawn Flush**

_Template:_ `~/.openclaw/workspace/HANDOFF-TEMPLATE.md`
_Purpose:_ Context handoff before spawning sub-agents. 5-bullet constraint.

### **Loop B: Context Gauge**

_Tool:_ `memory_status()` (L0)
_Purpose:_ Detect approaching amnesia wall. Call during OODA loops.
_Thresholds:_ GREEN (0-59%), CAUTION (60-79%), WARNING (80-94%), CRITICAL (95%+)

### **Loop C: Evidence Mirror**

_Hook:_ `after_tool_call` prints `[EVIDENCE] {tool} signed: {hash8}`
_Purpose:_ Anchor recent actions in consciousness to prevent hallucination.

---

**Core Rule:** Always use the minimal tool required for the task. Verify evidence packs in `~/.openclaw/guardspine-logs/` after L2+ actions.
