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

    # ── CORE GOVERNANCE PATH (FAIL-CLOSED) ────────────────────────────
    # If CIEU is unavailable or check_hook fails, DENY the tool call.
    # This is the governance gate — failures here mean the audit chain is broken.
    try:
        # Import ystar
        from ystar.adapters.hook import check_hook

        # ── CEO Code-Write Prohibition (Constitutional) ────────────────────
        tool = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {})
        if tool in ("Write", "Edit", "NotebookEdit"):
            file_path = tool_input.get("file_path", "")
            ceo_deny = ["Y-star-gov/ystar/", "Y-star-gov\\\\ystar\\\\", "/src/ystar/"]
            for deny_pattern in ceo_deny:
                if deny_pattern in file_path:
                    result = {
                        "action": "block",
                        "message": f"[Y*gov CONSTITUTIONAL] CEO禁止直接写代码。文件 {file_path} 属于CTO管辖范围。请派工程师执行。"
                    }
                    # Fail-closed output: if stdout.write fails, force-terminate process
                    try:
                        sys.stdout.write(json.dumps(result))
                        sys.stdout.flush()
                    except Exception as write_exc:
                        log(f"[CRITICAL] stdout.write failed in CEO deny path: {write_exc}")
                        os._exit(1)
                    sys.exit(0)

        # ── Run check_hook (Policy compilation happens inside with caching) ──
        result = check_hook(payload)

    except Exception as core_exc:
        # FAIL-CLOSED: Core governance path is broken.
        # Emit DENY event and block the tool call.
        log(f"[FAIL-CLOSED] Core governance unavailable: {core_exc}")
        log(traceback.format_exc())

        # Try to write CIEU event (best-effort, may also fail)
        try:
            import uuid
            REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
            SESSION_JSON = os.path.join(REPO_ROOT, ".ystar_session.json")
            sys.path.insert(0, REPO_ROOT)
            from ystar.governance.cieu_store import CIEUStore
            from ystar.governance.identity_detector import get_active_agent
            cieu_db = os.path.join(REPO_ROOT, ".ystar_cieu.db")
            try:
                with open(SESSION_JSON, "r") as f:
                    session = json.load(f)
                cieu_db = session.get("cieu_db", cieu_db)
                active_agent = get_active_agent(session)
            except Exception:
                active_agent = "unknown"

            cieu = CIEUStore(db_path=cieu_db)
            now = time.time()
            deny_event = {
                "event_id": str(uuid.uuid4()),
                "session_id": "hook_fail_closed",
                "agent_id": active_agent,
                "event_type": "GOVERNANCE_FAIL_CLOSED",
                "action": "deny",
                "evidence_grade": "system",
                "created_at": now,
                "seq_global": time.time_ns() // 1000,
                "params": {
                    "tool": payload.get("tool_name", "unknown"),
                    "error": str(core_exc),
                    "source": "hook_wrapper.fail_closed",
                },
                "violations": ["core_governance_unavailable"],
                "drift_detected": True,
                "human_initiator": "hook",
            }
            cieu.write_dict(deny_event)
        except Exception as cieu_exc:
            log(f"[FAIL-CLOSED] Could not write CIEU deny event: {cieu_exc}")

        # DENY the tool call
        result = {
            "action": "block",
            "message": (
                f"[Y*gov FAIL-CLOSED] Core governance unavailable. "
                f"CIEU audit chain is broken — blocking tool call for safety.\\n\\n"
                f"Error: {core_exc}\\n\\n"
                f"Fix: Run \`ystar doctor\` to diagnose governance health."
            )
        }
        # Fail-closed output: if stdout.write fails, force-terminate process
        # to prevent outer catch-all from converting DENY to allow
        try:
            sys.stdout.write(json.dumps(result))
            sys.stdout.flush()
        except Exception as write_exc:
            log(f"[CRITICAL] stdout.write failed in fail-closed path: {write_exc}")
            os._exit(1)  # Hard kill — do NOT let outer catch-all convert to allow
        sys.exit(0)

    # ── Telegram event trigger (Board 2026-04-15, Secretary-owned) ───────
    # Best-effort: never block on failure. Scans Bash git commits for
    # MILESTONE_SHIPPED markers → push to @YstarBridgeLabs.
    try:
        if payload.get("tool_name") == "Bash":
            cmd = (payload.get("tool_input") or {}).get("command", "") or ""
            if "git commit" in cmd and "[L4 SHIPPED]" in cmd:
                # fire-and-forget, do not await; do not block tool call
                import subprocess
                title = cmd.split("[L4 SHIPPED]", 1)[1][:120].strip().strip('"').strip("'")
                subprocess.Popen(
                    [
                        "/usr/bin/python3",
                        os.path.join(os.path.dirname(__file__), "telegram_notify.py"),
                        "event",
                        "MILESTONE_SHIPPED",
                        title or "(no title)",
                        "L4 ship detected via hook_wrapper",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
    except Exception as _tg_exc:
        log(f"[TG-EVENT] skipped: {_tg_exc}")

    # Output ONLY valid JSON to stdout
    sys.stdout.write(json.dumps(result))

except Exception as e:
    # This catch-all handles non-core failures (payload parsing, watcher startup, etc.)
    # Core governance failures are handled by the fail-closed block above.
    log(f"[FAIL-OPEN] Non-core hook error: {e}")
    log(traceback.format_exc())
    # Output empty JSON (allow) for edge failures so Claude Code doesn't crash
    sys.stdout.write("{}")

