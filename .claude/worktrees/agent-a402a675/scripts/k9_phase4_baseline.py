"""K9 Phase 4A: Test baseline assessment system."""
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

    # Step 1: Check what baseline files exist
    print("\n--- Step 1: Find baseline code ---")
    r1 = await send_wait(client, me,
        "Please run: find /tmp/ystar-gov-study/ystar -name '*.py' | xargs grep -l 'retroactive\\|baseline\\|RetroAssessment\\|assess_batch' 2>/dev/null")
    print(f"Files found: {r1[:500]}")

    # Step 2: Test imports
    print("\n--- Step 2: Test baseline imports ---")
    r2 = await send_wait(client, me,
        "Please run this Python command:\n"
        "/opt/homebrew/bin/python3.11 -c \""
        "import sys; sys.path.insert(0, '/tmp/ystar-gov-study'); "
        "from ystar.governance.metalearning import ContractQuality, NormativeObjective, learn; "
        "print('metalearning OK'); "
        "print('ContractQuality:', [f for f in dir(ContractQuality) if not f.startswith('_')]); "
        "print('NormativeObjective:', [f for f in dir(NormativeObjective) if not f.startswith('_')])"
        "\"")
    print(f"Imports: {r2[:1000]}")

    # Step 3: Try CLI retroactive
    print("\n--- Step 3: Try CLI baseline ---")
    r3 = await send_wait(client, me,
        "Please run: cd /tmp/ystar-gov-study && /opt/homebrew/bin/python3.11 -m ystar init 2>&1 | head -20")
    print(f"CLI init: {r3[:1000]}")

    # Step 4: Test metalearning learn() function
    print("\n--- Step 4: Test metalearning learn() ---")
    r4 = await send_wait(client, me,
        "Please run this Python command:\n"
        "/opt/homebrew/bin/python3.11 -c \""
        "import sys; sys.path.insert(0, '/tmp/ystar-gov-study'); "
        "from ystar.governance.metalearning import learn, CallRecord; "
        "print('learn() signature:', learn.__doc__[:200] if learn.__doc__ else 'no doc'); "
        "import inspect; sig = inspect.signature(learn); "
        "print('Parameters:', list(sig.parameters.keys()))"
        "\"")
    print(f"learn(): {r4[:1000]}")

    await client.disconnect()
    print("\nPhase 4A complete!")

asyncio.run(main())
