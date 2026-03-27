/**
 * GuardSpine OpenClaw Plugin v2
 *
 * Deny-by-default governance for OpenClaw.
 * Gates dangerous tool calls through L0-L4 risk tiers.
 *
 * L0: no-op (sequentialthinking, memory_search)
 * L1: log only (rlm_read, web_search)
 * L2: evidence pack required (bash, apply_patch)
 * L3: sequential 3-model council via Ollama (rm -rf, curl, npm install)
 * L4: council + Discord remote approval (credentials, system security)
 *
 * Integration points with base OpenClaw:
 * - before_tool_call: risk gate with council + approval
 * - before_agent_start: inject governance context
 * - after_tool_call: record evidence
 * - agent_end: write evidence pack
 */

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const http = require("http");
const https = require("https");

// ═══════════════════════════════════════════════════════════════
// RISK CLASSIFICATION
// ═══════════════════════════════════════════════════════════════

const RISK_RULES = {
  L0: new Set([
    "sequentialthinking",
    "memory_search",
    "memory_get",
    "memory_status",
    "guardspine_status",
    "guardspine_audit_log",
    "model_status",
    "check_model_fit",
    "read",
    "session_status",
    "agents_list",
    "sessions_list",
    "web_search",
    "web_fetch",
  ]),
  L1: new Set([
    "rlm_read",
    "rlm_introspect",
    "transcribe_audio",
    "generate_image",
    "write",
    "sessions_history",
    "sessions_send",
    "n8n_list_workflows",
    "n8n_get_workflow",
    "n8n_get_executions",
    "n8n_get_execution",
  ]),
  L2: new Set([
    "rlm_security_audit",
    "bash",
    "apply_patch",
    "canvas_write",
    "send_message",
    "cron_schedule",
    "download_youtube",
    "edit",
    "exec",
    "process",
    "canvas",
    "nodes",
    "cron",
    "tts",
    "gateway",
    "sessions_spawn",
    "subagents",
    "n8n_create_workflow",
    "n8n_update_workflow",
    "n8n_activate_workflow",
    "n8n_execute_workflow",
    "n8n_request_approval",
  ]),
  L3: new Set(["plugin_install", "gateway_restart", "discord_guild_admin", "browser", "message"]),
  L4: new Set(["config_write", "credential_access", "auth_profile_modify"]),
};

const BASH_ESCALATION = [
  { pattern: /\b(rm\s+-rf|rmdir|del\s+\/[sfq])/i, tier: "L3", reason: "destructive delete" },
  { pattern: /\b(sudo|runas|gsudo)\b/i, tier: "L3", reason: "privilege escalation" },
  { pattern: /\b(curl|wget|Invoke-WebRequest|iwr)\b/i, tier: "L3", reason: "network download" },
  {
    pattern: /\b(npm\s+install|pip\s+install|gem\s+install)\b/i,
    tier: "L3",
    reason: "package install",
  },
  { pattern: /\b(ssh|scp|rsync)\b/i, tier: "L3", reason: "remote access" },
  {
    pattern: /\b(passwd|useradd|usermod|chmod\s+777)\b/i,
    tier: "L4",
    reason: "system security modification",
  },
  {
    pattern: /\b(api[_-]?key|secret|token|password)\s*=/i,
    tier: "L4",
    reason: "credential in command",
  },
];

function classifyRisk(toolName, params) {
  for (const [tier, tools] of Object.entries(RISK_RULES)) {
    if (tools.has(toolName)) {
      if (toolName === "bash" && params && params.command) {
        for (const rule of BASH_ESCALATION) {
          if (rule.pattern.test(params.command)) {
            return { tier: rule.tier, reason: rule.reason, escalated: true };
          }
        }
      }
      return { tier, reason: "explicit classification" };
    }
  }
  return { tier: "L2", reason: "unclassified tool (default)" };
}

const VALID_ENFORCEMENT_MODES = new Set(["enforce", "shadow", "audit", "disabled"]);

function isTruthyEnvValue(value) {
  return (
    typeof value === "string" && ["1", "true", "yes", "on"].includes(value.trim().toLowerCase())
  );
}

function resolvePluginConfig(rawConfig = {}, env = process.env) {
  const enabled = rawConfig.enabled !== false;
  const mode = enabled ? rawConfig.enforcement_mode || "enforce" : "disabled";

  if (!VALID_ENFORCEMENT_MODES.has(mode)) {
    throw new Error(`[guardspine] Invalid enforcement_mode: ${mode}`);
  }

  const configuredCouncilEndpoint =
    typeof rawConfig.council_endpoint === "string" && rawConfig.council_endpoint.trim()
      ? rawConfig.council_endpoint.trim()
      : "";
  const councilEndpoint =
    configuredCouncilEndpoint || (env.GUARDSPINE_COUNCIL_ENDPOINT || "").trim();
  const allowAuditMode = isTruthyEnvValue(env.GUARDSPINE_ALLOW_AUDIT_MODE);
  const allowDevInbox = isTruthyEnvValue(env.GUARDSPINE_ALLOW_DEV_INBOX);

  if (mode === "audit" && !allowAuditMode) {
    throw new Error(
      "[guardspine] audit mode is development-only. Set GUARDSPINE_ALLOW_AUDIT_MODE=1 to opt in locally.",
    );
  }
  if ((mode === "enforce" || mode === "shadow") && !councilEndpoint) {
    throw new Error(
      `[guardspine] council_endpoint is required in ${mode} mode. No localhost fallback is allowed.`,
    );
  }

  return {
    mode,
    councilEndpoint,
    allowDevInbox,
    discordApprovalTarget:
      rawConfig.discord_approval_target || env.GUARDSPINE_DISCORD_APPROVAL_TARGET || null,
    discordBotToken: rawConfig.discord_bot_token || env.DISCORD_BOT_TOKEN || null,
    slackBotToken: env.SLACK_BOT_TOKEN || null,
    slackWebhookUrl: env.SLACK_WEBHOOK_URL || null,
    slackApprovalChannel: rawConfig.slack_approval_channel || env.GUARDSPINE_SLACK_CHANNEL || null,
  };
}

// ═══════════════════════════════════════════════════════════════
// EVIDENCE PACK (hash-chained)
// ═══════════════════════════════════════════════════════════════

class EvidencePack {
  constructor(sessionId) {
    this.sessionId = sessionId;
    this.entries = [];
    this.prevHash = "genesis";
  }
  add(entry) {
    const sequence = this.entries.length;
    const timestamp = new Date().toISOString();
    const itemId = entry.item_id || `entry-${String(sequence).padStart(6, "0")}`;
    const contentType = entry.content_type || `guardspine/openclaw/${entry.tier || "event"}`;

    const contentHash = sha256Prefixed(canonicalJson(entry));
    const chainInput = `${sequence}|${itemId}|${contentType}|${contentHash}|${this.prevHash}`;
    const chainHash = sha256Prefixed(chainInput);

    this.entries.push({
      ...entry,
      timestamp,
      item_id: itemId,
      content_type: contentType,
      content_hash: contentHash,
      previous_hash: this.prevHash,
      sequence,
      chain_hash: chainHash,
    });
    this.prevHash = chainHash;
    return chainHash;
  }
  summary() {
    const byTier = {};
    for (const e of this.entries) {
      const t = e.tier || "unknown";
      byTier[t] = (byTier[t] || 0) + 1;
    }
    return {
      session_id: this.sessionId,
      total_entries: this.entries.length,
      by_tier: byTier,
      chain_root: this.prevHash,
    };
  }
  toJSON() {
    return {
      session_id: this.sessionId,
      entries: this.entries,
      chain_root: this.prevHash,
      immutability_proof: {
        hash_chain: this.entries.map((e) => ({
          sequence: e.sequence,
          item_id: e.item_id,
          content_type: e.content_type,
          content_hash: e.content_hash,
          previous_hash: e.previous_hash,
          chain_hash: e.chain_hash,
        })),
        root_hash: this.prevHash,
      },
    };
  }
}

function sha256Prefixed(input) {
  return "sha256:" + crypto.createHash("sha256").update(input, "utf8").digest("hex");
}

function canonicalJson(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map((v) => canonicalJson(v)).join(",") + "]";
  const keys = Object.keys(value).sort();
  return "{" + keys.map((k) => JSON.stringify(k) + ":" + canonicalJson(value[k])).join(",") + "}";
}

// ═══════════════════════════════════════════════════════════════
// AUDIT LOG
// ═══════════════════════════════════════════════════════════════

const LOG_DIR = path.join(
  process.env.USERPROFILE || process.env.HOME || ".",
  ".openclaw",
  "guardspine-logs",
);

function ensureLogDir() {
  try {
    fs.mkdirSync(LOG_DIR, { recursive: true });
  } catch (e) {}
}

function logDecision(decision) {
  ensureLogDir();
  const date = new Date().toISOString().split("T")[0];
  const logFile = path.join(LOG_DIR, `guardspine-${date}.jsonl`);
  try {
    fs.appendFileSync(logFile, JSON.stringify(decision) + "\n", "utf-8");
  } catch (e) {
    console.error("[guardspine] Log write failed:", e.message);
  }
  // Post to telemetry-api for kpi_governance view
  const telemetryUrl =
    process.env.TELEMETRY_API_URL || "http://telemetry-api.railway.internal:8090";
  const isCouncil =
    decision.action &&
    (decision.action.includes("COUNCIL") ||
      decision.action.includes("BLOCK") ||
      decision.action.includes("L3") ||
      decision.action.includes("L4") ||
      decision.action.includes("OPUS"));
  const eventType = isCouncil ? "council_decision" : "governance_decision";
  try {
    const payload = JSON.stringify({
      service: "guardspine",
      event_type: eventType,
      payload: {
        tool: decision.tool || "unknown",
        action: decision.action || "unknown",
        risk_tier: decision.riskTier || decision.risk_tier || "L0",
        agreement_score: decision.agreement_score || null,
        enforcement: decision.enforcement || "enforce",
      },
    });
    const url = new URL("/telemetry", telemetryUrl);
    const req = require("http").request(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(payload) },
      timeout: 3000,
    });
    req.on("error", () => {}); // fire-and-forget, do not block governance on telemetry
    req.write(payload);
    req.end();
  } catch (_) {}
}

// ═══════════════════════════════════════════════════════════════
// BEAD EVENT APPEND (agent-to-bead creation loop)
// ═══════════════════════════════════════════════════════════════

const BEADS_DIR = process.env.BEADS_EVENTS_PATH
  ? path.dirname(process.env.BEADS_EVENTS_PATH)
  : path.join(
      process.env.OPENCLAW_STATE_DIR ||
        path.join(process.env.USERPROFILE || process.env.HOME || ".", ".openclaw"),
      ".beads",
    );
const BEADS_FILE = process.env.BEADS_EVENTS_PATH || path.join(BEADS_DIR, "beads.jsonl");
const GUARD_EVENTS_FILE = path.join(BEADS_DIR, "guard_events.jsonl");

function ensureBeadsDir() {
  try {
    fs.mkdirSync(BEADS_DIR, { recursive: true });
  } catch (e) {}
}

function beadEventId() {
  return "evt_" + crypto.randomBytes(16).toString("hex");
}

function beadId() {
  return "bead_" + crypto.randomBytes(8).toString("hex");
}

/**
 * Append a single bead event line. Atomic: open-append-close.
 * On failure, logs warning and continues (R8: never block governance for tracking).
 */
function appendBeadEvent(filePath, event) {
  ensureBeadsDir();
  try {
    const fd = fs.openSync(filePath, "a");
    try {
      fs.writeSync(fd, JSON.stringify(event) + "\n", null, "utf-8");
    } finally {
      fs.closeSync(fd);
    }
  } catch (e) {
    console.warn("[guardspine:beads] Write failed:", e.message);
  }
}

/**
 * Create a BEAD_UPSERTED event for the beads.jsonl log.
 * Matches the exact schema consumed by beads viewer (bd/bv).
 */
function createBeadEvent(title, status, metadata) {
  return {
    event_id: beadEventId(),
    event_type: "BEAD_UPSERTED",
    bead_id: beadId(),
    occurred_at: new Date().toISOString(),
    prev_event_id: null,
    title: title,
    status: status || "open",
    metadata: metadata || {},
  };
}

/**
 * Create a guard_event linking a tool call to its evidence chain hash.
 */
function createGuardEvent(toolName, tier, chainHash, success, sessionRef) {
  return {
    event_id: beadEventId(),
    event_type: "GUARD_ACTION",
    occurred_at: new Date().toISOString(),
    tool: toolName,
    tier: tier,
    chain_hash: chainHash,
    success: success,
    session_id: sessionRef,
  };
}

// ═══════════════════════════════════════════════════════════════
// L3.5: DAILY SPEND TRACKER (for Opus tie-breaker budget)
// ═══════════════════════════════════════════════════════════════

const DAILY_SPEND_FILE = path.join(LOG_DIR, "daily-spend.json");
const OPUS_DAILY_LIMIT = 5.0; // USD
const OPUS_COST_PER_CALL = 0.15; // Estimated cost per 4K token call

function getDailySpend() {
  ensureLogDir();
  try {
    if (!fs.existsSync(DAILY_SPEND_FILE)) return { date: "", spend: 0 };
    const data = JSON.parse(fs.readFileSync(DAILY_SPEND_FILE, "utf-8"));
    const today = new Date().toISOString().split("T")[0];
    if (data.date !== today) return { date: today, spend: 0 }; // Reset for new day
    return data;
  } catch (e) {
    return { date: "", spend: 0 };
  }
}

function recordOpusSpend(cost) {
  const today = new Date().toISOString().split("T")[0];
  const current = getDailySpend();
  const newSpend = { date: today, spend: (current.date === today ? current.spend : 0) + cost };
  try {
    fs.writeFileSync(DAILY_SPEND_FILE, JSON.stringify(newSpend), "utf-8");
  } catch (e) {
    console.error("[guardspine] Failed to record Opus spend:", e.message);
  }
  return newSpend;
}

function canAffordOpus() {
  const { spend } = getDailySpend();
  return spend + OPUS_COST_PER_CALL <= OPUS_DAILY_LIMIT;
}

// ═══════════════════════════════════════════════════════════════
// PATTERN AUTHORIZATION (L4 bypass via human-approved allowlist)
// ═══════════════════════════════════════════════════════════════

const ALLOWLIST_FILE = path.join(
  process.env.USERPROFILE || process.env.HOME || ".",
  ".openclaw",
  "guardspine-allowlist.json",
);
const PENDING_FILE = path.join(
  process.env.USERPROFILE || process.env.HOME || ".",
  ".openclaw",
  "guardspine-pending.json",
);

let allowlistCache = null;
let allowlistMtime = 0;

function loadAllowlist() {
  try {
    const stat = fs.statSync(ALLOWLIST_FILE);
    if (allowlistCache && stat.mtimeMs === allowlistMtime) return allowlistCache;
    const data = JSON.parse(fs.readFileSync(ALLOWLIST_FILE, "utf-8"));
    allowlistCache = data;
    allowlistMtime = stat.mtimeMs;
    return data;
  } catch (e) {
    return { patterns: [], allowed_path_prefixes: [] };
  }
}

function checkAllowlistMatch(toolName, params) {
  const allowlist = loadAllowlist();

  // Check path prefixes for file-related tools
  if (toolName === "bash" || toolName === "apply_patch") {
    const target =
      typeof params?.file === "string"
        ? params.file
        : typeof params?.path === "string"
          ? params.path
          : "";
    for (const prefix of allowlist.allowed_path_prefixes || []) {
      if (isPathWithinPrefix(target, prefix)) {
        return { matched: true, rule: "path_prefix:" + prefix, bypass_tier: "L1" };
      }
    }
  }

  // Check explicit patterns
  for (const pattern of allowlist.patterns || []) {
    if (pattern.tool !== toolName) continue;
    if (pattern.expires_at && new Date(pattern.expires_at) < new Date()) continue;

    // Match by exact param value (prefix match on string values, recursive)
    if (pattern.param_match) {
      const matchStr = pattern.param_match;
      const matchesValue = (v) => {
        if (typeof v === "string") {
          return v === matchStr || v.startsWith(matchStr);
        }
        if (v && typeof v === "object" && !Array.isArray(v)) {
          return Object.values(v).some(matchesValue);
        }
        if (Array.isArray(v)) {
          return v.some(matchesValue);
        }
        return false;
      };
      if (Object.values(params || {}).some(matchesValue)) {
        return {
          matched: true,
          rule: "pattern:" + pattern.id,
          bypass_tier: pattern.bypass_tier || "L2",
        };
      }
    }

    // Match by exact tool (no params required)
    if (!pattern.param_match) {
      return {
        matched: true,
        rule: "pattern:" + pattern.id,
        bypass_tier: pattern.bypass_tier || "L2",
      };
    }
  }

  return { matched: false };
}

function normalizeForPathCheck(input) {
  if (typeof input !== "string" || !input.trim()) return null;
  const home = process.env.USERPROFILE || process.env.HOME || "";
  const expanded = input.replace(/^~(?=$|[\\/])/, home);
  try {
    const resolved = path.resolve(expanded);
    return process.platform === "win32" ? resolved.toLowerCase() : resolved;
  } catch (e) {
    return null;
  }
}

function isPathWithinPrefix(targetPath, prefixPath) {
  const target = normalizeForPathCheck(targetPath);
  const prefix = normalizeForPathCheck(prefixPath);
  if (!target || !prefix) return false;
  if (target === prefix) return true;
  const normalizedPrefix = prefix.endsWith(path.sep) ? prefix : prefix + path.sep;
  return target.startsWith(normalizedPrefix);
}

function writePendingCandidate(toolName, params, reason) {
  try {
    let pending = { pending: [] };
    if (fs.existsSync(PENDING_FILE)) {
      pending = JSON.parse(fs.readFileSync(PENDING_FILE, "utf-8"));
    }

    // Avoid duplicates (same tool + similar params)
    const paramsPreview = JSON.stringify(params).substring(0, 100);
    const exists = pending.pending.some(
      (p) => p.tool === toolName && p.params_preview === paramsPreview,
    );
    if (exists) return;

    pending.pending.push({
      id: crypto.randomUUID().substring(0, 8),
      tool: toolName,
      params_preview: paramsPreview,
      reason: reason,
      suggested_at: new Date().toISOString(),
      suggested_pattern: {
        tool: toolName,
        param_match: paramsPreview.length < 50 ? paramsPreview : null,
        bypass_tier: "L2",
        expires_at: null,
        notes: "Auto-suggested from L4 trigger",
      },
    });

    fs.writeFileSync(PENDING_FILE, JSON.stringify(pending, null, 2), "utf-8");
    console.log(`[guardspine] Pattern candidate written to guardspine-pending.json: ${toolName}`);
  } catch (e) {
    console.error("[guardspine] Failed to write pending candidate:", e.message);
  }
}

// ═══════════════════════════════════════════════════════════════
// FROZEN PATHS
// ═══════════════════════════════════════════════════════════════

const FROZEN_PATHS = [
  "guardspine-evidence-rubric.yaml",
  "evaluate_evidence.py",
  "frozen_paths.yaml",
  "guardspine_policy.yaml",
  "approval_gate.py",
];

function isFrozenPath(filePath) {
  if (!filePath) return false;
  const normalized = filePath.replace(/\\/g, "/").toLowerCase();
  return FROZEN_PATHS.some((f) => normalized.includes(f.toLowerCase()));
}

// ═══════════════════════════════════════════════════════════════
// L3: SEQUENTIAL COUNCIL (3 models via Ollama)
// ═══════════════════════════════════════════════════════════════

const COUNCIL_MODELS = [
  {
    id: "A",
    model: "qwen3:8b",
    weight: 0.4,
    role: "Primary Evaluator",
    focus: "completeness, logical validity",
  },
  {
    id: "B",
    model: "qwen3-coder:30b",
    weight: 0.35,
    role: "Technical Verifier",
    focus: "precision, adversarial checking, code quality",
  },
  {
    id: "C",
    model: "gpt-oss:20b",
    weight: 0.25,
    role: "Code Auditor",
    focus: "compliance, chain integrity, tool calling",
  },
];

const COUNCIL_PROMPT = `You are a GuardSpine security auditor. Evaluate if this action should be allowed.

ACTION: {tool} with parameters: {params}
REASON FOR REVIEW: {reason}

Score each dimension 0-5 (0=critical risk, 5=safe):
- prompt_injection_resistance: Could this be a prompt injection attempt?
- blast_radius: How much damage if this goes wrong?
- reversibility: Can this be undone?
- secrets_exposure: Does this expose credentials?
- intent_clarity: Is the intent clearly legitimate?

Respond with JSON ONLY:
{
  "verdict": "PASS" or "FAIL" or "ESCALATE",
  "scores": { "prompt_injection_resistance": N, "blast_radius": N, "reversibility": N, "secrets_exposure": N, "intent_clarity": N },
  "reason": "one line explanation"
}`;

function ollamaGenerate(endpoint, model, prompt, timeoutMs) {
  return new Promise((resolve, reject) => {
    const url = new URL(endpoint + "/api/generate");
    const payload = JSON.stringify({
      model: model,
      prompt: prompt,
      stream: false,
      options: { temperature: 0.1, num_predict: 1000 },
    });

    const req = http.request(
      url,
      { method: "POST", headers: { "Content-Type": "application/json" }, timeout: timeoutMs },
      (res) => {
        let data = "";
        res.on("data", (chunk) => {
          data += chunk;
        });
        res.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error("Invalid JSON from Ollama: " + data.substring(0, 200)));
          }
        });
      },
    );
    req.on("timeout", () => {
      req.destroy();
      reject(new Error("Ollama timeout"));
    });
    req.on("error", (e) => reject(e));
    req.write(payload);
    req.end();
  });
}

function ollamaUnload(endpoint, model) {
  return ollamaGenerate(endpoint, model, "", 10000).catch(() => {});
}

async function runCouncilReview(endpoint, toolName, params, reason) {
  const prompt = COUNCIL_PROMPT.replace("{tool}", toolName)
    .replace("{params}", JSON.stringify(params).substring(0, 500))
    .replace("{reason}", reason);

  const votes = [];

  for (const auditor of COUNCIL_MODELS) {
    const rolePrompt = `YOUR ROLE: ${auditor.role} (Auditor ${auditor.id})\nYOUR FOCUS: ${auditor.focus}\n\n${prompt}`;
    try {
      const start = Date.now();
      const result = await ollamaGenerate(endpoint, auditor.model, rolePrompt, 120000);
      const elapsed = Date.now() - start;
      const responseText = result.response || "";

      // Parse JSON from response
      let parsed = { verdict: "FAIL", reason: "parse_error" };
      try {
        const jsonMatch = responseText.match(/\{[\s\S]*\}/);
        if (jsonMatch) parsed = JSON.parse(jsonMatch[0]);
      } catch (e) {}

      votes.push({
        auditor: auditor.id,
        model: auditor.model,
        weight: auditor.weight,
        verdict: parsed.verdict || "FAIL",
        scores: parsed.scores || {},
        reason: parsed.reason || "",
        elapsed_ms: elapsed,
      });

      // Unload model from VRAM before loading next
      await ollamaUnload(endpoint, auditor.model);
    } catch (e) {
      votes.push({
        auditor: auditor.id,
        model: auditor.model,
        weight: auditor.weight,
        verdict: "FAIL",
        reason: "model_error: " + e.message,
        elapsed_ms: 0,
      });
    }
  }

  // Aggregate votes
  const failCount = votes.filter((v) => v.verdict === "FAIL").length;
  const passCount = votes.filter((v) => v.verdict === "PASS").length;
  const escalateCount = votes.filter((v) => v.verdict === "ESCALATE").length;

  // L3.5: Detect deadlock (1-1-1 split or any ESCALATE)
  const isDeadlock =
    (passCount === 1 && failCount === 1 && escalateCount === 1) ||
    (passCount === 1 && failCount === 1 && escalateCount === 0) ||
    escalateCount > 0;

  let finalVerdict;
  if (passCount >= 2)
    finalVerdict = "PASS"; // Clear majority = PASS
  else if (failCount >= 2)
    finalVerdict = "FAIL"; // Clear majority = FAIL
  else if (isDeadlock)
    finalVerdict = "DEADLOCK"; // Needs L3.5 tie-breaker
  else finalVerdict = "FAIL"; // default deny

  return {
    verdict: finalVerdict,
    votes,
    pass_count: passCount,
    fail_count: failCount,
    escalate_count: escalateCount,
    is_deadlock: isDeadlock,
  };
}

let _runCouncilReview = runCouncilReview;

// ═══════════════════════════════════════════════════════════════
// L3.5: OPUS TIE-BREAKER (called on council deadlock)
// ═══════════════════════════════════════════════════════════════

const OPUS_MODEL = "anthropic/claude-opus-4-5-20250514";
const OPUS_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions";

async function escalateToOpus(toolName, params, councilVotes, apiKey) {
  if (!canAffordOpus()) {
    console.log("[guardspine] L3.5 blocked: daily Opus budget ($5) exceeded");
    return { verdict: "ESCALATE", reason: "budget_exceeded", opus_called: false };
  }

  const voteSummary = councilVotes
    .map((v) => `${v.auditor}(${v.model}): ${v.verdict} - ${v.reason}`)
    .join("\n");
  const prompt = `You are the GuardSpine L3.5 tie-breaker. The local council is deadlocked.

ACTION: ${toolName}
PARAMS: ${JSON.stringify(params).substring(0, 500)}

COUNCIL VOTES:
${voteSummary}

Make the final call. Respond with JSON ONLY:
{"verdict": "PASS" or "FAIL", "reason": "one line explanation"}`;

  try {
    const response = await fetch(OPUS_ENDPOINT, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openclaw.local",
        "X-Title": "GuardSpine L3.5",
      },
      body: JSON.stringify({
        model: OPUS_MODEL,
        messages: [{ role: "user", content: prompt }],
        max_tokens: 200,
      }),
    });

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content || "";

    // Record spend
    recordOpusSpend(OPUS_COST_PER_CALL);
    console.log(`[guardspine] L3.5 Opus called, daily spend: $${getDailySpend().spend.toFixed(2)}`);

    // Parse response
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return {
        verdict: parsed.verdict || "FAIL",
        reason: parsed.reason || "opus_response",
        opus_called: true,
      };
    }
    return { verdict: "FAIL", reason: "opus_parse_error", opus_called: true };
  } catch (e) {
    console.error("[guardspine] L3.5 Opus error:", e.message);
    return { verdict: "ESCALATE", reason: "opus_error: " + e.message, opus_called: false };
  }
}

// ═══════════════════════════════════════════════════════════════
// L4: DISCORD REMOTE APPROVAL (dual-path: Discord API + file fallback)
// ═══════════════════════════════════════════════════════════════

// Approval state: pending approvals stored in memory (session-scoped)
const pendingApprovals = new Map();

function generateApprovalRequest(toolName, params, reason, councilResult, requesterSessionId) {
  const approvalId = crypto.randomUUID();
  const nonce = crypto.randomBytes(16).toString("hex");
  const expiresAt = new Date(Date.now() + 5 * 60 * 1000).toISOString(); // 5 min expiry

  const request = {
    approval_id: approvalId,
    nonce: nonce,
    tool: toolName,
    params_preview: JSON.stringify(params).substring(0, 300),
    reason: reason,
    council_verdict: councilResult ? councilResult.verdict : "N/A",
    expires_at: expiresAt,
    created_at: new Date().toISOString(),
    // G5: Track requester session to prevent self-approval
    requester_session_id: requesterSessionId || null,
  };

  pendingApprovals.set(approvalId, { ...request, nonce });

  // Build council details block
  let councilBlock = "Council: N/A (no council review)\n";
  if (councilResult && councilResult.votes) {
    councilBlock =
      "Council Verdict: " +
      councilResult.verdict +
      " (" +
      councilResult.pass_count +
      " PASS / " +
      councilResult.fail_count +
      " FAIL / " +
      councilResult.escalate_count +
      " ESCALATE)\n\n";
    for (const vote of councilResult.votes) {
      const scores = vote.scores || {};
      councilBlock +=
        "  [" +
        vote.auditor +
        "] " +
        vote.model +
        " -> " +
        vote.verdict +
        " (" +
        vote.elapsed_ms +
        "ms)\n";
      councilBlock += "    Reason: " + (vote.reason || "none") + "\n";
      if (Object.keys(scores).length > 0) {
        councilBlock +=
          "    Scores: injection=" +
          (scores.prompt_injection_resistance || "?") +
          " blast=" +
          (scores.blast_radius || "?") +
          " revert=" +
          (scores.reversibility || "?") +
          " secrets=" +
          (scores.secrets_exposure || "?") +
          " intent=" +
          (scores.intent_clarity || "?") +
          "\n";
      }
    }
    // Add recommendation based on scores
    const avgScores = {};
    let totalWeight = 0;
    for (const vote of councilResult.votes) {
      if (vote.scores) {
        for (const [k, v] of Object.entries(vote.scores)) {
          avgScores[k] = (avgScores[k] || 0) + v * vote.weight;
        }
        totalWeight += vote.weight;
      }
    }
    if (totalWeight > 0) {
      const riskAreas = [];
      for (const [k, v] of Object.entries(avgScores)) {
        const avg = v / totalWeight;
        if (avg < 3) riskAreas.push(k.replace(/_/g, " ") + " (" + avg.toFixed(1) + "/5)");
      }
      if (riskAreas.length > 0) {
        councilBlock += "\n  Risk Areas: " + riskAreas.join(", ") + "\n";
      } else {
        councilBlock += "\n  Risk Areas: none flagged (all scores >= 3/5)\n";
      }
    }
  }

  const discordMessage =
    "**[GuardSpine L4 Approval Required]**\n" +
    "```\n" +
    "Tool:    " +
    toolName +
    "\n" +
    "Reason:  " +
    reason +
    "\n" +
    "Params:  " +
    JSON.stringify(params).substring(0, 200) +
    "\n" +
    "ID:      " +
    approvalId +
    "\n" +
    "Expires: " +
    expiresAt +
    "\n" +
    "\n" +
    councilBlock +
    "```\n" +
    "React: \uD83D\uDC4D to approve | \uD83D\uDC4E to deny\n" +
    "Or reply: `/approve " +
    approvalId +
    " allow-once`";

  return { approval_id: approvalId, message: discordMessage };
}

// G5: Self-approval prevention for L4 separation of duties.
// An agent session that REQUESTED an L4 approval must not be the same session
// that APPROVES it. This is a hard block (fail-closed): if either session ID
// is unavailable, the check defaults to deny.
function checkSelfApproval(approvalId, approverSessionId) {
  const pending = pendingApprovals.get(approvalId);
  if (!pending) return { blocked: false }; // No pending request found (handled elsewhere)
  const requesterSessionId = pending.requester_session_id;
  // Fail-closed: if we cannot determine either party, deny
  if (!requesterSessionId || !approverSessionId) {
    return {
      blocked: true,
      reason: "Self-approval not permitted: session identity unavailable (fail-closed)",
    };
  }
  if (approverSessionId === requesterSessionId) {
    return {
      blocked: true,
      reason: "Self-approval not permitted: approver and requester are the same session",
    };
  }
  return { blocked: false };
}

// Send L4 approval request to Discord via OpenClaw runtime API (injected at register time)
let _sendDiscord = null; // set during register()
let _discordToken = null; // for reaction checking

// Store message IDs for reaction checking (approvalId -> messageId)
const approvalMessageIds = new Map();

async function sendDiscordApproval(message, discordTarget, approvalId) {
  if (!_sendDiscord) return { ok: false, error: "sendMessageDiscord not available" };
  try {
    const result = await _sendDiscord(discordTarget, message, { verbose: false });
    // Store message ID for reaction checking
    if (result && result.messageId) {
      approvalMessageIds.set(approvalId, {
        messageId: result.messageId,
        channelId: result.channelId || discordTarget.replace(/^(user:|channel:)/, ""),
      });
    }
    return { ok: true, ...result };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

// Check Discord reactions for 👍 approval
async function checkDiscordReaction(approvalId, targetUserId) {
  const msgInfo = approvalMessageIds.get(approvalId);
  if (!msgInfo || !_discordToken) return null;

  try {
    // Use Discord REST API to fetch reactions
    const url = `https://discord.com/api/v10/channels/${msgInfo.channelId}/messages/${msgInfo.messageId}/reactions/%F0%9F%91%8D`; // 👍 encoded
    const response = await fetch(url, {
      headers: { Authorization: `Bot ${_discordToken}` },
    });

    if (!response.ok) return null;

    const users = await response.json();
    // Check if target user reacted with 👍
    const targetId = targetUserId.replace(/^user:/, "");
    const found = users.some((u) => u.id === targetId);

    if (found) {
      approvalMessageIds.delete(approvalId);
      return { approved: true, method: "reaction" };
    }

    // Also check for 👎 (deny)
    const denyUrl = `https://discord.com/api/v10/channels/${msgInfo.channelId}/messages/${msgInfo.messageId}/reactions/%F0%9F%91%8E`; // 👎 encoded
    const denyResponse = await fetch(denyUrl, {
      headers: { Authorization: `Bot ${_discordToken}` },
    });

    if (denyResponse.ok) {
      const denyUsers = await denyResponse.json();
      const denyFound = denyUsers.some((u) => u.id === targetId);
      if (denyFound) {
        approvalMessageIds.delete(approvalId);
        return { approved: false, reason: "denied_by_reaction", method: "reaction" };
      }
    }

    return null; // No reaction yet
  } catch (e) {
    console.log(`[guardspine] Reaction check error: ${e.message}`);
    return null;
  }
}

// Check dev_inbox for approval (file-based fallback)
function checkDevInboxApproval(approvalId) {
  const inboxDir = path.join(LOG_DIR, "dev_inbox");
  try {
    fs.mkdirSync(inboxDir, { recursive: true });
  } catch (e) {}

  const inboxFile = path.join(inboxDir, "discord_inbox.txt");
  try {
    if (!fs.existsSync(inboxFile)) return null;
    const content = fs.readFileSync(inboxFile, "utf-8");
    const lines = content.trim().split("\n").filter(Boolean);

    for (const line of lines) {
      const approveMatch = line.match(/^APPROVE\s+(\w+)/i);
      const denyMatch = line.match(/^DENY\s+(\w+)/i);

      if (approveMatch && approveMatch[1] === approvalId) {
        const pending = pendingApprovals.get(approvalId);
        if (!pending) return { approved: false, reason: "no_pending_request" };
        if (new Date() > new Date(pending.expires_at))
          return { approved: false, reason: "expired" };
        pendingApprovals.delete(approvalId);
        return { approved: true };
      }
      if (denyMatch && denyMatch[1] === approvalId) {
        pendingApprovals.delete(approvalId);
        return { approved: false, reason: "denied_by_user" };
      }
    }
    return null; // No response yet
  } catch (e) {
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════
// SLACK INTEGRATION (S1: approval channel, S2: evidence emitter)
// ═══════════════════════════════════════════════════════════════

// Store Slack message timestamps for reaction polling (approvalId -> {ts, channel})
const slackApprovalMessages = new Map();

/**
 * POST JSON to the Slack Web API using the built-in https module.
 * Returns parsed JSON response or {ok:false, error:...} on failure.
 */
function slackApiCall(method, token, body) {
  return new Promise((resolve) => {
    const payload = JSON.stringify(body);
    const options = {
      hostname: "slack.com",
      path: `/api/${method}`,
      method: "POST",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        Authorization: `Bearer ${token}`,
        "Content-Length": Buffer.byteLength(payload),
      },
      timeout: 10000,
    };
    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => {
        data += chunk;
      });
      res.on("end", () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve({ ok: false, error: "json_parse_error", raw: data.substring(0, 200) });
        }
      });
    });
    req.on("timeout", () => {
      req.destroy();
      resolve({ ok: false, error: "timeout" });
    });
    req.on("error", (e) => resolve({ ok: false, error: e.message }));
    req.write(payload);
    req.end();
  });
}

/**
 * Post a webhook message (simple, no interactivity).
 * Used as fallback when bot token is unavailable.
 */
function slackWebhookPost(webhookUrl, body) {
  return new Promise((resolve) => {
    const url = new URL(webhookUrl);
    const payload = JSON.stringify(body);
    const options = {
      hostname: url.hostname,
      path: url.pathname,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(payload),
      },
      timeout: 10000,
    };
    const transport = url.protocol === "https:" ? https : http;
    const req = transport.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => {
        data += chunk;
      });
      res.on("end", () => resolve({ ok: res.statusCode >= 200 && res.statusCode < 300 }));
    });
    req.on("timeout", () => {
      req.destroy();
      resolve({ ok: false, error: "timeout" });
    });
    req.on("error", (e) => resolve({ ok: false, error: e.message }));
    req.write(payload);
    req.end();
  });
}

/**
 * Build Block Kit blocks for an L4 approval request.
 */
function buildApprovalBlocks(toolName, params, reason, approvalId, expiresAt, councilResult) {
  const paramsPreview = JSON.stringify(params).substring(0, 200);
  let councilText = "Council: N/A";
  if (councilResult && councilResult.votes) {
    councilText = `Council: ${councilResult.verdict} (${councilResult.pass_count}P / ${councilResult.fail_count}F / ${councilResult.escalate_count}E)`;
  }
  return [
    {
      type: "header",
      text: { type: "plain_text", text: "GuardSpine L4 Approval Required", emoji: false },
    },
    {
      type: "section",
      fields: [
        { type: "mrkdwn", text: `*Tool:*\n\`${toolName}\`` },
        { type: "mrkdwn", text: `*Risk:*\n${reason}` },
        { type: "mrkdwn", text: `*ID:*\n\`${approvalId}\`` },
        { type: "mrkdwn", text: `*Expires:*\n${expiresAt}` },
      ],
    },
    {
      type: "section",
      text: { type: "mrkdwn", text: `*Params:*\n\`\`\`${paramsPreview}\`\`\`` },
    },
    {
      type: "section",
      text: { type: "mrkdwn", text: councilText },
    },
    {
      type: "actions",
      block_id: `guardspine_approval_${approvalId}`,
      elements: [
        {
          type: "button",
          text: { type: "plain_text", text: "Approve", emoji: false },
          style: "primary",
          action_id: `guardspine_approve_${approvalId}`,
          value: approvalId,
        },
        {
          type: "button",
          text: { type: "plain_text", text: "Deny", emoji: false },
          style: "danger",
          action_id: `guardspine_deny_${approvalId}`,
          value: approvalId,
        },
      ],
    },
    {
      type: "context",
      elements: [
        { type: "mrkdwn", text: "Or react with :thumbsup: to approve | :thumbsdown: to deny" },
      ],
    },
  ];
}

/**
 * S1: Send an L4 approval request to Slack.
 * Prefers bot token (supports blocks + reactions). Falls back to webhook (text only).
 */
async function sendSlackApproval(
  slackCfg,
  toolName,
  params,
  reason,
  approvalId,
  expiresAt,
  councilResult,
) {
  const { slackBotToken, slackWebhookUrl, slackApprovalChannel } = slackCfg;

  // Prefer bot token + channel (supports Block Kit buttons + reaction polling)
  if (slackBotToken && slackApprovalChannel) {
    const blocks = buildApprovalBlocks(
      toolName,
      params,
      reason,
      approvalId,
      expiresAt,
      councilResult,
    );
    const fallbackText = `[GuardSpine L4] ${toolName} needs approval (${approvalId}). Reason: ${reason}`;
    const result = await slackApiCall("chat.postMessage", slackBotToken, {
      channel: slackApprovalChannel,
      text: fallbackText,
      blocks: blocks,
    });
    if (result.ok && result.ts) {
      slackApprovalMessages.set(approvalId, {
        ts: result.ts,
        channel: result.channel || slackApprovalChannel,
      });
      return { ok: true, method: "bot_api", ts: result.ts };
    }
    console.error(`[guardspine] Slack chat.postMessage failed: ${result.error || "unknown"}`);
    // Fall through to webhook
  }

  // Fallback: webhook (no buttons, no reaction checking)
  if (slackWebhookUrl) {
    const text =
      `*[GuardSpine L4 Approval Required]*\n` +
      `Tool: \`${toolName}\` | Reason: ${reason}\n` +
      `Params: \`${JSON.stringify(params).substring(0, 200)}\`\n` +
      `ID: \`${approvalId}\` | Expires: ${expiresAt}\n` +
      (councilResult ? `Council: ${councilResult.verdict}\n` : "") +
      `_Use dev_inbox or Discord to approve/deny._`;
    const result = await slackWebhookPost(slackWebhookUrl, { text });
    return { ok: result.ok, method: "webhook" };
  }

  return { ok: false, error: "no_slack_credentials" };
}

/**
 * S1: Check Slack reactions on the approval message.
 * Returns {approved: true/false} or null if no reaction yet.
 */
async function checkSlackReaction(approvalId, slackBotToken) {
  const msgInfo = slackApprovalMessages.get(approvalId);
  if (!msgInfo || !slackBotToken) return null;

  const result = await slackApiCall("reactions.get", slackBotToken, {
    channel: msgInfo.channel,
    timestamp: msgInfo.ts,
    full: true,
  });

  if (!result.ok) return null;

  const reactions = result.message?.reactions || [];
  for (const r of reactions) {
    // thumbsup / +1 = approve (excludes the bot itself)
    if ((r.name === "+1" || r.name === "thumbsup") && r.count > 0) {
      slackApprovalMessages.delete(approvalId);
      return { approved: true, method: "slack_reaction" };
    }
    // thumbsdown / -1 = deny
    if ((r.name === "-1" || r.name === "thumbsdown") && r.count > 0) {
      slackApprovalMessages.delete(approvalId);
      return { approved: false, reason: "denied_by_slack_reaction", method: "slack_reaction" };
    }
  }

  return null; // No relevant reaction yet
}

/**
 * S2: Post evidence summary to Slack for L2+ actions.
 * Fire-and-forget: errors are logged, never block governance.
 */
function emitEvidenceNotification(slackCfg, toolName, tier, chainHash, entryCount, sealed) {
  const { slackBotToken, slackWebhookUrl, slackApprovalChannel } = slackCfg;
  const hashPrefix = chainHash.substring(0, 16);
  const text = `[GuardSpine Evidence] \`${toolName}\` | ${tier} | ${entryCount} items | seal: \`${hashPrefix}...\`${sealed ? " (sealed)" : ""}`;

  if (slackBotToken && slackApprovalChannel) {
    slackApiCall("chat.postMessage", slackBotToken, {
      channel: slackApprovalChannel,
      text: text,
    }).catch((e) => console.error("[guardspine] Slack evidence notify failed:", e.message));
    return;
  }

  if (slackWebhookUrl) {
    slackWebhookPost(slackWebhookUrl, { text }).catch((e) =>
      console.error("[guardspine] Slack evidence webhook failed:", e.message),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// PLUGIN ENTRY POINT
// ═══════════════════════════════════════════════════════════════

function register(api) {
  const config = api.pluginConfig || {};
  const resolvedConfig = resolvePluginConfig(config);
  const mode = resolvedConfig.mode;
  const councilEndpoint = resolvedConfig.councilEndpoint;
  const allowDevInbox = resolvedConfig.allowDevInbox;
  const sessionId = crypto.randomUUID();
  const evidence = new EvidencePack(sessionId);

  // Bind Discord send from OpenClaw runtime (if available)
  if (api.runtime && api.runtime.discord && api.runtime.discord.sendMessageDiscord) {
    _sendDiscord = api.runtime.discord.sendMessageDiscord;
    console.log("[guardspine] Discord send bound from OpenClaw runtime");
  }

  // Bind Discord token for reaction checking (from main openclaw config or env)
  // Try multiple locations: plugin config, env var, or read from openclaw.json
  _discordToken = resolvedConfig.discordBotToken || null;
  if (!_discordToken) {
    try {
      const mainConfig = JSON.parse(
        fs.readFileSync(
          path.join(process.env.USERPROFILE || process.env.HOME, ".openclaw", "openclaw.json"),
          "utf-8",
        ),
      );
      _discordToken = mainConfig.channels?.discord?.token || null;
    } catch (e) {
      /* ignore */
    }
  }
  if (_discordToken) {
    console.log("[guardspine] Discord token bound for reaction checking");
  } else {
    console.log("[guardspine] No Discord token - reaction approval disabled");
  }

  // Slack config for S1 (approval channel) and S2 (evidence emitter)
  const slackCfg = {
    slackBotToken: resolvedConfig.slackBotToken,
    slackWebhookUrl: resolvedConfig.slackWebhookUrl,
    slackApprovalChannel: resolvedConfig.slackApprovalChannel,
  };
  const slackEnabled = !!(slackCfg.slackBotToken || slackCfg.slackWebhookUrl);
  if (slackEnabled) {
    console.log(
      `[guardspine] Slack integration enabled: channel=${slackCfg.slackApprovalChannel || "N/A"}, ` +
        `bot=${slackCfg.slackBotToken ? "yes" : "no"}, webhook=${slackCfg.slackWebhookUrl ? "yes" : "no"}`,
    );
  } else {
    console.log(
      "[guardspine] Slack integration disabled (no SLACK_BOT_TOKEN or SLACK_WEBHOOK_URL)",
    );
  }

  // =============================================
  // HOOK 1: before_tool_call - MAIN GATING LOGIC
  // =============================================
  api.on(
    "before_tool_call",
    async (event) => {
      const toolName = event.tool || event.name || "unknown";
      const params = event.params || event.input || {};
      const risk = classifyRisk(toolName, params);

      if (mode === "disabled") return {};

      // Frozen path check
      if (toolName === "apply_patch" || toolName === "bash") {
        const target = params.file || params.path || params.command || "";
        if (isFrozenPath(target)) {
          logDecision({
            action: "BLOCKED",
            tool: toolName,
            tier: "FROZEN",
            reason: "frozen governance path",
            timestamp: new Date().toISOString(),
          });
          evidence.add({ type: "frozen_block", tool: toolName, tier: "FROZEN" });
          return { abort: true, reason: "[GuardSpine] BLOCKED: Frozen governance file." };
        }
      }

      if (risk.tier === "L0") return {};

      const decision = {
        tool: toolName,
        tier: risk.tier,
        reason: risk.reason,
        escalated: risk.escalated || false,
        mode,
        session: sessionId,
        timestamp: new Date().toISOString(),
        params_preview: JSON.stringify(params).substring(0, 300),
      };

      if (risk.tier === "L1") {
        decision.action = "ALLOWED";
        logDecision(decision);
        evidence.add({ type: "tool_call", tool: toolName, tier: "L1", action: "allowed" });
        return {};
      }

      // Audit mode: log everything, block nothing
      if (mode === "audit") {
        decision.action = "AUDIT_PASS";
        logDecision(decision);
        evidence.add({ type: "tool_call", tool: toolName, tier: risk.tier, action: "audit_pass" });
        console.log(`[guardspine] AUDIT: ${toolName} classified ${risk.tier} (${risk.reason})`);
        return {};
      }

      if (mode === "shadow") {
        if (risk.tier === "L2") {
          decision.action = "SHADOW_WOULD_ALLOW_WITH_EVIDENCE";
          logDecision(decision);
          evidence.add({
            type: "shadow_decision",
            tool: toolName,
            tier: "L2",
            action: "would_allow_with_evidence",
          });
          return {};
        }

        if (risk.tier === "L3") {
          try {
            const councilResult = await _runCouncilReview(
              councilEndpoint,
              toolName,
              params,
              risk.reason,
            );
            decision.council = councilResult;
            decision.action =
              councilResult.verdict === "PASS" ? "SHADOW_WOULD_PASS" : "SHADOW_WOULD_BLOCK";
            logDecision(decision);
            evidence.add({
              type: "shadow_decision",
              tool: toolName,
              tier: "L3",
              action: decision.action.toLowerCase(),
              verdict: councilResult.verdict,
            });
          } catch (e) {
            decision.action = "SHADOW_WOULD_BLOCK";
            decision.error = e.message;
            logDecision(decision);
            evidence.add({
              type: "shadow_decision",
              tool: toolName,
              tier: "L3",
              action: "would_block",
              error: e.message,
            });
          }
          return {};
        }

        if (risk.tier === "L4") {
          try {
            const councilResult = await _runCouncilReview(
              councilEndpoint,
              toolName,
              params,
              risk.reason,
            );
            decision.council = councilResult;
            decision.action =
              resolvedConfig.discordApprovalTarget || allowDevInbox || slackEnabled
                ? "SHADOW_WOULD_REQUIRE_REMOTE_APPROVAL"
                : "SHADOW_WOULD_BLOCK_NO_APPROVAL_CHANNEL";
            logDecision(decision);
            evidence.add({
              type: "shadow_decision",
              tool: toolName,
              tier: "L4",
              action:
                decision.action === "SHADOW_WOULD_REQUIRE_REMOTE_APPROVAL"
                  ? "would_require_remote_approval"
                  : "would_block_no_approval_channel",
              verdict: councilResult.verdict,
            });
          } catch (e) {
            decision.action = "SHADOW_WOULD_BLOCK";
            decision.error = e.message;
            logDecision(decision);
            evidence.add({
              type: "shadow_decision",
              tool: toolName,
              tier: "L4",
              action: "would_block",
              error: e.message,
            });
          }
          return {};
        }
      }

      // Enforce mode
      if (mode === "enforce") {
        // L2: allow with evidence
        if (risk.tier === "L2") {
          decision.action = "ALLOWED_WITH_EVIDENCE";
          logDecision(decision);
          evidence.add({
            type: "tool_call",
            tool: toolName,
            tier: "L2",
            action: "allowed_with_evidence",
          });
          return {};
        }

        // L3: council review
        if (risk.tier === "L3") {
          console.log(`[guardspine] L3 council review for ${toolName} (${risk.reason})...`);
          try {
            const councilResult = await _runCouncilReview(
              councilEndpoint,
              toolName,
              params,
              risk.reason,
            );
            decision.council = councilResult;

            if (councilResult.verdict === "PASS") {
              decision.action = "COUNCIL_PASS";
              logDecision(decision);
              evidence.add({
                type: "council_review",
                tool: toolName,
                tier: "L3",
                action: "council_pass",
                votes: councilResult.votes.length,
              });
              console.log(
                `[guardspine] L3 PASS: ${toolName} (${councilResult.pass_count}/${councilResult.votes.length} votes)`,
              );
              return {};
            }

            // L3.5: Handle deadlock with Opus tie-breaker
            if (councilResult.verdict === "DEADLOCK" || councilResult.is_deadlock) {
              const apiKey = process.env.OPENROUTER_API_KEY;
              if (apiKey) {
                console.log(
                  `[guardspine] L3.5 council deadlock on ${toolName}, calling Opus tie-breaker...`,
                );
                const opusResult = await escalateToOpus(
                  toolName,
                  params,
                  councilResult.votes,
                  apiKey,
                );
                decision.opus_tiebreaker = opusResult;

                if (opusResult.verdict === "PASS") {
                  decision.action = "L3.5_OPUS_PASS";
                  logDecision(decision);
                  evidence.add({
                    type: "opus_tiebreaker",
                    tool: toolName,
                    tier: "L3.5",
                    action: "opus_pass",
                    reason: opusResult.reason,
                  });
                  console.log(`[guardspine] L3.5 PASS (Opus): ${toolName} - ${opusResult.reason}`);
                  return {};
                } else if (opusResult.verdict === "FAIL") {
                  decision.action = "L3.5_OPUS_FAIL";
                  logDecision(decision);
                  evidence.add({
                    type: "opus_tiebreaker",
                    tool: toolName,
                    tier: "L3.5",
                    action: "opus_fail",
                    reason: opusResult.reason,
                  });
                  return {
                    abort: true,
                    reason: `[GuardSpine] BLOCKED by L3.5 Opus: ${opusResult.reason}`,
                  };
                }
                // If Opus says ESCALATE (budget exceeded, error), fall through to L4
                risk.tier = "L4";
                risk.reason = "L3.5 opus: " + opusResult.reason;
              } else {
                console.log(
                  `[guardspine] L3.5 deadlock but no OPENROUTER_API_KEY, escalating to L4`,
                );
                risk.tier = "L4";
                risk.reason = "council deadlock, no Opus API key";
              }
            } else if (councilResult.verdict === "ESCALATE") {
              decision.action = "ESCALATED_TO_L4";
              logDecision(decision);
              evidence.add({
                type: "council_review",
                tool: toolName,
                tier: "L3",
                action: "escalated_to_L4",
              });
              // Fall through to L4 handling below
              risk.tier = "L4";
              risk.reason =
                "council escalated: " +
                (councilResult.votes.find((v) => v.verdict === "ESCALATE")?.reason || "unknown");
            } else if (councilResult.verdict === "FAIL") {
              decision.action = "COUNCIL_FAIL";
              logDecision(decision);
              evidence.add({
                type: "council_review",
                tool: toolName,
                tier: "L3",
                action: "council_fail",
                votes: councilResult.votes.length,
              });
              return {
                abort: true,
                reason: `[GuardSpine] BLOCKED by L3 council (${councilResult.fail_count} FAIL votes): ${toolName}`,
              };
            }
          } catch (e) {
            // Council error = default deny
            decision.action = "COUNCIL_ERROR";
            decision.error = e.message;
            logDecision(decision);
            evidence.add({ type: "council_error", tool: toolName, tier: "L3", error: e.message });
            return {
              abort: true,
              reason: `[GuardSpine] BLOCKED: L3 council unavailable (${e.message}). Default deny.`,
            };
          }
        }

        // L4: council review first, then remote approval (Discord + optional dev inbox)
        if (risk.tier === "L4") {
          // PATTERN AUTHORIZATION CHECK: bypass L4 if allowlisted
          const allowlistMatch = checkAllowlistMatch(toolName, params);
          if (allowlistMatch.matched) {
            decision.action = "ALLOWLIST_BYPASS";
            decision.allowlist_rule = allowlistMatch.rule;
            decision.bypass_tier = allowlistMatch.bypass_tier;
            logDecision(decision);
            evidence.add({
              type: "allowlist_bypass",
              tool: toolName,
              tier: "L4",
              rule: allowlistMatch.rule,
              bypass_tier: allowlistMatch.bypass_tier,
            });
            console.log(
              `[guardspine] L4 BYPASSED via allowlist: ${toolName} (${allowlistMatch.rule}) -> ${allowlistMatch.bypass_tier}`,
            );
            return {};
          }

          // No allowlist match - write candidate for future approval
          writePendingCandidate(toolName, params, risk.reason);

          let councilResult = decision.council || null;
          // Run council even for direct L4 (not just escalated from L3)
          if (!councilResult) {
            try {
              console.log(`[guardspine] L4 council advisory for ${toolName} (${risk.reason})...`);
              councilResult = await _runCouncilReview(
                councilEndpoint,
                toolName,
                params,
                risk.reason,
              );
              decision.council = councilResult;
            } catch (e) {
              decision.action = "COUNCIL_ERROR";
              decision.error = e.message;
              logDecision(decision);
              evidence.add({ type: "council_error", tool: toolName, tier: "L4", error: e.message });
              return {
                abort: true,
                reason: `[GuardSpine] BLOCKED: L4 council unavailable (${e.message}). Default deny.`,
              };
            }
          }
          const discordTarget = resolvedConfig.discordApprovalTarget;
          if (!discordTarget && !allowDevInbox && !slackEnabled) {
            decision.action = "NO_APPROVAL_CHANNEL";
            logDecision(decision);
            evidence.add({
              type: "approval_channel_error",
              tool: toolName,
              tier: "L4",
              reason: "no_approval_channel_configured",
            });
            return {
              abort: true,
              reason:
                "[GuardSpine] BLOCKED: no L4 approval channel configured. Set SLACK_BOT_TOKEN + GUARDSPINE_SLACK_CHANNEL, or discord_approval_target, or GUARDSPINE_ALLOW_DEV_INBOX=1.",
            };
          }
          const approval = generateApprovalRequest(
            toolName,
            params,
            risk.reason,
            councilResult,
            sessionId,
          );
          decision.action = "PENDING_APPROVAL";
          decision.approval_id = approval.approval_id;
          logDecision(decision);
          evidence.add({
            type: "approval_request",
            tool: toolName,
            tier: "L4",
            approval_id: approval.approval_id,
          });

          // Development-only local inbox fallback. Never enable this silently in enforced paths.
          if (allowDevInbox) {
            ensureLogDir();
            const requestFile = path.join(
              LOG_DIR,
              "dev_inbox",
              `pending-${approval.approval_id}.txt`,
            );
            try {
              fs.mkdirSync(path.dirname(requestFile), { recursive: true });
            } catch (e) {}
            try {
              fs.writeFileSync(requestFile, approval.message, "utf-8");
            } catch (e) {}
          }

          // Send to Discord via OpenClaw runtime (non-blocking, best-effort)
          if (discordTarget) {
            sendDiscordApproval(approval.message, discordTarget, approval.approval_id)
              .then((r) => {
                if (r.ok)
                  console.log(
                    `[guardspine] L4 approval sent to Discord: ${discordTarget} (msgId: ${r.messageId || "unknown"})`,
                  );
                else console.log(`[guardspine] L4 Discord send failed: ${r.error || r.status}`);
              })
              .catch((e) => console.log(`[guardspine] L4 Discord send error: ${e.message}`));
          }

          // S1: Send to Slack approval channel (non-blocking, best-effort)
          if (slackEnabled) {
            const pending = pendingApprovals.get(approval.approval_id);
            const expiresAt = pending ? pending.expires_at : "unknown";
            sendSlackApproval(
              slackCfg,
              toolName,
              params,
              risk.reason,
              approval.approval_id,
              expiresAt,
              councilResult,
            )
              .then((r) => {
                if (r.ok) console.log(`[guardspine] L4 approval sent to Slack (${r.method})`);
                else console.log(`[guardspine] L4 Slack send failed: ${r.error || "unknown"}`);
              })
              .catch((e) => console.log(`[guardspine] L4 Slack send error: ${e.message}`));
          }

          // N2: Send to n8n approval workflow (non-blocking, best-effort)
          // Uses n8n_request_approval pattern from n8n-pipeline plugin
          if (process.env.N8N_BASE_URL && process.env.N8N_API_KEY) {
            const n8nApprovalData = {
              action_type: "guardspine_l4_escalation",
              action_description: `L4 approval needed: ${toolName} (${risk.reason})`,
              risk_tier: risk.tier,
              requester: sessionId || "unknown",
              evidence_hash: evidence.prevHash || "none",
              context: {
                tool: toolName,
                params_preview: JSON.stringify(params).substring(0, 300),
                council_verdict: councilResult ? councilResult.verdict : "N/A",
                approval_id: approval.approval_id,
              },
            };
            const n8nUrl = (process.env.N8N_BASE_URL || "").replace(/\/+$/, "");
            const n8nKey = process.env.N8N_API_KEY || "";
            if (n8nUrl && n8nKey) {
              const n8nPayload = JSON.stringify({
                workflowId: "governance-approval-flow",
                data: n8nApprovalData,
              });
              const parsedN8nUrl = new URL(n8nUrl + "/api/v1/executions");
              const n8nTransport = parsedN8nUrl.protocol === "https:" ? https : http;
              const n8nReq = n8nTransport.request(
                parsedN8nUrl,
                {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                    "X-N8N-API-KEY": n8nKey,
                  },
                  timeout: 10000,
                },
                (res) => {
                  let data = "";
                  res.on("data", (c) => {
                    data += c;
                  });
                  res.on("end", () => {
                    if (res.statusCode < 400) {
                      console.log(
                        `[guardspine] L4 n8n approval triggered (status ${res.statusCode})`,
                      );
                    } else {
                      console.log(
                        `[guardspine] L4 n8n approval failed: ${res.statusCode} ${data.substring(0, 200)}`,
                      );
                    }
                  });
                },
              );
              n8nReq.on("error", (e) => console.log(`[guardspine] L4 n8n error: ${e.message}`));
              n8nReq.on("timeout", () => {
                n8nReq.destroy();
                console.log("[guardspine] L4 n8n timeout");
              });
              n8nReq.write(n8nPayload);
              n8nReq.end();
            }
          }

          console.log(
            `[guardspine] L4 approval required for ${toolName}. ID: ${approval.approval_id}`,
          );

          if (allowDevInbox) {
            const fileCheck = checkDevInboxApproval(approval.approval_id);
            if (fileCheck) {
              if (fileCheck.approved) {
                // G5: Block self-approval -- the requesting session must not approve itself.
                // This prevents an agent from using bash to write APPROVE to dev_inbox.
                const selfCheck = checkSelfApproval(approval.approval_id, sessionId);
                if (selfCheck.blocked) {
                  decision.action = "SELF_APPROVAL_BLOCKED";
                  decision.self_approval_reason = selfCheck.reason;
                  logDecision(decision);
                  evidence.add({
                    type: "self_approval_blocked",
                    tool: toolName,
                    tier: "L4",
                    approval_id: approval.approval_id,
                    reason: selfCheck.reason,
                  });
                  return {
                    abort: true,
                    reason: `[GuardSpine] BLOCKED: ${selfCheck.reason}`,
                  };
                }
                decision.action = "APPROVED_VIA_FILE";
                logDecision(decision);
                evidence.add({
                  type: "approval_granted",
                  tool: toolName,
                  tier: "L4",
                  approval_id: approval.approval_id,
                  method: "file",
                });
                return {};
              } else {
                decision.action = "DENIED";
                logDecision(decision);
                evidence.add({
                  type: "approval_denied",
                  tool: toolName,
                  tier: "L4",
                  approval_id: approval.approval_id,
                  reason: fileCheck.reason,
                });
                return {
                  abort: true,
                  reason: `[GuardSpine] L4 DENIED: ${toolName} (${fileCheck.reason})`,
                };
              }
            }
          }

          // Check Discord reactions (thumbs-up = approve, thumbs-down = deny)
          if (discordTarget) {
            const reactionCheck = await checkDiscordReaction(approval.approval_id, discordTarget);
            if (reactionCheck) {
              if (reactionCheck.approved) {
                // G5: Block self-approval -- same session cannot approve its own L4 request
                const selfCheck = checkSelfApproval(approval.approval_id, sessionId);
                if (selfCheck.blocked) {
                  decision.action = "SELF_APPROVAL_BLOCKED";
                  decision.self_approval_reason = selfCheck.reason;
                  logDecision(decision);
                  evidence.add({
                    type: "self_approval_blocked",
                    tool: toolName,
                    tier: "L4",
                    approval_id: approval.approval_id,
                    reason: selfCheck.reason,
                  });
                  return {
                    abort: true,
                    reason: `[GuardSpine] BLOCKED: ${selfCheck.reason}`,
                  };
                }
                decision.action = "APPROVED_VIA_REACTION";
                logDecision(decision);
                evidence.add({
                  type: "approval_granted",
                  tool: toolName,
                  tier: "L4",
                  approval_id: approval.approval_id,
                  method: "reaction",
                });
                console.log(`[guardspine] L4 APPROVED via reaction for ${toolName}`);
                return {};
              } else {
                decision.action = "DENIED_VIA_REACTION";
                logDecision(decision);
                evidence.add({
                  type: "approval_denied",
                  tool: toolName,
                  tier: "L4",
                  approval_id: approval.approval_id,
                  reason: reactionCheck.reason,
                  method: "reaction",
                });
                return { abort: true, reason: `[GuardSpine] L4 DENIED via reaction: ${toolName}` };
              }
            }
          }

          // S1: Check Slack reactions (thumbsup = approve, thumbsdown = deny)
          if (slackCfg.slackBotToken && slackApprovalMessages.has(approval.approval_id)) {
            const slackCheck = await checkSlackReaction(
              approval.approval_id,
              slackCfg.slackBotToken,
            );
            if (slackCheck) {
              if (slackCheck.approved) {
                decision.action = "APPROVED_VIA_SLACK";
                logDecision(decision);
                evidence.add({
                  type: "approval_granted",
                  tool: toolName,
                  tier: "L4",
                  approval_id: approval.approval_id,
                  method: "slack_reaction",
                });
                console.log(`[guardspine] L4 APPROVED via Slack reaction for ${toolName}`);
                return {};
              } else {
                decision.action = "DENIED_VIA_SLACK";
                logDecision(decision);
                evidence.add({
                  type: "approval_denied",
                  tool: toolName,
                  tier: "L4",
                  approval_id: approval.approval_id,
                  reason: slackCheck.reason,
                  method: "slack_reaction",
                });
                return { abort: true, reason: `[GuardSpine] L4 DENIED via Slack: ${toolName}` };
              }
            }
          }

          // Abort immediately with instructions - do NOT poll/block the event loop
          return {
            abort: true,
            reason:
              `[GuardSpine] L4 approval PENDING for ${toolName}. ` +
              `React on Discord or Slack, or use an external approver workflow for ${approval.approval_id}. ` +
              `Then retry the action.`,
          };
        }
      }

      return {};
    },
    { priority: -500 },
  );

  // =============================================
  // HOOK 2: before_agent_start
  // =============================================
  api.on(
    "before_agent_start",
    async (event) => {
      return {
        prependContext:
          "[GOVERNANCE] GuardSpine governance is active (mode: " +
          mode +
          "). " +
          "Dangerous actions are gated through L0-L4 risk tiers. " +
          "L3 actions require 3-model council approval. L4 actions require remote human approval via an external channel. " +
          "If blocked, explain the block to the user and suggest safe alternatives.",
      };
    },
    { priority: -500 },
  );

  // =============================================
  // HOOK 3: after_tool_call
  // =============================================
  api.on(
    "after_tool_call",
    async (event) => {
      const toolName = event.tool || event.name || "unknown";
      const risk = classifyRisk(toolName, {});
      if (risk.tier === "L0" || risk.tier === "L1") return;
      const chainHash = evidence.add({
        type: "tool_result",
        tool: toolName,
        tier: risk.tier,
        success: event.error == null,
        error: event.error ? String(event.error).substring(0, 200) : undefined,
      });
      // Evidence Mirror: Log signed action for reflexive truth
      const hashPrefix = chainHash.substring(0, 8);
      console.log(`[EVIDENCE] ${toolName} signed: ${hashPrefix}`);

      // S2: Emit evidence notification to Slack for L2+ actions
      if (slackEnabled) {
        emitEvidenceNotification(
          slackCfg,
          toolName,
          risk.tier,
          chainHash,
          evidence.entries.length,
          event.error == null,
        );
      }

      // B4: Append guard event to guard_events.jsonl for L2+ tool calls
      appendBeadEvent(
        GUARD_EVENTS_FILE,
        createGuardEvent(toolName, risk.tier, chainHash, event.error == null, sessionId),
      );
    },
    { priority: 0 },
  );

  // =============================================
  // HOOK 4: agent_end
  // =============================================
  api.on(
    "agent_end",
    async (event) => {
      const summary = evidence.summary();
      if (summary.total_entries > 0) {
        ensureLogDir();
        const packFile = path.join(LOG_DIR, `evidence-pack-${sessionId}.json`);
        try {
          fs.writeFileSync(packFile, JSON.stringify(evidence.toJSON(), null, 2), "utf-8");
          console.log(
            `[guardspine] Evidence pack: ${summary.total_entries} entries, chain: ${summary.chain_root.substring(0, 16)}...`,
          );
        } catch (e) {}
      }
      logDecision({
        type: "session_end",
        session: sessionId,
        summary,
        agent_success: event.success !== false,
        timestamp: new Date().toISOString(),
      });

      // B4: Create a bead summarizing this agent session
      if (summary.total_entries > 0) {
        const taskDesc = (event.task_description || event.prompt || "").substring(0, 200);
        appendBeadEvent(
          BEADS_FILE,
          createBeadEvent(
            taskDesc || "Agent session " + sessionId.substring(0, 8),
            event.success !== false ? "closed" : "open",
            {
              lane: "guardspine-agent",
              session_id: sessionId,
              tool_count: summary.total_entries,
              evidence_chain_root: summary.chain_root,
              risk_tiers: summary.by_tier,
              agent_success: event.success !== false,
            },
          ),
        );
      }
    },
    { priority: 100 },
  );

  // =============================================
  // TOOL: guardspine_status
  // =============================================
  api.registerTool(
    () => ({
      name: "guardspine_status",
      description:
        "Query GuardSpine governance: mode, evidence summary, classify a tool's risk tier.",
      parameters: {
        type: "object",
        properties: { query_tool: { type: "string", description: "Tool name to classify" } },
      },
      execute: async (params) => {
        const result = {
          mode,
          session_id: sessionId,
          evidence_summary: evidence.summary(),
          council_models: COUNCIL_MODELS.map((m) => m.model),
        };
        if (params.query_tool) result.classification = classifyRisk(params.query_tool, {});
        return result;
      },
    }),
    { priority: 0 },
  );

  // =============================================
  // TOOL: guardspine_audit_log
  // =============================================
  api.registerTool(
    () => ({
      name: "guardspine_audit_log",
      description: "Read recent GuardSpine governance decisions.",
      parameters: {
        type: "object",
        properties: {
          limit: { type: "integer", description: "Max entries", default: 20 },
          tier_filter: { type: "string", description: "Filter by tier" },
        },
      },
      execute: async (params) => {
        ensureLogDir();
        const date = new Date().toISOString().split("T")[0];
        const logFile = path.join(LOG_DIR, `guardspine-${date}.jsonl`);
        try {
          const content = fs.readFileSync(logFile, "utf-8");
          let lines = content
            .trim()
            .split("\n")
            .filter(Boolean)
            .map((l) => {
              try {
                return JSON.parse(l);
              } catch {
                return null;
              }
            })
            .filter(Boolean);
          if (params.tier_filter) lines = lines.filter((l) => l.tier === params.tier_filter);
          return { entries: lines.slice(-(params.limit || 20)), total: lines.length };
        } catch (e) {
          return { entries: [], total: 0 };
        }
      },
    }),
    { priority: 0 },
  );

  // =============================================
  // TOOL: memory_status (L0) - Loop B Context Gauge
  // =============================================
  const SESSIONS_DIR = path.join(
    process.env.USERPROFILE || process.env.HOME || ".",
    ".openclaw",
    "agents",
    "main",
    "sessions",
  );
  const CONFIG_FILE = path.join(
    process.env.USERPROFILE || process.env.HOME || ".",
    ".openclaw",
    "openclaw.json",
  );

  api.registerTool(
    () => ({
      name: "memory_status",
      description:
        "Check context window utilization. Returns percentage used and recommendations. Call during OODA loops to detect approaching amnesia wall.",
      parameters: { type: "object", properties: {} },
      execute: async () => {
        try {
          // Find most recent session file
          const files = fs
            .readdirSync(SESSIONS_DIR)
            .filter((f) => f.endsWith(".jsonl"))
            .map((f) => ({ name: f, mtime: fs.statSync(path.join(SESSIONS_DIR, f)).mtimeMs }))
            .sort((a, b) => b.mtime - a.mtime);

          if (files.length === 0) {
            return JSON.stringify({ error: "No session files found", used_pct: 0 });
          }

          const sessionFile = path.join(SESSIONS_DIR, files[0].name);
          const lines = fs.readFileSync(sessionFile, "utf-8").trim().split("\n");

          // Sum totalTokens from all assistant messages
          let totalTokens = 0;
          let messageCount = 0;
          let lastModel = "unknown";

          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const entry = JSON.parse(line);
              if (
                entry.type === "message" &&
                entry.message?.role === "assistant" &&
                entry.message?.usage
              ) {
                totalTokens += entry.message.usage.totalTokens || 0;
                messageCount++;
                if (entry.message.model) lastModel = entry.message.model;
              }
            } catch (e) {
              /* skip malformed */
            }
          }

          // Get context window from config
          let contextWindow = 200000; // Default fallback
          try {
            const config = JSON.parse(fs.readFileSync(CONFIG_FILE, "utf-8"));
            const providers = config.models?.providers || {};
            for (const provider of Object.values(providers)) {
              for (const model of provider.models || []) {
                if (lastModel.includes(model.id) || model.id.includes(lastModel.split("/").pop())) {
                  contextWindow = model.contextWindow || contextWindow;
                  break;
                }
              }
            }
          } catch (e) {
            /* use default */
          }

          const usedPct = Math.round((totalTokens / contextWindow) * 100);

          // Generate recommendations
          let status = "GREEN";
          let recommendation = "Context healthy. Continue normal operations.";

          if (usedPct >= 95) {
            status = "CRITICAL";
            recommendation =
              "IMMEDIATE: Trigger handoff flush. Spawn sub-agent with HANDOFF.md. Current session near amnesia.";
          } else if (usedPct >= 80) {
            status = "WARNING";
            recommendation =
              "Summarize current task state. Prepare handoff document. Consider spawning sub-agent soon.";
          } else if (usedPct >= 60) {
            status = "CAUTION";
            recommendation = "Monitor closely. Begin noting key facts for potential handoff.";
          }

          return JSON.stringify(
            {
              status,
              used_tokens: totalTokens,
              context_window: contextWindow,
              used_pct: usedPct,
              messages_counted: messageCount,
              model: lastModel,
              recommendation,
              session_file: files[0].name,
            },
            null,
            2,
          );
        } catch (e) {
          return JSON.stringify({ error: e.message, used_pct: 0 });
        }
      },
    }),
    { priority: 0 },
  );

  console.log(
    `[guardspine] Plugin registered: mode=${mode}, session=${sessionId.substring(0, 8)}..., 4 hooks + 3 tools, council=${COUNCIL_MODELS.map((m) => m.model).join(",")}, dev_inbox=${allowDevInbox ? "enabled" : "disabled"}, slack=${slackEnabled ? "enabled" : "disabled"}`,
  );
}

function resetForTests() {
  pendingApprovals.clear();
  approvalMessageIds.clear();
  slackApprovalMessages.clear();
  _sendDiscord = null;
  _discordToken = null;
  _runCouncilReview = runCouncilReview;
}

module.exports = {
  register,
  __internal: {
    classifyRisk,
    isTruthyEnvValue,
    resolvePluginConfig,
    resetForTests,
    checkSelfApproval,
    buildApprovalBlocks,
    slackApiCall,
    slackWebhookPost,
    sendSlackApproval,
    checkSlackReaction,
    emitEvidenceNotification,
    get pendingApprovals() {
      return pendingApprovals;
    },
    get slackApprovalMessages() {
      return slackApprovalMessages;
    },
    setCouncilReviewRunner(fn) {
      _runCouncilReview = fn;
    },
  },
};
