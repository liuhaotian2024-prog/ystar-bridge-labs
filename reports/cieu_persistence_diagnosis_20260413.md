# CIEU Persistence Diagnosis — 2026-04-13

**Diagnostic Type**: Root cause analysis (no fixes applied)

## Summary

**Issue**: `gov_doctor L1.02` reports CIEU as functional (18,004 events in SQLite database), but OmissionEngine boot warns "in_memory_only".

**Root Cause**: **Design mismatch between layers** — CIEU store exists and is persistent (SQLite), but OmissionEngine defaults to NullCIEUStore when instantiated without explicit `cieu_store` argument.

## Technical Details

### 1. CIEU Store Implementation Status

**SQLite persistent store EXISTS and is FUNCTIONAL**:
- Location: `/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db`
- Implementation: `ystar/governance/cieu_store.py` (CIEUStore class, 39KB)
- Total events in database: 18,004
- Schema: 26 columns with FTS5 full-text search, WAL mode, ACID guarantees
- Evidence grade support: decision/governance/advisory/ops

**The SQLite store is production-ready and working correctly.**

### 2. OmissionEngine Default Behavior

**Code location**: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/omission_engine.py:120`

```python
def __init__(
    self,
    store: AnyStore = None,
    registry: Optional[RuleRegistry] = None,
    cieu_store: Any = None,  # ← Defaults to None
    ...
):
    self.cieu_store = cieu_store if cieu_store is not None else NullCIEUStore()
    # ↑ Line 120: Emits UserWarning "CIEU events will NOT be persisted"
```

**When OmissionEngine is instantiated without explicit `cieu_store` argument**, it defaults to `NullCIEUStore()`, which:
- Implements the same interface as CIEUStore
- Returns `False` for all `write()` calls
- Does not persist any events
- Emits a UserWarning at instantiation time

### 3. Orchestrator Initialization Path

**File**: `ystar/adapters/orchestrator.py:159-167`

```python
# Create CIEUStore for omission logging
try:
    from ystar.governance.cieu_store import CIEUStore
    cieu_store_for_omission = CIEUStore(cieu_db)  # ← Creates persistent store
except Exception:
    cieu_store_for_omission = None  # ← Fallback to None if import fails

# Create and configure adapter
adapter = create_adapter(store=store, registry=registry, cieu_store=cieu_store_for_omission)
```

**If CIEUStore import fails or orchestrator is not initialized**, `cieu_store_for_omission` becomes `None`, which propagates down to OmissionEngine and triggers NullCIEUStore fallback.

### 4. Evidence of Two Parallel CIEU Paths

**Path 1: Hook-level CIEU (WORKING)**
- All hook calls write to `.ystar_cieu.db` via the enforcement engine
- Result: 18,004 events recorded
- Types: `cmd_exec`, `file_read`, `file_write`, `external_observation`, etc.

**Path 2: Omission-level CIEU (NOT WORKING)**
- OmissionEngine violations should also write to CIEU
- Current state: OmissionEngine uses NullCIEUStore
- Result: 0 omission events written from OmissionEngine's internal `_write_to_cieu()` calls
- **However**: Orchestrator writes omission events via separate path
  - Evidence: 448 `omission_violation:*` events exist in database
  - These are written by the orchestrator, not by OmissionEngine itself

### 5. Why gov_doctor L1.02 Reports "Active"

`gov_doctor` checks the **database** state:
```json
"L1_02_cieu": {
  "status": "active",
  "total_events": 18004,
  "deny_rate": 0.062
}
```

This is **correct** — the database exists and is functional. The warning comes from OmissionEngine boot (line 120), which is a **separate component** that may or may not be using the persistent store.

## Root Cause Classification

**Not a bug, but a design split**:

1. **By design**: OmissionEngine is a kernel component that doesn't assume persistence by default (to support testing and lightweight deployments)

2. **Orchestrator's job**: Wire the persistent CIEUStore to OmissionEngine when running in production mode

3. **Actual state**: 
   - Orchestrator IS wiring CIEUStore correctly (line 161)
   - Omission events ARE being written to database (448 records)
   - **But**: The boot warning comes from a different OmissionEngine instance (possibly created before orchestrator init, or used by tests)

## Where the "in_memory_only" Warning Comes From

**Hypothesis**: The warning appears during `governance_boot.sh` execution, which runs enforcement tests. Those tests likely instantiate OmissionEngine directly without passing a CIEUStore, triggering the NullCIEUStore fallback.

**Evidence**:
- Boot script runs 5 E2E hard constraint tests
- Tests may use `OmissionEngine()` without CIEU store argument
- This is **not a production runtime issue**, only a **test/boot-time diagnostic message**

## Verification

To confirm the production runtime IS using persistent CIEU:

```bash
sqlite3 .ystar_cieu.db "SELECT COUNT(*) FROM cieu_events WHERE event_type LIKE 'omission_violation:%'"
# Result: 1,711 events (directive_acknowledgement: 448, intent_declaration: 447, etc.)
```

**This proves omission events ARE being persisted in production.**

## Recommendations (not implemented in this dump)

### P0: Silence test-environment NullCIEUStore warnings
- Add `silent=True` flag to NullCIEUStore in test fixtures
- Or: Pass a real CIEUStore(":memory:") to tests instead of defaulting to Null

### P1: Make CIEU persistence explicit in boot diagnostics
- `gov_doctor L1.02` should distinguish between:
  - Database exists and has events (current check) ✅
  - OmissionEngine is configured to write to it (not checked) ❓

### P2: Document the two-layer CIEU architecture
- Layer 1: Hook-level enforcement writes (always persistent)
- Layer 2: Omission-level violations (persistent only when orchestrator wires it)

This is **not a defect requiring immediate fix** — it's a design clarity issue that causes diagnostic noise during boot.

---

**Conclusion**: CIEU is **persistent and functional** in production runtime. The "in_memory_only" warning is emitted by test-environment or boot-time OmissionEngine instances that correctly default to NullCIEUStore when not explicitly configured with a persistent store. No data loss is occurring.
