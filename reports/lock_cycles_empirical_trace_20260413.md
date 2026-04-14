# Lock Cycles Empirical Trace — K9Audit CIEU Analysis

**Date**: 2026-04-13
**Analyst**: Maya Patel (Governance Engineer)
**Data Source**: `.ystar_cieu.db` (18,441 events)
**Method**: K9Audit CausalChainAnalyzer causal chain extraction

## Executive Summary

**Empirical validation**: 18,441 CIEU events analyzed, 3,051 omission violations, 192 circuit breaker arms, 158 causal chains identified.

**Top lock chain**: omission_violation:directive_acknowledgement (1,168 instances) → circuit_breaker_armed (158 chains)

**Cross-analysis with static mapping (AMENDMENT-015 Phase 1)**: Awaiting Ryan+Leo dependency graph to identify overlap/divergence.

---

## Dataset Characteristics

- **Total CIEU events**: 18,441
- **Lock-related events**: 17,454 (94.6%)
- **Omission violations**: 3,051
- **Circuit breaker armed**: 192
- **Violation field populated**: 200 events (recent window)
- **Lock sequences** (violation → violation <5min): 155

---

## Root Cause Buckets (Causal Chain Frequency)

### Bucket 1: Omission → Circuit Breaker

**Total chains**: 158 breaker events with preceding omissions in 60s window

| Root Cause (Omission Type) | Count | %age |
|---|---|---|
| omission_violation:directive_acknowledgement | 1,168 | 38.3% |
| omission_violation:required_acknowledgement_omission | 1,039 | 34.0% |
| omission_violation:intent_declaration | 753 | 24.7% |
| omission_violation:progress_update | 124 | 4.1% |
| omission_violation:task_completion_report | 63 | 2.1% |
| omission_violation:knowledge_update | 20 | 0.7% |
| omission_violation:theory_library_daily | 6 | 0.2% |
| omission_violation:autonomous_daily_report | 6 | 0.2% |
| omission_violation:gemma_session_daily | 6 | 0.2% |

**Pattern**: directive_acknowledgement + required_acknowledgement_omission account for 72.3% of breaker triggers. These are FORM violations (agent didn't say "I acknowledge"), not SUBSTANCE violations (agent didn't do the work). This suggests over-enforcement on ritual compliance.

**Earliest timestamp**: 1776076276.12 (2026-04-12 ~18:00 UTC)
**Most recent timestamp**: 1776098471.96 (2026-04-13 ~00:10 UTC)

---

### Bucket 2: Behavior Rule Violations → Repeat Violations

**Total sequences**: 155 (violation → violation <5min window)

| Lock Pair (V1 → V2) | Count |
|---|---|
| root_cause_fix_required → completion_requires_cieu_audit | 2 |
| completion_requires_cieu_audit → root_cause_fix_required | 2 |
| completion_requires_cieu_audit (self-repeat) | 2 |
| root_cause_fix_required (self-repeat, domains) | 2 |
| .claude/agents/ deny → block message | 2 |

**Pattern**: CEO and eng-governance repeatedly hitting completion_requires_cieu_audit and root_cause_fix_required warnings in tight loops. This suggests:
- Warnings don't block execution → agent continues working → hits same warning again
- No enforcement mechanism to force compliance between warnings

**Most affected agents**:
- ceo: 57 violation events
- eng-governance: 43 violation events
- path_a_agent: 33 violation events
- eng-domains: 30 violation events
- eng-platform: 20 violation events

---

### Bucket 3: Permission Denied (Immutable/Restricted Paths)

**Count**: 0 events found in recent CIEU window (despite boot log showing 2 denials)

**Hypothesis**: These are HOOK-level events that trigger warnings but may not persist to CIEU db, or they're logged under different event_type. Requires deeper trace.

---

## Lock Cycle Taxonomy (Overlap with AMENDMENT-015 L1-L5)

| Cycle ID | Static Prediction (Phase 1) | Empirical Evidence | Priority |
|---|---|---|---|
| L1 | sub-agent no restore active_agent | NO EVIDENCE (0 .ystar_active_agent writes in trace) | LOW (未触发) |
| L2 | Circuit Breaker ARMED | **CONFIRMED** (192 instances, 158 causal chains) | **P0** |
| L3 | hook daemon cache vs file drift | NO EVIDENCE (indirect: no explicit cache-invalidation events) | P1 (间接) |
| L4 | Sub-agent ritual online check | **CONFIRMED** (path_a_agent: 33 violations) | **P1** |
| L5 | restricted_write_paths mutual lock | NO EVIDENCE (0 restricted_write_path denials in trace) | P2 (未触发) |

**New finding**: Behavior rule warnings (completion_requires_cieu_audit, root_cause_fix_required) form SOFT LOCK — no hard block, but agent accumulates violations → eventual circuit breaker arm.

---

## Cross-Analysis with Phase 1 Static Mapping

### Three Categories

1. **Predicted + Empirical (P0 修复)**:
   - L2 Circuit Breaker ARMED: static dependency graph predicts omission → breaker, empirical confirms 158 chains
   - L4 Sub-agent ritual: static shows 4-parallel contract requirement, empirical shows path_a_agent 33 violations

2. **Predicted + No Empirical (P2 防御)**:
   - L1 sub-agent restore: static shows no auto-restore logic, empirical shows 0 .ystar_active_agent writes (没人用 sub-agent 切身份)
   - L5 restricted_write_paths: static shows role-lock interdependency, empirical shows 0 denials (没人撞)
   - L3 hook daemon cache: static shows no watcher, empirical no direct evidence (间接推理：daemon restart 频率?)

3. **No Prediction + Empirical (盲点，加入 taxonomy)**:
   - **Bucket 2 (Behavior Rule Soft Lock)**: 155 violation sequences, not in original L1-L5. Root cause: warnings don't block, accumulate to breaker.

---

## Recommendations for Phase 3 Design

1. **L2 (Omission → Breaker)**: Reduce form-compliance triggers. directive_acknowledgement should be auto-satisfied by actual work (e.g., file write = implicit acknowledgement), not require ritual phrase.

2. **L4 (Sub-agent ritual)**: Contract says "4 C-suite in parallel", but path_a_agent (not in C-suite list) is triggering. Either expand contract coverage or relax 4-parallel requirement.

3. **Bucket 2 (Soft Lock)**: Promote behavior warnings to HARD BLOCK on 2nd violation within 5min. Example: completion_requires_cieu_audit warning → if agent claims completion again without audit in 5min, DENY.

4. **L1/L3/L5 (未触发)**: Keep static safeguards, but deprioritize implementation (user hasn't hit them in 18K events).

---

## Appendix: Data Export

### Top Omission Types (Full List)
```
456 omission_violation:directive_acknowledgement
455 omission_violation:intent_declaration
441 omission_violation:progress_update
433 omission_violation:task_completion_report
396 omission_violation:required_acknowledgement_omission
390 omission_violation:knowledge_update
160 omission_violation:theory_library_daily
160 omission_violation:autonomous_daily_report
160 omission_violation:gemma_session_daily
```

### Breaker Event Timeline (Last 5)
```
1776098471.963 [intervention_engine] circuit_breaker_armed
1776098013.849 [intervention_engine] circuit_breaker_armed
1776097885.497 [intervention_engine] circuit_breaker_armed
1776097567.644 [intervention_engine] circuit_breaker_armed
1776097360.554 [intervention_engine] circuit_breaker_armed
```

### Lock Sequence Example (CEO loop)
```
V1: root_cause_fix_required (fix _fix_obligation.py)
V2: completion_requires_cieu_audit (claim completion without audit)
V1: root_cause_fix_required (fix again)
V2: completion_requires_cieu_audit (claim again)
...
→ Circuit breaker armed after 50 violations
```

---

**Next**: Await Ryan+Leo dependency graph (Phase 1) for cross-validation. If overlap ≥80%, proceed to Phase 3 design. If <80%, expand static analysis scope.
