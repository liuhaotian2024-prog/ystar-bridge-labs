# Migration Kickoff — 治理团队搬家OpenClaw

**启动时间**: 2026-04-11 23:5x
**Board授权**: "搬家，必须搬家，整个团队搬到open claw上面去" + "明天早上希望看到你们已经搬家结束了"
**执行依据**: reports/governance_team_on_openclaw.md（CTO Ethan plan）
**CEO**: Aiden（本session）盯进度

---

## 老大的睡前承诺（不撒谎）

**今夜可完成**: Phase 1 — CEO agent试点（0.5天工作量）
- openclaw agents add ceo
- 写 ~/.openclaw/agents/ceo/agent/IDENTITY.md（拷贝 .claude/agents/ceo.md persona）
- 更新 openclaw.json maxConcurrent: 6
- 验证 `openclaw agent --agent ceo --local --message "状态汇报" --json` 返回Aiden身份回复

**今夜物理上做不完**:
- Phase 2: CEO驱动Claude Code执行手（1天）
- Phase 3: Secretary改session.json hook（0.5天）
- Phase 4: 全员CTO/CMO/CSO/CFO/Secretary迁移（1天）

**明早老大能验证的**: 一个常驻在OpenClaw上的Aiden，你随时能 `openclaw agent --agent ceo` 调他，他不会失忆。这是真起点。

---

## 执行分工（spawn工程subagent）

- **Ryan Park (eng-platform)**: openclaw agents add + agentDir结构 + bindings配置
- **Leo Chen (eng-kernel)**: IDENTITY.md从 .claude/agents/ceo.md 提取 + agent memory结构
- **CEO (我)**: 进度盯防 + 异常上报BOARD_PENDING + 完成后写交付报告

执行进度实时更新本文件。
