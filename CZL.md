# CZL — Causal Zero Loop

**Y\* Bridge Labs 的核心方法论**，2026-04-15 创造。

CZL 是一个量化的因果收敛循环。每个任务定义显式的 Y\* (完成标准) 与 Xt (当前态)，执行行动 U 得到 Yt+1，计算 Rt+1 = distance(Yt+1, Y\*)。**Rt+1 = 0 才算真完成**。

## Canonical documentation index

- `README.md` #CZL section — 概览 + 实证数据 + 对比框架
- `governance/WORKING_STYLE.md` §第十二条 — CZL 任务工作法完整规范
- `AGENTS.md` §Session-Level Y\* Doctrine — Session-level 5 条硬约束
- `AGENTS.md` §Rule Verification Three-Layer Doctrine — 规则写了/在跑/在拦三层
- `governance/sub_agent_atomic_dispatch.md` — Atomic Dispatch 纪律 (1 dispatch = 1 deliverable, ≤10 tool_uses)
- `knowledge/shared/methodology_assets_20260415.md` — 12 项方法论完整 lookup index
- `scripts/k9_audit_v3.py` — 3-Layer audit (Liveness + Causal Chain + Invariant)
- `.czl_subgoals.json` — HiAgent working memory 子目标树 (CEO dogfood live)
- `reports/ceo/campaign_v7_business_pivot_plan_20260415.md` — 商业化 pivot 背景与 CZL 应用

## 五元组

| Symbol | Meaning |
|--------|---------|
| Y\*    | 人类定义的完成标准 (agent 不得自设) |
| Xt     | 当前状态快照 (tool_use 实测, 非印象) |
| U      | 行动集 (1..N 步) |
| Yt+1   | 行动完成后的实际状态 |
| Rt+1   | distance(Yt+1, Y\*) — 量化残差 |

## 2026-04-15 实证

- 5 campaigns 全 Rt+1=0 ship
- Architecture Fix Campaign: 72 tool_uses / 10 件 constitutional ship (7.2 uses/item)
- Pre-atomic baseline: 47 tool_uses / 0 件 (60x 效率改善)
- 100+ live CIEU events 作可审计证据链

## 与其他框架区别

| 框架 | 有顶层 Y\* | 有量化 Rt+1 | 方向性 |
|------|-----------|------------|--------|
| CZL  | 是 | 是 (distance) | 收敛到 0 |
| Cursor periodic reset | 否 | 否 | fresh start |
| VeriMAP (EACL 2026) | 否 (子任务局部) | 否 | 局部 pass/fail |
| Ralph Loop | 是 (binary) | 否 (pass/fail) | 无方向 |

## Canonical commit pointer

历史 canonical commits 可通过 `git log --all --grep="CZL" --oneline` 查到。
当前 README.md + CZL.md 首次 ship commit 由本次 atomic dispatch 产出。
