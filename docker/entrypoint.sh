#!/bin/bash
set -e
# Fix volume permissions (Railway volumes mount as root:root)
# Only chown data dir -- extensions must stay root-owned for plugin trust check
chown -R openclaw:openclaw /app/.openclaw/data 2>/dev/null || true
# Ensure openclaw user can write config/logs but NOT modify extensions
chown openclaw:openclaw /app/.openclaw /app/.openclaw/openclaw.json 2>/dev/null || true
# Drop to non-root and exec CMD
exec gosu openclaw "$@"
