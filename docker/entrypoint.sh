#!/bin/bash
# NO set -e -- we want to see all errors
echo "[entrypoint] starting" >&2

# Fix volume permissions
chown -R openclaw:openclaw /app/.openclaw 2>&1 || echo "[entrypoint] chown failed (non-fatal)" >&2

# Restore baked config
if [ -f /app/.openclaw/openclaw.json.baked ]; then
  cp /app/.openclaw/openclaw.json.baked /app/.openclaw/openclaw.json
  echo "[entrypoint] restored openclaw.json from baked" >&2
fi

# Auth profiles
echo "[entrypoint] checking /app/auth-profiles.json.baked exists: $(ls -la /app/auth-profiles.json.baked 2>&1)" >&2
if [ -f /app/auth-profiles.json.baked ]; then
  for STATE_DIR in /app/.openclaw /root/.openclaw; do
    AGENT_DIR="$STATE_DIR/agents/main/agent"
    mkdir -p "$AGENT_DIR" 2>&1 || echo "[entrypoint] mkdir $AGENT_DIR failed" >&2
    cp /app/auth-profiles.json.baked "$AGENT_DIR/auth-profiles.json" 2>&1 || echo "[entrypoint] cp to $AGENT_DIR failed" >&2
    echo "[entrypoint] wrote auth-profiles to $AGENT_DIR ($(wc -c < "$AGENT_DIR/auth-profiles.json" 2>/dev/null || echo 0) bytes)" >&2
  done
  chown -R openclaw:openclaw /app/.openclaw/agents 2>&1 || true
else
  echo "[entrypoint] WARNING: /app/auth-profiles.json.baked NOT FOUND" >&2
  echo "[entrypoint] /app/ contents: $(ls /app/*.baked 2>&1)" >&2
fi

# Copy config to /root too
if [ -f /app/.openclaw/openclaw.json.baked ]; then
  mkdir -p /root/.openclaw 2>&1 || true
  cp /app/.openclaw/openclaw.json.baked /root/.openclaw/openclaw.json 2>&1 || true
fi

echo "[entrypoint] dropping to openclaw user, running: $@" >&2
exec gosu openclaw "$@"
