"use strict";
const test = require("node:test");
const assert = require("node:assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");

const { register } = require("../plugin.js");

// Build a temp outreach.db with two prospects via python's stdlib sqlite3
// (better-sqlite3 is not installed here, so the plugin uses the python path).
function makeDb() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openclaw-inj-"));
  const dbPath = path.join(dir, "outreach.db");
  const py = [
    "import sqlite3, sys",
    "c = sqlite3.connect(sys.argv[1])",
    "c.execute('CREATE TABLE prospects (id TEXT, name TEXT, email TEXT, company TEXT, lane TEXT, funnel_stage TEXT, pain_bucket TEXT, signal_type TEXT)')",
    "c.execute(\"INSERT INTO prospects (id,name,email) VALUES ('real-1','Alice','a@x.com')\")",
    "c.execute(\"INSERT INTO prospects (id,name,email) VALUES ('real-2','Bob','b@x.com')\")",
    "c.commit(); c.close()",
  ].join("\n");
  const pyFile = path.join(dir, "seed.py");
  fs.writeFileSync(pyFile, py, "utf-8");
  execFileSync("python", [pyFile, dbPath]);
  return dbPath;
}

function loadTools(dbPath) {
  const tools = {};
  register({
    pluginConfig: { outreach_db_path: dbPath, discovery_tree_path: dbPath + ".notree" },
    registerTool: (factory) => {
      const t = factory();
      tools[t.name] = t;
    },
  });
  return tools;
}

test("discovery_prep: a SQL-injection prospect_id matches nothing (parameterized)", () => {
  const tools = loadTools(makeDb());
  // Classic injection: OLD concatenated code returned a row; parameterized must not.
  const res = tools.discovery_prep.execute({ prospect_id: "nope' OR '1'='1" });
  assert.ok(
    res && res.error === "Prospect not found",
    "injection payload should NOT resolve to a real prospect: " + JSON.stringify(res),
  );
});

test("outreach_query: free-form SQL filter is rejected, not concatenated", () => {
  const tools = loadTools(makeDb());
  const res = tools.outreach_query.execute({ filter: "1=1; DROP TABLE prospects" });
  assert.ok(
    res && typeof res.error === "string" && /filter must be/.test(res.error),
    "dangerous free-form filter should be rejected: " + JSON.stringify(res),
  );
});

test("outreach_query: a simple parameterized filter still works", () => {
  const tools = loadTools(makeDb());
  const res = tools.outreach_query.execute({ filter: "id = real-1", columns: "id,name" });
  assert.ok(
    res && !res.error && res.count === 1 && res.prospects[0].id === "real-1",
    "simple 'column = value' filter should return the matching row: " + JSON.stringify(res),
  );
});

test("outreach_query: a charset-valid but non-whitelisted column is rejected", () => {
  const tools = loadTools(makeDb());
  // 'password' passes the old charset check but is not an allowed prospect column.
  const res = tools.outreach_query.execute({ columns: "id,password" });
  assert.ok(
    res && typeof res.error === "string" && /subset of/.test(res.error),
    "off-whitelist column should be rejected, not read: " + JSON.stringify(res),
  );
});

test("outreach_query: a filter on a non-whitelisted column is rejected", () => {
  const tools = loadTools(makeDb());
  const res = tools.outreach_query.execute({ filter: "sqlite_version = x" });
  assert.ok(
    res && typeof res.error === "string" && /filter column must be/.test(res.error),
    "off-whitelist filter column should be rejected: " + JSON.stringify(res),
  );
});
