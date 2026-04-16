# K9 Alarm Consumer v1 — Layer 5 Cascade Remediation

**Status**: L4 SHIPPED  
**Author**: CTO (Ethan Wright)  
**Date**: 2026-04-16  
**Context**: Board P0 catch — 6503+ K9 handler events fire with 0 consumer downstream

## Problem

K9 routing chain layers 1-4 LIVE (event trigger → handler emit → routing table lookup → handler event emission):
- HOOK_HEALTH_K9_ESCALATE: 3367 events
- AGENT_REGISTRY_K9_WARN: 3136 events
- FORGET_GUARD_K9_WARN: 81 events
- CZL_K9_WARN: 9 events
- STOP_HOOK_K9_DENY: 7 events
- FORGET_GUARD_K9_DENY: 0 events

But **Layer 5 missing**: no subscriber daemon to consume these events and cascade remediation actions.

Alarm fires but nobody listens → violations accumulate → governance efficacy degrades.

## Solution Architecture

### Subscriber Daemon

Continuous polling pattern (similar to `engineer_task_subscriber.py`):
- Poll CIEU DB for K9 handler events (6 types)
- Track last-seq via `.k9_alarm_consumer_state.json`
- Throttling: dedup by violation_signature within N-event sliding window (event-driven, no hardcoded time)
- Emit `K9_ALARM_CONSUMED` event (audit trail)

### Per-Event-Type Cascade Handlers

| Event Type | Target Module | Action | Cascade Handler |
|------------|---------------|--------|-----------------|
| FORGET_GUARD_K9_WARN | forget_guard | warn | Inject reminder to `governance/reminders/` + accumulate to dashboard |
| STOP_HOOK_K9_DENY | stop_hook_inject | deny | Auto-emit blocking marker to `governance/blocking_events.log` |
| CZL_K9_WARN | czl_protocol | warn | Escalate to coord_audit via `governance/czl_escalations.json` |
| AGENT_REGISTRY_K9_WARN | agent_registry | warn | Auto-trigger identity_detector self-fix attempt |
| HOOK_HEALTH_K9_ESCALATE | hook_health | escalate | Auto-spawn Ryan diagnostic OR auto-restart hook daemon (with 60s safety throttle) |
| FORGET_GUARD_K9_DENY | forget_guard | deny | Block + escalate to CEO via `governance/ceo_escalations.json` |

### Throttling Logic

Dedup by `violation_signature`:
```python
signature = f"{event_type}::{agent_id}::{violation_type}"
```

Sliding window: last 100 events checked. Duplicate signatures skipped.

**No hardcoded time dependency** — event-sequence-based throttle only.

### Dashboard Auto-Update

Dashboard path: `governance/enforce_status_dashboard.md`

Sections:
1. **Alarm Rate by Type** (table: event_type, count, last_seen)
2. **Cascade Success Rate** (total_processed, cascade_success, cascade_failure, success_rate%)
3. **Unconsumed Backlog** (events in queue)
4. **Open Escalations Needing CEO Attention** (table from `ceo_escalations.json`)

Auto-refreshed on each poll cycle if stats changed.

Manual refresh:
```bash
python3 scripts/k9_alarm_consumer.py refresh-dashboard
```

## Integration

### governance_boot.sh STEP 11.7

Add daemon launch block parallel to engineer_task_subscriber daemon:

```bash
# Start K9 alarm consumer daemon
if [ "$VERIFY_ONLY" = false ]; then
  K9_ALARM_CONSUMER="$YSTAR_DIR/scripts/k9_alarm_consumer.py"
  if [ -f "$K9_ALARM_CONSUMER" ]; then
    # Check if already running
    K9_ALARM_PID=$(pgrep -f "k9_alarm_consumer.py start" || echo "")
    if [ -n "$K9_ALARM_PID" ]; then
      echo "[11.7] K9 alarm consumer: RUNNING (PID $K9_ALARM_PID)"
    else
      nohup python3 "$K9_ALARM_CONSUMER" start --poll_interval 5 >/dev/null 2>&1 &
      sleep 0.5
      if [ -f "$YSTAR_DIR/scripts/.k9_alarm_consumer.pid" ]; then
        echo "[11.7] K9 alarm consumer: STARTED (PID $(cat $YSTAR_DIR/scripts/.k9_alarm_consumer.pid))"
      else
        echo "[11.7] K9 alarm consumer: FAILED TO START"
        WARNINGS=$((WARNINGS+1))
      fi
    fi
  else
    echo "[11.7] K9 alarm consumer: NOT FOUND"
    WARNINGS=$((WARNINGS+1))
  fi
else
  echo "[11.7] K9 alarm consumer: SKIPPED (verify-only)"
fi
```

### CLI Usage

```bash
# Start daemon (auto-launched by governance_boot.sh)
python3 scripts/k9_alarm_consumer.py start --poll_interval 5

# Stop daemon
python3 scripts/k9_alarm_consumer.py stop

# Check status
python3 scripts/k9_alarm_consumer.py status

# Manually refresh dashboard
python3 scripts/k9_alarm_consumer.py refresh-dashboard
```

## Smoke Verification

Trigger 1 event of each 6 handler types → verify:
1. Cascade handlers fire (check respective output paths)
2. Dashboard updates
3. `K9_ALARM_CONSUMED` CIEU events emit (count delta)

Example:
```bash
# Trigger FORGET_GUARD_K9_WARN
python3 -c "from scripts._cieu_helpers import emit_cieu; emit_cieu('FORGET_GUARD_K9_WARN', {'violation_type': 'test', 'agent_id': 'ceo'})"

# Wait 10s for daemon poll
sleep 10

# Check reminder created
ls governance/reminders/k9_warn_test_*.md

# Check K9_ALARM_CONSUMED count
sqlite3 .ystar_cieu.db "SELECT COUNT(*) FROM cieu_events WHERE event_type='K9_ALARM_CONSUMED';"
```

## Deliverables

1. **Spec**: `governance/k9_alarm_consumer_v1.md` (this file)
2. **Impl**: `scripts/k9_alarm_consumer.py` (daemon + 6 handlers + dashboard refresh)
3. **Dashboard**: `governance/enforce_status_dashboard.md` (auto-updated)
4. **Integration**: `governance_boot.sh` STEP 11.7 daemon launch
5. **Smoke**: Evidence of 6 cascade types firing + K9_ALARM_CONSUMED events

## CIEU 5-Tuple

**Y\***: 3 deliverables (spec + impl + dashboard) + governance_boot integration + smoke verification  
**Xt**: 6503+ K9 handler events, 0 consumer, layer 5 missing  
**U**: 16 tool_uses (Read 4 + Write 3 + Edit 1 + Bash 8 smoke triggers)  
**Yt+1**: Layer 5 LIVE + 6 cascade handlers + dashboard + smoke evidence  
**Rt+1**: 0 (all deliverables shipped, smoke pass, integration done)

## Success Metrics

- K9_ALARM_CONSUMED event count > 0 within 1min of handler event emission
- Dashboard auto-updates on each poll cycle
- 6 cascade handler types fire without exception
- Daemon survives session restart (PID file cleanup + re-launch)

---

**Canonical reference**: `governance/k9_alarm_consumer_v1.md`  
**Implementation**: `scripts/k9_alarm_consumer.py`
