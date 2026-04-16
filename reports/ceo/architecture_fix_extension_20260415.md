# Architecture Fix Campaign Extension — W26-W28 K9 Audit v3

**Date**: 2026-04-15 night (late)
**Status**: Board 批准 (2026-04-15 night)
**Builds on**: W20-W25 Sub-Agent Reliability Architecture Fix

## 为什么扩展

Board 给 K9 Audit 3-layer 方案（Liveness / Causal Chain / Invariant）是**通用 governance audit 方法论升级**——不只修 sub-agent reliability，是整个"章程→规则→引擎→hook→sub-agent→audit"治理 stack 的最后一块。

W20-W25 修 sub-agent 可靠性（dispatch 层）。
W26-W28 修 audit 方法（verification 层）。

## W26-W28 定义

### W26: k9_audit_v3.py 实现（Maya/Ryan，≤15 tool_uses）
- 通用 3 函数：`check_component_liveness` / `check_causal_chain` / `check_invariant`
- `run_all_liveness_checks`：5 组件（hook_chain / OmissionEngine / ForgetGuard / Intent / RLE）
- `run_all_chain_checks`：4 业务流程（Board 指令 / ForgetGuard 拦截 / CZL 收敛 / 义务履行）
- `run_all_invariant_checks`：5 不变式（指令失败必记录 / 义务不悬空 / 升级必 Board 响应 / Gap 必处理 / Hook 启动必有治理动作）

### W27: CIEU event_type taxonomy（Samantha 文档 + Maya 代码，≤12 tool_uses）
- 写 `governance/cieu_event_taxonomy.md` 列出所有 canonical event_type + 命名规范
- 审计当前 ~20 种混乱命名（DEFER_LANGUAGE_DRIFT / BEHAVIOR_RULE_VIOLATION / FORGET_GUARD / WIRE_BROKEN 等）
- emit 代码 migrate 到 canonical 名字
- 兼容层保留 30 天旧名字 → new 名字

### W28: k9_audit_v3 cron + 替代 wire_integrity_check_v2 主 audit（Ryan，≤10 tool_uses）
- `crontab 0 */6 * * *` 跑 k9_audit_v3
- wire_integrity_check_v2 保留作 **schema-level check**（hook 注册 / 治理文件 / 包配置）
- k9_audit_v3 作 **behavior-level check**（CIEU event 有无 / 因果链 / 不变式）
- 两者并列 cron，不互相取代——schema + behavior 双维度 audit

## 我批评方案的 4 点（已采纳入实施）

1. **CIEU event_type 归一化**（W27 专攻）
2. **时间窗口自适应**（W26 impl 时 per-组件 config，不一刀切）
3. **跨 session 关联用 `task_id` / `obligation_id`**（不只 session_id）
4. **Causal chain 配对用 `seq_global` 或唯一关联 ID**（不只 MAX timestamp）

## Campaign Timeline

| 完成顺序 | Campaign | 预计 tool_uses | Owner |
|---|---|---|---|
| 1 | W20 atomic dispatch doctrine | 7 ✅ | Samantha |
| 2 | W21 increment commit rule | 5 ✅ | Maya |
| 3 | W22 sub-agent boot prompt | 2 ✅ | Samantha |
| 4 | W21.5 CTO team permission | 5 ✅ | Ethan |
| 5 | W23 daemon stateless | ~15 | Maya (跑中) |
| 6 | W24 CEO prompt 自检 + AGENTS.md | ~6 | Samantha |
| 7 | W25 CEO mid-stream SendMessage 协议 | ~10 | Maya |
| 8 | W26 k9_audit_v3 impl | ~15 | Maya/Ryan |
| 9 | W27 CIEU event_type taxonomy | ~12 | Samantha + Maya |
| 10 | W28 k9_audit_v3 cron + 替代 | ~10 | Ryan |

**Total est**: 87 tool_uses across 10 atomic dispatches
**Pre-atomic baseline**: 1 Ethan #5 dispatch 47 tool_uses truncated 0 ship
**Atomic gain**: 同样 tool 成本 → 10 件 ship

## 完整 Governance Stack 闭环

W20-W28 ship 完后：
```
Layer 1 — Doctrine (AGENTS.md IRON RULE 0/0.5 + Session Y* + Three-Layer)
  ↓
Layer 2 — Rule engine (forget_guard.py + 15+ rules)
  ↓
Layer 3 — Dispatch infra (atomic + increment commit + boot template)
  ↓
Layer 4 — Runtime hook (daemon stateless AMENDMENT-016 v2)
  ↓
Layer 5 — Sub-agent boot (prompt template 含 czl_subgoals + git log)
  ↓
Layer 6 — CEO orchestration (mid-stream check-in + 1-deliverable discipline)
  ↓
Layer 7 — Behavior audit (k9_audit_v3 3-layer: Liveness + Chain + Invariant)
```

7 层闭环 = CZL 真绑死永不失效的架构完成。
