# Pricing Strategy Framework

## Value Metric Selection

**Definition**: The unit by which you charge customers - what they pay for as they use more.

**When to use**:
- Designing initial pricing model
- Pivoting from unprofitable pricing
- Launching new product tiers

**Common value metrics by product type**:
- **Per-seat**: Users, team members (e.g., Slack, Notion)
- **Per-usage**: API calls, compute hours, storage GB (e.g., AWS, Stripe)
- **Per-outcome**: Leads generated, revenue processed (e.g., HubSpot, Shopify)
- **Per-feature**: Access to modules or capabilities (e.g., Adobe tiers)

**Step-by-step selection process**:

1. **List what correlates with customer value**
   - Interview 5-10 customers: "As you get more value, what increases?"
   - Common answers: team size, revenue, volume processed, features used

2. **Evaluate against criteria**
   - Easy to understand? (Can customers predict their bill?)
   - Grows with usage? (Aligns with customer success)
   - Hard to game? (Can't be easily circumvented)
   - Example: "Per project" fails if customers can stuff unlimited work into one project

3. **Test growth alignment**
   - Best metric: grows naturally as customer gets more value
   - Poor metric: requires customer to buy more before they see value

4. **Validate with data**
   - Analyze existing customers: does metric correlate with retention?
   - Check willingness to pay: do high-metric customers pay more happily?

**Healthy benchmarks** (Patrick Campbell, ProfitWell):
- Companies with usage-based pricing grow 38% faster than per-seat (ProfitWell 2021 data)
- Hybrid models (base + usage) have 23% higher NRR

**Common mistakes**:
- Choosing a metric that doesn't scale (per company = no expansion revenue)
- Too complex (e.g., "per API call type weighted by compute cost")
- Misaligned incentives (charging per email sent when you want more engagement)
- Copying competitors without understanding your value delivery

---

## Pricing Tier Design

**Definition**: Creating 2-4 packages at different price points to serve different customer segments.

**When to use**:
- Initial product launch
- Expanding from single tier to multi-tier
- Annual pricing review

**Step-by-step tier creation**:

1. **Identify 2-3 distinct customer segments**
   ```
   Example for Y*gov:
   - Individual developers (learning, side projects)
   - Small teams (startups, 2-10 people)
   - Enterprises (compliance requirements, scale)
   ```

2. **Define capabilities per tier using good/better/best**
   ```
   Tier 1 (Free/Low): Core value, limited scale
   Tier 2 (Mid): Remove limitations, add collaboration
   Tier 3 (High): Add enterprise features (SSO, audit, SLA)
   ```

3. **Set anchor price points**
   - Find competitor pricing for similar segments
   - Aim for 3-5x multiplier between tiers (e.g., $49, $199, $999)
   - Bottom tier: customer acquisition
   - Top tier: margin and positioning

4. **Design feature gates that encourage upgrades**
   ```
   Good gates:
   - User limits (forces growth to upgrade)
   - Collaboration features (team value > individual value)
   - Compliance/security (enterprises must have)

   Bad gates:
   - Artificial limits on core features
   - Removing features customers already used
   ```

5. **Create visual pricing page**
   - Show all tiers side-by-side
   - Highlight recommended tier (usually middle)
   - Use annual discount to encourage longer commits

**Healthy benchmarks** (Price Intelligently):
- 3 tiers optimal for SaaS (more than 4 creates decision paralysis)
- Middle tier should be 60-70% of new sales (if not, tiers are poorly designed)
- 10-20% annual prepay discount is standard

**Common mistakes**:
- Too many tiers (>4 causes analysis paralysis)
- Bottom tier too generous (cannibalizes paid tiers)
- Feature distribution doesn't match value perception
- Pricing page focuses on features, not outcomes
- Not having a clear upgrade path

---

## Freemium vs Free Trial

**Definition**:
- **Freemium**: Free tier with limitations, paid upgrades (keep forever)
- **Free trial**: Full access for limited time (14-30 days typical)

**When to use each**:

**Choose Freemium if**:
- Low marginal cost to serve free users (COGS <$5/user/month)
- Viral/network effects (more users = more value for paid users)
- Long evaluation cycle (developers, technical products)
- Need large user base for conversion funnel
- Example: Slack, Figma, GitHub

**Choose Free Trial if**:
- High cost to serve (infrastructure, support)
- Clear value demonstration in <30 days
- Sales-assisted model (demo + trial + close)
- Immediate ROI for customer
- Example: Enterprise analytics, compliance tools

**Choose Hybrid** (limited free + trial of premium):
- Complex product with basic free use case
- Want community + paid customers
- Example: Notion (free personal, trial team features)

**Step-by-step freemium design**:

1. **Calculate affordable free tier cost**
   ```
   Max cost per free user = (Target paid conversion rate × LTV × Acceptable CAC %) / Free users needed per conversion

   Example:
   2% conversion, $5,000 LTV, willing to spend 20% on CAC
   Max free cost = (0.02 × $5,000 × 0.20) / 50 = $0.40/user/month
   ```

2. **Set free tier limits that force upgrade at value inflection**
   - Don't gate on time (defeats freemium model)
   - Gate on team size, usage volume, or advanced features
   - Example: "Free for 1 user, $49/mo for teams"

3. **Design upgrade prompts**
   - Show upgrade CTA when user hits limit
   - Demonstrate what they'd unlock
   - Make upgrade frictionless (1-click billing)

**Healthy benchmarks** (OpenView Partners):
- Freemium conversion rate: 2-5% to paid (industry benchmark)
- Free trial conversion: 15-25% (source needed)
- Best freemium: conversion happens within 60-90 days

**Common mistakes**:
- Freemium tier too generous (no reason to upgrade)
- Free trial too short for complex products
- Not nurturing free users (treat as long sales cycle)
- Mixing models (confusing free tier + trial)
- No clear upgrade trigger

---

## Usage-Based Pricing

**Definition**: Customers pay based on consumption (API calls, seats, storage, compute) rather than fixed subscription.

**When to use**:
- Product has variable usage patterns
- Usage correlates directly with customer value
- Infrastructure costs scale with usage
- Want to reduce barrier to entry

**Step-by-step implementation**:

1. **Choose base unit of consumption**
   - Must be measurable, understandable, predictable
   - Examples: API calls, GB stored, hours computed, transactions processed

2. **Set pricing per unit**
   ```
   Cost-plus method:
   Unit Price = (Infrastructure Cost per Unit × 3-5x markup) + Margin

   Value-based method:
   Survey customers: "How much value does 1,000 units provide?"
   Price = Fraction of value delivered
   ```

3. **Add base tier or minimums**
   ```
   Common models:
   - Pure usage: $0.01 per API call (AWS model)
   - Base + usage: $49/mo + $0.005 per call over 10,000 (Stripe model)
   - Committed use: $499/mo for 100k calls, then $0.003 overage (enterprise model)
   ```

4. **Build usage dashboard for customers**
   - Real-time usage visibility
   - Spending alerts
   - Usage forecasting
   - Critical for trust and retention

5. **Test pricing granularity**
   - Too fine-grained: $0.0001 per call (confusing)
   - Too coarse: $100 per 1M calls (big jumps)
   - Aim for: customer can estimate monthly bill within 20%

**Healthy benchmarks** (OpenView SaaS Benchmarks):
- Usage-based companies have 20-30% higher NRR (OpenView 2022)
- Typical margin on usage pricing: 70-80%
- Budget predictability: customers should forecast spend within ±25%

**Common mistakes**:
- Unpredictable bills (customers churn from bill shock)
- No spending limits or alerts
- Pricing units don't match customer mental model
- Can't estimate cost before using
- Infrastructure costs aren't actually variable (kills margin)

---

## Competitive Pricing Analysis

**Definition**: Systematic research of how competitors price similar products.

**When to use**:
- Setting initial pricing
- Quarterly pricing reviews
- Entering new market segment
- Responding to competitor launches

**Step-by-step process**:

1. **Identify 5-10 direct and adjacent competitors**
   - Direct: solve same problem, same buyer
   - Adjacent: different approach, same outcome

2. **Build pricing comparison matrix**
   ```
   Create spreadsheet with:
   - Competitor name
   - Pricing tiers (names + prices)
   - Value metric (per seat, per usage, etc.)
   - Key features per tier
   - Free tier or trial details
   - Annual discount %
   - Add-on pricing
   ```

3. **Normalize for comparison**
   - Convert all to monthly equivalent
   - Calculate effective price per user/unit
   - Note: list price vs. actual discount practices

4. **Analyze positioning**
   - Where are you in price range? (premium, mid, budget)
   - What features justify price differences?
   - Who anchors high? Who anchors low?

5. **Secret shop their sales process**
   - Request demo/trial
   - Note discount flexibility
   - Understand their value pitch
   - Learn objection handling

**Healthy benchmarks**:
- Industry benchmark (source needed): pricing review every 6-12 months
- Price increases: 5-10% annually for existing customers (with value adds)

**Common mistakes**:
- Only comparing list prices (ignore negotiation, discounts)
- Not comparing apples-to-apples features
- Competing on price instead of value
- Copying competitor pricing without understanding their economics
- Ignoring adjacent/substitute products

---

## Price Anchoring

**Definition**: Strategic placement of high-priced option to make target price seem reasonable.

**When to use**:
- Designing pricing page
- Introducing new premium tier
- Negotiating enterprise deals

**Step-by-step implementation**:

1. **Create decoy tier**
   - Add tier priced 2-3x your target tier
   - Include features only 5-10% of customers need
   - Makes target tier look like "smart choice"

2. **Visual anchoring on pricing page**
   ```
   Layout:
   [Basic] [Popular - HIGHLIGHT THIS] [Premium] [Enterprise]
   $29       $99 (SAVE 40% badge)       $299      Custom
   ```

3. **Show annual savings**
   - Display monthly price with "billed annually"
   - Show strikethrough monthly price: ~~$129~~ $99/mo

4. **Cross-out original price**
   - "Was $149, now $99" (for limited promotions)
   - Only use if time-bound, not permanent

**Common mistakes**:
- Decoy tier has no realistic use case (customers see through it)
- Too many tiers dilutes anchoring effect
- Anchor price is so high it lacks credibility

---

## Willingness-to-Pay Research

**Definition**: Structured method to discover what customers will actually pay for your product.

**When to use**:
- Before setting initial pricing
- Before major pricing change
- When considering new tier or feature

**Step-by-step Van Westendorp method** (Price Sensitivity Meter):

1. **Survey 50-100 target customers with 4 questions**:
   - At what price is this too expensive (you wouldn't consider it)?
   - At what price is it expensive but you'd consider it?
   - At what price is it a good deal?
   - At what price is it so cheap you'd question quality?

2. **Plot results**
   - X-axis: price points
   - Y-axis: % of respondents
   - Find intersections:
     - Point of Marginal Cheapness (PMC)
     - Point of Marginal Expensiveness (PME)
     - Optimal price: midpoint between PMC and PME

3. **Validate with A/B test**
   - Test ±20% around optimal price
   - Measure conversion rate, not just clicks
   - Run for statistical significance (100+ conversions per variant)

**Alternative: Conjoint analysis** (for complex products):
- Show customers pairs of feature bundles + prices
- Ask which they prefer
- Software calculates feature value and price sensitivity

**Healthy benchmarks** (Madhavan Ramanujam, "Monetizing Innovation"):
- Willingness-to-pay research should happen before building (not after)
- 10x more companies fail from underpricing than overpricing

**Common mistakes**:
- Asking "What would you pay?" (people lowball)
- Only surveying existing customers (they're anchored to current price)
- Not segmenting by customer type
- Confusing "willingness to pay" with "current budget"
- Trusting stated intent over revealed preference (watch behavior, not surveys)

---

## Monthly Pricing Review Checklist

**Week 1**:
1. Update competitive pricing matrix
2. Check for new entrants or pricing changes
3. Flag any competitors who dropped prices

**Week 2**:
1. Analyze conversion rate by tier
2. Calculate revenue per tier
3. Identify underperforming tiers

**Week 3**:
1. Review customer feedback on pricing (support tickets, churn surveys)
2. Identify most common upgrade/downgrade paths
3. Check if free tier conversion is on target (2-5%)

**Month End**:
1. Calculate effective price (revenue / customers)
2. Model impact of 10% price increase on revenue and churn
3. Recommend pricing experiments for next quarter

---

## When to Increase Prices

**Signals you should raise prices**:
- LTV:CAC ratio >5:1 (underpricing)
- Conversion rate >40% (no price resistance)
- Net Revenue Retention >120% (customers see value)
- Strong competitive position (defensible differentiation)

**How to execute**:
1. Grandfather existing customers for 6-12 months
2. Add new features to justify increase
3. Communicate value, not just price change
4. Raise 10-20% per year (digestible)
5. A/B test on new customers first
