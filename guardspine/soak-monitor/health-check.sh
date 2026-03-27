#!/bin/sh

# Soak monitor: check health of all guardspine-ai-ops services.
# Runs in a loop (default 5 min interval) so Railway keeps the container alive.
# No dependencies beyond curl and sh.

CHECK_INTERVAL="${CHECK_INTERVAL:-300}"
TELEMETRY_URL="${TELEMETRY_API_URL:-http://telemetry-api.railway.internal:8090}"
TIMEOUT=20

# Globals reset each cycle
CHECKED=0
HEALTHY=0
HEALTHY_LIST=""
UNHEALTHY=""
DETAILS=""

check() {
  name="$1"
  url="$2"
  health_path="$3"

  if [ -z "$url" ]; then
    return
  fi

  CHECKED=$((CHECKED + 1))
  full_url="${url}${health_path}"

  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$full_url" 2>/dev/null) || status=0

  if [ "$status" -ge 200 ] && [ "$status" -lt 400 ]; then
    ok=true
    HEALTHY=$((HEALTHY + 1))
    if [ -z "$HEALTHY_LIST" ]; then
      HEALTHY_LIST="\"$name\""
    else
      HEALTHY_LIST="$HEALTHY_LIST,\"$name\""
    fi
  else
    ok=false
    if [ -z "$UNHEALTHY" ]; then
      UNHEALTHY="\"$name\""
    else
      UNHEALTHY="$UNHEALTHY,\"$name\""
    fi
  fi

  entry="{\"service\":\"$name\",\"status\":$status,\"ok\":$ok}"
  if [ -z "$DETAILS" ]; then
    DETAILS="$entry"
  else
    DETAILS="$DETAILS,$entry"
  fi
}

check_pg() {
  if [ -z "$DATABASE_URL" ]; then
    return
  fi

  CHECKED=$((CHECKED + 1))

  host=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^/]*\)/.*|\1|p')
  dbname=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')
  pg_host=$(echo "$host" | cut -d: -f1)
  pg_port=$(echo "$host" | cut -d: -f2)

  if [ -z "$pg_host" ] || [ -z "$pg_port" ]; then
    echo "[WARN]  postgres: could not parse DATABASE_URL"
    ok=false
    status=0
    if [ -z "$UNHEALTHY" ]; then
      UNHEALTHY="\"postgres\""
    else
      UNHEALTHY="$UNHEALTHY,\"postgres\""
    fi
  elif timeout "$TIMEOUT" pg_isready -h "$pg_host" -p "$pg_port" -d "$dbname" -t "$TIMEOUT" >/dev/null 2>&1; then
    ok=true
    HEALTHY=$((HEALTHY + 1))
    status=200
    if [ -z "$HEALTHY_LIST" ]; then
      HEALTHY_LIST="\"postgres\""
    else
      HEALTHY_LIST="$HEALTHY_LIST,\"postgres\""
    fi
  else
    ok=false
    status=0
    if [ -z "$UNHEALTHY" ]; then
      UNHEALTHY="\"postgres\""
    else
      UNHEALTHY="$UNHEALTHY,\"postgres\""
    fi
  fi

  entry="{\"service\":\"postgres\",\"status\":$status,\"ok\":$ok}"
  if [ -z "$DETAILS" ]; then
    DETAILS="$entry"
  else
    DETAILS="$DETAILS,$entry"
  fi
}

run_checks() {
  # Reset counters
  CHECKED=0
  HEALTHY=0
  HEALTHY_LIST=""
  UNHEALTHY=""
  DETAILS=""

  # Core services (defaults to Railway internal DNS)
  check "guardspine" "${GUARDSPINE_HEALTH_URL:-http://guardspine-internal.railway.internal}" "/health"
  check "n8n"        "${N8N_HEALTH_URL:-http://n8n.railway.internal}"                       "/healthz"
  check "openclaw"   "${OPENCLAW_HEALTH_URL:-http://openclaw.railway.internal}"              "/health"
  check "paperclip"  "${PAPERCLIP_HEALTH_URL:-http://paperclip.railway.internal:3100}"       "/api/health"
  check_pg

  # Additional Railway services (defaults for internal DNS)
  LITELLM_HEALTH_URL="${LITELLM_HEALTH_URL:-http://litellm.railway.internal:4000}"
  TELEMETRY_API_HEALTH_URL="${TELEMETRY_API_HEALTH_URL:-http://telemetry-api.railway.internal:8090}"
  DECISION_ENGINE_HEALTH_URL="${DECISION_ENGINE_HEALTH_URL:-http://decision-engine.railway.internal:8091}"
  MIROFISH_HEALTH_URL="${MIROFISH_HEALTH_URL:-http://mirofish.railway.internal:5001}"

  check "litellm"         "$LITELLM_HEALTH_URL"         "/health/readiness"
  check "telemetry-api"   "$TELEMETRY_API_HEALTH_URL"   "/health"
  check "decision-engine" "$DECISION_ENGINE_HEALTH_URL" "/health"
  check "mirofish"        "$MIROFISH_HEALTH_URL"        "/health"
  check "ops-portal"      "${OPS_PORTAL_HEALTH_URL:-http://ops-portal.railway.internal:8080}" "/"

  # Log summary
  echo "[INFO]  checked=$CHECKED healthy=$HEALTHY unhealthy=[$UNHEALTHY] details=[$DETAILS]"

  # POST to telemetry-api
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%S")
  PAYLOAD="{\"service\":\"soak-monitor\",\"event_type\":\"health_check\",\"payload\":{\"checked\":$CHECKED,\"healthy\":[$HEALTHY_LIST],\"unhealthy\":[$UNHEALTHY],\"details\":[$DETAILS],\"timestamp\":\"$TIMESTAMP\"}}"
  curl -s -X POST "${TELEMETRY_URL}/telemetry" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    --max-time 10 >/dev/null 2>&1 || echo "[WARN]  telemetry POST failed (non-fatal)"

  if [ "$HEALTHY" -eq "$CHECKED" ]; then
    echo "[INFO]  all $CHECKED services healthy"
  else
    echo "[WARN]  $((CHECKED - HEALTHY))/$CHECKED services unhealthy"
  fi
}

# Main loop
echo "[INFO]  soak-monitor starting (interval=${CHECK_INTERVAL}s)"
while true; do
  run_checks
  sleep "$CHECK_INTERVAL"
done
