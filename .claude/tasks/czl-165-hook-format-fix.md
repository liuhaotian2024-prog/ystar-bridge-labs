# CZL-165 — hook.py 输出格式 + 异常 logging 修复

**Priority**: P0
**Assigned**: Ryan Park (eng-platform)
**Deadline**: ≤15 tool_uses
**Scope**: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/hook.py`

## 修复 A: 5 处输出格式错误

Lines **198, 618, 885, 961, 997** 返回错误格式：
```python
{"action": "block", "message": "..."}
```

**正确格式 (OpenClaw PreToolUse spec)**:
```python
{
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "...",
        "violations": [...]  # 如果原有
    }
}
```

搜索所有 `"action": "block"` 返回语句，全部替换为正确格式。保留 violations 字段如果原有。

## 修复 B: 8 处 bare except 缺 logging

Lines **611, 654, 1056, 1329, 1334, 1388, 1461, 1592** 有 `except Exception:` 但无 logging。

每个加：
```python
except Exception as e:
    _log.warning("[HOOK-ERROR] {context}: %s", e)
    pass
```

其中 `{context}` 说明功能路径 (例: `"Bash command content scan"`, `"LESSON_READ tracking"`, `"session config cache fallback"`)。

## 验证

```bash
cd /Users/haotianliu/.openclaw/workspace/Y-star-gov
python3 -m pytest tests/ -k "hook" -q --tb=short
```

确认 0 new failures。

## 约束

- **禁止 git commit/push/add**
- ≤15 tool_uses
- 只改这 13 处，不扩散

---
CEO dispatch: 2026-04-17 CZL-165 → Ryan (eng-platform, adapters/ owner)
