# K9-RT Sentinel Dispatch Plan — Three-Track Parallel Build

**Date**: 2026-04-16  
**CTO**: Ethan Wright  
**Objective**: Ship live governance fuse (L2 defense) with soft warning injection (L3)

---

## Architecture Overview

```
CIEU Event Stream
       ↓
   [Maya's Sentinel] ← consumes Leo's Rt+1 events
       ↓
   .ystar_warning_queue.json
       ↓
   [Ryan's Stop Hook] → injects <system-reminder>
```

---

## Spine Interface Contract (Critical Path)

**Leo emits** → **Maya consumes**:

```python
# CIEU event type (Leo defines, Maya subscribes)
{
  "event_type": "RT_MEASUREMENT",
  "task_id": str,           # UUID or semantic ID linking CIEU events
  "rt_value": float,        # 0.0 = closure, >0 = gap
  "y_star": str,            # ideal contract predicate
  "x_t": str,               # measured pre-state
  "u": list[str],           # actions taken
  "y_t_plus_1": str,        # measured post-state
  "timestamp": ISO8601,
  "agent_id": str,          # from registry
  "role_tags": {            # 3D baseline from commit dedf11d7
    "producer": str,
    "executor": str,
    "governed": str
  }
}
```

**Maya reads** `.ystar_cieu.db` and filters `event_type = "RT_MEASUREMENT"`.  
**Ryan reads** `.ystar_warning_queue.json` (Maya writes) and injects on next `UserPromptSubmit`.

---

## Track 1: Leo-Kernel (Schema + Emit Contract)

**Owner**: Leo Chen (eng-kernel)  
**File**: `.claude/tasks/k9rt_01_schema_leo.md`

**Deliverables**:
1. `ystar/kernel/rt_measurement.py` — Rt+1 calculation + CIEU event emit helper
2. Schema validation in `tests/kernel/test_rt_measurement.py`
3. Stub events in `tests/fixtures/rt_events.json` for Maya's integration tests

**Interface Contract**:
- Exposes `emit_rt_measurement(task_id, y_star, x_t, u, y_t_plus_1, rt_value, role_tags)` callable
- Writes to CIEU DB with `event_type="RT_MEASUREMENT"`
- Schema versioned (v1.0), fields match spine contract above

**Success Criteria (L3 Tested)**:
- ✅ `pytest tests/kernel/test_rt_measurement.py` passes (6+ assertions)
- ✅ Stub events file contains ≥3 sample events (Rt=0, Rt>0, CEO boundary violation case)
- ✅ No modifications outside `ystar/kernel/`, `tests/kernel/`, `tests/fixtures/`

**NOT in Scope**:
- ❌ Auto-emit from existing CIEU helpers (Phase 2)
- ❌ Rt calculation logic (agents self-report for MVP)
- ❌ UI/CLI for manual Rt entry

---

## Track 2: Maya-Governance (Sentinel Engine)

**Owner**: Maya Patel (eng-governance)  
**File**: `.claude/tasks/k9rt_02_sentinel_maya.md`

**Deliverables**:
1. `ystar/governance/k9_rt_sentinel.py` — CIEU stream subscriber, 3D+5-tuple checker
2. Warning queue writer: `.ystar_warning_queue.json` append-only
3. Integration test: `tests/governance/test_k9_rt_sentinel.py` using Leo's stub events

**Interface Contract**:
- **Input**: Leo's `RT_MEASUREMENT` events from CIEU DB
- **Output**: JSON lines appended to `.ystar_warning_queue.json`:
  ```json
  {
    "task_id": "uuid",
    "violation_type": "rt_not_closed" | "3d_role_mismatch",
    "details": "Producer=ceo ∩ Executor=ceo ∩ Write-path ⊃ ./reports/cto/ (CEO engineering boundary)",
    "rt_value": 0.42,
    "timestamp": "2026-04-16T..."
  }
  ```
- **Pilot Rule**: CEO engineering boundary only (Producer=ceo AND Executor=ceo AND write path ⊃ `./reports/cto/` OR `./src/`)

**Success Criteria (L3 Tested)**:
- ✅ `pytest tests/governance/test_k9_rt_sentinel.py` passes (8+ assertions)
- ✅ Detects Rt>0 from stub events, writes warning to queue
- ✅ Detects 3D role violation (CEO writing to `reports/cto/`), writes warning
- ✅ No false positives on clean stub events (Rt=0, role alignment OK)

**NOT in Scope**:
- ❌ Real-time streaming (batch mode OK for MVP)
- ❌ Multi-rule engine (pilot = 1 rule hardcoded)
- ❌ Alert persistence beyond JSON file

---

## Track 3: Ryan-Platform (Hook Injection)

**Owner**: Ryan Park (eng-platform)  
**File**: `.claude/tasks/k9rt_03_hook_ryan.md`

**Deliverables**:
1. Extend `ystar/adapters/hooks/stop_hook.py` — read warning queue on `UserPromptSubmit` event
2. Inject `<system-reminder>` with warnings into prompt
3. Queue drain after injection (append `.processed` timestamp or move to `.ystar_warning_queue_archive.json`)
4. Integration test: `tests/adapters/hooks/test_stop_hook_warnings.py`

**Interface Contract**:
- **Input**: Reads `.ystar_warning_queue.json` (Maya writes)
- **Output**: Injects into Claude Code prompt:
  ```xml
  <system-reminder>
  ⚠️ K9-RT Sentinel detected unresolved gap:
  Task: {task_id}
  Violation: {violation_type}
  Details: {details}
  Rt+1 = {rt_value} (must reach 0.0 for closure)
  </system-reminder>
  ```
- Drains queue after injection (no duplicate warnings)

**Success Criteria (L3 Tested)**:
- ✅ `pytest tests/adapters/hooks/test_stop_hook_warnings.py` passes (5+ assertions)
- ✅ Mock queue file with 2 warnings → hook injects 2 `<system-reminder>` blocks
- ✅ Queue cleared after injection (file empty or archived)
- ✅ No injection if queue is empty (silent pass)

**NOT in Scope**:
- ❌ Warning severity levels (all warnings treated equally)
- ❌ User-facing UI (terminal only)
- ❌ Integration with external alerting (Slack/email)

---

## Assembly Step (CEO Collapses 3 Outputs)

**After all 3 tracks report L3 Tested**:

1. CEO runs E2E integration test:
   - Spawn sub-agent with deliberate CEO boundary violation (write to `./src/ystar/kernel/` as `agent_id=ceo`)
   - Sub-agent emits `RT_MEASUREMENT` with Rt>0
   - Maya's Sentinel detects, writes warning queue
   - Next UserPromptSubmit → Ryan's hook injects `<system-reminder>`
   - Verify Claude Code session sees warning in system context

2. CEO documents E2E flow in `reports/autonomous/k9_rt_fuse_e2e_test.md`

3. If E2E passes → CEO commits all 3 tracks + E2E test, bumps version to v0.43-alpha

4. If E2E fails → CEO identifies failing interface, returns to owner for fix (no re-dispatch, same task card, iterate)

---

## Scope Guards (What NOT to Build)

### All Tracks
- ❌ No auto-remediation (warnings only, no blocking)
- ❌ No multi-agent coordination beyond CIEU event schema
- ❌ No UI beyond terminal/log output
- ❌ No external dependencies (stay within ystar-gov repo)

### Pilot Constraints
- ✅ **One rule only**: CEO engineering boundary (Producer=CEO ∩ Executor=CEO ∩ Write-path ⊃ restricted dirs)
- ✅ Soft enforcement only (warnings, not hard deny like ForgetGuard)
- ✅ Session-local only (no cross-session memory required for MVP)

---

## Convergence Estimate (Tool-Use Budget)

| Track | Engineer | Est. Tool Uses | Blocking? |
|-------|----------|----------------|-----------|
| T1 Leo | Kernel | 12-18 | **SPINE** (blocks T2) |
| T2 Maya | Governance | 20-30 | Blocks T3 E2E only |
| T3 Ryan | Platform | 10-15 | Parallel with T2 |
| CEO Assembly | CEO | 8-12 | After all 3 L3 |

**Critical Path**: Leo schema → Maya sentinel → CEO E2E (Ryan can finish anytime before E2E)

**Same-Session Target**: Yes, if all 3 engineers spawn in parallel after Leo's schema lands (est. 50-75 total tool uses)

---

## Risk Mitigation

1. **Schema drift**: Leo must version schema in docstring + emit `schema_version` field
2. **Queue corruption**: Ryan must validate JSON parse before injection (fail-safe: skip corrupt entries, log error)
3. **CIEU DB lock contention**: Maya reads in batch mode (not real-time), acceptable for MVP
4. **False positives**: Pilot rule hardcoded with explicit path allow-list (CEO can tweak without Maya rebuild)

---

**CTO Sign-Off**: Ethan Wright  
**Next Step**: CEO spawns Leo → await schema → spawn Maya+Ryan in parallel

---

## Appendix A — Task Card 1: Leo-Kernel (Rt+1 Measurement Schema)

**Engineer**: Leo Chen (eng-kernel)  
**Goal**: Define and implement Rt+1 measurement CIEU event schema + emit contract for K9-RT Sentinel integration

**Files in Scope**:
- `ystar/kernel/rt_measurement.py` (new)
- `tests/kernel/test_rt_measurement.py` (new)
- `tests/fixtures/rt_events.json` (new)

**Interface Contract with Maya & Ryan**:
Leo's output is the **spine** — Maya and Ryan depend on this schema.

**Emit Contract**:
```python
def emit_rt_measurement(
    task_id: str,           # UUID or semantic ID linking CIEU events
    y_star: str,            # ideal contract predicate
    x_t: str,               # measured pre-state
    u: list[str],           # actions taken
    y_t_plus_1: str,        # measured post-state
    rt_value: float,        # 0.0 = closure, >0 = gap
    role_tags: dict,        # {"producer": str, "executor": str, "governed": str}
    agent_id: str = None    # auto-detect from .ystar_active_agent if None
) -> None:
    """
    Write RT_MEASUREMENT event to CIEU DB.
    Schema version: 1.0
    """
```

**CIEU Event Schema (v1.0)**:
```json
{
  "event_type": "RT_MEASUREMENT",
  "schema_version": "1.0",
  "task_id": "str",
  "rt_value": 0.0,
  "y_star": "str",
  "x_t": "str",
  "u": ["action1", "action2"],
  "y_t_plus_1": "str",
  "timestamp": "ISO8601",
  "agent_id": "str",
  "role_tags": {
    "producer": "ceo",
    "executor": "ceo",
    "governed": "ceo"
  }
}
```

**Stub Events for Maya's Tests** (write to `tests/fixtures/rt_events.json`):
Must include ≥3 samples:
1. **Clean closure**: Rt=0.0, role alignment OK
2. **Open gap**: Rt>0, task not closed
3. **CEO boundary violation**: Producer=ceo, Executor=ceo, task touches `./reports/cto/` or `./src/ystar/` (pilot rule trigger case)

**Success Criteria (L3 Tested)**:
- ✅ `pytest tests/kernel/test_rt_measurement.py` passes (6+ assertions covering schema validation, CIEU DB write, field types)
- ✅ Stub events file exists with ≥3 valid sample events
- ✅ No modifications outside `ystar/kernel/`, `tests/kernel/`, `tests/fixtures/`
- ✅ Schema version field present in all emitted events
- ✅ `emit_rt_measurement()` callable from external modules (Maya can import)

**Explicit Out-of-Scope**:
- ❌ Auto-emit from existing CIEU helpers (Phase 2 work)
- ❌ Rt calculation logic (agents self-report rt_value for MVP)
- ❌ UI/CLI for manual Rt entry
- ❌ Real-time streaming (batch read OK for Maya)
- ❌ Multi-version schema support (v1.0 only for pilot)

**L-Tag Targets**: L3 Tested (E2E integration is CEO's assembly step, not Leo's responsibility)

---

## Appendix B — Task Card 2: Maya-Governance (K9-RT Sentinel Engine)

**Engineer**: Maya Patel (eng-governance)  
**Goal**: Build CIEU stream subscriber that detects Rt+1 closure gaps and 3D role violations, writes warnings to queue for Ryan's hook injector

**Files in Scope**:
- `ystar/governance/k9_rt_sentinel.py` (new)
- `tests/governance/test_k9_rt_sentinel.py` (new)
- `.ystar_warning_queue.json` (sentinel writes here, gitignored)

**Interface Contract with Leo**:
- **Input**: Reads Leo's `RT_MEASUREMENT` events from `.ystar_cieu.db` (filter `event_type="RT_MEASUREMENT"`)
- **Schema**: Leo's v1.0 schema (5-tuple fields + role_tags)

**Interface Contract with Ryan**:
- **Output**: Append-only JSON lines to `.ystar_warning_queue.json`:
```json
{
  "task_id": "uuid",
  "violation_type": "rt_not_closed" | "3d_role_mismatch",
  "details": "str (human-readable violation description)",
  "rt_value": 0.42,
  "timestamp": "ISO8601",
  "agent_id": "str",
  "role_tags": {"producer": "str", "executor": "str", "governed": "str"}
}
```

**Pilot Rule (Hardcoded for MVP)**:
Trigger warning if **ALL** conditions met:
1. `role_tags.producer == "ceo"` AND `role_tags.executor == "ceo"`
2. Task involves write operations to restricted paths: `./reports/cto/`, `./reports/eng-*/`, `./src/ystar/`, `./tests/` (CEO engineering boundary violation)
3. OR: `rt_value > 0` for any task (closure gap)

**Dual Detection Axes**:
1. **3D Role Baseline** (reuse commit dedf11d7 Producer/Executor/Governed taxonomy)
2. **5-Tuple Closure** (per-task_id sliding window, trigger if Rt+1 > 0)

**Success Criteria (L3 Tested)**:
- ✅ `pytest tests/governance/test_k9_rt_sentinel.py` passes (8+ assertions)
- ✅ Detects Rt>0 from Leo's stub events, writes warning to queue with correct fields
- ✅ Detects 3D role violation (CEO writing engineering files), writes `violation_type="3d_role_mismatch"`
- ✅ No false positives on clean stub events (Rt=0, role alignment OK)
- ✅ Queue file appends correctly (no overwrites, valid JSON-lines format)
- ✅ Handles corrupt CIEU DB gracefully (logs error, does not crash)

**Explicit Out-of-Scope**:
- ❌ Real-time streaming (batch mode OK, poll interval ≥5s acceptable)
- ❌ Multi-rule engine (pilot = 1 hardcoded rule, no config file)
- ❌ Alert persistence beyond JSON file (no DB writes for warnings)
- ❌ Warning deduplication (same violation repeated = multiple warnings OK for MVP)
- ❌ Severity levels (all warnings treated equally)

**L-Tag Targets**: L3 Tested (Ryan's hook integration is separate track)

---

## Appendix C — Task Card 3: Ryan-Platform (Stop/UserPromptSubmit Hook Warning Injector)

**Engineer**: Ryan Park (eng-platform)  
**Goal**: Extend Y*gov Stop hook to inject K9-RT warnings into Claude Code session context on next user prompt

**Files in Scope**:
- `ystar/adapters/hooks/stop_hook.py` (modify existing)
- `tests/adapters/hooks/test_stop_hook_warnings.py` (new)
- `.ystar_warning_queue.json` (read-only for this track)
- `.ystar_warning_queue_archive.json` (write processed warnings here)

**Interface Contract with Maya**:
- **Input**: Reads `.ystar_warning_queue.json` (Maya writes)
- **Schema**: Maya's warning queue format (task_id, violation_type, details, rt_value, timestamp, agent_id, role_tags)

**Hook Behavior**:
On `UserPromptSubmit` event (same trigger as current Stop hook):
1. Read `.ystar_warning_queue.json`
2. For each warning entry:
   ```xml
   <system-reminder>
   ⚠️ K9-RT Sentinel detected unresolved gap:
   Task: {task_id}
   Violation: {violation_type}
   Details: {details}
   Rt+1 = {rt_value} (must reach 0.0 for closure)
   Agent: {agent_id} (Producer={role_tags.producer}, Executor={role_tags.executor})
   </system-reminder>
   ```
3. Append processed entries to `.ystar_warning_queue_archive.json` with `processed_at` timestamp
4. Clear `.ystar_warning_queue.json` (truncate to empty)

**Failure Modes**:
- Queue file missing → silent pass (no warnings to inject)
- Queue file corrupt JSON → log error to `hook_observe.log`, skip injection, do NOT crash session
- Archive write fails → log warning, continue (warnings re-injected next prompt OK for MVP)

**Success Criteria (L3 Tested)**:
- ✅ `pytest tests/adapters/hooks/test_stop_hook_warnings.py` passes (5+ assertions)
- ✅ Mock queue file with 2 warnings → hook injects 2 `<system-reminder>` blocks in correct XML format
- ✅ Queue cleared after successful injection (file empty or deleted)
- ✅ Archive file contains processed warnings with `processed_at` timestamp
- ✅ No injection if queue is empty (silent pass, no log noise)
- ✅ Corrupt JSON in queue → logs error, does not crash hook execution

**Explicit Out-of-Scope**:
- ❌ Warning severity levels (all warnings injected equally)
- ❌ User-facing UI beyond terminal (no GUI, no web dashboard)
- ❌ Integration with external alerting (Slack/email/PagerDuty)
- ❌ Warning aggregation/deduplication (inject all warnings as-is)
- ❌ Configurable injection format (hardcoded XML template OK for MVP)

**L-Tag Targets**: L3 Tested (CEO E2E assembly will verify injection appears in Claude Code session context)
