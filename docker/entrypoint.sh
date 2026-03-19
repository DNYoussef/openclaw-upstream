#!/bin/bash
set -e
# Fix volume permissions (Railway volumes mount as root:root)
# Only chown data dir -- extensions must stay root-owned for plugin trust check
chown -R openclaw:openclaw /app/.openclaw/data 2>/dev/null || true
# Ensure openclaw user can write to .openclaw dir for logs/state
chown openclaw:openclaw /app/.openclaw 2>/dev/null || true

# Restore baked config on every startup.
# The gateway (and plugins) may overwrite openclaw.json at runtime,
# corrupting it with unrecognized keys or removing our settings
# (e.g. dangerouslyDisableDeviceAuth). Restoring from the baked
# copy ensures a clean config on every container start.
if [ -f /app/.openclaw/openclaw.json.baked ]; then
  cp /app/.openclaw/openclaw.json.baked /app/.openclaw/openclaw.json
fi
chown openclaw:openclaw /app/.openclaw/openclaw.json 2>/dev/null || true

# Seed auth-profiles.json from env var if present (subscription OAuth tokens)
if [ -n "$OPENCLAW_AUTH_PROFILES_B64" ]; then
  AGENT_DIR="/app/.openclaw/agents/main/agent"
  mkdir -p "$AGENT_DIR"
  echo "$OPENCLAW_AUTH_PROFILES_B64" | base64 -d > "$AGENT_DIR/auth-profiles.json"
  chown -R openclaw:openclaw /app/.openclaw/agents 2>/dev/null || true
  echo "[entrypoint] auth-profiles.json seeded from env" >&2
  echo "[entrypoint] auth file size: $(wc -c < "$AGENT_DIR/auth-profiles.json") bytes" >&2
else
  echo "[entrypoint] OPENCLAW_AUTH_PROFILES_B64 not set, skipping auth seed" >&2
fi

# Drop to non-root and exec CMD
exec gosu openclaw "$@"
