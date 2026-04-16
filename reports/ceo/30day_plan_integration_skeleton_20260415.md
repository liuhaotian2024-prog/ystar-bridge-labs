# 30-Day 矿机方案 — CEO 整合 Skeleton (待 4 部门研究归齐)

**Date**: 2026-04-15 night
**Status**: Skeleton + integration framework. 4 部门 sub-research 各自 ship 后 CEO 整合本文件。
**Y\* (Board 给的)**: 完整清晰合理可执行的方案含明确目标 + 实施路线图

## 4 部门 sub-research 收齐状态

| 部门 | Owner | 报告 | 状态 |
|---|---|---|---|
| **CSO 市场调研** | Zara | `reports/sales/bounty_platform_market_research_20260415.md` | ✅ ship (commit 449d5989) — Top 3: Plugin / Bounty Service / Workflow Resale |
| **CFO 财务可行性** | Marco | `reports/cfo/monetization_models_research_20260415.md` | ✅ ship (commit 3e11a335) — 推荐 #1 Plugin LTV:CAC 11.76:1, BEP 15客户, payback 0.5-1月 |
| **CMO 分发策略** | Sofia (a3ed0b777350827ec) | `reports/cmo/distribution_strategy_30day_20260415.md` | ⏳ 跑中 |
| **CTO 技术可行性** | Ryan (a40f303dbca00f6ea) | `reports/eng-platform/tech_feasibility_30day_20260415.md` | ⏳ 跑中 |

## Integration Framework (待 4 报告齐后填入)

### Y\* 制定（基于 4 部门数据）

预期方向 (CFO 已锚定 #1 Plugin)：

```yaml
y_star: "30 天内 ship Y*gov Claude Code Plugin v1.0 上 marketplace + 第一笔$49/mo 订阅收入到账"
artifact_persistence:
  - commit_to_origin (czl-runtime + plugin code)
  - referenced_in_marketplace (Anthropic plugin listing)
  - first_paying_customer (Stripe payment confirmation)
freshness_policy: tied_to_campaign
owner_after_rt1: ceo (revenue tracking) + cto (plugin maintenance)

y_star_criteria:
  P1: Plugin code 完成 + 86 tests pass (CTO scope, 待 Ryan 报告确认)
  P2: Marketplace 上架 (CMO scope, 待 Sofia 报告 launch playbook)
  P3: Pricing infra ($49/mo Stripe Checkout) (CFO scope, Marco 已建议)
  P4: Distribution channels active (Show HN + GitHub README + Discord, 待 Sofia)
  P5: First paying customer (revenue check)
```

### Implementation Roadmap (Day 1-30)

待 4 报告齐后填入。预期 phase split:
- **Day 1-7 (Foundation)**: CTO 决定 plugin scope + 收 czl-runtime MVP code
- **Day 8-14 (Build)**: 86 test pass + manifest + Anthropic marketplace 提交
- **Day 15-21 (Launch)**: 上架 + Show HN + Awesome list 提交
- **Day 22-30 (Iterate + Revenue)**: 用户反馈循环 + 第一笔收入闭环

### Risk Register (4 部门各自提)

待整合 (待 4 报告齐).

### 不做什么

- 不做企业长销售
- 不做 Web3 高额 bounty 主线
- 不做重人力咨询型

### 整合后 CEO 决策需 Board 批
- 财务: $1k-$2k cash 投入是否 OK (Marco 已分析)
- 法律: K9 AGPL 与 Y*gov MIT 在 plugin bundle 的合规性 (Ryan 报告会涵盖)
- 时间窗口: 4 月 marketplace 刚开 → 时间敏感但有可能其他玩家也在追

## 实践 Atomic + R 归零

**本 skeleton 本身遵循 atomic 原则**：
- CEO 写 reports/ scope 内
- ≤5 tool_uses
- 不 dispatch 新 sub-agent (4 已派)
- 等 Sofia + Ryan 返回后 CEO 整合 (合法 management work)
- 整合后立刻 ship final plan + report Board

## 期望最终 deliverable

`reports/ceo/30day_mining_plant_v1_20260415.md` — 含:
1. Y\* + Y\*-criteria (5 P)
2. Day 1-30 atomic dispatch sequence
3. 各部门 owner + budget
4. Risk register + mitigation
5. Revenue projection + cash flow
6. Show HN content draft
7. Board approval checkpoints (3 处)

预期 size: ≤2000 字 concise actionable.
