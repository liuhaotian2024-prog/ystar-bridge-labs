#!/bin/bash
# Y* Bridge Labs — Ensure Crontab Entries (Idempotent)
# Called by LaunchAgent at boot to restore crontab entries

REPO_ROOT="/Users/haotianliu/.openclaw/workspace/ystar-company"
TEMP_CRON="/tmp/ystar_crontab_$$"

# Define required entries (must match current active crontab)
REQUIRED_ENTRIES=(
    "50 0 * * * cd $REPO_ROOT && /usr/bin/python3 secretary/daily_reminder.py >> /tmp/secretary_daily.log 2>&1"
    "*/5 * * * * cd $REPO_ROOT && /usr/bin/python3 secretary/commit_watcher.py >> /tmp/secretary_watcher.log 2>&1"
    "23 */3 * * * $REPO_ROOT/scripts/ystar_wakeup.sh learning >> /tmp/ystar_learning.log 2>&1"
    "47 8 * * * $REPO_ROOT/scripts/ystar_wakeup.sh morning_report >> /tmp/ystar_morning.log 2>&1"
    "37 22 * * * $REPO_ROOT/scripts/ystar_wakeup.sh twin >> /tmp/ystar_twin.log 2>&1"
    "13 9 * * * $REPO_ROOT/scripts/ystar_wakeup.sh intel >> /tmp/ystar_intel.log 2>&1"
    "57 21 * * * $REPO_ROOT/scripts/ystar_wakeup.sh mission_report >> /tmp/ystar_mission.log 2>&1"
    "17 */2 * * * $REPO_ROOT/scripts/session_auto_restart.sh check >> /tmp/ystar_session_health.log 2>&1"
    "*/30 * * * * bash $REPO_ROOT/scripts/governance_boot.sh ceo --verify-only >> /tmp/ystar_gov_verify.log 2>&1"
    "0 6 * * * /usr/bin/python3 $REPO_ROOT/scripts/publish_morning_to_readme.py >> /tmp/readme_morning.log 2>&1"
)

echo "=== Y* Crontab Sync $(date) ==="

# Get current crontab
crontab -l 2>/dev/null > "$TEMP_CRON"

ADDED=0
for entry in "${REQUIRED_ENTRIES[@]}"; do
    if ! grep -qF "$entry" "$TEMP_CRON"; then
        echo "$entry" >> "$TEMP_CRON"
        echo "[ADD] $entry"
        ADDED=$((ADDED + 1))
    fi
done

if [ $ADDED -gt 0 ]; then
    crontab "$TEMP_CRON"
    echo "✓ Added $ADDED new crontab entries"
else
    echo "✓ All crontab entries already present"
fi

rm -f "$TEMP_CRON"
