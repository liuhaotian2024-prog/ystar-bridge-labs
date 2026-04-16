# F2 Emit-Side Canonical Validation Pattern — 2026-04-16

**Context:** 39.8% unknown_family agent_id in 35k CIEU events. F1 fixed registry, F2 fixes emit points.

## Root Cause

Emit points (INSERT INTO cieu_events) **never validated agent_id** against canonical registry. Scripts hardcoded `"agent"`, `"system"`, `"ceo"`, or read `.ystar_active_agent` without validation. Result: numeric unknown_family persisted even after registry canonicalize.

## Solution Pattern

**Central emit helper with canonical validation:**

```python
# scripts/_cieu_helpers.py

def _load_canonical_registry() -> set[str]:
    """Load 19 canonical roles from governance/agent_id_canonical.json"""
    registry = json.load(open(CANONICAL_REGISTRY_PATH))
    canonical = set()
    canonical.update(registry["roles"].keys())  # 10 primary roles
    for component in registry["system_components"]:
        canonical.add(f"system:{component}")  # 7 system components
    canonical.add("system")  # fallback
    return canonical

def _get_canonical_agent() -> str:
    """Validate agent_id, return 'unidentified' + emit warning if not canonical."""
    agent_id = _get_current_agent()  # Read .ystar_active_agent
    if agent_id in _load_canonical_registry():
        return agent_id
    # Not canonical → emit warning
    _emit_unidentified_warning(agent_id, caller_context=_get_caller_context())
    return "unidentified"

def emit_cieu(event_type, decision, passed, task_description, **kwargs):
    """Central CIEU emitter with automatic canonical agent_id."""
    agent_id = _get_canonical_agent()  # Validated or 'unidentified'
    # ... INSERT INTO cieu_events with validated agent_id ...
```

**Usage in emit points:**

```python
# Before (session_health_watchdog.py)
conn.execute("""INSERT INTO cieu_events ...""", (
    event_id, seq_global, time.time(), "watchdog", "system", ...  # Hardcoded
))

# After
emit_cieu(
    event_type="SESSION_HEALTH_CHECK",
    decision="info",
    passed=1,
    task_description="Health OK",
    session_id="watchdog"
)
```

## Warning System

Non-canonical agent_id triggers `AGENT_ID_UNIDENTIFIED_EMIT` event:

```json
{
  "event_type": "AGENT_ID_UNIDENTIFIED_EMIT",
  "agent_id": "system",
  "decision": "warn",
  "passed": 0,
  "task_description": "Agent 'test-agent' not in canonical registry",
  "params_json": {
    "script": "/path/to/script.py",
    "line": 42,
    "function": "emit_drift"
  }
}
```

Also logs to stderr for real-time debugging:
```
[AGENT_ID_UNIDENTIFIED_EMIT] agent='test-agent' caller=/path/to/script.py
```

## Migration Strategy (Batch Approach)

**Batch 1 (F2):** ystar-company top 3 scripts (session_health_watchdog, session_close_yml, forget_guard)
- **Impact:** 16.27% unidentified rate (still high because unmigrated sources exist)

**Batch 2 (F2.1 scope):** Y-star-gov orchestrator + gov-mcp
- **Target:** SESSION_JSON_SCHEMA_VIOLATION (10,590 events), external_observation (10,511 events), orchestration:* (13,422 events)
- **Expected impact:** ~90% coverage of new events

**Batch 3:** Remaining 37 ystar-company scripts
- **Long tail cleanup**

## Atomic Pragmatism

**Why not migrate all 40 scripts at once?**
1. **Risk:** One bad migration breaks 40 emit points
2. **Verification:** Hard to isolate which script caused regression
3. **Tool budget:** 15 tool_use limit for atomic dispatch

**Better:** 3-5 scripts per batch + verification script + commit. Next batch learns from previous.

## Verification Script Pattern

Every emit-side migration batch must ship verification script:

```python
# scripts/f2_emit_verification.py
def main():
    # 1. Load registry
    registry = _load_canonical_registry()
    
    # 2. Test current agent validation
    current_agent = _get_canonical_agent()
    assert current_agent in registry or current_agent == "unidentified"
    
    # 3. Emit test event
    emit_cieu(event_type="F2_VERIFICATION_TEST", ...)
    
    # 4. Verify test event in DB has canonical agent_id
    cursor.execute("SELECT agent_id FROM cieu_events WHERE event_type = 'F2_VERIFICATION_TEST' ...")
    agent_id = cursor.fetchone()[0]
    assert agent_id in registry
    
    # 5. Check recent unidentified rate
    cursor.execute("SELECT COUNT(*) FILTER (WHERE agent_id = 'unidentified') / COUNT(*) ...")
    unidentified_pct = cursor.fetchone()[0]
    print(f"Unidentified rate: {unidentified_pct}%")
```

## Fail-Open Design

Emit helper must never crash caller:

```python
def emit_cieu(...):
    try:
        # ... validation + INSERT ...
        return True
    except Exception as e:
        sys.stderr.write(f"[CIEU_EMIT_ERROR] {event_type}: {e}\n")
        return False  # Fail-open
```

**Why:** Hook pipeline scripts (forget_guard, whitelist_emit) run async. Crash = silent hook failure = governance blind spot.

## Next Session Handoff

F2.1 batch should target Y-star-gov orchestrator emit points:
1. Grep Y-star-gov for `INSERT INTO cieu_events`
2. Find `session_json_schema_violation` emit point (10,590 events)
3. Migrate to `emit_cieu()` helper (may need to install helper in Y-star-gov or import from ystar-company)
4. Run verification + check unidentified rate drops below 5%

**Coordinate with CTO (Ethan)** — Y-star-gov changes need 86 tests to pass before commit.

---

**Ryan Park (eng-platform)**  
2026-04-16 — F2 emit-side fix completed, batch approach validated  
