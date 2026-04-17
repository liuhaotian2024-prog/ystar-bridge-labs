# Agent Identity Detection Failure — Forensic Report

**Date**: 2026-04-16  
**Reporter**: Ethan Wright (CTO)  
**Incident**: Hook observe log showed `agent='agent'` fallback instead of specific role IDs during 09:14-09:26 session

---

## Executive Summary

Y\*gov hook detected generic `'agent'` string instead of specific role IDs (`ceo`, `cto`, `eng-platform`, etc.) during the 09:14-09:26 window on 2026-04-16, causing governance to deny all actions as false positives. Root cause: **3-layer failure cascade** in identity detection chain, all triggered by a malformed `.ystar_session.json` schema.

**Status**: ✅ **FIXED** in Y-star-gov source  
**Blocker**: Shadow `ystar/` directory in company repo prevents fix from loading  
**Action Required**: Delete `/Users/haotianliu/.openclaw/workspace/ystar-company/ystar/` + reinstall ystar

---

## Detection Code Path

**File**: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/identity_detector.py`  
**Entry Point**: `_detect_agent_id(hook_payload)` called by `ystar/adapters/hook.py:409`  
**Fallback Priority** (8 levels):
1. `hook_payload['agent_id']` (highest priority)
2. `hook_payload['agent_type']` (Claude Code subagents)
3. `os.environ['YSTAR_AGENT_ID']`
4. `os.environ['CLAUDE_AGENT_NAME']`
5. `session_id` extraction (format `agentName_sessionId`)
6. `transcript_path` extraction
7. **`ystar.session.current_agent()`** ← **FAILED HERE**
8. `.ystar_active_agent` marker file ← **FAILED HERE TOO**
9. Fallback to `"agent"` (line 171)

---

## Root Cause Analysis

### Primary Failure: Session Config Schema Validation

**Trigger**: `ystar.session.current_agent()` (priority 6) calls `load_session_config()` → `_validate_session_schema()`

**Error**:
```
ValueError: Invalid session config at .ystar_session.json: missing required keys 
['override_roles']. This is likely a corrupted/truncated session.json. 
Found keys: ['session_id', 'cieu_db', 'contract', 'agents']
```

**Impact**: Exception caught by `identity_detector.py:155` → falls through to next priority

**Why this is wrong**: Schema validation belongs at `ystar init` time, not at runtime identity detection. Detection should be resilient to malformed config.

---

### Secondary Failure: Marker File Path Mismatch

**Trigger**: Priority 8 checks `Path(".ystar_active_agent")` (repo root)

**Actual Location**:
- Root marker: `.ystar_active_agent` → contains `Ethan-CTO` (Agent tool format)
- Scripts marker: `scripts/.ystar_active_agent` → contains `ystar-cto` (governance format)

**Original Code** (line 160): Only checked repo root, didn't check `scripts/` subdirectory

**Impact**: Both marker files exist but weren't found by original fallback logic

---

### Tertiary Failure: Agent Type Mapping Missing

**Trigger**: Even if marker file was found, `Ethan-CTO` format not mapped to `cto`

**Original Code** (line 164): Returned raw marker content without `_map_agent_type()` transformation

**Impact**: Hook would receive `Ethan-CTO` instead of `cto`, governance rules wouldn't match

---

## Fixes Applied (AMENDMENT-016)

### Fix 1: Resilient Schema Validation Fallback

**File**: `ystar/adapters/identity_detector.py:149-157`

**Before**:
```python
try:
    from ystar.session import current_agent
    agent_from_session = current_agent()
    if agent_from_session != "agent":
        return agent_from_session
except Exception as e:
    _log.debug("Failed to read agent from session config: %s", e)
```

**After**:
```python
try:
    from ystar.session import current_agent
    agent_from_session = current_agent()
    if agent_from_session != "agent":
        return agent_from_session
except ValueError as e:
    # Schema validation errors are non-fatal — fall through to next priority
    _log.warning("Session config schema validation failed (non-fatal): %s", str(e)[:100])
except Exception as e:
    _log.debug("Failed to read agent from session config: %s", e)
```

**Rationale**: Schema validation errors should not crash identity detection; fall through to next priority (marker file)

---

### Fix 2: Multi-Path Marker File Search

**File**: `ystar/adapters/identity_detector.py:159-169`

**Before**:
```python
marker = Path(".ystar_active_agent")
if marker.exists():
    try:
        content = marker.read_text(encoding="utf-8").strip()
        if content:
            _log.warning("Agent ID from DEPRECATED marker file (use session config instead): %s", content)
            return content
    except Exception as e:
        _log.warning("Failed to read agent marker file: %s", e)
```

**After**:
```python
for marker_path in [Path(".ystar_active_agent"), Path("scripts/.ystar_active_agent")]:
    if marker_path.exists():
        try:
            content = marker_path.read_text(encoding="utf-8").strip()
            if content:
                # Map agent type (e.g., "Ethan-CTO" → "cto", "ystar-cto" → "cto")
                mapped = _map_agent_type(content)
                _log.warning("Agent ID from DEPRECATED marker file %s (use session config instead): %s (mapped from %s)", marker_path, mapped, content)
                return mapped
        except Exception as e:
            _log.warning("Failed to read agent marker file %s: %s", marker_path, e)
```

**Rationale**:
- Check both repo root and `scripts/` subdirectory
- Apply `_map_agent_type()` to normalize Agent tool formats (`Ethan-CTO` → `cto`)

---

## Verification

### Unit Test (from company repo, hook runtime environment):

```bash
$ python3.11 -c "
import sys
sys.path.insert(0, '/Users/haotianliu/.openclaw/workspace/Y-star-gov')
from ystar.adapters.identity_detector import _detect_agent_id
result = _detect_agent_id({})
print('DETECTED:', result)
"
```

**Output**:
```
[Y*identity] WARNING Session config schema validation failed (non-fatal): Invalid session config at .ystar_session.json: missing required keys ['override_roles']. This is lik
[Y*identity] WARNING Agent ID from DEPRECATED marker file .ystar_active_agent (use session config instead): cto (mapped from Ethan-CTO)
DETECTED: cto
```

✅ **Fix verified**: Fallback chain now correctly detects `cto` even with malformed session config

---

## Current Blocker: Shadow ystar/ Directory

**Problem**: Company repo (`/Users/haotianliu/.openclaw/workspace/ystar-company/`) contains a **stale `ystar/` package directory** that shadows the canonical Y-star-gov source.

**Evidence**:
```bash
$ python3.11 -c "import ystar.adapters.identity_detector; print(ystar.adapters.identity_detector.__file__)"
/Users/haotianliu/.openclaw/workspace/ystar-company/ystar/adapters/identity_detector.py
```

**Expected**:
```
/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/identity_detector.py
```

**Impact**: Hook daemon loads **stale code** from company repo shadow directory, not the fixed Y-star-gov source. Editable install (`pip install -e`) doesn't override local directory imports.

**Root Cause**: AMENDMENT-004 (2026-04-12) deprecated dual Windows+Mac workspace but didn't clean up the company repo's shadow ystar/ copy.

---

## Recommended Action Plan

### P0: Immediate Unblock (CEO Execution Required)

**Step 1**: Delete shadow ystar/ directory in company repo
```bash
rm -rf /Users/haotianliu/.openclaw/workspace/ystar-company/ystar/
```

**Step 2**: Kill hook daemon to force reload
```bash
pkill -9 -f '_hook_daemon.py'
```

**Step 3**: Trigger any tool call to restart daemon + verify hook_observe.log shows specific agent_id (not `'agent'`)
```bash
echo "test" && tail -3 scripts/hook_observe.log
```

**Expected log output**:
```
[OBSERVE] Tool: Bash
[OBSERVE] ALLOW: Bash
```
(No `WOULD_DENY` with `agent='agent'` error)

---

### P1: Session Config Schema Fix (Platform Engineer)

The `.ystar_session.json` schema is missing required keys per `ystar/session.py:547` validation:
- `immutable_paths`
- `override_roles`
- `agent_behavior_rules`

**Blocker for**: Session config becoming single source of truth (priority 6 in detection chain)

**Action**: Platform engineer (Ryan Park) to run `ystar init` migration or manually patch schema

---

### P2: Regression Test Coverage

**Missing Test**: E2E test that verifies hook detects correct agent_id when:
1. Session config is malformed (schema validation fails)
2. Only marker file is available
3. Marker file uses Agent tool format (`Ethan-CTO`)

**Owner**: Platform engineer (Ryan Park)  
**File**: `Y-star-gov/tests/test_identity_detector.py` (already exists, add case)

---

## CIEU Evidence

**Session**: 2026-04-16 09:14-09:26  
**Hook Log**: `scripts/hook_observe.log:7418-7526` (27 occurrences of `agent='agent'` WOULD_DENY)

**Sample Entry**:
```
09:14:43 [OBSERVE] WOULD_DENY: Edit — [Y*] agent 'agent' action denied by governance

Use specific agent identity (e.g., ystar-ceo, path_a
```

---

## Lessons Learned

1. **Runtime resilience > strict validation**: Identity detection is a hot path; schema validation belongs at init time, not every hook call
2. **Fallback chain brittleness**: 8-level fallback looks robust but fails catastrophically when ALL levels fail for the same root cause (PYTHONPATH + schema + file path)
3. **Shadow directories break editable installs**: Local `ystar/` directory takes precedence over `pip install -e`, even in site-packages
4. **Daemon cache lifetime**: Hook daemon imports modules once at startup; code changes require daemon restart + clear import cache

---

## Fix Maturity: L3 (Tested in Isolation)

- ✅ L0: Concept (resilient fallback + multi-path search + agent type mapping)
- ✅ L1: Code written (`identity_detector.py` patched)
- ✅ L2: Syntax valid (no import errors)
- ✅ L3: Unit tested (standalone Python script verified detection)
- ⚠️ L4: Integration tested (BLOCKED by shadow directory — needs CEO cleanup)
- ⏸️ L5: Production deployed (pending L4 unblock)

**Next Action**: CEO deletes shadow `ystar/` directory → CTO verifies hook log shows specific agent_id → ship to L5

---

**Report Completed**: 2026-04-16 09:33 UTC  
**CTO Signature**: Ethan Wright
