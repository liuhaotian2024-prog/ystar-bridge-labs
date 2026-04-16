# 顾问 3-维断裂框架 — CEO 反驳 + 采纳规划

**Date**: 2026-04-16
**Owner**: CEO (Aiden)
**Trigger**: Board 转递 consultant 3-dim audit framework + P0 claim "PreToolUse 未注册 = 治理完全失效"
**Status**: P0 CLAIM **FALSIFIED** ❌ / framework 结构**采纳** ✅
**L-tag**: [L0 rebuttal with hard data]

## TL;DR (Board 先看这段)

**顾问 P0 claim 基于过时或错位的 snapshot — 验证为假。** 我们当前 Labs 治理活着：PreToolUse / PostToolUse 真注册了，7 天真产出 15,761 deny events (17% rejection rate), 1,733 tool-call governance events 活流. **但顾问 3-维思维框架 (生产者/使用执行者/被治理者) 结构有价值，采纳为 K9 top-level audit 入口**，且暴露 3 个真缺口值得修.

## 逐条反驳 (硬数据)

| 顾问 claim | 实际硬数据 | 判定 |
|---|---|---|
| PreToolUse 未注册 | `.claude/settings.json` 真有 PreToolUse: `hook_wrapper.py` + `hook_wrapper_observe.py` | ❌ 假 |
| PostToolUse 未注册 | 真有: `hook_prompt_gate.py` + `hook_subagent_output_scan.py` | ❌ 假 |
| hook_client_labs.sh 不在 settings | 真不在 — 但**功能由 hook_wrapper.py 替代**，hook_client_labs.sh 疑似 dead code | ⚠️ 真但非 P0 |
| 0 个 tool-call gov 事件 | 7d: 928 BEHAVIOR_RULE_VIOLATION + 329 WARN + 208 WHITELIST_DRIFT + 268 MATCH = **1,733 events** | ❌ 假 |
| 0 个 deny decisions | 7d: **15,761 / 92,229 = 17.089% deny rate** | ❌ 假 |
| forget_guard.py 从未被调用 | hook_wrapper.py 0 mentions — **可能真 dead code**，但治理不经它走，走 `ystar.adapters.hook.check_hook()` | ⚠️ 部分真 (非 P0) |
| deny 规则形同虚设 | 15k deny events 证明 rules 生效 | ❌ 假 |

**结论**: 顾问快照可能来自另一个 project / 别的机器 / 过时配置, 或者他搜索 "PreToolUse" 时 grep 方式漏掉了 camelCase. 与我们当前 repo 硬状态**不符**。

## 顾问框架的真价值

P0 claim 虽错, 但**3-维思维本身**比我们现有四层框架 (structural/behavioral/dataflow/cross-repo) 更本质：

- 四层框架答"检查什么"
- 3-维框架答"从什么角度检查"
- 前者是后者的具体实现

**暴露出的 3 个真缺口**（framework catch 出, 不是 P0 claim 本身）：

### G1: delegation_chain inheritance monotonicity 未显式 verify
父合约 deny 规则应被子 agent 继承（单调性：deny 只增不减）。当前我们**没有任何自动检查**保证这一点。

### G2: 重复违规 → 行为未改变信号
顾问 dim 3 check 4：同一 agent 同类违规 ≥3 次 = warn 没改行为. 我们有 forget_guard rules 但**不自动检测 warn 无效 → 升 deny**.

### G3: K9 缺 top-level 3-维 audit 入口
现有 K9 是 scan/detect, 没有"从 3 个角度同时验证治理效果真实发生"的宏观 audit.

## 采纳 plan

### 立即 (本周)

**Maya 派工**: 实装 `scripts/k9_three_dim_audit.py` (`governance/` 新入口), 含:
- `check_producer_integrity()` — CIEU 生产者完整性 (现有部分可复用)
- `check_executor_integrity()` — hook 链 + check() 端到端 callable proof
- `check_governed_integrity()` — delegation monotonicity + 重复违规无效检测 + deny 真发生率

### 后续 (下周)

- 把 3-维 audit 接入 `ensure_crontab.sh` 每 4h 跑一次 + 每日 K9 报告
- 发现 G1/G2/G3 中任一 = Rt+1 ≠ 0 的硬条件

### 不做

- 不重写现有 hook_wrapper.py (功能正常, 只是命名与顾问 mental model 不同)
- 不紧急移除 hook_client_labs.sh / forget_guard.py (进 dead code audit backlog)
- 不 block 30-day plan (Day 5+ 照常跑)

## Rt+1 归零条件

- 3-维 audit 脚本 ship + 3 维度至少各 4 check 真跑
- G1 / G2 / G3 各出 1 份 baseline report
- 发现 real violation 就修, 没真 violation 就 baseline = 0 记录下来

---

**一句话**: 顾问警钟没有打错 "应有 3-维思维", 只是打错了"我们没实装"。我们实装了核心，缺的是**能把实装可视化呈现** 的 audit 层. 今天采纳框架, 明天跑出第一份 3-维 report.
