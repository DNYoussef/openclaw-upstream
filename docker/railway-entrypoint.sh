#!/bin/sh
# Railway volumes mount as root. OpenClaw runs as node (uid 1000).
# Fix ownership before starting.
if [ -d /data ]; then
  mkdir -p /data/.openclaw /data/workspace 2>/dev/null || true
  chown -R node:node /data 2>/dev/null || true
fi
chown -R node:node /home/node 2>/dev/null || true

# Seed config from OPENCLAW_SEED_CONFIG env var (base64-encoded JSON).
# This lets us write a valid config without SSH after deploy.
if [ -n "$OPENCLAW_SEED_CONFIG" ]; then
  echo "$OPENCLAW_SEED_CONFIG" | base64 -d > /data/.openclaw/openclaw.json
  chown node:node /data/.openclaw/openclaw.json
  unset OPENCLAW_SEED_CONFIG
fi

# Drop to node user and run openclaw CLI with passed arguments
exec gosu node node dist/index.js "$@"
