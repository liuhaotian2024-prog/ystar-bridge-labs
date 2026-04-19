# CZL-163A: Hook Output Format Compliance

**Engineer**: Leo Chen (eng-kernel)
**Priority**: P0
**Estimated tool_uses**: 12

## Context
hook.py 有 5 处返回 bare `{"action":"block","message":"..."}` 格式，违反 OpenClaw canonical hook output schema。同时 8 处 bare `except Exception:` 违反 Vogels "everything fails" 原则 — fail-open path 必须有 context logging。

## Task
修复 `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/hook.py`:

### Part 1: Hook Output Format (5 fixes)
Lines 198, 618, 885, 961, 997 — 替换所有 bare `{"action":"block"}` returns 为 canonical format:
```python
{
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",  # or PostToolUse depending on context
        "permissionDecision": "deny",
        "permissionDecisionReason": message  # existing message variable
    }
}
```

### Part 2: Bare Exception Handlers (8 fixes)
Lines 611, 654, 1056, 1329, 1334, 1388, 1461, 1592 — 所有 bare `except Exception: pass` 改为:
```python
except Exception as e:
    _log.warning("Fail-open: [context] %s", e)
```
每个 context 明确说明哪个 subsystem (e.g., "LESSON_READ emit", "Omission setup", "Orchestrator feed")。

## Acceptance Criteria
- [ ] 所有 5 处返回 canonical hook output structure
- [ ] 所有 8 处 except 有 warning log with context
- [ ] `python3 -m pytest tests/adapters/hooks/ -v` pass
- [ ] No files outside `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/hook.py` modified
- [ ] **NO git commit/push/add**

## Files in scope
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/hook.py`

## Boot Context
Read this task card + `cd /Users/haotianliu/.openclaw/workspace/Y-star-gov && git log --oneline -10`.
