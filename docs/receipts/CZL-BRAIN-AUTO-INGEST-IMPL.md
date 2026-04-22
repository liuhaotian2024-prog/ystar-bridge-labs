Audience: CEO (Aiden) for dispatch closeout + CTO (Ethan) for architectural awareness + eng-platform (Ryan) for boundary wiring dependency
Research basis: CTO ruling CZL-BRAIN-AUTO-INGEST (boundary c+d pattern), Leo's CZL-BRAIN-ADD-NODE-PRESERVE receipt (add_node now safe), empirical review of aiden_brain.py/aiden_import.py signatures, production smoke test of increment_access_count on WHO_I_AM node
Synthesis: brain_auto_ingest.py implements scan_sources + extract_candidates + apply_ingest with hash-based dedup and activation_log emission; increment_access_count wired in both auto_ingest module and aiden_brain.py; 38 regression tests all green

# CZL-BRAIN-AUTO-INGEST-IMPL Receipt

**Author**: eng-kernel (Leo Chen)
**Date**: 2026-04-19
**Status**: COMPLETE
**Maturity**: L4 SHIPPED

## CIEU 5-Tuple

- **Y***: auto-ingest module shipped + access_count increment path wired + regression tests green
- **Xt**: Ethan ruled boundary (c)+(d); aiden_import was monolith scanning only knowledge/ceo/wisdom/; access_count never incremented by activation_log writes; no auto-ingest module existed
- **U**: (1) Created brain_auto_ingest.py (299 LOC) with scan_sources/extract_candidates/apply_ingest/increment_access_count (2) Added increment_access_count to aiden_brain.py (3) Wrote 38 regression tests covering 9 test classes (4) Fixed _infer_depth priority ordering (5) Fixed sqlite3.Row.get() incompatibility (6) Smoke-tested on production brain (WHO_I_AM 0->1)
- **Yt+1**: calling brain_auto_ingest.scan_sources() + apply_ingest() ingests files from reports/knowledge/memory with content_hash dedup, writes activation_log entries at level 0.3, creates proximity edges for same-dir batch, and increment_access_count works for CIEU-event-triggered node access
- **Rt+1**: 0

## Files Created/Modified

| File | Change |
|------|--------|
| `Y-star-gov/ystar/governance/brain_auto_ingest.py` | NEW: 299 LOC semantic module with scan_sources, extract_candidates, apply_ingest, increment_access_count, sentinel persistence, content-hash dedup, CLI entry point |
| `ystar-company/scripts/aiden_brain.py` | ADDED: increment_access_count(node_id) function -- the missing code path per CTO ruling Q8 |
| `Y-star-gov/tests/governance/test_brain_auto_ingest.py` | NEW: 38 tests in 9 classes covering all invariants |

## Test Results

```
38 passed in 107.25s

TestContentHash (3 tests): deterministic, different content, length 16
TestNodeIdScheme (3 tests): slash separator, spaces to underscore, nested path
TestInferType (4 tests): reports, knowledge, memory, unknown
TestInferDepth (4 tests): wisdom->kernel, lessons->tactical, cto->operational, default
TestExtractSummary (3 tests): frontmatter, short lines skipped, fallback
TestScanSources (4 tests): finds new md, ignores non-md, hash dedup skips unchanged, detects changed content
TestApplyIngest (7 tests): ingests nodes, content_hash populated, no double ingest, access_count preserved on re-ingest, activation_log written, co-activation edges same dir
TestIncrementAccessCount (4 tests): increments from zero, multiple times, updates last_accessed, nonexistent node no crash
TestSentinel (2 tests): persists across runs, fresh returns defaults
TestFullMode (1 test): re-ingests unchanged after sentinel clear
TestCIEUEvents (2 tests): event increments access_count, empty DB graceful
TestErrorResilience (1 test): unreadable file skipped
TestCreatedAtPreservation (1 test): created_at not reset on update
```

## Production Smoke Test

```
WHO_I_AM access_count: 0 -> 1 (delta: 1)
PASS: increment_access_count works on production brain
```

## Architectural Notes

- Module location: `Y-star-gov/ystar/governance/brain_auto_ingest.py` (product-core per Ethan's owner split)
- Sentinel file: `scripts/.brain_ingest_sentinel.json` (tracks file_hashes + last_cieu_id)
- Auto-ingest activation_level: 0.3 (moderate warmth per CTO ruling section 5)
- access_count NOT incremented by auto-ingest (only by explicit activate/touch/increment_access_count)
- Co-activation: same-directory files get bidirectional proximity edges with co_activations counter
- Error resilience: per-file try/except, non-fatal CIEU DB unavailability, PRAGMA busy_timeout=5000
- CLI: `brain_auto_ingest.py --mode delta|full [--company-root PATH] [--brain-db PATH]`

## Dependency for eng-platform (Ryan)

Ryan can now wire `brain_auto_ingest.py --mode delta` into:
1. `governance_boot.sh` (after ALL SYSTEMS GO)
2. `session_close_yml.py` (after secretary_curate block)

The module outputs JSON to stdout: `{"ingested": N, "skipped": M, "errors": E, "total_scanned": T, "cieu_activations": C}`
