#!/usr/bin/env bash
#
# Guard Lane smoke tests - standalone curl script.
# Tests guard lane endpoints against the Railway deployment.
#
# Usage:
#   bash scripts/smoke-guard-lanes.sh
#   GUARDSPINE_API_URL=http://localhost:8000 bash scripts/smoke-guard-lanes.sh
#
set -euo pipefail

API="${GUARDSPINE_API_URL:-https://backend-production-0f5d.up.railway.app}"
EMAIL="${GUARDSPINE_EMAIL:?Set GUARDSPINE_EMAIL env var}"
PASSWORD="${GUARDSPINE_PASSWORD:?Set GUARDSPINE_PASSWORD env var}"

# Detect python binary (python3 on Linux/Mac, python on Windows)
PY=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo "")

PASS=0
FAIL=0
TOTAL=0

check() {
    local name="$1" expected="$2" actual="$3"
    TOTAL=$((TOTAL + 1))
    if [ "$actual" = "$expected" ]; then
        printf "  PASS  %s (HTTP %s)\n" "$name" "$actual"
        PASS=$((PASS + 1))
    else
        printf "  FAIL  %s (expected %s, got %s)\n" "$name" "$expected" "$actual"
        FAIL=$((FAIL + 1))
    fi
}

printf "=== Guard Lane Smoke Tests ===\n"
printf "Target: %s\n\n" "$API"

# -- Authenticate --
printf "[1/7] Authenticating as %s...\n" "$EMAIL"
LOGIN_RESP=$(curl --max-time 15 -s -X POST "$API/api/v1/auth/local/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

TOKEN=$(printf '%s' "$LOGIN_RESP" | $PY -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || true)

if [ -z "$TOKEN" ]; then
    printf "  FAIL  Authentication failed. Response: %s\n" "$LOGIN_RESP"
    exit 1
fi
printf "  PASS  Got access token\n\n"

AUTH="Authorization: Bearer $TOKEN"

# -- Create temp files --
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT
printf "dummy" > "$TMPDIR/test.pdf"
printf "dummy" > "$TMPDIR/test.xlsx"
printf "dummy" > "$TMPDIR/test.png"

# -- Test 1: List lanes --
printf "[2/7] GET /guard/lanes\n"
STATUS=$(curl --max-time 15 -s -o /dev/null -w "%{http_code}" \
    "$API/api/v1/guard/lanes" -H "$AUTH")
check "list_lanes" "200" "$STATUS"

# Verify lane count
LANE_COUNT=$(curl --max-time 15 -s "$API/api/v1/guard/lanes" -H "$AUTH" | \
    $PY -c "import sys,json; print(len(json.load(sys.stdin)['lanes']))" 2>/dev/null || echo "0")
if [ "$LANE_COUNT" = "3" ]; then
    printf "  PASS  lane count = 3\n"
else
    printf "  FAIL  lane count expected 3, got %s\n" "$LANE_COUNT"
fi
printf "\n"

# -- Test 2: PDF lane 501 --
printf "[3/7] POST /guard/lanes/pdf (expect 501)\n"
STATUS=$(curl --max-time 20 -s -o /dev/null -w "%{http_code}" \
    -X POST "$API/api/v1/guard/lanes/pdf" \
    -H "$AUTH" \
    -F "original=@$TMPDIR/test.pdf" \
    -F "updated=@$TMPDIR/test.pdf")
check "pdf_lane_501" "501" "$STATUS"
printf "\n"

# -- Test 3: Sheet lane 501 --
printf "[4/7] POST /guard/lanes/sheet (expect 501)\n"
STATUS=$(curl --max-time 20 -s -o /dev/null -w "%{http_code}" \
    -X POST "$API/api/v1/guard/lanes/sheet" \
    -H "$AUTH" \
    -F "original=@$TMPDIR/test.xlsx" \
    -F "updated=@$TMPDIR/test.xlsx")
check "sheet_lane_501" "501" "$STATUS"
printf "\n"

# -- Test 4: Image lane 501 --
printf "[5/7] POST /guard/lanes/image (expect 501)\n"
STATUS=$(curl --max-time 20 -s -o /dev/null -w "%{http_code}" \
    -X POST "$API/api/v1/guard/lanes/image" \
    -H "$AUTH" \
    -F "before=@$TMPDIR/test.png" \
    -F "after=@$TMPDIR/test.png")
check "image_lane_501" "501" "$STATUS"
printf "\n"

# -- Test 5: Bridge create bundle --
printf "[6/7] POST /guard/lanes/pdf/bundle (expect 201)\n"
BUNDLE_RESP=$(curl --max-time 15 -s -w "\n%{http_code}" \
    -X POST "$API/api/v1/guard/lanes/pdf/bundle" \
    -H "$AUTH" \
    -H "Content-Type: application/json" \
    -d '{"evidence_hash":"deadbeef1234","risk_tier":"L2","diff_summary":{"pages":2,"changes":1},"review":{"overall_risk":"medium"},"findings_count":1}')
STATUS=$(printf '%s' "$BUNDLE_RESP" | tail -1)
BODY=$(printf '%s' "$BUNDLE_RESP" | head -1)
check "bridge_create_bundle" "201" "$STATUS"

# Verify bundle_id present
BUNDLE_ID=$(printf '%s' "$BODY" | $PY -c "import sys,json; print(json.load(sys.stdin).get('bundle_id',''))" 2>/dev/null || echo "")
if [ -n "$BUNDLE_ID" ]; then
    printf "  PASS  bundle_id = %s\n" "$BUNDLE_ID"
else
    printf "  FAIL  no bundle_id in response\n"
fi
printf "\n"

# -- Test 6: Bridge invalid lane 400 --
printf "[7/7] POST /guard/lanes/invalid/bundle (expect 400)\n"
STATUS=$(curl --max-time 15 -s -o /dev/null -w "%{http_code}" \
    -X POST "$API/api/v1/guard/lanes/invalid/bundle" \
    -H "$AUTH" \
    -H "Content-Type: application/json" \
    -d '{"evidence_hash":"x","risk_tier":"L1","diff_summary":{}}')
check "bridge_invalid_lane_400" "400" "$STATUS"

# -- Test 7 (bonus): Bridge missing fields 422 --
STATUS=$(curl --max-time 15 -s -o /dev/null -w "%{http_code}" \
    -X POST "$API/api/v1/guard/lanes/pdf/bundle" \
    -H "$AUTH" \
    -H "Content-Type: application/json" \
    -d '{}')
check "bridge_missing_fields_422" "422" "$STATUS"
printf "\n"

# -- Summary --
printf "=== Results: %d/%d passed" "$PASS" "$TOTAL"
if [ "$FAIL" -gt 0 ]; then
    printf ", %d FAILED" "$FAIL"
fi
printf " ===\n"

exit "$FAIL"
