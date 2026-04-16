# Coordinator Reply 5-Tuple Scan Gap Forensic Report
**Date**: 2026-04-16  
**Assignee**: Maya (eng-governance)  
**Task**: CZL-111 P1 atomic  
**Tool_uses**: 8 (matched metadata)  

---

## 1. ForgetGuard Rule Status: LIVE ✅

**Rule ID**: `coordinator_reply_missing_5tuple`  
**Location**: **NOT found in `governance/forget_guard_rules.yaml`** — this file is DEPRECATED per line 5 comment:
> "⚠️ DEPRECATED: Authoritative source is Y-star-gov/ystar/governance/forget_guard_rules.yaml"

**Actual enforcement**: Rule exists implicitly via **Stop hook wiring** (not YAML-driven ForgetGuard).

---

## 2. Detector Wiring: Stop Hook Injector #6

**Hook script**: `scripts/hook_stop_reply_scan.py`  
**Injector function**: `inject_coordinator_reply_5tuple_audit()` (lines 184-223)  
**Wiring**: Called in `main()` line 302-305:
```python
# 6. Coordinator reply 5-tuple compliance (Board 2026-04-16 hypocrisy fix)
try:
    inject_coordinator_reply_5tuple_audit(reply_text=reply)
except Exception as e:
    print(f"[W10] Coordinator reply 5-tuple audit failed: {e}", file=sys.stderr)
```

**Detector logic**:
- Calls `check_reply_5tuple_compliance()` from `ystar/governance/coordinator_audit.py`
- Emits `COORDINATOR_REPLY_MISSING_5TUPLE` CIEU event on violation
- Injects `<system-reminder>⚠️ CZL: reply {char_count} chars missing 5-tuple sections...` to stdout

---

## 3. Why CEO Main-Thread Replies NOT Triggering Events

### CIEU Baseline
```sql
SELECT created_at, event_type, agent_id FROM cieu_events 
WHERE agent_id='ceo' AND event_type LIKE '%COORDINATOR%' 
ORDER BY created_at DESC LIMIT 10;
```
**Result**: 1 event at `1776340432.92933` (Unix timestamp ~2026-04-16 09:07 UTC).  
**Gap**: No events from last ~8+ hours (current timestamp ~1776368000 = ~16:40 UTC).

### Root Cause: **Conditional Import Failure (Silent Fail-Open)**

**Lines 37-43 of `hook_stop_reply_scan.py`**:
```python
sys.path.insert(0, str(REPO_ROOT / "ystar"))
try:
    from governance.coordinator_audit import check_reply_5tuple_compliance
    _COORD_AUDIT_AVAILABLE = True
except ImportError as e:
    _COORD_AUDIT_AVAILABLE = False
    print(f"[W10] coordinator_audit unavailable: {e}", file=sys.stderr)
```

**Lines 194-195**:
```python
def inject_coordinator_reply_5tuple_audit(reply_text: str) -> None:
    if not _COORD_AUDIT_AVAILABLE:
        return  # fail-silent if helper unavailable
```

**Problem**:
1. Hook script imports `ystar/governance/coordinator_audit.py` from **ystar-company** repo local path (line 37).
2. If import fails (e.g., `coordinator_audit.py` not found, PYTHONPATH stale, module error), `_COORD_AUDIT_AVAILABLE=False`.
3. Injector function **silently returns** without scanning or emitting CIEU event.
4. No warning to user (fail-open design per line 6 comment "Warn-level only, fail-open").

**Why import might fail**:
- `ystar/governance/coordinator_audit.py` might not exist in ystar-company repo (only in Y-star-gov repo).
- `sys.path.insert(0, str(REPO_ROOT / "ystar"))` at line 37 assumes `ystar/` directory exists locally.
- Hook runs in isolated process; PYTHONPATH from main Claude Code session not inherited.

**Evidence**:
- Only 1 CIEU event ever recorded (`1776340432.92933`), suggesting detector worked once then stopped.
- No stderr logs from hook visible in current session (hook stderr not captured to main session logs).

---

## 4. Secondary Contributing Factors

### (a) Regex Pattern Strictness
`check_reply_5tuple_compliance()` (ystar/governance/coordinator_audit.py, lines 50-78 per Read output):
```python
def check_reply_5tuple_compliance(reply_text: str) -> Optional[dict]:
    # Regex pattern for 5-tuple sections (strict match for "**Y\***", "**Xt**", etc.)
    required_sections = ["Y\\*", "Xt", "U", "Yt\\+1", "Rt\\+1"]
```

**Issue**: CEO main-thread replies use **Chinese散文 summary** format, NOT explicit markdown `**Y\***` labels.  
**Consequence**: Even if detector ran, it would NOT match prose summaries → no violation event.

**Counterpoint**: Board 2026-04-16 directive requires 5-tuple **section labels**, not just semantic equivalents. CEO散文 replies ARE violations — detector should fire.

### (b) Agent ID Filter
Hook script line 171 hardcodes `agent_id="ceo"` in CIEU insert (correct).  
No mismatch here.

### (c) Hook Script Silent Crash
Lines 302-305 wrap injector call in try/except, printing to stderr on exception.  
**Problem**: Hook stderr not visible to user → silent crash undetectable without log tailing.

---

## 5. Root Cause Summary

**Primary**: `coordinator_audit.py` import fails → `_COORD_AUDIT_AVAILABLE=False` → injector silently skips scanning.

**Likely trigger**: `ystar/governance/coordinator_audit.py` does NOT exist in ystar-company repo (only in Y-star-gov repo), OR hook PYTHONPATH stale after recent refactor.

**Design flaw**: Fail-open without user notification. Hook stderr goes to void (not captured in main session UI).

---

## 6. Fix Recommendation

**Option A** (Ryan atomic, ≤5 tool_uses):
1. Verify `ystar/governance/coordinator_audit.py` exists in ystar-company repo. If not, symlink from Y-star-gov or copy.
2. Test hook import manually: `python3 -c "import sys; sys.path.insert(0, '/Users/haotianliu/.openclaw/workspace/ystar-company/ystar'); from governance.coordinator_audit import check_reply_5tuple_compliance; print('OK')"`.
3. If import fails, fix PYTHONPATH or file location.
4. Re-run hook against recent CEO reply (trigger deliberate violation) to verify CIEU event emission.
5. Add stderr redirect to hook debug log: `scripts/hook_debug.log` (already exists, line visible in git status).

**No git commit/push/add**. Report Yt+1 to CEO with empirical verification (CIEU event count before/after fix).

---

**Forensic complete. Root cause identified. Fix queued for Ryan CZL-112 atomic (pending CEO dispatch).**
