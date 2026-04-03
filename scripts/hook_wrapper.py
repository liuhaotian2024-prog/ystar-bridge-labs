"""
Y*gov hook wrapper — thin shell that delegates to check_hook().

Task 3: Simplified architecture (v0.49)
- Policy compilation + session config caching moved to Y*gov kernel (hook.py)
- hook_wrapper.py is now a thin shell: read stdin → call check_hook → output result
- Keeps: CEO code-write block, session boot enforcement, basic logging
"""
import json
import sys
import os
import traceback
import time

LOG = os.path.join(os.path.dirname(__file__), "hook_debug.log")

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

try:
    # ── Session Boot Check ──────────────────────────────────────────────
    boot_flag = os.path.join(os.path.dirname(__file__), ".session_booted")
    call_counter = os.path.join(os.path.dirname(__file__), ".session_call_count")

    # Increment call counter
    try:
        count = int(open(call_counter, "r").read().strip()) if os.path.exists(call_counter) else 0
    except Exception:
        count = 0
    count += 1
    with open(call_counter, "w") as f:
        f.write(str(count))

    # Read stdin
    raw = sys.stdin.buffer.read().decode('utf-8-sig')
    raw = raw.lstrip(chr(0xFEFF))
    payload = json.loads(raw)

    # Import ystar
    from ystar.adapters.hook import check_hook

    # ── CEO Code-Write Prohibition (Constitutional) ────────────────────
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
                sys.stdout.write(json.dumps(result))
                sys.exit(0)

    # ── Run check_hook (Policy compilation happens inside with caching) ──
    result = check_hook(payload)

    # Output ONLY valid JSON to stdout
    sys.stdout.write(json.dumps(result))

except Exception as e:
    log(f"FATAL ERROR: {e}")
    log(traceback.format_exc())
    # Output empty JSON so Claude Code doesn't crash
    sys.stdout.write("{}")

