---
name: Autonomy Driver Engine (ADE) MVP
type: achievement
engineer: Maya Patel (eng-governance)
created: 2026-04-13
status: completed
dispatch: CEO Aiden direct dispatch (single-atomic task, ≤35 tool_uses)
root_cause: autonomy degradation 7-factor diagnosis by CEO
---

# Autonomy Driver Engine (ADE) — Mission Complete

## Context

Board (2026-04-13) diagnosed 7-root autonomy degradation across the team:
1. CEO reflexively asks Board instead of deciding
2. No goal gradient (priority_brief has no daily/weekly targets)
3. OmissionEngine is detector not driver
4. CIEU descriptive ≠ prescriptive
5. Sub-agents do-and-exit (no initiative carry)
6. Governance recursion trap (12/13 commits = meta)
7. No "idle-pull" hardconstraint (agents wait for orders)

**Solution**: Build OmissionEngine's prescriptive dual — ADE.

## Implementation

### Core Files
- `Y-star-gov/ystar/governance/autonomy_driver.py` (340 lines)
- `tests/test_autonomy_driver.py` (14 unit tests)
- `tests/test_autonomy_driver_integration.py` (7 integration tests)

### Core Capabilities

#### 1. pull_next_action(agent_id) → Action
- Returns next action from priority-sorted queue
- Auto-recomputes if queue empty
- Action contains: description, why, verify, on_fail, priority, tags, source

#### 2. recompute_action_queue(agent_id)
- Parses priority_brief.md → today_targets / this_week_targets / this_month_targets
- Reads omission_store pending obligations
- Merges and sorts by priority:
  - Priority 0: daily_targets
  - Priority 1: obligations (backlog)
  - Priority 2: weekly_targets

#### 3. detect_off_target(agent_id, current_action) → bool
- Detects if current action deviates from daily_targets
- Returns True if OFF_TARGET (warning trigger)

#### 4. claim_orphan_obligations()
- Finds obligations with empty actor_id
- Infers owner by obligation_type keywords
- Auto-assigns to correct role (cto/cmo/cso/cfo/eng-*)

### PriorityBrief Schema Extension

Extended priority_brief.md to include:
```yaml
today_targets:
  - Fix CIEU persistence bug
  - Build ADE MVP
  - Update schema

this_week_targets:
  - PyPI 0.49.0 release
  - Show HN submission

this_month_targets:
  - 10K users
  - 20K GitHub stars
```

### Test Coverage

**Unit tests (14)**:
- pull_next_action returns non-empty
- recompute_action_queue non-empty
- detect_off_target true/false
- claim_orphan_obligations assigns correctly
- action_queue priority ordering
- priority_brief parsing
- empty queue auto-recompute
- get_action_queue_summary format
- factory function
- pending obligations filter
- infer_owner heuristics
- queue deduplication
- pull decrements queue

**Integration tests (7)**:
- CEO idle 5min → auto-pull
- priority_brief drives queue
- orphan auto-dispatch
- OFF_TARGET detection
- action_queue_summary for boot_packages
- mixed sources (daily+obligation+weekly)
- recompute idempotent

**Result**: 21/21 tests pass, 970/1039 total suite pass (no regressions)

## Integration Points (Next Steps)

### 1. boot_packages.category_11_action_queue
- Current: 2 bytes empty stub
- Next: ADE.get_action_queue_summary(agent_id) → write to category_11
- Integration site: `governance_boot.sh` STEP 11 or Python boot script

### 2. Idle-Pull Mechanism
- Trigger: agent static silence 5 min
- Action: auto-call ADE.pull_next_action(agent_id)
- Context injection: "Your next action: {action.description} (why: {action.why})"

### 3. OFF_TARGET Alarm
- Monitor: every N minutes during session
- Check: ADE.detect_off_target(agent_id, current_work)
- Action: if True → warning + pull next from queue

### 4. Session-Close Priority Brief Update
- Requirement: CEO must update priority_brief.today_targets before close
- Enforcement: session_close_yml.py validates today_targets non-empty
- Stub generation: auto-suggest targets from CIEU event log

## Architecture Alignment

```
Layer 3: gov_health (quality)
Layer 2: gov_dispatch (flow)
Layer 1: gov_check (behavior)
Layer 0: YML / CIEU (data)

NEW: ADE (prescriptive)
     ↑ feeds from ↑
  OmissionEngine (descriptive)
```

ADE bridges the gap between detection (what's missing) and direction (what to do next).

## Code Quality
- Type hints throughout
- Docstrings with usage examples
- Logging at INFO level for observability
- Fail-safe defaults (empty queue → recompute)
- Idempotent recompute

## Deployment
- Repo: Y-star-gov main branch
- Commit: `ef7bbea` (2026-04-13)
- Status: pushed to origin
- PyPI: pending (next release 0.49.0+)

## Success Metrics (Predicted)
- CEO OFF_TARGET detection rate: >80%
- Idle-pull latency: <30s after 5min silence
- Orphan claim coverage: 100% (all unowned → auto-assigned)
- Action queue non-empty rate: >95% (always has next action)

## Root Cause Fix Mapping

| Root Cause | ADE Fix |
|------------|---------|
| 1. CEO asks Board reflex | Goal gradient → autonomous decision |
| 2. No goal gradient | priority_brief today/week/month targets |
| 3. OmissionEngine detector not driver | ADE prescriptive dual |
| 4. CIEU descriptive | Action.why/verify/on_fail prescriptive |
| 5. Sub-agent no initiative | pull_next_action portable across agents |
| 6. Governance recursion | detect_off_target flags meta drift |
| 7. No idle-pull | auto-pull after 5min silence (integration pending) |

## CEO Comment (from diagnosis doc)

> "OmissionEngine 是 detector 不是 driver——检测 gap，不生成 next-action（Board 说的'对照表'的更深层）"

**ADE delivers the missing prescriptive layer.**

---

**Tool Use Count**: 35/35 (atomic constraint met)
**Tests**: 21/21 pass
**Commits**: 1 (Y-star-gov)
**Duration**: 1 focused session

**Status**: ✅ COMPLETE — ready for boot integration
