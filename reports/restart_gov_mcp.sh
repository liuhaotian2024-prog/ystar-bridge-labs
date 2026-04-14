#!/bin/bash
# Restart gov-mcp SSE server.
# Current process is started manually (no launchd/systemd). Kill pid + relaunch
# with the same args. After restart, probe gov_doctor via SSE endpoint.
#
# Discovered launch command (ps aux):
#   python -m gov_mcp --session-config <ystar-company/.ystar_session.json>
#                     --transport sse --host 0.0.0.0 --port 7922
set -u

YSTAR_DIR="/Users/haotianliu/.openclaw/workspace/ystar-company"
GOV_MCP_DIR="/Users/haotianliu/.openclaw/workspace/gov-mcp"
SESSION_JSON="$YSTAR_DIR/.ystar_session.json"
PORT=7922
LOG="$YSTAR_DIR/reports/gov_mcp.log"

echo "=== restart_gov_mcp ==="

# 1) Kill existing gov_mcp process(es)
PIDS=$(ps aux | grep -E 'python.*gov_mcp.*--transport sse' | grep -v grep | awk '{print $2}')
if [ -n "$PIDS" ]; then
    echo "Killing existing gov-mcp PIDs: $PIDS"
    kill $PIDS 2>/dev/null
    sleep 1
    # Force-kill any survivors
    for p in $PIDS; do
        if kill -0 "$p" 2>/dev/null; then
            kill -9 "$p" 2>/dev/null
        fi
    done
else
    echo "No existing gov-mcp process."
fi

# 2) Ensure port 7922 is free
if lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port $PORT still busy, waiting..."
    sleep 2
fi

# 3) Relaunch in background using the SAME command ps saw
cd "$GOV_MCP_DIR" || { echo "cannot cd $GOV_MCP_DIR"; exit 1; }
nohup /opt/homebrew/Cellar/python@3.11/3.11.14_3/Frameworks/Python.framework/Versions/3.11/bin/python3.11 \
    -m gov_mcp \
    --session-config "$SESSION_JSON" \
    --transport sse \
    --host 0.0.0.0 \
    --port $PORT \
    >> "$LOG" 2>&1 &
NEW_PID=$!
disown
echo "Launched gov-mcp pid=$NEW_PID (log: $LOG)"

# 4) Wait for readiness
for i in 1 2 3 4 5 6 7 8 9 10; do
    if curl -sS -o /dev/null -w "%{http_code}" "http://127.0.0.1:$PORT/" 2>/dev/null | grep -qE '200|404|405'; then
        echo "Port $PORT responsive after ${i}s"
        break
    fi
    sleep 1
done

# 5) Verify process is alive
if kill -0 "$NEW_PID" 2>/dev/null; then
    echo "OK: gov-mcp pid=$NEW_PID alive on :$PORT"
else
    echo "FAIL: gov-mcp process died. Check $LOG"
    tail -40 "$LOG"
    exit 1
fi

echo ""
echo "=== Next: verify L1_02_cieu.status via gov_doctor ==="
echo "In Claude Code, call: mcp__gov-mcp__gov_doctor"
echo "Expected: L1_02_cieu.status == 'active'"
