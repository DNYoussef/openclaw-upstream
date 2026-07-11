#!/bin/bash
# OpenClaw Railway entrypoint -- permanent auth fix
# NO set -e -- we want to see all errors, not crash on non-fatal ones
echo "[entrypoint] starting ($(date -u))" >&2

# ---------------------------------------------------------------------------
# 1. Pin OPENCLAW_STATE_DIR so seed-auth.cjs and gateway agree on paths
# ---------------------------------------------------------------------------
export OPENCLAW_STATE_DIR="/app/.openclaw"
export HOME="/app"
echo "[entrypoint] OPENCLAW_STATE_DIR=${OPENCLAW_STATE_DIR}" >&2
echo "[entrypoint] HOME=${HOME}" >&2

# ---------------------------------------------------------------------------
# 2. Fix volume permissions (Railway volumes mount as root)
# ---------------------------------------------------------------------------
for d in /app/.openclaw /app/.openclaw/agents /app/.openclaw/agents/main /app/.openclaw/agents/main/agent /app/.openclaw/data; do
  mkdir -p "$d" 2>/dev/null || true
done
chown -R openclaw:openclaw /app/.openclaw 2>&1 || echo "[entrypoint] chown /app/.openclaw failed (non-fatal)" >&2

# ---------------------------------------------------------------------------
# 3. ALWAYS restore baked config (survives volume corruption + resets)
# ---------------------------------------------------------------------------
if [ -f /app/.openclaw/openclaw.json.baked ]; then
  cp -f /app/.openclaw/openclaw.json.baked /app/.openclaw/openclaw.json
  chown openclaw:openclaw /app/.openclaw/openclaw.json 2>/dev/null || true
  echo "[entrypoint] config restored from baked" >&2
fi

# Seed config from env var if present (overrides baked file)
if [ -n "$OPENCLAW_SEED_CONFIG" ]; then
  echo "$OPENCLAW_SEED_CONFIG" | base64 -d > /app/.openclaw/openclaw.json
  chown openclaw:openclaw /app/.openclaw/openclaw.json 2>/dev/null || true
  echo "[entrypoint] config seeded from OPENCLAW_SEED_CONFIG env" >&2
fi

# ---------------------------------------------------------------------------
# 4. Seed auth-profiles from the environment
#    Write to the EXACT path the gateway will read:
#    $OPENCLAW_STATE_DIR/agents/main/agent/auth-profiles.json
# ---------------------------------------------------------------------------
AGENT_DIR="/app/.openclaw/agents/main/agent"
mkdir -p "$AGENT_DIR" 2>/dev/null || true

if [ -n "$OPENCLAW_AUTH_PROFILES_B64" ]; then
  echo "$OPENCLAW_AUTH_PROFILES_B64" | base64 -d > "$AGENT_DIR/auth-profiles.json"
  echo "[entrypoint] auth-profiles written from B64 env ($(wc -c < "$AGENT_DIR/auth-profiles.json") bytes)" >&2
else
  echo "[entrypoint] WARNING: no auth-profiles source available" >&2
fi

chown -R openclaw:openclaw /app/.openclaw/agents 2>&1 || true

# ---------------------------------------------------------------------------
# 5. Log gateway token status (don't print the actual token)
# ---------------------------------------------------------------------------
if [ -n "$OPENCLAW_GATEWAY_TOKEN" ]; then
  echo "[entrypoint] OPENCLAW_GATEWAY_TOKEN is set (${#OPENCLAW_GATEWAY_TOKEN} chars)" >&2
else
  echo "[entrypoint] WARNING: OPENCLAW_GATEWAY_TOKEN not set -- dashboard will require device identity" >&2
fi

# ---------------------------------------------------------------------------
# 6. Log Slack token status
# ---------------------------------------------------------------------------
if [ -n "$SLACK_BOT_TOKEN" ]; then
  echo "[entrypoint] SLACK_BOT_TOKEN is set" >&2
else
  echo "[entrypoint] WARNING: SLACK_BOT_TOKEN not set" >&2
fi

# ---------------------------------------------------------------------------
# 7. Verify state before dropping privileges
# ---------------------------------------------------------------------------
echo "[entrypoint] auth-profiles exists: $(test -f "$AGENT_DIR/auth-profiles.json" && echo "YES ($(wc -c < "$AGENT_DIR/auth-profiles.json") bytes)" || echo "NO")" >&2
echo "[entrypoint] config exists: $(test -f /app/.openclaw/openclaw.json && echo "YES" || echo "NO")" >&2
echo "[entrypoint] dropping to openclaw user, running: $@" >&2

# ---------------------------------------------------------------------------
# 8. Drop to non-root user and start gateway
# ---------------------------------------------------------------------------
exec gosu openclaw "$@"
