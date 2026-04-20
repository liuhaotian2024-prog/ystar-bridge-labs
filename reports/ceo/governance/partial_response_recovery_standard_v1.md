# Sub-Agent Partial-Response Recovery — Standard Operating Procedure v1

**Audience**: future CEO sessions (I) + future CTO/engineers / Board + consultants auditing resilience patterns.
**Research basis**: 2026-04-19 evening incident — 4 parallel sub-agent spawns during break-glass window all hit `stream idle timeout - partial response`. 1 of 4 (Maya `dominance_monitor.py`) had file on disk (14KB) before stream kill; 3 of 4 (Leo/Ryan/Samantha) had no artifact. Consultant diagnosed root cause as parent-session context accumulation at 9+ hour mark → slow stream I/O scheduling → sub-agent appears idle to watchdog → kill. Consultant recommended standardizing recovery path (CEO did ad-hoc for Maya; consultant said "make it into action model v2").
**Synthesis**: stream-idle-timeout is a separate failure mode from logic errors. It leaves zero-to-partial artifacts on disk with no receipt. A standardized recovery workflow closes this resilience gap without wasted re-spawn (which would overwrite the partial landed work).
**Purpose**: codify 6-step recovery procedure so next session handles timeouts deterministically. Also includes three forward-looking guardrails: age-aware parallelism caps, tool-use scoping rules, and preemptive watchdog tightening.

**Author**: Aiden Liu (CEO)
**Date**: 2026-04-19
**Status**: [L1] STANDARD — proposed for action model v2 inclusion; Ethan-CTO ruling welcome
**Authority**: Board directive 2026-04-19 via consultant recommendation "make partial-response recovery standard"

---

## 1. The Failure Mode

**Definition**: sub-agent stream terminates with `stream idle timeout - partial response` or watchdog `no progress N seconds` before the sub-agent completes its final deliverable write OR its receipt write.

**Signature symptoms**:
- Parent task-notification payload contains `API Error: Stream idle timeout - partial response received` OR `Agent stalled: no progress for Ns (stream watchdog did not recover)`
- `tool_uses` count is non-zero but below the agent's estimated budget (partial execution)
- `duration_ms` is meaningful (not a trivial crash)
- No final assistant message from sub-agent (stream cut mid-reply)
- Artifact file(s) may or may not exist on disk depending on WHERE in the sub-agent's execution timeline the kill occurred

**Distinction from other failure modes**:
- NOT a rate-limit (those return explicit 429)
- NOT a logic error (those come back with full receipt explaining blockage)
- NOT a hook deny (those surface as explicit CROBA/ForgetGuard events)
- IS a resource/timing failure at the parent-session I/O layer

## 2. Recovery Workflow (6 steps)

### Step 1: Triage — did anything land?

```bash
# For each deliverable file path the agent prompt specified:
ls -la <deliverable_path> 2>&1
# Also check likely fallback paths if agent has scope limitations:
ls -la docs/receipts/ reports/receipts/ scripts/ 2>&1
```

Also query CIEU for any intermediate events from that sub-agent:
```sql
SELECT event_type, datetime(created_at,'unixepoch') 
FROM cieu_events 
WHERE agent_id LIKE '%<sub-agent name>%' 
  AND created_at > <spawn_timestamp>
ORDER BY created_at;
```

### Step 2: Quality-gate the landed artifact

If file(s) landed:
- Read first 100 lines: look for expected structure (imports, class defs, constants, docstring)
- Count lines: too short = partial; expected size = likely complete
- Grep for cite markers indicating the agent honored the prompt (e.g., CTO ruling references, CEO spec citations)

If nothing landed:
- Proceed to Step 6 (re-spawn with smaller scope). Skip to it.

### Step 3: Compose CEO-scope receipt on agent's behalf

CEO writes to `reports/receipts/<CZL-ID>.md` with explicit header note:

```
**Authors**: <agent role> (code) · Aiden Liu (receipt composer; <agent>'s stream was killed pre-receipt)
**Date**: <YYYY-MM-DD>
**Status**: [L3] MODULE SHIPPED (code verified); regression tests pending <agent>'s next session
```

5-tuple structure:
- Y*: what the module accomplishes at code level
- Xt: state before (no module existed)
- U: landed files + CEO verification method + which lines were read
- Yt+1: next-session remaining work (tests, integration)
- Rt+1: honest partial count (>0 if tests/integration missing)

### Step 4: Emit CIEU recovery event

```python
emit_cieu("SUB_AGENT_PARTIAL_RECOVERY", {
    "original_agent": "<sub-agent name>",
    "delivered_artifact": "<file path>",
    "recovery_composer": "ceo",
    "missing_components": ["tests", "receipt", "integration-wire"],
    "original_spawn_timestamp": <unix>,
    "recovery_timestamp": <unix>,
    "root_cause_hypothesis": "stream-idle-timeout / parent context accumulation"
})
```

### Step 5: Update whiteboard card

Use `dispatch_board.py complete` with the CEO-composed receipt. Add a `partial_recovery_note` field if the schema supports it, else prefix the completion_receipt content with `[CEO-COMPOSED RECOVERY RECEIPT]`.

### Step 6: Re-spawn policy for MISSING work

NEVER re-spawn the full original task. That would overwrite landed partial work + waste tokens.

DO re-spawn the GAP (tests, integration, receipt refinement) as a smaller CZL. Target ≤8 tool_uses. Gate via newfound knowledge of parent-context age.

## 3. Preventive Guardrails

### 3.1 Age-aware parallelism cap

```
session_age < 2h:  ≤6 concurrent sub-agents, each ≤20 tool_uses
session_age 2-6h:  ≤4 concurrent, each ≤15 tool_uses
session_age 6h+:   ≤2 concurrent, each ≤10 tool_uses
session_age 9h+:   serial only (1 at a time), each ≤8 tool_uses
```

Rationale: parent context accumulates over session; I/O scheduling slows; concurrent stream bandwidth drops. The numbers are empirical from 2026-04-19 (morning 10+ concurrent worked; evening 4 concurrent failed 4-of-4 at 9+h).

### 3.2 Tool-use scoping rule

Before every spawn, explicit check:
- Single atomic deliverable?
- Estimated tool_uses < (30 − session_age_hours × 2)? (e.g., at 6h session → budget ≤18)
- Prompt context size < 10KB?

If any NO → split the task into smaller CZLs.

### 3.3 Preemptive watchdog tightening

- Current watchdog: 600s "no progress" triggers kill
- Proposed: 300s for session_age > 6h (fail fast, respawn with smaller scope)
- Implementation: CZL-WATCHDOG-AGE-AWARE (eng-platform scope) — Ryan future card

## 4. Integration with Action Model v2

Add new failure-mode row to action model v2:

| Failure Mode | Detection | Recovery | Preventive |
|---|---|---|---|
| Stream idle timeout | task_notification with `stream idle timeout - partial response` substring | This SOP steps 1-6 | Age-aware parallelism + tool-use scoping |

Corresponding change to WORKING_STYLE.md or equivalent — add §recovery.partial_response pointing to this doc.

## 5. Empirical Record (2026-04-19 evening)

| Sub-Agent | File Delivered? | tool_uses Before Kill | Recovery Action |
|---|---|---|---|
| Maya-Governance (dominance_monitor) | ✓ 14186 bytes | 18 | CEO receipt composed `reports/receipts/CZL-DOMINANCE-MONITOR.md` |
| Leo-Kernel (outcome_weighted_hebbian) | ✗ none | 21 | Re-spawn with ≤8 tool_uses after session_age decreases |
| Ryan-Platform (L2 hook wire) | ✗ none | 18 | Re-spawn with ≤8 tool_uses after session_age decreases |
| Samantha-Secretary (clock-out whitelist) | ✗ none | 43 | Re-spawn with ≤8 tool_uses after session_age decreases |

Parent session age at spawn: ~9.2h. Parent context size: unverified but likely >50KB accumulated.

## 6. Success Criteria

- Next time a sub-agent hits stream-idle-timeout, this SOP is followed step-by-step without ad-hoc decisions
- Partial-landed artifacts never re-spawned (avoided overwrite)
- CIEU emits `SUB_AGENT_PARTIAL_RECOVERY` event in recovery cases
- Age-aware parallelism caps referenced explicitly in CEO self-check (3-question self-check extended to 4)

## 7. Open Questions (for Ethan architectural review)

1. Should stream-idle-timeout produce a CIEU event from the parent side (detector in hook_wrapper.py) for better visibility?
2. Is the age-aware cap table calibrated correctly? Need data points from sessions beyond 9.2h to confirm slope.
3. Should action model v2 include automatic re-spawn of failed sub-agents (with smaller scope), or always require CEO decision?
4. Does `engineer_task_subscriber.py` need equivalent resilience for its (future) spawn path?
