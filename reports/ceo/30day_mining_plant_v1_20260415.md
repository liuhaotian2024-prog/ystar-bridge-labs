# 30-Day 矿机方案 v1 — Y*gov Claude Code Plugin

**Date**: 2026-04-16 night (post 4-部门 research 整合)
**Owner**: CEO (Aiden) integration
**Status**: 待 Board 批 → 启动 Day 1
**Y\* (Board 给的)**: 完整清晰合理可执行的方案含明确目标 + 实施路线图

## 4 部门 research 整合（一致结论）

| 部门 | 报告 | 推荐 | 一致度 |
|---|---|---|---|
| CSO Zara | bounty_platform_market_research_20260415.md | #1 Plugin / #2 Bug Bounty / #3 Workflow Resale | 与 Marco 一致 |
| CFO Marco | monetization_models_research_20260415.md | **#1 Plugin $49/mo** LTV:CAC 11.76:1, BEP 15客户, payback 0.5-1月 | anchor 决策 |
| CMO Sofia | distribution_strategy_30day_20260415.md | **#1 Plugin** ✅ Marco. Show HN 5-15k traffic, CAC $25-$50 organic | ✅ Marco |
| CTO Ryan | tech_feasibility_30day_20260415.md | **#1 Plugin 85% ready** 21d eng + 9d QA | ✅ but flag 3-week hardening 必须 |

**3/4 部门 explicit endorse Plugin**。Bug Bounty 双边市场 30 天无法建立 (CMO)。Workflow Resale 需企业销售 (CMO)。

## 30-Day Y* (CIEU 5-tuple format)

```yaml
y_star: "30 天内 ship Y*gov Claude Code Plugin v1.0 上 Anthropic marketplace + 至少 1 笔 $49/mo 订阅收入到账"
y_star_criteria:
  P1: Plugin packaging 完成 (gov-mcp 38 tools 子集) — CTO Ryan owner
  P2: 86 tests pass + Python 3.9-3.12 tox + MCP stateless E2E — CTO
  P3: Anthropic marketplace 提交 + 上架审核通过 — CTO + CMO
  P4: Stripe Checkout $49/mo subscription infra + landing page — CFO + CMO
  P5: Show HN 发布 + GitHub README + 3 社区 (Anthropic Discord / r/LocalLLaMA / Twitter dev) launch — CMO
  P6: 第一笔 paying customer (Stripe payment confirmed) — Revenue check
artifact_persistence:
  - commit_to_origin (plugin code in dedicated repo)
  - referenced_in_marketplace (Anthropic listing live URL)
  - first_paying_customer (Stripe webhook confirmation)
freshness_policy: tied_to_campaign
owner_after_rt1: ceo (revenue tracking) + cto (plugin maintenance) + cmo (marketing iteration)
```

## Day 1-30 Implementation Roadmap

### Phase 1 — Day 1-7 Foundation (CTO 主)
- D1-2: Anthropic marketplace 上架文档 deep dive (Ryan)
- D3-4: gov-mcp 38 tools subset → plugin packaging (Ryan + Maya)
- D5-7: MCP stateless daemon E2E validation (W23 已 ship 基础) + Python 3.9-3.12 tox matrix

### Phase 2 — Day 8-14 Build
- D8-10: 86 tests 在 plugin 环境真跑通过 (Maya/Ryan)
- D11-12: Stripe Checkout $49/mo + landing page (Marco + Sofia)
- D13-14: Anthropic marketplace 正式提交 + 审核 wait

### Phase 3 — Day 15-21 Launch
- D15-17: README rewrite (Sofia, 已有 CZL 章节作 anchor) + buy button
- D18-19: 上架公告 + Plugin marketplace listing 优化
- D20-21: Show HN 提交 (Sat 10am ET 黄金时段) + Discord/Reddit/Twitter

### Phase 4 — Day 22-30 Iterate + Revenue
- D22-25: Show HN traffic 监控 + activation 优化 (Sofia 警示: awareness ≠ activation)
- D26-28: 用户反馈循环 + Week 4 activation campaign (CMO 建议)
- D29-30: 第一笔 paying customer 闭环 + Y*-criteria 全 verify

## Risk Register

| # | 风险 | 来源部门 | Mitigation |
|---|---|---|---|
| R1 | Anthropic marketplace 审核 reject | CTO Ryan | D1-2 提前 deep dive 文档 + buffer 审核窗口 |
| R2 | "Show HN awareness ≠ activation" | CMO Sofia | Week 4 activation campaign + email nurture |
| R3 | CFO 假设 20% trial→paid 过乐观 | CMO vs CFO 分歧 | Week 4 真实漏斗数据校准 |
| R4 | 3-week hardening 不够 (CTO flag) | CTO Ryan | Day 1-3 priority MCP stateless validation |
| R5 | Cash $1k-$2k 投入是否 OK | CFO Marco | **Board 批所需** |

## CEO 决策 checkpoints (3 处需 Board 批)

1. **Day 0 (now)**: 批准启动方案 + 授权 $1k-$2k cash
2. **Day 7**: 中期 review (Phase 1 done, Plugin packaging 真 ready?)
3. **Day 21**: Launch 前 final go/no-go (Phase 3 完前)

## Cash + Revenue Projection (CFO Marco)

```
Cash 投入: $1k-$2k (marketing + marketplace listing 费用)
30-day target: 1 paying customer = $49 MRR
12-mo moderate scenario: $35,280 ARR (60 customers)
12-mo aggressive scenario: $176,400 ARR (300 customers)
Runway 延长 (moderate): 11.76 月 @ $3k/月 burn rate
LTV:CAC: 11.76:1 to 23.52:1 (best-in-class)
```

## 不做什么（明示 scope 锁）

- 不做 Bug Bounty Service (CMO 警示双边市场冷启动 30 天不可能)
- 不做 Workflow Resale (CMO 警示 $299/mo 需企业销售周期)
- 不做企业长销售 (Board 早些明令)
- 不做 Web3 高额 bounty 主线
- 不做重人力咨询型业务

## 与 CZL/Y\*gov stack 关联

Plugin 实质 = Y\*gov + gov-mcp + CZL runtime 打包成 Anthropic marketplace 可装产品。**今晚 Architecture Fix Campaign 10/10 ship 是基础设施 prerequisite**。CZL 真绑死 + atomic dispatch + state machine whitelist 都已 live。Plugin 是这套 stack 的**第一个商业产品形态**。

## Y\* 满足 = Rt+1 = 0

```
Rt+1 = (P1未done + P2未done + P3未done + P4未done + P5未done + P6未done)
当前 Rt+1 = 6 (Day 0)
Day 30 target: Rt+1 = 0
```

## Board 决策 ask

请明示批准:
- [ ] 30-day 矿机方案 v1 启动
- [ ] 授权 $1k-$2k cash 投入
- [ ] Day 7 / Day 21 中期 review checkpoint

批后立刻 Day 1 启动. CEO orchestrate, atomic dispatch sequence 严格执行.
