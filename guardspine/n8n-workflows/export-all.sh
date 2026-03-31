#!/usr/bin/env bash
# Export ALL n8n workflows to JSON files for version control.
# Usage: N8N_API_KEY=xxx bash n8n-export-all.sh [output_dir]
#
# This is the emergency backup that prevents catastrophic data loss.
# Fetches all workflows via pagination (handles databases with >250 workflows).

set -euo pipefail

N8N_URL="${N8N_BASE_URL:-http://n8n.railway.internal:5678}"
N8N_API_KEY="${N8N_API_KEY:?N8N_API_KEY is required}"
OUTPUT_DIR="${1:-./n8n-workflow-backup-$(date +%Y%m%d-%H%M%S)}"

mkdir -p "$OUTPUT_DIR"

echo "=== n8n Workflow Exporter ==="
echo "URL: $N8N_URL"
echo "Output: $OUTPUT_DIR"
echo ""

# Fetch all workflow IDs and names via pagination
# Handles databases with arbitrary numbers of workflows
ALL_WORKFLOWS=""
OFFSET=0
LIMIT=100
TOTAL_PAGES=0

while true; do
  echo "Fetching page $((OFFSET / LIMIT + 1))..."
  
  PAGE=$(curl -sf \
    -H "X-N8N-API-KEY: $N8N_API_KEY" \
    "${N8N_URL}/api/v1/workflows?limit=${LIMIT}&offset=${OFFSET}" 2>/dev/null || echo "[]")
  
  # Check if we got an empty page (end of results)
  if [ "$PAGE" = "[]" ] || [ -z "$PAGE" ]; then
    break
  fi
  
  # Parse workflows from this page and append
  WORKFLOWS_IN_PAGE=$(echo "$PAGE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    workflows = data.get('data', data) if isinstance(data, dict) else data
    for wf in workflows:
        print(json.dumps({'id': wf['id'], 'name': wf['name'], 'active': wf.get('active', False)}))
except:
    pass
" || echo "")
  
  if [ -z "$WORKFLOWS_IN_PAGE" ]; then
    # No workflows in this page, we're done
    break
  fi
  
  ALL_WORKFLOWS="${ALL_WORKFLOWS}${WORKFLOWS_IN_PAGE}"$'\n'
  OFFSET=$((OFFSET + LIMIT))
  TOTAL_PAGES=$((TOTAL_PAGES + 1))
done

echo "Fetched $TOTAL_PAGES page(s) of workflows"
echo ""

COUNT=0
ERRORS=0

while IFS= read -r line; do
  # Skip empty lines
  [ -z "$line" ] && continue
  
  # Extract fields safely via JSON parsing
  WF_ID=$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
  WF_NAME=$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['name'])" 2>/dev/null || echo "")
  WF_ACTIVE=$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['active'])" 2>/dev/null || echo "")
  
  # Validate WF_ID format (alphanumeric, underscore, hyphen only)
  # Prevents shell injection if API returns corrupted data
  if ! [[ "$WF_ID" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "✗ INVALID ID FORMAT: $WF_ID — SKIPPED (potential corruption)"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  # Sanitize name for filename
  SAFE_NAME=$(echo "$WF_NAME" | sed 's/[^a-zA-Z0-9._-]/_/g' | cut -c1-80)
  FILENAME="${WF_ID}__${SAFE_NAME}.json"

  # Export workflow (safely quoted variables)
  if curl -sf \
    -H "X-N8N-API-KEY: $N8N_API_KEY" \
    "${N8N_URL}/api/v1/workflows/${WF_ID}" \
    > "${OUTPUT_DIR}/${FILENAME}" 2>/dev/null; then
    echo "✓ [$WF_ID] $WF_NAME (active=$WF_ACTIVE)"
    COUNT=$((COUNT + 1))
  else
    echo "✗ [$WF_ID] $WF_NAME — EXPORT FAILED"
    ERRORS=$((ERRORS + 1))
  fi
done <<< "$ALL_WORKFLOWS"

echo ""
echo "=== Export Complete ==="
echo "Exported: $COUNT workflows"
echo "Errors:   $ERRORS"
echo "Location: $OUTPUT_DIR"

# Create manifest with metadata
echo "{ \"exported_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"count\": $COUNT, \"errors\": $ERRORS, \"pages\": $TOTAL_PAGES }" \
  > "${OUTPUT_DIR}/MANIFEST.json"

# Exit code indicates success/failure
if [ "$ERRORS" -gt 0 ]; then
  echo ""
  echo "⚠️  PARTIAL FAILURE: Exported $COUNT workflows, but $ERRORS failed."
  echo "   Backup may be incomplete. Check n8n API and network connectivity."
  exit 1
fi

exit 0
