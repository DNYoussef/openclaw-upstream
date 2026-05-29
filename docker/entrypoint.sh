#!/bin/bash
# OpenClaw Railway entrypoint -- permanent auth fix
# NO set -e -- we want to see all errors, not crash on non-fatal ones
DEBUG_ENTRYPOINT="${OPENCLAW_DEBUG_ENTRYPOINT:-0}"

log_entrypoint() {
  echo "[entrypoint] $1" >&2
}

log_entrypoint_debug() {
  if [ "$DEBUG_ENTRYPOINT" = "1" ]; then
    log_entrypoint "$1"
  fi
}

log_entrypoint_warning() {
  log_entrypoint "WARNING: $1"
}

log_entrypoint_debug "starting ($(date -u))"

# ---------------------------------------------------------------------------
# 1. Pin OPENCLAW_STATE_DIR so seed-auth.cjs and gateway agree on paths
# ---------------------------------------------------------------------------
export OPENCLAW_STATE_DIR="/app/.openclaw"
export HOME="/app"
export OPENCLAW_AGENT_DIR="/app/.openclaw/agents/main/agent"
export PI_CODING_AGENT_DIR="${OPENCLAW_AGENT_DIR}"
log_entrypoint_debug "OPENCLAW_STATE_DIR=${OPENCLAW_STATE_DIR}"
log_entrypoint_debug "HOME=${HOME}"
log_entrypoint_debug "OPENCLAW_AGENT_DIR=${OPENCLAW_AGENT_DIR}"

ensure_dir_owned() {
  local dir="$1"
  mkdir -p "$dir" 2>/dev/null || true
  chown openclaw:openclaw "$dir" 2>/dev/null || log_entrypoint_warning "chown ${dir} failed (non-fatal)"
}

ensure_file_owned() {
  local target="$1"
  if [ -e "$target" ]; then
    chown openclaw:openclaw "$target" 2>/dev/null || log_entrypoint_warning "chown ${target} failed (non-fatal)"
  fi
}

# ---------------------------------------------------------------------------
# 2. Fix volume permissions (Railway volumes mount as root)
# ---------------------------------------------------------------------------
for d in \
  /app/.openclaw \
  /app/.openclaw/agents \
  /app/.openclaw/agents/main \
  /app/.openclaw/agents/main/agent \
  /app/.openclaw/data \
  /app/.openclaw/logs \
  /app/.openclaw/extensions; do
  ensure_dir_owned "$d"
done

# ---------------------------------------------------------------------------
# 3. Restore config from a single source of truth.
#    Prefer the baked file shipped with the image; use OPENCLAW_SEED_CONFIG
#    only as a legacy fallback when the baked file is unavailable.
# ---------------------------------------------------------------------------
if [ -f /app/.openclaw/openclaw.json.baked ]; then
  cp -f /app/.openclaw/openclaw.json.baked /app/.openclaw/openclaw.json
  ensure_file_owned /app/.openclaw/openclaw.json
  log_entrypoint_debug "config restored from baked"
elif [ -n "$OPENCLAW_SEED_CONFIG" ]; then
  echo "$OPENCLAW_SEED_CONFIG" | base64 -d > /app/.openclaw/openclaw.json
  ensure_file_owned /app/.openclaw/openclaw.json
  log_entrypoint_warning "config seeded from OPENCLAW_SEED_CONFIG env (fallback)"
else
  log_entrypoint_warning "no config source available"
fi

# ---------------------------------------------------------------------------
# 4. ALWAYS restore auth-profiles (the key fix for the race condition)
#    Write to the EXACT path the gateway will read:
#    $OPENCLAW_STATE_DIR/agents/main/agent/auth-profiles.json
# ---------------------------------------------------------------------------
AGENT_DIR="/app/.openclaw/agents/main/agent"
mkdir -p "$AGENT_DIR" 2>/dev/null || true

if [ -n "$OPENCLAW_AUTH_PROFILES_B64" ]; then
  echo "$OPENCLAW_AUTH_PROFILES_B64" | base64 -d > "$AGENT_DIR/auth-profiles.json"
  log_entrypoint_debug "auth-profiles written from B64 env ($(wc -c < "$AGENT_DIR/auth-profiles.json") bytes)"
elif [ -f /app/auth-profiles.json.baked ]; then
  cp -f /app/auth-profiles.json.baked "$AGENT_DIR/auth-profiles.json"
  log_entrypoint_debug "auth-profiles restored from baked ($(wc -c < "$AGENT_DIR/auth-profiles.json") bytes)"
else
  log_entrypoint_warning "no auth-profiles source available"
fi

ensure_file_owned "$AGENT_DIR/auth-profiles.json"

# ---------------------------------------------------------------------------
# 5. Log gateway token status (don't print the actual token)
# ---------------------------------------------------------------------------
if [ -n "$OPENCLAW_GATEWAY_TOKEN" ]; then
  log_entrypoint_debug "OPENCLAW_GATEWAY_TOKEN is set (${#OPENCLAW_GATEWAY_TOKEN} chars)"
else
  log_entrypoint_warning "OPENCLAW_GATEWAY_TOKEN not set -- dashboard will require device identity"
fi

# ---------------------------------------------------------------------------
# 6. Log Slack token status
# ---------------------------------------------------------------------------
if [ -n "$SLACK_BOT_TOKEN" ]; then
  log_entrypoint_debug "SLACK_BOT_TOKEN is set"
else
  log_entrypoint_warning "SLACK_BOT_TOKEN not set"
fi

# ---------------------------------------------------------------------------
# 7. Verify state before dropping privileges
# ---------------------------------------------------------------------------
log_entrypoint_debug "auth-profiles exists: $(test -f "$AGENT_DIR/auth-profiles.json" && echo "YES ($(wc -c < "$AGENT_DIR/auth-profiles.json") bytes)" || echo "NO")"
log_entrypoint_debug "config exists: $(test -f /app/.openclaw/openclaw.json && echo "YES" || echo "NO")"
log_entrypoint_debug "dropping to openclaw user, running: $@"

# ---------------------------------------------------------------------------
# 8. Drop to non-root user and start gateway
# ---------------------------------------------------------------------------
exec gosu openclaw "$@"
