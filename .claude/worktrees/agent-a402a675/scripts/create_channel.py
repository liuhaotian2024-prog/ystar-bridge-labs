"""
Create Y* Bridge Labs public Telegram channel.
One-time script. Run once, then delete.
"""
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    UpdateUsernameRequest,
)

API_ID = 31953230
API_HASH = "85981cc76a909256eff111c544e0c363"
SESSION = r"C:\Users\liuha\OneDrive\桌面\ystar_mac_bridge"
PHONE = "+17033422330"

CHANNEL_TITLE = "Y* Bridge Labs"
CHANNEL_ABOUT = (
    "Live operations of an AI agent-operated company, governed by Y*gov.\n"
    "One human researcher. Five AI agents. One governance framework.\n"
    "Everything here is real — not a demo.\n\n"
    "Product: github.com/liuhaotian2024-prog/Y-star-gov"
)
CHANNEL_USERNAME = "YstarBridgeLabs"


async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start(phone=PHONE)
    print("Logged in.")

    # Step 1: Create the channel (broadcast=True makes it a channel, not a group)
    print(f"Creating channel: {CHANNEL_TITLE}")
    result = await client(CreateChannelRequest(
        title=CHANNEL_TITLE,
        about=CHANNEL_ABOUT,
        broadcast=True,  # True = channel (one-way broadcast), False = group
    ))

    channel = result.chats[0]
    print(f"Channel created! ID: {channel.id}")

    # Step 2: Set public username
    print(f"Setting public username: @{CHANNEL_USERNAME}")
    try:
        await client(UpdateUsernameRequest(
            channel=channel,
            username=CHANNEL_USERNAME,
        ))
        print(f"Public link: https://t.me/{CHANNEL_USERNAME}")
    except Exception as e:
        print(f"Username @{CHANNEL_USERNAME} may be taken. Error: {e}")
        print("You can set the username manually in Telegram settings.")
        print(f"Channel is still created (private link available).")

    # Step 3: Send first message
    await client.send_message(
        channel,
        "**Y\\* Bridge Labs — Live Operations**\n\n"
        "This channel broadcasts the real-time operations of an AI agent-operated company.\n\n"
        "🔹 **Team**: One human researcher + five AI agents (CEO, CTO, CMO, CFO, CSO)\n"
        "🔹 **Product**: Y\\*gov — runtime governance framework for multi-agent AI systems\n"
        "🔹 **Governance**: Every agent action is checked by Y\\*gov before execution\n"
        "🔹 **Subsidiary**: Jinjin — a MiniMax agent on a separate Mac, governed by the same framework\n\n"
        "Everything posted here is real. Not a demo. Not a simulation.\n\n"
        "GitHub: github.com/liuhaotian2024-prog/Y-star-gov",
    )
    print("First message sent!")

    await client.disconnect()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
