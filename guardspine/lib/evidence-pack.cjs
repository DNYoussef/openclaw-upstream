// Hash-chained evidence pack. Extracted from plugin.js (Phase 3B) so it has
// its own test coverage -- it previously existed only as an inline class with
// zero direct tests.
//
// DURABILITY: plugin.js only wrote the full chain to disk once, in the
// agent_end hook. A crash or kill between session start and agent_end lost
// every entry added in memory -- the tamper-evident chain is the receipt the
// essay argues for (Section VII); a receipt that can silently vanish before
// it's ever written isn't one. When `persistDir` is passed, each add()
// appends that entry to `evidence-pack-<sessionId>.jsonl` immediately, so a
// crash mid-session still leaves every entry added so far on disk. This
// mirrors logDecision's own philosophy exactly (best-effort, never throws,
// console.error on failure only) -- deliberately not hardened further here,
// per explicit scope decision to leave logDecision's error handling alone.

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

function sha256Prefixed(input) {
  return "sha256:" + crypto.createHash("sha256").update(input, "utf8").digest("hex");
}

function canonicalJson(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map((v) => canonicalJson(v)).join(",") + "]";
  const keys = Object.keys(value).sort();
  return "{" + keys.map((k) => JSON.stringify(k) + ":" + canonicalJson(value[k])).join(",") + "}";
}

class EvidencePack {
  constructor(sessionId, persistDir) {
    this.sessionId = sessionId;
    this.entries = [];
    this.prevHash = "genesis";
    this.persistDir = persistDir || null;
    if (this.persistDir) {
      try {
        fs.mkdirSync(this.persistDir, { recursive: true });
      } catch (e) {}
    }
  }
  add(entry) {
    const sequence = this.entries.length;
    const timestamp = new Date().toISOString();
    const itemId = entry.item_id || `entry-${String(sequence).padStart(6, "0")}`;
    const contentType = entry.content_type || `guardspine/openclaw/${entry.tier || "event"}`;

    const contentHash = sha256Prefixed(canonicalJson(entry));
    const chainInput = `${sequence}|${itemId}|${contentType}|${contentHash}|${this.prevHash}`;
    const chainHash = sha256Prefixed(chainInput);

    const fullEntry = {
      ...entry,
      timestamp,
      item_id: itemId,
      content_type: contentType,
      content_hash: contentHash,
      previous_hash: this.prevHash,
      sequence,
      chain_hash: chainHash,
    };
    this.entries.push(fullEntry);
    this.prevHash = chainHash;
    this._persistEntry(fullEntry);
    return chainHash;
  }
  _persistEntry(fullEntry) {
    if (!this.persistDir) return;
    try {
      const file = path.join(this.persistDir, `evidence-pack-${this.sessionId}.jsonl`);
      fs.appendFileSync(file, JSON.stringify(fullEntry) + "\n", "utf-8");
    } catch (e) {
      console.error("[guardspine] evidence-pack incremental persist failed:", e.message);
    }
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

module.exports = { EvidencePack, sha256Prefixed, canonicalJson };
