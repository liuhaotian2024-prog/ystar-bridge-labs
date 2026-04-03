"""Deploy AGENTS.md to Mac and start first intelligence task."""
import asyncio
from telethon import TelegramClient

SESSION = r"C:\Users\liuha\OneDrive\桌面\ystar_mac_bridge"

async def send_and_wait(client, me, text, timeout=45):
    msg = await client.send_message("K9newclaw_bot", text)
    for i in range(timeout):
        await asyncio.sleep(1)
        msgs = await client.get_messages("K9newclaw_bot", limit=3, min_id=msg.id)
        for m in msgs:
            if m.sender_id != me.id:
                return m.text
    return None

async def main():
    client = TelegramClient(SESSION, 31953230, "85981cc76a909256eff111c544e0c363")
    await client.start(phone="+17033422330")
    me = await client.get_me()
    print(f"Connected as {me.first_name}")

    # Step 1: Deploy AGENTS.md
    print("\n--- Step 1: Deploying AGENTS.md ---")
    cmd1 = (
        'Please write the following content to a file called AGENTS.md in your working directory:\n\n'
        '# AGENTS.md - Y* Bridge Labs Mac Outpost\n'
        '# Governed by Y*gov\n\n'
        '## Agent: K9 Scout\n'
        '## Role: Intelligence gathering for Y* Bridge Labs\n\n'
        '## Permitted: web search, file read/write, shell commands, browser automation\n'
        '## Prohibited: rm -rf, sudo, /etc access, sending emails, credential access\n\n'
        '## Daily Tasks:\n'
        '1. Search HN for AI governance discussions\n'
        '2. Search Reddit for AI agent pain points\n'
        '3. Check github.com/liuhaotian2024-prog/Y-star-gov stats\n'
        '4. Track Proofpoint and Microsoft agent-governance updates\n'
        '5. Report findings via Telegram'
    )
    resp = await send_and_wait(client, me, cmd1)
    print(f"Response: {resp[:500] if resp else 'No response'}")

    # Step 2: Run ystar doctor to confirm governance
    print("\n--- Step 2: Verify Y*gov governance ---")
    resp2 = await send_and_wait(client, me, "Please run: /opt/homebrew/bin/python3.11 -m ystar doctor")
    print(f"Response: {resp2[:500] if resp2 else 'No response'}")

    # Step 3: First intelligence task
    print("\n--- Step 3: First intelligence task ---")
    cmd3 = (
        'Please search the web for the following and give me a summary:\n'
        '1. Any Hacker News posts from the last 7 days about "AI agent governance" or "AI agent audit"\n'
        '2. Current star count of github.com/liuhaotian2024-prog/Y-star-gov\n'
        '3. Any recent news about Proofpoint Agent Integrity Framework'
    )
    resp3 = await send_and_wait(client, me, cmd3, timeout=60)
    print(f"Response: {resp3[:1500] if resp3 else 'No response'}")

    await client.disconnect()
    print("\nDone!")

asyncio.run(main())
