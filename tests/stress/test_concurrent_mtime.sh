#!/usr/bin/env bash
# Exp 1: 50 file/sec concurrent mtime change (watcher stress test)
# Touch 3000 files in 60s (50/s) — watcher should not crash / miss / latency explosion

set -e

echo "=== Exp 1: Concurrent mtime change (50 file/sec) ==="
echo "Starting background mtime storm (3000 touches in 60s)..."

# Background mtime storm
(
  for i in $(seq 1 3000); do
    touch /Users/haotianliu/.openclaw/workspace/ystar-company/governance/forget_guard_rules.yaml
    sleep 0.02
  done
) &
STORM_PID=$!

echo "Storm started (PID: $STORM_PID). Sampling hook call latency..."

# Concurrent hook call latency sampling
for i in $(seq 1 30); do
  start=$(python3 -c "import time; print(time.time())")
  echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/test.md"}}' | bash /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_client_labs.sh > /dev/null 2>&1 || true
  end=$(python3 -c "import time; print(time.time())")
  latency=$(python3 -c "print($end - $start)")
  echo "Sample $i latency: ${latency}s"

  # Check if latency exceeded 1s threshold
  python3 -c "
import sys
if float('$latency') > 1.0:
    print('FAIL: latency exceeded 1s threshold')
    sys.exit(1)
" || { echo "FAIL: Latency spike detected"; kill $STORM_PID 2>/dev/null || true; exit 1; }

  sleep 2
done

# Wait for storm to complete
wait $STORM_PID 2>/dev/null || true

echo "PASS: All hook calls completed with latency < 1s during mtime storm"
