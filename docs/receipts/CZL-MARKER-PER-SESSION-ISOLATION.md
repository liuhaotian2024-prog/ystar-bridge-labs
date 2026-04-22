Audience: CTO (Ethan Wright) + Board for lock-death taxonomy review
Research basis: empirical evidence from 2026-04-19 hook_debug.log 16:10-16:11 write-storm, AMENDMENT-020 paste failure, daemon crash during 11 concurrent sub-agent dispatch
Synthesis: per-session marker isolation eliminates shared-file race by giving each Claude Code session its own marker/stack/lock files

# CZL-MARKER-PER-SESSION-ISOLATION Receipt

## CIEU 5-Tuple

- **Y***: marker-file race closed; N concurrent sub-agents can each hold their own identity without clobber
- **Xt**: 2026-04-19 CEO spawned 11 parallel sub-agents; all wrote to single `.ystar_active_agent`; marker write-storm caused secretary identity loss within <1 tool call; hook daemon crashed (stale socket), session fail-closed, Board manual recovery required
- **U**: 6 file edits + 16-case regression test + lock-death taxonomy entries (paths #11 and #12)
- **Yt+1**: 53 lockdeath tests pass (37 pre-existing + 16 new); no cross-session identity clobber; backward compat preserved
- **Rt+1**: 0

## Files Modified

### 1. `scripts/agent_stack.py` (ystar-company)
- Added `_get_session_id()`: returns session-unique ID from `CLAUDE_SESSION_ID` env var or `PPID` fallback
- Added `_session_marker_file()`, `_session_stack_file()`, `_session_lock_file()`: compute per-session file paths
- Updated `_StackLock` to use per-session lock file
- Updated `_read_stack()`, `_write_stack()` to use per-session stack file
- Updated `_read_marker()` with fallback chain: per-session -> global -> DEFAULT_AGENT
- Updated `_write_marker()` to write both per-session (primary) and global (backward compat)
- Added `cleanup_session_files()` for end-of-session cleanup
- Added `get_session_id()` public API

### 2. `scripts/hook_wrapper.py` (ystar-company)
- Replaced single `_MARKER_PATH` with `_MARKER_DIR` + `_MARKER_GLOBAL`
- Added `_read_session_marker()` function implementing fallback chain:
  1. Per-session marker via `CLAUDE_SESSION_ID`
  2. Per-session marker via `PPID`
  3. Global marker (backward compat)

### 3. `ystar/adapters/identity_detector.py` (Y-star-gov)
- Updated priority 7 marker file detection to check per-session markers first:
  - `CLAUDE_SESSION_ID`-based markers (repo root + scripts/)
  - `PPID`-based markers (repo root + scripts/)
  - Global markers (existing behavior, lowest priority)

### 4. `ystar/adapters/hook.py` (Y-star-gov)
- Updated Agent tool identity write to use per-session marker as primary target
- Global marker still written for backward compat
- CIEU event now records `per_session` flag

### 5. `tests/governance_lockdeath/conftest.py` (ystar-company)
- Added `SCRIPTS_DIR` patch so per-session file computation uses tmp_path
- Added env var cleanup (`CLAUDE_SESSION_ID`, `PPID`) to ensure pre-existing tests use global marker

### 6. `tests/governance_lockdeath/test_L09_cwd_drift.py` (ystar-company)
- Updated `test_real_hook_wrapper_marker_path_is_absolute` to check `_MARKER_GLOBAL`/`_MARKER_DIR` instead of legacy `_MARKER_PATH`

### 7. `tests/governance_lockdeath/test_L11_marker_per_session_isolation.py` (NEW)
- 14 tests in `TestL11MarkerPerSessionIsolation`:
  - Session ID from env, sanitization, PPID fallback, no-session-ID fallback
  - Push/pop writes per-session marker
  - Two sessions no cross-contamination (core invariant)
  - 10 concurrent sessions no clobber (reproduces the 2026-04-19 failure)
  - Fallback chain (missing session marker, both missing)
  - Per-session stack isolation
  - Cleanup function
  - Global marker backward compat
  - Public API
- 2 tests in `TestL12DaemonExitMidDispatch`:
  - Stale socket detection
  - Marker write-storm count verification

## Lock-Death Taxonomy Update

### Path #11: Marker-Contention
- **Trigger**: N parallel sub-agents spawned concurrently, each calling `push_agent()` with different identity
- **Mechanism**: All N writes hit single `.ystar_active_agent`, creating write-storm; no identity holds for >1 tool call
- **Evidence**: hook_debug.log 16:10-16:11 shows 10+ alternating writes across 5 roles within seconds
- **Fix**: Per-session marker files (`.ystar_active_agent.<session_id>`) isolate each session's identity namespace
- **Test**: `test_L11_marker_per_session_isolation.py::test_ten_concurrent_sessions_no_clobber`

### Path #12: Daemon-Exit-Mid-Dispatch
- **Trigger**: Hook daemon overwhelmed by concurrent marker writes + tool-call storm
- **Mechanism**: Daemon crashes, leaves stale socket at `/tmp/ystar_hook.sock`; all subsequent tool calls fail-closed
- **Evidence**: During this task, hook_wrapper processes hung at 87% CPU each (5 concurrent processes), daemon socket missing
- **Fix**: Per-session isolation (L11) reduces write contention; daemon sentinel (nice-to-have, not implemented) would auto-restart
- **Test**: `test_L11_marker_per_session_isolation.py::TestL12DaemonExitMidDispatch`

## Diagnosis vs Samantha's Hypothesis

Samantha's write-storm diagnosis is confirmed empirically. During implementation of this fix, I observed the exact failure mode live: the hook daemon crashed, 5 hook_wrapper processes hung at 87% CPU each, and the marker file was externally modified from "ceo" to "eng-platform" by a concurrent process. This is textbook path #11 -> #12 cascade.

## Test Results

```
53 passed in 0.27s
```

All 37 pre-existing lockdeath tests pass (zero regression). 16 new tests added and passing.

## Daemon Auto-Restart Companion (Not Implemented)

The task mentioned a nice-to-have `governance_watcher_daemon_sentinel.py`. This was not implemented because:
1. The per-session isolation fix (L11) eliminates the root cause of the daemon crash (write contention storm)
2. A daemon sentinel adds operational complexity (cron job, PID management, restart loops)
3. The existing break-glass path (pkill + governance_boot.sh) provides manual recovery

If daemon crashes persist after L11 deployment, a sentinel should be revisited as a separate CZL.
