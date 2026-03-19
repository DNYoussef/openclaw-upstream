// Preload script: write auth-profiles.json from OPENCLAW_AUTH_PROFILES_B64 env var
// This runs inside the Node.js process, bypassing any entrypoint/volume issues
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
  const dirs = [
    path.join(process.env.OPENCLAW_STATE_DIR || "/app/.openclaw", "agents", "main", "agent"),
    path.join(process.env.HOME || "/root", ".openclaw", "agents", "main", "agent"),
    process.env.OPENCLAW_AGENT_DIR || "",
  ].filter(Boolean);

  for (const dir of new Set(dirs)) {
    try {
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(path.join(dir, "auth-profiles.json"), data, "utf8");
      console.error(
        `[seed-auth] wrote auth-profiles.json to ${dir} (source: ${source}, ${data.length} bytes)`,
      );
    } catch (e) {
      console.error(`[seed-auth] failed to write to ${dir}: ${e.message}`);
    }
  }
} else {
  console.error(
    "[seed-auth] no auth data found (OPENCLAW_AUTH_PROFILES_B64 not set, /app/auth-profiles.json.baked not found)",
  );
}
