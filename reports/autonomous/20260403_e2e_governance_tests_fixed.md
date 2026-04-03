# E2E Governance Pipeline Tests Fixed

**Date:** 2026-04-03  
**Agent:** eng-governance  
**Status:** ✅ Complete  
**Commit:** ad9e7f9

---

## Problem Statement

4 end-to-end governance pipeline tests were failing after previous GateCheckResult fix:
- `test_obligations_produce_violations`
- `test_report_engine_produces_kpis`
- `test_governance_loop_produces_suggestions`
- `test_full_governance_pipeline_smoke`

All failures had the same symptom: **violations list was empty when it should contain violations**.

---

## Root Cause Analysis

### The Issue
Tests were manually setting obligations overdue like this:
```python
ob.due_at = time.time() - 10  # Overdue by 10 seconds
```

However, `OmissionEngine.is_overdue()` checks:
```python
def is_overdue(self, now):
    eff = self.effective_due_at  # = due_at + grace_period_secs
    return now > eff
```

And `effective_due_at` is defined as:
```python
@property
def effective_due_at(self):
    return self.due_at + self.grace_period_secs  # grace_period = 30.0s
```

### The Math
- Test set: `due_at = now - 10`
- Effective deadline: `(now - 10) + 30 = now + 20`
- Is overdue check: `now > now + 20` → **FALSE**

Result: The obligation was overdue relative to `due_at`, but **not overdue relative to effective deadline**. The scan created reminders but not violations.

---

## Solution

Changed all 4 tests to set obligations overdue by **40 seconds** (beyond the 30s grace period):

```python
# Before
ob.due_at = time.time() - 10  # WRONG: within grace period

# After  
ob.due_at = time.time() - 40  # CORRECT: beyond grace period
```

This ensures:
- `effective_due_at = (now - 40) + 30 = now - 10`
- `is_overdue = now > now - 10` → **TRUE**
- Violations are correctly created

---

## Test Results

### Before Fix
```
555 passed, 4 failed
```

### After Fix
```
559 passed
```

All e2e governance pipeline tests now pass. Full pipeline verified:
1. Session config → obligations created ✅
2. Overdue obligations → violations generated ✅
3. Violations → KPIs calculated ✅
4. KPIs → governance suggestions produced ✅
5. All events recorded to CIEU ✅

---

## Files Modified

1. **tests/test_governance_pipeline_e2e.py**
   - 4 test fixes: changed overdue time from 10s to 40s
   - Added explanatory comments about grace period

2. **ystar/governance/intervention_engine.py** (from previous fix)
   - Obligation fulfillment now prioritized before identity check

3. **ystar/governance/intervention_models.py** (from previous fix)
   - Added `GateCheckResult.reason` property for backward compatibility

4. **ystar/governance/omission_store.py** (from previous fix)
   - `update_obligation()` now updates `due_at`, `grace_period_secs`, `hard_overdue_secs`

---

## Impact Assessment

### Immediate
- ✅ PyPI 0.48.0 release is unblocked
- ✅ Full governance pipeline test coverage verified
- ✅ Grace period semantics now tested correctly

### Systemic Insights
This revealed a subtle but important design constraint: **all governance tests must account for grace periods when testing violation detection**. 

The two-stage timeout system (PENDING → SOFT_OVERDUE → HARD_OVERDUE) is working as designed:
1. `due_at`: Target completion time
2. `effective_due_at`: `due_at + grace_period` (when violation actually occurs)
3. `hard_overdue_threshold`: `effective_due_at + hard_overdue_secs` (when severity escalates)

This grace period design is constitutional - it prevents false violations during normal latency variations.

---

## Recommendations

1. **Documentation**: Add a test writing guide explaining grace period semantics
2. **Test Utilities**: Create a helper function `make_overdue(obligation, margin_secs=10)` that automatically accounts for grace period
3. **Validation**: Consider adding a test invariant checker that warns if test deadlines are within grace period

---

## Constitutional Thinking

**What system failure does this reveal?**
- Test infrastructure didn't make grace period semantics obvious
- Easy to write tests that appear correct but test the wrong thing

**Where else could the same failure exist?**
- Any other tests that manually manipulate `due_at` might have the same issue
- Production code that computes deadlines might not account for grace periods

**Who should have caught this?**
- Test framework should have helper utilities for deadline manipulation
- Code review should have caught the grace period oversight

**Prevention strategy:**
- ✅ Implemented: Fixed all 4 tests with clear comments
- TODO: Create `test_utils.py` with `make_overdue()` helper
- TODO: Add grace period section to testing guide

---

**Status:** Ready for PyPI 0.48.0 release
