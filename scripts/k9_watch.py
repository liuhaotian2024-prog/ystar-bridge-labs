"""
K9 Watch — Real-time message listener for K9 Scout.
Runs continuously, prints new messages as they arrive.
Usage: python scripts/k9_watch.py
Press Ctrl+C to stop.
"""
import asyncio
from telethon import TelegramClient, events

SESSION = r"C:\Users\liuha\OneDrive\桌面\ystar_mac_bridge"
API_ID = 31953230
API_HASH = "85981cc76a909256eff111c544e0c363"
PHONE = "+17033422330"
BOT_USERNAME = "K9newclaw_bot"

async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start(phone=PHONE)
    me = await client.get_me()

    bot_entity = await client.get_entity(BOT_USERNAME)
    print(f"[K9 Watch] Listening for K9 Scout messages...")
    print(f"[K9 Watch] Press Ctrl+C to stop.\n")

    @client.on(events.NewMessage(from_users=bot_entity.id))
    async def handler(event):
        ts = event.date.strftime("%H:%M:%S")
        text = event.text[:500] if event.text else "(no text)"
        print(f"\n{'='*60}")
        print(f"[K9 {ts}] NEW MESSAGE (#{event.id})")
        print(f"{'='*60}")
        print(text)
        if event.text and len(event.text) > 500:
            print(f"... ({len(event.text)} chars total)")
        print()

    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[K9 Watch] Stopped.")
