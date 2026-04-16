# Daemon Concurrent-Write Investigation (CZL-105 P2)

**Date**: 2026-04-16  
**Investigator**: CTO (Ethan Wright)  
**Task**: #25 Backlog Drain — daemon concurrent-write/socket-lock forensics  
**Campaign**: Campaign v6 — K9 Routing + Phase 2-3 Backlog Drain  

---

## Executive Summary

**Finding**: Current daemon architecture has **partial race protection** — SQLite CIEU db uses WAL mode (wal + checkpoint=1000), but **3 shared resources lack explicit locking**:
1. `.ystar_active_agent` (10 bytes, plain text)
2. `dispatch_board.json` (17 bytes, JSON)
3. `hook_observe.log` (440KB, append-only log)

**Race Risk**: Medium-Low. No empirical CIEU evidence of write corruption (0 events matching `WRITE_ERROR`, `CORRUPT`, `partial write`, `lock timeout`). However, `.ystar_active_agent` drift incidents documented in Memory (feedback_daemon_cache_workaround, project_active_agent_drift) suggest **semantic race** (stale value cached, not corrupt write).

**Recommendation**: Implement **per-resource advisory locks** (fcntl.flock) for `.ystar_active_agent` and `dispatch_board.json`. `hook_observe.log` safe as append-only (POSIX guarantees atomic appends <PIPE_BUF). AMENDMENT-016 daemon stateless rewrite appears **in-progress but NOT LIVE** (no shipped code detected in CZL-105 investigation window).

---

## 1. Daemon Inventory

### Active Daemons Writing Shared Resources

| Daemon | PID File | Write Targets | Lock Mechanism | Race Risk |
|--------|----------|---------------|----------------|-----------|
| `k9_routing_subscriber.py` | `/tmp/k9_subscriber.pid` | CIEU db, `.ystar_warning_queue.json` | SQLite WAL (db only) | LOW (db protected, queue single-writer) |
| `k9_alarm_consumer.py` | `scripts/.k9_alarm_consumer.pid` | CIEU db, `governance/reminders/*.md`, `governance/blocking_events.log`, `governance/czl_escalations.json`, `governance/ceo_escalations.json`, `governance/hook_health_escalations.json` | SQLite WAL (db only) | LOW-MEDIUM (multiple JSON files, no locks) |
| `cto_dispatch_broker.py` | `scripts/.cto_broker.pid` | CIEU db, `dispatch_board.json` | **fcntl.flock** (LOCK_SH/LOCK_EX) | **LOW (flock live, lines 29-42)** |
| `engineer_task_subscriber.py` | `scripts/.engineer_subscriber.pid` | CIEU db, `dispatch_board.json` (via subprocess) | Subprocess delegates to dispatch_board.py | LOW (single subscriber instance) |

### Shared Resource Lock Coverage

| Resource | Writers | Lock Type | Status |
|----------|---------|-----------|--------|
| `.ystar_cieu.db` | All 4 daemons + hook adapter | SQLite WAL (journal_mode=wal, checkpoint=1000) | ✅ PROTECTED |
| `.ystar_active_agent` | Hook daemon, governance_boot.sh, agent_mode_manager.py | **NONE** | ❌ UNPROTECTED |
| `dispatch_board.json` | cto_dispatch_broker, engineer_task_subscriber (via dispatch_board.py) | fcntl.flock (LOCK_SH/LOCK_EX) in broker only | ⚠️ PARTIAL (broker has lock, subscriber calls dispatch_board.py subprocess — needs audit) |
| `hook_observe.log` | Hook daemon (Y-star-gov adapter) | NONE (append-only) | ✅ SAFE (POSIX atomic append <PIPE_BUF) |
| `.ystar_warning_queue.json` | k9_routing_subscriber | NONE | ⚠️ LOW (single writer, but no lock) |
| `governance/*.json` (escalations, czl_escalations, etc.) | k9_alarm_consumer | NONE | ⚠️ MEDIUM (multiple JSON files, append-like writes) |

---

## 2. Empirical Evidence of Races

### CIEU Query for Write Failures
```sql
SELECT COUNT(*) FROM cieu_events WHERE 
  event_type LIKE '%WRITE_ERROR%' OR 
  event_type LIKE '%CORRUPT%' OR 
  task_description LIKE '%partial write%' OR 
  task_description LIKE '%lock timeout%';
```
**Result**: `0` events.

**Interpretation**: No hard crashes or corruption detected in CIEU audit trail. However, **semantic race** documented:
- Memory entry `project_active_agent_drift`: Sub-agent completes, doesn't restore `.ystar_active_agent`, CEO loses write permissions.
- Memory entry `feedback_daemon_cache_workaround`: Daemon caches old agent_id after sub-agent runs, temporary workaround = `pkill -9 + rm socket`.

**Root Cause Hypothesis**: `.ystar_active_agent` is **read-modify-write** without lock:
1. Daemon A reads "cto" from file
2. Sub-agent spawns, writes "ryan-platform"
3. Daemon A caches old "cto" value in memory
4. Sub-agent exits, doesn't write "cto" back (assumes daemon owns state)
5. CEO tries to write, hook adapter sees agent_id="cto" (from Daemon A's stale env) vs file="ryan-platform", rejects as unauthorized.

This is **not a write collision** — it's a **state-ownership race**.

---

## 3. Lock Strategy Recommendation

### Tier 1: Critical (Implement Now)
- **`.ystar_active_agent`**: Mandatory `fcntl.flock(LOCK_EX)` on all writes (governance_boot.sh, agent_mode_manager.py, hook daemon). Read-only accesses use `LOCK_SH`.
- **Pattern**: Same as `cto_dispatch_broker.py` lines 26-42:
  ```python
  with open(PATH, "r+") as f:
      fcntl.flock(f.fileno(), fcntl.LOCK_EX)
      # read-modify-write
      fcntl.flock(f.fileno(), fcntl.LOCK_UN)
  ```

### Tier 2: Medium Priority
- **`dispatch_board.json`**: Audit `engineer_task_subscriber` subprocess calls to `dispatch_board.py` — verify they inherit flock from parent OR dispatch_board.py has its own lock.
- **`governance/*.json` (escalations, czl_escalations, etc.)**: Convert to single-file append log OR add flock to k9_alarm_consumer JSON writes.

### Tier 3: No Action Required
- **CIEU database**: WAL mode sufficient (concurrent reads + single-writer queue via timeout).
- **`hook_observe.log`**: Append-only, POSIX guarantees atomic <PIPE_BUF (4KB on macOS/Linux).

### Advisory vs Mandatory Locks
**Recommendation**: **Advisory locks only** (fcntl.flock). Rationale:
- Mandatory locks require filesystem support (not portable across macOS/Linux dev vs prod).
- All Y* Bridge Labs daemons are cooperative (same team, same codebase).
- Advisory flock is the POSIX standard for this use case.

---

## 4. AMENDMENT-016 Daemon Stateless Rewrite Status

**Expected Scope (per AGENTS.md reference)**: "委派好用到 CEO 不需要自己写 (AMENDMENT-016 daemon identity fix)".

**Investigation**: Grep for AMENDMENT-016 across repo:
- **Found references**: docs/AMENDMENT_018 (SSoT sync transport), scripts/exp7_bootstrap.sh (pilot).
- **No shipped daemon refactor detected**: k9_routing_subscriber.py, k9_alarm_consumer.py, cto_dispatch_broker.py all retain stateful PID files + long-running while loops.
- **Conclusion**: AMENDMENT-016 daemon stateless rewrite is **PLANNED but NOT SHIPPED** as of 2026-04-16 CZL-105 investigation window.

**Impact on Race Risk**: Stateless rewrite would eliminate the `.ystar_active_agent` cache race by removing daemon state ownership. Until shipped, **lock-based mitigation required**.

---

## 5. Race Inventory Table

| Race Type | Resource | Daemons Involved | Symptoms | Severity | Mitigation |
|-----------|----------|------------------|----------|----------|------------|
| Read-Modify-Write | `.ystar_active_agent` | Hook daemon, governance_boot, agent_mode_manager | CEO write permissions lost, "restricted" errors | **HIGH** | Add fcntl.flock |
| Concurrent JSON Write | `dispatch_board.json` | cto_broker, engineer_subscriber subprocess | None detected (broker has flock) | LOW | Audit subprocess lock inheritance |
| Concurrent JSON Append | `governance/ceo_escalations.json` etc. | k9_alarm_consumer (solo writer) | None detected | LOW | Consider single-file append log OR add flock |
| SQLite Write Collision | `.ystar_cieu.db` | All 4 daemons + hook adapter | None (WAL mode) | **NONE** | Already mitigated |
| Log Write Collision | `hook_observe.log` | Hook adapter (solo writer) | None (POSIX atomic append) | **NONE** | No action |

---

## 6. Recommended Next Steps

1. **Immediate (P0)**: Add fcntl.flock to `.ystar_active_agent` writes in:
   - `scripts/governance_boot.sh` (shell flock wrapper OR rewrite critical section in Python)
   - `scripts/agent_mode_manager.py`
   - Y-star-gov hook adapter (if it writes .ystar_active_agent)

2. **Next Sprint (P1)**: Audit `engineer_task_subscriber` subprocess dispatch_board.py calls — verify lock inheritance or add explicit flock.

3. **Next Sprint (P1)**: Consolidate k9_alarm_consumer JSON writes (ceo_escalations.json, czl_escalations.json, etc.) into single append-only log OR add flock.

4. **Long-term (P2)**: Ship AMENDMENT-016 daemon stateless rewrite to eliminate state-ownership races entirely.

---

## 7. Metadata

**Tool Uses**: 10/14 (under budget)  
**Files Read**: 5 daemon scripts, 1 CIEU db query, 3 shared resource stat checks  
**Git Ops**: 0 (investigation only, per dispatch constraints)  
**Choice Questions**: 0 (per Iron Rule 0)  
**5-Tuple Receipt**: See below  

---

## Appendix A: fcntl.flock Code Pattern

```python
import fcntl
from pathlib import Path

ACTIVE_AGENT_FILE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/.ystar_active_agent")

def safe_write_active_agent(agent_id: str):
    """Write .ystar_active_agent with exclusive lock."""
    ACTIVE_AGENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ACTIVE_AGENT_FILE, "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.write(agent_id)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def safe_read_active_agent() -> str:
    """Read .ystar_active_agent with shared lock."""
    if not ACTIVE_AGENT_FILE.exists():
        return "unknown"
    with open(ACTIVE_AGENT_FILE, "r") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        agent_id = f.read().strip()
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return agent_id
```

---

## Appendix B: Empirical Evidence Links

- Memory entry: `feedback_daemon_cache_workaround` — documents pkill workaround for stale agent_id cache
- Memory entry: `project_active_agent_drift` — documents CEO write permission loss after sub-agent
- CIEU query result: 0 write-error events (no hard corruption detected)
- SQLite pragma output: `wal` + `checkpoint=1000` (WAL mode confirmed live)

---

**End of Report**
