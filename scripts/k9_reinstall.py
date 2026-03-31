"""K9: Reinstall Y*gov with baseline fix and verify."""
import asyncio
from telethon import TelegramClient

SESSION = r"C:\Users\liuha\OneDrive\桌面\ystar_mac_bridge"

async def send_wait(client, me, text, timeout=120):
    msg = await client.send_message("K9newclaw_bot", text)
    for i in range(timeout):
        await asyncio.sleep(1)
        msgs = await client.get_messages("K9newclaw_bot", limit=5, min_id=msg.id)
        for m in msgs:
            if m.sender_id != me.id:
                return m.text
        if i % 30 == 29:
            print(f"  Waiting... {i+1}s")
    return "NO RESPONSE"

async def main():
    client = TelegramClient(SESSION, 31953230, "85981cc76a909256eff111c544e0c363")
    await client.start(phone="+17033422330")
    me = await client.get_me()
    print("Connected.")

    print("\n=== Step 1: Force reinstall from latest GitHub ===")
    r1 = await send_wait(client, me,
        "Please run: /opt/homebrew/bin/pip3.11 install --force-reinstall --no-cache-dir git+https://github.com/liuhaotian2024-prog/Y-star-gov.git 2>&1 | tail -5")
    print(r1[:500] if r1 else "NO RESPONSE")

    print("\n=== Step 2: Clean old files ===")
    r2 = await send_wait(client, me,
        "Please run: rm -f .ystar_session.json .ystar_cieu.db .ystar_retro_baseline.db && echo Old files cleaned")
    print(r2[:300] if r2 else "NO RESPONSE")

    print("\n=== Step 3: Fresh ystar setup ===")
    r3 = await send_wait(client, me,
        "Please run: /opt/homebrew/bin/python3.11 -m ystar setup --yes 2>&1")
    print(r3[:1500] if r3 else "NO RESPONSE")

    print("\n=== Step 4: Check for baseline file ===")
    r4 = await send_wait(client, me,
        "Please run: ls -la .ystar_retro* .ystar_baseline* .ystar_cieu* .ystar_session* 2>/dev/null && echo Files found || echo No baseline files")
    print(r4[:500] if r4 else "NO RESPONSE")

    print("\n=== Step 5: Run doctor ===")
    r5 = await send_wait(client, me,
        "Please run: /opt/homebrew/bin/python3.11 -m ystar doctor 2>&1")
    print(r5[:1000] if r5 else "NO RESPONSE")

    await client.disconnect()
    print("\nDone!")

asyncio.run(main())
