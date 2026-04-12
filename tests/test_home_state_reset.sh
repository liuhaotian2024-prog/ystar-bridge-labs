#!/bin/bash
# Test: home state auto-reset at boot (方案 C)
# 3 cases:
#   1. active_agent=eng-platform → boot ceo → should become ceo
#   2. active_agent=ceo → boot ceo → should remain ceo
#   3. --verify-only + active_agent=eng-platform → should NOT change (diagnostic mode)
#
# Note: tests isolate the HOME-RESET block logic by replaying it against a
# temp YSTAR_DIR, so we don't touch the real marker or daemon.

set -u

PASS=0
FAIL=0
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Extract the HOME-RESET logic as a local function mirroring governance_boot.sh
home_reset() {
  local AGENT_ID="$1"
  local VERIFY_ONLY="$2"
  local YSTAR_DIR="$3"
  if [ "$AGENT_ID" = "ceo" ] && [ "$VERIFY_ONLY" = false ]; then
    CURRENT_MARKER=$(cat "$YSTAR_DIR/.ystar_active_agent" 2>/dev/null || echo "")
    if [ -n "$CURRENT_MARKER" ] && [ "$CURRENT_MARKER" != "ceo" ]; then
      echo "ceo" > "$YSTAR_DIR/.ystar_active_agent"
    fi
  fi
}

check() {
  local name="$1" expected="$2" actual="$3"
  if [ "$actual" = "$expected" ]; then
    echo "  PASS: $name (got '$actual')"
    PASS=$((PASS+1))
  else
    echo "  FAIL: $name (expected '$expected', got '$actual')"
    FAIL=$((FAIL+1))
  fi
}

echo "=== Test 1: active_agent=eng-platform → boot ceo → should reset to ceo ==="
T1="$TMP/t1"; mkdir -p "$T1"
echo "eng-platform" > "$T1/.ystar_active_agent"
home_reset "ceo" false "$T1"
check "case-1-reset" "ceo" "$(cat "$T1/.ystar_active_agent")"

echo "=== Test 2: active_agent=ceo → boot ceo → should remain ceo ==="
T2="$TMP/t2"; mkdir -p "$T2"
echo "ceo" > "$T2/.ystar_active_agent"
home_reset "ceo" false "$T2"
check "case-2-noop" "ceo" "$(cat "$T2/.ystar_active_agent")"

echo "=== Test 3: --verify-only + active_agent=eng-platform → should NOT change ==="
T3="$TMP/t3"; mkdir -p "$T3"
echo "eng-platform" > "$T3/.ystar_active_agent"
home_reset "ceo" true "$T3"
check "case-3-verify-only-preserves" "eng-platform" "$(cat "$T3/.ystar_active_agent")"

echo ""
echo "=== RESULT: $PASS passed, $FAIL failed ==="
exit $FAIL
