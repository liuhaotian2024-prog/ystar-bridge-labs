# Burn Rate Calculation Guide — CFO Financial Analysis

**Source:** AGENTS.md CFO Obligations章节  
**Moved to knowledge:** 2026-04-03（Constitutional cleanup）  
**Authority:** Board financial oversight

---

## Purpose

Calculate weekly and monthly burn rate to track company spending, forecast runway, and inform Board financial decisions.

## Data Sources

### Primary: Token Usage Logs

**Location:** `data/token_logs/YYYY-MM.jsonl`

**Format:**
```json
{
  "timestamp": "2026-04-03T14:30:22",
  "agent": "ystar-cfo",
  "model": "claude-sonnet-4-5",
  "tokens": {"input": 15234, "output": 3421, "total": 18655},
  "cost_usd": 0.28,
  "session_id": "xyz",
  "project": "ystar-company"
}
```

### Secondary: Fixed Costs

**Location:** `reports/cfo/fixed_costs.md`

**Categories:**
1. Claude Max subscription: $20/month per seat
2. USPTO patent fees: one-time (already paid)
3. Domain/hosting: $X/month (if applicable)
4. Third-party services: list any active subscriptions

---

## Calculation Methods

### Method 1: Weekly Burn Rate (Preferred for Short-term Tracking)

**Formula:**
```
Weekly Burn = Token Costs (past 7 days) + (Fixed Costs / 4.33)
```

**Steps:**

1. **Extract past 7 days of token logs:**
```bash
# Get start and end timestamps
START=$(date -d "7 days ago" +%s)
END=$(date +%s)

# Extract and sum costs
jq -r --argjson start "$START" --argjson end "$END" \
  'select(.timestamp >= ($start | todate) and .timestamp <= ($end | todate)) | .cost_usd' \
  data/token_logs/$(date +%Y-%m).jsonl \
  | awk '{sum+=$1} END {print sum}'
```

2. **Add prorated fixed costs:**
```
Fixed_Weekly = (Claude_Max_Monthly * Seats) / 4.33
```

3. **Total weekly burn:**
```
Weekly_Burn = Token_Costs_7days + Fixed_Weekly
```

**Example:**
```
Token costs (7 days): $12.34
Claude Max (3 seats): $60/month = $13.86/week
Weekly burn: $12.34 + $13.86 = $26.20
```

---

### Method 2: Monthly Burn Rate (For Runway Calculation)

**Formula:**
```
Monthly Burn = Token Costs (past 30 days) + Fixed Costs
```

**Steps:**

1. **Extract past 30 days:**
```bash
START=$(date -d "30 days ago" +%s)
END=$(date +%s)

jq -r --argjson start "$START" --argjson end "$END" \
  'select(.timestamp >= ($start | todate) and .timestamp <= ($end | todate)) | .cost_usd' \
  data/token_logs/$(date +%Y-%m).jsonl data/token_logs/$(date -d "1 month ago" +%Y-%m).jsonl \
  | awk '{sum+=$1} END {print sum}'
```

2. **Add monthly fixed costs:**
```
Fixed_Monthly = Claude_Max_Monthly * Seats + Other_Subscriptions
```

3. **Total monthly burn:**
```
Monthly_Burn = Token_Costs_30days + Fixed_Monthly
```

**Example:**
```
Token costs (30 days): $52.80
Claude Max (3 seats): $60/month
Other services: $0
Monthly burn: $52.80 + $60 = $112.80
```

---

### Method 3: Agent-Level Breakdown

**Purpose:** Understand which agents consume most resources

**Query:**
```bash
# Group by agent, sum costs
jq -r '.agent, .cost_usd' data/token_logs/$(date +%Y-%m).jsonl \
  | paste - - \
  | awk '{agents[$1]+=$2} END {for (a in agents) print a, agents[a]}' \
  | sort -k2 -rn
```

**Example output:**
```
ystar-cto 28.50
ystar-ceo 15.20
ystar-cmo 8.40
ystar-cfo 3.20
ystar-cso 1.80
```

**Analysis:**
- Which agent is most expensive?
- Is cost proportional to value delivered?
- Should we optimize agent prompts or model selection?

---

### Method 4: Model-Level Breakdown

**Purpose:** Optimize model selection for cost efficiency

**Query:**
```bash
# Group by model, sum costs
jq -r '.model, .cost_usd' data/token_logs/$(date +%Y-%m).jsonl \
  | paste - - \
  | awk '{models[$1]+=$2} END {for (m in models) print m, models[m]}' \
  | sort -k2 -rn
```

**Example output:**
```
claude-opus-4-6 35.60
claude-sonnet-4-5 18.20
claude-haiku-4-5 3.30
```

**Analysis:**
- Is Opus usage justified by task complexity?
- Could some Opus tasks be downgraded to Sonnet?
- Haiku usage (good for simple tasks)

---

## Runway Calculation

**Formula:**
```
Runway (months) = Available Capital / Monthly Burn Rate
```

**Steps:**

1. **Determine available capital:**
   - Board provides this (not tracked in code)
   - Example: $10,000 seed funding

2. **Calculate monthly burn** (Method 2 above)

3. **Compute runway:**
```
Runway = $10,000 / $112.80/month = 88.7 months
```

**Interpretation:**
- >12 months = healthy
- 6-12 months = monitor closely
- <6 months = urgent cost optimization or fundraising needed

---

## Weekly Report Template

**File:** `reports/cfo/burn_rate_YYYY-MM-DD.md`

```markdown
# Weekly Burn Rate Report

**Period:** [Start Date] to [End Date]  
**Prepared by:** CFO  
**Date:** [YYYY-MM-DD]

## Summary

| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Token Costs | $12.34 | $10.50 | +17.5% |
| Fixed Costs (prorated) | $13.86 | $13.86 | 0% |
| **Total Burn** | **$26.20** | **$24.36** | **+7.6%** |

## Token Usage by Agent

| Agent | Tokens | Cost | % of Total |
|-------|--------|------|------------|
| CTO | 125,430 | $6.50 | 52.7% |
| CEO | 89,210 | $4.20 | 34.0% |
| CMO | 22,100 | $1.34 | 10.9% |
| CFO | 5,020 | $0.30 | 2.4% |

## Token Usage by Model

| Model | Sessions | Tokens | Cost |
|-------|----------|--------|------|
| Opus 4.6 | 8 | 98,450 | $7.80 |
| Sonnet 4.5 | 15 | 132,210 | $4.24 |
| Haiku 4.5 | 3 | 11,100 | $0.30 |

## Notable Activity

- CTO: Heavy usage due to P0 bug fix sprint
- CEO: Preparing Board materials
- Opus usage spike: Complex architecture decisions

## Runway

**Current monthly burn:** $112.80  
**Available capital:** $10,000 (assumed)  
**Runway:** 88.7 months

## Recommendations

1. **Cost optimization opportunities:**
   - Consider downgrading routine tasks from Opus to Sonnet
   - Implement prompt caching for repetitive queries

2. **Trend analysis:**
   - Burn increased 7.6% this week (within normal variance)
   - Watch for sustained increases >20%

3. **Model selection:**
   - 63% of cost from Opus (8/26 sessions)
   - Verify all Opus usage is for complex tasks

## Next Week Forecast

**Predicted burn:** $24-28 (normal operations)  
**Risks:** None identified  
**Opportunities:** Prompt optimization could reduce 10-15%
```

---

## Automation Scripts

### Script 1: Weekly Burn Calculation

**Location:** `scripts/calculate_burn.sh`

```bash
#!/bin/bash
# Calculate weekly burn rate

DAYS=7
START=$(date -d "$DAYS days ago" +%s)
END=$(date +%s)

# Token costs
TOKEN_COST=$(jq -r --argjson start "$START" --argjson end "$END" \
  'select(.timestamp >= ($start | todate) and .timestamp <= ($end | todate)) | .cost_usd' \
  data/token_logs/*.jsonl | awk '{sum+=$1} END {printf "%.2f", sum}')

# Fixed costs (prorated)
CLAUDE_MAX=60  # $60/month for 3 seats
FIXED_WEEKLY=$(echo "$CLAUDE_MAX / 4.33" | bc -l | xargs printf "%.2f")

# Total
TOTAL=$(echo "$TOKEN_COST + $FIXED_WEEKLY" | bc | xargs printf "%.2f")

echo "Token costs: \$$TOKEN_COST"
echo "Fixed costs (prorated): \$$FIXED_WEEKLY"
echo "Total weekly burn: \$$TOTAL"
```

### Script 2: Agent Breakdown

**Location:** `scripts/agent_costs.sh`

```bash
#!/bin/bash
# Breakdown costs by agent

echo "Agent cost breakdown (this month):"
jq -r '.agent, .cost_usd' data/token_logs/$(date +%Y-%m).jsonl \
  | paste - - \
  | awk '{agents[$1]+=$2} END {for (a in agents) printf "%s: $%.2f\n", a, agents[a]}' \
  | sort -t'$' -k2 -rn
```

---

## Quality Checks

**Before submitting weekly report:**

- ✅ Token logs complete for full 7 days
- ✅ No missing session recordings
- ✅ Fixed costs up to date
- ✅ Calculations verified (manual spot check)
- ✅ Trend comparison with last week
- ✅ Anomalies explained in "Notable Activity"

---

## Troubleshooting

### Missing token logs

**Symptom:** Gaps in `data/token_logs/*.jsonl`

**Cause:** Agent forgot to run `track_burn.py`

**Fix:** 
1. Reconstruct from Claude Code session history
2. Estimate if exact data unavailable
3. Note in report: "Estimated due to missing log"

### Inconsistent model pricing

**Symptom:** Cost doesn't match expected pricing

**Cause:** Model pricing changed, or incorrect pricing in script

**Fix:**
1. Update `scripts/model_pricing.json`
2. Recalculate past week with correct pricing
3. Note correction in report

### Sudden cost spike

**Symptom:** Burn increased >50% week-over-week

**Causes:**
- P0 bug requiring extended sessions
- New feature development
- External research (WebSearch costs)

**Analysis:**
1. Check agent breakdown - which agent spiked?
2. Check session summaries - what work was done?
3. Assess if spike is one-time or sustained
4. Report to Board if sustained increase

---

**Last updated:** 2026-04-03  
**Scripts location:** `scripts/calculate_burn.sh`, `scripts/agent_costs.sh`  
**Next review:** When pricing model changes
