# K9 Routing Chain End-to-End Architecture Specification
**CTO Technical Report — Board 2026-04-16**  
**Author**: Ethan Wright (CTO)  
**Context**: K9 event-trigger #52 has emit-side complete, but routing chain 4 links ≥3 断 — no subscriber, no action handler, no cascade protocol. This spec defines end-to-end design + reference implementation skeleton.

---

## Executive Summary

**Problem**: K9 `k9_event_trigger.py` emits `K9_AUDIT_TRIGGERED` + `K9_VIOLATION_DETECTED` events with `routing_target` metadata, but **no component subscribes** to these events. Routing table maps violation → (target_module, action), but target modules (ForgetGuard, StopHook, CZL, etc.) have **no entry point** for K9-triggered violations. The cascade chain is broken at ≥3 of 4 links.

**Solution**: Define the 4-link routing chain architecture with Pattern B (CIEU event-bus subscriber) as recommended pattern, provide reference implementation skeleton for 1 end-to-end flow, and smoke test verification protocol.

**Deliverables**:
1. 4-link routing chain specification
2. Pattern A/B/C comparison + recommendation
3. Reference implementation skeleton (1 end-to-end example)
4. 6 concrete routing mappings
5. Smoke test verification protocol

---

## 1. The 4-Link K9 Routing Chain

### Link 1: K9 → Routing Decision (EXISTS in #52)

**Status**: ✅ Shipped in `k9_event_trigger.py` (commit pending)

**Mechanism**: K9 event-trigger runs lightweight violation checks, consults `VIOLATION_ROUTING` table, emits CIEU events with routing metadata.

**VIOLATION_ROUTING Table** (excerpt from `k9_event_trigger.py:40-70`):
```python
VIOLATION_ROUTING = {
    "ceo_engineering_boundary": ("forget_guard", "warn"),
    "subagent_unauthorized_git_op": ("stop_hook_inject", "deny"),
    "dispatch_missing_5tuple": ("czl_protocol", "warn"),
    "agent_id_unidentified": ("agent_registry", "warn"),
    "defer_language": ("forget_guard", "warn"),
    "choice_question_to_board": ("forget_guard", "deny"),
    # ... 14 total mappings in current code
}
```

**Output**:
- CIEU event `K9_AUDIT_TRIGGERED` with metadata:
  ```json
  {
    "event_type": "K9_AUDIT_TRIGGERED",
    "agent_id": "ceo",
    "violations_found": 2,
    "violations": ["ceo_engineering_boundary", "defer_language"],
    "routing_targets": ["forget_guard:warn", "forget_guard:warn"]
  }
  ```
- CIEU event `K9_VIOLATION_DETECTED` per violation with `routing_target` and `action` fields.

**Gap**: routing_target is **metadata-only label**. No dispatch mechanism.

---

### Link 2: Routing → Module Invocation (MISSING — This Spec Defines It)

**Problem**: K9 emits routing_target field, but **no component reads it**. Target modules (ForgetGuard, StopHook, CZL, etc.) run independently via their own triggers (PreToolUse hook for ForgetGuard, PostToolUse for others), but have **no K9-specific entry point**.

**Architecture Choice**: Pattern A vs B vs C

#### Pattern A: Direct Callback (Synchronous)
**Mechanism**: K9 imports target module, calls handler function directly in same Python process.

**Implementation**:
```python
# In k9_event_trigger.py
from ystar.governance.forget_guard import handle_k9_violation as fg_handle
from ystar.governance.czl_protocol import handle_k9_violation as czl_handle

ROUTING_HANDLERS = {
    "forget_guard": fg_handle,
    "czl_protocol": czl_handle,
    # ...
}

def k9_audit_on_event(...):
    # ... detect violations ...
    for violation_type in violations:
        target_module, action = VIOLATION_ROUTING[violation_type]
        handler = ROUTING_HANDLERS.get(target_module)
        if handler:
            handler(violation_type, action, payload)
```

**Pros**:
- Instant execution (synchronous)
- Simple logic flow (no event-bus polling)
- Easy to debug (single call stack)

**Cons**:
- Tight coupling (K9 must import all target modules)
- Cross-repo dependency (K9 is in `ystar-company/scripts/`, target modules in `Y-star-gov/ystar/governance/`)
- Import cycles risk (ForgetGuard already imports from K9 helpers)
- Cannot route to external processes (e.g., GUI alerts, Board notifications)

---

#### Pattern B: CIEU Event-Bus Subscriber (Asynchronous) — **RECOMMENDED**
**Mechanism**: Target modules start lightweight daemon/listener that polls CIEU database for `K9_VIOLATION_DETECTED` events filtered by `routing_target` field, then executes handler logic.

**Implementation**:
```python
# In ystar/governance/forget_guard_listener.py (new file)
import time
import sqlite3
from pathlib import Path

CIEU_DB = Path.cwd() / ".ystar_cieu.db"
LAST_SEQ_FILE = Path.cwd() / ".forget_guard_last_seq"

def get_last_processed_seq() -> int:
    if LAST_SEQ_FILE.exists():
        return int(LAST_SEQ_FILE.read_text().strip())
    return 0

def handle_k9_violation(violation_type: str, action: str, payload: dict):
    """ForgetGuard's K9 violation handler"""
    if action == "deny":
        # Emit FORGET_GUARD_DENY event + inject stdout reminder
        emit_cieu("FORGET_GUARD_K9_DENY", {...})
        print(f"[FORGET_GUARD] DENIED: {violation_type}", file=sys.stderr)
    elif action == "warn":
        # Emit FORGET_GUARD_WARN event only
        emit_cieu("FORGET_GUARD_K9_WARN", {...})

def listen_k9_events():
    """Poll CIEU for K9_VIOLATION_DETECTED events targeting forget_guard"""
    last_seq = get_last_processed_seq()
    
    while True:
        conn = sqlite3.connect(str(CIEU_DB))
        cursor = conn.cursor()
        
        # Query new K9_VIOLATION_DETECTED events with routing_target=forget_guard
        cursor.execute("""
            SELECT seq_global, task_description FROM cieu_events
            WHERE event_type = 'K9_VIOLATION_DETECTED'
            AND seq_global > ?
            AND json_extract(task_description, '$.routing_target') = 'forget_guard'
            ORDER BY seq_global ASC
        """, (last_seq,))
        
        for row in cursor.fetchall():
            seq_global, task_desc_json = row
            metadata = json.loads(task_desc_json)
            
            violation_type = metadata['violation_type']
            action = metadata['action']
            
            handle_k9_violation(violation_type, action, metadata)
            
            last_seq = seq_global
            LAST_SEQ_FILE.write_text(str(last_seq))
        
        conn.close()
        time.sleep(0.5)  # Poll interval

if __name__ == "__main__":
    listen_k9_events()
```

**Startup**: Add to `governance_boot.sh`:
```bash
nohup python3 ystar/governance/forget_guard_listener.py &> .forget_guard_listener.log &
echo $! > .forget_guard_listener.pid
```

**Pros**:
- Loose coupling (no cross-repo imports)
- Scales to external processes (can route to GUI, Slack, email)
- CIEU-native (all coordination through audit log)
- Supports async workflows (e.g., Board escalation requiring human response)
- Survives K9 crashes (event persisted in DB)

**Cons**:
- Polling latency (0.5s delay, though can use sqlite triggers for near-instant)
- Requires daemon management (start/stop/health check)
- More moving parts (daemon process + PID file + log rotation)
- State persistence needed (`.forget_guard_last_seq` file)

---

#### Pattern C: Stdout Protocol (Hook Chain Integration)
**Mechanism**: K9 writes structured marker to stdout (e.g., `[K9_ROUTE:forget_guard:warn]`), PostToolUse hook chain reads it, dispatches to target module via subprocess call.

**Implementation**:
```python
# In k9_event_trigger.py
def k9_audit_on_event(...):
    # ... detect violations ...
    for violation_type in violations:
        target_module, action = VIOLATION_ROUTING[violation_type]
        # Write stdout marker
        print(f"[K9_ROUTE:{target_module}:{action}:{violation_type}]", file=sys.stdout)
```

```bash
# In hook_prompt_gate.py (PostToolUse hook)
k9_output=$(python3 scripts/k9_event_trigger.py ...)
if echo "$k9_output" | grep -q '\[K9_ROUTE:'; then
    route_line=$(echo "$k9_output" | grep '\[K9_ROUTE:')
    target=$(echo "$route_line" | cut -d: -f2)
    action=$(echo "$route_line" | cut -d: -f3)
    violation=$(echo "$route_line" | cut -d: -f4)
    
    if [ "$target" = "forget_guard" ]; then
        python3 scripts/forget_guard.py <<< "{\"k9_violation\": \"$violation\", \"action\": \"$action\"}"
    fi
fi
```

**Pros**:
- Works through existing hook plumbing (no new daemon)
- Synchronous execution (same hook call stack)
- Simple state model (no persistence files)

**Cons**:
- Limited bandwidth (stdout protocol fragile for large payloads)
- Hook chain complexity (already 5+ components in PostToolUse chain)
- Parsing fragility (stdout markers can collide with tool output)
- Doesn't scale to external routing (email/Slack/GUI)
- Hard to debug (buried in hook logs)

---

### Pattern Recommendation: **Pattern B (CIEU Event-Bus Subscriber)**

**Rationale**:
1. **Loose Coupling**: K9 and target modules decoupled via CIEU event-bus. No cross-repo imports, no import cycles.
2. **CIEU-Native**: All coordination through audit log = transparent, traceable, survives crashes.
3. **Scalability**: Can route to external processes (Board escalation via MCP, GUI alerts, Slack notifications).
4. **Resilience**: Event persisted before handler runs. Handler crash doesn't lose violation record.
5. **Audit Integrity**: Every step emits CIEU event. Full cascade chain visible in CIEU log (K9 detect → route → handle → confirm).

**Cost**: Requires daemon management (start/stop/health check), polling latency (0.5s default, can optimize with sqlite triggers), state persistence (last_seq file). **Acceptable cost** for a governance framework that values transparency and resilience over tight coupling.

**Fallback**: If daemon management proves fragile in production, downgrade to Pattern A (direct callback) as interim solution. Pattern C (stdout protocol) **not recommended** due to hook chain complexity and parsing fragility.

---

### Link 3: Module Action Handler (MISSING — This Spec Defines It)

**Problem**: Target modules (ForgetGuard, CZL, etc.) have internal logic but **no K9-specific entry point**. Need standardized handler signature + action semantics.

#### Handler Signature (All Target Modules)

```python
def handle_k9_violation(
    violation_type: str,  # e.g., "ceo_engineering_boundary"
    action: str,          # "warn" | "deny" | "escalate"
    payload: dict         # Original event payload (file_path, command, etc.)
) -> dict:
    """
    Handle K9-triggered violation.
    
    Returns:
        {
            "handled": bool,
            "cieu_event": str,  # Event type emitted (e.g., "FORGET_GUARD_K9_WARN")
            "action_taken": str  # Human-readable description
        }
    """
```

#### Target Module Action Matrix

| Target Module | Action | Handler Logic | CIEU Event Emitted | Side Effects |
|---------------|--------|---------------|-------------------|--------------|
| **forget_guard** | warn | Emit CIEU event + stderr warning | `FORGET_GUARD_K9_WARN` | Print recipe to stderr |
| **forget_guard** | deny | Emit CIEU + inject stdout reminder + **block tool call** | `FORGET_GUARD_K9_DENY` | Return deny signal to hook chain |
| **stop_hook_inject** | warn | Emit CIEU event | `STOP_HOOK_K9_WARN` | Log to hook_observe.log |
| **stop_hook_inject** | deny | Emit CIEU + **block Bash execution** | `STOP_HOOK_K9_DENY` | Return deny exit code |
| **czl_protocol** | warn | Emit CIEU + inject CZL reminder to stdout | `CZL_K9_WARN` | Append to next assistant message |
| **agent_registry** | warn | Emit CIEU event | `AGENT_REGISTRY_K9_WARN` | Log to .ystar_active_agent history |
| **agent_registry** | escalate | Emit CIEU + **write Board escalation file** | `AGENT_REGISTRY_K9_ESCALATE` | Write `reports/escalation/{timestamp}.md` |
| **three_dim_audit** | warn | Emit CIEU event | `THREE_DIM_AUDIT_K9_WARN` | Log producer/executor mismatch |
| **hook_health** | warn | Emit CIEU event | `HOOK_HEALTH_K9_WARN` | Log stale hook warning |
| **hook_health** | escalate | Emit CIEU + **kill dead hook daemon** | `HOOK_HEALTH_K9_ESCALATE` | `pkill -9 -f gov-mcp` + restart |

#### Reference Implementation: ForgetGuard Handler

```python
# In ystar/governance/forget_guard.py (add new function)

def handle_k9_violation(violation_type: str, action: str, payload: dict) -> dict:
    """
    Handle K9-triggered violation for ForgetGuard domain.
    
    Called by forget_guard_listener.py when K9_VIOLATION_DETECTED event
    with routing_target=forget_guard is detected in CIEU database.
    """
    from _cieu_helpers import emit_cieu
    import sys
    
    if action == "deny":
        # Deny action: emit CIEU + stderr warning + return deny signal
        emit_cieu(
            event_type="FORGET_GUARD_K9_DENY",
            decision="deny",
            passed=0,
            task_description=f"K9 violation denied: {violation_type}",
            drift_detected=1,
            drift_category="k9_routing",
            evidence_grade="violation"
        )
        
        # Print actionable recipe to stderr (visible to agent)
        print(f"\n{'='*70}", file=sys.stderr)
        print(f"[FORGET_GUARD] K9 VIOLATION DENIED: {violation_type}", file=sys.stderr)
        print(f"{'='*70}", file=sys.stderr)
        print(f"Action blocked. See governance/forget_guard_rules.yaml rule {violation_type}.", file=sys.stderr)
        print(f"{'='*70}\n", file=sys.stderr)
        
        return {
            "handled": True,
            "cieu_event": "FORGET_GUARD_K9_DENY",
            "action_taken": "deny_tool_call"
        }
    
    elif action == "warn":
        # Warn action: emit CIEU event only (non-blocking)
        emit_cieu(
            event_type="FORGET_GUARD_K9_WARN",
            decision="warn",
            passed=1,
            task_description=f"K9 violation warned: {violation_type}",
            drift_detected=1,
            drift_category="k9_routing",
            evidence_grade="warning"
        )
        
        return {
            "handled": True,
            "cieu_event": "FORGET_GUARD_K9_WARN",
            "action_taken": "emit_warning_only"
        }
    
    else:
        # Unknown action — log and fail-open
        print(f"[FORGET_GUARD] Unknown action: {action}", file=sys.stderr)
        return {"handled": False, "cieu_event": None, "action_taken": "unknown_action"}
```

---

### Link 4: Cascade Confirmation Audit (MISSING — This Spec Defines It)

**Problem**: No end-to-end verification that K9 detection → routing → handler → confirmation cascade completed successfully. Need CIEU event chain to prove all 4 links fired.

#### Cascade Flow (5-Step Trace)

**Example**: `subagent_unauthorized_git_op` violation

1. **K9 Detection** (Link 1):
   - K9 runs `check_3d_role_integrity()`, detects sub-agent attempting `git commit`
   - Emits CIEU event `K9_VIOLATION_DETECTED`:
     ```json
     {
       "event_type": "K9_VIOLATION_DETECTED",
       "violation_type": "subagent_unauthorized_git_op",
       "routing_target": "stop_hook_inject",
       "action": "deny",
       "seq_global": 1234
     }
     ```

2. **Routing Decision** (Link 2):
   - ForgetGuard listener polls CIEU DB, finds new event with `routing_target=forget_guard` (wrong target for this example — using `stop_hook_inject`)
   - StopHook listener (hypothetical) reads event, extracts `violation_type` and `action`

3. **Handler Invocation** (Link 3):
   - StopHook listener calls `handle_k9_violation("subagent_unauthorized_git_op", "deny", payload)`
   - Handler logic: emit `STOP_HOOK_K9_DENY` event + **block Bash tool execution**

4. **Action Execution**:
   - Handler emits CIEU event `STOP_HOOK_K9_DENY`:
     ```json
     {
       "event_type": "STOP_HOOK_K9_DENY",
       "violation_type": "subagent_unauthorized_git_op",
       "action_taken": "deny_bash_execution",
       "seq_global": 1235
     }
     ```
   - Handler returns deny signal to hook chain → Bash tool call blocked

5. **Confirmation Audit** (Link 4):
   - Coordinator audit (or smoke test) queries CIEU database:
     ```sql
     SELECT event_type, seq_global, task_description
     FROM cieu_events
     WHERE event_type IN ('K9_VIOLATION_DETECTED', 'STOP_HOOK_K9_DENY')
     ORDER BY seq_global ASC
     ```
   - Expected result: 2 events, seq_global 1234→1235, time delta <1s
   - **Cascade confirmed** if both events present

#### Failure Modes + Fallback

| Step | Failure Mode | Detection | Fallback |
|------|-------------|-----------|----------|
| 1. K9 Detection | K9 crashes, no event emitted | Coordinator audit: no `K9_VIOLATION_DETECTED` event in 1min window after tool call | Retry K9 on next tool call; emit `K9_DETECTION_FAILED` event |
| 2. Routing | Listener daemon dead, event unread | Coordinator audit: `K9_VIOLATION_DETECTED` event exists but no handler event after 5s | Restart listener daemon; emit `K9_ROUTING_TIMEOUT` event |
| 3. Handler Invocation | Handler function crashes | Listener logs exception, emits `K9_HANDLER_CRASHED` event | Fallback to default action (warn-only); escalate to Board |
| 4. Action Execution | Action (e.g., deny) doesn't block tool | Coordinator audit: tool executed despite `DENY` action | Emit `K9_ACTION_INEFFECTIVE` event; escalate to Board |
| 5. Confirmation | CIEU DB write failure | Handler returns success but no CIEU event | Retry CIEU write; if fails 3x, write to `.k9_audit_failures.log` |

---

## 2. Routing Mappings (6 Concrete Examples)

| Violation Type | Routing Target | Action | CIEU Event Emitted | Description |
|----------------|---------------|--------|-------------------|-------------|
| **ceo_engineering_boundary** | `forget_guard` | `warn` | `FORGET_GUARD_K9_WARN` | CEO editing `src/` or `ystar/` files directly (violates AGENTS.md charter) |
| **subagent_unauthorized_git_op** | `stop_hook_inject` | `deny` | `STOP_HOOK_K9_DENY` | Sub-agent attempting `git commit` without CTO authorization |
| **dispatch_missing_5tuple** | `czl_protocol` | `warn` | `CZL_K9_WARN` | CTO dispatch task without Y*/Xt/U/Yt+1/Rt+1 5-tuple |
| **agent_id_unidentified** | `agent_registry` | `warn` | `AGENT_REGISTRY_K9_WARN` | Agent ID not in canonical registry (typo or unauthorized agent) |
| **choice_question_to_board** | `forget_guard` | `deny` | `FORGET_GUARD_K9_DENY` | Agent output contains "请选择 1/2/3" or "Option A/B" (violates Iron Rule 0) |
| **hook_chain_missing** | `hook_health` | `escalate` | `HOOK_HEALTH_K9_ESCALATE` | No `HOOK_PRE_CALL` or `HOOK_POST_CALL` event in 10min window (hook daemon dead) |

---

## 3. Reference Implementation Skeleton

**Goal**: End-to-end example for 1 violation type (`subagent_unauthorized_git_op`) demonstrating all 4 links.

### File 1: `k9_event_trigger.py` (LINK 1 — Already Exists)
See lines 40-70, 256-332 in current implementation. No changes needed.

### File 2: `ystar/governance/stop_hook_listener.py` (LINK 2 — New File)

```python
#!/usr/bin/env python3
"""
StopHook K9 Listener — CIEU Event-Bus Subscriber for stop_hook_inject routing
Polls CIEU database for K9_VIOLATION_DETECTED events targeting stop_hook_inject.
"""
import time
import json
import sqlite3
import sys
from pathlib import Path

CIEU_DB = Path.cwd() / ".ystar_cieu.db"
LAST_SEQ_FILE = Path.cwd() / ".stop_hook_last_seq"

def get_last_processed_seq() -> int:
    if LAST_SEQ_FILE.exists():
        return int(LAST_SEQ_FILE.read_text().strip())
    return 0

def handle_k9_violation(violation_type: str, action: str, payload: dict) -> dict:
    """StopHook's K9 violation handler (LINK 3)"""
    from _cieu_helpers import emit_cieu
    
    if action == "deny":
        # Deny bash execution — emit CIEU event
        emit_cieu(
            event_type="STOP_HOOK_K9_DENY",
            decision="deny",
            passed=0,
            task_description=f"K9 violation denied: {violation_type}",
            drift_detected=1,
            drift_category="k9_routing",
            command=payload.get("command"),
            evidence_grade="violation"
        )
        
        print(f"[STOP_HOOK] DENIED: {violation_type}", file=sys.stderr)
        
        return {"handled": True, "cieu_event": "STOP_HOOK_K9_DENY", "action_taken": "deny_bash"}
    
    elif action == "warn":
        emit_cieu(
            event_type="STOP_HOOK_K9_WARN",
            decision="warn",
            passed=1,
            task_description=f"K9 violation warned: {violation_type}",
            drift_detected=1,
            drift_category="k9_routing",
            evidence_grade="warning"
        )
        
        return {"handled": True, "cieu_event": "STOP_HOOK_K9_WARN", "action_taken": "warn_only"}
    
    return {"handled": False}

def listen_k9_events():
    """Poll CIEU for K9 events targeting stop_hook_inject (LINK 2)"""
    last_seq = get_last_processed_seq()
    
    while True:
        try:
            conn = sqlite3.connect(str(CIEU_DB), timeout=2.0)
            cursor = conn.cursor()
            
            # Query new K9_VIOLATION_DETECTED events with routing_target=stop_hook_inject
            cursor.execute("""
                SELECT seq_global, task_description FROM cieu_events
                WHERE event_type = 'K9_VIOLATION_DETECTED'
                AND seq_global > ?
                AND json_extract(task_description, '$.routing_target') = 'stop_hook_inject'
                ORDER BY seq_global ASC
            """, (last_seq,))
            
            for row in cursor.fetchall():
                seq_global, task_desc_json = row
                metadata = json.loads(task_desc_json)
                
                violation_type = metadata.get('violation_type')
                action = metadata.get('action')
                
                # Invoke handler (LINK 3)
                result = handle_k9_violation(violation_type, action, metadata)
                
                # Update last processed seq
                last_seq = seq_global
                LAST_SEQ_FILE.write_text(str(last_seq))
            
            conn.close()
        except Exception as e:
            print(f"[STOP_HOOK_LISTENER] Error: {e}", file=sys.stderr)
        
        time.sleep(0.5)  # Poll interval

if __name__ == "__main__":
    listen_k9_events()
```

### File 3: `governance_boot.sh` Integration (Daemon Startup)

Add to `governance_boot.sh` after hook daemon start:

```bash
# Start K9 routing listeners
if [ ! -f .stop_hook_listener.pid ]; then
    nohup python3 ystar/governance/stop_hook_listener.py &> .stop_hook_listener.log &
    echo $! > .stop_hook_listener.pid
    echo "[BOOT] StopHook K9 listener started (PID: $(cat .stop_hook_listener.pid))"
fi

if [ ! -f .forget_guard_listener.pid ]; then
    nohup python3 scripts/forget_guard_listener.py &> .forget_guard_listener.log &
    echo $! > .forget_guard_listener.pid
    echo "[BOOT] ForgetGuard K9 listener started (PID: $(cat .forget_guard_listener.pid))"
fi
```

### File 4: Smoke Test (LINK 4 — Cascade Verification)

```python
#!/usr/bin/env python3
"""
K9 Routing Chain Smoke Test
Manufactures a violation, verifies all 4 links fire within 1s.
"""
import sqlite3
import time
from pathlib import Path

CIEU_DB = Path.cwd() / ".ystar_cieu.db"

def get_baseline_seq() -> int:
    """Get current max seq_global before manufacturing violation"""
    conn = sqlite3.connect(str(CIEU_DB))
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(seq_global) FROM cieu_events")
    max_seq = cursor.fetchone()[0] or 0
    conn.close()
    return max_seq

def manufacture_violation():
    """Trigger a subagent_unauthorized_git_op violation"""
    # Write temp file to trigger K9 detection
    # (Actual violation manufacture depends on hook integration)
    print("[SMOKE_TEST] Manufacturing subagent_unauthorized_git_op violation...")
    # Simulate by directly calling k9_audit_on_event
    import sys
    sys.path.insert(0, "scripts")
    from k9_event_trigger import k9_audit_on_event
    
    payload = {
        "tool": "Bash",
        "command": "git commit -m 'test'",
        "file_path": None
    }
    
    k9_audit_on_event("TOOL_USE_BASH", "eng-kernel", payload)
    print("[SMOKE_TEST] Violation emitted to CIEU")

def verify_cascade(baseline_seq: int) -> bool:
    """Verify K9_VIOLATION_DETECTED → STOP_HOOK_K9_DENY cascade"""
    conn = sqlite3.connect(str(CIEU_DB))
    cursor = conn.cursor()
    
    # Wait up to 2s for cascade to complete
    for _ in range(4):
        cursor.execute("""
            SELECT event_type, seq_global FROM cieu_events
            WHERE seq_global > ?
            AND event_type IN ('K9_VIOLATION_DETECTED', 'STOP_HOOK_K9_DENY')
            ORDER BY seq_global ASC
        """, (baseline_seq,))
        
        events = cursor.fetchall()
        
        if len(events) >= 2:
            # Check cascade integrity
            k9_event = next((e for e in events if e[0] == 'K9_VIOLATION_DETECTED'), None)
            handler_event = next((e for e in events if e[0] == 'STOP_HOOK_K9_DENY'), None)
            
            if k9_event and handler_event:
                print(f"[SMOKE_TEST] ✅ CASCADE CONFIRMED:")
                print(f"  - K9_VIOLATION_DETECTED: seq_global={k9_event[1]}")
                print(f"  - STOP_HOOK_K9_DENY: seq_global={handler_event[1]}")
                conn.close()
                return True
        
        time.sleep(0.5)
    
    conn.close()
    print("[SMOKE_TEST] ❌ CASCADE FAILED: Missing handler event after 2s")
    return False

if __name__ == "__main__":
    baseline = get_baseline_seq()
    manufacture_violation()
    success = verify_cascade(baseline)
    exit(0 if success else 1)
```

**Usage**:
```bash
python3 scripts/k9_routing_chain_smoke_test.py
```

**Expected Output**:
```
[SMOKE_TEST] Manufacturing subagent_unauthorized_git_op violation...
[SMOKE_TEST] Violation emitted to CIEU
[SMOKE_TEST] ✅ CASCADE CONFIRMED:
  - K9_VIOLATION_DETECTED: seq_global=1234
  - STOP_HOOK_K9_DENY: seq_global=1235
```

---

## 4. Implementation Roadmap

### Phase 1: Listener Daemon (1 Target Module) — 2 hours
- Create `ystar/governance/stop_hook_listener.py` (Pattern B subscriber)
- Add daemon startup to `governance_boot.sh`
- Test with manufactured `subagent_unauthorized_git_op` violation

### Phase 2: Handler Implementation (All Target Modules) — 4 hours
- Add `handle_k9_violation()` to `forget_guard.py`, `czl_protocol.py`, `coordinator_audit.py`
- Create new handler modules for `agent_registry`, `hook_health`, `three_dim_audit`
- Standardize CIEU event names (`{MODULE}_K9_WARN`, `{MODULE}_K9_DENY`, `{MODULE}_K9_ESCALATE`)

### Phase 3: Smoke Test Suite — 2 hours
- Write smoke test for each routing mapping (6 tests total)
- Verify CIEU cascade integrity (2 events, <1s delta)
- Add to CI/CD pipeline (`pytest tests/test_k9_routing_chain.py`)

### Phase 4: Coordinator Audit Integration — 3 hours
- Modify `coordinator_audit.py` to detect cascade failures (Link 4 monitoring)
- Emit `K9_ROUTING_TIMEOUT` event if handler event missing after 5s
- Add fallback logic (restart listener daemon, escalate to Board)

**Total Estimate**: 11 engineering hours (2 sprint days with Leo Chen + Maya Patel)

---

## 5. Open Questions for Board

1. **Daemon Health Check**: Should coordinator audit monitor listener daemon PIDs and auto-restart on crash, or rely on Board manual intervention?
   
2. **Polling Interval Optimization**: Current 0.5s poll interval acceptable, or invest in sqlite triggers for <100ms latency?

3. **External Routing**: Should we design Link 2 to support external processes (email, Slack, GUI alerts) in v1, or defer to v2?

4. **Cascade Timeout**: 5s timeout for handler response acceptable, or needs tuning based on dogfooding data?

---

## 6. Conclusion

This spec defines the 4-link K9 routing chain end-to-end architecture with **Pattern B (CIEU event-bus subscriber)** as recommended pattern. Reference implementation skeleton demonstrates `subagent_unauthorized_git_op` violation cascade from K9 detection through StopHook denial to CIEU confirmation audit.

**Key Deliverables**:
- ✅ 4-link routing chain specification
- ✅ Pattern A/B/C comparison + Pattern B recommendation
- ✅ Reference implementation skeleton (stop_hook_listener.py + handler + smoke test)
- ✅ 6 concrete routing mappings
- ✅ Smoke test verification protocol

**Next Steps**: CTO assigns implementation to Platform Engineer (Ryan Park) + Governance Engineer (Maya Patel), target ship date 2026-04-18.

---

**Signed**: Ethan Wright, CTO  
**Date**: 2026-04-16  
**CIEU Event**: `CTO_ARCHITECTURE_SPEC_SHIPPED`
