# Y*gov Discount Authority Matrix

**Effective Date:** 2026-04-13  
**Owner:** CFO (Marco), approved by Board  
**Status:** INTERNAL USE ONLY — DO NOT DISTRIBUTE EXTERNALLY  
**L:** L3-CONFIDENTIAL (competitive intel + negotiation strategy)

---

## Purpose

This matrix defines who can approve discounts during sales negotiations. Aligns with **AMENDMENT-005 RAPID decision framework** (Board → CEO → C-suite delegation).

---

## Discount Approval Authority

| Discount Range | Approver | Conditions | Typical Use Case |
|----------------|----------|------------|------------------|
| **0-10%** | CSO (Zara) | Any customer, any tier. No approval required. | Annual prepay incentive, multi-year commit, volume discount (3+ Team tier seats). |
| **11-20%** | CSO (Zara) | Requires written justification in CRM. Report to CFO within 24h. | Competitive displacement (customer switching from competitor), strategic partnership, early adopter discount. |
| **21-35%** | CEO (Aiden) | Requires written justification + CFO sign-off on unit economics. | Enterprise land deal (>$20k/year ACV), reference customer commitment, co-marketing agreement. |
| **36-50%** | CEO (Aiden) + Board notification | Requires Board notification within 48h. CFO must confirm deal remains profitable. | Strategic anchor customer (Fortune 500, regulatory validation), patent/IP cross-license, market entry deal (first customer in new vertical). |
| **>50%** | Board (Haotian Liu) only | Explicit Board approval required before quote. | Non-monetary strategic value only (e.g., government contract for credibility, academic research partnership). |

---

## Non-Discount Concessions (Require Same Approval Level as Equivalent Discount)

| Concession | Equivalent Discount | Approver |
|------------|---------------------|----------|
| **Extended payment terms** (net-60, net-90) | 5-10% | CSO (≤net-60), CEO (>net-60) |
| **Custom onboarding** (>10h professional services) | 10-15% | CEO |
| **Custom domain pack development** (waived $500-1,500 fee) | 15-20% | CEO |
| **SLA upgrade** (99.9% → 99.95%, or 4h → 1h CSM response) | 10-15% | CEO |
| **Free pilot extension** (>30 days) | 5% per additional 30 days | CSO (≤60 days total), CEO (>60 days) |

---

## Prohibited Discounts (Board Approval Required)

The following discounts are **prohibited without explicit Board approval**, regardless of percentage:

1. **Multi-tier downgrade after contract signing** (e.g., Enterprise → Team after first year).
2. **Perpetual license** (Y*gov is SaaS-only; no perpetual pricing without Board approval).
3. **Revenue share or equity swap** (instead of cash payment).
4. **Free Enterprise tier** (free Team tier is OK for strategic partners; Enterprise requires Board approval).
5. **Unbundled pricing** (selling CIEU audit trail without governance engine, or vice versa).

---

## Discount Justification Requirements

All discounts **>10%** must include the following in CRM notes:

1. **Why this discount?** (competitive pressure, strategic value, volume commit, etc.)
2. **What did we get in return?** (annual prepay, case study, reference, co-marketing, etc.)
3. **Is the deal still profitable?** (CFO must confirm unit economics remain positive.)
4. **Competitor intel** (if competitive displacement: who are we displacing? what was their price?)

---

## Volume Discount Schedule (Pre-Approved by CFO)

CSO can quote the following volume discounts **without additional approval**:

| Volume (Annual Contract Value) | Discount |
|--------------------------------|----------|
| $2,000-5,000/year | 10% |
| $5,001-10,000/year | 15% |
| $10,001-25,000/year | 20% |
| $25,001-50,000/year | 25% |
| >$50,000/year | Custom (CEO approval required) |

**Example:**
- 5 Team tier seats ($79/mo each) = $4,740/year → eligible for 10% discount → $4,266/year.
- 1 Enterprise tier ($899/mo base) = $10,788/year → eligible for 15% discount → $9,170/year.

---

## Annual Prepay Discount (Standard, Pre-Approved)

| Payment Terms | Discount |
|---------------|----------|
| **Monthly billing** | 0% (list price) |
| **Annual prepay** | 20% |
| **Multi-year prepay (2-year)** | 25% |
| **Multi-year prepay (3-year)** | 30% |

**Example:**
- Team tier: $79/mo monthly = $948/year.
- Team tier annual prepay: $758/year (20% off).
- Team tier 2-year prepay: $1,422 ($711/year, 25% off).

---

## Competitive Displacement Bonus (Pre-Approved)

If customer is switching from a direct competitor (LangSmith, Datadog LLM Observability, or similar), CSO can offer:

- **Additional 10% discount** (on top of volume/prepay discounts, max 20% total without CEO approval).
- **Free onboarding** (up to 5 hours professional services, normally $200/hour).
- **30-day extended trial** (Team or Enterprise tier, full feature access).

**Proof required:** Screenshot of competitor invoice or written attestation from customer.

---

## Strategic Partner Discount (CEO Approval Required)

For **strategic partnerships** (co-marketing, joint ventures, integration partners), CEO can approve:

- **Up to 40% discount** for annual contracts.
- **Free Team tier** (indefinitely, as long as partnership is active).
- **Revenue share model** (Board approval required if >40% discount equivalent).

**Examples of strategic partners:**
- Claude Code marketplace (Anthropic partnership).
- LangChain integration partner.
- Academic research institutions (Harvard, MIT, Stanford for governance research).

---

## Emergency Discount Authority (Time-Sensitive Deals)

If a deal requires **<24h turnaround** and CEO/Board is unavailable:

1. **CSO can approve up to 25%** (instead of normal 20% limit).
2. **Must notify CEO + CFO within 6 hours** (Slack + email).
3. **Ratification required within 48 hours** (CEO reviews and confirms or claws back deal).

**Use case:** Customer procurement deadline, competitive bid scenario, end-of-quarter close.

---

## Escalation Process

### If Customer Asks for Discount Beyond Your Authority:

1. **Log request in CRM** (Salesforce/HubSpot/Notion).
2. **Prepare justification** (see "Discount Justification Requirements" above).
3. **Escalate to next level:**
   - CSO → CEO (Slack: `@aiden`, email: aiden@ystar.ai)
   - CEO → Board (email: haotian@ystar.ai, subject: "URGENT: Discount Approval Request")
4. **Response SLA:**
   - CSO → CEO: 4 business hours.
   - CEO → Board: 24 hours (48h for >50% discounts).

### If Approval Denied:

1. **Communicate value, not price.** ("Our audit trail prevented a $500k breach for [customer X]. What's your cost of a single incident?")
2. **Offer non-discount concessions.** (Extended trial, custom onboarding, case study participation.)
3. **Walk away if unprofitable.** (A bad deal is worse than no deal. CFO can veto any deal with negative unit economics.)

---

## CFO Veto Rights

CFO (Marco) can **veto any deal** (regardless of discount approval level) if:

1. **Unit economics are negative** (cost to serve > revenue after discount).
2. **Payment terms create cash flow risk** (e.g., net-180 for a startup with <6mo runway).
3. **Customer has credit risk** (bankruptcy, payment default history).
4. **Deal structure violates revenue recognition** (GAAP/IFRS compliance).

**Veto process:**
1. CFO notifies CEO + CSO in writing (Slack + email).
2. CSO has 24h to revise deal structure.
3. If unresolvable, CEO makes final call (can override CFO with Board notification).

---

## Reporting Requirements

### Weekly (CSO → CFO)
- Total discounts given ($ and %).
- Breakdown by discount range (0-10%, 11-20%, 21-35%, etc.).
- Competitive displacement count.

### Monthly (CFO → Board)
- Average discount % by tier (Team, Enterprise).
- Top 5 deals by discount % (with justifications).
- Unit economics impact (gross margin before/after discounts).

### Quarterly (CFO → Board)
- Discount policy effectiveness (are we leaving money on the table? are deals profitable?).
- Recommendation for policy updates (tighten or loosen discount authority).

---

## Audit Trail (Y*gov Governance Applied to Ourselves)

Every discount approval **>10%** must be logged in:

1. **CRM** (Salesforce/HubSpot/Notion) with justification.
2. **CIEU audit log** (if sales agent is AI-powered in the future).
3. **Finance tracker** (`finance/discount_log.md`, CFO maintains).

**CASE-002 protocol applies:** No fabricated discounts. Every discount must trace to a real customer, real negotiation, real approval.

---

## Amendment History

| Date | Amendment | Approver |
|------|-----------|----------|
| 2026-04-13 | Initial version (aligns with AMENDMENT-005 RAPID) | Board (Haotian Liu) |

---

**Next Review Date:** 2026-07-13 (quarterly review, align with Q2 close)
