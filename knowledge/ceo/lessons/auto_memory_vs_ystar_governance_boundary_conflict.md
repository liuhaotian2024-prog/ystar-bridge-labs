---
lesson_id: 98d46e72-bf03-448e-ac99-392af3842a4d
---

# Lesson: auto-memory 系统与 Y*gov 治理的边界冲突

**发现日期**: 2026-04-12
**触发**: CEO 尝试写 feedback memory 到 `~/.claude/projects/.../memory/` → Y*gov hook DENY（不在 CEO allowed write paths）

## 现象

Claude Code harness 提供 auto-memory 系统，路径在 `~/.claude/projects/<project_hash>/memory/`，按规范应写入 user/feedback/project/reference 四类 memory 文件。

Y*gov hook 的 CEO write boundary 只允许：
- `./reports/`
- `./BOARD_PENDING.md`, `./DISPATCH.md`, `./OKR.md`, `./DIRECTIVE_TRACKER.md`, `./OPERATIONS.md`, `./WEEKLY_CYCLE.md`
- `./knowledge/`

**冲突**: auto-memory 路径不在白名单 → CEO 想存 feedback memory 时被 deny。

## 根因

两个 memory 系统设计目标不同：
- **auto-memory (harness 层)**: Claude Code 框架内置，重启后自动加载到 prompt
- **Y*gov memory (产品层)**: `.ystar_memory.db` + `knowledge/{role}/`，由 CEO/Secretary 维护，受 hook 治理

但**没人决定过两个系统怎么协同**：
- harness 默认 agent 自由写 `~/.claude/...`
- Y*gov 默认所有非白名单路径都 deny

## 临时绕行

把 feedback/project/lesson 写到 `knowledge/ceo/feedback/`、`knowledge/ceo/decisions/`、`knowledge/ceo/lessons/`（CEO 允许路径）。

代价：不进入 Claude harness auto-memory 自动加载链——下次 session 启动 prompt 不会自动包含这些 memory，要靠 governance_boot.sh 主动 surface。

## 该怎么修（待 L3 提案）

两个方向，二选一：

**方向 A**: 把 `~/.claude/projects/<project_hash>/memory/` 加入 CEO（以及全员）allowed write paths
- 利：不破坏 harness auto-memory 流程
- 弊：把治理边界打穿到用户 home 目录，跨 workspace 风险

**方向 B**: 在 governance_boot.sh 增加一步，把 `knowledge/{role}/` 下的 feedback/decisions/lessons 同步生成 `~/.claude/.../memory/*.md` 索引
- 利：保持治理边界严格
- 弊：双写，需保持一致性

**推荐**: B（保边界，加同步），属"团队 + 治理关系整理" L2 任务的一部分（`reports/proposals/team_governance_relationship_integration_l2.md`）。

## 关联

- `reports/proposals/team_governance_relationship_integration_l2.md`
- `governance/INTERNAL_GOVERNANCE.md` (boundary 定义)
- AMENDMENT-004（路径正名相关）
