const assert = require("assert");
const fs = require("fs");
const path = require("path");
const {
  findBridgeReferences,
  checkOwnCouncilIsWired,
  checkGovernanceRouting,
} = require("./check-governance-routing.cjs");

function test(name, fn) {
  try {
    fn();
    console.log("PASS:", name);
  } catch (e) {
    console.error("FAIL:", name, "--", e.message);
    process.exitCode = 1;
  }
}

const CLEAN_SAMPLE = `
function runCouncilReview(endpoint, toolName, params, reason) {
  return litellmGenerate(endpoint, 'haiku', 'prompt', 1000);
}
let _runCouncilReview = runCouncilReview;
api.on(
  "before_tool_call",
  async (event) => {
    const councilResult = await _runCouncilReview(councilEndpoint, toolName, params, risk.reason);
  }
);
`;

test("POSITIVE CONTROL: a real bridge reference (connector.py) IS detected -- proves this check can actually fail, not just always pass", () => {
  const withBridge =
    CLEAN_SAMPLE +
    '\nconst { spawn } = require("child_process");\nspawn("python", ["connector.py"]);';
  const hits = findBridgeReferences(withBridge);
  assert.ok(
    hits.length >= 2,
    `expected at least connector.py + child_process to be caught, got: ${JSON.stringify(hits)}`,
  );
});

test("POSITIVE CONTROL: a reference to openclaw-hardening in real code (not a comment) is caught", () => {
  const withRef = CLEAN_SAMPLE + '\nconst OPENCLAW_ROOT = "../openclaw-hardening";';
  const hits = findBridgeReferences(withRef);
  assert.ok(hits.some((h) => /openclaw-hardening/i.test(h)));
});

test("clean source (no bridge references) reports zero hits", () => {
  const hits = findBridgeReferences(CLEAN_SAMPLE);
  assert.deepStrictEqual(hits, []);
});

test("checkOwnCouncilIsWired confirms the real council function is defined, aliased, and called from the hook", () => {
  const result = checkOwnCouncilIsWired(CLEAN_SAMPLE);
  assert.strictEqual(result.wired, true);
});

test("POSITIVE CONTROL: checkOwnCouncilIsWired correctly reports NOT wired if the hook never calls it", () => {
  const notWired = `
function runCouncilReview() {}
let _runCouncilReview = runCouncilReview;
api.on("before_tool_call", async (event) => { /* does not call council at all */ });
`;
  const result = checkOwnCouncilIsWired(notWired);
  assert.strictEqual(result.wired, false);
});

test("checkGovernanceRouting: clean+wired source passes overall", () => {
  const result = checkGovernanceRouting(CLEAN_SAMPLE);
  assert.strictEqual(result.ok, true);
});

test("checkGovernanceRouting: a bridge reference alone fails overall, even if own council is also wired", () => {
  const withBridge = CLEAN_SAMPLE + '\nrequire("child_process").execSync("python connector.py");';
  const result = checkGovernanceRouting(withBridge);
  assert.strictEqual(result.ok, false);
  assert.ok(result.bridgeReferences.length > 0);
});

test("POSITIVE CONTROL (audit round 1): worker_threads is caught, not just child_process", () => {
  const withWorker =
    CLEAN_SAMPLE +
    '\nconst { Worker } = require("worker_threads");\nnew Worker("./run-connector.js");';
  const hits = findBridgeReferences(withWorker);
  assert.ok(hits.some((h) => /worker_threads/.test(h)));
});

test("POSITIVE CONTROL (audit round 1): common subprocess-wrapper libraries (execa, cross-spawn) are caught", () => {
  const withExeca =
    CLEAN_SAMPLE + '\nconst execa = require("execa");\nexeca("python", ["connector.py"]);';
  assert.ok(findBridgeReferences(withExeca).some((h) => /execa/.test(h)));
  const withCrossSpawn = CLEAN_SAMPLE + '\nconst spawn = require("cross-spawn");';
  assert.ok(findBridgeReferences(withCrossSpawn).some((h) => /cross-spawn/.test(h)));
});

test('POSITIVE CONTROL (audit round 1): a bare "python" mention in real code is caught even without a specific subprocess library named', () => {
  const hits = findBridgeReferences(CLEAN_SAMPLE + '\nconst runtime = "python3";');
  assert.ok(hits.some((h) => /python/i.test(h)));
});

test("audit round 1 fix: a bridge keyword appearing ONLY inside a comment does not count as a real reference", () => {
  const onlyInComment =
    CLEAN_SAMPLE +
    "\n// TODO: maybe wire up connector.py and openclaw-hardening someday, low priority";
  const hits = findBridgeReferences(onlyInComment);
  assert.deepStrictEqual(
    hits,
    [],
    `a comment-only mention must not count as a live reference, got: ${JSON.stringify(hits)}`,
  );
});

test("audit round 1 fix: a bridge keyword appearing only inside a comment does NOT let a real reference hide by being commented out (still caught if it also exists as real code)", () => {
  const mixed =
    CLEAN_SAMPLE +
    '\n// old approach:\n// spawn("python", ["connector.py"]);\nrequire("child_process").spawn("python", ["connector.py"]); // still live';
  const hits = findBridgeReferences(mixed);
  assert.ok(
    hits.length > 0,
    "the real, uncommented invocation must still be caught even though a comment nearby also mentions it",
  );
});

test("audit round 1 fix: checkOwnCouncilIsWired ignores a call to _runCouncilReview that exists only in a comment near before_tool_call", () => {
  const fakeWiring = `
function runCouncilReview() {}
let _runCouncilReview = runCouncilReview;
api.on("before_tool_call", async (event) => {
  // old code used to do: _runCouncilReview(endpoint, tool, params, reason);
  // but this hook no longer actually calls it
});
`;
  const result = checkOwnCouncilIsWired(fakeWiring);
  assert.strictEqual(
    result.wired,
    false,
    "a call appearing only in a comment must not count as real wiring",
  );
});

test("audit round 1 fix: const/var indirection (not just let) is recognized", () => {
  const withConst = CLEAN_SAMPLE.replace("let _runCouncilReview", "const _runCouncilReview");
  assert.strictEqual(checkOwnCouncilIsWired(withConst).hasIndirection, true);
  const withVar = CLEAN_SAMPLE.replace("let _runCouncilReview", "var _runCouncilReview");
  assert.strictEqual(checkOwnCouncilIsWired(withVar).hasIndirection, true);
});

test("THE REAL FILE: the actual live plugin.js passes this check today (this is the state Phase 3A documents, not just a hypothetical)", () => {
  const pluginPath = path.join(__dirname, "..", "extensions", "guardspine", "plugin.js");
  const source = fs.readFileSync(pluginPath, "utf8");
  const result = checkGovernanceRouting(source);
  assert.deepStrictEqual(
    result.bridgeReferences,
    [],
    `plugin.js unexpectedly references the dormant bridge: ${JSON.stringify(result.bridgeReferences)}`,
  );
  assert.strictEqual(
    result.ownCouncil.wired,
    true,
    `plugin.js's own council is not wired as expected: ${JSON.stringify(result.ownCouncil)}`,
  );
});

test("audit round 2 fix: a URL (http:// or https://) on a line does not get mistaken for a comment start, hiding real code after it", () => {
  // plugin.js does exactly this shape throughout (building LiteLLM/Discord/
  // Slack URLs) -- a naive //.*$ strip would truncate the rest of the line,
  // silently hiding a real bridge reference or hook call that followed.
  const withUrlThenRealCode =
    CLEAN_SAMPLE +
    '\nconst url = "https://discord.com/api/v10"; require("child_process").spawn("python", ["connector.py"]);';
  const hits = findBridgeReferences(withUrlThenRealCode);
  assert.ok(
    hits.length > 0,
    "a real bridge reference after a URL on the same line must still be caught, not silently truncated away",
  );
});

test("audit round 2 fix: a URL does not prevent a REAL trailing comment on the same line from still being stripped", () => {
  const withUrlThenComment =
    CLEAN_SAMPLE +
    '\nconst url = "https://discord.com/api"; // this really is just a comment, mentions connector.py';
  const hits = findBridgeReferences(withUrlThenComment);
  assert.deepStrictEqual(
    hits,
    [],
    "the trailing real comment must still be stripped even though the line also contains a URL",
  );
});

test("audit round 2 fix: an indirection assigned from a renamed/mock/disabled variant is NOT mistaken for the real wiring", () => {
  const withMock = CLEAN_SAMPLE.replace(
    "let _runCouncilReview = runCouncilReview;",
    "let _runCouncilReview = runCouncilReviewMock;",
  );
  assert.strictEqual(
    checkOwnCouncilIsWired(withMock).hasIndirection,
    false,
    "aliasing from a differently-named function must not count as wiring the real one",
  );
});

test("audit round 2 fix: a call to _runCouncilReview inside a DIFFERENT hook does not falsely satisfy before_tool_call's wiring", () => {
  const wrongHook = `
function runCouncilReview() {}
let _runCouncilReview = runCouncilReview;
api.on("before_tool_call", async (event) => {
  // neutered: does nothing
});
api.on("after_tool_call", async (event) => {
  await _runCouncilReview(endpoint, tool, params, reason);
});
`;
  const result = checkOwnCouncilIsWired(wrongHook);
  assert.strictEqual(
    result.hookCallsIt,
    false,
    "a call inside a later, different hook must not count as before_tool_call calling it",
  );
});

test("audit round 2 fix: whitespace before the call parenthesis (e.g. from a formatter) does not cause a false failure", () => {
  const withSpace = CLEAN_SAMPLE.replace("_runCouncilReview(", "_runCouncilReview (");
  assert.strictEqual(checkOwnCouncilIsWired(withSpace).hookCallsIt, true);
});

test('audit round 3 fix: an EARLIER, unrelated mention of "before_tool_call" (e.g. a doc comment listing hook names, exactly like plugin.js\'s real header) does not shift the search window away from the actual registration', () => {
  const withEarlyMention = `
/**
 * Integration points:
 * - before_tool_call: risk gate with council + approval
 */
function runCouncilReview() {}
let _runCouncilReview = runCouncilReview;
api.on("before_tool_call", async (event) => {
  await _runCouncilReview(endpoint, tool, params, reason);
});
`;
  const result = checkOwnCouncilIsWired(withEarlyMention);
  assert.strictEqual(
    result.hookCallsIt,
    true,
    "an earlier mention of the hook name elsewhere in the file must not break finding the real registration",
  );
});

test("audit round 3 fix: a differently-formatted NEXT hook registration (extra whitespace before the paren) still bounds the search correctly", () => {
  const withSpacedNextHook = `
function runCouncilReview() {}
let _runCouncilReview = runCouncilReview;
api.on("before_tool_call", async (event) => {
  // neutered: does nothing
});
api.on ("after_tool_call", async (event) => {
  await _runCouncilReview(endpoint, tool, params, reason);
});
`;
  const result = checkOwnCouncilIsWired(withSpacedNextHook);
  assert.strictEqual(
    result.hookCallsIt,
    false,
    "a call inside a later hook (even one with unusual spacing before its paren) must still be excluded from the boundary",
  );
});

test("audit round 4 fix: a template-literal-style hook registration (backticks instead of quotes) is still recognized", () => {
  const withBackticks = CLEAN_SAMPLE.replace('"before_tool_call"', "`before_tool_call`");
  const result = checkOwnCouncilIsWired(withBackticks);
  assert.strictEqual(result.hookCallsIt, true);
});

if (process.exitCode) {
  console.error(
    "\nFAIL-FIRST CHECK: some assertions failed (expected right now -- lib/check-governance-routing.js does not exist yet, or the file it checks doesn't match reality).",
  );
} else {
  console.log("\nAll governance-routing assertions passed.");
}
