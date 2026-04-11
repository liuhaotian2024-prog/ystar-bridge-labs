#!/bin/bash
# Y* Bridge Labs — Agent Wake-Up Script
# 用途：系统crontab调用，自动启动Claude Code执行空闲学习或晨检
# 安装：crontab -e 添加以下行（每3小时跑一次）：
#   23 */3 * * * /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ystar_wakeup.sh learning
#   47 8 * * *   /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ystar_wakeup.sh morning_report
#   37 22 * * *  /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ystar_wakeup.sh twin
#
# Board授权后执行: chmod +x scripts/ystar_wakeup.sh && crontab -e

YSTAR_DIR="/Users/haotianliu/.openclaw/workspace/ystar-company"
LOG_DIR="$YSTAR_DIR/reports/daily"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

mkdir -p "$LOG_DIR"

case "$1" in
  learning)
    # 轮换角色（基于小时数取模）
    HOUR=$(date +%H)
    ROLES=("cto" "cmo" "cfo" "cso" "secretary" "ceo")
    IDX=$(( HOUR / 3 % 6 ))
    ROLE=${ROLES[$IDX]}

    echo "[$DATE $TIME] Starting idle learning for $ROLE" >> "$LOG_DIR/wakeup.log"

    cd "$YSTAR_DIR"
    if [ -f scripts/idle_learning.py ]; then
      python3 scripts/idle_learning.py --actor "$ROLE" --priority all >> "$LOG_DIR/wakeup.log" 2>&1
    else
      echo "[$DATE $TIME] idle_learning.py not found, skipping" >> "$LOG_DIR/wakeup.log"
    fi
    ;;

  morning_report)
    echo "[$DATE $TIME] Generating morning report" >> "$LOG_DIR/wakeup.log"

    cd "$YSTAR_DIR"
    if [ -f scripts/learning_report.py ]; then
      python3 scripts/learning_report.py > "$LOG_DIR/${DATE}_morning.md" 2>&1
    fi

    # 也统计CIEU
    python3 -c "
import sqlite3, json
from datetime import datetime, timedelta
db = sqlite3.connect('.ystar_cieu.db')
now = datetime.now().timestamp()
day_ago = now - 86400
count = db.execute('SELECT COUNT(*) FROM cieu_events WHERE created_at > ?', (day_ago,)).fetchone()[0]
print(f'CIEU events (24h): {count}')
db.close()
" >> "$LOG_DIR/${DATE}_morning.md" 2>&1

    echo "[$DATE $TIME] Morning report saved to $LOG_DIR/${DATE}_morning.md" >> "$LOG_DIR/wakeup.log"
    ;;

  twin)
    echo "[$DATE $TIME] Starting Digital Twin Evolution" >> "$LOG_DIR/wakeup.log"

    cd "$YSTAR_DIR"
    if [ -f scripts/twin_evolution.py ]; then
      python3 scripts/twin_evolution.py --mode all >> "$LOG_DIR/wakeup.log" 2>&1
    else
      echo "[$DATE $TIME] twin_evolution.py not found, skipping" >> "$LOG_DIR/wakeup.log"
    fi

    # Generate twin report
    if [ -f scripts/twin_report.py ]; then
      python3 scripts/twin_report.py > "$LOG_DIR/${DATE}_twin_evolution.md" 2>&1
      echo "[$DATE $TIME] Twin evolution report saved to $LOG_DIR/${DATE}_twin_evolution.md" >> "$LOG_DIR/wakeup.log"
    fi
    ;;

  *)
    echo "Usage: $0 {learning|morning_report|twin}"
    exit 1
    ;;
esac
