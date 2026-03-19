#!/bin/bash
set -e
# Fix volume permissions (Railway volumes mount as root:root)
chown -R openclaw:openclaw /app/.openclaw 2>/dev/null || true

# Restore baked config on every startup (prevents runtime corruption)
if [ -f /app/.openclaw/openclaw.json.baked ]; then
  cp /app/.openclaw/openclaw.json.baked /app/.openclaw/openclaw.json
fi
chown openclaw:openclaw /app/.openclaw/openclaw.json 2>/dev/null || true

# Restore baked auth-profiles on every startup
# The baked copy lives OUTSIDE the volume mount at /app/auth-profiles.json.baked
# Write to BOTH /app/.openclaw AND /root/.openclaw (gateway may use either depending on HOME)
if [ -f /app/auth-profiles.json.baked ]; then
  for STATE_DIR in /app/.openclaw /root/.openclaw; do
    AGENT_DIR="$STATE_DIR/agents/main/agent"
    mkdir -p "$AGENT_DIR" 2>/dev/null || true
    cp /app/auth-profiles.json.baked "$AGENT_DIR/auth-profiles.json"
  done
  chown -R openclaw:openclaw /app/.openclaw/agents 2>/dev/null || true
  echo "[entrypoint] auth-profiles.json restored to /app/.openclaw and /root/.openclaw" >&2
fi

# Also copy the baked config to /root/.openclaw for consistency
if [ -f /app/.openclaw/openclaw.json.baked ]; then
  mkdir -p /root/.openclaw 2>/dev/null || true
  cp /app/.openclaw/openclaw.json.baked /root/.openclaw/openclaw.json 2>/dev/null || true
fi

# Drop to non-root and exec CMD
exec gosu openclaw "$@"
