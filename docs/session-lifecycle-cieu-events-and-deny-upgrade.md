# Task: Session Lifecycle CIEU Events + WARNING→DENY Upgrade + Protocol Rule

**Dispatcher:** CTO Ethan Wright (via Aiden/承远, single-Mac OpenClaw workspace)
**Executor:** Sub-agent engineering team — Maya-Governance lead, Ryan-Platform restarts daemon, Leo-Kernel runs tests (all sub-agents in the same Claude Code session, per AMENDMENT-004)
**Priority:** P0 — Board blocking, Board will test immediately upon completion
**Source Directive:** Board 2026-04-11 three-step urgent package
**Filed under docs/ (not .claude/tasks/) because CTO write-boundary excludes .claude/tasks/ — CEO to relocate if desired.**

---

## Context (what Board observed)

CIEU contains **no** session-lifecycle events — `session_start`, `session_close`, `continuation_loaded`, `obligation_check`, `boot_protocol_completed` are all absent. Because of that, `_check_must_check_health_on_session_start` has no ground-truth to reason over. Board wants three coordinated changes, then the hook daemon restarted so Board can test immediately.

Verified preconditions (read-only inspection by CTO on Windows):
- `Y-star-gov/ystar/adapters/cieu_writer.py` — 96 lines, `_write_boot_record` + `_write_cieu` use `CIEUStore.write_dict(...)` with free-string `event_type` and `evidence_grade` (no enum).
- `Y-star-gov/ystar/adapters/boundary_enforcer.py` — 2194 lines. Key anchors:
  - `_record_behavior_rule_cieu` at line 564
  - `_check_behavior_rules` at line 1508, DENY block starts 1559, WARNING calls 1580–1589
  - 10 WARNING-rule functions at lines 766, 819, 875, 937, 994, 1053, 1109, 1279, 1327, 1444
  - Module-level state `_SESSION_TOOL_CALLS`, `_SESSION_START_TIME` at 552–555
- `ystar-company/scripts/governance_boot.sh` — line 166 is `if [ $FAILURES -eq 0 ]; then … ALL SYSTEMS GO …` — inject `session_start` emit inside that branch.
- `ystar-company/scripts/session_close_yml.py` — `main()` at line 301, `return 0` at line 353 — inject `session_close` emit just before.

---

## Step 1 — Add 5 session-lifecycle CIEU event types + wire emitters

### 1.1 New event_types (free strings, no enum changes)

- `session_start`
- `session_close`
- `continuation_loaded`
- `obligation_check`
- `boot_protocol_completed`

All five written via `CIEUStore.write_dict({...})`. Use `evidence_grade="session_lifecycle"`.

### 1.2 Helper in `ystar/adapters/cieu_writer.py`

Append after `_write_boot_record`:

```python
def _write_session_lifecycle(
    event_type: str,
    who: str,
    session_id: str,
    cieu_db: str,
    extra_params: dict | None = None,
) -> None:
    """Write a session-lifecycle CIEU event.

    Valid event_type values:
      session_start, session_close, continuation_loaded,
      obligation_check, boot_protocol_completed.

    Silent-fail like _write_cieu — must never break the execution path.
    """
    try:
        from ystar.governance.cieu_store import CIEUStore
        store = CIEUStore(cieu_db)
        store.write_dict({
            "session_id":    session_id,
            "agent_id":      who,
            "event_type":    event_type,
            "decision":      "info",
            "passed":        True,
            "violations":    [],
            "params":        {"ts": time.time(), **(extra_params or {})},
            "contract_hash": "",
            "evidence_grade": "session_lifecycle",
        })
        _log.info("Session lifecycle event written: %s", event_type)
    except Exception as e:
        _log.error("session lifecycle write failed (non-fatal): %s", e)
```

Add to `__all__`.

### 1.3 Emit `session_start` from `scripts/governance_boot.sh`

Inside the `if [ $FAILURES -eq 0 ]; then` branch at line 166 (right after the `echo "=== GOVERNANCE BOOT: ALL SYSTEMS GO ==="`), add:

```bash
  # Emit session_start CIEU event (Board 2026-04-11)
  python3 - <<'PYEOF' 2>/dev/null
import json, os, sys, time
# Resolve Y-star-gov path (supports both Windows and MAC layouts)
candidates = [
    os.path.expanduser("~/.openclaw/workspace/Y-star-gov"),
    os.path.join(os.path.dirname(os.path.abspath(".")), "Y-star-gov"),
    r"C:\Users\liuha\OneDrive\桌面\Y-star-gov",
]
for p in candidates:
    if os.path.isdir(p):
        sys.path.insert(0, p); break
try:
    from ystar.adapters.cieu_writer import _write_session_lifecycle
    cfg = {}
    if os.path.exists(".ystar_session.json"):
        with open(".ystar_session.json") as f:
            cfg = json.load(f)
    sid = cfg.get("session_id", "unknown")
    _write_session_lifecycle("session_start", os.environ.get("AGENT_ID","unknown"),
                             sid, ".ystar_cieu.db",
                             {"boot_status": "ALL_SYSTEMS_GO"})
    print("[ok] session_start CIEU event emitted")
except Exception as e:
    print(f"[warn] session_start emit failed: {e}", file=sys.stderr)
PYEOF
```

Export `AGENT_ID` at the top of the script so the heredoc sees it: `export AGENT_ID="$AGENT_ID"` near line 15 (just after the arg parse).

### 1.4 Emit `session_close` from `scripts/session_close_yml.py`

In `main()`, just before `return 0` (line 353), add:

```python
    # Emit session_close CIEU event (Board 2026-04-11)
    try:
        sys.path.insert(0, str(YSTAR_GOV_PATH))
        from ystar.adapters.cieu_writer import _write_session_lifecycle
        sid = "unknown"
        sess_cfg_path = company_root / ".ystar_session.json"
        if sess_cfg_path.exists():
            sid = json.loads(sess_cfg_path.read_text()).get("session_id", "unknown")
        _write_session_lifecycle(
            "session_close", agent_id, sid, str(cieu_db_path),
            {"summary_preview": summary[:120]},
        )
    except Exception as e:
        print(f"[warn] session_close emit failed: {e}", file=sys.stderr)
```

### 1.5 Auto-emit `continuation_loaded`, `obligation_check`, `boot_protocol_completed` from `boundary_enforcer.py`

Add at module scope (after `_SESSION_DOCUMENTS_CREATED` at ~line 555):

```python
# ── Session lifecycle auto-emitters (Board 2026-04-11) ──
_PROTOCOL_STATE: dict = {}  # session_id -> set[str] of emitted events

def _hydrate_protocol_state(session_id: str, cieu_db: str = ".ystar_cieu.db") -> None:
    """Populate _PROTOCOL_STATE[session_id] from CIEU on first access per session."""
    if session_id in _PROTOCOL_STATE:
        return
    _PROTOCOL_STATE[session_id] = set()
    try:
        from ystar.governance.cieu_store import CIEUStore
        store = CIEUStore(cieu_db)
        # Use whatever query API CIEUStore exposes — fallback to raw iteration if needed.
        # See tests/test_cieu_store.py for the canonical accessor.
        for row in store.all() if hasattr(store, "all") else []:
            if row.get("session_id") == session_id and row.get("event_type") in {
                "session_start", "continuation_loaded",
                "obligation_check", "boot_protocol_completed",
            }:
                _PROTOCOL_STATE[session_id].add(row["event_type"])
    except Exception:
        pass  # silent — never break the hook path

def _emit_once(session_id: str, event: str, who: str,
               cieu_db: str = ".ystar_cieu.db", extra: dict | None = None) -> None:
    seen = _PROTOCOL_STATE.setdefault(session_id, set())
    if event in seen:
        return
    seen.add(event)
    try:
        from ystar.adapters.cieu_writer import _write_session_lifecycle
        _write_session_lifecycle(event, who, session_id, cieu_db, extra or {})
    except Exception as _e:
        _log.error("lifecycle emit failed: %s", _e)
```

Then, inside `_check_behavior_rules`, immediately after `_track_tool_call(who, tool_name, params)` (line 1542) and **before** the `cfg` load:

```python
    # Session lifecycle detection (runs regardless of per-agent rules cfg)
    try:
        from ystar.adapters.identity_detector import _load_session_config
        _cfg_lc = _load_session_config() or {}
        _sid = _cfg_lc.get("session_id", "unknown")
    except Exception:
        _sid = "unknown"
    _hydrate_protocol_state(_sid)

    # Detector 1: continuation_loaded
    if tool_name == "Read":
        _fp = str(params.get("file_path", "")).replace("\\", "/")
        if _fp.endswith("memory/continuation.json") or _fp.endswith("memory/continuation.md"):
            _emit_once(_sid, "continuation_loaded", who, extra={"file": _fp})

    # Detector 2: obligation_check
    if tool_name == "mcp__gov-mcp__gov_obligations":
        _emit_once(_sid, "obligation_check", who, extra={"tool": tool_name})
    elif tool_name == "Read" and "omission" in str(params.get("file_path", "")).lower():
        _emit_once(_sid, "obligation_check", who, extra={"tool": tool_name,
                                                         "via": "omission_db_read"})

    # Detector 3: boot_protocol_completed (all three present)
    _seen = _PROTOCOL_STATE.get(_sid, set())
    if {"session_start", "continuation_loaded", "obligation_check"}.issubset(_seen) \
            and "boot_protocol_completed" not in _seen:
        _emit_once(_sid, "boot_protocol_completed", who)
```

---

## Step 2 — New DENY rule `_check_session_start_protocol_completed`

Add the following function immediately **before** `_check_behavior_rules` (around line 1507):

```python
_BOOT_PROTOCOL_WHITELIST_TOOLS = {
    "mcp__gov-mcp__gov_obligations",
    "mcp__gov-mcp__gov_session_info",
    "mcp__gov-mcp__gov_health",
    "mcp__gov-mcp__gov_check",
    "mcp__gov-mcp__gov_doctor",
    "ToolSearch",
}

def _check_session_start_protocol_completed(
    who: str, tool_name: str, params: dict, session_cfg: Any = _SENTINEL
) -> Optional[PolicyResult]:
    """DENY any non-protocol action until session_start + continuation_loaded
    + obligation_check all appear in CIEU for the current session.

    Whitelist (always allowed even before protocol done):
      - gov-mcp obligations/session_info/health/check/doctor
      - ToolSearch (harness bookkeeping — cannot be blocked)
      - Bash running governance_boot.sh or session_close_yml.py
      - Read of memory/continuation.{json,md}, memory/session_handoff.md,
        or .ystar_session.json
    """
    try:
        from ystar.adapters.identity_detector import _load_session_config
        cfg = _load_session_config() or {}
        sid = cfg.get("session_id", "unknown")
    except Exception:
        return None  # silent-fail — never block on our own error

    _hydrate_protocol_state(sid)
    seen = _PROTOCOL_STATE.get(sid, set())

    if "boot_protocol_completed" in seen:
        return None  # fast path

    # Whitelist
    if tool_name in _BOOT_PROTOCOL_WHITELIST_TOOLS:
        return None
    if tool_name == "Bash":
        cmd = str(params.get("command", ""))
        if "governance_boot.sh" in cmd or "session_close_yml.py" in cmd:
            return None
    if tool_name == "Read":
        fp = str(params.get("file_path", "")).replace("\\", "/")
        if (fp.endswith("memory/continuation.json")
                or fp.endswith("memory/continuation.md")
                or fp.endswith("memory/session_handoff.md")
                or fp.endswith(".ystar_session.json")):
            return None

    missing = [e for e in ("session_start", "continuation_loaded", "obligation_check")
               if e not in seen]
    if not missing:
        return None  # three present, boot_protocol_completed will fire this call

    reason = (
        f"必须先完成session start protocol：1.跑boot 2.读continuation 3.查obligation. "
        f"Missing events: {missing}. Tool '{tool_name}' blocked for agent '{who}'."
    )
    _record_behavior_rule_cieu(
        who=who,
        rule_name="session_start_protocol_completed",
        event_type="BEHAVIOR_RULE_VIOLATION",
        decision="DENY",
        passed=False,
        reason=reason,
        params={"tool": tool_name, "missing": missing},
    )
    return PolicyResult(
        allowed=False, reason=reason, who=who, what=tool_name, violations=[],
    )
```

Wire it as the **first** DENY check inside `_check_behavior_rules` (just before `_check_autonomous_mission_requires_article_11` at line 1559):

```python
    deny_result = _check_session_start_protocol_completed(who, tool_name, params, cfg)
    if deny_result is not None:
        return deny_result
```

Per Board: this supersedes `_check_must_check_health_on_session_start`. Keep that function existing (and upgraded per Step 3) but it is now redundant; leave it in place until Board signs off on deletion in a follow-up.

---

## Step 3 — Upgrade 10 WARNING rules to DENY

Functions to upgrade (exact line numbers verified):

| Function | Line |
|---|---|
| `_check_verification_before_assertion` | 766 |
| `_check_root_cause_fix_required` | 819 |
| `_check_document_requires_execution_plan` | 875 |
| `_check_no_fabrication` | 937 |
| `_check_counterfactual_before_major_decision` | 994 |
| `_check_must_check_health_on_session_start` | 1053 |
| `_check_completion_requires_cieu_audit` | 1109 |
| `_check_directive_decompose_timeout` | 1279 |
| `_check_content_length_check` | 1327 |
| `_check_real_conversation_count_required` | 1444 |

For each: inside the violating branch,

1. `event_type="BEHAVIOR_RULE_WARNING"` → `event_type="BEHAVIOR_RULE_VIOLATION"`
2. `decision="WARNING"` → `decision="DENY"`
3. Replace the trailing `return None` (still inside the violating branch, after `_log.warning(reason)`) with:
   ```python
   return PolicyResult(
       allowed=False, reason=reason, who=who, what=tool_name, violations=[],
   )
   ```
   (Keep the function-level `return None` at the end — that's the "rule passed" path.)

**Special case — `_check_content_length_check` (1327):** the per-platform `for platform, ...` loop currently `_log.warning`s but does not return. Return the `PolicyResult` from inside the loop on first violation.

**Wiring change in `_check_behavior_rules` (lines 1579–1589):** move all 10 calls out of the WARNING block and into the DENY block, each wrapped as:

```python
    deny_result = _check_verification_before_assertion(who, tool_name, params, agent_rules)
    if deny_result is not None:
        return deny_result
    # ... repeat for the other 9 ...
```

Delete the old bare calls.

**Docstring update:** rewrite the enumerated rule list in the `_check_behavior_rules` docstring (lines 1514–1530) to mark rules 2–7, 10, 13, 14, 16 as `(DENY)` instead of `(WARNING)`.

---

## Step 4 — Tests, rebuild, restart, verify

### 4.1 Test-file updates (expected breakage)

Tests in `Y-star-gov/tests/test_behavior_rules.py` (and possibly `test_boundary_enforcer.py`) currently assert WARNING behavior for these 10 rules. **Lift expectations to DENY in the same commit — do not weaken the rules to pass stale tests.** Pattern per test:

```python
# Before:
assert result is None  # WARNING only
# After:
assert result is not None and result.allowed is False
assert "session_start_protocol" in result.reason or "BEHAVIOR_RULE_VIOLATION" in ...
```

### 4.2 Build + install

```bash
cd /path/to/Y-star-gov
python -m pytest tests/test_boundary_enforcer.py tests/test_behavior_rules.py -x
python -m pytest tests/ -x        # full suite — 86 tests must pass
python -m build
pip install --force-reinstall dist/ystar-*.whl
```

### 4.3 Restart hook daemon (Ryan-Platform)

```bash
pkill -f "ystar.*hook.*daemon" || true
ystar hook-install
ystar doctor
```

### 4.4 End-to-end verification

```bash
cd /path/to/ystar-company
# Preserve existing CIEU — do NOT wipe it for verification; just tail the new events.
bash scripts/governance_boot.sh cto
sqlite3 .ystar_cieu.db \
  "SELECT event_type, agent_id, datetime(created_at,'unixepoch')
   FROM cieu_events
   WHERE event_type IN ('session_start','session_close',
                        'continuation_loaded','obligation_check',
                        'boot_protocol_completed')
   ORDER BY created_at DESC LIMIT 20;"
# Expected: at least a session_start row for cto.
```

Simulate a fresh agent session and confirm a non-whitelisted tool call (e.g. `Write` to an arbitrary file) is DENIED with reason containing `必须先完成session start protocol`. After Read(continuation.json) + gov_obligations, `boot_protocol_completed` lands and subsequent calls are allowed.

---

## Deliverables

1. Code changes in one logical commit:
   - `Y-star-gov/ystar/adapters/cieu_writer.py`
   - `Y-star-gov/ystar/adapters/boundary_enforcer.py`
   - `ystar-company/scripts/governance_boot.sh`
   - `ystar-company/scripts/session_close_yml.py`
   - `Y-star-gov/tests/test_behavior_rules.py` (+ any sibling tests with WARNING expectations)
2. New wheel installed on MAC, hook daemon restarted, `ystar doctor` green.
3. Verification log posted back (the sqlite SELECT above + one DENY-fire sample) to `reports/daily/`.

**Do not** commit the wheel artifact or `.ystar_cieu.db`. Code + tests only.

---

## Risk Analysis

- **Self-brick risk:** the new DENY rule could block its own protocol. Mitigated by whitelist (boot script, continuation reads, gov_* MCP, ToolSearch) and silent-fail on config-load errors.
- **Stale tests:** guaranteed to break — fix expectations in the same patch.
- **Daemon state loss on restart:** `_PROTOCOL_STATE` hydrates from CIEU on first call per session; crashes and restarts recover correctly.
- **`CIEUStore.all()` API assumption:** if that accessor doesn't exist, Maya should use whatever `tests/test_cieu_store.py` demonstrates as the canonical read path. The hydrate helper silent-fails either way — correctness degrades to "DENY fires once legitimately after first manual protocol completion," which is acceptable.

---

## Why this matters

Board's observation is the root-cause fix: the governance layer has been asserting behavior rules with no ground-truth event stream beneath them. After this patch, every future behavioral rule can key off five canonical lifecycle events instead of heuristics over `_SESSION_TOOL_CALLS`.
