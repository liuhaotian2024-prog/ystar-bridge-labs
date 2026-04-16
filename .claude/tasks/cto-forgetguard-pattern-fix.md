## Task: Fix ForgetGuard Pattern Matching + Boot Smoke Test Guard

**Task ID**: CTO-FORGETGUARD-PATTERN-FIX  
**Engineer**: cto (Ethan Wright)  
**Priority**: P1 (blocks boot health verification)  
**Created**: 2026-04-15  
**Status**: pending_ceo_approval

---

### Context

Boot step 8.6 (self-heal smoke test) fails with:
```
AssertionError: ForgetGuard should detect CEO→eng dispatch
```

**Root Cause**: ForgetGuard pattern matching algorithm requires 60% keyword match (11/18 keywords), but test context only matches 4/18 (22%).

**Current Pattern** (forget_guard_rules.yaml):
```
CEO assigns code|git|build|test|pytest|commit task directly to 
eng-kernel|eng-governance|eng-platform|eng-domains without CTO approval
```

**Test Context**:
```python
{
    'agent_id': 'ceo',
    'action_type': 'task_assignment',
    'action_payload': 'fix bug in nl_to_contract.py',
    'target_agent': 'eng-kernel',
}
```

**Search String Built**: `"ceo task_assignment fix bug in nl_to_contract.py eng-kernel"`

**Matched Keywords**: `ceo`, `task`, `to`, `eng-kernel` → 4/18 = 22% < 60% threshold

---

### Acceptance Criteria

- [ ] Rewrite `forget_guard_rules.yaml` pattern to use 5 core keywords
- [ ] Boot step 8.6 smoke test passes with new pattern
- [ ] Smoke test failure emits CIEU event (`BOOT_SMOKE_TEST_FAILURE`)
- [ ] Add `.ystar_boot_failure` flag file creation when `FAILURES > 0`
- [ ] All 86 Y*gov tests still pass
- [ ] Boot script runs clean (zero failures)

---

### Files in Scope

**Y*gov Source**:
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/forget_guard_rules.yaml`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/forget_guard.py`

**Company Scripts**:
- `/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/governance_boot.sh`

---

### Estimated Time: 1-1.5 hours
