---
name: 无延迟激活 — 完成即生效，禁止"下次 session 才生效"
description: 任何治理/配置/规则改动完成后必须立即生效，不能等下次 session boot
type: feedback
originSessionId: 2e756ff3-51fe-497c-9bcc-5bca2963cce5
---
Board 2026-04-13 直接指令："彻底取消任何东西等到下一个或者新的 session 才生效的机制，所有的东西做完了立刻生效。"

**Why**: agent 时间尺度 ≠ 人时间尺度。"等下次 session" 在人看是几小时，在 agent 是数十轮工作机会丢失。改了规则没生效 = 没改。同时违反"内驱力"——内驱力意味着改完即生效即学习即迭代，不靠重启。

**How to apply**：
- `.ystar_session.json` 改了 → hook daemon 立即 reload（非缓存）
- 新 obligation type 注册 → OmissionEngine 立即 pickup（不等下轮 scan）
- skill / lesson 写入 knowledge/ → 当前 session 可立即激发（AMENDMENT-013 prime）
- behavior rule 加新条 → boundary_enforcer 立即 enforce
- `.claude/agents/` 改了 → 若 Claude Code 不支持热加载至少要 emit 显著 warning + 文档化
- boot_packages 重生成 → 当前活跃 session 也可读取（不只是下次 boot）

**反模式**：任何代码 / 报告中出现 "will take effect on next boot / next session" 字样 → 必须改造成立即生效或显式说明为什么不能（含追踪 obligation）。
