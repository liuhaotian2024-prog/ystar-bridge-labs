---
name: Board shell command marker convention
description: Any command CEO needs Board to run in shell must be prefixed with ❕ marker, visually prominent, with clear return signal
type: feedback
originSessionId: 36ef8c73-06cf-42bb-931e-9a2e522c40d0
---
CEO 向 Board 请求 shell 执行任何命令时，**必须给 Claude Code 对话框可直接粘贴的 `!<command>` 格式**（感叹号前缀），不是普通 bash 代码块。格式：

```
❕ **老大在对话框里粘这一行（前面是感叹号）：**

\`\`\`
!<command>
\`\`\`

❕ 回车即可，输出接回对话。
```

**关键点：** 命令前必须真的是 `!` 字符（不是 ❕ 符号），且代码块语言标签不能写 `bash`（会让 Board 以为要开终端），用纯 fenced block。

**Why:** Board 2026-04-13 纠正。Claude Code 的对话框把 `!` 前缀当内联 bash，输出直接进对话。常规 `\`\`\`bash ... \`\`\`` 代码块只是展示，Board 要开终端才能跑——打断 session flow。用 `!` 形式让 Board 一次回车搞定。

**Why:** Board 2026-04-13 指令。没有标记的命令容易被 Board 当成 CEO 线自己会跑（实际是被 hook 拒后的请求），导致老大漏看、CEO 继续撞墙空转。❕ 是视觉 tripwire。

**How to apply:**
- 所有 restricted-path 写操作（.ystar_active_agent / priority_brief.md / BOARD_PENDING.md）被 hook 拒后的 Board shell 请求
- 所有需要 CEO/CTO MCP grant 但当前身份不够的 gov_* 命令（gov_reset_breaker 等）
- 任何需要老大手动 override 身份锁的场景
- 一次对话里可多条，每条独立标 ❕
- 命令块后必须写一句"执行完回 X 即可"告诉 Board return signal
- 禁止把 shell 命令藏在段落文字里不标记
