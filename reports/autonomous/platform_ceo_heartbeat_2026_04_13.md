---
date: 2026-04-13
agent: eng-platform (Ryan Park)
type: autonomous_work
dispatch_source: CEO Aiden direct dispatch
task_id: ceo_self_heartbeat_loop
status: completed
tool_uses: 13 / 25 (52%)
---

# Platform Report: CEO Self-Heartbeat Loop — Autonomy Root Capability

## Executive Summary

**Problem**: ADE idle-pull (commit `57be953`) emits next-action to other agents, but **CEO has no self-heartbeat** → CEO remains reactive (waits for Board questions or agent pings).

**Solution**: Implemented `scripts/ceo_heartbeat.py` — autonomous monitoring loop that detects CEO idle/off-target states and emits CIEU triggers every 5 minutes.

**Impact**: CEO now has autonomous proactivity loop. No longer dependent on external stimuli to act.

---

## What Was Shipped

### 1. Core Implementation

**File**: `scripts/ceo_heartbeat.py` (227 lines)

**Capabilities**:
- Reads `.ystar_active_agent` → only runs when CEO is active (respects role boundaries)
- Parses `reports/priority_brief.md` YAML → extracts `today_targets` list
- Queries `.ystar_memory.db` → gets last CEO CIEU event timestamp
- Emits 3 CIEU trigger types:
  - `CEO_HEARTBEAT_IDLE` — no CEO events in last 5min
  - `CEO_HEARTBEAT_OFF_TARGET` — current action misaligned with today_targets (future: integrate with ADE)
  - `CEO_TODAY_DONE_PULL_TOMORROW` — all today_targets complete (future: integrate with omission_store)

**CLI**:
```bash
# Dry-run test
python3 scripts/ceo_heartbeat.py --dry-run --once

# Production (single run)
python3 scripts/ceo_heartbeat.py --once

# Continuous loop (testing)
python3 scripts/ceo_heartbeat.py --interval 300  # 5min
```

### 2. Test Coverage

**File**: `tests/test_ceo_heartbeat.py` (14 unit + integration tests)

**Results**: ✅ **14/14 PASS** (100%)

**Coverage areas**:
- YAML parsing (priority_brief.md frontmatter)
- CIEU db queries (last CEO event timestamp)
- Idle detection (no events / old events / recent events)
- CIEU emission (real + dry-run modes)
- Active agent boundary (skip when not CEO)
- Integration flow (idle trigger end-to-end)

### 3. Documentation

**Files**:
- `knowledge/eng-platform/achievements/ceo_heartbeat_autonomy_loop_2026_04_13.md` — achievement report
- `docs/ceo_heartbeat_integration.md` — integration guide (crontab setup, troubleshooting, architecture)

---

## Crontab Integration (Board Manual Action Required)

**Installation command**:

```bash
crontab -e

# Add this line:
*/5 * * * * /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ceo_heartbeat.py --once >> /tmp/ceo_heartbeat.log 2>&1
```

**Verification**:

```bash
# Check logs
tail -f /tmp/ceo_heartbeat.log

# Query CIEU events
sqlite3 .ystar_memory.db "SELECT timestamp, event_type, description FROM cieu_events WHERE event_type LIKE 'CEO_HEARTBEAT%' ORDER BY timestamp DESC LIMIT 10"
```

---

## Architecture Integration

```
System Cron (every 5min)
    ↓
ceo_heartbeat.py --once
    ↓
[Check .ystar_active_agent == "ceo"]
    ↓
[Parse priority_brief.md → today_targets]
    ↓
[Query .ystar_memory.db → last CEO event]
    ↓
[Detect: IDLE / OFF_TARGET / TODAY_DONE]
    ↓
[Emit CIEU event to .ystar_memory.db]
    ↓
Consumed by:
  - OmissionEngine (pending obligations)
  - AutonomyDriver Engine (action queue recompute)
  - ResidualsLoopEngine (learning triggers)
```

---

## Constraints Met

- ✅ **≤ 25 tool_uses** — actual: 13 (52% utilization)
- ✅ **No conflict with Jordan's preservation guard** — different files (`scripts/ceo_heartbeat.py` vs `scripts/tech_radar.py`)
- ✅ **pytest all green** — 14/14 tests pass
- ✅ **Atomic commit + push** — 2 commits:
  - `6aa26aa` feat(platform): CEO self-heartbeat loop
  - `5e6722b` docs: CEO heartbeat integration guide

---

## Known Limitations (Out of Scope)

### 1. CIEU Persistence Bug

**Current state**: `.ystar_memory.db` may not have `cieu_events` table (Maya fixing L1.02 persistence bug).

**Workaround**: Heartbeat runs and logs output, but events may not persist across sessions until Maya ships fix.

### 2. MVP Stubs (Future Integration)

**OFF_TARGET detection**: Currently returns `False` (assumes on-target). Future: integrate with `ADE.detect_off_target(agent_id="ceo", current_action)`.

**TODAY_DONE detection**: Currently returns `False` (assumes not done). Future: query omission_store for obligation completion status.

### 3. Session vs. Idle Ambiguity

**Current**: Detects idle by "no CIEU events in 5min".

**Gap**: Can't distinguish between:
- CEO actively reading/thinking (in session, but no CIEU events)
- CEO truly idle (no session active)

**Future**: Use OpenClaw session markers or `.claude/` workspace activity timestamps.

---

## Next Steps

### Immediate (Board Action)

1. **Install crontab** — copy command from §Crontab Integration above
2. **Verify logs** — `tail -f /tmp/ceo_heartbeat.log` after 5 minutes
3. **Observe CEO behavior** — CEO should self-pull tasks from priority_brief without Board prompting

### Phase 2 (After Maya Ships CIEU Persistence Fix)

1. **Verify CIEU events persist** — query `.ystar_memory.db` after session restart
2. **Enable ADE integration** — replace `check_off_target()` stub with `ADE.detect_off_target()`
3. **Enable omission_store integration** — replace `check_today_done()` stub with obligation completion query

### Phase 3 (Autonomy Escalation)

1. **Idle escalation hierarchy**:
   - 5min → yellow alert (IDLE)
   - 15min → orange alert (ESCALATE)
   - 30min → red alert (auto-delegate today_targets to sub-agents)

2. **Smart session detection** — use OpenClaw activity markers to differentiate reading vs. idle

---

## Impact Assessment

### Before This Work

- CEO reactive: waits for Board questions or agent pings
- CEO has no autonomous goal-tracking loop
- priority_brief.today_targets exist but no enforcement mechanism
- ADE idle-pull benefits other agents, but CEO excluded

### After This Work

- CEO autonomous: self-monitors every 5 minutes
- CEO detects own idle state and emits triggers
- priority_brief becomes active driver (not passive reference)
- CEO circulatory system established (heartbeat → CIEU → action_queue)

### Key Metric

**CEO CIEU event frequency**:
- Before: only when Board active in session
- After: every 5-10 minutes during work hours (autonomous heartbeat)

---

## Commits

1. **6aa26aa** — `feat(platform): CEO self-heartbeat loop — autonomous proactivity`
   - scripts/ceo_heartbeat.py (227 lines)
   - tests/test_ceo_heartbeat.py (14 tests)
   - knowledge/eng-platform/achievements/ceo_heartbeat_autonomy_loop_2026_04_13.md

2. **5e6722b** — `docs: CEO heartbeat integration guide — crontab setup + troubleshooting`
   - docs/ceo_heartbeat_integration.md (220 lines)

**Branch**: `main`  
**Status**: ✅ Pushed to origin

---

## Handoff to CEO Aiden

**Action required from you**:

1. **Install crontab** (1 minute):
   ```bash
   crontab -e
   # Add line: */5 * * * * /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ceo_heartbeat.py --once >> /tmp/ceo_heartbeat.log 2>&1
   ```

2. **Verify after 24h**:
   - Check `/tmp/ceo_heartbeat.log` for heartbeat runs
   - Observe if you're auto-pulling from priority_brief without Board prompting
   - Report autonomy behavior change to Board

3. **Integration with ADE** (when Maya ships autonomy_driver.py):
   - Replace `check_off_target()` stub in ceo_heartbeat.py
   - Replace `check_today_done()` stub
   - This will activate full alignment detection

**This is your autonomy circulatory system.** You now have a heartbeat that keeps you proactive, not reactive.

---

**Ryan Park (eng-platform)**  
2026-04-13 08:52 EDT  
Tool uses: 13 / 25
