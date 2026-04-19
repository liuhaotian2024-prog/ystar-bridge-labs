---
name: Layer 3 Verification Service — CZL-164 三层方案 Phase 1
type: strategy
created: 2026-04-17
source: CTO CZL-164 hallucination root cause analysis
status: SPEC (待 CTO review + 实施)
based_on: research into chaos_engineering, SRE, quality_gates, dogfooding theories
audience: CTO (Ethan) for implementation
---

# Verification Service v1 — 独立于 sub-agent 自报的验证层

## 问题

Sub-agent 说"完成了" → CEO 只能选择信或不信。
当前验证 = CEO 手动 ls/wc/pytest → 不可扩展。
CZL-164 诊断: 系统奖励"关闭任务"胜过"诚实汇报" → 需要独立验证。

## 设计原则

1. **Executor ≠ Validator** — 执行者不能给自己打分
2. **Automated** — 不依赖 CEO 记得去验证
3. **Structural** — hook-level 或 post-task-notification 自动触发
4. **Proportional** — 验证深度匹配任务重要性

## 验证层级

| 任务类型 | 验证级别 | 自动化 |
|---------|---------|--------|
| Write/Edit 文件 | L1: 文件存在 + 非空 + wc 行数合理 | ✅ 可自动 |
| 代码修改 | L2: L1 + pytest 通过 | ✅ 可自动 |
| 架构设计 | L3: L2 + CEO review | ⚠️ 半自动 |
| 外部发布 | L4: L3 + Board 批准 | 手动 |

## 实现方案 (CTO 实施)

在 PostToolUse hook 或 task-notification handler 中:

```python
def auto_verify(task_receipt):
    """Post-receipt automatic verification."""
    claimed_files = extract_file_paths(task_receipt)
    results = []
    for f in claimed_files:
        exists = os.path.exists(f)
        lines = count_lines(f) if exists else 0
        results.append({
            "file": f, "exists": exists, "lines": lines,
            "verdict": "PASS" if exists and lines > 0 else "FAIL"
        })
    
    all_pass = all(r["verdict"] == "PASS" for r in results)
    if not all_pass:
        emit_cieu("RECEIPT_VERIFICATION_FAILED", results)
    return results
```

## 与现有系统的集成

- Gate 2 receipt validator 已有 artifact extraction → 扩展为 auto-verify
- CIEU event: RECEIPT_VERIFICATION_FAILED 触发 K9 routing → CEO alert
- ForgetGuard: 新规则 `receipt_unverified_auto` → 48h dry-run

## 不做什么

- 不替代 CEO 判断力 (L3/L4 仍需人工)
- 不惩罚诚实失败 (CZL-164 Lesson: 奖励 TASK_EXCEEDS_CAPABILITY)
- 不增加 sub-agent 负担 (验证在 agent 外部运行)
