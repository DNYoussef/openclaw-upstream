#!/bin/bash
set -e
# Fix volume permissions (Railway volumes mount as root:root)
chown -R openclaw:openclaw /app/.openclaw/data 2>/dev/null || true
chown openclaw:openclaw /app/.openclaw 2>/dev/null || true

# Restore baked config on every startup (prevents runtime corruption)
if [ -f /app/.openclaw/openclaw.json.baked ]; then
  cp /app/.openclaw/openclaw.json.baked /app/.openclaw/openclaw.json
fi
chown openclaw:openclaw /app/.openclaw/openclaw.json 2>/dev/null || true

# Restore baked auth-profiles on every startup
# The baked copy lives OUTSIDE the volume mount at /app/auth-profiles.json.baked
AGENT_DIR="/app/.openclaw/agents/main/agent"
if [ -f /app/auth-profiles.json.baked ]; then
  mkdir -p "$AGENT_DIR" 2>/dev/null || true
  cp /app/auth-profiles.json.baked "$AGENT_DIR/auth-profiles.json"
  chown -R openclaw:openclaw /app/.openclaw/agents 2>/dev/null || true
  echo "[entrypoint] auth-profiles.json restored from baked image" >&2
fi

# Drop to non-root and exec CMD
exec gosu openclaw "$@"
