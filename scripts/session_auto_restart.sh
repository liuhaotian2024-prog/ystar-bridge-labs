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

    echo "[$DATE $TIME] Session state saved. Ready for restart." >> "$LOG_DIR/wakeup.log"
    echo "STATE_SAVED"
    ;;

  verify)
    # After restart, verify state was loaded correctly
    cd "$YSTAR_DIR"

    echo "=== Verification ==="

    # Check YML memories loaded
    MEMORIES=$(python3 -c "
import sys; sys.path.insert(0,'/Users/haotianliu/.openclaw/workspace/Y-star-gov')
from ystar.memory import MemoryStore
s = MemoryStore(db_path='.ystar_memory.db')
total = sum(s.get_agent_summary(a)['total_memories'] for a in ['ceo','cto','cmo','cfo','cso','secretary'])
print(total)
" 2>/dev/null)
    echo "YML memories: $MEMORIES"

    # Check session handoff
    echo "session_handoff.md: $(wc -l < memory/session_handoff.md 2>/dev/null) lines"

    # Check CIEU
    CIEU=$(python3 -c "
import sqlite3
db = sqlite3.connect('.ystar_cieu.db')
print(db.execute('SELECT COUNT(*) FROM cieu_events').fetchone()[0])
db.close()
" 2>/dev/null)
    echo "CIEU events: $CIEU"

    # Check cron jobs
    echo "Cron jobs: $(crontab -l 2>/dev/null | grep ystar | wc -l)"

    echo "=== Verification Complete ==="
    ;;

  *)
    echo "Usage: $0 {check|save|verify}"
    echo "  check  — Check if session needs restart"
    echo "  save   — Save all state before restart"
    echo "  verify — After restart, verify state integrity"
    exit 1
    ;;
esac
