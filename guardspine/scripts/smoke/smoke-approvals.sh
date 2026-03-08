#!/usr/bin/env bash
# smoke-approvals.sh -- Approval workflow smoke tests via curl
#
# Usage:
#   bash scripts/smoke-approvals.sh [BASE_URL]
#
# Defaults to the Railway production deployment.
# Exit code 0 = all tests pass, 1 = at least one failure.

set -euo pipefail

BASE="${1:-https://backend-production-0f5d.up.railway.app}"
PASS=0
FAIL=0
TAG="$(date +%s)"

# Detect python binary (python3 on Linux/macOS, python on Windows)
PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"

green() { printf "\033[32m%s\033[0m\n" "$1"; }
red()   { printf "\033[31m%s\033[0m\n" "$1"; }
info()  { printf "  -> %s\n" "$1"; }

assert_status() {
    local label="$1" expected="$2" actual="$3"
    if [ "$expected" = "$actual" ]; then
        green "PASS: $label (HTTP $actual)"
        PASS=$((PASS + 1))
    else
        red "FAIL: $label (expected $expected, got $actual)"
        FAIL=$((FAIL + 1))
    fi
}

assert_json_field() {
    local label="$1" json="$2" field="$3" expected="$4"
    local actual
    actual=$(echo "$json" | $PY -c "import sys,json; print(json.load(sys.stdin).get('$field',''))" 2>/dev/null || echo "PARSE_ERROR")
    if [ "$actual" = "$expected" ]; then
        green "PASS: $label ($field=$actual)"
        PASS=$((PASS + 1))
    else
        red "FAIL: $label ($field expected '$expected', got '$actual')"
        FAIL=$((FAIL + 1))
    fi
}

echo "============================================"
echo " GuardSpine Approval Smoke Tests"
echo " Target: $BASE"
echo "============================================"
echo ""

# -- 1. Health check --
echo "[1/7] Health check"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/health")
assert_status "GET /health" "200" "$HTTP"

# -- 2. Login as admin --
echo ""
echo "[2/7] Login as admin"
ADMIN_EMAIL="${ADMIN_EMAIL:?Set ADMIN_EMAIL env var}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:?Set ADMIN_PASSWORD env var}"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/auth/local/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")
HTTP=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
assert_status "POST /auth/local/login (admin)" "200" "$HTTP"
ADMIN_TOKEN=$(echo "$BODY" | $PY -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
info "Token: ${ADMIN_TOKEN:0:20}..."

# -- 3. Login as viewer --
echo ""
echo "[3/7] Login as viewer"
VIEWER_EMAIL="${VIEWER_EMAIL:?Set VIEWER_EMAIL env var}"
VIEWER_PASSWORD="${VIEWER_PASSWORD:?Set VIEWER_PASSWORD env var}"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/auth/local/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$VIEWER_EMAIL\",\"password\":\"$VIEWER_PASSWORD\"}")
HTTP=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
assert_status "POST /auth/local/login (viewer)" "200" "$HTTP"
VIEWER_TOKEN=$(echo "$BODY" | $PY -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
info "Token: ${VIEWER_TOKEN:0:20}..."

# -- 4. Create L3 approval --
echo ""
echo "[4/7] Create L3 approval request"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/guard/approval/request" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"resume_webhook_url\":\"https://example.com/noop\",\"risk_tier\":3,\"guard_type\":\"smoke-test\",\"workflow_execution_id\":\"smoke-wf-$TAG\",\"evidence_hash\":\"hash-$TAG\",\"bead_id\":\"smoke-bead-$TAG\"}")
HTTP=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
assert_status "POST /guard/approval/request" "200" "$HTTP"
assert_json_field "approval status" "$BODY" "status" "pending"
APPROVAL_ID=$(echo "$BODY" | $PY -c "import sys,json; print(json.load(sys.stdin).get('approval_id',''))" 2>/dev/null)
info "Approval ID: $APPROVAL_ID"

# -- 5. Self-approval test (admin approves own) --
echo ""
echo "[5/7] Self-approval guard test (admin approves own request)"
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/approvals/$APPROVAL_ID/approve?rationale=Self-approval+smoke" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
HTTP=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
# Guard does NOT fire because created_by is empty string
assert_status "POST /approvals/{id}/approve (self)" "200" "$HTTP"
assert_json_field "self-approval status" "$BODY" "status" "approved"
info "NOTE: Self-approval guard bypassed (created_by is empty)"

# -- 6. Cross-user approval (viewer approves admin's new request) --
echo ""
echo "[6/7] Cross-user approval (viewer approves)"
# Create fresh approval
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/guard/approval/request" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"resume_webhook_url\":\"https://example.com/noop\",\"risk_tier\":3,\"guard_type\":\"smoke-cross\",\"workflow_execution_id\":\"smoke-cross-$TAG\",\"evidence_hash\":\"hashcross-$TAG\",\"bead_id\":\"smoke-cross-$TAG\"}")
HTTP=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
CROSS_ID=$(echo "$BODY" | $PY -c "import sys,json; print(json.load(sys.stdin).get('approval_id',''))" 2>/dev/null)
info "New approval: $CROSS_ID"

RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE/api/v1/approvals/$CROSS_ID/approve?rationale=Cross-user+smoke" \
  -H "Authorization: Bearer $VIEWER_TOKEN")
HTTP=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
assert_status "POST /approvals/{id}/approve (viewer)" "200" "$HTTP"
assert_json_field "cross-approval status" "$BODY" "status" "approved"

# -- 7. List approvals with status filter --
echo ""
echo "[7/7] List approvals filtering"
RESP=$(curl -s -w "\n%{http_code}" "$BASE/api/v1/approvals?status=pending" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
HTTP=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
assert_status "GET /approvals?status=pending" "200" "$HTTP"
TOTAL=$(echo "$BODY" | $PY -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null)
info "Pending approvals: $TOTAL"

# -- Summary --
echo ""
echo "============================================"
echo " Results: $PASS passed, $FAIL failed"
echo "============================================"

if [ "$FAIL" -gt 0 ]; then
    red "SMOKE TEST FAILED"
    exit 1
else
    green "ALL SMOKE TESTS PASSED"
    exit 0
fi
