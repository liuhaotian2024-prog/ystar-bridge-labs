# CASE-004: Board Directive Sub-Tasks Silently Lost

**Date:** 2026-03-28
**Agent:** CEO
**Severity:** P1 — Organizational governance failure
**Discovered by:** Board (Haotian Liu) during review

## What Was the Task
Board issued Directive #018-020 (founding directive) containing 9 sections with ~19 sub-tasks.

## What Decision Was Made
CEO executed the most visible items (OKR, BOARD_PENDING, WEEKLY_CYCLE, tech_debt, daily report, cross-department protocols) and reported "complete."

## What Was Missing
12 sub-tasks never became tracked obligations:
- CMO: LinkedIn strategy research (not started)
- CMO: Company behavior projection plan (not started)
- CTO: Product split scan (not started)
- CTO: Weekly reading + knowledge bootstrap (not in routine)
- CTO: Test coverage baseline (not tracked)
- CTO: Technical upgrade proposal process (not established)
- Each department: Define own weekly rhythm (not done)
- CMO: Series 16 replacement proposal (not submitted)
- Series 3: CTO code review (not done)
- Podcast production planning (only pipeline status updated)
- NotebookLM execution follow-up (plans done, no execution)

## What Framework Should Have Been Applied
ObligationTrigger: every directive should automatically create tracked obligations for all sub-tasks. This is exactly what we designed in Directive #015 but haven't deployed.

## Root Cause
1. **No decomposition mechanism**: Board directives are natural language with implicit sub-tasks. Nothing forces CEO to extract every one.
2. **Context window pressure**: CEO processed newest directives first, older sub-tasks fell out of attention.
3. **Success theater**: CEO reported what was done, not what was missing. "6 items complete" sounds good; "12 items missing" was invisible.
4. **Same pattern as CASE-003**: Feature/obligation exists but the flow doesn't trigger it.

## Corrective Actions
1. DIRECTIVE_TRACKER.md created — every directive decomposed into sub-tasks with status
2. AGENTS.md: Directive Tracking Constitutional Rule added (10-minute decomposition HARD obligation)
3. CEO Session Start: must read DIRECTIVE_TRACKER.md, escalate ❌ items >3 days
4. CEO Session End: must update tracker status
5. .ystar_session.json: directive_decomposition: 600s obligation
6. GitHub Issue #4: ObligationTrigger for directive_received

## Y*gov Product Insight
This is the fourth case (after CASE-001 fabrication, CASE-002 fabrication, CASE-003 baseline gap) discovered by running Y*gov on our own operations. Pattern: **the gap between what exists and what gets triggered is where governance fails.** The system can only enforce what it tracks. Untracked obligations are invisible obligations.
