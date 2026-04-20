Audience: CEO (Aiden) for dispatch closeout + CTO (Ethan) for architectural awareness + eng-platform (Ryan) for brain_auto_ingest wiring dependency
Research basis: Empirical analysis of aiden_brain.db (150 nodes, 1902 edges, 1.4M activation_log rows), source review of aiden_brain.py add_node() lines 94-116 and add_edge() lines 131-146, CTO ruling CZL-BRAIN-AUTO-INGEST items 2+3+8 confirming INSERT OR REPLACE as root cause, post-fix verification via production aiden_import run
Synthesis: INSERT OR REPLACE in SQLite = DELETE + INSERT, destroying all columns not in the INSERT list; fixing to INSERT ON CONFLICT DO UPDATE preserves learning state; 16 nodes recovered from activation_log
Purpose: Unblock brain_auto_ingest pipeline (Ryan eng-platform) which depends on add_node() being safe to call repeatedly

# CZL-BRAIN-ADD-NODE-PRESERVE Receipt

**Author**: Leo Chen (eng-kernel)
**Date**: 2026-04-19
**Status**: COMPLETE
**Maturity**: L4 SHIPPED

## CIEU 5-Tuple

- **Y***: aiden_import no longer destroys learning state; existing access_count preserved on re-import; data recovery from activation_log completed
- **Xt**: INSERT OR REPLACE in add_node() (line 101-116) and add_edge() (lines 135-146) of aiden_brain.py was deleting and re-inserting rows on every upsert, zeroing access_count/co_activations/created_at across all 150 nodes and 1902 edges on every aiden_import run
- **U**: (1) Fixed add_node() to INSERT ON CONFLICT DO UPDATE preserving access_count/last_accessed/created_at/base_activation/embedding/triggers (2) Fixed add_edge() same pattern preserving co_activations/created_at (3) Added content_hash parameter to add_node() (4) Updated aiden_import.py to pass content_hash (5) Added import safety guard (6) Wrote 12 regression tests (7) Recovered 16 nodes from activation_log (8) Verified end-to-end with real aiden_import run
- **Yt+1**: Re-ran aiden_import on production DB after fix: all 66 nodes with access_count > 0 preserved; 64/150 nodes now have content_hash populated; 12/12 tests pass
- **Rt+1**: 0

## Files Modified

| File | Change |
|------|--------|
| `scripts/aiden_brain.py` | `add_node()`: INSERT OR REPLACE -> INSERT ON CONFLICT DO UPDATE; added content_hash param; preserves access_count/last_accessed/created_at/base_activation/embedding/triggers |
| `scripts/aiden_brain.py` | `add_edge()`: INSERT OR REPLACE -> INSERT ON CONFLICT DO UPDATE; preserves co_activations/created_at |
| `scripts/aiden_import.py` | Pass content_hash to add_node(); added `_verify_add_node_is_safe()` guard that refuses to run if INSERT OR REPLACE is still present |
| `scripts/brain_recover_access_counts.py` | NEW: one-time recovery script deriving access_count from activation_log JSON |
| `tests/platform/test_add_node_preserves_state.py` | NEW: 12 regression tests covering all preservation invariants |

## Sibling Audit

| File | Pattern | Status |
|------|---------|--------|
| `scripts/aiden_brain.py` add_node() | INSERT OR REPLACE (nodes) | FIXED |
| `scripts/aiden_brain.py` add_edge() | INSERT OR REPLACE (edges) | FIXED |
| `scripts/aiden_embed.py` | No INSERT OR REPLACE | CLEAN |
| `scripts/aiden_recall.py` | No INSERT OR REPLACE | CLEAN |
| `scripts/aiden_import.py` | Uses add_node/add_edge (delegated) | FIXED via upstream |

## Data Recovery

- **Source**: activation_log table (1,426,800 rows) with JSON `activated_nodes` column
- **Method**: COUNT per node_id extracted from JSON; backfill where derived > current
- **Result**: 16 nodes recovered, largest being team/ceo (398,647), team/cfo (398,647), team/cmo (391,123)
- **Post-recovery**: 66/150 nodes have access_count > 0 (up from 54)
- **Limitation**: Nodes never referenced in activation_log (e.g. WHO_I_AM) cannot be recovered; their access_count will accumulate correctly going forward
- **Note per CTO ruling**: activation_log is the only audit surface; historical counts for nodes not in activation_log are genuinely unrecoverable

## Test Results

```
12 passed in 0.24s

TestAddNodePreservesState::test_access_count_preserved_on_re_add PASSED
TestAddNodePreservesState::test_last_accessed_preserved_on_re_add PASSED
TestAddNodePreservesState::test_created_at_preserved_on_re_add PASSED
TestAddNodePreservesState::test_base_activation_preserved_on_re_add PASSED
TestAddNodePreservesState::test_embedding_preserved_on_re_add PASSED
TestAddNodePreservesState::test_triggers_preserved_on_re_add PASSED
TestAddNodeNewInsert::test_new_node_insert PASSED
TestAddNodeNewInsert::test_content_hash_updated_on_re_add PASSED
TestAddEdgePreservesState::test_co_activations_preserved_on_re_add PASSED
TestAddEdgePreservesState::test_edge_created_at_preserved PASSED
TestBatchImportPreservation::test_batch_import_preserves_counts PASSED
TestNoInsertOrReplace::test_no_insert_or_replace_in_source PASSED
```

## Post-Fix Verification

Ran `aiden_import.py` on production DB after fix:
- 64 nodes imported, 486 edges created
- All 66 nodes with access_count > 0 preserved (verified via query)
- 64/150 nodes now have content_hash populated
- Brain stats unchanged: 150 nodes, 1902 edges, 422 hebbian_edges
