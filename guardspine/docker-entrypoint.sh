#!/bin/sh
# Seed auth-profiles.json from env var if present
if [ -n "$OPENCLAW_AUTH_PROFILES_B64" ]; then
  AGENT_DIR="${OPENCLAW_STATE_DIR:-/app/.openclaw}/agents/main/agent"
  mkdir -p "$AGENT_DIR"
  echo "$OPENCLAW_AUTH_PROFILES_B64" | base64 -d > "$AGENT_DIR/auth-profiles.json"
  echo "[entrypoint] auth-profiles.json seeded"
fi

# Override persisted model config to use subscription providers
if [ -n "$OPENCLAW_PRIMARY_MODEL" ]; then
  echo "[entrypoint] primary model: $OPENCLAW_PRIMARY_MODEL"
fi

exec node openclaw.mjs gateway --allow-unconfigured "$@"
