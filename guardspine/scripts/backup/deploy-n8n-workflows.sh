#!/usr/bin/env bash
# deploy-n8n-workflows.sh -- Create n8n workflows from JSON definitions
# Usage: N8N_BASE_URL=https://... N8N_API_KEY=... ./deploy-n8n-workflows.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="$SCRIPT_DIR/../../n8n-workflows"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

if [ -z "${N8N_BASE_URL:-}" ]; then echo "ERROR: N8N_BASE_URL not set"; exit 1; fi
if [ -z "${N8N_API_KEY:-}" ]; then echo "ERROR: N8N_API_KEY not set"; exit 1; fi

N8N_BASE_URL="${N8N_BASE_URL%/}"
CREATED=0
SKIPPED=0
FAILED=0

for json_file in "$WORKFLOW_DIR"/*.json; do
  [ -f "$json_file" ] || continue
  fname=$(basename "$json_file")
  wf_name=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['name'])" "$json_file" 2>/dev/null || echo "unknown")

  log "Deploying: $wf_name ($fname)"

  # Check if workflow with same name already exists
  existing=$(curl -s --max-time 15 \
    "${N8N_BASE_URL}/api/v1/workflows?limit=100" \
    -H "Accept: application/json" \
    -H "X-N8N-API-KEY: ${N8N_API_KEY}" 2>/dev/null || echo '{"data":[]}')

  existing_id=$(echo "$existing" | python3 -c "
import json,sys
data = json.load(sys.stdin)
for wf in data.get('data', []):
    if wf.get('name') == '$wf_name':
        print(wf['id'])
        break
" 2>/dev/null || echo "")

  if [ -n "$existing_id" ]; then
    log "  SKIP: '$wf_name' already exists (id: $existing_id)"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Create workflow
  response=$(curl -s --max-time 30 \
    -X POST "${N8N_BASE_URL}/api/v1/workflows" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
    -d @"$json_file" 2>&1)

  new_id=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")

  if [ -n "$new_id" ]; then
    log "  CREATED: $wf_name (id: $new_id)"
    CREATED=$((CREATED + 1))
  else
    log "  FAILED: $wf_name -- $response"
    FAILED=$((FAILED + 1))
  fi
done

log "Done. Created: $CREATED, Skipped: $SKIPPED, Failed: $FAILED"
