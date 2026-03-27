# SaaS Metrics Framework

## ARR/MRR (Annual/Monthly Recurring Revenue)

**Definition**: Normalized annual or monthly value of recurring revenue under contract.

**When to use**:
- Weekly/monthly board reporting
- Sales team quota tracking
- Investor updates

**How to calculate**:
```
MRR = Sum of all monthly subscription fees
ARR = MRR × 12 (or sum of annual contracts)

New MRR = New customers × monthly fee
Expansion MRR = Upgrades from existing customers
Churned MRR = Lost customers × their monthly fee
Net New MRR = New + Expansion - Churned
```

**Healthy benchmarks**:
- Month-over-month MRR growth: 10-20% (early stage, per David Skok)
- ARR growth: 3x year-over-year (T2D3 model by Neeraj Agrawal, Battery Ventures)

**Common mistakes**:
- Including one-time setup fees in MRR
- Counting annual contracts as 12 months of MRR immediately
- Not normalizing discounts (count actual cash, not list price)
- Mixing bookings with revenue

---

## Churn Rate

**Definition**: Percentage of customers or revenue lost in a period.

**Types**:
- **Gross Revenue Churn**: Revenue lost from cancellations and downgrades
- **Net Revenue Churn**: Gross churn minus expansion revenue from existing customers

**When to use**:
- Monthly health checks
- Customer success team scorecards
- Long-term viability assessment

**How to calculate**:
```
Gross Revenue Churn Rate = (Churned MRR / Starting MRR) × 100
Net Revenue Churn Rate = ((Churned MRR - Expansion MRR) / Starting MRR) × 100
```

**Healthy benchmarks** (Jason Lemkin, SaaStr):
- Annual gross revenue churn: <10% for SMB, <5% for enterprise
- Best-in-class: Negative net revenue churn (expansion > churn)

**Common mistakes**:
- Using customer count churn instead of revenue churn (whales matter more)
- Not segmenting by cohort (mixing old and new customers)
- Ignoring seasonality in annual contracts
- Counting paused accounts as churned

---

## Net Revenue Retention (NRR)

**Definition**: Percentage of revenue retained from a cohort over time, including expansions.

**When to use**:
- Evaluating product-market fit
- Assessing upsell/cross-sell effectiveness
- Investor due diligence (public SaaS companies report this)

**How to calculate**:
```
NRR = ((Starting MRR + Expansion - Downgrades - Churn) / Starting MRR) × 100

Example:
Starting MRR from Jan 2025 cohort: $100,000
12 months later:
- Expansion: +$30,000
- Downgrades: -$5,000
- Churn: -$15,000
NRR = ($100k + $30k - $5k - $15k) / $100k = 110%
```

**Healthy benchmarks** (Bessemer Cloud Index):
- Good: >100% (negative net churn)
- Great: >120% (best public SaaS companies)
- Poor: <90%

**Common mistakes**:
- Mixing cohorts (must track same starting group)
- Including new customer revenue (only existing customers)
- Not excluding customers who were already churned

---

## Magic Number

**Definition**: Sales efficiency metric showing how much ARR you generate per dollar spent on sales and marketing.

**When to use**:
- Deciding when to scale sales team
- Optimizing CAC payback period
- Quarterly GTM strategy review

**How to calculate**:
```
Magic Number = (Net New ARR in Quarter) / (Sales & Marketing Spend in Prior Quarter)

Example:
Q1 S&M spend: $200,000
Q2 net new ARR: $300,000
Magic Number = $300k / $200k = 1.5
```

**Healthy benchmarks** (David Skok, Matrix Partners):
- <0.75: Don't scale sales yet, fix product/market fit
- 0.75-1.0: Efficient, safe to scale
- >1.0: Very efficient, invest aggressively

**Common mistakes**:
- Using gross new ARR instead of net new (must subtract churn)
- Wrong quarter lag (sales cycles vary by product)
- Not including all marketing costs (events, tools, headcount)

---

## Burn Multiple

**Definition**: Dollars burned per dollar of net new ARR generated.

**When to use**:
- Capital efficiency assessment
- Runway planning
- Comparing efficiency across startups

**How to calculate**:
```
Burn Multiple = Net Burn / Net New ARR

Example:
Quarterly net burn: $500,000
Net new ARR in quarter: $400,000
Burn Multiple = $500k / $400k = 1.25
```

**Healthy benchmarks** (David Sack, Craft Ventures):
- <1.5x: Efficient (top quartile)
- 1.5-2x: Acceptable
- >3x: Unsustainable

**Common mistakes**:
- Using gross burn instead of net burn
- Not annualizing quarterly ARR adds
- Comparing companies at different stages (early stage burns more)

---

## Rule of 40

**Definition**: Growth rate + profit margin should exceed 40%.

**When to use**:
- Balancing growth vs profitability
- Late-stage company health check
- Public market readiness assessment

**How to calculate**:
```
Rule of 40 = YoY Revenue Growth Rate (%) + EBITDA Margin (%)

Example:
Revenue growth: 50%
EBITDA margin: -20%
Rule of 40 = 50% + (-20%) = 30% (below threshold)
```

**Healthy benchmarks** (Bessemer, Brad Feld):
- >40%: Healthy balance
- <40% but growing >100%: Acceptable for early stage
- <40% and slowing growth: Problem

**Common mistakes**:
- Using ARR growth instead of revenue growth (recognition matters)
- Calculating EBITDA incorrectly (must exclude stock comp for true cash picture)
- Applying this to pre-revenue companies (only relevant at scale)

---

## Weekly CFO Checklist

**Monday Morning**:
1. Calculate last week's new MRR, expansion, churn
2. Update rolling 12-week MRR chart
3. Flag any unusual churn events

**Month End (within 3 days)**:
1. Close month's MRR/ARR
2. Calculate gross/net revenue churn
3. Update NRR for each cohort
4. Review burn multiple vs target

**Quarter End**:
1. Calculate Magic Number
2. Assess Rule of 40
3. Prepare board metrics deck
4. Update annual forecast
