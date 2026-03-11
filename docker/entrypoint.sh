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

# Drop to non-root and exec CMD
exec gosu openclaw "$@"
