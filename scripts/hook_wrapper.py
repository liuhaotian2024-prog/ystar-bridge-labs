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
import re

# Y*gov module path fix (Board 2026-04-16 P0: ModuleNotFoundError emergency)
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")

LOG = os.path.join(os.path.dirname(__file__), "hook_debug.log")

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")

FAIL_CLOSED_LOG = os.path.join(os.path.dirname(__file__), "hook_fail_closed.jsonl")

def emit_cieu_or_fallback(event_dict, reason_tag):
    """
    Three-tier degradation for fail-closed audit events.
    Layer 1: CIEU chain (preferred, cryptographic audit)
    Layer 2: Structured JSONL log (survives governance-layer crash)
    Layer 3: stderr (survives everything short of OS failure)
    """
    # Layer 1: CIEU
    try:
        REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, REPO_ROOT)
        from ystar.governance.cieu_store import CIEUStore
        SESSION_JSON = os.path.join(REPO_ROOT, ".ystar_session.json")
        cieu_db = os.path.join(REPO_ROOT, ".ystar_cieu.db")
        try:
            with open(SESSION_JSON, "r") as f:
                session = json.load(f)
            cieu_db = session.get("cieu_db", cieu_db)
        except Exception:
            pass
        CIEUStore(db_path=cieu_db).write_dict(event_dict)
        return "cieu"
    except Exception as cieu_exc:
        # Layer 2: structured JSONL
        try:
            fallback_record = {
                "ts": time.time(),
                "tag": reason_tag,
                "cieu_error": str(cieu_exc),
                "event": event_dict,
            }
            with open(FAIL_CLOSED_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(fallback_record) + "\n")
            log(f"[FAIL-CLOSED-L2] {reason_tag}: CIEU down, wrote to {FAIL_CLOSED_LOG}")
            return "jsonl"
        except Exception as file_exc:
            # Layer 3: stderr
            try:
                sys.stderr.write(
                    f"[FAIL-CLOSED-L3] {reason_tag}: CIEU+file both failed. "
                    f"cieu_err={cieu_exc} file_err={file_exc}\n"
                )
            except Exception:
                pass  # If even stderr fails, nothing we can do
            return "stderr"

try:
    # ── ARCH-6: Feature-flagged v2 thin adapter ──────────────────────────
    # When YSTAR_HOOK_V2=1, delegate entirely to the thin adapter path.
    # The thin adapter uses handle_hook_event() which runs router rules
    # (Layer 3) before check_hook (Layer 2+1).  All hook_wrapper logic
    # (CEO guard, CZL-159, agent stack, dispatch gate) is bypassed — those
    # must be registered as router rules for v2 to be fully equivalent.
    # CZL-HOOK-V2-BYPASS 2026-04-23 — Board shell sed disabled v2 path after
    # 3h fail-closed deadlock (see reports/incidents/2026-04-23-hook-fail-closed-deadlock.md
    # and reports/ceo/iron_rule_incident_response_3channel_20260423.md).
    # Pairs with Y-star-gov commit f6374ef (v2 adapter marker fallback symmetric fix).
    # Re-enable ONLY after: (1) v2 adapter marker override symmetric with v1 verified;
    # (2) YSTAR_HOOK_V2=1 removed from shell profile/launchd; (3) 10+ regression pass
    # on concurrent subagent marker resolution.
    if False and os.environ.get("YSTAR_HOOK_V2") == "1":
        raw = sys.stdin.buffer.read().decode('utf-8-sig').lstrip(chr(0xFEFF))
        payload = json.loads(raw)
        from ystar.adapters.hook import handle_hook_event
        rules_dir = os.environ.get("YSTAR_RULES_DIR", "")
        result = handle_hook_event(payload, rules_dir=rules_dir or None)
        sys.stdout.write(json.dumps(result))
        sys.exit(0)

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

    # ── CZL-WHO-I-AM-SYSTEM-BINDING: UserPromptSubmit WHO_I_AM injection ──
    # Board directive: inject WHO_I_AM v0.4 key section into every user prompt
    # context so CEO identity framing is structurally present, not memory-dependent.
    _hook_event = payload.get("hook_event_name", "") or payload.get("hookEventName", "")
    if _hook_event == "UserPromptSubmit":
        _whoiam_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "knowledge", "ceo", "wisdom", "WHO_I_AM.md"
        )
        _whoiam_inject = ""
        try:
            if os.path.isfile(_whoiam_path):
                with open(_whoiam_path, "r", encoding="utf-8") as _wf:
                    _whoiam_full = _wf.read()
                # Extract L3 framing section (resilient: try multiple markers)
                _section_starts = [
                    "## 2026-04-20 L3 Framing",  # v0.5+
                    "## v0.4",                     # v0.4
                ]
                _section_ends = [
                    "## WHO_I_AM",                 # v0.5+ next section
                    "## \u6700\u6df1\u5c42",       # "## 最深层" v0.4 next section
                ]
                _v04_start = -1
                for _marker in _section_starts:
                    _v04_start = _whoiam_full.find(_marker)
                    if _v04_start >= 0:
                        break
                _v04_end = -1
                if _v04_start >= 0:
                    for _end_marker in _section_ends:
                        _v04_end = _whoiam_full.find(_end_marker, _v04_start + 1)
                        if _v04_end > _v04_start:
                            break
                    if _v04_end <= _v04_start:
                        # Fallback: take 2000 chars from start marker
                        _v04_end = min(_v04_start + 2000, len(_whoiam_full))
                if _v04_start >= 0 and _v04_end > _v04_start:
                    _whoiam_inject = _whoiam_full[_v04_start:_v04_end].strip()
        except Exception as _whoiam_exc:
            log(f"[WHO_I_AM] Read failed (graceful degradation): {_whoiam_exc}")

        if _whoiam_inject:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalSystemPrompt": (
                        "<system-reminder>WHO_I_AM active framing:\n"
                        + _whoiam_inject
                        + "\n</system-reminder>"
                    )
                }
            }
            log("[WHO_I_AM] Injected v0.4 framing into UserPromptSubmit")
        else:
            result = {}
            log("[WHO_I_AM] No v0.4 content found or file missing — pass-through")
        sys.stdout.write(json.dumps(result))
        sys.exit(0)

    # ── CZL-P1-a: Payload agent_id override from .ystar_active_agent ──
    # The identity_detector has multiple fallback priorities. When Claude Code
    # sends payload with agent_id="" and agent_type="agent" (the default for
    # the root process), identity_detector's priority 2 returns "agent" and
    # short-circuits before reaching the .ystar_active_agent file marker.
    # Fix: read the marker file here and inject into payload so priority 1
    # (payload.agent_id) resolves correctly. Also clear agent_type to prevent
    # the priority 1.5 short-circuit returning "agent".
    #
    # Sibling Bug #4 fix (2026-04-18): Save original payload values BEFORE
    # marker override so CEO guard can detect subagent context even when
    # the marker is stale "ceo" (e.g. push_agent failed or wasn't called).
    #
    # CZL-MARKER-PER-SESSION-ISOLATION (2026-04-19): Fallback chain reads
    # per-session marker first, then global marker. This prevents N concurrent
    # sub-agents from clobbering each other's identity via the shared global
    # marker file. Per-session marker uses CLAUDE_SESSION_ID or PPID suffix.
    _original_agent_id = payload.get("agent_id", "")
    _original_agent_type = payload.get("agent_type", "")

    _MARKER_DIR = "/Users/haotianliu/.openclaw/workspace/ystar-company/scripts"
    _MARKER_GLOBAL = os.path.join(_MARKER_DIR, ".ystar_active_agent")
    _marker_content = None

    # Per-session marker fallback chain
    def _read_session_marker():
        """Read per-session marker first, then global marker."""
        # 1. Per-session marker via CLAUDE_SESSION_ID
        _sid = os.environ.get("CLAUDE_SESSION_ID", "").strip()
        if _sid:
            _sanitized = "".join(c for c in _sid if c.isalnum() or c in "-_")
            if _sanitized:
                _session_path = os.path.join(_MARKER_DIR, f".ystar_active_agent.{_sanitized}")
                try:
                    _content = open(_session_path, "r", encoding="utf-8").read().strip()
                    if _content:
                        log(f"[P1-a] Read per-session marker ({_sanitized}): '{_content}'")
                        return _content
                except FileNotFoundError:
                    pass
        # 2. Per-session marker via PPID
        _ppid = os.environ.get("PPID", "")
        if not _ppid:
            try:
                _ppid = str(os.getppid())
            except Exception:
                _ppid = ""
        if _ppid and _ppid != "1":
            _ppid_path = os.path.join(_MARKER_DIR, f".ystar_active_agent.ppid_{_ppid}")
            try:
                _content = open(_ppid_path, "r", encoding="utf-8").read().strip()
                if _content:
                    log(f"[P1-a] Read per-session marker (ppid_{_ppid}): '{_content}'")
                    return _content
            except FileNotFoundError:
                pass
        # 3. Global marker — pick newest of (scripts/.ystar_active_agent, workspace-root/.ystar_active_agent)
        #    governance_boot.sh writes to workspace-root; older code writes scripts/. Mismatch caused
        #    lock-death #10 (boot reset root to 'ceo' but scripts/ stale 'ystar-cto' held hook lock).
        _root_path = "/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_active_agent"
        _candidates = []
        for _path in (_MARKER_GLOBAL, _root_path):
            try:
                _st = os.stat(_path)
                _c = open(_path, "r", encoding="utf-8").read().strip()
                if _c:
                    _candidates.append((_st.st_mtime, _c))
            except FileNotFoundError:
                pass
        if _candidates:
            _candidates.sort(reverse=True)
            return _candidates[0][1]
        return None

    try:
        _marker_content = _read_session_marker()
        if _marker_content and _marker_content != "agent":
            payload["agent_id"] = _marker_content
            # Clear agent_type to prevent priority 1.5 from returning "agent"
            if payload.get("agent_type") in ("", "agent", None):
                payload.pop("agent_type", None)
            log(f"[P1-a] Payload agent_id overridden to '{_marker_content}' from marker fallback chain")
    except FileNotFoundError:
        pass  # No marker file — identity_detector will use its own fallbacks
    except Exception as _marker_exc:
        log(f"[P1-a] Failed to read marker file: {_marker_exc}")

    # ── CORE GOVERNANCE PATH (FAIL-CLOSED) ────────────────────────────
    # If CIEU is unavailable or check_hook fails, DENY the tool call.
    # This is the governance gate — failures here mean the audit chain is broken.
    try:
        # Import ystar
        from ystar.adapters.hook import check_hook

        # ── CEO Code-Write Prohibition (Constitutional) ────────────────────
        # CZL-ARCH-1-followup (2026-04-18, Maya diagnosis): Added agent_id
        # guard so this rule only denies CEO, not all agents. Previously it
        # blocked every subagent (eng-kernel, eng-governance, eng-platform)
        # from writing Y-star-gov/ystar/ which is their actual scope — the
        # source of today's repeated Leo/Maya/Ryan lock-deaths.
        #
        # Sibling Bug #4 fix (2026-04-18, Ryan diagnosis): When CEO spawns
        # a subagent, the marker may still be "ceo" if push_agent hasn't
        # fired yet or failed. We detect subagent context via:
        #   1. agent_stack depth > 0 (subagent was properly pushed)
        #   2. Original payload agent_type is non-empty AND non-"agent"
        #      (Claude Code sets specific agent_type for subagent contexts)
        # If subagent context is detected, skip CEO guard entirely.
        tool = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {})
        _caller_id = payload.get("agent_id", "")
        # Removed "" from _ceo_identities — empty string is ambiguous and
        # should not be treated as CEO (it means "unknown", not "CEO").
        _ceo_identities = ("ceo", "Aiden-CEO", "Aiden")

        # Subagent context detection (Sibling Bug #4)
        _is_subagent_context = False
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from agent_stack import stack_depth as _stack_depth
            if _stack_depth() > 0:
                _is_subagent_context = True
                log(f"[BUG4-FIX] Subagent detected via stack depth > 0, skipping CEO guard")
        except Exception as _stack_exc:
            log(f"[BUG4-FIX] stack_depth check failed: {_stack_exc}")
        # Fallback: check if original payload indicates subagent context
        # (agent_type set to something specific by Claude Code for subagents)
        if not _is_subagent_context and _original_agent_type not in ("", "agent", None):
            _is_subagent_context = True
            log(f"[BUG4-FIX] Subagent detected via original agent_type='{_original_agent_type}'")
        # Fallback 2: marker itself is an engineer identity (not CEO) — trust it
        if not _is_subagent_context and _caller_id not in _ceo_identities and _caller_id != "":
            _is_subagent_context = True
            log(f"[BUG4-FIX] Subagent detected via marker identity='{_caller_id}' (not CEO)")

        if tool in ("Write", "Edit", "NotebookEdit") and _caller_id in _ceo_identities and not _is_subagent_context:
            file_path = tool_input.get("file_path", "")
            ceo_deny = ["Y-star-gov/ystar/", "Y-star-gov\\\\ystar\\\\", "/src/ystar/"]
            for deny_pattern in ceo_deny:
                if deny_pattern in file_path:
                    result = {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": f"[Y*gov CONSTITUTIONAL] CEO禁止直接写代码。文件 {file_path} 属于CTO管辖范围。请派工程师执行。"
                        }
                    }
                    # Fail-closed output: if stdout.write fails, force-terminate process
                    try:
                        sys.stdout.write(json.dumps(result))
                        sys.stdout.flush()
                    except Exception as write_exc:
                        log(f"[CRITICAL] stdout.write failed in CEO deny path: {write_exc}")
                        os._exit(1)
                    sys.exit(0)

        # ── CZL-159: CEO Pre-Output U-Workflow Enforcement ────────────────
        # Block CEO Write to external-facing paths without research/synthesis/audience evidence.
        # Integrated here (not separate hook) because matcher-per-tool is unreliable (CZL-160).
        if tool == "Write":
            _enforced_prefixes = ("reports/", "content/", "knowledge/ceo/strategy/")
            _fp = tool_input.get("file_path", "")
            _is_enforced = any(pfx in _fp for pfx in _enforced_prefixes)
            if _is_enforced:
                _content = tool_input.get("content", "")
                _research = bool(re.search(
                    r"(source[s]?[:\s]|cite[ds]?[\s:]|per\s+\w|according\s+to|"
                    r"search|found\s+that|reference[ds]?|evidence|data\s+show|"
                    r"based\s+on|research|study|paper|article|empirical)",
                    _content, re.IGNORECASE))
                _synthesis = bool(re.search(
                    r"(therefore|because|analysis|conclude[ds]?|lesson[s]?|"
                    r"insight[s]?|implication|root\s+cause|pattern|takeaway|"
                    r"diagnosis|framework|principle|synthesis|assessment)",
                    _content, re.IGNORECASE))
                _audience = bool(re.search(
                    r"(audience|purpose|for\s+board|stakeholder|reader[s]?|"
                    r"目标受众|目的|面向|intended\s+for|context\s+for|"
                    r"decision\s+maker|consumer|recipient)",
                    _content, re.IGNORECASE))
                _missing = []
                if not _research: _missing.append("research")
                if not _synthesis: _missing.append("synthesis")
                if not _audience: _missing.append("audience")
                if _missing:
                    # -- CZL-166: Append actionable header template to deny --
                    try:
                        from ystar.rules.auto_rewrite import czl159_header_autoinject_template
                        _header_template = czl159_header_autoinject_template()
                    except Exception:
                        # Fallback: inline template (Leo Y-star-gov side not yet merged)
                        _header_template = (
                            "\n\n--- Copy this template into your document header before writing ---\n"
                            "Audience: [who is the intended reader?]\n"
                            "Research basis: [cite sources, data, or evidence]\n"
                            "Synthesis: [what is the core insight / conclusion?]\n"
                            "Purpose: [what decision or action should this enable?]\n"
                            "---\n"
                            "Fill in each bracket, then re-attempt the Write."
                        )
                    _block_msg = (
                        f"[CZL-159 CEO PRE-OUTPUT BLOCK] Write to {_fp} missing "
                        f"U-workflow signals: {', '.join(_missing)}. "
                        f"Do research/synthesis/audience framing before writing."
                        f"{_header_template}"
                    )
                    log(f"[CZL-159] BLOCKED: {_fp} missing {_missing}")
                    result = {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": _block_msg
                        }
                    }
                    try:
                        sys.stdout.write(json.dumps(result))
                        sys.stdout.flush()
                    except Exception as write_exc:
                        log(f"[CRITICAL] stdout.write failed in CZL-159 path: {write_exc}")
                        os._exit(1)
                    sys.exit(0)

        # ── CZL-P1-e: Push current agent onto stack before subagent spawn ──
        if tool == "Agent":
            try:
                sys.path.insert(0, os.path.dirname(__file__))
                from agent_stack import push_agent as _push_agent
                _subagent_name = tool_input.get("agent", "")
                if _subagent_name:
                    _prev = _push_agent(_subagent_name)
                    log(f"[P1-e] Agent stack PUSH: {_prev} -> {_subagent_name}")
            except Exception as _push_exc:
                log(f"[P1-e] Agent stack push failed (non-fatal): {_push_exc}")

        # ── CZL Gate 1: Dispatch 5-tuple validator (Board 2026-04-16) ──────
        if tool == "Agent":
            try:
                from ystar.kernel.czl_protocol import validate_dispatch
                prompt = tool_input.get("prompt", "")
                missing_sections = validate_dispatch(prompt)
                if missing_sections:
                    # Inject warning into stdout (non-blocking, warn-only until 1776499200)
                    warning_msg = f"⚠️ CZL Gate 1: dispatch missing sections {missing_sections}"
                    # Do NOT block the tool call yet (dry_run mode), just log + emit CIEU
                    log(f"[CZL-GATE1] {warning_msg}")

                    # Emit CIEU event (via 3-tier fallback: CIEU → JSONL → stderr)
                    import uuid
                    try:
                        REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
                        SESSION_JSON = os.path.join(REPO_ROOT, ".ystar_session.json")
                        sys.path.insert(0, REPO_ROOT)
                        from ystar.adapters.identity_detector import get_active_agent
                        with open(SESSION_JSON, "r") as f:
                            session = json.load(f)
                        active_agent = get_active_agent(session)
                    except Exception:
                        active_agent = "unknown"

                    gate1_event = {
                        "event_id": str(uuid.uuid4()),
                        "session_id": "hook_gate1",
                        "agent_id": active_agent,
                        "event_type": "CZL_DISPATCH_GATE1_VIOLATION",
                        "action": "warn",
                        "evidence_grade": "system",
                        "created_at": time.time(),
                        "seq_global": time.time_ns() // 1000,
                        "params": {
                            "missing_sections": missing_sections,
                            "recipient": tool_input.get("agent", "unknown"),
                            "dry_run_until": 1776499200,
                            "source": "hook_wrapper.gate1",
                        },
                        "violations": ["czl_dispatch_incomplete"],
                        "drift_detected": True,
                        "human_initiator": "hook",
                    }
                    emit_cieu_or_fallback(gate1_event, "GATE1_VIOLATION")

                    # Inject warning to stdout via system-reminder (best-effort)
                    # Note: OpenClaw hook output goes to logs, not directly to model
                    # This is logged for transparency; actual enforcement via ForgetGuard
                    sys.stderr.write(f"{warning_msg}\n")

            except Exception as gate1_exc:
                log(f"[CZL-GATE1] Failed to validate dispatch: {gate1_exc}")
                # Do not block tool call on validator failure (fail-open for Gate 1)

        # ── Run check_hook (Policy compilation happens inside with caching) ──
        result = check_hook(payload)

        # ── ForgetGuard wire (Board 2026-04-22 catch: commission infra was装不接线) ──
        # governance/forget_guard_rules.yaml has 32 YAML commission rules; prior to
        # this wire they were dead (hook_wrapper had 0 references). Now invoked on
        # every PreToolUse after boundary_enforcer via check_hook. If forget_guard
        # returns a violation, override result to deny/warn.
        if payload.get("hook_event_name") == "PreToolUse":
            try:
                REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
                sys.path.insert(0, REPO_ROOT)
                from ystar.governance.forget_guard import check_forget_violation
                _fg_context = {
                    "tool": payload.get("tool_name", ""),
                    "tool_input": payload.get("tool_input", {}),
                    "agent_id": payload.get("agent_id", ""),
                    "active_agent": payload.get("agent_id", ""),
                    "file_path": payload.get("tool_input", {}).get("file_path", ""),
                    "command": payload.get("tool_input", {}).get("command", ""),
                    "content": payload.get("tool_input", {}).get("content", ""),
                }
                _fg_violation = check_forget_violation(_fg_context)
                if _fg_violation:
                    _fg_action = _fg_violation.get("action", "warn")
                    _fg_recipe = _fg_violation.get("recipe", "")
                    _fg_rule = _fg_violation.get("rule_id", "unknown")
                    _fg_sev = _fg_violation.get("severity", "low")
                    log(f"[FORGET_GUARD] rule={_fg_rule} action={_fg_action} sev={_fg_sev}")
                    if _fg_action == "deny":
                        # Only override if current result is not already a deny
                        _hso = result.get("hookSpecificOutput", {}) if isinstance(result, dict) else {}
                        if _hso.get("permissionDecision") != "deny":
                            result = {
                                "hookSpecificOutput": {
                                    "hookEventName": "PreToolUse",
                                    "permissionDecision": "deny",
                                    "permissionDecisionReason": (
                                        f"[ForgetGuard DENY rule={_fg_rule}] {_fg_recipe}"
                                    )
                                }
                            }
                    elif _fg_action == "warn":
                        # Append warning to permissionDecisionReason (don't override decision)
                        if isinstance(result, dict):
                            _hso = result.get("hookSpecificOutput", {})
                            _existing = _hso.get("permissionDecisionReason", "")
                            _warn_text = f"\n\n[ForgetGuard WARN rule={_fg_rule}] {_fg_recipe}"
                            if _existing:
                                _hso["permissionDecisionReason"] = _existing + _warn_text
                            else:
                                # attach as new field even without deny
                                _hso["permissionDecisionReason"] = _warn_text
                                result["hookSpecificOutput"] = _hso
            except Exception as _fg_exc:
                # Fail-open: forget_guard failure must not brick tool calls
                log(f"[FORGET_GUARD] check failed (fail-open): {_fg_exc}")

        # ── Brain Context Injection (Board 2026-04-19: Layer 3 root cause fix) ──
        # Query 6D brain for relevant wisdom nodes and inject into hook response.
        # CEO-only, read-only, graceful degradation (empty on any failure).
        _caller_for_brain = payload.get("agent_id", "")
        if _caller_for_brain in _ceo_identities:
            try:
                from hook_ceo_pre_output_brain_query import (
                    query_brain_for_context,
                    format_brain_context_for_hook,
                )
                _brain_nodes = query_brain_for_context(payload, k=3)
                if _brain_nodes:
                    _brain_text = format_brain_context_for_hook(_brain_nodes)
                    # Inject into result without overriding permission decision
                    if isinstance(result, dict):
                        result["brain_context"] = _brain_nodes
                        # Also append to permissionDecisionReason if present
                        _hso = result.get("hookSpecificOutput", {})
                        _existing_reason = _hso.get("permissionDecisionReason", "")
                        if _existing_reason:
                            _hso["permissionDecisionReason"] = (
                                _existing_reason + "\n\n" + _brain_text
                            )
                        log(f"[BRAIN] Injected {len(_brain_nodes)} wisdom nodes")
                    else:
                        log("[BRAIN] result is not dict, skipping injection")
            except Exception as _brain_exc:
                log(f"[BRAIN] Query failed (non-fatal): {_brain_exc}")

    except Exception as core_exc:
        # FAIL-CLOSED: Core governance path is broken.
        # Emit DENY event and block the tool call.
        log(f"[FAIL-CLOSED] Core governance unavailable: {core_exc}")
        log(traceback.format_exc())

        # Emit deny event via 3-tier fallback (CIEU → JSONL → stderr)
        try:
            import uuid
            REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
            SESSION_JSON = os.path.join(REPO_ROOT, ".ystar_session.json")
            sys.path.insert(0, REPO_ROOT)
            from ystar.adapters.identity_detector import get_active_agent
            try:
                with open(SESSION_JSON, "r") as f:
                    session = json.load(f)
                active_agent = get_active_agent(session)
            except Exception:
                active_agent = "unknown"

            deny_event = {
                "event_id": str(uuid.uuid4()),
                "session_id": "hook_fail_closed",
                "agent_id": active_agent,
                "event_type": "GOVERNANCE_FAIL_CLOSED",
                "action": "deny",
                "evidence_grade": "system",
                "created_at": time.time(),
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
            emit_cieu_or_fallback(deny_event, "CORE_FAIL_CLOSED")
        except Exception as build_exc:
            # Even building the event failed — stderr is our last resort
            try:
                sys.stderr.write(
                    f"[FAIL-CLOSED-L3] CORE_FAIL_CLOSED: event build failed. "
                    f"build_err={build_exc} core_err={core_exc}\n"
                )
            except Exception:
                pass

        # DENY the tool call
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"[Y*gov FAIL-CLOSED] Core governance unavailable. "
                    f"CIEU audit chain is broken — blocking tool call for safety.\\n\\n"
                    f"Error: {core_exc}\\n\\n"
                    f"Fix: Run \`ystar doctor\` to diagnose governance health."
                )
            }
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

