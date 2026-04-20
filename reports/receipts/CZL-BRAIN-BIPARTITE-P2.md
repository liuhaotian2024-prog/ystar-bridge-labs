Audience: CEO (Aiden) for dispatch validation + Board for empirical verification of escape bucket + training_eligible segregation
Research basis: Board 2026-04-19 two empirical findings (warn-as-escape + pre-hook contamination anchor 2026-04-16 05:07:20 UTC); CTO Ruling CZL-BRAIN-BIPARTITE Q2/Q5/Q6; production .ystar_cieu.db (468,428 rows at migration time)
Synthesis: Normalizer v2 reclassified 52,658 warn+passed=0 events from escalate to escape (85x increase in escape bucket); training_eligible column segregates 87,402 pre-hook contamination-suspect events from 381,026 clean post-hook events
Purpose: Unblock bipartite learning Phase 3 (contrastive training) with correctly labeled escape samples and contamination-free training set

# CZL-BRAIN-BIPARTITE-P2 Receipt

**Author**: Leo Chen (eng-kernel)
**Date**: 2026-04-19
**Task**: Normalizer v2 (warn-as-escape + time-cut training_eligible)
**Dispatched by**: Board (via CEO)

## CIEU 5-Tuple

- **Y\***: warn correctly classified as escape when passed=0; training_eligible column segregates 21.4% pre-hook contamination
- **Xt**: v1 misclassified warn into escalate (85x undercount of escape samples); no time-cut available; any training would ingest pre-hook contaminated positives
- **U**: D1 normalizer v2 signature change + D2 migration 002 + D3 re-normalize + D4 tests 74 pass + D5 verification query
- **Yt+1**: escape bucket 53,269 events; training_eligible=1 has 381,026 post-hook events; training_eligible=0 has 87,402 pre-hook contamination-suspect events; 74/74 tests pass
- **Rt+1**: 0

## Deliverables

### D1 -- Normalizer v2 (`cieu_decision_normalizer.py`)

- CANONICAL_VALUES expanded from 6 to 7 (added `escape`)
- `normalize()` signature: `normalize(raw_decision: str, passed: int | None = None) -> str`
- v1 backwards compatibility: `normalize("warn")` (no passed arg) returns `"escalate"` as before
- New rules:
  - warn/warning + passed=0 -> `escape`
  - warn/warning + passed=1 -> `allow`
  - allow/accept/approved/pass/passed + passed=0 -> `escape`
- warn/warning removed from static `_RAW_TO_CANONICAL` map; handled by `_PASSED_DEPENDENT_KEYS` dispatch

### D2 -- Migration 002 (`migrations/002_add_training_eligible.py`)

- `ALTER TABLE cieu_events ADD COLUMN training_eligible INTEGER DEFAULT 0` (idempotent)
- Backfill uses `typeof()` dispatch to handle mixed REAL (epoch) + TEXT (ISO) `created_at` formats
- Anchor: 2026-04-16 05:07:20 UTC (epoch 1776316040.0)
- `CREATE INDEX idx_training_eligible_decision ON cieu_events(training_eligible, decision_canonical)`

### D3 -- Re-normalization

- Fetches all distinct `(decision, passed)` pairs, applies v2 normalizer, UPDATE in single transaction
- Handles NULL passed values separately with v1 compat path

### D4 -- Tests (74 pass, target was >= 55)

Test classes and counts:
- TestCanonicalValues: 4 tests (7 buckets, escape present, immutable)
- TestNormalizeAllow: 10 tests (with passed=1 variants)
- TestNormalizeDeny: 6 tests (with passed=0 and passed=1)
- TestNormalizeEscalate: 6 tests (v1 compat, explicit escalate)
- TestNormalizeEscape: 14 tests (warn+passed=0, allow+passed=0, case/whitespace variants)
- TestNormalizeRewrite: 3 tests
- TestNormalizeInfo: 3 tests
- TestNormalizeUnknown: 3 tests
- TestNormalizeEdgeCases: 11 tests (JSON, whitespace, empty, exhaustive canonical check)
- TestProvenanceForAgent: 7 tests
- TestTrainingEligibleMigration: 7 tests (epoch backfill, ISO text format, re-normalize warn+escape, index creation)

### D5 -- Verification Query (post-migration distribution)

```
canonical             passed  eligible     count
--------------------  ------  --------  --------
info                       1         1   156,262
allow                      1         1    69,555
escape                     0         1    52,148
escalate                   0         1    41,418
info                       1         0    31,584
deny                       0         1    28,026
unknown                    1         1    27,794
allow                      1         0    27,404
deny                       0         0    12,438
unknown                    1         0     8,498
deny                       1         1     5,440
escalate                   0         0     3,644
deny                       1         0     2,545
escape                     0         0     1,121
unknown                    0         1       181
rewrite                    1         1        56
escalate                   1         0         6
info                       0         1         5
unknown                    0         0         1
```

Summary:
- **Escape total**: 53,269 (was 611 in v1 -- 85x increase, matching Board prediction of ~52,655)
- **training_eligible=1 (post-hook, clean)**: 381,026
- **training_eligible=0 (pre-hook, contamination-suspect)**: 87,402
- **Clean positives (allow+passed=1+eligible=1)**: 69,555
- **Clean negatives (deny+passed=0+eligible=1)**: 28,026

## Bug Found and Fixed During Execution

The initial migration used string comparison (`created_at >= '2026-04-16 05:07:20'`) for the training_eligible backfill. This only matched 2 of 468K rows because `created_at` is stored as REAL (epoch float) for 99.9996% of rows. Fixed by adding `typeof()` dispatch in the UPDATE CASE statement to handle both REAL and TEXT formats. The migration script was updated to use this corrected approach.

## Files Modified

1. `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/cieu_decision_normalizer.py` -- normalizer v2
2. `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/migrations/002_add_training_eligible.py` -- new migration
3. `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/tests/test_cieu_decision_normalizer.py` -- 74 tests

## Scope Guard Compliance

- No git commit, no git push (per directive)
- Only touched normalizer + new migration + tests (per scope guard)
- ALTER TABLE authorized by Board 2026-04-19 directive
- Training pipeline NOT touched (data-layer only)

## Tool Uses

15 tool calls total
