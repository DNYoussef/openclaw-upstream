#!/usr/bin/env bash
# verify-slack-integration.sh
#
# Verifies Slack integration readiness against the Railway backend.
# Checks: health, auth, slack endpoints, optional test message delivery.
#
# Usage:
#   ./scripts/verify-slack-integration.sh
#   SLACK_TEST_CHANNEL=C12345 ./scripts/verify-slack-integration.sh

set -euo pipefail

BACKEND_URL="${BACKEND_URL:-https://backend-production-0f5d.up.railway.app}"
LOGIN_EMAIL="${LOGIN_EMAIL:?Set LOGIN_EMAIL env var}"
LOGIN_PASSWORD="${LOGIN_PASSWORD:?Set LOGIN_PASSWORD env var}"
SLACK_TEST_CHANNEL="${SLACK_TEST_CHANNEL:-}"

PASS=0
FAIL=0
WARN=0

pass() { PASS=$((PASS + 1)); echo "  [PASS] $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  [FAIL] $1"; }
warn() { WARN=$((WARN + 1)); echo "  [WARN] $1"; }

echo "=== GuardSpine Slack Integration Verification ==="
echo "Backend: $BACKEND_URL"
echo ""

# ------- 1. Health check -------
echo "--- Step 1: Backend Health ---"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/health" 2>/dev/null || echo "000")
if [ "$HEALTH_STATUS" = "200" ]; then
  pass "Backend health endpoint returned 200"
else
  fail "Backend health endpoint returned $HEALTH_STATUS (expected 200)"
fi

# ------- 2. Auth token -------
echo ""
echo "--- Step 2: Authentication ---"
AUTH_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$LOGIN_EMAIL\",\"password\":\"$LOGIN_PASSWORD\"}" 2>/dev/null || echo "{}")

TOKEN=$(echo "$AUTH_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")

if [ -n "$TOKEN" ] && [ "$TOKEN" != "None" ] && [ "$TOKEN" != "" ]; then
  pass "Obtained auth token"
else
  fail "Could not obtain auth token -- remaining tests may fail"
  TOKEN=""
fi

# ------- 3. Slack interactivity endpoint exists -------
echo ""
echo "--- Step 3: Slack Endpoints ---"

# POST /api/v1/slack/interactivity (no Slack headers = should get 401, not 404)
INTERACT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "$BACKEND_URL/api/v1/slack/interactivity" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "payload={}" 2>/dev/null || echo "000")

if [ "$INTERACT_STATUS" = "401" ]; then
  pass "Slack interactivity endpoint exists (returned 401 -- missing signature, as expected)"
elif [ "$INTERACT_STATUS" = "404" ]; then
  fail "Slack interactivity endpoint NOT FOUND (404)"
elif [ "$INTERACT_STATUS" = "422" ]; then
  pass "Slack interactivity endpoint exists (returned 422 -- validation, endpoint registered)"
else
  warn "Slack interactivity endpoint returned $INTERACT_STATUS (expected 401)"
fi

# POST /api/v1/slack/events (no Slack headers = should get 401, not 404)
EVENTS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "$BACKEND_URL/api/v1/slack/events" \
  -H "Content-Type: application/json" \
  -d '{"type":"url_verification","challenge":"test"}' 2>/dev/null || echo "000")

if [ "$EVENTS_STATUS" = "401" ]; then
  pass "Slack events endpoint exists (returned 401 -- missing signature, as expected)"
elif [ "$EVENTS_STATUS" = "404" ]; then
  fail "Slack events endpoint NOT FOUND (404)"
else
  warn "Slack events endpoint returned $EVENTS_STATUS (expected 401)"
fi

# POST /api/v1/slack/test-delivery (requires admin auth)
if [ -n "$TOKEN" ]; then
  TEST_DELIVERY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$BACKEND_URL/api/v1/slack/test-delivery" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"channel":"C_PLACEHOLDER","message":"verify script dry run"}' 2>/dev/null || echo "000")

  if [ "$TEST_DELIVERY_STATUS" = "200" ]; then
    pass "Slack test-delivery endpoint exists and responded"
  elif [ "$TEST_DELIVERY_STATUS" = "404" ]; then
    fail "Slack test-delivery endpoint NOT FOUND (404)"
  elif [ "$TEST_DELIVERY_STATUS" = "500" ]; then
    # 500 likely means bot token not set -- endpoint exists but cannot deliver
    warn "Slack test-delivery returned 500 (endpoint exists, bot token likely not configured)"
  else
    warn "Slack test-delivery returned $TEST_DELIVERY_STATUS"
  fi
else
  warn "Skipping test-delivery check (no auth token)"
fi

# POST /api/v1/slack/send-approval (requires auth)
if [ -n "$TOKEN" ]; then
  SEND_APPROVAL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$BACKEND_URL/api/v1/slack/send-approval" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"approval_id":"nonexistent","channel":"C_PLACEHOLDER"}' 2>/dev/null || echo "000")

  if [ "$SEND_APPROVAL_STATUS" = "404" ]; then
    # 404 = approval not found, which means the endpoint IS registered and working
    pass "Slack send-approval endpoint exists (returned 404 for nonexistent approval -- correct)"
  elif [ "$SEND_APPROVAL_STATUS" = "422" ]; then
    pass "Slack send-approval endpoint exists (returned 422 -- validation)"
  else
    warn "Slack send-approval returned $SEND_APPROVAL_STATUS"
  fi
else
  warn "Skipping send-approval check (no auth token)"
fi

# ------- 4. Optional: Send test message -------
echo ""
echo "--- Step 4: Live Delivery Test ---"

if [ -n "$SLACK_TEST_CHANNEL" ] && [ -n "$TOKEN" ]; then
  echo "  Sending test message to channel $SLACK_TEST_CHANNEL..."
  DELIVERY_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/v1/slack/test-delivery" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"channel\":\"$SLACK_TEST_CHANNEL\",\"message\":\"GuardSpine integration verification -- $(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" 2>/dev/null || echo "{}")

  DELIVERY_SUCCESS=$(echo "$DELIVERY_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success',False))" 2>/dev/null || echo "False")

  if [ "$DELIVERY_SUCCESS" = "True" ]; then
    pass "Test message delivered to Slack channel $SLACK_TEST_CHANNEL"
  else
    DELIVERY_ERROR=$(echo "$DELIVERY_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('error','unknown'))" 2>/dev/null || echo "unknown")
    fail "Test message delivery failed: $DELIVERY_ERROR"
  fi
else
  if [ -z "$SLACK_TEST_CHANNEL" ]; then
    warn "Skipping live delivery test (set SLACK_TEST_CHANNEL=C... to enable)"
  else
    warn "Skipping live delivery test (no auth token)"
  fi
fi

# ------- Summary -------
echo ""
echo "=== Summary ==="
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
echo "  Warnings: $WARN"

if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "Some checks FAILED. Review output above."
  exit 1
fi

echo ""
echo "All critical checks passed."
exit 0
