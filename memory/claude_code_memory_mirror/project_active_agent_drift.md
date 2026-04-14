---
name: active_agent identity drift after sub-agent
description: Sub-agent invocation overwrites .ystar_active_agent to sub-agent's role and doesn't restore; CEO line loses write permissions mid-session
type: project
originSessionId: 36ef8c73-06cf-42bb-931e-9a2e522c40d0
---
每次 Agent tool 调 sub-agent（Ethan/Maya/Ryan/Jordan/Leo/...）后，`.ystar_active_agent` 被改成 sub-agent 的角色，永不 restore 回 ceo。后果：CEO 本线后续对 `reports/priority_brief.md`、`.ystar_active_agent` 等 restricted 路径的写操作全部被 hook 拒。无法自救（restore 需 secretary，但切 secretary 也需经过这把锁）。

**Why:** 2026-04-13 现场复现——派 Maya 诊断 → 派 Ryan dispatch → 再 Edit priority_brief.md 时 hook 报 "current agent is 'eng-governance'" 后又变 'eng-platform'。这是 AMENDMENT-009 要修的 escape hatch。

**How to apply:**
- 在 AMENDMENT-009 FIX-3（boot → autonomy）实装之前，任何一轮派完 sub-agent 后 CEO 写权限视为已失效
- 有大批 CEO-restricted 写操作（priority_brief / BOARD_PENDING / .ystar_active_agent）的回合，**先写完再派 sub-agent**，顺序不能反
- 撞墙后不要尝试 workaround（同一把锁所有角色都切不过去），直接请 Board shell 一行 `!echo ceo > .ystar_active_agent`
- **额外陷阱：** 写 `.ystar_active_agent` 回 ceo 后 hook daemon 仍缓存旧角色——必须同时重启 daemon (`!pkill -f _hook_daemon && bash scripts/governance_boot.sh ceo`) 才真正生效。文件层修复 + daemon 重启是双步组合动作。
