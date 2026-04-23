# Patent 63/981,777 Claim 1 — Merkle Seal Wire-up Receipt

```yaml
Y_star: seal_session() fires on every session close + all historical sessions backfilled
Xt: 0 sealed events, 0 sealed_sessions rows (pre-fix baseline)
U:
  - Wire seal_session() into session_close_yml.py (session close production path)
  - Create scripts/backfill_merkle_sealing.py (one-shot historical backfill CLI)
  - Run backfill on production .ystar_cieu.db
Yt1: 659489 sealed events, 29671 sealed_sessions rows, wire-up live for all future sessions
Rt1: 0
tool_uses: 14
cieu_event_ids:
  backfill_run: 7988118d-6567-4a62-80e3-8b097f0dd6fd
  wire_up: (SESSION_SEALED emits on next real session close — wire-up is in session_close_yml.py:428-465)
```

---

## What was done

### Wire-up (session_close_yml.py)

Added 30 lines at the session close path (after `session_close` CIEU event, before `update_priority_brief`):

1. Instantiates `CIEUStore` with the session's CIEU DB path
2. Calls `store.seal_session(sid)` — idempotent (INSERT OR REPLACE)
3. On success with events > 0: emits `SESSION_SEALED` CIEU event with merkle_root, prev_root, sealed_at, event_count
4. On failure: logs warning to stderr + emits `SESSION_SEAL_FAILED` CIEU warn event, does NOT block session close
5. Also fixed missing `emit_cieu` import (pre-existing bug — `write_board_lessons()` called it without import)

### Backfill script (scripts/backfill_merkle_sealing.py)

- `--dry-run`: counts unsealed sessions without writing
- `--help`: argparse help
- `--db`: optional DB path override
- Iterates `SELECT DISTINCT session_id FROM cieu_events LEFT JOIN sealed_sessions ... WHERE ss.session_id IS NULL`
- Emits `BACKFILL_MERKLE_SEALING_RUN` CIEU event at completion with success/fail/total breakdown

## SQL proof

```
BEFORE:
  SELECT COUNT(*) FROM cieu_events WHERE sealed = 1;  →  0
  SELECT COUNT(*) FROM sealed_sessions;                →  0

AFTER:
  SELECT COUNT(*) FROM cieu_events WHERE sealed = 1;  →  659489
  SELECT COUNT(*) FROM sealed_sessions;                →  29671
```

## Files modified

- `scripts/session_close_yml.py` — wire-up trigger + import fix (lines 27, 428-465)
- `scripts/backfill_merkle_sealing.py` — new file (backfill CLI)
- `reports/kernel/patent_claim1_wireup_receipt_20260423.md` — this receipt
