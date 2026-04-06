#!/usr/bin/env python3
"""Secretary: Daily task reminder → Telegram.
Runs via crontab at 8:50 Beijing time (0:50 UTC)."""
import os, sys, json, urllib.request, urllib.parse, time

def load_secrets():
    with open(os.path.expanduser("~/.gov_mcp_secrets.env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def send_telegram(text):
    load_secrets()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": "@YstarBridgeLabs", "text": text}).encode()
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("ok", False)
    except:
        return False

def read_tasks():
    tasks_file = os.path.expanduser(
        "~/.openclaw/workspace/ystar-company/knowledge/CURRENT_TASKS.md"
    )
    if not os.path.isfile(tasks_file):
        return "No CURRENT_TASKS.md found."
    with open(tasks_file) as f:
        return f.read()

def main():
    today = time.strftime("%Y-%m-%d")
    day_num = (int(time.time()) - 1742947200) // 86400 + 1  # Day 1 = March 26

    tasks = read_tasks()

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

    msg = f"""📋 Secretary Daily Reminder
📅 {today} · Day {day_num}

━━ Board待决事项 ━━
{chr(10).join(board_items) if board_items else "无待决事项"}

━━ 今日重点 ━━
• CMO: X日更 + Telegram日报
• CSO: Follow 5目标 + 回复3讨论
• CTO: 前端持续优化
• Secretary: 档案索引更新

— Secretary Agent · Y*gov"""

    ok = send_telegram(msg)
    print(f"{'Sent' if ok else 'Failed'}: {today}")

if __name__ == "__main__":
    main()
