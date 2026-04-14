#!/usr/bin/env bash
# Exp 2: Daemon kill mid-process (graceful degradation test)

set -e

echo "=== Exp 2: Daemon kill mid-process ==="

# Start hook call with long-running payload
echo "Starting hook call with 10s sleep payload..."
echo '{"tool_name":"Bash","tool_input":{"command":"sleep 10"}}' | bash /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_client_labs.sh &
HOOK_PID=$!

sleep 0.5

# Kill daemon mid-flight
echo "Killing hook daemon mid-flight..."
pkill -9 -f hook_daemon || true

sleep 2

# Check hook call exit status
wait $HOOK_PID
EXIT_CODE=$?
echo "Hook call exit code: $EXIT_CODE"

# Verify daemon respawn and new calls succeed
echo "Testing new hook call after daemon death..."
sleep 2
echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/test.md"}}' | bash /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_client_labs.sh > /tmp/hook_recovery.out 2>&1

if [ $? -eq 0 ]; then
  echo "PASS: Hook calls recovered after daemon kill"
else
  echo "FAIL: Hook calls failed after daemon respawn"
  cat /tmp/hook_recovery.out
  exit 1
fi
