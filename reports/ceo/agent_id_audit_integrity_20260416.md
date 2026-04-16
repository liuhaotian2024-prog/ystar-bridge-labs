# Agent ID Audit Integrity — P0 Discovery

**Date**: 2026-04-16 morning
**Owner**: CEO (Aiden)
**Trigger**: Board Q "查不出 CTO 的实际能力、违规、执行等实际问题"
**Status**: DIAGNOSTIC COMPLETE → design + impl phase
**L-tag**: [L0 ESCALATED]

## TL;DR

7 天 91,455 CIEU events 里，**超 54% 没真实角色身份**（'agent' / 'orchestrator' / 'unknown' / '' 四种 fallback 或内部组件 ID 填充）。每个 sub-agent 不是独立可审计主体，导致 Board 级问题"CTO 能力怎么样"无解。

## Raw Data (7d)

| agent_id | count | pct | 性质 |
|---|---|---|---|
| `'agent'` | 16,922 | 18.5% | **generic fallback** ⚠️ |
| `'orchestrator'` | 13,422 | 14.7% | 内部 scheduler |
| `'unknown'` | 10,476 | 11.5% | **明确未知** ⚠️ |
| `''` (空) | 9,004 | 9.8% | **空字符串 bug** ⚠️ |
| `'ceo'` | 7,988 | 8.7% | ✅ 真 CEO |
| `'path_a_agent'` | 4,937 | 5.4% | 内部组件 |
| `'intervention_engine'` | 4,197 | 4.6% | 内部组件 |
| `'cto'` | 3,175 | 3.5% | ✅ 真 CTO |
| `'eng-governance'` | 3,171 | 3.5% | ✅ 真 Maya |
| `'eng-platform'` | 3,073 | 3.4% | ✅ 真 Ryan |
| `'ryan-platform'` | 2,320 | 2.5% | **Ryan 别名** ⚠️ |
| `'secretary'` | 1,857 | 2.0% | ✅ 真 Samantha |
| `'eng-domains'` | 1,774 | 1.9% | ✅ 真 Jordan |
| `'eng-kernel'` | 975 | 1.1% | ✅ 真 Leo |
| `'samantha-secretary'` | 823 | 0.9% | **Samantha 别名** ⚠️ |

## Root Causes

### RC1: 多源 emit 点缺 canonical registry
CIEU 事件来自 daemon / orchestrator / sub-agent / 手动脚本，每种填 agent_id 方式不一致。无强制校验。

### RC2: fallback 默认值污染
当 emit 点拿不到明确身份时，填 `'agent'` / `'unknown'` / `''`。应该 reject 或强制 `_get_current_agent()` fresh read.

### RC3: 角色 ID 别名混用
`ryan-platform` vs `eng-platform`, `samantha-secretary` vs `secretary`, `ethan-cto` vs `cto` — 来自 `.claude/agents/*.md` subagent_type 与内部 role name 不一致。

### RC4: .ystar_active_agent 漂移
Sub-agent 跑完不自动 restore 父级身份（memory feedback `active_agent_drift` 已记录）. AMENDMENT-016 v2 daemon stateless fix 只解了 daemon 缓存，没解 `.ystar_active_agent` 文件漂移.

## Design Fix

### F1: Canonical agent_id registry (新文件)
`governance/agent_id_canonical.json` — 列 10 合法 ID: `ceo / cto / cmo / cso / cfo / eng-kernel / eng-governance / eng-platform / eng-domains / secretary`.

### F2: Emit-side 强制校验
所有 CIEU emit 入口（`_get_current_agent()` 或等价）必须：
- Read `.ystar_active_agent`
- 对照 registry，不在白名单 → 写 `'unknown_caller'` + 记告警 CIEU event
- 禁用 `'agent'` / `''` / `'unknown'` 默认值

### F3: Sub-agent 身份 handshake
派 sub-agent 时：
- Spawn 前 CEO 保存当前 `.ystar_active_agent` 到 stack
- Sub-agent boot 时（boot_prompt_template 注入）设 `.ystar_active_agent = <role>`
- Sub-agent exit 时 CEO 从 stack pop restore

### F4: 历史数据 migration
一次性 UPDATE:
- `ryan-platform` → `eng-platform`
- `samantha-secretary` → `secretary`
- `ethan-cto` → `cto`
- 内部组件 (`orchestrator` / `path_a_agent` / `intervention_engine`) 保留但明确标为 `system:*` 前缀，区分人类角色 vs 系统组件

### F5: Audit query rebuild
`twin_report.py` + `k9_audit_v3.py` 改查：
- 只 aggregate `agent_id IN registry` 的 events（忽略 `system:*`）
- 按真实角色出 KPI：CTO 决策数 / 违规率 / 任务完成率

## Priority & Sequencing

**P0 (本周)**：F1 + F4（registry + 历史 migration）— 立即让过去数据可查
**P1 (下周)**：F2 + F3（emit-side + handshake）— 让未来数据干净
**P2 (backlog)**：F5（audit query rebuild）— 把 KPI dashboard 接上

## 与 30-day plan 关系

**非 blocking but critical**：30-day Plugin 产品本身可以先跑，因为 runtime enforcement（forget_guard / Stop hook / Engineering Boundary）照样拦真违规。但**对外 demo / 对内管理** 需要 CTO KPI 真能查，所以 F1 + F4 应 Day 8 前上。Ethan Day 2 照跑不干扰。

## 派工

- **Ryan**: F1 + F4 (migration plan + data backfill) — spec + SQL 脚本，CEO 批后执行
- **Ethan**: F2 + F3 (daemon + handshake) — Day 2 后并入 Plugin 打磨阶段
- **Samantha**: 归档本 report + follow-up meeting 纪要

## Rt+1 zero 条件

- `agent_id IN (unknown_family)` 比例 < 5%（目前 54%）
- 10 合法角色 ID 各占比清晰可查
- CTO KPI dashboard 真能出一张表

---

**Board 看到这条 = 我们的 audit integrity 2 天前的基础从未验证过，现在验证了 bug 比想象大。30-day plan 不受影响继续跑，audit fix 并线推。**
