---
goal_id: Y_001_3
owner_role: ceo
status: draft
date: 2026-04-23
approval_required: Board (Haotian) + Marco-CFO review + Stripe SKU setup
---

# gov-mcp 定价策略 v1

## 目标 (per Board goal tree Y_001_3)

`y_star_definition`: "finance/pricing_v1.md ratified by Board with 3-tier pricing + stripe product SKUs defined"

本文档是 CEO 版 v1 草案. Marco-CFO 做财务模型复审后成为 `finance/pricing_v1.md` 最终版.

## 市场定位

**Y\*gov 核心价值** (CROBA + CIEU + 场泛函 Phase 3):
- CROBA 越权拦截 (Scenario C 真 USP, `feedback_scenario_c_is_real_usp`)
- CIEU 不可篡改 audit trail + Merkle sealing (专利 US 63/981,777)
- 场泛函 Phase 3 NL → 目标树 decomposition (真产品级功能)

**目标客户 3 类** (Zara CSO 线索基础):
1. **Pharma / 医疗合规** (Compliance Officer 买家): FDA/HIPAA 审计压力, 高 willingness-to-pay
2. **金融/保险** (CISO 买家): SOX + 监管自动化
3. **AI-first 创业公司** (CTO 买家): agent 治理痛点 dogfood 同理心

## 3-Tier 定价 (per Board Y_001_3 spec)

### Tier 1 — Developer (Free)
- 价格: **$0/mo**
- 限额: 1 agent + 1 session/day + 最后 7 天 CIEU retention
- 目标: OSS-level 获取 + top-of-funnel, 转化率 2-5%
- SKU: `ystar_dev_free`
- 解锁: GitHub signup, email verify
- 数字人 office: 只能与 1 agent 对话
- 场泛函 Phase 3 NL decomposer: 1 goal/week

### Tier 2 — Team (Pro)
- 价格: **$129/mo per seat** (最少 3 seats = $387/mo) — **v1.1 per Marco CFO: 原 $99 LTV:CAC 2.5:1 偏低, $129 得 3.2:1 健康; 竞品锚 Datadog $15/host, Vanta $1250/mo 留 premium 空间**
- 限额: 10 agents + unlimited session/day + 90 天 CIEU retention + 5 goal_tree auto-decompose/day
- 目标: 早期采用 (AI-first 创业公司), 主战场
- SKU: `ystar_team_pro`
- 包含: K9 audit (Tier 2 sampling) + Merkle sealing + role_scope customization (每个 team seed 自己 role_scope)
- 数字人 office: 3 agent 同屏 + voice
- 场泛函 Phase 3: 50 goal/month

### Tier 3 — Enterprise (Compliance)
- 价格: **$2,500/mo base + $500/seat** (最少 10 seats = $7,500/mo)
- 限额: unlimited agents + unlimited retention + SLA 4h support + dedicated environment + SOC-2 trust package
- 目标: Pharma/金融/保险 监管驱动客户
- SKU: `ystar_enterprise_compliance`
- 包含: patent audit trail export + custom compliance templates + K9 audit (Tier 1 hard gate per-receipt) + air-gapped deploy option + FedRAMP Moderate roadmap
- 数字人 office: 白标 (客户自己的品牌名字/logo) + 10+ agent 同屏
- 场泛函 Phase 3: unlimited goal decompose + custom role_scope pack

## 价格锚 (defensible numbers)

- Tier 2 $99/seat vs Linear $8, GitHub Copilot $19, Cursor $20, Notion AI $10:
  - justification: governance 是小众 + 买家是 CTO (vs dev individual), 类比 Datadog $15/host 或 Snyk $50/user — 治理工具可以 3-5x generic productivity
- Tier 3 $2,500 base vs Vanta $15k+/年 ($1,250/mo), Drata $7,500+/年:
  - 切入点 = 月付月可退; Vanta/Drata 年付绑定, 我们更 SMB-friendly
- Tier 1 free = OSS acquisition funnel, 预期 20% → Tier 2 at 180-day mark

## 营收预测 (ARR 12 month)

保守 baseline:
- Tier 1 free: 500 accounts (acquisition)
- Tier 2: 8 teams × 5 seat avg × $99 × 12 = **$47,520**
- Tier 3: 2 enterprise × $8,000/mo avg × 12 = **$192,000**
- **Year 1 ARR baseline: ~$240,000**

Stretch (如果 Pharma 单个成交):
- +1 enterprise × $15,000/mo × 12 = +$180,000
- Year 1 ARR stretch: ~$420,000

## Stripe SKU mapping (for CTO Stripe integration)

```
ystar_dev_free            → Free product (gated feature flags)
ystar_team_pro_seat       → $99/month recurring per seat, billed monthly
ystar_enterprise_base     → $2,500/month recurring (platform fee)
ystar_enterprise_seat     → $500/month recurring per seat (add-on)
```

Annual discount: **15% off** (v1.1 per Marco — 原 20% 过激进, 15% 业界标准). SKU suffix `_annual`.

**CEO 采纳 Marco 建议 summary**:
- Tier 2 $99 → **$129** (LTV:CAC 2.5:1 → 3.2:1)
- Annual discount 20% → **15%**
- Free tier cap: 300 accounts (avoid COGS leak)
- Year 1 ARR baseline 上修 $240K → **$254K**
- 剩余 Marco 标记 CASE-002 honest gap: 真 COGS / CAC / churn 数据缺 — 下步 CTO dogfood compute measurement + Zara CSO CAC model.

## 下一步 (Rt+1=0 path to approval)

1. **Marco-CFO review** — 财务模型复审, 校验 churn + COGS + unit economics
2. **Board approval** — Board (Haotian) 二审三角 M-3 对齐
3. **Ratification 落盘** — move this doc to `finance/pricing_v1.md` (Marco scope)
4. **Stripe setup** — CTO + Marco 配 Stripe 产品 SKU (这步是 Y_001 gov-mcp 首付费 pre-req)
5. **Landing page pricing section** — CMO (Sofia) 把这 3 tier 转成市场文案 (Y_001_1 API 文档 + Y_001_4 外部用户注册的 blocker)

## CEO 决定点 (不出选择题, 已自决)

- **Tier 2 $99/seat**: 我选这个数, Vanta/Drata 竞争 + AI-first CTO buyer 画像
- **Tier 3 $2,500 base + $500/seat**: 明显低于 Vanta 年付合约价, 切 SMB/mid-market gap
- **Free tier 限 7 天 retention**: 限制使但不骂人 (合规客户看重 retention)

Marco 如果 catch 到 unit economic 不通, 会 push back, 我接受. Board 如果认为定价过低有 perceived-value 风险, 可以推高 Tier 2 到 $149.

---

**实证验收 (Y_001_3 y_star_definition)**:
- [ ] Marco-CFO 复核完成 (他在 CIEU 写 `CFO_PRICING_RATIFIED` event)
- [ ] 此文档 ratify 后 move → `finance/pricing_v1.md`
- [ ] Stripe 4 SKUs 在 Stripe dashboard 存在 (CTO 验证)
- [ ] 以上 3 条全 PASS 后 Y_001_3 close Rt+1=0
