# CASE-003: Baseline Assessment Not Triggered During Installation

**Date:** 2026-03-29
**Agent:** CTO (installation flow) / CEO (deployment oversight)
**Severity:** P1 — Product gap, data permanently lost
**Discovered by:** Board (Haotian Liu) during K9 Scout verification

## What Was the Task
Deploy Y*gov on Mac mini (K9 Scout) and verify all features work.

## What Decision Was Made
Team ran `ystar setup` + `ystar hook-install` + `ystar doctor`. All 6 checks passed. Team declared installation successful.

## What Was Missing
The installation flow never triggered `ystar baseline` or `_run_retroactive_baseline()`. The code exists in:
- `ystar/kernel/retroactive.py` — `assess_batch()`, `RetroAssessment`, `RetroScanResult`
- `ystar/_cli.py:179-289` — `_run_retroactive_baseline()`

But neither `ystar setup` nor `ystar hook-install` calls it. The user must manually run `ystar baseline` — which is not documented in the README, not mentioned in `ystar doctor` output, and not part of the standard installation flow.

## What Was the Outcome
The Mac's pre-governance state was never recorded. We cannot produce a Before/After comparison for this deployment. The "before" snapshot is permanently lost — you can't retroactively capture what the system looked like before governance was active.

## What Framework Should Have Been Applied
Werner Vogels' "everything fails" principle: if a step can be skipped, it will be skipped. Critical data collection must be automatic, not optional.

## Root Cause Analysis
1. **Installation flow incomplete:** `ystar setup` should automatically trigger baseline assessment
2. **No documentation:** README doesn't mention `ystar baseline` command
3. **No reminder:** `ystar doctor` doesn't check for baseline existence
4. **Team blind spot:** CTO and CEO focused on "does check() work?" and missed "did we capture the before state?"

## What to Do Differently
1. `ystar setup` must automatically run baseline assessment before installing hooks
2. `ystar doctor` should check: "Does .ystar_retro_baseline.db exist? If not, warn."
3. README installation instructions must include baseline step
4. The correct installation flow should be:
   ```
   ystar setup          → configure session
   ystar baseline       → capture pre-governance state (AUTOMATIC)
   ystar hook-install   → activate governance
   ystar doctor         → verify everything including baseline
   ```

## Y*gov Product Issue
This is not a semantic-layer violation (CASE-001, CASE-002). This is an **installation flow gap**: the product has the feature but the flow doesn't use it.

**GitHub Issue needed:** "ystar setup should automatically trigger baseline assessment"
