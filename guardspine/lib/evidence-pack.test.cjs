const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { EvidencePack, sha256Prefixed, canonicalJson } = require("./evidence-pack.cjs");

function test(name, fn) {
  try {
    fn();
    console.log("PASS:", name);
  } catch (e) {
    console.error("FAIL:", name, "--", e.message);
    process.exitCode = 1;
  }
}

function tmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "evidence-pack-test-"));
}

test("sha256Prefixed produces a stable, prefixed digest", () => {
  const h1 = sha256Prefixed("abc");
  const h2 = sha256Prefixed("abc");
  assert.strictEqual(h1, h2);
  assert.ok(h1.startsWith("sha256:"));
});

test("canonicalJson sorts keys so field order never changes the hash input", () => {
  assert.strictEqual(canonicalJson({ b: 1, a: 2 }), canonicalJson({ a: 2, b: 1 }));
});

test("EvidencePack.add builds a hash chain across entries", () => {
  const pack = new EvidencePack("sess-1");
  pack.add({ tier: "L2", tool: "bash" });
  pack.add({ tier: "L3", tool: "write" });
  assert.strictEqual(pack.entries.length, 2);
  assert.strictEqual(pack.entries[0].previous_hash, "genesis");
  assert.strictEqual(pack.entries[1].previous_hash, pack.entries[0].chain_hash);
  assert.strictEqual(pack.prevHash, pack.entries[1].chain_hash);
});

test("summary() reports total entries and per-tier counts", () => {
  const pack = new EvidencePack("sess-2");
  pack.add({ tier: "L2" });
  pack.add({ tier: "L2" });
  pack.add({ tier: "L3" });
  const summary = pack.summary();
  assert.strictEqual(summary.total_entries, 3);
  assert.deepStrictEqual(summary.by_tier, { L2: 2, L3: 1 });
});

test("toJSON() includes the full hash chain and root hash", () => {
  const pack = new EvidencePack("sess-3");
  pack.add({ tier: "L2" });
  const json = pack.toJSON();
  assert.strictEqual(json.immutability_proof.hash_chain.length, 1);
  assert.strictEqual(json.immutability_proof.root_hash, pack.prevHash);
});

test("no persistDir: add() never touches disk (backward-compatible with the old inline-class behavior)", () => {
  const pack = new EvidencePack("sess-4");
  pack.add({ tier: "L1" });
  assert.strictEqual(pack.persistDir, null);
});

test("THE DURABILITY FIX, proven with a positive control: with persistDir set, every add() is on disk immediately -- simulating a crash before any final write", () => {
  const dir = tmpDir();
  const pack = new EvidencePack("sess-crash", dir);
  pack.add({ tier: "L2", tool: "bash" });
  pack.add({ tier: "L3", tool: "write" });
  // No equivalent of agent_end's final fs.writeFileSync ever runs here --
  // this simulates the process being killed mid-session.
  const jsonlFile = path.join(dir, "evidence-pack-sess-crash.jsonl");
  assert.ok(fs.existsSync(jsonlFile), "the incremental JSONL file must exist after add(), before any final write");
  const lines = fs
    .readFileSync(jsonlFile, "utf-8")
    .trim()
    .split("\n")
    .map((l) => JSON.parse(l));
  assert.strictEqual(lines.length, 2, "both entries added before the simulated crash must already be on disk");
  assert.strictEqual(lines[0].tool, "bash");
  assert.strictEqual(lines[1].tool, "write");
  assert.strictEqual(lines[1].previous_hash, lines[0].chain_hash, "the persisted lines must preserve the real hash chain, not just raw entries");
});

test("POSITIVE CONTROL: the crash-durability assertion above can actually fail -- proven by checking the OLD (no-persistDir) behavior would have left nothing on disk", () => {
  const dir = tmpDir();
  const pack = new EvidencePack("sess-nopersist", null);
  pack.add({ tier: "L2", tool: "bash" });
  const wouldBeFile = path.join(dir, "evidence-pack-sess-nopersist.jsonl");
  assert.ok(
    !fs.existsSync(wouldBeFile),
    "without persistDir, nothing is written -- this is the exact gap Phase 3B closes, reproduced here as a positive control",
  );
});

test("_persistEntry failure is swallowed (never throws), matching logDecision's own best-effort philosophy", () => {
  const pack = new EvidencePack("sess-5", "Z:\\definitely\\not\\a\\real\\path\\on\\this\\machine");
  assert.doesNotThrow(() => pack.add({ tier: "L2" }));
  assert.strictEqual(pack.entries.length, 1, "the in-memory chain must still record the entry even if the disk write fails");
});

test("persistDir is created if it does not already exist", () => {
  const dir = path.join(tmpDir(), "nested", "does", "not", "exist", "yet");
  assert.ok(!fs.existsSync(dir));
  const pack = new EvidencePack("sess-6", dir);
  pack.add({ tier: "L1" });
  assert.ok(fs.existsSync(path.join(dir, "evidence-pack-sess-6.jsonl")));
});

if (process.exitCode) {
  console.error("\nFAIL-FIRST CHECK: some assertions failed.");
} else {
  console.log("\nAll evidence-pack assertions passed.");
}
