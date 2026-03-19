// Preload script: write auth-profiles.json from baked file or env var
// Runs inside Node.js process via --require, before gateway code loads
const fs = require("fs");
const path = require("path");

const b64 = process.env.OPENCLAW_AUTH_PROFILES_B64;
const bakedPath = "/app/auth-profiles.json.baked";

const source = b64 ? "env" : fs.existsSync(bakedPath) ? "baked" : null;
const data = b64
  ? Buffer.from(b64, "base64").toString("utf8")
  : fs.existsSync(bakedPath)
    ? fs.readFileSync(bakedPath, "utf8")
    : null;

if (data) {
  // Validate JSON before writing
  let parsed;
  try {
    parsed = JSON.parse(data);
  } catch (e) {
    process.stdout.write(`[seed-auth] ERROR: invalid JSON: ${e.message}\n`);
    process.exit(0); // don't crash gateway
  }

  const profileCount = Object.keys(parsed.profiles || {}).length;
  process.stdout.write(
    `[seed-auth] source=${source} profiles=${profileCount} bytes=${data.length}\n`,
  );

  const dirs = [
    path.join(process.env.OPENCLAW_STATE_DIR || "/app/.openclaw", "agents", "main", "agent"),
    path.join(process.env.HOME || "/root", ".openclaw", "agents", "main", "agent"),
    process.env.OPENCLAW_AGENT_DIR || "",
  ].filter(Boolean);

  for (const dir of new Set(dirs)) {
    try {
      fs.mkdirSync(dir, { recursive: true });
      const filePath = path.join(dir, "auth-profiles.json");
      fs.writeFileSync(filePath, data, "utf8");
      // Verify write
      const verify = fs.readFileSync(filePath, "utf8");
      const verifyParsed = JSON.parse(verify);
      const verifyProfiles = Object.keys(verifyParsed.profiles || {}).length;
      process.stdout.write(
        `[seed-auth] OK ${dir} (${verifyProfiles} profiles, ${verify.length} bytes)\n`,
      );
    } catch (e) {
      process.stdout.write(`[seed-auth] FAIL ${dir}: ${e.message}\n`);
    }
  }
} else {
  process.stdout.write(
    "[seed-auth] NO DATA (OPENCLAW_AUTH_PROFILES_B64 not set, /app/auth-profiles.json.baked not found)\n",
  );
  process.stdout.write(
    `[seed-auth] env keys: ${Object.keys(process.env)
      .filter((k) => k.includes("OPENCLAW") || k.includes("AUTH"))
      .join(", ")}\n`,
  );
  process.stdout.write(
    `[seed-auth] HOME=${process.env.HOME} STATE_DIR=${process.env.OPENCLAW_STATE_DIR} AGENT_DIR=${process.env.OPENCLAW_AGENT_DIR}\n`,
  );
}
