# Circuit Breaker Violation Analysis — 2026-04-13

**Diagnostic Type**: Dump-only (no fixes applied)

## Summary

- **Circuit Breaker Status**: ARMED (1755 violations reported at boot)
- **Threshold**: 50 violations in 10-minute sliding window
- **Latest ARM Event**: seq_global 1776097360553584 (timestamp 1776097360.55358)

## Findings

### 1. Circuit Breaker Trigger Analysis

**Actual violation count in 10-minute window before ARM**: 31 omission violations + 3 behavior rule violations = **34 total**

This is **below the 50-violation threshold** configured in InterventionEngine.

**Discrepancy**: Boot message reports "1755 violations" but:
- The circuit breaker threshold is 50 (hardcoded in `intervention_engine.py` line 50)
- Only 34 violations were recorded in the 10-minute window before ARM
- The 1755 number appears to be a **cumulative counter** that persisted across sessions

### 2. Top-3 Noisy Rules (in latest ARM window)

| Rule Type | Count | Verdict |
|-----------|-------|---------|
| `omission_violation:intent_declaration` | 10 | **True violations** — agents not declaring intent before major actions |
| `omission_violation:required_acknowledgement_omission` | 9 | **True violations** — agents not acknowledging received directives |
| `omission_violation:directive_acknowledgement` | 9 | **True violations** — agents not acknowledging Board directives |

**All three are genuine governance failures**, not false positives.

### 3. Root Cause: Cumulative Counter Persistence Bug

The circuit breaker counter (`_circuit_breaker_violation_count`) appears to be:
- **Accumulating across sessions** instead of resetting
- Not properly using the sliding window mechanism (lines 74-81 in intervention_engine.py implement the window, but the counter may be loaded from persistent state)

**Evidence**:
- Boot script reports 1755 violations (cumulative)
- Actual window-based count is only 34
- Circuit breaker armed despite being below threshold

### 4. CIEU Enforcement Events: Zero Records

```sql
SELECT COUNT(*) FROM cieu_events WHERE event_type = 'enforcement' AND passed = 0;
-- Result: 0
```

**No `enforcement` event type exists** in the CIEU database. All governance events use specific types like:
- `omission_violation:*` (448-447 events per type)
- `intervention_pulse:*` (203-112 events)
- `intervention_gate:deny` (99 events)
- `BEHAVIOR_RULE_VIOLATION` (210 events)

The original query assumption (looking for `enforcement` table or `action='DENY'`) was incorrect.

## CIEU Database Status

- **Total events**: 18,004
- **Event types**: 72 distinct types
- **No `enforcement_events` table** (events stored in unified `cieu_events` table)
- **Top event types**:
  - `external_observation`: 4,321
  - `cmd_exec`: 1,874
  - `file_read`: 1,463
  - `OFF_TARGET_WARNING`: 976
  - `KNOWLEDGE_IMPORT`: 971

## Recommendations (not implemented in this dump)

1. **P0**: Reset circuit breaker counter on session boot (currently persists indefinitely)
2. **P1**: Add `gov_reset_breaker` call to `governance_boot.sh` to clear stale counts
3. **P2**: Add circuit breaker metrics to `gov_doctor` L1.10 heartbeat check
4. **P3**: Investigate why intent_declaration/acknowledgement violations are so frequent (agents not following obligation protocols)

---

**Next Steps**: Board to decide whether to:
- Reset breaker now (`gov_reset_breaker` tool)
- Fix counter persistence bug (requires Leo/Maya code change)
- Accept current state and monitor next window
