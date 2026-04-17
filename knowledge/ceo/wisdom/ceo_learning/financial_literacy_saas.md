---
name: CEO Financial Literacy — SaaS Unit Economics (学习笔记 Round 9)
type: ceo_learning
discovered: 2026-04-17
source: SaaS metrics 2025-2026 benchmarks
depth: medium
---

## CEO 必须懂的 8 个 SaaS 财务指标

### Revenue (收入)
| 指标 | 公式 | 2026 benchmark | Y* Labs 现状 |
|---|---|---|---|
| MRR | 月经常性收入 | varies | $0 |
| ARR | MRR × 12 | varies | $0 |
| Growth Rate | (ARR_now - ARR_prior) / ARR_prior | 26% median, 50% top | N/A |

### Customer Economics (客户经济学)
| 指标 | 公式 | 健康值 | Y* Labs |
|---|---|---|---|
| CAC | 获客总成本 / 新客户数 | varies | $0 (无客户) |
| LTV | ARPU × 客户生命周期 | varies | $0 |
| LTV:CAC | LTV / CAC | 3:1 → 5:1 | N/A |
| CAC Payback | CAC / 月毛利 | <12 months | N/A |

### Health (健康度)
| 指标 | 公式 | 警戒线 | Y* Labs |
|---|---|---|---|
| Churn | 流失客户 / 总客户 / 月 | SMB 3-7%, Enterprise <1% | N/A |
| Burn Rate | 月支出 - 月收入 | N/A | 未跟踪 (API costs?) |
| Runway | 现金 / 月 burn rate | >18 months | 未知 |
| Rule of 40 | Growth% + Margin% | ≥ 40 | N/A |

## Y* Bridge Labs 独特财务特征 (AI 公司 vs 人类公司)

| 传统 SaaS | Y* Labs |
|---|---|
| 员工薪资 = 最大成本 | **员工成本 = $0** (AI agents 无薪资) |
| 办公室 = 第二成本 | **办公室 = $0** |
| 主要成本 = 人力 + 房租 | **主要成本 = API token 消耗** |
| CAC 含销售人员薪资 | CAC = 纯数字 (广告/内容/赏金) |
| 规模化需要招人 | **规模化 = spawn more agents** |

**关键洞察**: 我们的 burn rate 几乎全是 Anthropic API 费用。一旦有收入，margin 极高 (因为无人工成本)。这是 AI 公司的结构性优势。

**CEO 应做 (CFO 没在线时)**:
1. 跟踪每月 API 费用 (Anthropic dashboard)
2. 估算每 session token 消耗 → 月均 burn
3. Board 出资 runway 还剩多少?
4. 第一个客户需要定价多少才能 cover burn?

## CEO 财务决策框架 v0.1

```python
def financial_check(decision):
    # 1. 会增加 burn rate 吗?
    if increases_burn(decision) and runway < 6_months:
        return "慎重 — runway 短时不增支出"
    
    # 2. 有 unit economics 支撑吗?
    if targets_customer and ltv_cac_ratio < 3:
        return "获客成本太高 — 要么降 CAC 要么提 LTV"
    
    # 3. 符合 Rule of 40 吗?
    if growth_rate + margin < 40:
        return "要么增长更快要么更盈利 — 不能两个都低"
    
    # 4. AI 公司特殊: margin 天然高
    # 无人工成本 → margin 主要由 API 费用决定
    # 每个客户的 API 消耗 = variable cost
    # 定价必须 > API cost per customer × 安全系数
```

## 下一步
- 查 Anthropic API 实际定价 → 估算 burn
- 让 CFO (Marco) 建简单 unit economics model
- 但 per dependency_sequencing: 产品先能用 → 再谈定价
