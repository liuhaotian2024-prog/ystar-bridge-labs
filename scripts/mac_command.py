"""
Send a command to Mac's OpenClaw via Telegram and get response.
Usage: python mac_command.py "your command here"
Session already authenticated - no login needed.
"""
import asyncio
import sys
import time
from telethon import TelegramClient

API_ID = 31953230
API_HASH = "85981cc76a909256eff111c544e0c363"
BOT_USERNAME = "K9newclaw_bot"
# Use the session file created during login
SESSION_FILE = r"C:\Users\liuha\OneDrive\桌面\ystar_mac_bridge"

async def send_and_wait(command, wait_secs=30):
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start(phone="+17033422330")
    me = await client.get_me()

    # Remember timestamp before sending
    before = time.time()

    # Send command
    await client.send_message(BOT_USERNAME, command)
    print(f"Sent: {command}")
    print(f"Waiting up to {wait_secs}s for response...")

    # Poll for new response
    for i in range(wait_secs):
        await asyncio.sleep(1)
        messages = await client.get_messages(BOT_USERNAME, limit=5)
        for msg in messages:
            if msg.sender_id != me.id and msg.date.timestamp() > before - 5:
                print(f"\n=== Mac Response ===")
                print(msg.text)
                print(f"=== End ===")
                await client.disconnect()
                return msg.text

    print("No response received within timeout.")
    await client.disconnect()
    return None

async def main():
    if len(sys.argv) < 2:
        print('Usage: python mac_command.py "your command"')
        return
    command = " ".join(sys.argv[1:])
    await send_and_wait(command)

if __name__ == "__main__":
    asyncio.run(main())
