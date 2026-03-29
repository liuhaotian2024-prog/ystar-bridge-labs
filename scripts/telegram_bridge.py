"""
Y* Bridge Labs — Telegram Bridge to Mac OpenClaw
Run once to login, then use send_command() to control the Mac.
"""
import asyncio
import sys
from telethon import TelegramClient

API_ID = 31953230
API_HASH = "85981cc76a909256eff111c544e0c363"
BOT_USERNAME = "K9newclaw_bot"
SESSION_FILE = "ystar_telegram_session"

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start(phone="+17033422330")
    print("Login successful!")

    # Send command if provided as argument
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        print(f"Sending: {command}")
        await client.send_message(BOT_USERNAME, command)

        # Wait for response
        print("Waiting for response...")
        await asyncio.sleep(15)

        messages = await client.get_messages(BOT_USERNAME, limit=3)
        for msg in reversed(messages):
            if msg.sender_id != (await client.get_me()).id:
                print(f"\n--- Bot Response ---")
                print(msg.text)
                print(f"--- End ---")
    else:
        print(f"Usage: python {sys.argv[0]} <command to send>")
        print(f'Example: python {sys.argv[0]} "请执行命令：curl ifconfig.me"')

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
