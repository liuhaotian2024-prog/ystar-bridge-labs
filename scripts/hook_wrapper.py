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

GOV-009 upgrade (2026-04-10): "qualified" is now stricter.
- A recent INTENT_RECORDED row counts as qualified ONLY if its params dict
  contains non-empty values for meaning, success_bar, assumptions, theory.
- Unqualified rows are treated identically to missing rows: the guard
  writes one GOV006_VIOLATION_WARNING and logs. Warn-only, fail-open.
- _intent_is_qualified() encapsulates the check so hook_debug.log can
  distinguish "no recent intent" from "recent intent lacks GOV-009 fields".

DAEMON CACHE LOCK FIX (2026-04-13):
- Backported exp7 watcher (71fd6db from ystar-company-test)
- GovernanceWatcher polls .ystar_active_agent, AGENTS.md, .ystar_session.json (2s)
- On change → invalidates daemon identity + rule cache → next hook call reloads
- Fail-open: watcher crash never blocks main flow, hook runs with last cached state
- E2E target: <5s from file write → daemon behavior change
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


# ── Daemon Cache Invalidation (exp7 backport) ─────────────────────────────
_daemon_cache_valid = True
_governance_watcher = None


def invalidate_daemon_cache(changed_files):
    """Invalidation callback for GovernanceWatcher.

    Clears ystar.adapters.identity_detector._SESSION_CONFIG_CACHE.
    Next hook call will reload identity + session config + rules from disk.
    """
    global _daemon_cache_valid
    _daemon_cache_valid = False

    # Clear Y*gov's session config cache
    try:
        sys.path.insert(0, REPO_ROOT)
        from ystar.adapters import identity_detector
        identity_detector._SESSION_CONFIG_CACHE = None
        log(f"[cache] cleared Y*gov session config cache")
    except Exception as e:
        log(f"[cache] failed to clear Y*gov cache (fail-open): {e}")

    # Clear boundary_enforcer's write_paths cache
    try:
        from ystar.adapters import boundary_enforcer
        boundary_enforcer._AGENT_WRITE_PATHS.clear()
        log(f"[cache] cleared write_paths cache")
    except Exception as e:
        log(f"[cache] failed to clear write_paths cache (fail-open): {e}")

    log(f"[cache] invalidated due to: {', '.join(changed_files)}")


def ensure_watcher_started():
    """Start GovernanceWatcher on first hook call (lazy init)."""
    global _governance_watcher
    if _governance_watcher is not None:
        return  # Already started

    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from governance_watcher import create_watcher

        _governance_watcher = create_watcher(REPO_ROOT, log_fn=log)
        _governance_watcher.set_invalidation_callback(invalidate_daemon_cache)
        _governance_watcher.start()
        log("[watcher] GovernanceWatcher started")
    except Exception as e:
        log(f"[watcher] FAIL-OPEN: startup error {e}")
        # Fail-open: watcher failure never blocks main flow


# GOV-009 quality-bar fields required on every INTENT_RECORDED row.
GOV009_REQUIRED_FIELDS = ("meaning", "success_bar", "assumptions", "theory")


def _intent_is_qualified(params) -> bool:
    """GOV-009 — return True iff all four quality-bar fields are present
    and non-empty in the row's params dict.

    The CIEUStore returns params as a JSON string on read
    (``record.params_json``) — this helper expects the already-parsed dict.
    """
    if not isinstance(params, dict):
        return False
    for field in GOV009_REQUIRED_FIELDS:
        val = params.get(field)
        if val is None:
            return False
        if isinstance(val, str):
            if not val.strip():
                return False
        elif isinstance(val, (list, tuple)):
            if not val:
                return False
            # Require at least one non-empty string entry for list fields.
            if not any(isinstance(x, str) and x.strip() for x in val):
                return False
        else:
            # Any other type is treated as unqualified — the schema is
            # str for meaning/success_bar and list[str] for assumptions/theory.
            return False
    return True


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

        # GOV-009: a row counts only if recent AND has all four
        # quality-bar fields non-empty. Track which reason applies so
        # hook_debug.log can distinguish "no recent intent" from
        # "recent intent lacks GOV-009 fields".
        recent_rows = [r for r in rows if (now - (r.created_at or 0)) <= window_secs]
        if not recent_rows:
            violation_reason = "no_recent_intent"
        else:
            qualified = False
            for r in recent_rows:
                try:
                    params = json.loads(r.params_json or "{}")
                except (json.JSONDecodeError, TypeError):
                    params = {}
                if _intent_is_qualified(params):
                    qualified = True
                    break
            if qualified:
                return  # silent pass
            violation_reason = "unqualified_intent_gov009"

        # No qualified recent intent → warn-only violation row.
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
                "violation_reason": violation_reason,  # GOV-009
                "warned_at": now,
                "source": "hook_wrapper.intent_guard",
            },
            "violations": [violation_reason],
            "drift_detected": True,
            "human_initiator": "hook",
        }
        try:
            cieu.write_dict(warn)
            log(f"[intent-guard] WARN: {tool_name} {fp_rel} — {violation_reason} "
                f"(window={window_hours}h)")
        except Exception as exc:
            log(f"[intent-guard] warn write failed ({exc}); fail-open")
    except Exception as exc:
        # Catch-all fail-open. Hook failures must never become tool failures.
        log(f"[intent-guard] unexpected error ({exc}); fail-open")

def check_continuation_compliance(tool_name, tool_input, call_count):
    """Session前5个tool call必须和action_queue相关。

    v2 continuation protocol: if agent is querying CIEU/session.json
    plumbing instead of executing action_queue items, emit a warning.
    Warn-only, never blocks.
    """
    if call_count > 5:
        return None  # Only enforce first 5 calls

    cont_path = os.path.join(REPO_ROOT, "memory", "continuation.json")
    if not os.path.exists(cont_path):
        return None

    try:
        with open(cont_path, "r") as f:
            cont = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    anti = cont.get("anti_patterns", [])

    # Detect plumbing queries in early calls
    if tool_name == "Bash":
        cmd = tool_input.get("command", "").lower()
        plumbing_indicators = ["cieu", "session.json", "omission", ".ystar_session"]
        if any(x in cmd for x in plumbing_indicators):
            if "report_plumbing_to_board" in anti:
                log(f"[continuation] WARN: call #{call_count} is plumbing query, "
                    f"should be executing action_queue. cmd={cmd[:80]}")
                return {
                    "action": "warn",
                    "message": "[CONTINUATION] \u524d5\u4e2a\u52a8\u4f5c\u5e94\u6267\u884caction_queue\uff0c\u4e0d\u662f\u67e5\u6c34\u7ba1\u3002"
                }

    return None


def _main():
    global _daemon_cache_valid

    try:
        # ── Governance Watcher (lazy start on first call) ──────────────────
        ensure_watcher_started()

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

        # ── Continuation Compliance Check (v2 protocol) ───────────────────
        tool = payload.get("tool_name", "")
        tool_input_raw = payload.get("tool_input", {})
        cont_warn = check_continuation_compliance(tool, tool_input_raw, count)
        if cont_warn is not None:
            log(f"[continuation] warn emitted for call #{count}: {tool}")
            # Warn-only: log but don't block

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

        # ── AMENDMENT-013: Proactive Skill Activation ──────────────────────
        # Check if activation triggers, inject skill content if matched
        # Fail-open: activation errors logged but never block
        try:
            from ystar.adapters.activation_triggers import should_activate_skill
            # Get active agent from session
            agent_name = os.environ.get("YSTAR_ACTIVE_AGENT", "ceo")

            activation = should_activate_skill(
                agent_name=agent_name,
                action_type=tool,
                action_params=tool_input,
                context={}
            )

            if activation:
                # Emit CIEU SKILL_ACTIVATION event
                try:
                    from ystar.kernel.cieu import emit
                    emit(
                        "SKILL_ACTIVATION",
                        agent=agent_name,
                        skill_id=activation.skill_id,
                        trigger_rule=activation.trigger_rule,
                        action_type=tool,
                        priority=activation.priority
                    )
                except Exception as emit_exc:
                    log(f"[activation] CIEU emit failed: {emit_exc}")

                # Prepend skill to result message (if ALLOW)
                if result.get("action") in ("continue", "allow", None):
                    skill_header = (
                        f"[Y*] 📖 SKILL ACTIVATED: {os.path.basename(activation.skill_id)}\n\n"
                        f"{activation.skill_content}\n\n"
                        f"---\n\n"
                    )
                    # Prepend to message if exists, else create message
                    if "message" in result:
                        result["message"] = skill_header + result["message"]
                    else:
                        result["message"] = skill_header

                    log(f"[activation] Skill injected: {activation.skill_id} (rule: {activation.trigger_rule})")
        except Exception as activation_exc:
            # Fail-open: activation failures should never block
            log(f"[activation] fail-open: {activation_exc}")

        # ── GOV-010: OmissionScheduler tick (at most once per 5 min) ──────
        # Piggybacks on every PreToolUse call. The scheduler's should_scan()
        # rate-limits so actual scans happen at most once per interval.
        # Fail-open: scan errors are logged but never block the tool call.
        try:
            from ystar.governance.omission_engine import OmissionEngine
            from ystar.governance.omission_scheduler import OmissionScheduler
            if not hasattr(_main, '_omission_scheduler'):
                _engine = OmissionEngine()  # defaults to SQLite store (GOV-010)
                _main._omission_scheduler = OmissionScheduler(
                    _engine, interval_seconds=300, log_fn=log
                )
            scan_result = _main._omission_scheduler.tick()
            if scan_result.get("scanned") and scan_result.get("violations"):
                log(f"[omission-scan] {len(scan_result['violations'])} violation(s) found")
        except Exception as scan_exc:
            log(f"[omission-scan] fail-open: {scan_exc}")

        # Output ONLY valid JSON to stdout
        sys.stdout.write(json.dumps(result))

    except Exception as e:
        log(f"FATAL ERROR: {e}")
        log(traceback.format_exc())
        # Output empty JSON so Claude Code doesn't crash
        sys.stdout.write("{}")


if __name__ == "__main__":
    _main()

