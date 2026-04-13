# CEO Self-Heartbeat Loop — Integration Guide

## Overview

`scripts/ceo_heartbeat.py` provides autonomous proactivity for CEO Aiden by monitoring idle time and alignment with `priority_brief.md` targets.

## How It Works

Every 5 minutes (configurable), the heartbeat loop:

1. **Checks identity** — only runs when `.ystar_active_agent == "ceo"`
2. **Reads targets** — parses `reports/priority_brief.md` YAML frontmatter
3. **Queries activity** — checks `.ystar_memory.db` for last CEO CIEU event
4. **Emits triggers** if conditions met:
   - `CEO_HEARTBEAT_IDLE` — no CEO events in last 5min
   - `CEO_HEARTBEAT_OFF_TARGET` — current action misaligned with today_targets
   - `CEO_TODAY_DONE_PULL_TOMORROW` — all today_targets complete

## Installation

### Option 1: System Crontab (Recommended)

```bash
crontab -e
```

Add this line:

```cron
*/5 * * * * /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ceo_heartbeat.py --once >> /tmp/ceo_heartbeat.log 2>&1
```

### Option 2: Manual Testing

```bash
# Test without emitting CIEU events
python3 scripts/ceo_heartbeat.py --dry-run --once

# Run once and emit real events
python3 scripts/ceo_heartbeat.py --once

# Continuous loop (testing only)
python3 scripts/ceo_heartbeat.py --interval 60
```

## Verifying It's Working

### 1. Check crontab logs

```bash
tail -f /tmp/ceo_heartbeat.log
```

Expected output every 5 minutes:
```
[2026-04-13 08:52:34] CEO Heartbeat Check
[SKIP] Active agent is eng-platform, not ceo
```

OR (when CEO is active):
```
[2026-04-13 09:00:00] CEO Heartbeat Check
[INFO] Today's targets: 3 items
[CIEU] CEO_HEARTBEAT_IDLE — CEO idle for >5min, pulling next action from priority_brief
```

### 2. Query CIEU database

```bash
sqlite3 .ystar_memory.db "SELECT timestamp, event_type, description FROM cieu_events WHERE event_type LIKE 'CEO_HEARTBEAT%' ORDER BY timestamp DESC LIMIT 10"
```

### 3. Monitor priority_brief alignment

When CEO is active and receiving heartbeat triggers, check:

```bash
cat reports/priority_brief.md | grep -A 10 "today_targets:"
```

CEO should be working on items from this list, not drifting to meta-tasks.

## Architecture

```
┌──────────────────────┐
│  System Cron (every  │
│      5 minutes)      │
└──────────┬───────────┘
           │
           v
┌──────────────────────────────────────────────┐
│  scripts/ceo_heartbeat.py --once             │
│                                              │
│  1. Read .ystar_active_agent                │
│     └─> SKIP if not "ceo"                   │
│                                              │
│  2. Parse reports/priority_brief.md         │
│     └─> Extract today_targets list          │
│                                              │
│  3. Query .ystar_memory.db                  │
│     └─> Get last CEO event timestamp        │
│                                              │
│  4. Detect condition:                        │
│     ├─> OFF_TARGET → emit CIEU              │
│     ├─> IDLE (>5min) → emit CIEU            │
│     └─> TODAY_DONE → emit CIEU              │
└──────────────────────────────────────────────┘
           │
           v
┌──────────────────────────────────────────────┐
│  .ystar_memory.db (CIEU events table)       │
│                                              │
│  Consumed by:                                │
│  - gov-mcp OmissionEngine                    │
│  - Autonomy Driver Engine (ADE)             │
│  - ResidualsLoopEngine (RLE)                │
└──────────────────────────────────────────────┘
```

## Dependencies

- **CIEU persistence** — requires `.ystar_memory.db` with `cieu_events` table
  - Current status: Maya (eng-governance) fixing L1.02 CIEU persistence bug
  - Until fixed, heartbeat runs but events may not persist across sessions

- **priority_brief.md** — requires YAML frontmatter with `today_targets`
  - Schema: `reports/priority_brief.md` v0.4+
  - Validator: `scripts/priority_brief_validator.py`

- **Active agent tracking** — requires `.ystar_active_agent` file
  - Managed by `scripts/governance_boot.sh`
  - Restricted write path (only Secretary can modify)

## Troubleshooting

### Symptom: No CIEU events emitted

**Diagnosis**:
```bash
python3 scripts/ceo_heartbeat.py --dry-run --once
```

**Possible causes**:
1. Active agent is not "ceo" → expected, heartbeat only runs for CEO
2. CEO has recent activity (<5min) → expected, no idle trigger
3. CIEU db missing `cieu_events` table → Maya fixing persistence bug

### Symptom: Cron not running

**Check cron service**:
```bash
# macOS
launchctl list | grep cron

# Linux
systemctl status cron
```

**Check cron logs**:
```bash
# macOS
tail -f /tmp/ceo_heartbeat.log

# Linux
tail -f /var/log/syslog | grep cron
```

### Symptom: Permission denied

**Fix Python path in crontab**:
```bash
which python3  # get full path
# Update crontab with absolute path
```

## Future Enhancements

### Phase 2: Integrate with ADE

When `ystar/governance/autonomy_driver.py` is implemented:

```python
# Replace stub
def check_off_target(targets: list) -> bool:
    from ystar.governance.autonomy_driver import AutonomyDriver
    ade = AutonomyDriver(cieu_store=cieu_store, omission_store=omission_store)
    
    # Get CEO's current action (from session state or CIEU log)
    current_action = get_current_ceo_action()
    
    return ade.detect_off_target(agent_id="ceo", current_action=current_action)
```

### Phase 3: Smart Session Detection

Differentiate between:
- CEO actively thinking (in session, but no CIEU events due to reading)
- CEO truly idle (no session active)

Use OpenClaw session markers or `.claude/` workspace activity.

### Phase 4: Escalation Hierarchy

```
IDLE 5min  → emit CEO_HEARTBEAT_IDLE (yellow alert)
IDLE 15min → emit CEO_HEARTBEAT_ESCALATE (orange alert)
IDLE 30min → auto-delegate today_targets to sub-agents (red alert)
```

## References

- **Achievement report**: `knowledge/eng-platform/achievements/ceo_heartbeat_autonomy_loop_2026_04_13.md`
- **Tests**: `tests/test_ceo_heartbeat.py` (14 tests, all passing)
- **Related**: `knowledge/eng-governance/achievements/autonomy_driver_engine_mvp_2026_04_13.md` (ADE spec)
- **Priority brief schema**: `governance/priority_brief_schema.md`

---

**This is CEO's autonomy circulatory system** — no longer waiting for Board to ask questions.
