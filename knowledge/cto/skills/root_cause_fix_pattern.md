# Root Cause Fix Pattern

## When to Use This

**Trigger**: You are about to edit Python code to fix a bug, resolve a test failure, or patch unexpected behavior.

**Mandatory for**:
- Any code change in Y*gov source (`/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/`)
- Test failures (regressions, new test cases failing)
- Bug reports from Board or CIEU audit
- "Quick fixes" (especially these — shortcuts accumulate technical debt)

**NOT required for**:
- New feature development (greenfield code with tests)
- Documentation updates
- Refactoring with 100% test coverage

---

## Core Pattern

Every bug fix must follow **5-step root cause discipline**:

### Step 1: Symptom vs. Root Cause
**DO NOT** fix the symptom. Find the root cause.

- **Symptom**: "Test X is failing"
- **Root cause**: "Function Y doesn't validate input Z"

**How to find root cause**:
1. Reproduce the bug locally (`pytest -xvs tests/test_X.py::test_Y`)
2. Add print statements / breakpoints to trace execution
3. Ask: "Why did this pass before?" (check git blame, recent commits)
4. Ask: "What assumption broke?" (input changed? dependency updated?)

**Output**: Write one sentence root cause to commit message.

### Step 2: Blast Radius Analysis
**Before fixing**, ask: "Where else does this bug exist?"

- Same bug pattern in other files?
- Same vulnerable assumption in related functions?
- Same missing validation in sibling code paths?

**How to check blast radius**:
```bash
# Search for similar patterns
grep -r "pattern_that_caused_bug" ystar/

# Check all callers of buggy function
grep -r "buggy_function_name" ystar/ tests/
```

**Output**: List all affected locations (fix them ALL, not just the reported one).

### Step 3: Prevention Action
**After fixing**, ask: "How do we prevent this class of bug from recurring?"

**Prevention options** (pick at least one):
- Add type hints (if bug was type confusion)
- Add input validation (if bug was bad data)
- Add assertion / guard clause (if bug was violated invariant)
- Add regression test (if bug was untested edge case)
- Add docstring warning (if bug was API misuse)
- Refactor to make bug impossible (best option)

**Output**: Document prevention action in commit message.

### Step 4: Test Coverage Verification
**Every fix MUST have a test** that:
1. Reproduces the original bug (test fails on old code)
2. Passes on fixed code
3. Will catch regressions if someone breaks it again

**How to verify**:
```bash
# Checkout old code (before fix)
git stash
# Run new test (should fail)
pytest tests/test_new_regression.py
# Restore fix
git stash pop
# Run test again (should pass)
pytest tests/test_new_regression.py
```

**Output**: Test file path in commit message.

### Step 5: CIEU Audit Trail
**After committing**, check CIEU for related violations.

**Why**: Bug fixes often correlate with governance violations. If you're fixing "function doesn't validate input", check CIEU for "action allowed without validation" events.

**How to check**:
```python
from ystar.kernel.cieu import CIEUDatabase

db = CIEUDatabase()
recent = db.query_recent(hours=24, event_type="policy_violation")
for event in recent:
    if "validation" in event.reason.lower():
        print(f"Related CIEU event: {event.event_id}")
```

**Output**: If CIEU reveals pattern, file `reports/cieu_insights/bug_X_governance_correlation.md`.

---

## Common Mistakes

1. **Fixing symptom, not cause**: changing test assertion instead of fixing buggy code.
   - Fix: If your "fix" involves updating expected test output, you're doing it wrong.

2. **Narrow fix (missed blast radius)**: fixing one occurrence, leaving 5 others.
   - Fix: Always grep for the bug pattern across entire codebase.

3. **No prevention**: fixing the bug but not preventing recurrence.
   - Fix: Every fix should make the codebase MORE robust, not just pass tests.

4. **Skipping test**: "it's a tiny fix, doesn't need a test."
   - Fix: Tiny fixes regress. No test = no confidence. Board mandate: ALWAYS test.

5. **Committing without running ALL tests**: "I only changed one file, don't need full suite."
   - Fix: Run `pytest --tb=short -q` before EVERY commit. Regressions are expensive.

---

## Example

**Bug Report**: `test_behavior_rules.py::test_autonomous_mission_article11_required` failing.

### Step 1: Root Cause
**Symptom**: Test expects DENY for autonomous mission without Article 11, but hook returns ALLOW.

**Investigation**:
```bash
pytest -xvs tests/test_behavior_rules.py::test_autonomous_mission_article11_required
# Trace shows: boundary_enforcer._check_behavior_rules() not detecting "autonomous mission" keyword
```

**Root Cause**: Detection regex in `boundary_enforcer.py` checks for "autonomous_mission" (underscore) but agent writes "autonomous mission" (space). Regex needs to handle both.

### Step 2: Blast Radius
```bash
grep -r "autonomous_mission" ystar/adapters/
# Found: activation_triggers.py also uses same narrow pattern
```

**Blast radius**: 2 files affected (boundary_enforcer.py + activation_triggers.py).

### Step 3: Prevention
**Fix**: Update regex to `r"autonomous[_\s]mission"` (matches both underscore and space).

**Prevention**: Add docstring to `_detect_autonomous_mission()` explaining keyword variations. Add test case for both formats.

### Step 4: Test Coverage
**New test**:
```python
def test_autonomous_mission_space_vs_underscore():
    """Regression: both 'autonomous mission' and 'autonomous_mission' should trigger."""
    # Test space version
    result1 = policy.check("ceo", "write", content="I declare autonomous mission to build X")
    assert not result1.allowed  # should DENY without Article 11

    # Test underscore version
    result2 = policy.check("ceo", "write", content="autonomous_mission: build X")
    assert not result2.allowed
```

**Verification**:
```bash
git stash  # revert to buggy code
pytest tests/test_behavior_rules.py::test_autonomous_mission_space_vs_underscore
# FAIL (as expected)
git stash pop  # restore fix
pytest tests/test_behavior_rules.py::test_autonomous_mission_space_vs_underscore
# PASS
```

### Step 5: CIEU Audit
```python
# Check recent CIEU for autonomous mission declarations that weren't caught
db = CIEUDatabase()
recent = db.query_recent(hours=168, event_type="external_observation")  # last week
for event in recent:
    if "autonomous" in str(event.params).lower():
        if event.decision == "allow":  # should have been DENY
            print(f"Missed violation: {event.event_id} at {event.timestamp}")
```

**Finding**: 3 instances where CEO declared autonomous missions with space format, all incorrectly allowed. Filed `reports/cieu_insights/autonomous_mission_regex_gap.md`.

### Commit Message
```
fix: autonomous mission detection handles space/underscore variants

Root cause: regex matched "autonomous_mission" but not "autonomous mission"
Blast radius: boundary_enforcer.py + activation_triggers.py
Prevention: updated regex to r"autonomous[_\s]mission", added docstring
Test: test_autonomous_mission_space_vs_underscore (regression coverage)
CIEU: 3 historical false-allows, filed cieu_insights report

Fixes test_behavior_rules.py::test_autonomous_mission_article11_required
```

---

**CTO Iron Law**: No bug fix without prevention action. Every fix should make the system stronger, not just pass tests.

If your commit message doesn't mention blast radius + prevention + test, it's not a complete fix.
