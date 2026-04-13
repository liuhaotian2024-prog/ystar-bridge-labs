# AMENDMENT-015: Systemic Self-Lock Root-Cause Audit

**Authority**: Board 2026-04-13
**Owner**: Ethan-CTO (lead) → Ryan-Platform + Maya-Governance + Leo-Kernel
**Scope**: gov-mcp repo + Y*gov repo 双仓联合审计 + 改造
**Deadline**: 设计 doc EOD 2026-04-14，patch set EOD 2026-04-16
**Motivation**: 本 session 24h 内暴露 5+ 自锁模式，每一个产品化后会复现在用户端

## 问题陈述

Y*gov + gov-mcp 的权限/身份/state 三层形成**循环依赖**：
- 锁 A（active_agent restricted_write_paths）需要角色 X
- 切到角色 X 需要写 .ystar_active_agent
- 写 .ystar_active_agent 又需要锁 A 解开

本 session 实测 5 处此类环：

| # | 现场 | 循环依赖 |
|---|------|---------|
| L1 | sub-agent 跑完不 restore active_agent | 无自动归还机制；手工修复需 secretary，但 secretary 无法切入 |
| L2 | Circuit Breaker ARMED 1739 | intent_declaration 形式缺失触发；reset 需 CEO/CTO MCP grant，Platform 修 prefix 时自己也撞 |
| L3 | hook daemon 缓存 vs 文件漂移 | 文件改了 daemon 不重读；重启 daemon 又需要当前身份对 |
| L4 | Sub-agent ritual online check | contract 要求 4 并行，Sofia-CMO subagent 不存在；即使存在，sub-agent 在一句话 ping 场景集体失效（身份穿透/早退/截断） |
| L5 | restricted_write_paths 与 role switch 互锁 | priority_brief.md 只能 ceo/secretary 写；CEO 漂移后只能等 Board override |

## 审计任务（Ethan 分派）

### Phase 1: Mapping (Ryan + Leo, 4h)
1. 枚举 gov-mcp 所有 MCP tool 的 permission matrix（tool × role × required_lock）
2. 枚举 Y*gov 所有 restricted_write_paths / immutable_paths / agent_role_gates
3. 画依赖图：每条权限规则的 precondition → 是否自洽 / 有无环
4. 输出 `reports/lock_dependency_graph_20260413.md`

### Phase 2: Root-Cause Taxonomy (Maya, 2h)
对 Phase 1 找到的每个环：
- 归类：本质安全需要 vs 过度防御 vs 历史遗留
- 标注：修复它是否引入新漏洞
- 输出 `reports/lock_cycles_taxonomy_20260413.md`

### Phase 3: 架构设计 (Ethan, 6h)
基于 Phase 1+2，设计改造方案：
- **身份层**：单 source of truth（.ystar_active_agent 还是内存态？谁 owner？sub-agent 切身份的语义是 shadow 还是 transfer？）
- **权限层**：引入 capability-based delegation 替代角色白名单（用户可自定义 role，不预设）
- **自恢复层**：sub-agent 退出时 auto-restore caller；daemon 文件 watcher 代替缓存
- **用户逃生层**：强制 safe-mode 快捷命令（`ystar safemode` 绕过所有 role check 单次修 state）
- 输出 `reports/amendment_015_design_20260413.md` (6-pager 格式)

### Phase 4: Patch set (Leo kernel + Ryan platform + Maya governance, 8h)
- gov-mcp: 改造 MCP tool permission 注册接口
- Y*gov: 改造 hook daemon state 读取（watcher 代替缓存）+ role_gate → capability_gate 迁移
- 新增：`ystar safemode` CLI + MCP `gov_safemode` tool
- 测试：每个 lock cycle 写一个 red-team 测试（模拟用户撞环）

### Phase 5: 红队验证 (Ethan, 2h)
- 20 个用户场景模拟：装包 → 切角色 → sub-agent → 回 CEO → 撞锁 → 自恢复
- Accept: 0 cycle 需要"Board shell override"

## Reporting
每 phase 完一个写一条到 `reports/amendment_015_progress.md`。总 deadline EOD 2026-04-16 完整 patch set commit。

## 产品化指标
- **用户 MTTR < 60s**：撞任何一个锁到自己恢复 < 60 秒
- **零 Board shell override**：所有锁有用户可达的逃生路径
- **测试覆盖**：20 red-team 场景 100% pass
