# Platform Engineer — Full System Pipeline Audit

Date: 2026-04-02
Reporter: Platform Engineer
Severity: P0 — System-wide governance pipeline disconnection

## Executive Summary

GovernanceLoop ran 558 cycles with ZERO output. Board complaint is justified.
Root cause: Pipeline is WIRED but NOT CONNECTED — interfaces exist but data flow is broken.

## Audit Findings

### 1. Orchestrator → GovernanceLoop: PARTIAL CONNECTION

**Status:** Interface connected, but producing empty output

**Evidence:**
- File: `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/adapters/orchestrator.py`
- Lines 135-174: `_build_governance_loop()` correctly creates GovernanceLoop instance
- Lines 151-155: ReportEngine initialized with REAL OmissionStore (not None/Mock)
- Line 166-170: GovernanceLoop initialized with report_engine, intervention_engine, causal_engine

**Runtime Verification:**
```
CIEU events: 1763 total
GovernanceLoop cycles: 558 (logged to CIEU)
Recent cycle data:
  Health: degraded
  Suggestions: 0  ← PROBLEM
  Action required: True
  Observation healthy: False
```

**Diagnosis:** GovernanceLoop is RUNNING but producing ZERO suggestions despite degraded health.

---

### 2. GovernanceLoop → Suggestion Generation: DISCONNECTED

**Status:** Interface exists but conditions never trigger

**Evidence:**
- File: `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/governance/governance_loop.py`
- Line 665: `_generate_governance_suggestions(latest)` is called
- Delegates to `ystar/governance/suggestion_policy.py:106`

**Suggestion Policy Logic:**
```python
# File: suggestion_policy.py, lines 125-141
if obs.omission_detection_rate > odr_min and obs.omission_recovery_rate < orr_max:
    # Generate suggestion
```

**Runtime Observation Data:**
```python
# From observation_fusion.py:19-44
obligation_fulfillment_rate = kpis.get("obligation_fulfillment_rate", 0.0)
omission_detection_rate = kpis.get("omission_detection_rate", 0.0)
```

**Root Cause:** ALL KPI values are 0.0 (defaults), so NO suggestion conditions are met.

---

### 3. ReportEngine → OmissionStore: CONNECTED BUT EMPTY

**Status:** Interface connected, but data source is empty

**Evidence:**
- File: `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/governance/reporting.py`
- Lines 790-818: `baseline_report()` and `daily_report()` correctly query OmissionStore
- Database path: `.ystar_cieu_omission.db`

**Actual Database Contents:**
```
Tables: ['entities', 'obligations', 'governance_events', 'omission_violations']
Total obligations: 0  ← ROOT CAUSE
Obligations by status: []
```

**Diagnosis:** OmissionStore is initialized but has ZERO obligations registered.
This means:
- No obligation_timing from session config was registered
- Or obligation registration failed silently
- Or obligations were created but not persisted

---

### 4. Orchestrator → InterventionEngine: DISCONNECTED

**Status:** Interface exists but scan chain never executes

**Evidence:**
- File: `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/adapters/orchestrator.py`
- Lines 206-210: `_should_run_intervention_scan()` checks for conditions
- Lines 244-298: `_run_intervention_scan()` implements scan→pulse chain

**Runtime Verification:**
```
CIEU events matching 'intervention': 0
CIEU events matching 'path_a': 0
```

**Diagnosis:** InterventionEngine scan is NEVER triggered because:
- Line 227-230: Condition requires `self._omission_adapter is not None`
- Line 263-264: `scan_result = self._omission_adapter.engine.scan(now=now)`
- If OmissionAdapter has ZERO obligations, scan returns empty result
- Empty result → no violations → no pulses → no CIEU events

---

### 5. Orchestrator → Path A: DISCONNECTED

**Status:** Interface exists but trigger condition never met

**Evidence:**
- File: `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/adapters/orchestrator.py`
- Lines 371-373: Path A trigger condition
```python
if (tighten_result.overall_health in ("degraded", "critical")
        and tighten_result.governance_suggestions):  ← Never True
    self._run_path_a_cycle(tighten_result, now)
```

**Runtime Verification:**
```
Health: degraded  ← Condition 1: MET
Suggestions: 0    ← Condition 2: NOT MET
```

**Diagnosis:** Path A is correctly wired but NEVER activates because GovernanceLoop produces ZERO suggestions.

---

### 6. ExperienceBridge → GovernanceLoop: PARTIAL CONNECTION

**Status:** Interface defined but bridge instance is None

**Evidence:**
- File: `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/governance/governance_loop.py`
- Line 236: `experience_bridge: Optional[Any] = None` parameter exists
- Line 244: `self._experience_bridge = experience_bridge`
- Lines 462-469: Bridge metrics merge logic exists
- Lines 671-685: Bridge suggestion merge logic exists

**Runtime State:**
- Orchestrator's `_build_governance_loop()` does NOT pass experience_bridge
- `self._experience_bridge` remains None
- Merge logic is never executed

**Diagnosis:** ExperienceBridge interface is WIRED but instance is NOT PROVIDED by orchestrator.

---

## Root Cause Analysis

### Primary Failure: OmissionStore is Empty

**Location:** `ystar/adapters/hook.py:507-622`
Function: `_setup_omission_from_contract()`

This function is responsible for:
1. Reading `obligation_timing` from session config
2. Registering obligations in OmissionStore
3. Configuring OmissionEngine with timing constraints

**Hypothesis:** One of the following is failing silently:
1. Session config has no `obligation_timing` data
2. `apply_openclaw_accountability_pack()` fails to register obligations
3. Obligations are registered but not persisted to DB
4. DB writes succeed but are not committed

**Evidence for Silent Failure:**
- Line 620-621: `except Exception as exc: _log.error("Omission engine setup failed: %s", exc)`
- Silent except blocks throughout the setup chain
- No CIEU event for "omission_setup_complete"

---

### Secondary Failure: Zero-Data Propagation

Even if OmissionStore is empty, the system should NOT produce 558 cycles of identical empty output.

**Expected Behavior:** After 1-2 empty cycles, GovernanceLoop should:
1. Detect that observation data is all zeros
2. Log a warning to CIEU
3. Trigger a fallback suggestion: "investigate obligation registration"

**Actual Behavior:** Silent spin loop producing identical results.

**Missing Logic:**
- No data quality check in `observe_from_report_engine()`
- No fallback suggestion policy for "all KPIs are zero" state

---

## Summary Table

| Subsystem | Connection | Data Flow | Evidence |
|-----------|-----------|-----------|----------|
| **Orchestrator → GovernanceLoop** | Connected | Empty | Lines 135-174, 558 cycles logged |
| **GovernanceLoop → ReportEngine** | Connected | Empty | Lines 451-472, KPIs all 0.0 |
| **ReportEngine → OmissionStore** | Connected | Empty | DB has 0 obligations |
| **OmissionStore ← Session Config** | DISCONNECTED | ZERO | Obligation registration failed |
| **GovernanceLoop → SuggestionPolicy** | Connected | Empty | Conditions never met (KPIs=0) |
| **GovernanceLoop → Path A** | Wired | Never triggered | Suggestions=0 blocks activation |
| **Orchestrator → InterventionEngine** | Wired | Never triggered | No violations (store empty) |
| **GovernanceLoop → ExperienceBridge** | Wired | Not provided | Bridge instance is None |

---

## Recommendations

### Immediate Actions (Governance Engineer)

1. **Fix OmissionStore Registration (P0)**
   - Add instrumentation to `_setup_omission_from_contract()`
   - Log obligation registration events to CIEU
   - Add unit test: "session with obligation_timing creates N obligations"

2. **Add Data Quality Checks (P0)**
   - In `observe_from_report_engine()`: detect "all zeros" state
   - Generate fallback suggestion when data is missing
   - Stop logging identical empty cycles

3. **Wire ExperienceBridge (P1)**
   - Modify `orchestrator._build_governance_loop()` to create ExperienceBridge instance
   - Pass to GovernanceLoop constructor
   - Verify metrics merge logic executes

### Cross-Module Tests (Platform Engineer)

4. **Add Integration Test (P0)**
   - File: `tests/test_architecture.py`
   - Test: "session with obligation_timing → GovernanceLoop produces suggestions"
   - End-to-end pipeline verification

5. **Add Observability (P1)**
   - CIEU event: "omission_setup_complete" (obligation count, timing config)
   - CIEU event: "governance_loop_observation" (KPI snapshot)
   - CIEU event: "suggestion_policy_evaluation" (conditions checked, results)

---

## Board Accountability

**Board's Concern:** "GovernanceLoop空转558次但零输出，Path A零激活。这是CTO团队验证失职。"

**Platform Engineer Response:** Concern is VALID.

**Failures:**
1. No end-to-end integration test covering `session config → obligations → suggestions → Path A`
2. No data quality monitoring in production sessions
3. Silent failure chains with excessive try/except blocks
4. No fallback behavior when critical data is missing

**QA Lead Corrective Action:**
- Write P0 test: `test_governance_pipeline_e2e()`
- Add to `tests/test_architecture.py`
- Block future releases if this test fails

---

## Next Steps

1. Governance Engineer: Fix obligation registration (root cause)
2. Platform Engineer: Write integration test (verification)
3. CTO: Review and approve fixes
4. Board: Re-audit after fixes deployed

Report complete. No code modifications made (audit only).

---

**Files Referenced:**
- `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/adapters/orchestrator.py`
- `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/adapters/hook.py`
- `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/governance/governance_loop.py`
- `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/governance/suggestion_policy.py`
- `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/governance/reporting.py`
- `C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/governance/observation_fusion.py`
- Database: `C:/Users/liuha/OneDrive/桌面/ystar-company/.ystar_cieu_omission.db`
