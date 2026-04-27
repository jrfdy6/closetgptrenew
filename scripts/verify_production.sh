#!/usr/bin/env bash

set -euo pipefail

FRONTEND_URL="${FRONTEND_URL:-https://closetgpt-frontend.vercel.app}"
BACKEND_URL="${BACKEND_URL:-https://closetgptrenew-production.up.railway.app}"

failures=0

check_status() {
  local name="$1"
  local url="$2"
  local expected="$3"
  local actual

  actual="$(curl -sS -o /dev/null -w "%{http_code}" "$url")"

  if [[ "$actual" == "$expected" ]]; then
    printf 'PASS  %-28s %s -> %s\n' "$name" "$actual" "$url"
  else
    printf 'FAIL  %-28s expected=%s actual=%s %s\n' "$name" "$expected" "$actual" "$url"
    failures=$((failures + 1))
  fi
}

echo "Verifying production surfaces"
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"
echo

check_status "frontend-root" "$FRONTEND_URL/" "200"
check_status "frontend-signin" "$FRONTEND_URL/signin" "200"
check_status "frontend-debug-token" "$FRONTEND_URL/debug-token" "404"
check_status "frontend-personalization" "$FRONTEND_URL/personalization-demo" "404"
check_status "frontend-test-env" "$FRONTEND_URL/api/test-env" "404"

check_status "backend-health" "$BACKEND_URL/health" "200"
check_status "backend-health-simple" "$BACKEND_URL/health/simple" "200"
check_status "backend-api-health" "$BACKEND_URL/api/health" "200"
check_status "backend-debug-routes" "$BACKEND_URL/debug/routes" "404"
check_status "backend-test-inline" "$BACKEND_URL/api/test-inline" "404"
check_status "backend-test-simple" "$BACKEND_URL/api/test-simple/health" "404"
check_status "backend-monitoring" "$BACKEND_URL/api/monitoring/dashboard" "404"
check_status "backend-firebase-debug" "$BACKEND_URL/api/wardrobe/firebase-debug" "404"
check_status "backend-openapi" "$BACKEND_URL/openapi.json" "404"

echo

if (( failures > 0 )); then
  printf 'Production verification failed: %d check(s) failed.\n' "$failures"
  exit 1
fi

echo "Production verification passed."
