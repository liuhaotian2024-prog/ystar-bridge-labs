# CZL-163C: Kernel CZL Protocol Validation Logic

**Engineer**: Leo Chen (eng-kernel)
**Priority**: P0
**Estimated tool_uses**: 10

## Context
`tests/kernel/test_czl_protocol.py` 有 4 个 validation tests 失败,因为 `validate_dispatch()` 返回空列表 — validation logic 未实现或未调用。

Failed tests:
1. `test_validate_dispatch_missing_y_star` — 缺 Y* 应报错
2. `test_validate_dispatch_xt_speculation_markers` — Xt 含"印象中/应该"等推测词应报错
3. `test_validate_dispatch_u_exceeds_atomic_limit` — U 估计 >15 tool_uses 应报错
4. `test_validate_dispatch_missing_recipient` — 缺 recipient 应 warning

## Task
Find `validate_dispatch()` 函数实现(likely in `ystar/kernel/` 或 `ystar/governance/czl_protocol.py`),实现 4 个 validation gates:

### Gate 1: 5-tuple completeness
- 所有 5 个字段 (Y*, Xt, U, Yt+1, Rt+1) 必须存在
- Regex pattern: `\*\*Y\*\*:`, `\*\*Xt\*\*:`, etc.

### Gate 2: Xt speculation markers
Chinese: "印象中", "应该", "可能", "估计"
English: "probably", "might", "seems like", "I think"
Any match → append issue

### Gate 3: Atomic dispatch limit
U section 包含 ">15 tool" or "20 iterations" or similar → append issue

### Gate 4: Recipient
Prompt 不含 "@{agent}" or "派 {role}" → append warning

## Acceptance Criteria
- [ ] All 4 test cases pass
- [ ] `python3 -m pytest tests/kernel/test_czl_protocol.py::test_validate_dispatch_missing_y_star -v` PASS
- [ ] `python3 -m pytest tests/kernel/test_czl_protocol.py::test_validate_dispatch_xt_speculation_markers -v` PASS
- [ ] `python3 -m pytest tests/kernel/test_czl_protocol.py::test_validate_dispatch_u_exceeds_atomic_limit -v` PASS
- [ ] `python3 -m pytest tests/kernel/test_czl_protocol.py::test_validate_dispatch_missing_recipient -v` PASS
- [ ] No other tests broken
- [ ] **NO git commit/push/add**

## Files in scope
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/czl_protocol.py` (likely location)
- or `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/czl_protocol.py`

## Boot Context
Read this task card + `cd /Users/haotianliu/.openclaw/workspace/Y-star-gov && git log --oneline -10`.
