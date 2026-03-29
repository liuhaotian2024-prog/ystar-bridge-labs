"""K9 Phase 2: Test OmissionEngine + Phase 3: CIEU chain on Mac."""
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

    # Phase 2: OmissionEngine
    print("\n=== PHASE 2: OmissionEngine ===")
    create2 = (
        'Please run this shell command:\n\n'
        'cat > /tmp/test_phase2.py << \'ENDPY\'\n'
        'import sys, time\n'
        'sys.path.insert(0, "/tmp/ystar-gov-study")\n'
        'from ystar.governance.omission_engine import OmissionEngine, OmissionAdapter\n'
        'from ystar.governance.omission_engine import ObligationStatus, Severity\n'
        'results = []\n'
        'def t(name, ok):\n'
        '    s = "PASS" if ok else "FAIL"\n'
        '    results.append((name, s))\n'
        '    print(f"[{s}] {name}")\n'
        '\n'
        '# Test 1: Create engine\n'
        'engine = OmissionEngine()\n'
        't("engine_create", engine is not None)\n'
        '\n'
        '# Test 2: Add obligation\n'
        'engine.add_obligation("agent1", "task_completion", deadline_secs=5.0, required_event_types=["task_completed"])\n'
        'obs = engine.store.list_obligations(entity_id="agent1")\n'
        't("add_obligation", len(obs) >= 1)\n'
        '\n'
        '# Test 3: Check status is PENDING\n'
        'ob = obs[0]\n'
        't("status_pending", ob.status == ObligationStatus.PENDING)\n'
        '\n'
        '# Test 4: Scan before deadline - no violation\n'
        'r = engine.scan(now=time.time())\n'
        't("scan_no_violation", len(r.violations) == 0)\n'
        '\n'
        '# Test 5: Scan after deadline - SOFT_OVERDUE\n'
        'r = engine.scan(now=time.time() + 10)\n'
        'obs2 = engine.store.list_obligations(entity_id="agent1")\n'
        'overdue = [o for o in obs2 if o.status == ObligationStatus.SOFT_OVERDUE]\n'
        't("soft_overdue", len(overdue) >= 1)\n'
        '\n'
        '# Test 6: Fulfill obligation\n'
        'class FakeEvent:\n'
        '    entity_id = "agent1"\n'
        '    event_type = "task_completed"\n'
        '    event_id = "evt1"\n'
        'fulfilled = engine._try_fulfill(FakeEvent())\n'
        't("fulfill", len(fulfilled) >= 1)\n'
        '\n'
        'p = sum(1 for _,s in results if s=="PASS")\n'
        'print(f"PHASE2: {p}/{len(results)} PASSED")\n'
        'ENDPY\n'
        '/opt/homebrew/bin/python3.11 /tmp/test_phase2.py'
    )
    r2 = await send_wait(client, me, create2, timeout=120)
    print(f"Phase 2 Results:\n{r2[:2000]}")

    # Phase 3: CIEU chain
    print("\n=== PHASE 3: CIEU Audit Chain ===")
    create3 = (
        'Please run this shell command:\n\n'
        'cat > /tmp/test_phase3.py << \'ENDPY\'\n'
        'import sys, os, tempfile\n'
        'sys.path.insert(0, "/tmp/ystar-gov-study")\n'
        'from ystar.governance.cieu_store import CIEUStore\n'
        'results = []\n'
        'def t(name, ok):\n'
        '    s = "PASS" if ok else "FAIL"\n'
        '    results.append((name, s))\n'
        '    print(f"[{s}] {name}")\n'
        '\n'
        'db = os.path.join(tempfile.mkdtemp(), "test.db")\n'
        'store = CIEUStore(db_path=db)\n'
        't("create_store", store is not None)\n'
        '\n'
        '# Write records\n'
        'store.write(session_id="s1", seq_local=1, seq_global=1, tool_name="Read", agent_id="test", decision="allow", params_json="{}", contract_hash="abc")\n'
        'store.write(session_id="s1", seq_local=2, seq_global=2, tool_name="Bash", agent_id="test", decision="deny", params_json="{}", contract_hash="abc")\n'
        'store.write(session_id="s1", seq_local=3, seq_global=3, tool_name="Write", agent_id="test", decision="allow", params_json="{}", contract_hash="abc")\n'
        't("write_records", True)\n'
        '\n'
        '# Query\n'
        'total = store.count_decisions(session_id="s1")\n'
        't("count_decisions", total == 3)\n'
        '\n'
        '# Seal session\n'
        'root = store.seal_session("s1")\n'
        't("seal_session", root is not None and len(root) > 0)\n'
        'print(f"  Merkle root: {root[:32]}...")\n'
        '\n'
        '# Verify sealed session\n'
        'valid = store.verify_session_seal("s1")\n'
        't("verify_seal", valid)\n'
        '\n'
        'p = sum(1 for _,s in results if s=="PASS")\n'
        'print(f"PHASE3: {p}/{len(results)} PASSED")\n'
        'ENDPY\n'
        '/opt/homebrew/bin/python3.11 /tmp/test_phase3.py'
    )
    r3 = await send_wait(client, me, create3, timeout=120)
    print(f"Phase 3 Results:\n{r3[:2000]}")

    await client.disconnect()
    print("\nAll phases complete!")

asyncio.run(main())
