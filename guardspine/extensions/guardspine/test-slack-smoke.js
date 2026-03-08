/**
 * Smoke tests for GuardSpine Slack integration.
 * Run: node test-slack-smoke.js
 * No external test framework required -- uses built-in assert module.
 */

const assert = require("assert");
const https = require("https");
const http = require("http");

// ---------------------------------------------------------------
// Stub helpers: intercept https.request before plugin loads
// ---------------------------------------------------------------

let _interceptedRequests = [];
let _mockResponse = { statusCode: 200, body: '{"ok":true}' };

const _origHttpsRequest = https.request;
const _origHttpRequest = http.request;

function installHttpsStub() {
  _interceptedRequests = [];
  https.request = function stubRequest(options, callback) {
    _interceptedRequests.push({ module: "https", options });
    const fakeRes = new (require("events").EventEmitter)();
    fakeRes.statusCode = _mockResponse.statusCode;
    if (callback) {
      process.nextTick(() => {
        callback(fakeRes);
        process.nextTick(() => {
          fakeRes.emit("data", _mockResponse.body);
          fakeRes.emit("end");
        });
      });
    }
    return {
      on(evt, fn) {
        if (evt === "timeout" && _mockResponse.timeout) {
          process.nextTick(fn);
        }
      },
      write() {},
      end() {},
      destroy() {},
    };
  };
  http.request = function stubRequest(options, callback) {
    _interceptedRequests.push({ module: "http", options });
    const fakeRes = new (require("events").EventEmitter)();
    fakeRes.statusCode = _mockResponse.statusCode;
    if (callback) {
      process.nextTick(() => {
        callback(fakeRes);
        process.nextTick(() => {
          fakeRes.emit("data", _mockResponse.body);
          fakeRes.emit("end");
        });
      });
    }
    return {
      on(evt, fn) {
        if (evt === "timeout" && _mockResponse.timeout) {
          process.nextTick(fn);
        }
      },
      write() {},
      end() {},
      destroy() {},
    };
  };
}

function restoreHttp() {
  https.request = _origHttpsRequest;
  http.request = _origHttpRequest;
}

function setMockResponse(opts) {
  _mockResponse = { statusCode: 200, body: '{"ok":true}', timeout: false, ...opts };
}

// Install stubs BEFORE requiring the plugin so its https ref is our stub
installHttpsStub();

const plugin = require("./plugin.js");
const {
  buildApprovalBlocks,
  slackApiCall,
  slackWebhookPost,
  sendSlackApproval,
  checkSlackReaction,
  emitEvidenceNotification,
  checkSelfApproval,
  resetForTests,
  slackApprovalMessages,
} = plugin.__internal;

// ---------------------------------------------------------------
// Test runner
// ---------------------------------------------------------------

let passed = 0;
let failed = 0;
const results = [];

async function test(name, fn) {
  try {
    await fn();
    passed++;
    results.push({ name, status: "PASS" });
    console.log(`  PASS  ${name}`);
  } catch (e) {
    failed++;
    results.push({ name, status: "FAIL", error: e.message });
    console.log(`  FAIL  ${name}`);
    console.log(`        ${e.message}`);
  }
}

// ---------------------------------------------------------------
// Tests
// ---------------------------------------------------------------

async function runAll() {
  console.log("\n=== GuardSpine Slack Smoke Tests ===\n");

  // ---------------------------
  // buildApprovalBlocks
  // ---------------------------

  await test("buildApprovalBlocks returns valid Block Kit array", () => {
    const blocks = buildApprovalBlocks(
      "config_write",
      { path: "/etc/passwd" },
      "system security modification",
      "abc12345",
      "2026-03-08T12:00:00Z",
      null,
    );
    assert.ok(Array.isArray(blocks), "blocks should be an array");
    assert.ok(blocks.length >= 4, "should have at least 4 blocks");
    // Header block
    assert.strictEqual(blocks[0].type, "header");
    assert.strictEqual(blocks[0].text.type, "plain_text");
    assert.ok(blocks[0].text.text.includes("L4 Approval"), "header mentions L4");
    // Section with fields
    assert.strictEqual(blocks[1].type, "section");
    assert.ok(Array.isArray(blocks[1].fields), "section has fields");
    // Actions block with approve/deny buttons
    const actionsBlock = blocks.find((b) => b.type === "actions");
    assert.ok(actionsBlock, "should have an actions block");
    assert.strictEqual(actionsBlock.elements.length, 2, "two buttons: approve + deny");
    assert.strictEqual(actionsBlock.elements[0].style, "primary");
    assert.strictEqual(actionsBlock.elements[1].style, "danger");
    // Context block
    const ctxBlock = blocks.find((b) => b.type === "context");
    assert.ok(ctxBlock, "should have a context block");
  });

  await test("buildApprovalBlocks includes council info when provided", () => {
    const councilResult = {
      verdict: "DEADLOCK",
      pass_count: 1,
      fail_count: 1,
      escalate_count: 1,
      votes: [{ auditor: "A", model: "qwen3:8b", verdict: "PASS" }],
    };
    const blocks = buildApprovalBlocks(
      "bash",
      { command: "rm -rf /" },
      "destructive delete",
      "def67890",
      "2026-03-08T13:00:00Z",
      councilResult,
    );
    const councilSection = blocks.find(
      (b) => b.type === "section" && b.text && b.text.text.includes("Council"),
    );
    assert.ok(councilSection, "should have council section");
    assert.ok(councilSection.text.text.includes("DEADLOCK"), "shows council verdict");
    assert.ok(councilSection.text.text.includes("1P"), "shows pass count");
  });

  // ---------------------------
  // slackApiCall
  // ---------------------------

  await test("slackApiCall sends POST to slack.com and parses JSON response", async () => {
    setMockResponse({ body: '{"ok":true,"ts":"1234567890.123456","channel":"C123"}' });
    _interceptedRequests = [];
    const result = await slackApiCall("chat.postMessage", "xoxb-fake-token", {
      channel: "C123",
      text: "hello",
    });
    assert.strictEqual(result.ok, true);
    assert.strictEqual(result.ts, "1234567890.123456");
    assert.ok(_interceptedRequests.length > 0, "should have made a request");
    const req = _interceptedRequests[0];
    assert.strictEqual(req.options.hostname, "slack.com");
    assert.strictEqual(req.options.path, "/api/chat.postMessage");
    assert.ok(req.options.headers.Authorization.includes("xoxb-fake-token"));
  });

  await test("slackApiCall returns {ok:false} on JSON parse error", async () => {
    setMockResponse({ body: "not json at all" });
    const result = await slackApiCall("chat.postMessage", "xoxb-fake", { channel: "C1" });
    assert.strictEqual(result.ok, false);
    assert.strictEqual(result.error, "json_parse_error");
  });

  await test("slackApiCall returns {ok:false} on timeout (no exception)", async () => {
    // Simulate timeout by having the stub fire the timeout event
    _interceptedRequests = [];
    const origReq = https.request;
    https.request = function timeoutStub(options, callback) {
      _interceptedRequests.push({ module: "https", options });
      const handlers = {};
      return {
        on(evt, fn) {
          handlers[evt] = fn;
          if (evt === "timeout") process.nextTick(fn);
        },
        write() {},
        end() {},
        destroy() {
          if (handlers.error) {
            /* noop */
          }
        },
      };
    };
    const result = await slackApiCall("chat.postMessage", "xoxb-fake", { channel: "C1" });
    assert.strictEqual(result.ok, false);
    assert.strictEqual(result.error, "timeout");
    https.request = origReq;
    installHttpsStub();
  });

  // ---------------------------
  // slackWebhookPost
  // ---------------------------

  await test("slackWebhookPost sends to webhook URL and returns ok on 200", async () => {
    setMockResponse({ statusCode: 200, body: "ok" });
    _interceptedRequests = [];
    const result = await slackWebhookPost("https://hooks.slack.com/services/T00/B00/xxxx", {
      text: "test message",
    });
    assert.strictEqual(result.ok, true);
    assert.ok(_interceptedRequests.length > 0);
    assert.strictEqual(_interceptedRequests[0].options.hostname, "hooks.slack.com");
  });

  await test("slackWebhookPost returns ok:false on non-2xx status", async () => {
    setMockResponse({ statusCode: 500, body: "internal error" });
    const result = await slackWebhookPost("https://hooks.slack.com/services/T00/B00/xxxx", {
      text: "test",
    });
    assert.strictEqual(result.ok, false);
  });

  // ---------------------------
  // sendSlackApproval
  // ---------------------------

  await test("sendSlackApproval uses bot token + channel when both present", async () => {
    resetForTests();
    setMockResponse({ body: '{"ok":true,"ts":"111.222","channel":"C-APPROVAL"}' });
    _interceptedRequests = [];
    const cfg = {
      slackBotToken: "xoxb-test",
      slackWebhookUrl: "https://hooks.slack.com/x",
      slackApprovalChannel: "C-APPROVAL",
    };
    const result = await sendSlackApproval(
      cfg,
      "bash",
      { command: "rm -rf /" },
      "destructive",
      "appr-001",
      "2026-03-08T14:00:00Z",
      null,
    );
    assert.strictEqual(result.ok, true);
    assert.strictEqual(result.method, "bot_api");
    // Should have stored approval message for reaction checking
    assert.ok(slackApprovalMessages.has("appr-001"), "should store message for reaction polling");
    const stored = slackApprovalMessages.get("appr-001");
    assert.strictEqual(stored.ts, "111.222");
  });

  await test("sendSlackApproval falls back to webhook when bot token missing", async () => {
    resetForTests();
    setMockResponse({ statusCode: 200, body: "ok" });
    _interceptedRequests = [];
    const cfg = {
      slackBotToken: null,
      slackWebhookUrl: "https://hooks.slack.com/services/T/B/xxx",
      slackApprovalChannel: null,
    };
    const result = await sendSlackApproval(
      cfg,
      "config_write",
      {},
      "credential access",
      "appr-002",
      "2026-03-08T15:00:00Z",
      null,
    );
    assert.strictEqual(result.ok, true);
    assert.strictEqual(result.method, "webhook");
  });

  await test("sendSlackApproval returns error when no credentials at all", async () => {
    resetForTests();
    const cfg = { slackBotToken: null, slackWebhookUrl: null, slackApprovalChannel: null };
    const result = await sendSlackApproval(
      cfg,
      "bash",
      {},
      "test",
      "appr-003",
      "2026-03-08T16:00:00Z",
      null,
    );
    assert.strictEqual(result.ok, false);
    assert.strictEqual(result.error, "no_slack_credentials");
  });

  // ---------------------------
  // checkSlackReaction
  // ---------------------------

  await test("checkSlackReaction returns APPROVED on thumbsup", async () => {
    resetForTests();
    slackApprovalMessages.set("react-001", { ts: "100.200", channel: "C-TEST" });
    setMockResponse({
      body: JSON.stringify({
        ok: true,
        message: { reactions: [{ name: "thumbsup", count: 1, users: ["U123"] }] },
      }),
    });
    const result = await checkSlackReaction("react-001", "xoxb-token");
    assert.ok(result, "should return a result");
    assert.strictEqual(result.approved, true);
    assert.strictEqual(result.method, "slack_reaction");
    // Should have cleaned up the stored message
    assert.ok(!slackApprovalMessages.has("react-001"), "should clean up after approval");
  });

  await test("checkSlackReaction returns DENIED on thumbsdown", async () => {
    resetForTests();
    slackApprovalMessages.set("react-002", { ts: "100.300", channel: "C-TEST" });
    setMockResponse({
      body: JSON.stringify({
        ok: true,
        message: { reactions: [{ name: "thumbsdown", count: 1, users: ["U456"] }] },
      }),
    });
    const result = await checkSlackReaction("react-002", "xoxb-token");
    assert.ok(result, "should return a result");
    assert.strictEqual(result.approved, false);
    assert.ok(result.reason.includes("denied"), "reason should mention denied");
  });

  await test("checkSlackReaction returns null when no reaction yet", async () => {
    resetForTests();
    slackApprovalMessages.set("react-003", { ts: "100.400", channel: "C-TEST" });
    setMockResponse({
      body: JSON.stringify({ ok: true, message: { reactions: [] } }),
    });
    const result = await checkSlackReaction("react-003", "xoxb-token");
    assert.strictEqual(result, null);
  });

  await test("checkSlackReaction returns null when no stored message", async () => {
    resetForTests();
    const result = await checkSlackReaction("nonexistent", "xoxb-token");
    assert.strictEqual(result, null);
  });

  await test("checkSlackReaction returns null when no bot token", async () => {
    resetForTests();
    slackApprovalMessages.set("react-004", { ts: "100.500", channel: "C-TEST" });
    const result = await checkSlackReaction("react-004", null);
    assert.strictEqual(result, null);
  });

  await test("checkSlackReaction handles +1 alias for thumbsup", async () => {
    resetForTests();
    slackApprovalMessages.set("react-005", { ts: "100.600", channel: "C-TEST" });
    setMockResponse({
      body: JSON.stringify({
        ok: true,
        message: { reactions: [{ name: "+1", count: 2, users: ["U789", "U012"] }] },
      }),
    });
    const result = await checkSlackReaction("react-005", "xoxb-token");
    assert.ok(result);
    assert.strictEqual(result.approved, true);
  });

  await test("checkSlackReaction handles -1 alias for thumbsdown", async () => {
    resetForTests();
    slackApprovalMessages.set("react-006", { ts: "100.700", channel: "C-TEST" });
    setMockResponse({
      body: JSON.stringify({
        ok: true,
        message: { reactions: [{ name: "-1", count: 1, users: ["U345"] }] },
      }),
    });
    const result = await checkSlackReaction("react-006", "xoxb-token");
    assert.ok(result);
    assert.strictEqual(result.approved, false);
  });

  // ---------------------------
  // emitEvidenceNotification (L2+ only)
  // ---------------------------

  await test("emitEvidenceNotification fires for L2 tier", async () => {
    _interceptedRequests = [];
    setMockResponse({ body: '{"ok":true}' });
    const cfg = {
      slackBotToken: "xoxb-test",
      slackWebhookUrl: null,
      slackApprovalChannel: "C-EVIDENCE",
    };
    emitEvidenceNotification(cfg, "bash", "L2", "sha256:abcdef1234567890", 5, false);
    // Give the async fire-and-forget a tick to run
    await new Promise((r) => setTimeout(r, 50));
    assert.ok(_interceptedRequests.length > 0, "should have fired a Slack API call for L2");
  });

  await test("emitEvidenceNotification fires for L3 tier", async () => {
    _interceptedRequests = [];
    setMockResponse({ body: '{"ok":true}' });
    const cfg = {
      slackBotToken: "xoxb-test",
      slackWebhookUrl: null,
      slackApprovalChannel: "C-EVIDENCE",
    };
    emitEvidenceNotification(cfg, "plugin_install", "L3", "sha256:fedcba0987654321", 10, true);
    await new Promise((r) => setTimeout(r, 50));
    assert.ok(_interceptedRequests.length > 0, "should have fired a Slack API call for L3");
  });

  await test("emitEvidenceNotification uses webhook fallback when no bot token", async () => {
    _interceptedRequests = [];
    setMockResponse({ statusCode: 200, body: "ok" });
    const cfg = {
      slackBotToken: null,
      slackWebhookUrl: "https://hooks.slack.com/services/T/B/xxx",
      slackApprovalChannel: null,
    };
    emitEvidenceNotification(cfg, "bash", "L2", "sha256:1111222233334444", 3, false);
    await new Promise((r) => setTimeout(r, 50));
    assert.ok(_interceptedRequests.length > 0, "should have fired webhook for evidence");
  });

  await test("emitEvidenceNotification does nothing when no Slack credentials", async () => {
    _interceptedRequests = [];
    const cfg = { slackBotToken: null, slackWebhookUrl: null, slackApprovalChannel: null };
    emitEvidenceNotification(cfg, "bash", "L2", "sha256:0000", 1, false);
    await new Promise((r) => setTimeout(r, 50));
    assert.strictEqual(_interceptedRequests.length, 0, "should NOT fire when no credentials");
  });

  // ---------------------------
  // Error resilience: timeout returns {ok:false}, not exception
  // ---------------------------

  await test("slackApiCall timeout returns {ok:false} not an exception", async () => {
    // Already tested above, but verify no throw
    const origReq = https.request;
    https.request = function (options, callback) {
      const handlers = {};
      return {
        on(evt, fn) {
          handlers[evt] = fn;
          if (evt === "timeout") process.nextTick(fn);
        },
        write() {},
        end() {},
        destroy() {},
      };
    };
    let threw = false;
    try {
      const result = await slackApiCall("test.method", "xoxb-fake", {});
      assert.strictEqual(result.ok, false);
      assert.strictEqual(result.error, "timeout");
    } catch (e) {
      threw = true;
    }
    assert.strictEqual(threw, false, "slackApiCall should never throw, always resolve");
    https.request = origReq;
    installHttpsStub();
  });

  await test("slackWebhookPost network error returns {ok:false} not an exception", async () => {
    const origReq = https.request;
    https.request = function (options, callback) {
      const handlers = {};
      return {
        on(evt, fn) {
          handlers[evt] = fn;
          process.nextTick(() => {
            if (evt === "error") fn(new Error("ECONNREFUSED"));
          });
        },
        write() {},
        end() {},
        destroy() {},
      };
    };
    let threw = false;
    try {
      const result = await slackWebhookPost("https://hooks.slack.com/x", { text: "test" });
      assert.strictEqual(result.ok, false);
      assert.ok(result.error.includes("ECONNREFUSED"));
    } catch (e) {
      threw = true;
    }
    assert.strictEqual(threw, false, "slackWebhookPost should never throw");
    https.request = origReq;
    installHttpsStub();
  });

  // ---------------------------
  // checkSelfApproval still works (verify previous agent's work)
  // ---------------------------

  await test("checkSelfApproval is exported and functional", () => {
    assert.strictEqual(typeof checkSelfApproval, "function");
    // Set up a pending approval
    const { pendingApprovals } = plugin.__internal;
    pendingApprovals.clear();
    pendingApprovals.set("self-test-1", {
      approval_id: "self-test-1",
      requester_session_id: "session-AAA",
    });
    // Same session should be blocked
    const same = checkSelfApproval("self-test-1", "session-AAA");
    assert.strictEqual(same.blocked, true);
    assert.ok(same.reason.includes("same session"));
    // Different session should pass
    const diff = checkSelfApproval("self-test-1", "session-BBB");
    assert.strictEqual(diff.blocked, false);
    // Missing approver session should fail-closed
    const noApprover = checkSelfApproval("self-test-1", null);
    assert.strictEqual(noApprover.blocked, true);
    assert.ok(noApprover.reason.includes("fail-closed"));
    pendingApprovals.clear();
  });

  // ---------------------------
  // Summary
  // ---------------------------

  console.log(`\n=== Results: ${passed} passed, ${failed} failed ===\n`);
  restoreHttp();
  process.exit(failed > 0 ? 1 : 0);
}

runAll().catch((e) => {
  console.error("Test runner crashed:", e);
  restoreHttp();
  process.exit(1);
});
