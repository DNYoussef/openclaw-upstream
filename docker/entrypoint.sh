#!/bin/bash
set -e
# Fix volume permissions (Railway volumes mount as root:root)
chown -R openclaw:openclaw /app/.openclaw/data 2>/dev/null || true
# Drop to non-root and exec CMD
exec gosu openclaw "$@"
