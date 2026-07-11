// Preload script: write auth-profiles.json BEFORE gateway code loads.
// Runs inside Node.js process via --require.
//
// PERMANENT FIX for the Railway race condition:
// 1. Replicate the gateway's exact path resolution (resolveStateDir + agent dir)
// 2. Write auth-profiles.json to ALL candidate paths
// 3. Intercept fs.writeFileSync to block empty-store overwrites during gateway init
// 4. Also seed gateway config from OPENCLAW_SEED_CONFIG if present
const fs = require("fs");
const path = require("path");
const os = require("os");

// ---------------------------------------------------------------------------
// Step 0: Resolve the EXACT paths the gateway will use
// ---------------------------------------------------------------------------
// Mirror src/config/paths.ts resolveStateDir() logic
function resolveStateDir() {
  const override =
    (process.env.OPENCLAW_STATE_DIR || "").trim() ||
    (process.env.CLAWDBOT_STATE_DIR || "").trim();
  if (override) return override;

  const home = process.env.HOME || process.env.USERPROFILE || os.homedir();
  const newDir = path.join(home, ".openclaw");

  // Check legacy dirs (same order as gateway)
  const legacyNames = [".clawdbot", ".moldbot", ".moltbot"];
  if (fs.existsSync(newDir)) return newDir;
  for (const name of legacyNames) {
    const dir = path.join(home, name);
    if (fs.existsSync(dir)) return dir;
  }
  return newDir;
}

// Mirror src/agents/agent-paths.ts resolveOpenClawAgentDir() logic
function resolveAgentDir() {
  const override =
    (process.env.OPENCLAW_AGENT_DIR || "").trim() ||
    (process.env.PI_CODING_AGENT_DIR || "").trim();
  if (override) return override;
  return path.join(resolveStateDir(), "agents", "main", "agent");
}

const gatewayAgentDir = resolveAgentDir();
const gatewayAuthPath = path.join(gatewayAgentDir, "auth-profiles.json");

process.stdout.write(
  `[seed-auth] gateway will read from: ${gatewayAuthPath}\n`,
);
process.stdout.write(
  `[seed-auth] HOME=${process.env.HOME} STATE_DIR=${process.env.OPENCLAW_STATE_DIR || "(unset)"} AGENT_DIR=${process.env.OPENCLAW_AGENT_DIR || "(unset)"}\n`,
);

// ---------------------------------------------------------------------------
// Step 1: Write auth-profiles.json
// ---------------------------------------------------------------------------
const b64 = process.env.OPENCLAW_AUTH_PROFILES_B64;
const data = b64 ? Buffer.from(b64, "base64").toString("utf8") : null;

if (data) {
  let parsed;
  try {
    parsed = JSON.parse(data);
  } catch (e) {
    process.stdout.write(`[seed-auth] ERROR: invalid JSON: ${e.message}\n`);
    // Don't crash gateway -- continue without auth
    parsed = null;
  }

  if (parsed) {
    const profileCount = Object.keys(parsed.profiles || {}).length;
    process.stdout.write(`[seed-auth] source=env profiles=${profileCount} bytes=${data.length}\n`);

    // Write to the gateway's resolved path PLUS fallback locations
    const dirs = new Set([
      gatewayAgentDir,
      path.join(process.env.OPENCLAW_STATE_DIR || "/app/.openclaw", "agents", "main", "agent"),
      path.join(process.env.HOME || "/root", ".openclaw", "agents", "main", "agent"),
    ]);

    for (const dir of dirs) {
      try {
        fs.mkdirSync(dir, { recursive: true });
        const filePath = path.join(dir, "auth-profiles.json");
        fs.writeFileSync(filePath, data, "utf8");
        const verify = fs.readFileSync(filePath, "utf8");
        const verifyProfiles = Object.keys(JSON.parse(verify).profiles || {}).length;
        process.stdout.write(
          `[seed-auth] OK ${filePath} (${verifyProfiles} profiles)\n`,
        );
      } catch (e) {
        process.stdout.write(`[seed-auth] FAIL ${dir}: ${e.message}\n`);
      }
    }

    // -----------------------------------------------------------------------
    // Step 2: INTERCEPT empty-store overwrites (the race condition fix)
    // -----------------------------------------------------------------------
    // The gateway's loadAuthProfileStoreForAgent() can create an empty store
    // {version:N, profiles:{}} and call saveJsonFile() which uses
    // fs.writeFileSync. We intercept writes to auth-profiles.json and block
    // any that would replace a populated store with an empty one.
    const _origWriteFileSync = fs.writeFileSync;
    fs.writeFileSync = function patchedWriteFileSync(filePath, content, opts) {
      if (
        typeof filePath === "string" &&
        filePath.endsWith("auth-profiles.json")
      ) {
        // Check if this write would empty out a populated store
        let incoming;
        try {
          incoming =
            typeof content === "string"
              ? JSON.parse(content)
              : JSON.parse(content.toString("utf8"));
        } catch {
          // Not JSON or not parseable -- let it through
          return _origWriteFileSync.call(fs, filePath, content, opts);
        }

        const incomingProfiles = Object.keys(incoming.profiles || {}).length;

        // If the incoming write has zero profiles, check if existing file has data
        if (incomingProfiles === 0) {
          try {
            const existing = JSON.parse(fs.readFileSync(filePath, "utf8"));
            const existingProfiles = Object.keys(
              existing.profiles || {},
            ).length;
            if (existingProfiles > 0) {
              process.stdout.write(
                `[seed-auth] BLOCKED empty overwrite of ${filePath} (existing has ${existingProfiles} profiles)\n`,
              );
              return; // Block the write
            }
          } catch {
            // File doesn't exist or isn't readable -- let the write proceed
          }
        }
      }
      return _origWriteFileSync.call(fs, filePath, content, opts);
    };

    process.stdout.write("[seed-auth] fs.writeFileSync interceptor ACTIVE\n");
  }
} else {
  process.stdout.write(
    "[seed-auth] NO AUTH DATA (OPENCLAW_AUTH_PROFILES_B64 not set, baked file not found)\n",
  );
  process.stdout.write(
    `[seed-auth] env keys: ${Object.keys(process.env)
      .filter((k) => k.includes("OPENCLAW") || k.includes("AUTH"))
      .join(", ")}\n`,
  );
}

// ---------------------------------------------------------------------------
// Step 3: Seed gateway config from OPENCLAW_SEED_CONFIG (redundant safety)
// ---------------------------------------------------------------------------
const seedConfig = process.env.OPENCLAW_SEED_CONFIG;
if (seedConfig) {
  try {
    const configData = Buffer.from(seedConfig, "base64").toString("utf8");
    JSON.parse(configData); // validate
    const stateDir = resolveStateDir();
    const configPath = path.join(stateDir, "openclaw.json");
    fs.mkdirSync(stateDir, { recursive: true });
    fs.writeFileSync(configPath, configData, "utf8");
    process.stdout.write(`[seed-auth] config seeded to ${configPath}\n`);
  } catch (e) {
    process.stdout.write(
      `[seed-auth] config seed failed: ${e.message}\n`,
    );
  }
}
