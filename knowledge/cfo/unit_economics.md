# Unit Economics Framework

## Lifetime Value (LTV)

**Definition**: Total net profit expected from a customer over their entire relationship with your company.

**When to use**:
- Determining affordable CAC
- Pricing decisions
- Customer segmentation strategy
- Channel ROI analysis

**How to calculate**:

**Method 1 - ARPU-based (simple)**:
```
LTV = (ARPU × Gross Margin %) / Revenue Churn Rate

Example:
ARPU: $500/month
Gross Margin: 80%
Monthly Revenue Churn: 3%
LTV = ($500 × 0.80) / 0.03 = $13,333
```

**Method 2 - Cohort-based (more accurate)**:
```
LTV = (Average Monthly Revenue per Customer × Gross Margin % × Average Customer Lifetime in Months)

Example:
ARPU: $500/month
Gross Margin: 80%
Average lifetime: 36 months (from cohort data)
LTV = $500 × 0.80 × 36 = $14,400
```

**Healthy benchmarks** (Pacific Crest SaaS Survey):
- SaaS gross margin: 70-80%
- Enterprise customers: LTV typically 3-5 years of ARPU
- SMB customers: LTV typically 1-2 years of ARPU

**Common mistakes**:
- Using gross revenue instead of gross margin
- Not discounting future cash flows (for multi-year LTV, apply 10-15% discount rate)
- Assuming churn rate stays constant (usually improves over time)
- Including expansion revenue twice (already in ARPU if calculated properly)

---

## Customer Acquisition Cost (CAC)

**Definition**: Total sales and marketing cost to acquire one new customer.

**When to use**:
- Evaluating marketing channel efficiency
- Sales team hiring decisions
- Budget allocation across channels
- Setting growth targets

**How to calculate**:

**Blended CAC**:
```
CAC = (Total Sales & Marketing Expenses) / (Number of New Customers)

Example:
Q1 S&M spend: $150,000
New customers: 30
CAC = $150,000 / 30 = $5,000
```

**By-Channel CAC** (critical for optimization):
```
Channel CAC = (Channel-Specific Costs) / (Customers from Channel)

Example - Paid Search:
Ad spend: $20,000
Landing page tool: $500
Attribution: 15 customers
Paid Search CAC = $20,500 / 15 = $1,367
```

**Fully-Loaded CAC** (includes overhead):
```
Fully-Loaded CAC = (Total S&M + 50% of G&A allocated to S&M) / New Customers
```

**Healthy benchmarks** (David Skok):
- LTV:CAC ratio >3:1 (see below)
- CAC payback period <12 months for SMB, <18 months for enterprise

**Common mistakes**:
- Not including salaries, tools, overhead (only counting ad spend)
- Using sign-up count instead of paying customers
- Not separating organic from paid channels
- Ignoring assisted conversions (multi-touch attribution matters)

---

## LTV:CAC Ratio

**Definition**: How much lifetime value you generate per dollar spent acquiring customers.

**When to use**:
- Assessing business model sustainability
- Deciding when to raise prices or increase spend
- Investor pitch (this is a key metric VCs examine)

**How to calculate**:
```
LTV:CAC Ratio = LTV / CAC

Example:
LTV: $13,333
CAC: $5,000
Ratio = 13,333 / 5,000 = 2.67:1
```

**Healthy benchmarks** (David Skok, Bessemer):
- <1:1 — Business is broken
- 1:1-3:1 — Unprofitable or marginal
- 3:1-5:1 — Healthy, sustainable
- >5:1 — Underinvesting in growth (should spend more on sales/marketing)

**Common mistakes**:
- Using different time periods for LTV and CAC (must align)
- Not segment by customer type (enterprise vs SMB have vastly different ratios)
- Ignoring that early customers often have worse economics
- Treating 3:1 as target instead of minimum threshold

---

## CAC Payback Period

**Definition**: Months required to recover the cost of acquiring a customer.

**When to use**:
- Cash flow planning
- Determining sustainable growth rate
- Sales compensation design
- Credit line or fundraising decisions

**How to calculate**:
```
CAC Payback = CAC / (ARPU × Gross Margin %)

Example:
CAC: $5,000
ARPU: $500/month
Gross Margin: 80%
Payback = $5,000 / ($500 × 0.80) = 12.5 months
```

**Alternative (using actual cash data)**:
```
Payback Month = First month when cumulative gross profit > CAC
```

**Healthy benchmarks** (Jason Lemkin, SaaStr):
- SMB SaaS: <12 months (ideally 6-8)
- Mid-market: 12-18 months
- Enterprise: 18-24 months acceptable

**Common mistakes**:
- Using gross revenue instead of gross margin contribution
- Not accounting for onboarding/implementation costs
- Assuming linear revenue (many SaaS products have ramp periods)
- Forgetting that payback period should shrink as you scale

---

## Gross Margin for SaaS

**Definition**: Revenue minus direct costs of delivering the service (COGS).

**When to use**:
- Pricing decisions
- Infrastructure optimization
- Investor benchmarking
- LTV calculations

**How to calculate**:
```
Gross Margin % = ((Revenue - COGS) / Revenue) × 100

SaaS COGS typically includes:
- Hosting costs (AWS, GCP, Azure)
- Third-party API costs
- Customer support (if dedicated)
- Professional services for onboarding

Example:
MRR: $100,000
Hosting: $8,000
APIs: $3,000
Support: $5,000
Total COGS: $16,000
Gross Margin = ($100k - $16k) / $100k = 84%
```

**Healthy benchmarks** (SaaS Capital, Bessemer):
- Good SaaS: 70-75%
- Great SaaS: 80-85%
- Best-in-class: >85%
- Enterprise with services: 60-70% (acceptable if services are strategic)

**Common mistakes**:
- Including S&M or R&D in COGS (those are operating expenses)
- Not tracking unit economics as you scale (margins should improve)
- Ignoring free tier costs (they're real COGS)
- Mixing one-time setup fees with recurring margin

---

## Contribution Margin

**Definition**: Revenue minus variable costs (COGS + variable S&M per customer).

**When to use**:
- Understanding per-customer profitability
- Freemium conversion modeling
- Growth scenario planning

**How to calculate**:
```
Contribution Margin = Revenue - COGS - Variable Marketing Costs

Per Customer:
Contribution Margin = ARPU - (COGS per user + CAC / Expected Lifetime in Months)

Example:
ARPU: $500
COGS per user: $100
CAC: $5,000
Expected lifetime: 30 months
Monthly CAC burden = $5,000 / 30 = $167
Contribution Margin = $500 - $100 - $167 = $233/month
```

**Healthy benchmarks**:
- Industry benchmark (source needed): Positive contribution margin by month 12
- Negative contribution margin acceptable if payback <12 months

**Common mistakes**:
- Confusing contribution margin with gross margin
- Not amortizing CAC properly
- Ignoring customer success costs that scale with customer count
- Using blended metrics instead of cohort-specific data

---

## Monthly Unit Economics Checklist

**Week 1**:
1. Calculate last month's blended CAC
2. Update LTV using latest churn data
3. Check LTV:CAC ratio - flag if <3:1
4. Review gross margin - investigate if <75%

**Week 2**:
1. Break down CAC by channel
2. Identify best and worst performing channels
3. Calculate payback period for each segment

**Week 3**:
1. Update cohort retention curves
2. Recalculate LTV for each cohort
3. Check if older cohorts are improving (they should)

**Week 4**:
1. Prepare unit economics section for monthly board deck
2. Model impact of pricing changes on LTV:CAC
3. Recommend channel budget shifts based on CAC data

---

## Red Flags to Escalate Immediately

- LTV:CAC drops below 2:1 for two consecutive months
- CAC payback extends beyond 18 months
- Gross margin drops below 70%
- Blended CAC increases >20% month-over-month without explanation
- Any customer segment with negative LTV
