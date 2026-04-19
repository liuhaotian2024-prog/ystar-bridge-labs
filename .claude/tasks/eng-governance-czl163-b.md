# CZL-163B: Reply Taxonomy Length Validation

**Engineer**: Maya Patel (eng-governance)
**Priority**: P1
**Estimated tool_uses**: 8

## Context
`tests/governance/test_reply_taxonomy.py` 有 2 个长度检查 tests 失败:
1. `test_query_too_long` — [QUERY] >120 chars 应 invalid
2. `test_ack_too_long` — [ACK] >30 chars 应 invalid

目前 `validate_template(tag, reply)` 不检查长度,返回 `is_valid=True`。

## Task
Find `validate_template()` 函数 (likely in `ystar/governance/reply_taxonomy.py` 或类似文件),添加长度验证:

### Template Rules
- `[QUERY]`: 整个 reply 长度 ≤ 120 chars
- `[ACK]`: 整个 reply 长度 ≤ 30 chars
- Other tags (DISPATCH, RECEIPT, NOTIFICATION): no length limit

### Implementation
在 `validate_template()` 中添加:
```python
if tag == "QUERY" and len(reply) > 120:
    errors.append("QUERY exceeds 120 character limit")
    is_valid = False
if tag == "ACK" and len(reply) > 30:
    errors.append("ACK exceeds 30 character limit")
    is_valid = False
```

## Acceptance Criteria
- [ ] `python3 -m pytest tests/governance/test_reply_taxonomy.py::test_query_too_long -v` PASS
- [ ] `python3 -m pytest tests/governance/test_reply_taxonomy.py::test_ack_too_long -v` PASS
- [ ] All 13 other tests in `test_reply_taxonomy.py` still PASS
- [ ] No files outside scope modified
- [ ] **NO git commit/push/add**

## Files in scope
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/reply_taxonomy.py` (likely location)

## Boot Context
Read this task card + `cd /Users/haotianliu/.openclaw/workspace/Y-star-gov && git log --oneline -10`.
