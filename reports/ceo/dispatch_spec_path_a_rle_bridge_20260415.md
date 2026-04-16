# Dispatch Spec: Path A ↔ RLE Bridge

**For**: Maya-Governance (eng-governance)
**Priority**: P0 (Board 2026-04-15 night 揭示，产品架构最深问题)
**Scope**: Y\*gov source — `ystar/governance/`
**Estimated**: 2-3h

---

## Background (Board 给的诊断)

**Path A 通路审计结果**：13 组件 import 链全 ✅，但有**冷启动断裂** + **47/64 边未接** + **RLE↔Path A 完全断开**。

最关键发现：**ResidualLoopEngine (RLE) 就是 CZL**。AMENDMENT-014 (2026-04-12) 把 CZL 实装进 Y\*gov 叫 `ResidualLoopEngine`，注释原文：
```
# CIEU = (Xt, U, Y*, Yt+1, Rt+1)  where Rt+1 = distance(Y*, Yt+1)
# If Rt+1 > epsilon → compute next U → emit intent → agent acts → new CIEU
```
振荡检测、最大迭代、Board 上报都有。

**但 RLE 和 Path A 并行运行互不知道对方**：
- RLE 在 `_hook_daemon.py` PostToolUse 触发
- Path A 在 `GovernanceLoop.tighten()` OmissionStore 数据驱动

**应然**：
```
RLE 算出 Rt+1 持续非零
  → 产生 GovernanceSuggestion ("目标长期未收敛")
  → 喂给 GovernanceLoop / Path A
  → Path A 去接线/修复让 Rt+1 能归零的那些模块
```

## Y\* (Maya 必达)

1. `ResidualLoopEngine` 持续非零 Rt+1 流出后能产生 `GovernanceSuggestion`
2. `GovernanceSuggestion` 喂入 `GovernanceLoop` 作为非 OmissionStore 来源
3. live demo: 故意造一个 Rt+1>0 不收敛的循环 → 5 分钟内 GovernanceLoop emit suggestion → Path A pick up → 至少接 1 条 module graph edge
4. 不破坏现有 OmissionStore→GovernanceLoop 路径
5. 三层 doctrine：Layer 1 (代码 grep) + Layer 2 (production 触发 log) + Layer 3 (E2E demo)

## Xt (现状)

- `Y-star-gov/ystar/governance/residual_loop_engine.py` 存在
- `Y-star-gov/ystar/governance/governance_loop.py::tighten()` 现只读 OmissionStore
- module graph 23 节点 / 64 边 / 47 未接

## U (Maya 自定 implementation，建议)

1. RLE 内加 `_should_emit_suggestion()`：连续 N 次 Rt+1 > epsilon → 触发
2. 新方法 `RLE.emit_governance_suggestion(reason="long_unconverged")` → 写入 GovernanceSuggestion 通道
3. GovernanceLoop.observe_from_residual_engine() 新观测源（与 OmissionStore 并列）
4. 第二优先（Board 提示）：把 enforce → GovernanceLoop.tighten 接线（每次治理 enforce 回流观测）
5. 第三优先：IntentContract → check / assess_batch / learn 三条边

## Rt+1=0 判据

- E2E demo script: trigger 一个不收敛 task → 5 分钟内 GovernanceLoop 收到 RLE-source suggestion → Path A 接线 ≥1 边 → CIEU 有完整 trace
- 接线后 module graph 47→46 (或更少) 未接边
- 不破坏现有 24 tests (跑 pytest tests/test_governance_loop* 全绿)

## 后续 (本任务外，可入 backlog)

- Domain pack 边接线（finance/healthcare/devops）—— Board 第三优先
- 冷启动断裂修法（首次部署喂初始 observations）

---

**派工时机**：Maya 完成 W16 amendment + governance + OR-bug 后立刻 dispatch 这个。
