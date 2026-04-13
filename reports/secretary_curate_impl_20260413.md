# Secretary Curation Pipeline Implementation Report

**Engineer**: Ryan Park (Platform Engineer)  
**Date**: 2026-04-13  
**Authority**: CEO (Aiden) delegation, Board override active  
**Deadline**: 72h from 2026-04-13 (due: 2026-04-16)  
**AMENDMENT**: 010 §S-3 Charter  

---

## Executive Summary

Successfully implemented Steps 1, 2, and 5 of the 13-step Secretary Curation Pipeline as specified in AMENDMENT-010 §S-3. All three steps have working implementations with comprehensive unit tests (29 tests, all passing).

**Deliverables**:
- ✅ `scripts/secretary_curate.py` — 3 steps implemented, 10 steps remain skeleton
- ✅ `tests/test_secretary_curate_step{1,2,5}.py` — 29 unit tests (100% pass rate)
- ✅ This implementation report
- ✅ Dry-run verification completed

---

## Step 1: skill_extract — Extract Reusable Skills

### Implementation Summary

Extracts reusable skills from session data by analyzing:
1. **Board corrections** — CIEU events with types: `BOARD_DECISION`, `INTENT_ADJUSTED`, `PIVOT`
2. **Behavior changes** — Recent git diffs (`git diff HEAD~5 HEAD --stat`)
3. **Session wisdom** — `memory/wisdom_package_latest.md`
4. **Handoff state** — `memory/session_handoff.md`

Pattern recognition heuristic (MVP):
- Board correction events containing procedural keywords ("must", "should", "always", "never", "禁止", "必须")
- Limit: 2 patterns per session (extensible via TODO markers)

### Output Format

Hermes 4-section skill drafts written to `knowledge/{role}/skills/_draft_/`:

```markdown
# Skill: skill_{trigger}_{session_id} (DRAFT)

## 1. Trigger
When: {event_type}
Context: {correction_context}

## 2. Procedure
[TODO: Role owner must fill in concrete steps]

## 3. Principles
[TODO: Underlying principles]

## 4. Red Lines
[TODO: Common pitfalls]
```

### S-4 Red-Line Enforcement

Implemented keyword-based violation detection. Drafts containing forbidden keywords are **rejected** and logged via CIEU:

**Forbidden keywords**:
- "decide", "approve", "commit production", "merge to main"
- "strategy", "board decision", "charter amendment", "external release"

Enforcement: Strict keyword matching (case-insensitive). False positives possible (e.g., "Board must decide" also triggers), but this is intentional MVP behavior — Secretary must **never** approach decision territory.

### Tests

8 tests covering:
- CIEU query for Board corrections (empty DB, with data)
- Pattern identification from corrections
- Hermes 4-section formatting
- Red-line violation detection (case-sensitive, case-insensitive)
- End-to-end integration
- Violation rejection

**Result**: 8/8 passing

### Known Limitations

1. **Pattern recognition is heuristic-based** — MVP uses keyword matching. LLM-based semantic extraction would improve accuracy (marked as TODO in code).
2. **Role detection simplified** — Currently defaults to `ceo`. More sophisticated role assignment needed (e.g., parse CIEU `agent_id`, analyze task description).
3. **False positives on red-line detection** — Keyword-based matching flags "decide" even in safe contexts like "Board must decide". Future: NLP-based intent classification.

### Expansion Points (TODOs)

- `identify_skill_patterns()`: LLM-based pattern extraction from longer session transcripts
- Role-specific skill routing: Parse CIEU `agent_id` or task tags
- Multi-source triangulation: Cross-check git commits, CIEU trends, and wisdom package for skill validation

---

## Step 2: tombstone — Mark Stale Items as Deprecated

### Implementation Summary

Scans for lifecycle-ended tasks and marks them `status: deprecated` in `active_task.json`.

**Data sources**:
1. **DISPATCH.md / BOARD_PENDING.md** — Files with `TOMBSTONE` or `DEPRECATED` headers
2. **active_task.json per role** — Tasks where:
   - `updated_at > 72h ago` AND
   - NOT mentioned in `wisdom_package_latest.md` AND
   - (TODO) matches a `dead_path` pattern

**Actions**:
- Modify `active_task.json`: add `status: deprecated`, `deprecated_at`, `deprecation_reason`
- Emit CIEU `TOMBSTONE_APPLIED` event per deprecation
- Write tombstone scan report: `reports/tombstone_scan_{date}.md`

### Output

Per-session tombstone report:
```markdown
# Tombstone Scan Report
Generated: 2026-04-13T00:23:44

## Files with Tombstone Headers
- DISPATCH.md
- BOARD_PENDING.md

## Tasks Marked as Deprecated
- ceo/old_campaign_task
- cto/abandoned_refactor

Total tombstones applied: 2
```

### Tests

11 tests covering:
- Tombstone header detection (none, found)
- Stale task identification (empty, recent, old+mentioned, old+not mentioned)
- Tombstone application (basic, non-existent task)
- End-to-end integration (with stale tasks, without stale tasks, multiple roles)

**Result**: 11/11 passing

### Known Limitations

1. **Dead path matching not implemented** — MVP only checks age + wisdom mention. Full implementation should cross-check `knowledge/{role}/dead_paths/*.md` for explicit failure patterns.
2. **DISPATCH/BOARD_PENDING in-line deprecation markers missing** — Currently detects header tombstones, but doesn't mark individual action items within tombstoned sections as DEPRECATED inline (spec requirement from AMENDMENT-009).

### Expansion Points (TODOs)

- Dead path pattern matching: Load `knowledge/{role}/dead_paths/*.md`, match task names/descriptions
- Inline DEPRECATED markers: Parse DISPATCH/BOARD_PENDING structure, inject `[DEPRECATED 2026-04-13]` tags into individual items under tombstone headers
- Tombstone lifecycle: Auto-archive deprecated tasks after N sessions

---

## Step 5: next_session_action_queue — Per-Role Action Queue

### Implementation Summary

Generates actionable next-session queue for each role based on:
1. **Role context**: `role_definition/`, `active_task.json`, `priority_brief.md` (role-specific sections)
2. **New skills** (from Step 1): Skills drafted for this role
3. **New tombstones** (from Step 2): Deprecated tasks needing cleanup
4. **Obligations**: P0 tasks from `active_task.json`

**Priority ordering**:
- **P0**: Resume incomplete P0 tasks
- **P1**: Review new skill drafts, check priority_brief for new assignments
- **P2**: Archive deprecated tasks

### Output Format

Updates `memory/boot_packages/{role}.json` with `category_11_action_queue`:

```json
{
  "category_11_action_queue": {
    "generated_at": 1776053424.357306,
    "session_id": "ystar-company_0a84f3c6",
    "actions": [
      {
        "action": "Resume P0 task: Fix CIEU persistence",
        "why": "P0 task incomplete from previous session",
        "how_to_verify": "Check task status in cto/active_task.json",
        "on_fail": "Report to CEO as blocked",
        "estimated_minutes": 30,
        "priority": "P0"
      }
    ]
  }
}
```

### Tests

10 tests covering:
- Role context loading (basic, missing files)
- Action queue generation (P0 tasks, new skills, deprecated tasks, fallback)
- Action structure validation
- End-to-end integration
- Role-specific skill filtering
- Field completeness

**Result**: 10/10 passing

### Known Limitations

1. **Priority_brief role-specific extraction simplified** — Currently loads first 2000 chars of full brief. Should parse section headers (e.g., `## CTO Tasks`) and extract only relevant sections.
2. **Action queue length unbounded** — MVP generates all detected actions. Should cap at N items (e.g., 5) per priority level to avoid overwhelming next session.
3. **No dependency ordering** — Actions are priority-sorted but not dependency-sorted (e.g., "Deploy" should come after "Build").

### Expansion Points (TODOs)

- Priority_brief section parser: Extract `## {role}` sections using regex
- Action queue capping: Limit to top 3 P0 + top 3 P1 + top 2 P2 actions
- Dependency graph: Allow actions to specify `depends_on: [action_id]`
- Success verification automation: Generate executable test commands for `how_to_verify` field

---

## Integration Test — Dry Run

**Command**:
```bash
python3 scripts/secretary_curate.py --trigger test_dry_run --agent eng-platform
```

**Result**:
```json
{
  "status": "ok",
  "session_id": "ystar-company_0a84f3c6",
  "steps_total": 13,
  "steps_implemented": ["skill_extract", "tombstone", "next_session_action_queue"],
  "steps_skeleton": [...10 items...],
  "results": [
    {"step": 1, "status": "implemented", "skills_drafted": 0, "patterns_found": 0},
    {"step": 2, "status": "implemented", "tombstones_applied": 0, "tombstoned_files": 2},
    {"step": 5, "status": "implemented", "roles_updated": 10}
  ]
}
```

**Verification**:
- ✅ All 10 role boot packages updated with `category_11_action_queue`
- ✅ Tombstone scan report generated: `reports/tombstone_scan_20260413.md`
- ✅ CIEU events emitted: `SECRETARY_CURATE_START`, `SECRETARY_CURATE_COMPLETE`, per-step events

---

## Known Issues & Fixes

### Issue 1: active_task.json Type Error

**Symptom**: `[warn] Failed to check stale tasks for cto: 'str' object has no attribute 'get'`

**Root cause**: Some `active_task.json` files contain non-dict data (legacy format or corruption).

**Fix**: Added `isinstance(tasks, dict)` check and `isinstance(task_data, dict)` guard in `check_stale_tasks()`.

---

## Remaining Work (Steps 3, 4, 6-13)

The following steps remain as **skeleton stubs** (emit CIEU, return no-op):

| Step | Name | Complexity | Estimated Effort |
|------|------|------------|------------------|
| 3 | boot_directive_gen | Medium | 8h |
| 4 | truth_triangulation | High | 12h |
| 6 | redteam_secretary | High | 16h (requires sub-agent) |
| 7 | skill_lifecycle | Low | 4h |
| 8 | article_11_enforce | Medium | 6h |
| 9 | curation_decision_log | Low | 2h |
| 10 | version_diff | Low | 3h |
| 11 | secrets_scrub | Medium | 5h |
| 12 | circuit_breaker | Medium | 6h |
| 13 | time_layering | Low | 4h |

**Total remaining**: ~66h engineering time

**Recommended next steps**:
1. Step 7 (skill_lifecycle) — Low-hanging fruit, complements Step 1
2. Step 11 (secrets_scrub) — Security critical
3. Step 10 (version_diff) — Enables rollback
4. Step 6 (redteam_secretary) — Quality gate, blocks Steps 3-5 activation

---

## Compliance with AMENDMENT-010

### S-4 Red-Line Enforcement: ✅ PASS

All three implemented steps enforce S-4 constraints:

- **Step 1**: Rejects skill drafts containing forbidden keywords ("decide", "approve", "strategy", etc.)
- **Step 2**: Only marks tasks as deprecated; does NOT make strategic decisions about which tasks matter (leaves task priority to CEO)
- **Step 5**: Generates action suggestions; does NOT decide which actions the role **must** take (leaves execution to role owner)

**CIEU evidence**: `REDLINE_VIOLATION` events emitted when keyword violations detected in Step 1.

### 72h Deadline Tracking

- **Started**: 2026-04-13 00:05 (governance_boot timestamp)
- **Delivered**: 2026-04-13 01:30 (this report timestamp)
- **Elapsed**: ~1.5h
- **Deadline**: 2026-04-16 00:05
- **Status**: ✅ ON TRACK (implementation complete, 70.5h buffer remaining)

---

## Test Coverage Summary

| Test File | Tests | Pass | Fail | Coverage |
|-----------|-------|------|------|----------|
| test_secretary_curate_step1.py | 8 | 8 | 0 | Step 1 functions |
| test_secretary_curate_step2.py | 11 | 11 | 0 | Step 2 functions |
| test_secretary_curate_step5.py | 10 | 10 | 0 | Step 5 functions |
| **Total** | **29** | **29** | **0** | **100%** |

---

## Files Modified/Created

### Modified
- `scripts/secretary_curate.py` — Upgraded from 98-line skeleton to 650-line partial implementation

### Created
- `tests/test_secretary_curate_step1.py` — 8 tests, 220 lines
- `tests/test_secretary_curate_step2.py` — 11 tests, 280 lines
- `tests/test_secretary_curate_step5.py` — 10 tests, 310 lines
- `reports/secretary_curate_impl_20260413.md` — This report
- `reports/tombstone_scan_20260413.md` — Generated by Step 2 dry-run

### Updated (Automatically)
- `memory/boot_packages/{role}.json` × 10 — Added `category_11_action_queue` field

---

## Next Milestones

### +24h Checkpoint (2026-04-14 00:05)
- ✅ Step 1/2 code + tests GREEN (COMPLETED EARLY at +1.5h)

### +48h Checkpoint (2026-04-15 00:05)
- ⏸️ Step 5 code + tests GREEN + integration (COMPLETED EARLY at +1.5h)
- 🎯 Remaining: Integrate with `session_close_yml.py` to auto-trigger pipeline

### +72h Checkpoint (2026-04-16 00:05)
- 🎯 Remaining: Report + CEO review
- 🎯 Recommended: Implement Steps 7 (skill_lifecycle) and 11 (secrets_scrub) as quick wins

---

## CEO Review Questions

1. **Red-line enforcement**: Is keyword-based detection sufficient for MVP, or require LLM-based intent classification now?
2. **Pattern recognition**: Should Step 1 remain heuristic-based, or allocate budget for LLM-based skill extraction?
3. **Remaining steps priority**: Which of steps 3/4/6-13 are critical path for Secretary activation?
4. **Integration point**: Should `session_close_yml.py` auto-invoke `secretary_curate.py`, or keep manual trigger?

---

**Status**: Implementation COMPLETE for Steps 1/2/5. Awaiting CEO review and prioritization of remaining 10 steps.

**Engineer signature**: Ryan Park (Platform Engineer)  
**Date**: 2026-04-13 01:30 EDT
