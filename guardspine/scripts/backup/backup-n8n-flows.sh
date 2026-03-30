#!/usr/bin/env bash
# backup-n8n-flows.sh -- Export all n8n workflows via REST API and commit changes
# Usage: N8N_BASE_URL=https://... N8N_API_KEY=... ./backup-n8n-flows.sh
# Idempotent: safe to run on cron or manually.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
EXPORT_DIR="$REPO_ROOT/guardspine/n8n-workflows/backups"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# ---------------------------------------------------------------------------
# Validate environment
# ---------------------------------------------------------------------------
if [ -z "${N8N_BASE_URL:-}" ]; then
  log "ERROR: N8N_BASE_URL is not set"
  exit 1
fi
if [ -z "${N8N_API_KEY:-}" ]; then
  log "ERROR: N8N_API_KEY is not set"
  exit 1
fi

# Strip trailing slash from base URL
N8N_BASE_URL="${N8N_BASE_URL%/}"

# ---------------------------------------------------------------------------
# Ensure export directory exists
# ---------------------------------------------------------------------------
mkdir -p "$EXPORT_DIR"

# ---------------------------------------------------------------------------
# Fetch all workflows from n8n REST API
# ---------------------------------------------------------------------------
log "Fetching workflow list from $N8N_BASE_URL ..."

RESPONSE=$(curl -sSf \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Accept: application/json" \
  "$N8N_BASE_URL/api/v1/workflows" 2>&1) || {
  log "ERROR: Failed to fetch workflows. curl output:"
  log "$RESPONSE"
  exit 1
}

# n8n API returns { data: [...] } -- extract the array
WORKFLOW_IDS=$(echo "$RESPONSE" | python -c "
import json, sys
data = json.load(sys.stdin)
workflows = data.get('data', data) if isinstance(data, dict) else data
for w in workflows:
    print(w['id'])
" 2>/dev/null) || {
  log "ERROR: Failed to parse workflow list JSON"
  log "Response body (first 500 chars): ${RESPONSE:0:500}"
  exit 1
}

if [ -z "$WORKFLOW_IDS" ]; then
  log "No workflows found. Nothing to export."
  exit 0
fi

WORKFLOW_COUNT=$(echo "$WORKFLOW_IDS" | wc -l | tr -d ' ')
log "Found $WORKFLOW_COUNT workflow(s). Exporting..."

# ---------------------------------------------------------------------------
# Export each workflow
# ---------------------------------------------------------------------------
EXPORTED=0
FAILED=0

for WF_ID in $WORKFLOW_IDS; do
  WF_JSON=$(curl -sSf \
    -H "X-N8N-API-KEY: $N8N_API_KEY" \
    -H "Accept: application/json" \
    "$N8N_BASE_URL/api/v1/workflows/$WF_ID" 2>&1) || {
    log "WARN: Failed to fetch workflow $WF_ID, skipping"
    FAILED=$((FAILED + 1))
    continue
  }

  # Extract workflow name and sanitize for filename
  WF_NAME=$(echo "$WF_JSON" | python -c "
import json, sys, re
data = json.load(sys.stdin)
name = data.get('name', 'unnamed')
# Replace non-alphanumeric chars (except dash/underscore) with underscore
safe = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
# Collapse multiple underscores
safe = re.sub(r'_+', '_', safe).strip('_')
print(safe[:80])
" 2>/dev/null) || {
    WF_NAME="unnamed"
  }

  FILENAME="${WF_ID}__${WF_NAME}.json"
  FILEPATH="$EXPORT_DIR/$FILENAME"

  # Redact credential values to avoid pushing secrets to GitHub.
  # n8n stores credentials in nodes[].credentials (references) and may
  # inline sensitive values in node parameters. Strip known secret patterns.
  WF_JSON=$(echo "$WF_JSON" | python -c "
import json, sys, re

# Patterns for secret-looking string VALUES (provider prefixes, Bearer tokens, etc.)
SECRET_VALUE_RE = re.compile(
    r'^(Bearer\s+)?(ntn_|secret_|sk-|sk_|xox[bpas]-|ghp_|gho_|glpat-|AKIA|eyJ)',
    re.IGNORECASE,
)

# Keys whose values should always be redacted
SECRET_KEY_PARTS = (
    'password', 'secret', 'token', 'apikey', 'api_key',
    'authorization', 'accesstoken', 'access_token',
    'refreshtoken', 'refresh_token', 'privatekey',
    'private_key', 'client_secret', 'webhook_secret',
    'credentials',
)

# n8n header parameter keys that signal the sibling 'value' is a secret
AUTH_HEADER_NAMES = {'authorization', 'x-api-key', 'x-n8n-api-key'}

data = json.load(sys.stdin)

def redact_header_params(params_list):
    \"\"\"Redact value fields in n8n headerParameters where name is an auth header.\"\"\"
    result = []
    for p in params_list:
        if isinstance(p, dict) and p.get('name', '').lower() in AUTH_HEADER_NAMES:
            p = dict(p)
            if isinstance(p.get('value'), str) and len(p['value']) > 0:
                p['value'] = '***REDACTED***'
        result.append(p)
    return result

def redact(obj, parent_key=''):
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            lk = k.lower()
            is_secret_key = any(s in lk for s in SECRET_KEY_PARTS)
            if is_secret_key and isinstance(v, str) and len(v) > 0:
                result[k] = '***REDACTED***'
            elif is_secret_key and isinstance(v, dict):
                # Redact all string values inside credential sub-objects
                result[k] = {sk: ('***REDACTED***' if isinstance(sv, str) and len(sv) > 0 else sv) for sk, sv in v.items()}
            elif lk == 'parameters' and isinstance(v, list):
                # n8n headerParameters.parameters is a list of {name, value}
                result[k] = redact_header_params(v)
            else:
                result[k] = redact(v, parent_key=k)
        return result
    elif isinstance(obj, list):
        return [redact(item, parent_key=parent_key) for item in obj]
    elif isinstance(obj, str) and SECRET_VALUE_RE.match(obj):
        return '***REDACTED***'
    return obj

data = redact(data)
print(json.dumps(data))
" 2>&1) || {
    log "ERROR: Credential redaction failed for $WF_ID, skipping (refusing to write unredacted secrets)"
    FAILED=$((FAILED + 1))
    continue
  }

  # Pretty-print and write
  echo "$WF_JSON" | python -m json.tool > "$FILEPATH" 2>/dev/null || {
    # Fallback: write raw JSON if pretty-print fails
    echo "$WF_JSON" > "$FILEPATH"
  }

  log "  Exported: $FILENAME"
  EXPORTED=$((EXPORTED + 1))
done

log "Export complete: $EXPORTED succeeded, $FAILED failed"

# ---------------------------------------------------------------------------
# Git commit + push if there are changes
# ---------------------------------------------------------------------------
cd "$REPO_ROOT"

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  log "Not inside a git repo. Skipping commit."
  exit 0
fi

# Set git identity if not already configured (needed in CI)
if [ -z "$(git config user.name 2>/dev/null)" ]; then
  git config user.name "github-actions[bot]"
  git config user.email "github-actions[bot]@users.noreply.github.com"
fi

git add "$EXPORT_DIR"/*.json 2>/dev/null || true

if git diff --cached --quiet 2>/dev/null; then
  log "No workflow changes detected. Nothing to commit."
else
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
  git commit -m "$(cat <<EOF
chore(n8n): backup $EXPORTED workflow(s) [$TIMESTAMP]

Automated export via backup-n8n-flows.sh
EOF
  )"
  log "Changes committed."

  # Push only if a remote is configured for the current branch
  REMOTE_BRANCH=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "")
  if [ -n "$REMOTE_BRANCH" ]; then
    git push || {
      log "WARN: git push failed. Changes are committed locally."
    }
    log "Pushed to remote."
  else
    log "No upstream branch configured. Changes committed locally only."
  fi
fi

log "Done."
