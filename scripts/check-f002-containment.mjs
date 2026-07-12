#!/usr/bin/env node

import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const AUTH_PATH = "guardspine/auth/auth-profiles.json";
const BAKED_AUTH = ["auth-profiles", "json", "baked"].join(".");
const ANTHROPIC_SECRET = /sk-ant-(?:oat|ort|api)[A-Za-z0-9_-]{20,}/;
const JWT_SECRET = /eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}/;
const AUTH_PROFILE_SCHEMA = /"(?:profiles|access|refresh|anthropic:setup-token)"\s*:/;

function git(root, ...args) {
  return execFileSync("git", args, { cwd: root, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
}

function exactIgnore(root, name) {
  const file = path.join(root, name);
  if (!fs.existsSync(file)) {
    return false;
  }
  return fs
    .readFileSync(file, "utf8")
    .split(/\r?\n/)
    .some((line) => line.trim() === AUTH_PATH);
}

function scansForProfileJwt(relative) {
  return !/(^|\/)(?:test|tests|fixtures?)(\/|$)|\.test\.[^/]+$/.test(relative);
}

function hasAuthSecret(text) {
  return ANTHROPIC_SECRET.test(text) || (JWT_SECRET.test(text) && AUTH_PROFILE_SCHEMA.test(text));
}

function withoutAllowlistedLines(text) {
  const lines = text.split(/\r?\n/);
  return lines
    .filter(
      (line, index) =>
        !line.includes("pragma: allowlist secret") &&
        !lines[index - 1]?.includes("pragma: allowlist next-line secret"),
    )
    .join("\n");
}

function hasTrackedAuthSecret(relative, text) {
  const candidate = withoutAllowlistedLines(text);
  return (
    ANTHROPIC_SECRET.test(candidate) ||
    (scansForProfileJwt(relative) &&
      JWT_SECRET.test(candidate) &&
      AUTH_PROFILE_SCHEMA.test(candidate))
  );
}

function exposedHistory(root) {
  const commits = git(root, "rev-list", "--all").trim().split(/\r?\n/).filter(Boolean);
  if (!commits.length) {
    return 0;
  }
  const specs = commits.map((commit) => `${commit}:${AUTH_PATH}`).join("\n") + "\n";
  const objects = execFileSync("git", ["cat-file", "--batch-check=%(objectname) %(objecttype)"], {
    cwd: root,
    encoding: "utf8",
    input: specs,
    maxBuffer: 64 * 1024 * 1024,
  })
    .trim()
    .split(/\r?\n/);
  const counts = new Map();
  for (const line of objects) {
    const [object, type] = line.split(" ");
    if (type === "blob") {
      counts.set(object, (counts.get(object) ?? 0) + 1);
    }
  }
  let exposed = 0;
  for (const [object, count] of counts) {
    const content = git(root, "cat-file", "blob", object);
    if (hasAuthSecret(content)) {
      exposed += count;
    }
  }
  return exposed;
}

function inspect(root) {
  const tracked = git(root, "ls-files", "-z").split("\0").filter(Boolean);
  const failures = [];
  if (tracked.includes(AUTH_PATH)) {
    failures.push("F002_TRACKED_AUTH");
  }
  if (!exactIgnore(root, ".gitignore")) {
    failures.push("F002_GITIGNORE_MISSING");
  }
  if (!exactIgnore(root, ".dockerignore")) {
    failures.push("F002_DOCKERIGNORE_MISSING");
  }

  let baked = false;
  let secret = false;
  for (const relative of tracked) {
    const file = path.join(root, relative);
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
      continue;
    }
    const data = fs.readFileSync(file);
    if (data.includes(0)) {
      continue;
    }
    const text = data.toString("utf8");
    baked ||= text.includes(BAKED_AUTH);
    secret ||= hasTrackedAuthSecret(relative, text);
  }
  if (baked) {
    failures.push("F002_BAKED_AUTH");
  }
  if (secret) {
    failures.push("F002_SECRET_SHAPE");
  }

  const history = exposedHistory(root);
  return { failures, history };
}

function commit(root, message) {
  git(root, "add", "-A");
  git(root, "commit", "-m", message);
}

function selfTest() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "f002-containment-"));
  try {
    git(root, "init", "-q");
    git(root, "config", "user.email", "f002@example.invalid");
    git(root, "config", "user.name", "F-002 canary");
    fs.mkdirSync(path.join(root, "guardspine", "auth"), { recursive: true });
    fs.writeFileSync(path.join(root, ".gitignore"), `${AUTH_PATH}\n`);
    const access = ["sk-ant-oat", "CANARY_12345678901234567890"].join("_");
    const token = ["eyJcanaryHeader1", "eyJcanaryPayload2", "canarySignature3"].join(".");
    assert.equal(hasAuthSecret(JSON.stringify({ profiles: { canary: { token } } })), true);
    assert.equal(hasAuthSecret(JSON.stringify({ unrelatedHeader: token })), false);
    fs.writeFileSync(path.join(root, AUTH_PATH), `${JSON.stringify({ access, token })}\n`);
    fs.writeFileSync(
      path.join(root, "Dockerfile.railway"),
      `COPY ${AUTH_PATH} /app/${BAKED_AUTH}\n`,
    );
    git(root, "add", "-f", AUTH_PATH);
    commit(root, "red canary");

    const red = inspect(root);
    assert.deepEqual(red.failures, [
      "F002_TRACKED_AUTH",
      "F002_DOCKERIGNORE_MISSING",
      "F002_BAKED_AUTH",
      "F002_SECRET_SHAPE",
    ]);
    assert.equal(red.history, 1);

    fs.mkdirSync(path.join(root, "src"));
    fs.writeFileSync(path.join(root, "src", "provider.test.ts"), `const token = "${access}";\n`);
    fs.writeFileSync(path.join(root, ".dockerignore"), `${AUTH_PATH}\n`);
    fs.rmSync(path.join(root, AUTH_PATH));
    fs.writeFileSync(path.join(root, "Dockerfile.railway"), "FROM scratch\n");
    commit(root, "test path canary");

    const testPathRed = inspect(root);
    assert.deepEqual(testPathRed.failures, ["F002_SECRET_SHAPE"]);
    assert.equal(testPathRed.history, 1);

    fs.writeFileSync(
      path.join(root, "src", "provider.test.ts"),
      `// pragma: allowlist next-line secret\nconst token = "${access}";\n`,
    );
    commit(root, "contained head");

    const green = inspect(root);
    assert.deepEqual(green.failures, []);
    assert.equal(green.history, 1, "green HEAD must still report exposed history");
    console.log("F-002_SELF_TEST_OK red=5 green=1 history_exposed=1");
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

if (process.argv.includes("--self-test")) {
  selfTest();
} else {
  const root = git(process.cwd(), "rev-parse", "--show-toplevel").trim();
  const result = inspect(root);
  if (result.failures.length) {
    console.error(`F-002_HEAD_UNCONTAINED failures=${result.failures.join(",")}`);
  } else {
    console.log("F-002_HEAD_CONTAINED");
  }
  console.log(`F-002_HISTORY_EXPOSED count=${result.history}`);
  console.log("F-002_BLOCKED_EXTERNAL provider_revocation,image_cache_invalidation");
  if (result.failures.length) {
    process.exitCode = 1;
  }
}
