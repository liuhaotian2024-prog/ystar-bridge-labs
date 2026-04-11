"""
K9 Scout Inbox — Read all unprocessed messages from K9.
Run periodically to check for intelligence reports and test results.
Usage: python scripts/k9_inbox.py [--reply "message"]
"""
import asyncio
import sys
import json
import os
from datetime import datetime
from telethon import TelegramClient

SESSION = "/Users/haotianliu/.openclaw/workspace/ystar-company/ystar_telegram_session"
API_ID = 31953230
API_HASH = "85981cc76a909256eff111c544e0c363"
PHONE = "+17033422330"
LAST_READ_FILE = r"C:\Users\liuha\OneDrive\桌面\ystar-company\scripts\.k9_last_read"

def get_last_read_id():
    if os.path.exists(LAST_READ_FILE):
        with open(LAST_READ_FILE) as f:
            return int(f.read().strip())
    return 0

def save_last_read_id(msg_id):
    with open(LAST_READ_FILE, "w") as f:
        f.write(str(msg_id))

async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start(phone=PHONE)
    me = await client.get_me()

    # Check for reply mode
    if len(sys.argv) > 2 and sys.argv[1] == "--reply":
        reply_text = " ".join(sys.argv[2:])
        msg = await client.send_message("K9newclaw_bot", reply_text)
        print(f"Sent to K9: {reply_text[:100]}...")
        await client.disconnect()
        return

    # Read new messages since last check
    last_id = get_last_read_id()
    msgs = await client.get_messages("K9newclaw_bot", limit=20)

    new_msgs = []
    for m in reversed(msgs):
        if m.id > last_id and m.sender_id != me.id:
            new_msgs.append(m)

    if not new_msgs:
        print("K9 Inbox: No new messages.")
    else:
        print(f"K9 Inbox: {len(new_msgs)} new message(s)\n")
        for m in new_msgs:
            ts = m.date.strftime("%Y-%m-%d %H:%M")
            print(f"--- [{ts}] Message #{m.id} ---")
            print(m.text[:2000] if m.text else "(no text)")
            print()

    # Save highest message ID
    if msgs:
        max_id = max(m.id for m in msgs)
        save_last_read_id(max_id)
        print(f"(Saved read pointer: msg #{max_id})")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
