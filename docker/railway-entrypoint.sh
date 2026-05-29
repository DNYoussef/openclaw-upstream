#!/bin/sh
# Legacy Railway shim kept for older local experiments.
# Production uses docker/entrypoint.sh instead.
if [ -d /data ]; then
  mkdir -p /data/.openclaw /data/workspace 2>/dev/null || true
  chown -R node:node /data 2>/dev/null || true
fi
chown -R node:node /home/node 2>/dev/null || true

exec gosu node node dist/index.js "$@"
