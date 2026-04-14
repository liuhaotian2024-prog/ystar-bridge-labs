#!/usr/bin/env bash
# Exp 4: Race — 2 concurrent hook call + mtime change (consistency test)

set -e

echo "=== Exp 4: Race condition — concurrent hook calls + mtime change ==="

# Create test files
touch /tmp/a /tmp/b

# 2 hook calls in parallel
echo "Starting 2 concurrent hook calls..."
(echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/a"}}' | bash /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_client_labs.sh > /tmp/hook1.out 2>&1) &
(echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/b"}}' | bash /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_client_labs.sh > /tmp/hook2.out 2>&1) &

# Race: change rules mid-flight
sleep 0.1
echo "Touching rules file mid-flight..."
touch /Users/haotianliu/.openclaw/workspace/ystar-company/governance/forget_guard_rules.yaml

wait

# Both hooks should return consistent decision
echo "Checking consistency of concurrent hook responses..."
if diff /tmp/hook1.out /tmp/hook2.out > /dev/null 2>&1; then
  echo "PASS: Both hook responses consistent (no race condition detected)"
else
  echo "FAIL: Inconsistent hook responses detected"
  echo "Hook 1 output:"
  cat /tmp/hook1.out
  echo "Hook 2 output:"
  cat /tmp/hook2.out
  exit 1
fi
