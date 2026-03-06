#!/usr/bin/env bash
# deploy-n8n-workflows.sh -- Create or update n8n workflows from JSON definitions
# Reads ONLY from guardspine/n8n-workflows/definitions/ (hand-authored).
# Backups go to guardspine/n8n-workflows/backups/ (generated, never deployed).
# Usage: N8N_BASE_URL=https://... N8N_API_KEY=... ./deploy-n8n-workflows.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFINITION_DIR="$SCRIPT_DIR/../../n8n-workflows/definitions"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

if [ -z "${N8N_BASE_URL:-}" ]; then echo "ERROR: N8N_BASE_URL not set"; exit 1; fi
if [ -z "${N8N_API_KEY:-}" ]; then echo "ERROR: N8N_API_KEY not set"; exit 1; fi

N8N_BASE_URL="${N8N_BASE_URL%/}"

if [ ! -d "$DEFINITION_DIR" ]; then
  log "ERROR: Definition directory not found: $DEFINITION_DIR"
  exit 1
fi

CREATED=0
UPDATED=0
FAILED=0

# Fetch existing workflows once (fail hard on auth/network errors)
existing=$(curl -sf --max-time 15 \
  "${N8N_BASE_URL}/api/v1/workflows?limit=100" \
  -H "Accept: application/json" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}") || {
  log "ERROR: Cannot reach n8n API at ${N8N_BASE_URL}. Check URL and API key."
  exit 1
}

for json_file in "$DEFINITION_DIR"/*.json; do
  [ -f "$json_file" ] || continue
  fname=$(basename "$json_file")
  wf_name=$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['name'])" "$json_file" 2>/dev/null || echo "unknown")

  log "Deploying: $wf_name ($fname)"

  # Check if workflow with same name already exists
  existing_id=$(echo "$existing" | python -c "
import json,sys
data = json.load(sys.stdin)
name = sys.argv[1]
for wf in data.get('data', []):
    if wf.get('name') == name:
        print(wf['id'])
        break
" "$wf_name" 2>/dev/null || echo "")

  if [ -n "$existing_id" ]; then
    # Update existing workflow
    response=$(curl -s --max-time 30 \
      -X PATCH "${N8N_BASE_URL}/api/v1/workflows/${existing_id}" \
      -H "Accept: application/json" \
      -H "Content-Type: application/json" \
      -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
      -d @"$json_file" 2>&1)

    upd_id=$(echo "$response" | python -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")
    if [ -n "$upd_id" ]; then
      log "  UPDATED: $wf_name (id: $existing_id)"
      UPDATED=$((UPDATED + 1))
    else
      log "  FAILED update: $wf_name -- $response"
      FAILED=$((FAILED + 1))
    fi
  else
    # Create new workflow
    response=$(curl -s --max-time 30 \
      -X POST "${N8N_BASE_URL}/api/v1/workflows" \
      -H "Accept: application/json" \
      -H "Content-Type: application/json" \
      -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
      -d @"$json_file" 2>&1)

    new_id=$(echo "$response" | python -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")
    if [ -n "$new_id" ]; then
      log "  CREATED: $wf_name (id: $new_id)"
      CREATED=$((CREATED + 1))
    else
      log "  FAILED create: $wf_name -- $response"
      FAILED=$((FAILED + 1))
    fi
  fi
done

log "Done. Created: $CREATED, Updated: $UPDATED, Failed: $FAILED"

if [ "$FAILED" -gt 0 ]; then
  exit 1
fi
