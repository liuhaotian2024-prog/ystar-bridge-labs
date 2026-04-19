---
name: Hook Output Format — shipped ≠ live 的第三层
type: paradigm
discovered: 2026-04-17
trigger: CEO enforcement hook 3 轮 pressure test 全 fail → 根因是 Claude Code 输出格式
depth: operational
principles: [P-2, P-6, P-7]
---

## 发现

我们所有 hook 的 block 输出都是错的。

错: `{"action": "block", "message": "..."}`
对: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}`

这意味着我们之前认为"已 LIVE"的所有 block hook，实际上从来没有真正 block 过任何东西。

## shipped ≠ live 的三层

1. 代码存在 ≠ 代码执行 (wiring gap — hook_wrapper.py 不在 FAST PATH)
2. 代码执行 ≠ 输出被识别 (format gap — action vs permissionDecision)
3. 输出被识别 ≠ 行为改变 (测试覆盖验证)

CZL-160 修了 Layer 1。格式修复修了 Layer 2。3/3 empirical test 验证了 Layer 3。

## P-7 影响范围

需要全量修复的 hook 输出:
- hook_wrapper.py (CEO code-write prohibition + check_hook 结果 + fail-closed)
- forget_guard.py (deny 输出格式)
- 所有 daemon check_hook 返回的 block 结果
- hook_pretool_agent_dispatch.py (如果有 block 路径)

## P-6 教训

"按现实行动" = 永远 empirical verify。
文档说 A，代码写 A，但现实说 B。只有测试告诉你真相。
