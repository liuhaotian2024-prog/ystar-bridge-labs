# L7B Revenue Opportunity Radar Lane Prompt

Worktree path: `../ystar-company-l7-revenue`
Branch: `l7/revenue-opportunity-radar`

Objective: Build a read-only revenue opportunity discovery radar that converts existing L6 evidence/review artifacts into internal opportunity packets.

Scoped files:
- `l7_revenue_opportunity_radar/**`
- `scripts/l7_lanes/build_l7b_revenue_opportunity_radar.py`

Forbidden actions:
- No customer contact, grant/RFP submission, publication, payment, account creation, form submission, revenue execution, or manual URL request.

Validation command:
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/l7_lanes/build_l7b_revenue_opportunity_radar.py`

Completion report fields:
- Opportunity packets generated
- Evidence/artifact basis
- Next safe step
- External actions blocked
- Human approval required before external action
