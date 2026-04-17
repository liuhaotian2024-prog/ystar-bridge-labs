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
    IDX=$(( 10#$HOUR / 3 % 6 ))
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

  intel)
    echo "[$DATE $TIME] Starting CSO Intelligence Scan" >> "$LOG_DIR/wakeup.log"

    cd "$YSTAR_DIR"
    # Step 1: Jinjin scans (via Telegram if available)
    if [ -f scripts/k9.py ]; then
      python3 scripts/k9.py "search: AI governance news today" >> "$LOG_DIR/wakeup.log" 2>&1 || true
    fi

    # Step 2: Generate intel report via Gemma
    if [ -f scripts/local_learn.py ]; then
      python3.11 scripts/local_learn.py --mode questions --actor cso --task "AI governance market intelligence: what happened today in AI safety, AI governance, prompt injection defense, multi-agent systems" >> "$LOG_DIR/wakeup.log" 2>&1 || true
    fi

    echo "[$DATE $TIME] Intel scan complete" >> "$LOG_DIR/wakeup.log"
    ;;

  mission_report)
    echo "[$DATE $TIME] Generating Daily Mission Report" >> "$LOG_DIR/wakeup.log"
    cd "$YSTAR_DIR"
    
    # Generate comprehensive mission report
    cat > "$LOG_DIR/${DATE}_mission_report.md" << REPORT
# Y* Bridge Labs 每日任务进程报告
**日期**: $DATE
**生成**: CEO Aiden (自动)

## 一、今日计划 vs 实际完成
（由CEO在每日结束时填写）

## 二、各产品线进度
### ystar-defuse
- MVP状态：
- 测试通过率：
- 距离PyPI发布：

### 冒犯了AI脱口秀
- Episode进度：
- 视频生成状态：

### Y*gov核心
- behavior rules：
- 测试总数：

## 三、明日计划

## 四、需要Board关注的事项

## 五、团队健康度
$(python3 scripts/learning_report.py 2>/dev/null || echo "报告脚本未就绪")
REPORT

    echo "[$DATE $TIME] Mission report saved to $LOG_DIR/${DATE}_mission_report.md" >> "$LOG_DIR/wakeup.log"
    ;;

  *)
    echo "Usage: $0 {learning|morning_report|twin|intel|mission_report}"
    exit 1
    ;;
esac
