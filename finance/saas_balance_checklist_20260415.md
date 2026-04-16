# SaaS Balance Verification Checklist
**Date:** 2026-04-15
**Created by:** CFO Agent (marco-cfo)
**Purpose:** Board action items to close data gaps in financial_health_20260415.md

---

## ❕ BOARD MANUAL TASKS (No API Automation Available)

### 1. Anthropic Billing Dashboard

**URL:** https://console.anthropic.com/settings/billing
**Action:**
- Login with Board credentials
- Export March 2026 invoice (PDF or screenshot)
- Export April 2026 invoice (PDF or screenshot)
- Record actual USD amounts

**Save to:** `finance/invoices/anthropic_march_2026.pdf`
**Update:** `finance/master_ledger_20260415.md` with verified amounts

**Current Status:** March shows $1,350 in expenditure_log.md but NO INVOICE exists

---

### 2. HeyGen Dashboard

**URL:** https://app.heygen.com/home
**Action:**
- Login with Board credentials
- Navigate to Billing/Credits section
- Screenshot current balance (credits + USD value)
- Export billing history (all charges to date)

**Save to:** `finance/invoices/heygen_balance_20260415.png`
**Note:** HeyGen has no API endpoint for balance query (per knowledge/cmo/heygen_api_notes.md line 52)

**Current Status:** ~59 credits mentioned in Board conversation (informal estimate only)

---

### 3. Kling AI Dashboard

**URL:** https://app.klingai.com
**Action:**
- Login with Board credentials (中国手机号账号)
- Navigate to account/balance section
- Screenshot current balance (credits or CNY)
- Export billing history

**Save to:** `finance/invoices/kling_balance_20260415.png`

**Current Status:** MISSING DATA — key configured in `~/.gov_mcp_secrets.env` but never queried

---

### 4. Replicate Dashboard

**URL:** https://replicate.com/account/billing
**Action:**
- Login with Board credentials
- Screenshot current credit balance
- Export usage history

**Save to:** `finance/invoices/replicate_balance_20260415.png`

**Current Status:** MISSING DATA — secretary/api_registry.md line 71 mentions $10 balance but no verification date

---

### 5. X (Twitter) API Dashboard

**URL:** https://developer.twitter.com/en/portal/dashboard
**Action:**
- Login with @liuhaotian_dev account
- Navigate to billing
- Screenshot remaining credits from $5 top-up
- Export usage history

**Save to:** `finance/invoices/x_api_balance_20260415.png`

**Current Status:** MISSING DATA — $5 credit paid per secretary/api_registry.md line 53, but balance unknown

---

### 6. Credit Card SaaS Audit

**Action:**
- Pull all credit card statements for Jan-Apr 2026
- Identify recurring SaaS charges:
  - Domain registrations (GoDaddy, Namecheap, etc.)
  - Cloud hosting (AWS, GCP, Azure, DigitalOcean, etc.)
  - Monitoring/error tracking (Sentry, Datadog, etc.)
  - Email services (SendGrid, Mailgun, etc.)
  - Any other software subscriptions

**Save to:** `finance/credit_card_audit_202604.csv` with columns:
```
Date,Merchant,Amount,Category,Recurring (Y/N)
```

**Current Status:** MISSING DATA — financial_forecast_12m.md assumes $15/mo domain + $20-100/mo tooling but NO VERIFICATION

---

### 7. Bank Account Balance

**Action:**
- Document current cash balance allocated to Y* Bridge Labs operations
- If using personal funds, specify:
  - Total available capital willing to allocate
  - Maximum burn rate tolerance ($/month)
  - Runway comfort zone (months)

**Save to:** `finance/cash_reserves_20260415.md` (private, do not commit to public repo)

**Current Status:** MISSING DATA — runway calculation impossible without this

---

## 🤖 AUTOMATED TASKS (CFO/Secretary Can Build)

### 8. Build SaaS Balance Aggregator Script

**File:** `scripts/check_saas_balances.py`
**Function:** Query all APIs with balance endpoints, output JSON report
**APIs to query:**
- Replicate: `GET https://api.replicate.com/v1/account`
- X API: Check if balance endpoint exists in Twitter API v2
- Others: Research if balance API exists

**Save output to:** `finance/saas_balances_YYYYMMDD.json`

**Note:** HeyGen and Kling have no balance API endpoints (dashboard only)

---

### 9. Cron Job for Weekly Balance Check

**File:** `.github/workflows/weekly_balance_check.yml` OR cron on Mac
**Frequency:** Every Monday 9am
**Action:** Run `scripts/check_saas_balances.py`, commit results to `finance/`
**Owner:** Samantha (Secretary)

---

### 10. Deploy track_burn.py in Production

**Owner:** CTO (Ethan) + Platform Engineer (Ryan)
**Action:**
- Hook `scripts/track_burn.py` into Claude Code session end event
- Auto-parse session summary string
- Append to `finance/daily_burn.md`
- Weekly rollup to `finance/weekly_burn_YYYYWW.md`

**Blocker:** Requires Claude Code hook/plugin (check if settings.json supports post-session hooks)

---

## COMPLETION CRITERIA

✅ **financial_health_20260415.md v5** can be published when:
1. All 7 Board manual tasks completed (Anthropic + HeyGen + Kling + Replicate + X + Credit Card + Bank)
2. Actual numbers replace MISSING DATA in report
3. Trust Metric improves from 11% to >80%

✅ **Ongoing financial health monitoring** achieved when:
1. `scripts/check_saas_balances.py` deployed and cron job running
2. `track_burn.py` hooked into Claude Code sessions
3. Board reviews monthly financial summary (1st of each month)

---

## ESTIMATED TIME REQUIRED

| Task | Time | Blocker |
|------|------|---------|
| Anthropic billing export | 5 min | Board login access |
| HeyGen balance screenshot | 3 min | Board login access |
| Kling balance screenshot | 3 min | Board login access (中国手机验证) |
| Replicate balance screenshot | 2 min | Board login access |
| X API balance screenshot | 3 min | Board login access |
| Credit card audit | 20 min | Board has statements |
| Bank balance documentation | 5 min | Board decision on disclosure |
| **Total Board time:** | **~40 minutes** | |
| Build check_saas_balances.py | 1 hour | CFO/Secretary collaboration |
| Deploy track_burn.py hook | 2 hours | CTO/Platform engineer |

**Next CFO session:** Process Board-provided data and publish financial_health_20260415.md v5 with verified numbers.

---

**Maintained by:** CFO Agent (marco-cfo)
**Last Updated:** 2026-04-15
