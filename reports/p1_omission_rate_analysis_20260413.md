# P1 Root Cause Analysis: OmissionEngine Violation Production Rate
**Analyst:** Maya Patel (eng-governance)  
**Date:** 2026-04-13 00:35 EDT  
**Trigger:** CEO circuit breaker threshold change (accumulated → sliding window 10min)

---

## Executive Summary

**Root Cause:** NOT A BUG — OmissionEngine is working as designed. High violation production rate (985 violations in last 24h) is caused by **stale AMENDMENT-009 obligations that never get fulfilled**.

**Key Findings:**
- **2571 total violations** from **1532 unique obligations** (1.68 violations/obligation avg)
- Dual-stage aging system (soft_overdue → hard_overdue) means each unfulfilled obligation generates **2 violations**
- **1867 obligations currently in system** (1039 HARD_OVERDUE + 493 SOFT_OVERDUE + 335 PENDING)
- **30 new obligations created per type in last 24h** — continuous generation from boot contract enforcement
- All obligations are Secretary workflow types: `directive_acknowledgement`, `intent_declaration`, `progress_update`, etc.

**Circuit Breaker Fix:** CEO's sliding window change (line 313, `intervention_engine.py`) is **correct mitigation** — prevents accumulated stale violations from permanently ARMing the circuit breaker. Window allows natural decay of old violations while still catching sustained high-rate spikes.

---

## 1. Violation Production Analysis

### 1.1 Database State
```sql
-- Total violations vs unique obligations
SELECT COUNT(DISTINCT obligation_id) as unique_obligations, 
       COUNT(*) as total_violations
FROM omission_violations;
-- Result: 1532 | 2571

-- Recent activity (last 24h)
SELECT COUNT(*) FROM omission_violations 
WHERE detected_at > strftime('%s', 'now', '-24 hours');
-- Result: 985 violations

-- Obligation status distribution
SELECT status, COUNT(*) as count FROM obligations GROUP BY status;
-- Result:
--   hard_overdue | 1039
--   soft_overdue | 493
--   pending      | 335
```

### 1.2 Dual-Stage Violation Mechanism (omission_engine.py lines 192-242)

**Stage 1: SOFT_OVERDUE (first timeout)**
- Obligation crosses `due_at` → status becomes SOFT_OVERDUE
- Creates **first violation** (no "stage" marker in details_json)
- `soft_count += 1`, severity may escalate

**Stage 2: HARD_OVERDUE (due_at + hard_overdue_secs)**
- Crosses `hard_threshold` → status becomes HARD_OVERDUE
- Creates **second violation** with `{"stage": "hard_overdue"}` in details_json
- Severity forced to MEDIUM/HIGH minimum

**Example from database:**
```json
// Obligation 00be55e5-3368-40ac-b50d-9b7f23612673 has 2 violations:
// Violation 1 (soft): {"obligation_id": "...", "due_at": 1775953990.4169998}
// Violation 2 (hard): {..., "stage": "hard_overdue"}
```

This is **design-as-intended** — not duplicate counting, but progression through stages.

---

## 2. Obligation Source Analysis

### 2.1 Obligation Type Distribution
```
Type                                  Total | HARD | SOFT | PENDING
─────────────────────────────────────────────────────────────────
autonomous_daily_report               190   | 0    | 160  | 30
directive_acknowledgement             190   | 185  | 0    | 5
gemma_session_daily                   190   | 0    | 160  | 30
intent_declaration                    190   | 185  | 0    | 5
knowledge_update                      190   | 160  | 6    | 24
progress_update                       190   | 181  | 2    | 7
required_acknowledgement_omission     157   | 152  | 0    | 5
task_completion_report                190   | 176  | 5    | 9
theory_library_daily                  190   | 0    | 160  | 30
weekly_roadmap_audit                  190   | 0    | 0    | 190
─────────────────────────────────────────────────────────────────
TOTAL                                 1867  | 1039 | 493  | 335
```

### 2.2 Creation Rate
- **30 new obligations created in last 24h** for each type (except `required_acknowledgement_omission`: 30 new, 157 total historical)
- All obligations belong to entity `ystar-company_0a84f3c6`
- All obligations assigned to `actor_id: secretary`
- Date range: **2026-04-11 15:58:59** (oldest) to **2026-04-13 00:31:29** (newest)

### 2.3 Why Obligations Accumulate

**AMENDMENT-009 Boot Contract** (11-category timing enforcement) creates obligations at session start/boot for Secretary workflow milestones:
- `directive_acknowledgement` — Secretary must acknowledge Board directives
- `intent_declaration` — Agent must declare work intent before execution
- `progress_update` — Agent must report progress on tasks
- `knowledge_update` — Knowledge base must be updated
- `autonomous_daily_report` — Daily autonomous work report
- etc.

**The Problem:** These obligations require **specific governance events** to fulfill them, but:
1. Current agent workflows don't emit those fulfillment events consistently
2. Secretary pipeline (tombstone, curate, etc.) is partially implemented
3. Some obligation types (e.g., `weekly_roadmap_audit`) have **190 pending, 0 fulfilled** — never implemented

Result: Obligations pile up → soft violations → hard violations → database grows.

---

## 3. Circuit Breaker Analysis

### 3.1 Old Logic (Accumulated Count — BUG)
```python
# intervention_engine.py (before CEO fix)
self._circuit_breaker_violation_count += len(violations)

if (self._circuit_breaker_violation_count >= self._circuit_breaker_threshold
        and not self._circuit_breaker_armed):
    self._circuit_breaker_armed = True
    # STOP generating pulses
```

**Problem:** Count never decays. Once it hits 50, circuit breaker **ARMs permanently** until manual reset. Stale historical violations from days ago still counted.

**How it hit 1497:** 1.5 days of violations accumulating → 2571 total in DB → count kept climbing.

### 3.2 New Logic (Sliding Window 10min — CORRECT)
```python
# intervention_engine.py lines 336-344 (CEO's fix)
cutoff = now - self._circuit_breaker_window_secs  # 600 sec = 10 min
self._circuit_breaker_window = [
    (ts, c) for ts, c in self._circuit_breaker_window if ts > cutoff
]
if violations:
    self._circuit_breaker_window.append((now, len(violations)))
self._circuit_breaker_violation_count = sum(
    c for _, c in self._circuit_breaker_window
)
```

**Behavior:** Only counts violations in **last 10 minutes**. Old violations naturally expire from window.

**Current state:** Last 10 minutes has **8 violations** (far below threshold=50) → circuit breaker disarmed → system healthy.

---

## 4. Options for Mitigation

### 4.1 Option A: Increase Threshold (Easiest — Band-Aid)
```python
self._circuit_breaker_threshold = 200  # was 50
```
**Pros:** Quick, allows system to tolerate higher unfulfilled obligation rate.  
**Cons:** Doesn't fix root cause. If obligation creation rate increases (e.g., more agents), will hit threshold again.

### 4.2 Option B: Extend Grace Periods (Reduces Soft→Hard Promotion Rate)
```python
# In obligation creation (omission_rules.py or boot contract)
hard_overdue_secs = 1800  # increase from 120-300 to 30min
```
**Pros:** Fewer obligations reach HARD_OVERDUE stage → fewer total violations.  
**Cons:** Delays detection of real omissions. Not addressing root cause.

### 4.3 Option C: Clean Stale Obligations (Symptom Relief)
**Criteria for cleanup:**
- `weekly_roadmap_audit`: 190 pending, never implemented → **deprecate obligation type**
- `theory_library_daily`: 190 total (160 soft_overdue) → **fulfillment mechanism not wired**
- `gemma_session_daily`: same pattern

**Cleanup method:** Use Secretary tombstone mechanism (already implemented in pipeline step 2).

**SQL to identify candidates:**
```sql
-- Obligation types with >80% unfulfilled rate
SELECT obligation_type, 
       COUNT(*) as total,
       SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
       (SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as pending_pct
FROM obligations
GROUP BY obligation_type
HAVING pending_pct > 80
ORDER BY total DESC;
```

### 4.4 Option D: Wire Fulfillment Events (Root Fix — Recommended)
**For each obligation type, implement the fulfillment event emission:**

| Obligation Type                        | Required Event Type              | Implementation Needed             |
|----------------------------------------|----------------------------------|-----------------------------------|
| `autonomous_daily_report`              | `daily_report_submitted`         | Add CIEU event to cron job        |
| `gemma_session_daily`                  | `gemma_session_completed`        | Add CIEU event to Gemma script    |
| `theory_library_daily`                 | `theory_update_submitted`        | Wire to learning scripts          |
| `directive_acknowledgement`            | `directive_acknowledged`         | Add to CEO → delegate flow        |
| `intent_declaration`                   | `intent_declared`                | Add to task start hooks           |
| `progress_update`                      | `progress_reported`              | Add to task checkpoint hooks      |
| `knowledge_update`                     | `knowledge_committed`            | Git commit hook or manual trigger |
| `task_completion_report`               | `task_completed`                 | Task close hook                   |
| `required_acknowledgement_omission`    | `acknowledgement_received`       | Secretary ack flow                |
| `weekly_roadmap_audit`                 | NOT IMPLEMENTED → **DEPRECATE**  | —                                 |

**Recommended phased approach:**
1. **Immediate (P0):** Deprecate `weekly_roadmap_audit` obligation type (Secretary tombstone)
2. **Week 1 (P1):** Wire top-3 high-volume types (`autonomous_daily_report`, `gemma_session_daily`, `theory_library_daily`) to their cron jobs
3. **Week 2 (P1):** Wire Secretary workflow types (`directive_acknowledgement`, `intent_declaration`, `progress_update`) to delegation hooks
4. **Week 3 (P2):** Wire remaining types or increase their grace periods

---

## 5. Recommendations

### 5.1 Immediate Actions (CEO Decision Required)

**5.1.1 Keep Sliding Window Logic**  
✅ CEO's circuit breaker fix is correct. Do not revert.

**5.1.2 Deprecate Unimplemented Obligation Types**  
- `weekly_roadmap_audit` (190 obligations, 0 fulfilled, no implementation plan)
- Use Secretary tombstone mechanism to mark as deprecated
- Add migration to mark existing obligations as `CANCELLED` status

**5.1.3 Temporary Threshold Increase (Optional)**  
If obligation fulfillment wiring takes >1 week, raise threshold to 100 as temporary relief.

### 5.2 P1 Engineering Work (Next Sprint)

**5.2.1 CTO Task: Wire Top-3 Fulfillment Events**  
Assign to Ryan (eng-platform):
- Modify `ystar_wakeup.sh` daily report cron to emit `daily_report_submitted` event
- Modify `local_learn.py` Gemma session to emit `gemma_session_completed` event
- Modify theory learning scripts to emit `theory_update_submitted` event

**5.2.2 Secretary Task: Obligation Audit + Cleanup Script**  
Create script to:
1. Query all obligation types from DB
2. Calculate fulfillment rate per type
3. Auto-deprecate types with <5% fulfillment rate over 7 days
4. Generate weekly report to CEO

### 5.3 P2 Architecture Improvement

**5.3.1 Obligation Lifecycle Monitoring Dashboard**  
Add to `ystar doctor` output:
- Obligation creation rate (obligations/hour)
- Fulfillment rate by type
- Avg time-to-fulfill vs grace period
- Top-5 overdue obligation types

**5.3.2 Circuit Breaker Auto-Tuning**  
Instead of fixed threshold=50, calculate dynamic threshold based on:
- Historical violation rate (90th percentile over 7 days)
- Current obligation creation rate
- Target: threshold = baseline_rate × 3 (allowing 3× spike before ARM)

---

## 6. No Code Changes Required (Analysis Only)

Per CEO directive, this analysis does **not include code changes**. All findings documented for CEO decision.

If CEO approves Option D (wire fulfillment events), create separate task cards for:
- Ryan (eng-platform): cron job event emission
- Samantha (secretary): deprecation script
- Leo (eng-kernel): obligation lifecycle dashboard

---

## 7. Test Plan (If CEO Approves Fixes)

### 7.1 Verification Steps
1. Query obligation table weekly for 4 weeks, track growth rate
2. After fulfillment events wired, verify obligations transition to `fulfilled` status
3. Monitor circuit breaker window count — should stay <20 in normal operations
4. CIEU audit: verify fulfillment events appear in event log

### 7.2 Success Criteria
- Obligation growth rate: <50 new unfulfilled obligations per week (down from ~210 current rate)
- Fulfillment rate: >60% for implemented obligation types within 30 days
- Circuit breaker: no ARM events for 7 consecutive days

---

## Appendix A: Database Queries Used

```sql
-- Total violations and unique obligations
SELECT COUNT(DISTINCT obligation_id) as unique_obs, COUNT(*) as total_viols 
FROM omission_violations;

-- Recent violation rate
SELECT COUNT(*) FROM omission_violations 
WHERE detected_at > strftime('%s', 'now', '-24 hours');

-- Obligation status distribution
SELECT status, COUNT(*) FROM obligations GROUP BY status;

-- Obligation type distribution
SELECT obligation_type, status, COUNT(*) 
FROM obligations 
GROUP BY obligation_type, status 
ORDER BY obligation_type, status;

-- Recent obligation creation
SELECT datetime(created_at, 'unixepoch', 'localtime'), obligation_type, status
FROM obligations 
WHERE created_at > strftime('%s', 'now', '-6 hours') 
ORDER BY created_at DESC LIMIT 20;

-- Dual-stage violation evidence
SELECT obligation_id, COUNT(*) as viol_count, 
       GROUP_CONCAT(DISTINCT details_json) as stages
FROM omission_violations 
GROUP BY obligation_id 
HAVING viol_count > 1 
LIMIT 5;

-- Circuit breaker sliding window current state
SELECT COUNT(*) FROM omission_violations 
WHERE detected_at > strftime('%s', 'now', '-10 minutes');
```

---

**End of Report**  
**Status:** Analysis complete. Awaiting CEO decision on mitigation options.
