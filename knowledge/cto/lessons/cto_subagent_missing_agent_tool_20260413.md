---
name: CTO subagent 缺 Agent tool 物理派不了人
type: lesson / architecture-bug
created: 2026-04-13
severity: high
trigger: A023 ship 后第一次真要求 CTO 分派 CMO，Ethan-CTO subagent 报 "No Agent tool in CTO toolset"
lesson_id: eace160b-4c3d-4d50-97a7-74c9c3576b11
---

# Bug 描述

`.claude/agents/cto.md` frontmatter 没显式 `allowedTools: [Agent, ...]`。Claude Code subagent 系统在 sub-agent 内默认禁用 Agent tool 防止递归 spawn。结果：CTO 收到 "你统筹分派 Maya/Ryan" 的指令时，物理上无法执行——只能 (a) emergency 自己干（违反 must_dispatch_via_cto 精神）或 (b) 把任务卡写好但派不下去。

# 实战影响

- A023 (Article 11 enforcement) Ethan emergency 自己干，没真分派 Ryan/Maya（虽然交付完成，但绕过流程）
- A023 v4 视频任务 Ethan 写完 task card 然后报 "No Agent tool"，Board 已说 "看来我们真在裸奔"
- **must_dispatch_via_cto** 治理规则物理不可执行 = 假规则

# 错失成本

每次 CEO 需要"分派给某岗位"就只能 (a) 自己派 (越权违反规则) 或 (b) 派 Ethan 然后 Ethan 也派不下去 → 螺旋形 dispatch 失败。Board 反复 frustrated。

# 修复路径

`.claude/agents/cto.md` 加 `allowedTools` 明确含 `Agent`：
```yaml
allowedTools: [Read, Glob, Grep, Write, Edit, Bash, Agent]
```

或更精细：
```yaml
allowedTools:
  - Read
  - Glob  
  - Grep
  - Write
  - Edit
  - Bash
  - Agent  # critical for orchestration
disallowedTools: [WebFetch]
```

**风险**：递归 spawn 失控（CTO 派 CMO，CMO 派 X，无限层）。Mitigation: `maxTurns: 40` 已限单 sub-agent 转数；可加 `maxSubagentDepth: 2` 如 Claude Code 支持。

# 对所有 C-suite agents 检查

同样可能影响 CMO / CSO / CFO / Secretary。每个 C-suite 应能往下派工程师子 agent。需全员 audit allowedTools。

# 元教训

任何 "X 必经 Y" 治理规则部署前，**必须验证 Y 物理上能 do X**。否则规则是空架子，每次触发都 fallback 到违规行为。
