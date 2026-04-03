"""K9 Phase 1: Test check() engine on Mac."""
import asyncio
from telethon import TelegramClient

SESSION = r"C:\Users\liuha\OneDrive\桌面\ystar_mac_bridge"

async def send_wait(client, me, text, timeout=90):
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
    print("Connected to K9 Scout.")

    # Create test script
    print("\n--- Creating test script on Mac ---")
    create_cmd = (
        'Please run this shell command:\n\n'
        'cat > /tmp/test_phase1.py << \'ENDPY\'\n'
        'import sys\n'
        'sys.path.insert(0, "/tmp/ystar-gov-study")\n'
        'from ystar import check, IntentContract\n'
        'results = []\n'
        'def t(name, contract, params, expect_deny):\n'
        '    r = check(params, {}, contract)\n'
        '    ok = (not r.passed) if expect_deny else r.passed\n'
        '    s = "PASS" if ok else "FAIL"\n'
        '    results.append((name, s))\n'
        '    print(f"[{s}] {name}")\n'
        't("deny_path", IntentContract(deny=["/etc"]), {"file_path":"/etc/passwd"}, True)\n'
        't("deny_cmd", IntentContract(deny_commands=["rm -rf"]), {"command":"rm -rf /"}, True)\n'
        't("only_paths_allow", IntentContract(only_paths=["./ws"]), {"file_path":"./ws/f.txt"}, False)\n'
        't("only_paths_deny", IntentContract(only_paths=["./ws"]), {"file_path":"/secret"}, True)\n'
        't("traversal_FIX1", IntentContract(only_paths=["./ws"]), {"file_path":"./ws/../../etc"}, True)\n'
        't("domain_allow", IntentContract(only_domains=["github.com"]), {"url":"https://github.com/r"}, False)\n'
        't("domain_deny", IntentContract(only_domains=["github.com"]), {"url":"https://evil.com"}, True)\n'
        't("invariant_pass", IntentContract(invariant=["amount < 5000"]), {"amount":3000}, False)\n'
        't("invariant_fail", IntentContract(invariant=["amount < 5000"]), {"amount":9999}, True)\n'
        't("no_restrict", IntentContract(), {"file_path":"/any"}, False)\n'
        'p = sum(1 for _,s in results if s=="PASS")\n'
        'print(f"PHASE1: {p}/{len(results)} PASSED")\n'
        'ENDPY\n'
        'echo "Script created OK"'
    )
    r1 = await send_wait(client, me, create_cmd)
    print(f"Create: {r1[:300]}")

    # Run test
    print("\n--- Running Phase 1 tests ---")
    r2 = await send_wait(client, me, "Please run: /opt/homebrew/bin/python3.11 /tmp/test_phase1.py")
    print(f"Results:\n{r2[:2000]}")

    await client.disconnect()

asyncio.run(main())
