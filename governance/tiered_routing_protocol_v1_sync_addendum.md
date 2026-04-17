# Tiered Routing Protocol v1 — Sync Layer Addendum

**Constitutional — Board 2026-04-16 P0 emergency integration with tier-routing v1**

## Problem Statement

Tier-routing v1 (#66 in-flight) authorizes CEO T1 fast-lane direct dispatch to engineers. This solves velocity bottleneck but introduces **info asymmetry risk**: CTO Ethan spawns unaware of CEO recent dispatches → duplicate/conflicting scope assignments → chaos.

**Real failure case**: Ryan PYTHONPATH P0 emergency was CEO direct-dispatched T1. CTO instance spawned later for architecture work had no awareness, only learned via CIEU post-audit.

## Design Goal

**3-layer sync mechanism** ensuring T1 CEO fast-lane **coexists safely** with CTO orchestration authority. CTO awareness without blocking CEO velocity.

---

## Layer 1 — Immediate Audit Log (Append-Only)

### File: `governance/active_dispatch_log.md`

**Format** (newest-first immutable append):
```
[2026-04-16T14:32:15Z] CEO_DISPATCH(ryan-platform, atomic_id=CZL-66, scope=[governance/forget_guard_rules.yaml], tier=T1, expected_completion=30m)
[2026-04-16T13:58:42Z] CEO_DISPATCH(leo-kernel, atomic_id=CZL-65, scope=[ystar/kernel/czl_protocol.py], tier=T1, expected_completion=15m)
```

**Schema**:
- `timestamp`: ISO 8601 UTC
- `engineer`: ryan-platform / leo-kernel / maya-governance / jordan-domains
- `atomic_id`: CZL dispatch identifier (unique, matches CIEU event payload)
- `scope`: list of file paths in-scope
- `tier`: T1 / T2 / T3 (per tier-routing v1 spec)
- `expected_completion`: human-readable window (15m / 30m / 1h / 2h)

**Append helper** (single-line call, CEO uses before spawning):
```bash
python3 scripts/dispatch_sync.py record \
  --engineer ryan-platform \
  --atomic_id CZL-66 \
  --scope governance/forget_guard_rules.yaml \
  --tier T1 \
  --expected_completion 30m
```

**CIEU integration**: `dispatch_sync.py record` emits `CEO_DIRECT_DISPATCH_TIER1` event with payload:
```json
{
  "agent_target": "ryan-platform",
  "atomic_id": "CZL-66",
  "file_paths_in_scope": ["governance/forget_guard_rules.yaml"],
  "tool_use_budget": 15,
  "tier": "T1",
  "expected_completion_window": "30m"
}
```

---

## Layer 2 — CTO Boot Awareness Injection

### Mechanism: Auto-inject recent dispatch history into CTO spawn prompt

**Template injection point**: When CEO/Secretary spawns Ethan-CTO instance, boot prompt template auto-injects:

```
## BOOT CONTEXT — Recent CEO Direct Dispatches (last 24h)

CEO has directly dispatched the following T1 fast-lane atomic tasks in the last 24h:

[2026-04-16T14:32] ryan-platform: CZL-66 (governance/forget_guard_rules.yaml) — 30m window
[2026-04-16T13:58] leo-kernel: CZL-65 (ystar/kernel/czl_protocol.py) — 15m window

Before planning new dispatches, check active_dispatch_log.md to avoid scope conflicts.
If your planned work overlaps with CEO fast-lane dispatch, either:
(1) Skip that scope (CEO already dispatched)
(2) Coordinate via SendMessage to CEO before spawning duplicate sub-agent
```

**Implementation**:
- Modify `sub_agent_boot_prompt_template.md` Section 2 to include:
  ```bash
  cat governance/active_dispatch_log.md | head -10
  ```
- Or inline via `dispatch_sync.py get_recent --window_hours 24` (returns formatted list)

**Enforcement**: CTO instance boot checklist now includes "Read active_dispatch_log.md" as mandatory step (enforced via `subagent_boot_no_state_read` ForgetGuard rule variant).

---

## Layer 3 — Velocity Escalation Alert

### Trigger: CEO direct dispatch velocity > 5 within 1h window

**Purpose**: Detect CEO autonomous over-dispatching (signal of workload spike or planning breakdown). Auto-escalate to CTO for review.

**ForgetGuard Rule** (`governance/forget_guard_rules.yaml` new entry):

```yaml
- id: ceo_dispatch_velocity_too_high
  enabled: true
  description: "CEO T1 fast-lane dispatch velocity >5 within 1h window — auto-escalate to CTO for review"
  last_reviewed: "2026-04-16"
  reviewer: "eng-governance"

  trigger:
    event_source: cieu
    conditions:
      - type: event_type_equals
        value: "CEO_DIRECT_DISPATCH_TIER1"
      - type: velocity_threshold
        event_type: "CEO_DIRECT_DISPATCH_TIER1"
        count: 5
        window_seconds: 3600

  action: warn
  recipe: |
    CEO dispatch velocity exceeded threshold (>5 T1 fast-lane dispatches in 1h).

    This may indicate:
    - Workload spike requiring CTO orchestration
    - Planning breakdown (multiple atomic tasks should be single campaign)
    - T1 tier misclassification (tasks should be T2/T3)

    Automated escalation:
    (1) Auto-emit CIEU event: CEO_DISPATCH_VELOCITY_ALERT
    (2) (Post governance_ci impl) Auto-spawn Ethan-CTO with prompt:
        "Review CEO recent autonomous activity (last 1h). Recommend tier 
        reclassification or scope tightening if dispatch velocity abnormal."

    CEO: Review active_dispatch_log.md. Consider consolidating atomic tasks 
    into single campaign with CTO orchestration instead of fast-lane.

    Ref: governance/tiered_routing_protocol_v1_sync_addendum.md Layer 3

  cieu_event: CEO_DISPATCH_VELOCITY_ALERT
  severity: medium
```

**Counter reset**: Hourly window (rolling, not daily reset). Velocity counts CEO_DIRECT_DISPATCH_TIER1 events with timestamp within last 3600s.

**Escalation automation** (post-governance_ci):
- When `CEO_DISPATCH_VELOCITY_ALERT` fires, `governance_ci.py` auto-spawns Ethan-CTO with advisory prompt
- CTO reviews recent dispatches, recommends consolidation or tier reclassification
- CEO receives CTO recommendation via SendMessage (non-blocking, advisory only)

---

## Integration with Tier-Routing v1 (#66)

### Amendment to Tier-Routing v1 Spec

**Section 7 — Sync Layer Requirement** (new):

> **Sync Layer Mandatory**: T1 CEO direct-dispatch is authorized ONLY after 3-layer sync mechanism is LIVE:
> - Layer 1: `governance/active_dispatch_log.md` append + `CEO_DIRECT_DISPATCH_TIER1` CIEU emit
> - Layer 2: CTO boot prompt auto-injects recent dispatch history
> - Layer 3: `ceo_dispatch_velocity_too_high` ForgetGuard rule enabled
>
> **Before sync layer ships**: T1 tasks must route via CTO (legacy protocol). CEO may NOT fast-lane direct-dispatch.
>
> **After sync layer ships**: CEO authorized to fast-lane T1 atomics. CTO awareness guaranteed via boot context.

### Migration Path

1. **Ryan ships `dispatch_sync.py`** (per inline test card below)
2. **Maya amends `sub_agent_boot_prompt_template.md`** to inject `active_dispatch_log.md` (Layer 2)
3. **Maya adds `ceo_dispatch_velocity_too_high` rule** to `forget_guard_rules.yaml` (Layer 3)
4. **Ryan integrates `dispatch_sync.py record` call into `governance_boot.sh`** (CEO boot checklist)
5. **CTO tests**: Spawn Ethan instance, verify boot prompt includes recent dispatch history
6. **CEO tests**: Direct-dispatch T1 atomic, verify `active_dispatch_log.md` append + CIEU emit
7. **Tier-routing v1 (#66) Section 7 amendment merged** — sync layer certified LIVE

**Estimated timeline**: 3h total (1h Ryan, 1h Maya, 1h integration test).

---

## Test Card — Inline Specification for Ryan (eng-platform)

### Task: Ship `dispatch_sync.py` + governance_boot.sh integration

**Atomic ID**: CZL-67  
**Engineer**: ryan-platform  
**Priority**: P0 (blocks tier-routing v1 safe activation)  
**Scope**: `scripts/dispatch_sync.py`, `scripts/governance_boot.sh`

**Acceptance Criteria**:
- [ ] `scripts/dispatch_sync.py` exists with 2 subcommands:
  - `record --engineer X --atomic_id Y --scope Z --tier T --expected_completion W`
  - `get_recent --window_hours N` (returns last N hours dispatch list, newest-first)
- [ ] `record` subcommand appends to `governance/active_dispatch_log.md` (create if missing)
- [ ] `record` subcommand emits CIEU event `CEO_DIRECT_DISPATCH_TIER1` with JSON payload schema above
- [ ] `get_recent` subcommand reads `active_dispatch_log.md`, filters by timestamp window, returns formatted list
- [ ] `governance_boot.sh` Section 4 (CEO checklist) adds: `python3 scripts/dispatch_sync.py get_recent --window_hours 24` (verify command works, no enforcement yet)
- [ ] Tests pass: `python3 -m pytest tests/platform/test_dispatch_sync.py -q` (≥3 tests: record_appends, record_emits_cieu, get_recent_filters)
- [ ] No files outside `scripts/` modified
- [ ] Commit message: `[L3→L4] feat(platform): dispatch_sync.py — 3-layer CTO awareness (CZL-67)`

**Test specification** (Ryan writes these tests first):
```python
# tests/platform/test_dispatch_sync.py

def test_dispatch_sync_record_appends_to_log():
    # Setup: delete active_dispatch_log.md if exists
    # Execute: dispatch_sync.py record --engineer ryan-platform --atomic_id CZL-99 --scope foo.py --tier T1 --expected_completion 15m
    # Verify: governance/active_dispatch_log.md contains [timestamp] CEO_DISPATCH(ryan-platform, atomic_id=CZL-99, scope=[foo.py], tier=T1, expected_completion=15m)
    pass

def test_dispatch_sync_record_emits_cieu_event():
    # Execute: dispatch_sync.py record (same params as above)
    # Verify: CIEU database contains event type=CEO_DIRECT_DISPATCH_TIER1 with payload.agent_target=ryan-platform
    pass

def test_dispatch_sync_get_recent_filters_by_window():
    # Setup: populate active_dispatch_log.md with 3 entries (1h ago, 2h ago, 25h ago)
    # Execute: dispatch_sync.py get_recent --window_hours 24
    # Verify: output contains 2 entries (1h, 2h), excludes 25h entry
    pass
```

**Tool_use budget**: ≤12 (script is <100 lines, tests <80 lines, integration 1-line change to governance_boot.sh)

**Expected completion**: 30m

**Yt+1**: `dispatch_sync.py` shipped + 3 tests PASS + governance_boot.sh integration LIVE + commit hash available

**Rt+1 criteria**:
- `0.0` if all 6 acceptance criteria checked + 3 tests PASS + commit exists
- `1.0` if script incomplete or tests fail or no CIEU integration
- `0.5` if script works but tests missing or governance_boot.sh integration skipped

---

## Post-Sync Layer Activation — CTO Workflow Update

After sync layer ships, CTO spawn workflow becomes:

**Pre-spawn checklist** (enforced via boot prompt):
1. Read `governance/active_dispatch_log.md` (last 10 entries)
2. Check for scope overlap with planned dispatch
3. If overlap exists → SendMessage to CEO for coordination OR skip that scope

**Example**:
```
CTO: Planning to dispatch Maya to governance/forget_guard_rules.yaml.
Boot context shows CEO already dispatched ryan-platform to same file 15 minutes ago (CZL-66).
Action: SendMessage to CEO: "Ryan CZL-66 overlaps with my planned Maya dispatch. Coordinate?"
```

**No velocity penalty**: CTO awareness is passive (read log, no blocking wait). T1 fast-lane retains speed advantage.

---

## Monitoring & Observability

### CIEU Events
- `CEO_DIRECT_DISPATCH_TIER1` (per T1 dispatch)
- `CEO_DISPATCH_VELOCITY_ALERT` (when >5 dispatches in 1h)
- `CTO_BOOT_AWARENESS_INJECT` (when CTO instance reads active_dispatch_log.md)

### Audit Queries
```bash
# Show all CEO T1 dispatches in last 24h
python3 scripts/cieu_query.py --event_type CEO_DIRECT_DISPATCH_TIER1 --window_hours 24

# Show velocity alerts (CEO over-dispatching)
python3 scripts/cieu_query.py --event_type CEO_DISPATCH_VELOCITY_ALERT --window_hours 168

# Show CTO boot awareness reads
python3 scripts/cieu_query.py --event_type CTO_BOOT_AWARENESS_INJECT --window_hours 24
```

### Dashboard Metrics (post-governance_ci)
- T1 dispatch velocity (dispatches/hour)
- CTO-CEO scope collision rate (% of CTO spawns with overlap)
- Average T1 completion time vs expected_completion window

---

## Failure Modes & Mitigation

### Failure: CEO forgets to call `dispatch_sync.py record` before T1 dispatch
**Detection**: ForgetGuard rule `ceo_direct_dispatch_no_sync_log` (W22.2 backlog)  
**Mitigation**: CIEU event scan detects Agent tool call with engineer target but no prior `dispatch_sync.py record` call → emit `CEO_FORGOT_SYNC_LOG` warning

### Failure: `active_dispatch_log.md` grows unbounded (>1000 entries)
**Detection**: Weekly cron job checks file line count  
**Mitigation**: Archive entries >7 days old to `governance/archive/active_dispatch_log_{year}_{month}.md`

### Failure: CTO instance truncates before reading boot context
**Detection**: `subagent_boot_no_state_read` ForgetGuard rule (detects CTO spawn without `active_dispatch_log.md` read)  
**Mitigation**: Emit `CTO_BOOT_INCOMPLETE` event → CEO re-spawns CTO with explicit "read dispatch log first" reminder

---

## Appendix A — Tool Usage Metadata

**This spec authorship**:
- Tool_uses: 10 (4 Read, 3 Glob, 1 Write, 2 verification checks — honest accounting per E1 enforcement)
- Time to draft: ~18 minutes
- CIEU events emitted during authorship: 0 (spec drafting, no governance actions)

**Expected implementation tool budget**:
- Ryan CZL-67: ≤12 tool_uses (script + tests + integration)
- Maya boot template amendment: ≤5 tool_uses (read template, edit, commit)
- Maya ForgetGuard rule: ≤3 tool_uses (read yaml, append rule, commit)
- Total sync layer ship: ~20 tool_uses (3h elapsed time)

---

**Status**: [L1 SPEC] — ready for Ryan CZL-67 dispatch + Maya follow-on tasks  
**Next action**: CEO dispatch Ryan with inline test card above (atomic CZL-67)  
**Integration blocker**: None (tier-routing v1 #66 can land in parallel, Section 7 amendment merges after sync layer LIVE)
