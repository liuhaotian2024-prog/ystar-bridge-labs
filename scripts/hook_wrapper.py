"""
Y*gov hook wrapper — captures ALL errors to a log file.
This replaces the inline -c command to diagnose silent failures.
"""
import json
import sys
import os
import traceback

LOG = os.path.join(os.path.dirname(__file__), "hook_debug.log")

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        import time
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

try:
    # ── Session Boot Check ──────────────────────────────────────────────
    # Detects if CEO has completed the mandatory boot protocol.
    # Boot flag is written by the first successful handoff read.
    # If missing after 5+ tool calls in this session, inject a reminder.
    session_id_env = os.environ.get("CLAUDE_SESSION_ID", "")
    boot_flag = os.path.join(os.path.dirname(__file__), ".session_booted")
    call_counter = os.path.join(os.path.dirname(__file__), ".session_call_count")

    # Increment call counter for this session
    try:
        count = int(open(call_counter, "r").read().strip()) if os.path.exists(call_counter) else 0
    except Exception:
        count = 0
    count += 1
    with open(call_counter, "w") as f:
        f.write(str(count))

    log(f"Hook invoked. CWD={os.getcwd()} call={count} booted={os.path.exists(boot_flag)}")

    # Read stdin
    raw = sys.stdin.read()
    log(f"Stdin: {raw[:200]}")

    payload = json.loads(raw)
    log(f"Parsed tool: {payload.get('tool_name', '?')}")

    # Check AGENTS.md
    agents_path = os.path.join(os.getcwd(), "AGENTS.md")
    agents_exists = os.path.exists(agents_path)
    log(f"AGENTS.md exists: {agents_exists} at {agents_path}")

    # Import ystar
    from ystar import Policy
    from ystar.adapters.hook import check_hook
    log("ystar imported OK")

    # Monkey-patch _auto_write_cieu to log errors instead of swallowing
    import ystar.domains.openclaw.adapter as _adapter
    _orig_auto_write = _adapter._auto_write_cieu
    def _patched_auto_write(record):
        log(f"_auto_write_cieu called, store={_adapter._auto_persist_store}")
        try:
            if _adapter._auto_persist_store is not None:
                written = _adapter._auto_persist_store.write(record)
                log(f"_auto_write_cieu written={written}, db={getattr(_adapter._auto_persist_store, 'db_path', '?')}")
            else:
                log(f"_auto_write_cieu SKIPPED: no store")
        except Exception as e:
            log(f"_auto_write_cieu ERROR: {e}")
            log(traceback.format_exc())
    _adapter._auto_write_cieu = _patched_auto_write

    # Build policy
    if agents_exists:
        policy = Policy.from_agents_md_multi(agents_path)
    else:
        policy = Policy({})
    log(f"Policy built: {policy}")

    # Check CIEU count before
    try:
        from ystar.governance.cieu_store import CIEUStore
        cieu_path = os.path.join(os.getcwd(), ".ystar_cieu.db")
        store_before = CIEUStore(cieu_path)
        count_before = store_before.count()
        log(f"CIEU count BEFORE: {count_before}")
    except Exception as e:
        log(f"CIEU count check failed: {e}")
        count_before = -1

    # ── CEO Code-Write Prohibition (Constitutional) ────────────────────
    # CEO must not write to Y*gov source code. This is a governance boundary.
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    if tool in ("Write", "Edit", "NotebookEdit"):
        file_path = tool_input.get("file_path", "")
        ceo_deny = ["Y-star-gov/ystar/", "Y-star-gov\\ystar\\", "/src/ystar/"]
        for deny_pattern in ceo_deny:
            if deny_pattern in file_path:
                result = {
                    "action": "block",
                    "message": f"[Y*gov CONSTITUTIONAL] CEO禁止直接写代码。文件 {file_path} 属于CTO管辖范围。请派工程师执行。"
                }
                log(f"CEO CODE-WRITE BLOCK: {file_path}")
                sys.stdout.write(json.dumps(result))
                sys.exit(0)

    # Run check
    result = check_hook(payload, policy)
    log(f"Result: {result}")

    # Check CIEU count after
    try:
        store_after = CIEUStore(cieu_path)
        count_after = store_after.count()
        log(f"CIEU count AFTER: {count_after} (delta={count_after - count_before})")
    except Exception as e:
        log(f"CIEU count after failed: {e}")

    # ── Session Boot Enforcement (HARD BLOCK) ──────────────────────────────
    # If 5+ tool calls and boot protocol not completed, BLOCK all non-Read operations
    if count >= 5 and not os.path.exists(boot_flag):
        tool = payload.get("tool_name", "")
        # Allow Read/Grep/Glob (needed to execute boot protocol itself)
        if tool not in ("Read", "Grep", "Glob"):
            result = {
                "action": "block",
                "message": "[Y*gov CONSTITUTIONAL] SESSION BOOT NOT COMPLETED. 所有非读取操作被阻断。请立即执行boot协议：读取memory/session_handoff.md → memory/team_dna.md → 验证CIEU → 向老大汇报 → echo BOOTED > scripts/.session_booted"
            }
            log(f"BOOT HARD BLOCK at call {count}, tool={tool}")

    # Output ONLY valid JSON to stdout
    sys.stdout.write(json.dumps(result))

except Exception as e:
    log(f"FATAL ERROR: {e}")
    log(traceback.format_exc())
    # Output empty JSON so Claude Code doesn't crash
    sys.stdout.write("{}")
