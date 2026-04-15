#!/usr/bin/env python3
"""Secretary: Daily task reminder → Telegram.
Runs via crontab at 06:00 America/New_York (EST/EDT auto-adjust).

Board 2026-04-15 directive: time target = 美东 06:00 (not 北京 08:50).
Delivery path unified via scripts/telegram_notify.send_daily (3-channel module).
"""
import os, sys, time

# Make scripts/ importable when invoked from crontab
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
from telegram_notify import send_daily  # noqa: E402

def read_tasks():
    tasks_file = os.path.expanduser(
        "~/.openclaw/workspace/ystar-company/knowledge/CURRENT_TASKS.md"
    )
    if not os.path.isfile(tasks_file):
        return "No CURRENT_TASKS.md found."
    with open(tasks_file) as f:
        return f.read()

def check_temp_laws():
    """Check for active Temp Laws in governance/TEMP_LAW.md"""
    tl_file = os.path.expanduser(
        "~/.openclaw/workspace/ystar-company/governance/TEMP_LAW.md"
    )
    if not os.path.isfile(tl_file):
        return 0, []
    with open(tl_file) as f:
        content = f.read()
    active = []
    for line in content.split("\n"):
        if line.startswith("### TL-") and "执行中" in content[content.index(line):content.index(line)+500]:
            active.append(line.strip())
    return len(active), active


def main():
    # Use ET timezone (Board 2026-04-15: target send time = 06:00 America/New_York)
    os.environ['TZ'] = 'America/New_York'
    try:
        time.tzset()
    except AttributeError:
        pass  # Windows doesn't have tzset

    # Gate: only send at 06:XX ET unless --force or --dry-run given.
    # Cron runs this hourly; script self-gates → DST-safe without CRON_TZ.
    et_hour = int(time.strftime("%H"))
    if et_hour != 6 and "--force" not in sys.argv and "--dry-run" not in sys.argv:
        print(f"[daily_reminder] skip: ET hour={et_hour} (target=6)")
        return

    today = time.strftime("%Y-%m-%d %H:%M ET")
    day_num = (int(time.time()) - 1742961600) // 86400 + 1  # Day 1 = March 26 UTC

    tasks = read_tasks()

    # Check Temp Laws
    tl_count, tl_items = check_temp_laws()

    # Extract Board pending items
    board_items = []
    in_board = False
    for line in tasks.split("\n"):
        if "Board待决" in line:
            in_board = True
            continue
        if in_board and line.startswith("|") and "待" in line:
            board_items.append(line.strip())
        if in_board and line.strip() == "" and board_items:
            in_board = False

    # Temp Law alert
    tl_alert = ""
    if tl_count > 0:
        tl_alert = f"\n⚖️ 当前有{tl_count}条临时约法生效中，请各Agent优先处理。\n"

    msg = f"""📋 Secretary Daily Reminder
📅 {today} · Day {day_num}
{tl_alert}

━━ Board待决事项 ━━
{chr(10).join(board_items) if board_items else "无待决事项"}

━━ 今日重点 ━━
• CMO: X日更 + Telegram日报
• CSO: Follow 5目标 + 回复3讨论
• CTO: 前端持续优化
• Secretary: 档案索引更新

— Secretary Agent · Y*gov"""

    dry = "--dry-run" in sys.argv
    ok = send_daily(msg, dry_run=dry)
    print(f"{'Sent' if ok else 'Failed'}: {today}")

if __name__ == "__main__":
    main()
