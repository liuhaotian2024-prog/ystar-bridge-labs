"""
Y*gov hook wrapper — thin shell that delegates to check_hook().

Task 3: Simplified architecture (v0.49)
- Policy compilation + session config caching moved to Y*gov kernel (hook.py)
- hook_wrapper.py is now a thin shell: read stdin → call check_hook → output result
- Keeps: CEO code-write block, session boot enforcement, basic logging

GOV-008 Gap 2: Intent guard
- On Write/Edit/NotebookEdit against a protected path (governance/, agents/,
  README.md, the intent scripts themselves), query CIEU for any INTENT_RECORDED
  row within the last intent_guard_window_hours. If none, write a single
  GOV006_VIOLATION_WARNING row to CIEU and log. WARN-ONLY. FAIL-OPEN.
- Window + protected path list are loaded from .ystar_session.json. Defaults
  are 4 hours and the five paths above.
"""
import json
import sys
import os
import traceback
import time
import uuid

LOG = os.path.join(os.path.dirname(__file__), "hook_debug.log")
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SESSION_JSON = os.path.join(REPO_ROOT, ".ystar_session.json")
DEFAULT_GUARD_WINDOW_HOURS = 4
DEFAULT_GUARD_PROTECTED = [
    "governance/",
    "agents/",
    "README.md",
    "scripts/record_intent.py",
    "scripts/check_intents.py",
]

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def _intent_guard_check(tool_name, file_path):
    """GOV-008 Gap 2 — warn-only intent guard. Returns None.

    On any Write/Edit/NotebookEdit against a protected path, check CIEU for
    a recent INTENT_RECORDED row. On miss, write one GOV006_VIOLATION_WARNING
    row and log. Never blocks. Fail-open on any error so hook failures can
    never become production incidents.
    """
    try:
        if tool_name not in ("Write", "Edit", "NotebookEdit"):
            return
        if not file_path:
            return

        # Load config (window + protected paths) from .ystar_session.json.
        window_hours = DEFAULT_GUARD_WINDOW_HOURS
        protected = list(DEFAULT_GUARD_PROTECTED)
        cieu_db = os.path.join(REPO_ROOT, ".ystar_cieu.db")
        try:
            with open(SESSION_JSON, "r") as f:
                session = json.load(f)
            window_hours = float(session.get("intent_guard_window_hours",
                                             DEFAULT_GUARD_WINDOW_HOURS))
            protected = session.get("intent_guard_protected_paths", protected)
            cieu_db = session.get("cieu_db", cieu_db)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            log(f"[intent-guard] session config unreadable ({exc}); using defaults")

        # Normalize file_path to repo-relative for matching.
        fp_abs = os.path.abspath(file_path)
        try:
            fp_rel = os.path.relpath(fp_abs, REPO_ROOT)
        except ValueError:
            fp_rel = file_path
        fp_rel = fp_rel.replace(os.sep, "/")

        # Protected match: prefix (directory) OR exact file.
        def _matches(p, path):
            if p.endswith("/"):
                return path.startswith(p)
            return path == p
        if not any(_matches(p, fp_rel) for p in protected):
            return

        # Query CIEU for a recent INTENT_RECORDED row.
        sys.path.insert(0, REPO_ROOT)
        try:
            from ystar.governance.cieu_store import CIEUStore
        except Exception as exc:
            log(f"[intent-guard] CIEUStore import failed ({exc}); fail-open")
            return
        cieu = CIEUStore(db_path=cieu_db)
        now = time.time()
        window_secs = window_hours * 3600.0
        rows = cieu.query(event_type="INTENT_RECORDED", limit=200)
        has_recent = any((now - (r.created_at or 0)) <= window_secs for r in rows)
        if has_recent:
            return  # silent pass

        # No recent intent → warn-only violation row.
        warn = {
            "event_id": str(uuid.uuid4()),
            "session_id": "hook_intent_guard",
            "agent_id": "hook",
            "event_type": "GOV006_VIOLATION_WARNING",
            "decision": "info",
            "evidence_grade": "intent",
            "created_at": now,
            "seq_global": time.time_ns() // 1000,
            "params": {
                "tool": tool_name,
                "file_path": fp_rel,
                "window_hours": window_hours,
                "protected_path_match": next(
                    (p for p in protected if _matches(p, fp_rel)), None),
                "warned_at": now,
                "source": "hook_wrapper.intent_guard",
            },
            "violations": ["missing_recent_intent"],
            "drift_detected": True,
            "human_initiator": "hook",
        }
        try:
            cieu.write_dict(warn)
            log(f"[intent-guard] WARN: {tool_name} {fp_rel} — no INTENT_RECORDED "
                f"in {window_hours}h window")
        except Exception as exc:
            log(f"[intent-guard] warn write failed ({exc}); fail-open")
    except Exception as exc:
        # Catch-all fail-open. Hook failures must never become tool failures.
        log(f"[intent-guard] unexpected error ({exc}); fail-open")

def _main():
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

        # ── GOV-006 Intent Guard (GOV-008 Gap 2) ───────────────────────────
        # Warn-only. Writes GOV006_VIOLATION_WARNING to CIEU on miss. Never blocks.
        _intent_guard_check(tool, tool_input.get("file_path", ""))

        # ── Run check_hook (Policy compilation happens inside with caching) ──
        result = check_hook(payload)

        # Output ONLY valid JSON to stdout
        sys.stdout.write(json.dumps(result))

    except Exception as e:
        log(f"FATAL ERROR: {e}")
        log(traceback.format_exc())
        # Output empty JSON so Claude Code doesn't crash
        sys.stdout.write("{}")


if __name__ == "__main__":
    _main()

