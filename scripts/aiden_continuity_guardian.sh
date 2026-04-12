#!/bin/bash
# Aiden Continuity Guardian — Autonomous Session Lifecycle Wrapper
# Board-approved 2026-04-12
#
# Wraps Claude Code process with:
# - Continuous health monitoring (event-driven)
# - Graceful save chain on yellow-line threshold
# - Automatic process restart
# - Seamless next-session state injection
#
# Usage:
#   bash scripts/aiden_continuity_guardian.sh [agent_id]
#
# Board override:
#   touch /tmp/ystar_no_auto_restart  — Disable auto-restart
#   rm /tmp/ystar_no_auto_restart     — Re-enable
#
# This wrapper runs OUTSIDE Claude Code. Claude Code agent doesn't know it's wrapped.

YSTAR_DIR="/Users/haotianliu/.openclaw/workspace/ystar-company"
AGENT_ID="${1:-ceo}"

echo "========================================"
echo "  Aiden Continuity Guardian"
echo "  Agent: $AGENT_ID"
echo "  Board override: /tmp/ystar_no_auto_restart"
echo "========================================"
echo ""

cd "$YSTAR_DIR" || exit 1

# === Fail-Safe: Check if override file exists ===
check_override() {
  if [ -f /tmp/ystar_no_auto_restart ]; then
    echo "[GUARDIAN] Auto-restart disabled by Board."
    echo "[GUARDIAN] Remove /tmp/ystar_no_auto_restart to re-enable."
    return 0  # Override active
  fi
  return 1  # No override
}

# === Main Loop: Monitor → Save → Restart ===
while true; do
  echo ""
  echo "=== Starting New Session Cycle ==="
  echo "Time: $(date)"
  echo ""

  # Check override before starting
  if check_override; then
    echo "[GUARDIAN] Exiting due to Board override."
    exit 0
  fi

  # Clean old signals
  rm -f /tmp/ystar_health_yellow /tmp/ystar_ready_for_restart

  # === PHASE 1: Start Claude Code in Background ===
  echo "[GUARDIAN] Starting Claude Code process..."

  # Start claude in background (using 'claude' command from PATH)
  # Redirect output to log file for debugging
  LOG_FILE="$YSTAR_DIR/reports/daily/claude_session_$(date +%Y%m%d_%H%M%S).log"

  # Launch claude with project directory
  cd "$YSTAR_DIR"
  claude &
  CLAUDE_PID=$!

  echo "[GUARDIAN] Claude Code started (PID: $CLAUDE_PID)"
  echo "[GUARDIAN] Session log: $LOG_FILE"
  echo ""

  # Wait for claude to initialize
  sleep 5

  # Check if claude is still running
  if ! kill -0 $CLAUDE_PID 2>/dev/null; then
    echo "[GUARDIAN] ERROR: Claude Code process died immediately."
    echo "[GUARDIAN] Check your claude installation."
    exit 1
  fi

  # === PHASE 2: Start Health Watchdog in Background ===
  echo "[GUARDIAN] Starting health watchdog..."

  python3 "$YSTAR_DIR/scripts/session_health_watchdog.py" &
  WATCHDOG_PID=$!

  echo "[GUARDIAN] Watchdog started (PID: $WATCHDOG_PID)"
  echo ""

  # === PHASE 3: Wait for Yellow Line or Claude Exit ===
  echo "[GUARDIAN] Monitoring session health..."
  echo "[GUARDIAN] Yellow-line thresholds:"
  echo "  - JSONL size: 3.0 MB"
  echo "  - Call count: 500"
  echo "  - Runtime: 6.0 hours"
  echo "  - Hook deny rate: 30%"
  echo "  - Subagent output: 500 KB"
  echo "  - CIEU drift: 3 events"
  echo ""

  # Poll for signals
  while true; do
    # Check if Board override activated
    if check_override; then
      echo "[GUARDIAN] Board override detected. Cleaning up..."
      kill $WATCHDOG_PID 2>/dev/null
      kill $CLAUDE_PID 2>/dev/null
      exit 0
    fi

    # Check if claude process exited
    if ! kill -0 $CLAUDE_PID 2>/dev/null; then
      echo "[GUARDIAN] Claude Code process exited naturally."
      kill $WATCHDOG_PID 2>/dev/null
      break
    fi

    # Check for yellow-line signal
    if [ -f /tmp/ystar_health_yellow ]; then
      echo ""
      echo "[GUARDIAN] ⚠️  YELLOW LINE DETECTED"
      cat /tmp/ystar_health_yellow
      echo ""

      # Kill watchdog (no longer needed)
      kill $WATCHDOG_PID 2>/dev/null
      echo "[GUARDIAN] Watchdog stopped."

      # === PHASE 4: Graceful Save Chain ===
      echo ""
      echo "[GUARDIAN] Initiating graceful save chain..."
      bash "$YSTAR_DIR/scripts/session_graceful_restart.sh" "$AGENT_ID"
      SAVE_EXIT=$?

      if [ $SAVE_EXIT -eq 0 ]; then
        echo "[GUARDIAN] ✓ Save chain completed successfully."
      else
        echo "[GUARDIAN] ⚠  Save chain completed with warnings."
      fi

      # === PHASE 5: Graceful Shutdown of Claude Code ===
      echo ""
      echo "[GUARDIAN] Gracefully stopping Claude Code process..."

      # Send SIGTERM (graceful shutdown)
      kill -TERM $CLAUDE_PID 2>/dev/null

      # Wait up to 10 seconds for graceful exit
      WAIT_COUNT=0
      while kill -0 $CLAUDE_PID 2>/dev/null && [ $WAIT_COUNT -lt 10 ]; do
        sleep 1
        WAIT_COUNT=$((WAIT_COUNT+1))
      done

      # If still running, force kill
      if kill -0 $CLAUDE_PID 2>/dev/null; then
        echo "[GUARDIAN] Process did not exit gracefully. Forcing shutdown..."
        kill -KILL $CLAUDE_PID 2>/dev/null
      else
        echo "[GUARDIAN] ✓ Process exited gracefully."
      fi

      echo ""
      echo "[GUARDIAN] Session cycle complete. Restarting in 3 seconds..."
      sleep 3

      # Loop will restart claude
      break
    fi

    # Sleep briefly before next check
    sleep 5
  done

  # If claude exited naturally (not yellow-line), exit loop
  if [ ! -f /tmp/ystar_health_yellow ]; then
    echo "[GUARDIAN] Session ended naturally. Exiting guardian."
    exit 0
  fi

  # Otherwise, loop continues and restarts claude
done
