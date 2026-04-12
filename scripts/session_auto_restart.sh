#!/bin/bash
# Y* Bridge Labs — Session Auto-Restart Script
# 用途：检测session退化→保存状态→重启→验证
# 可由cron调用或agent手动触发
#
# crontab建议（每2小时检查一次）：
# 17 */2 * * * /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/session_auto_restart.sh check

YSTAR_DIR="/Users/haotianliu/.openclaw/workspace/ystar-company"
LOG_DIR="$YSTAR_DIR/reports/daily"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

case "$1" in
  check)
    # Check if current session needs restart
    # Proxy: if .session_booted exists and is older than 6 hours → suggest restart
    if [ -f "$YSTAR_DIR/scripts/.session_booted" ]; then
      AGE=$(( $(date +%s) - $(stat -f %m "$YSTAR_DIR/scripts/.session_booted") ))
      HOURS=$(( AGE / 3600 ))

      if [ $HOURS -ge 6 ]; then
        echo "[$DATE $TIME] WARNING: Session running for ${HOURS}h. Restart recommended." >> "$LOG_DIR/wakeup.log"
        echo "SESSION_RESTART_RECOMMENDED: ${HOURS}h elapsed"
      else
        echo "SESSION_OK: ${HOURS}h elapsed"
      fi
    else
      echo "NO_ACTIVE_SESSION"
    fi
    ;;

  save)
    # Save all state before restart
    echo "[$DATE $TIME] Saving session state..." >> "$LOG_DIR/wakeup.log"

    cd "$YSTAR_DIR"

    # Run session close
    if [ -f scripts/session_close_yml.py ]; then
      python3 scripts/session_close_yml.py ceo "Auto-restart: session exceeded health threshold" 2>&1 || true
    fi

    # Run twin evolution
    if [ -f scripts/twin_evolution.py ]; then
      python3.11 scripts/twin_evolution.py --mode all 2>&1 || true
    fi

    # Update learning report
    if [ -f scripts/learning_report.py ]; then
      python3 scripts/learning_report.py > "$LOG_DIR/${DATE}_learning.md" 2>&1 || true
    fi

    # Git commit all changes
    git add -A 2>/dev/null
    git commit -m "auto: session state saved before restart [$(date +%H:%M)]" 2>/dev/null || true
    git push 2>/dev/null || true

    # Clean session markers
    rm -f scripts/.session_booted scripts/.session_call_count

    # NEW: active_agent home state cleanup (方案 C)
    CURRENT_MARKER=$(cat ".ystar_active_agent" 2>/dev/null || echo "")
    if [ -n "$CURRENT_MARKER" ] && [ "$CURRENT_MARKER" != "ceo" ]; then
      echo "[CLEANUP] session close with active_agent='$CURRENT_MARKER', resetting to ceo"
      echo "ceo" > ".ystar_active_agent"
    fi

    echo "[$DATE $TIME] Session state saved. Ready for restart." >> "$LOG_DIR/wakeup.log"
    echo "STATE_SAVED"
    ;;

  verify)
    # After restart: delegate to governance_boot.sh (single source of truth)
    AGENT_ID="${2:-ceo}"
    echo "=== Post-Restart Verification (delegating to governance_boot.sh) ==="

    # Show session handoff summary first
    echo "--- Session Handoff Summary ---"
    if [ -f "$YSTAR_DIR/memory/session_handoff.md" ]; then
      head -30 "$YSTAR_DIR/memory/session_handoff.md"
      echo "... ($(wc -l < "$YSTAR_DIR/memory/session_handoff.md") total lines)"
    fi
    echo ""

    # Delegate full boot + verification to governance_boot.sh
    bash "$YSTAR_DIR/scripts/governance_boot.sh" "$AGENT_ID"
    BOOT_EXIT=$?

    echo ""
    echo "=== Verification Complete (governance_boot exit: $BOOT_EXIT) ==="
    ;;

  *)
    echo "Usage: $0 {check|save|verify}"
    echo "  check  — Check if session needs restart"
    echo "  save   — Save all state before restart"
    echo "  verify — After restart, verify state integrity"
    exit 1
    ;;
esac
