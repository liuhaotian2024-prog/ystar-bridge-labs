"""
K9 Scout Command Interface — Send commands to Mac OpenClaw via Telegram.
Usage: python scripts/k9.py "your command here"
Session pre-authenticated. No login needed.
"""
import asyncio
import sys
from telethon import TelegramClient

SESSION = r"C:\Users\liuha\OneDrive\桌面\ystar_mac_bridge"
API_ID = 31953230
API_HASH = "85981cc76a909256eff111c544e0c363"
PHONE = "+17033422330"

async def k9(command, timeout=60):
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start(phone=PHONE)
    me = await client.get_me()
    msg = await client.send_message("K9newclaw_bot", command)
    for i in range(timeout):
        await asyncio.sleep(1)
        msgs = await client.get_messages("K9newclaw_bot", limit=5, min_id=msg.id)
        for m in msgs:
            if m.sender_id != me.id:
                await client.disconnect()
                return m.text
    await client.disconnect()
    return None

async def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts/k9.py "command"')
        return
    cmd = " ".join(sys.argv[1:])
    print(f">>> K9 Scout: {cmd}")
    resp = await k9(cmd)
    if resp:
        print(resp)
    else:
        print("No response (Mac may be asleep)")

if __name__ == "__main__":
    asyncio.run(main())
