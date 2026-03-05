#!/bin/sh
# Railway volumes mount as root. OpenClaw runs as node (uid 1000).
# Fix ownership before starting.
if [ -d /data ]; then
  mkdir -p /data/.openclaw /data/workspace 2>/dev/null || true
  chown -R node:node /data 2>/dev/null || true
fi
chown -R node:node /home/node 2>/dev/null || true

# Drop to node user and run openclaw CLI with passed arguments
exec gosu node node dist/index.js "$@"
