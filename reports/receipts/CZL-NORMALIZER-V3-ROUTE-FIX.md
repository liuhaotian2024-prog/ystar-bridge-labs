Audience: CEO (Aiden), CTO (Ethan), eng-governance (Maya) who authored CZL-REWRITE-AUDIT diagnosis.
Research basis: Maya CZL-REWRITE-AUDIT finding that 56 events with decision_canonical='rewrite' contained 46 ROUTING_GATE_CHECK + 3 CTO_BROKER dispatches misclassified as rewrite. Only 7 REWRITE_APPLIED events are real corrective rewrites.
Synthesis: split route/dispatch out of rewrite canonical into new route bucket, ran migration on production DB (483,626 rows), confirmed rewrite dropped from 56 to 7 and route grew to 49.

# CZL-NORMALIZER-V3-ROUTE-FIX -- Split route/dispatch from rewrite canonical

**Author**: Leo Chen (eng-kernel)
**Date**: 2026-04-19
**Status**: COMPLETE
**Directive**: Board CZL-NORMALIZER-V3-ROUTE-FIX

## Receipt (5-tuple)

- **Y***: route/dispatch correctly classified as canonical route, not rewrite; rewrite bucket matches Maya's audit (7 real REWRITE_APPLIED events)
- **Xt**: 56 events misclassified as rewrite (46 ROUTING_GATE_CHECK + 3 CTO_BROKER + 7 real REWRITE_APPLIED)
- **U**: (1) Updated normalizer: 7-bucket -> 8-bucket, route/dispatch map to route not rewrite, (2) Created migration 003_recanonicalize_route.py, (3) Updated tests from 74 to 98, (4) Ran migration on production DB
- **Yt+1**: rewrite canonical = 7 (true rewrites only), route canonical = 49, all 98 tests pass
- **Rt+1**: 0

---

## Deliverables

### D1: Normalizer v3 -- new route canonical bucket

File: `Y-star-gov/ystar/governance/cieu_decision_normalizer.py`

Changes:
- CANONICAL_VALUES: 7 -> 8 members (added `route`)
- _RAW_TO_CANONICAL: `route` and `dispatch` now map to `"route"` (was `"rewrite"`)
- Docstring updated: 7-bucket -> 8-bucket, route bucket documented with CZL-REWRITE-AUDIT rationale
- normalize() function unchanged (pure lookup, already handles the new mapping)

### D2: Migration 003

File: `Y-star-gov/ystar/governance/migrations/003_recanonicalize_route.py`

SQL: `UPDATE cieu_events SET decision_canonical='route' WHERE decision IN ('route','dispatch')`

### D3: Tests -- 98 test cases (was 74)

File: `Y-star-gov/ystar/governance/tests/test_cieu_decision_normalizer.py`

New test classes:
- TestCanonicalValues: added test_exactly_eight_canonical_values, test_route_in_canonical
- TestNormalizeRewrite: expanded to 8 tests (rewrite case/whitespace/passed variants + negative assertions that route/dispatch no longer map here)
- TestNormalizeRoute: 12 new tests (route/dispatch x case/whitespace/passed variants)
- TestRouteRecanonicalization: 6 new tests (migration logic: single route, single dispatch, rewrite unaffected, mixed population 7+46+3, other canonicals unchanged, idempotent double-run)

### D4: Production migration run

```
[003] Total rows: 483,626
[003] BEFORE: rewrite=56, route=0
[003] AFTER:  rewrite=7, route=49
[003] Delta:  rewrite dropped by 49, route grew by 49
[003] All canonical values in expected set -- CLEAN
[003] Migration completed in 0.1s
```

The 49 migrated (vs Maya's expected ~56) is correct: 56 total had decision_canonical='rewrite', but 7 of those have raw decision='rewrite' (real REWRITE_APPLIED events), leaving exactly 49 with raw decision IN ('route','dispatch') that moved to canonical route.

### D5: Post-migration distribution

| decision_canonical | count |
|---|---|
| info | 192,532 |
| allow | 100,998 |
| escape | 53,269 |
| deny | 49,507 |
| escalate | 45,125 |
| unknown | 38,392 |
| None | 3,747 |
| route | 49 |
| rewrite | 7 |

---

## Files touched

1. `Y-star-gov/ystar/governance/cieu_decision_normalizer.py` -- normalizer v3
2. `Y-star-gov/ystar/governance/migrations/003_recanonicalize_route.py` -- new migration
3. `Y-star-gov/ystar/governance/tests/test_cieu_decision_normalizer.py` -- 98 tests (was 74)

## Verification

- 98/98 tests PASS (pytest, 0.55s)
- Production DB migrated: rewrite 56->7, route 0->49
- All canonical values in expected set (CLEAN)
- No git commit per scope guard

---

Completed 2026-04-19 by eng-kernel (Leo Chen). 14 tool_uses.
