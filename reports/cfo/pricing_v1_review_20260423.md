---
date: 2026-04-23
reviewer: Marco (CFO)
reviewed_document: reports/ceo/pricing_proposal_v1_20260423.md
goal_id: Y_001_3
verdict: SHIP WITH ADJUSTMENTS
---

# CFO Financial Review — Y*gov Pricing v1

## Verdict One-Liner

**SHIP WITH ADJUSTMENTS**: Tier 2 underpriced for value delivered. Recommend $129/seat (up from $99). Tier 3 economics solid. Free tier CAC acceptable given funnel assumptions.

---

## Unit Economics Table Per Tier

| Tier | Price | Est. COGS/mo | Gross Margin | Break-Even Vol | Recommendation |
|------|-------|--------------|--------------|----------------|----------------|
| **Tier 1 (Free)** | $0 | $8 (compute + storage + 7-day retention) | N/A | N/A | ACCEPTABLE as funnel cost. Max 500 accounts before COGS > CAC efficiency. |
| **Tier 2 (Team)** | $99/seat × 3 min = $297 | $45 (compute + 90-day storage + K9 sampling + support ~$15/team) | ~85% | 1 team | **RAISE TO $129/seat** ($387 min). Justification: Datadog $15/host, Snyk $50/user benchmarks support governance premium. Current $99 leaves 40% margin on table. |
| **Tier 3 (Enterprise)** | $2,500 base + $500/seat (min 10 = $7,500) | $1,200 (dedicated env $800 + SLA support $300 + compliance export $100) | ~84% | 1 customer | ACCEPT. Gross margin healthy. $7.5k/mo = $90k/yr vs Vanta $15k+/yr positions us 6x cheaper — room to move up if deals close easy. |

**Key COGS assumptions**:
- Compute (CROBA + CIEU + field decomposer): est. $3-5/agent/month at AWS spot + Gemma localhost hybrid (CTO verify)
- Storage (CIEU Merkle chain): $0.50/GB/month × 2GB avg/team = $1/team (Tier 2), unlimited retention Tier 3 = $8/customer avg
- Support: Tier 2 = async Slack ($15/team/month avg), Tier 3 = 4h SLA = 0.2 FTE support × $6k/mo = $1,200/customer (amortized over 10 customers = $120/customer, scales down as volume grows)

**COGS credibility check**: CEO/CTO must verify compute costs with real dogfood token burn data. I assume `track_burn.py` logs exist but I haven't seen November 2025–March 2026 aggregate compute spend. If actual COGS > my estimates, Tier 2 $129 becomes mandatory not optional.

---

## Top 3 Risks + Mitigation

### Risk 1: Tier 2 $99 Perceived-Value Trap
**Problem**: Pricing below Cursor ($20), Copilot ($19), Linear ($8) is defensible, but $99 for "governance tool" vs $19 for "code autocomplete" may trigger buyer skepticism — "why 5x more expensive than Copilot if both are dev tools?"

**Mitigation**:
- Reframe buyer persona: **CTO/Compliance Officer** (budget $500-2k/seat/year for audit/security tools), NOT individual developer (budget $20/month for productivity).
- Comp set on pricing page must anchor against Vanta ($1,250/mo), Drata ($625/mo), Datadog ($15/host × 50 hosts = $750/mo), NOT against Cursor/Copilot.
- Bundle messaging: "governance + audit + compliance" not "AI tool for devs."

**Adjusted verdict**: Raise to $129 closes perception gap (5.4x Copilot feels premium but defensible vs 4.2x feels "why?").

### Risk 2: Year 1 ARR Forecast Assumes 8 Teams + 2 Enterprise with ZERO CAC Data
**Problem**: CEO baseline assumes 8 Tier 2 teams ($47.5k ARR) and 2 Tier 3 enterprise ($192k ARR) but provides no CAC estimate, no channel breakdown, no lead source assumptions.

**Reality check**:
- If blended CAC = $5k (SaaS standard for $99/seat product), acquiring 8 teams = $40k spend.
- If enterprise CAC = $25k (complex sale, 6-month cycle), 2 customers = $50k spend.
- **Total S&M Year 1 burn: ~$90k** to hit $240k ARR baseline.
- LTV:CAC check: Tier 2 LTV = $99 × 5 seats × 30 months (assume 10% monthly churn) × 0.85 margin = $12,600. CAC $5k → ratio 2.5:1 (BELOW 3:1 threshold, marginal).

**Mitigation**:
- CSO (Zara) must provide lead gen cost model for Pharma/AI-first outreach before Y_001 ships.
- If CAC > $8k for Tier 2, pricing MUST go to $149/seat to hit 3:1 LTV:CAC minimum.
- Tier 3 economics safer: LTV = $7,500 × 36 months × 0.84 margin = $226k, CAC $25k → 9:1 ratio (healthy).

### Risk 3: 20% Annual Discount (10 Months for 12) Front-Loads Churn Risk
**Problem**: Annual discount standard in SaaS, but 20% is aggressive for unproven product. If customer churns at month 8 of prepaid annual, we've delivered 8 months for 10-month revenue but eaten 20% margin.

**Data gap**: CEO assumes "5-7% monthly gross churn" (SaaS standard) but Y*gov has ZERO customer retention data. First 12 months will be experimental cohort with likely higher churn (15-20% not 5-7%).

**Mitigation**:
- Reduce annual discount to 15% (industry median per ProfitWell data) for Year 1.
- OR require annual prepay (no monthly option for annual discount) — protects cash flow.
- After 6 months of retention data, re-evaluate discount aggressiveness.

---

## Recommended Adjustments (Specific Numbers)

1. **Tier 2 pricing: $99 → $129/seat**
   - New minimum (3 seats): $387/mo (was $297)
   - Rationale: Gross margin improvement ($45 COGS → 65% margin at $99 vs 72% at $129), better comp-set anchoring (Datadog/Snyk range), LTV:CAC buffer for CAC uncertainty.
   - Downside: May reduce conversion from Tier 1 free (2-5% assumed). Suggest A/B test $99 vs $129 on first 100 free→paid conversions.

2. **Annual discount: 20% → 15%**
   - Protects margin during high-churn Year 1 learning phase.
   - Still competitive (Vanta/Drata typically 10% annual discount).

3. **Tier 1 free cap: 500 accounts → add wait-list trigger at 300**
   - COGS risk: 500 × $8 = $4k/month burn with zero revenue.
   - At 300 accounts, activate wait-list for new free signups unless Tier 2 conversion hits 3% (9 paying teams).
   - Prevents runaway CAC if free tier becomes viral without paid conversion.

4. **Stripe SKU naming: add "_v1" suffix**
   - `ystar_team_pro_seat_v1`, `ystar_enterprise_base_v1`
   - Allows price changes in 6 months without Stripe SKU conflicts (create `_v2` SKUs, migrate customers).
   - Technical debt prevention.

---

## Next Steps (Rt+1=0 Path)

### CFO Scope (My Deliverables)
1. **Ratify adjusted pricing to `finance/pricing_v1.md`** (blocked on Board approval of $129 vs $99 decision)
2. **Build revenue forecast model** with CAC sensitivity analysis (3 scenarios: CAC $3k / $5k / $8k)
3. **Coordinate with CTO on Stripe setup**: SKU creation, webhook for MRR tracking, invoice auto-send
4. **Set up MRR dashboard**: weekly tracking starts when first paid customer converts (target: track_burn.py integration for COGS vs MRR margin analysis)

### CEO Must Provide Before Board Ratification
1. **Dogfood compute cost data**: What's actual Nov 2025–Mar 2026 CIEU + CROBA + field-decomposer token burn? My COGS estimates are theoretical.
2. **CAC assumption defense**: Where do 8 teams + 2 enterprise come from? Cold outreach? Inbound? Conference? Need channel breakdown.

### CTO Must Provide (Y_001 Blocker)
1. **Stripe product SKU setup** (4 SKUs per table above, `_v1` suffix)
2. **Feature flag enforcement** per tier (1 agent Tier 1, 10 agents Tier 2, unlimited Tier 3)
3. **CIEU retention policy** (7-day auto-delete Tier 1, 90-day Tier 2, unlimited Tier 3)

### CSO (Zara) Must Provide
1. **Lead gen cost estimate** for Pharma/AI-first outreach (needed for CAC model validation)
2. **First 10 enterprise prospect list** with willingness-to-pay signals (validates $7.5k/mo price point)

---

## CFO Notes to Board

**M-3 Value Production alignment**: Pricing model financially viable IF Tier 2 raised to $129. At $99, LTV:CAC margin too thin to survive CAC uncertainty in Year 1.

**Burn multiple projection**: Assuming $90k S&M spend Year 1 to acquire $240k ARR → burn multiple 0.375 (EXCELLENT, top quartile per David Sack). But this assumes CAC estimates hold — if CAC doubles, burn multiple → 0.75 (still acceptable).

**Revenue confidence**: Tier 3 ($192k of $240k baseline) carries the business. Tier 2 is acquisition funnel, not margin driver in Year 1. If enterprise deals slip (pharma sales cycles = 9-12 months), Year 1 ARR could be $50k not $240k. Recommend CEO/CSO focus 80% energy on Tier 3 pipeline, not Tier 2 volume.

**Honest gap (Rt+1 > 0)**: I have NOT seen real token burn data, real CAC from Zara's outreach, or real churn assumptions tested. These numbers are framework-compliant estimates, NOT empirical. CASE-002 Protocol: I label this **ESTIMATE** explicitly. Board should not ratify pricing until CTO/CEO/CSO provide data backing.

---

**File**: `reports/cfo/pricing_v1_review_20260423.md` | **Lines**: 152 | **Verdict**: SHIP WITH ADJUSTMENTS ($129 Tier 2, 15% annual discount, 300-account free cap)
