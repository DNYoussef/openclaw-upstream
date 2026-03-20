#!/usr/bin/env node
// test-agent.mjs -- Connect to a remote OpenClaw gateway and run a test agent prompt.
//
// Usage:
//   OPENCLAW_GATEWAY_TOKEN=<token> node guardspine/test-agent.mjs [prompt]
//
// Or set the token inline:
//   node guardspine/test-agent.mjs --token <token> "What is 2+2?"
//
// Requirements: npm install ws  (or run from the openclaw-upstream repo root)

import { randomUUID } from "node:crypto";
import { WebSocket } from "ws";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const GATEWAY_URL =
  process.env.OPENCLAW_GATEWAY_URL || "wss://openclaw-production-e5a2.up.railway.app";

const PROTOCOL_VERSION = 3;
const CONNECT_TIMEOUT_MS = 15_000;
const AGENT_TIMEOUT_MS = 120_000;

// Parse CLI args
let token = process.env.OPENCLAW_GATEWAY_TOKEN || "";
let prompt = "Say hello and confirm you are running.";
const args = process.argv.slice(2);
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--token" && args[i + 1]) {
    token = args[++i];
  } else if (!args[i].startsWith("--")) {
    prompt = args[i];
  }
}

if (!token) {
  console.error("ERROR: No gateway token. Set OPENCLAW_GATEWAY_TOKEN or pass --token <token>");
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Wait for a single WS message matching a predicate. */
function onceMessage(ws, predicate, timeoutMs = 10_000) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("onceMessage timeout")), timeoutMs);
    const onClose = (code, reason) => {
      clearTimeout(timer);
      ws.off("message", onMsg);
      reject(new Error(`WebSocket closed (${code}): ${reason ? reason.toString() : "no reason"}`));
    };
    const onMsg = (data) => {
      try {
        const obj = JSON.parse(data.toString());
        if (predicate(obj)) {
          clearTimeout(timer);
          ws.off("message", onMsg);
          ws.off("close", onClose);
          resolve(obj);
        }
      } catch {
        // ignore parse errors
      }
    };
    ws.on("message", onMsg);
    ws.once("close", onClose);
  });
}

/** Collect ALL messages until a final predicate fires or timeout. */
function collectMessages(ws, finalPredicate, timeoutMs = AGENT_TIMEOUT_MS) {
  return new Promise((resolve, reject) => {
    const collected = [];
    const timer = setTimeout(() => {
      ws.off("message", onMsg);
      ws.off("close", onClose);
      reject(
        new Error(
          `collectMessages timeout after ${timeoutMs}ms (got ${collected.length} messages)`,
        ),
      );
    }, timeoutMs);
    const onClose = (code, reason) => {
      clearTimeout(timer);
      ws.off("message", onMsg);
      reject(new Error(`WebSocket closed (${code}): ${reason ? reason.toString() : "no reason"}`));
    };
    const onMsg = (data) => {
      try {
        const obj = JSON.parse(data.toString());
        collected.push(obj);
        if (finalPredicate(obj)) {
          clearTimeout(timer);
          ws.off("message", onMsg);
          ws.off("close", onClose);
          resolve(collected);
        }
      } catch {
        // ignore
      }
    };
    ws.on("message", onMsg);
    ws.once("close", onClose);
  });
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  console.log(`Connecting to ${GATEWAY_URL} ...`);

  const ws = new WebSocket(GATEWAY_URL);

  // 1. Wait for open
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("WebSocket open timeout")), CONNECT_TIMEOUT_MS);
    ws.once("open", () => {
      clearTimeout(timer);
      resolve();
    });
    ws.once("error", (err) => {
      clearTimeout(timer);
      reject(err);
    });
  });
  console.log("WebSocket open.");

  // 2. Wait for connect.challenge
  const challenge = await onceMessage(
    ws,
    (o) => o.type === "event" && o.event === "connect.challenge",
    CONNECT_TIMEOUT_MS,
  );
  const nonce = challenge.payload?.nonce;
  if (typeof nonce !== "string" || !nonce.trim()) {
    throw new Error("Invalid or missing nonce in connect.challenge");
  }
  console.log(`Got connect.challenge nonce: ${nonce.slice(0, 8)}...`);

  // 3. Send connect request (operator, token-only, no device identity)
  //    The test suite confirms: { role: "operator", token, device: null } works.
  const connectId = randomUUID();
  const connectFrame = {
    type: "req",
    id: connectId,
    method: "connect",
    params: {
      minProtocol: PROTOCOL_VERSION,
      maxProtocol: PROTOCOL_VERSION,
      client: {
        id: "gateway-client",
        displayName: "guardspine-test",
        version: "0.1.0",
        platform: process.platform,
        mode: "backend",
      },
      caps: [],
      role: "operator",
      scopes: ["operator.admin"],
      auth: { token },
    },
  };
  ws.send(JSON.stringify(connectFrame));
  console.log("Sent connect request.");

  // 4. Wait for connect response
  const connectRes = await onceMessage(
    ws,
    (o) => o.type === "res" && o.id === connectId,
    CONNECT_TIMEOUT_MS,
  );
  if (!connectRes.ok) {
    console.error("Connect FAILED:", JSON.stringify(connectRes.error, null, 2));
    ws.close();
    process.exit(1);
  }
  console.log("Connected! hello-ok received.");
  if (connectRes.payload?.snapshot?.server) {
    console.log("  Server version:", connectRes.payload.snapshot.server?.version || "unknown");
  }

  // 5. Send agent request
  const agentReqId = randomUUID();
  const idempotencyKey = `guardspine-test-${Date.now()}`;
  const agentFrame = {
    type: "req",
    id: agentReqId,
    method: "agent",
    params: {
      message: prompt,
      sessionKey: "main",
      idempotencyKey,
    },
  };
  console.log(`\nSending agent request: "${prompt}"`);
  console.log(`  idempotencyKey: ${idempotencyKey}`);

  // Start collecting responses before sending (to avoid race)
  const responsePromise = collectMessages(
    ws,
    (o) => o.type === "res" && o.id === agentReqId && o.payload?.status !== "accepted",
    AGENT_TIMEOUT_MS,
  );

  ws.send(JSON.stringify(agentFrame));

  // 6. Collect all messages until final response
  let messages;
  try {
    messages = await responsePromise;
  } catch (err) {
    console.error("\nAgent request failed:", err.message);
    ws.close();
    process.exit(1);
  }

  // 7. Print results
  console.log(`\nReceived ${messages.length} message(s):\n`);

  for (const msg of messages) {
    if (msg.type === "res" && msg.id === agentReqId) {
      if (msg.payload?.status === "accepted") {
        console.log("[accepted] runId:", msg.payload.runId);
      } else {
        console.log("[final response]", msg.ok ? "OK" : "ERROR");
        console.log(JSON.stringify(msg.payload || msg.error, null, 2));
      }
    } else if (msg.type === "event") {
      console.log(`[event] ${msg.event}:`, JSON.stringify(msg.payload).slice(0, 200));
    } else {
      console.log(`[${msg.type || "unknown"}]`, JSON.stringify(msg).slice(0, 200));
    }
  }

  // 8. Clean up
  ws.close();
  console.log("\nDone.");
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
