#!/bin/sh
set -e

# Soak monitor: check health of all guardspine-ai-ops services.
# Exits 0 if all healthy, 1 if any unhealthy.
# Designed for Railway cron. No dependencies beyond curl and sh.

TIMEOUT=20
CHECKED=0
HEALTHY=0
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
  start=$(date +%s%N 2>/dev/null || date +%s)

  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$full_url" 2>/dev/null) || status=0
  end=$(date +%s%N 2>/dev/null || date +%s)

  if [ "$status" -ge 200 ] && [ "$status" -lt 400 ]; then
    ok=true
    HEALTHY=$((HEALTHY + 1))
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

# Check Postgres via pg_isready if DATABASE_URL is set
check_pg() {
  if [ -z "$DATABASE_URL" ]; then
    return
  fi

  CHECKED=$((CHECKED + 1))

  # Extract host:port from DATABASE_URL
  host=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^/]*\)/.*|\1|p')
  dbname=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')

  if pg_isready -h "$(echo "$host" | cut -d: -f1)" -p "$(echo "$host" | cut -d: -f2)" -d "$dbname" -t "$TIMEOUT" >/dev/null 2>&1; then
    ok=true
    HEALTHY=$((HEALTHY + 1))
    status=200
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

# Run checks
check "guardspine" "$GUARDSPINE_HEALTH_URL" "/health"
check "n8n"        "$N8N_HEALTH_URL"        "/healthz"
check "openclaw"   "$OPENCLAW_HEALTH_URL"   "/health"
check "paperclip"  "$PAPERCLIP_HEALTH_URL"  "/api/health"
check_pg

# Output structured JSON
echo "[INFO]  checked=$CHECKED healthy=$HEALTHY unhealthy=[$UNHEALTHY] details=[$DETAILS]"

# Exit code signals success/failure to Railway cron
if [ "$HEALTHY" -eq "$CHECKED" ]; then
  exit 0
else
  exit 1
fi
