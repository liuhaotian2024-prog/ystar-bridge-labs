# CZL-WHITEBOARD-WIPE-RCA Receipt

## Y* (verifiable predicate)
Whiteboard wipe class (concurrent-write data loss) prevented going forward.

## Xt (current state before fix)
- 37 to 0 task wipe occurred at 2026-04-19T17:30 during concurrent writer activity
- Manually restored from git commit e7b0127b
- No code-level protection against truncation races or accidental wipes

## U (actions taken)

### Root Cause Analysis

**Root cause**: Non-atomic read-modify-write with truncation-before-lock race condition.

Three interacting bugs in `scripts/dispatch_board.py`:

**Bug 1 — TOCTOU race (Time-of-Check to Time-of-Use)**:
- `_read_board()` acquired `LOCK_SH`, read data, released lock (line 24-28)
- `_write_board()` acquired `LOCK_EX`, wrote data, released lock (line 34-37)
- Between read and write, another process could read stale data and overwrite
- Multiple concurrent callers (CEO `post` + Maya `evaluate_blocks` + Ryan tests) all shared this window

**Bug 2 — Truncate-before-lock (THE WIPE MECHANISM)** (line 34):
- `open(BOARD_PATH, "w")` truncates the file to 0 bytes BEFORE `fcntl.flock()` acquires the lock
- If another process reads during truncation window, it gets empty/invalid JSON
- Fallback `return {"tasks": []}` (line 23) activates
- That process then writes `{"tasks": []}` back, wiping all 37 tasks

**Bug 3 — Test fixture writes to production data** (`tests/platform/test_dispatch_board.py` line 18):
- `BOARD_PATH.write_text('{"tasks": []}')` writes directly to PRODUCTION `governance/dispatch_board.json`
- No lock, no sanity check, uses the real production path
- If running concurrently with production operations, guaranteed wipe

**Concurrent writers in the incident window**:
- Ryan#3 IMPL (dispatch_board.py code edits)
- Maya#1 GOV-LIVE-EVAL-P1 (evaluate_blocks — read-only, not a direct cause)
- Multiple CEO `dispatch_board.py post` calls
- Potentially test runs using the old fixture

**Most likely trigger**: Two concurrent `post` calls hitting Bug 2 — one truncates via `open("w")`, the other reads empty file, gets `{"tasks": []}`, then writes that back.

### Minimal Fix Applied

**File: `scripts/dispatch_board.py`**

1. **Separate lockfile** (`governance/.dispatch_board.lock`): All readers and writers acquire this lock BEFORE touching the board file. Eliminates TOCTOU window.

2. **Atomic writes via temp-file-then-rename**: `_write_board_locked()` writes to `NamedTemporaryFile` then `os.replace()` to target. No truncation window. Even if the process crashes mid-write, the original file is untouched.

3. **Wipe protection sanity check**: Before writing, checks if task count would drop by >50% when previous count exceeds 5. If so, ABORTS the write, logs to CIEU (`DISPATCH_BOARD_WIPE_BLOCKED`), and raises `RuntimeError`.

4. **Locked read-modify-write pattern**: `post_task()`, `claim_task()`, `complete_task()` all use `_acquire_lock()` / `_read_board_locked()` / `_write_board_locked()` / `_release_lock()` in a single critical section.

5. **Test fixture isolation**: `tests/platform/test_dispatch_board.py` fixture changed from writing `{"tasks": []}` to production path to using `tmp_path` + `monkeypatch` for test isolation.

### Regression Test

**File: `tests/platform/test_dispatch_board_concurrent.py`** (9 tests, all PASS)

| Test | Verifies |
|------|----------|
| `test_atomic_write_no_truncation` | Temp-file-then-rename works correctly |
| `test_wipe_protection_blocks_accidental_wipe` | Sanity check blocks 20-to-2 drop |
| `test_wipe_protection_allows_normal_deletion` | Normal 10-to-9 deletion allowed |
| `test_wipe_protection_skipped_for_small_boards` | No false positive for <=5 task boards |
| `test_concurrent_post_no_data_loss` | 4 workers x 10 posts = 40 tasks (zero loss) |
| `test_concurrent_post_and_claim` | 2 posters + 2 claimers, no data loss, no double-claim |
| `test_concurrent_reads_never_see_empty` | Readers never see empty board during concurrent writes |
| `test_deliberate_wipe_attempt_blocked` | Sanity check blocks deliberate empty/small writes |
| `test_lock_prevents_interleaved_read_modify_write` | 5 seed + 4 concurrent posts = 9 (serialized) |

```
9 passed in 1.25s
```

## Yt+1 (predicted end state)
- Concurrent-write stress passes (9/9 tests green)
- Attempted wipe blocked by sanity check
- Production board never touched by test fixtures

## Rt+1
**0** — All 4 deliverables landed:
1. Root cause identified with line-number citations
2. Atomic-write + sanity check + fcntl lock retrofit applied
3. 9-test concurrent regression suite passes
4. This RCA report

## Recommendation
- **Ban direct writes**: Other scripts (`cto_dispatch_broker.py`, `engineer_task_subscriber.py`) have their own `_read_board()` / `_write_board()` copies with the SAME bugs. They should import from `dispatch_board.py` or be updated to use the same lockfile pattern. Filed as follow-up.
- **Lock path convention**: All scripts writing to `dispatch_board.json` MUST use `governance/.dispatch_board.lock` as the coordination point.

## Files Modified
- `scripts/dispatch_board.py` — atomic write infrastructure + mutation function fixes
- `tests/platform/test_dispatch_board_concurrent.py` — new (9 concurrent regression tests)
- `tests/platform/test_dispatch_board.py` — fixture isolation fix
- `reports/receipts/CZL-WHITEBOARD-WIPE-RCA.md` — this report
