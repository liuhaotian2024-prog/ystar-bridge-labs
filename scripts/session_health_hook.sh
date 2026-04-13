#!/usr/bin/env bash
# Y* Bridge Labs — PostToolUse Health Hook
# Increments call count. Every CHECK_INTERVAL calls, runs watchdog.
# If health is RESTART_NOW, outputs a blocking message to stderr.
#
# Hook contract: stdout = "" means allow, non-empty stderr = user-visible feedback

YSTAR_DIR="/Users/haotianliu/.openclaw/workspace/ystar-company"
CALL_FILE="$YSTAR_DIR/scripts/.session_call_count"
CHECK_INTERVAL=30  # check every 30 tool calls

# Ensure session marker exists
if [ ! -f "$YSTAR_DIR/scripts/.session_booted" ]; then
  touch "$YSTAR_DIR/scripts/.session_booted"
fi

# Read and increment call count
count=0
if [ -f "$CALL_FILE" ]; then
  count=$(cat "$CALL_FILE" 2>/dev/null || echo 0)
fi
count=$((count + 1))
echo "$count" > "$CALL_FILE"

# Only check on interval
if [ $((count % CHECK_INTERVAL)) -ne 0 ]; then
  exit 0
fi

# Extract context_pct from hook input
input=$(cat 2>/dev/null || true)
ctx_pct=""
if [ -n "$input" ]; then
  ctx_pct=$(echo "$input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('context_pct',''))" 2>/dev/null || true)
fi

ctx_arg=""
if [ -n "$ctx_pct" ]; then
  ctx_arg="--context-pct $ctx_pct"
fi

# Run watchdog
result=$(python3 "$YSTAR_DIR/scripts/session_watchdog.py" --quick $ctx_arg 2>/dev/null)
status=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','OK'))" 2>/dev/null || echo "OK")
score=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('score',100))" 2>/dev/null || echo "100")

case "$status" in
  RESTART_NOW)
    # Output warning to stderr — Claude Code shows this to the agent
    cat >&2 <<ALERT

╔══════════════════════════════════════════════════════════╗
║  ⚠️  SESSION HEALTH CRITICAL — Score: ${score}            ║
║                                                          ║
║  MANDATORY: Execute save-and-restart protocol NOW.       ║
║                                                          ║
║  1. python3 scripts/session_close_yml.py ceo "restart"   ║
║  2. bash scripts/session_auto_restart.sh save            ║
║  3. Tell Board: "老大，session需要重启"                    ║
╚══════════════════════════════════════════════════════════╝

ALERT
    ;;
  WARNING)
    # Softer warning every 60 calls when in WARNING
    if [ $((count % 60)) -eq 0 ]; then
      echo "⚠️ Session health: ${score}/100 — consider saving state soon" >&2
    fi
    ;;
esac

exit 0
