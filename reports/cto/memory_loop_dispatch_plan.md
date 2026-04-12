# Memory Loop Closure — Dispatch Plan

**Author**: Ethan Wright (CTO)
**Date**: 2026-04-12
**Upstream**: `reports/proposals/cto_memory_loop_closure_l2.md` (Board-approved 2026-04-12)
**Scope**: 3 original closures + 1 increment (Secretary auto-memory sync)
**Total estimate (parallel)**: ~1.5 engineering days + 24h smoke test

---

## 0. Architectural anchors (verified before dispatch)

- CIEU writer: `Y-star-gov/ystar/adapters/cieu_writer.py` — `_write_cieu`, `_write_session_lifecycle`, `_write_boot_record`. All three already share the "silent-fail, non-blocking" contract. This is the correct splice point for closure 1.
- CIEU store: `Y-star-gov/ystar/governance/cieu_store.py` (`CIEUStore.write_dict`).
- Memory store: `Y-star-gov/ystar/memory/store.py` (`MemoryStore.remember(mem, cieu_ref)`).
- Memory types registry: `Y-star-gov/ystar/memory/models.py` `BUILT_IN_MEMORY_TYPES`. **Critical gap**: neither `environment_assumption` nor `insight` nor `environment_change` exists today. Maya must add them in the same commit as closure 1.
- Active task: `ystar-company/scripts/active_task.py` line 225 — `INTENT_COMPLETED` CIEU emission. Hook insertion point for closure 3 is immediately after `save_state(role, current)` on line 223.
- Boot script: `ystar-company/scripts/governance_boot.sh` currently ends at STEP 10 (line 253–292). Closure 2 adds STEP 11 before `exit $FAILURES`.
- Active agent token: `ystar-company/.ystar_active_agent` (single line role name). Confirmed working via `echo cto > .ystar_active_agent`.

---

## 1. Closure 1 — CIEU → memory.db event bridge

**Owner**: Maya Patel (eng-governance) **Helper**: Ryan (platform, for queue plumbing)

### Files touched
- **NEW** `Y-star-gov/ystar/memory/ingest.py` — bridge module
- **EDIT** `Y-star-gov/ystar/adapters/cieu_writer.py` — call bridge after successful `write_dict`
- **EDIT** `Y-star-gov/ystar/memory/models.py` — add 4 new `MemoryType` rows: `environment_assumption` (half-life 365d), `insight` (180d), `environment_change` (30d), `human_directive` (365d)
- **NEW** `Y-star-gov/tests/test_memory_ingest.py`

### Public surface
```python
# ystar/memory/ingest.py
def should_ingest(event: dict) -> tuple[bool, str | None]:
    """Pure function. Returns (ingest?, memory_type). No I/O, no LLM."""

def enqueue(event: dict, memory_db_path: str) -> None:
    """Non-blocking. Drops event onto in-process queue. Safe to call from hook."""

def _worker_loop() -> None:
    """Background thread. Drains queue, writes to MemoryStore. Silent-fail."""

def start_worker(memory_db_path: str) -> None:
    """Lazily spawn daemon thread on first enqueue. Idempotent."""
```

### Trigger rules (pure, deterministic — Iron Rule 1 safe)
```
decision == "deny" AND max(violation.severity, default=0) >= 0.7   → memory_type="lesson"
params.get("drift_detected") == 1                                    → memory_type="environment_change"
event_type in {"insight","decision","lesson","environment_change"}  → memory_type=event_type
params.get("human_initiator")                                        → memory_type="human_directive"
```
No LLM, no network, no regex over free-text content. Severity comes from `violation.severity` in params (Maya: extend violation dataclass if missing — check `ystar/session.py:Violation`).

### Concurrency
- Single `queue.Queue(maxsize=1000)` module-global.
- Single daemon thread started lazily on first `enqueue`.
- Queue full → drop + `_log.warning("memory ingest queue full")`. Never block.
- Worker catches all exceptions, logs, continues.

### Splice point in cieu_writer._write_cieu
Immediately after `store.write_dict(...)`:
```python
try:
    from ystar.memory.ingest import enqueue
    enqueue({
        "event_type": tool_name,
        "decision": "allow" if result.allowed else "deny",
        "violations": [{"dimension": v.dimension, "severity": getattr(v,"severity",0.0), "message": v.message} for v in (result.violations or [])],
        "params": params,
        "agent_id": who,
        "session_id": session_id,
        "cieu_ref": None,  # store.write_dict should return rowid; if so, pass it
    }, memory_db_path=_resolve_memory_db())
except Exception:
    pass  # fail-open
```
`_resolve_memory_db()` reads `.ystar_session.json["memory_db"]` same pattern as `load_db()` in active_task.py.

### Tests
- `test_should_ingest_deny_high_severity` — returns `(True, "lesson")`.
- `test_should_ingest_allow_normal` — returns `(False, None)`.
- `test_enqueue_nonblocking_when_full` — fill queue, assert call returns < 10ms.
- `test_worker_writes_memory` — enqueue → sleep 0.2s → query MemoryStore, assert 1 row.
- `test_hook_path_no_llm_import` — import-time assertion that `openai`, `anthropic` are not in `sys.modules` after importing ingest.

### Commit
`feat(memory): CIEU→memory event bridge with trigger rules [closure-1]`

---

## 2. Closure 2 — boot-time memory_consistency_check (STEP 11)

**Owner**: Ryan Park (eng-platform) **Helper**: Maya

### Files touched
- **NEW** `ystar-company/scripts/memory_consistency_check.py`
- **EDIT** `ystar-company/scripts/governance_boot.sh` — append STEP 11 block before `exit $FAILURES`
- **NEW** `ystar-company/tests/test_memory_consistency_check.py`

### Behavior
`memory_consistency_check.py` exits with:
- `0` if no drift
- non-zero + stdout `MEMORY_DRIFT_DETECTED: <dimension>=<old>→<now>; ...` when any mismatch

### Checked dimensions
1. `platform` — `sys.platform`
2. `cwd` — `os.getcwd()` vs stored value (expected: `/Users/haotianliu/.openclaw/workspace/ystar-company`)
3. `git_remote` — `git config --get remote.origin.url`
4. `git_branch` — `git rev-parse --abbrev-ref HEAD`
5. `python_version` — `sys.version_info[:2]`
6. `critical_paths` — each of: `CLAUDE.md`, `AGENTS.md`, `scripts/governance_boot.sh`, `.ystar_session.json`, `Y-star-gov source dir from session.json`. Non-existence = drift.

### Storage model
Each dimension stored as one `environment_assumption` memory with content JSON: `{"dimension":"cwd","value":"/Users/..."}`. First-run bootstrap: if no assumptions exist for this agent, write current values (no drift reported). Subsequent runs compare.

### governance_boot.sh integration
```bash
# STEP 11: Memory consistency check
echo "-- STEP 11: memory_consistency_check --"
if python3.11 "$REPO_ROOT/scripts/memory_consistency_check.py" --agent "$AGENT_ID" 2>&1; then
    echo "  ok: no environment drift"
else
    echo "  FAIL: MEMORY_DRIFT_DETECTED (see above)"
    FAILURES=$((FAILURES+1))
    echo "MEMORY_DRIFT_PENDING_ACK=1" >> "$REPO_ROOT/.ystar_session_flags"
fi
```
Agent sees `.ystar_session_flags` during its first turn → must emit explicit "ack drift: update|revoke|keep" sentence. (Enforcement of this is policy-layer, out of scope for this closure — file the flag, Board behavior rules handle reaction.)

### Override
`--force-write` CLI flag refreshes all assumptions to current env. Board uses this when intentionally moving the repo. Script logs to CIEU as `event_type=environment_assumption_reset`.

### Tests
- `test_first_run_bootstraps_no_drift`
- `test_cwd_change_detected`
- `test_critical_path_missing_detected`
- `test_force_write_refreshes`

### Commit
`feat(boot): STEP 11 memory consistency check with drift detection [closure-2]`

---

## 3. Closure 3 — continuation.json streaming update

**Owner**: Ryan Park (eng-platform) **Helper**: Leo (if active_task signature changes)

### Files touched
- **EDIT** `ystar-company/scripts/active_task.py` — insert hook at end of `complete()` path
- **NEW** `ystar-company/scripts/continuation_writer.py` — atomic writer
- **NEW** `ystar-company/tests/test_continuation_streaming.py`

### continuation_writer API
```python
def rewrite_continuation(repo_root: Path, updates: dict) -> None:
    """
    Reads memory/continuation.json, merges updates, writes atomically.
    - temp file in same directory → os.replace → rename (atomic on POSIX)
    - adds/refreshes last_updated_ts = time.time()
    - idempotent: identical updates produce byte-identical file (aside from ts)
    - fail-open: all exceptions swallowed + logged to scripts/hook_debug.log
    """
```

### Merge semantics on INTENT_COMPLETED
Given `current` task dict from active_task.complete, apply:
- `action_queue`: find item where `task_id == current["task_id"]` → set `done=True`, `completed_at=ts`.
- `obligations`: for each obligation whose `cleared_by == task_id` → remove.
- `team_state[role]`: set `last_completed = current["task"]`, `last_completed_at = ts`.

If keys don't exist, no-op (idempotent).

### Splice point (active_task.py line ~228, after `write_cieu(...,"INTENT_COMPLETED",...)`)
```python
try:
    from continuation_writer import rewrite_continuation
    rewrite_continuation(REPO_ROOT, {
        "event": "INTENT_COMPLETED",
        "task_id": current["task_id"],
        "role": role,
        "task": current["task"],
        "output": current.get("output"),
    })
except Exception as e:
    with open(REPO_ROOT/"scripts"/"hook_debug.log","a") as f:
        f.write(f"[{time.time()}] continuation hook failed: {e}\n")
```

### Atomicity guarantee
```python
tmp = target.with_suffix(f".tmp.{os.getpid()}")
tmp.write_text(json.dumps(new_state, indent=2))
os.replace(tmp, target)  # atomic rename on POSIX
```

### Tests
- `test_rewrite_updates_action_queue_item`
- `test_rewrite_is_idempotent_modulo_timestamp`
- `test_rewrite_atomic_no_partial_on_kill` (simulate via `os.kill` mid-write in subprocess)
- `test_missing_continuation_file_bootstraps`

### Commit
`feat(active_task): stream continuation.json on INTENT_COMPLETED [closure-3]`

---

## 4. Increment 4 — Secretary auto-memory sync

**Owner**: Ryan Park + Secretary (Samantha) collab

### Prerequisite — write-path whitelist verification (BLOCKER if fails)
Before writing any code, Ryan runs:
```bash
echo 'probe' > "$HOME/.claude/projects/-Users-haotianliu--openclaw-workspace-ystar-company/memory/.probe.md"
```
as Secretary agent. If hook denies → file L3 amendment to `.ystar_session.json` extending `secretary.write_paths` with `~/.claude/projects/**/memory/**`. **Do not bypass the hook.** Do not `--no-verify`. If denied, halt closure 4 and report to CEO for Board L3 sign-off. The other 3 closures proceed regardless.

### Files touched
- **NEW** `ystar-company/scripts/secretary_auto_memory_sync.py`
- **NEW** `ystar-company/tests/test_auto_memory_sync.py`
- **EDIT** `ystar-company/scripts/cron_install.sh` (if exists) — add 30-min schedule

### Scan sources
For every `role ∈ {ceo,cto,cmo,cso,cfo,secretary,eng-*}`:
- `knowledge/{role}/feedback/*.md`
- `knowledge/{role}/decisions/*.md`
- `knowledge/{role}/lessons/*.md`

### Frontmatter contract (auto-memory standard)
```yaml
---
memory_id: auto_<sha8 of source path + source mtime>
agent_id: {role}
memory_type: {decision|lesson|feedback→insight}
source: knowledge/{role}/decisions/<file>
source_mtime: <epoch>
initial_score: 0.8
half_life_days: 90
tags: [auto_sync, {role}]
---
<body = extract first paragraph or summary block from source>
```

### Idempotency
Key = `memory_id`. If target `.md` exists and `source_mtime` matches → skip. If source was deleted → remove target (tombstone) and log.

### Output paths
Target directory: `~/.claude/projects/-Users-haotianliu--openclaw-workspace-ystar-company/memory/auto/{role}/<memory_id>.md`
Index file: `~/.claude/projects/.../memory/MEMORY.md` — table: `memory_id | agent | type | source | last_sync`

### Scheduling
- Manual: `python3 scripts/secretary_auto_memory_sync.py --role all` (Secretary can run on demand).
- Cron: `*/30 * * * * cd /Users/haotianliu/.openclaw/workspace/ystar-company && python3 scripts/secretary_auto_memory_sync.py --role all >> scripts/hook_debug.log 2>&1`

### Tests
- `test_frontmatter_generation`
- `test_idempotent_no_change_second_run`
- `test_tombstone_on_source_delete`
- `test_index_md_updated`
- `test_halts_gracefully_if_write_path_denied` (mock hook deny → log and exit 0)

### Commit
`feat(secretary): auto-memory sync from knowledge/**→claude-memory [increment-4]`

---

## 5. Execution timeline

| Day | Parallel lane A (Maya) | Parallel lane B (Ryan) | Gate |
|-----|------------------------|------------------------|------|
| D0 AM | Add 4 memory types + `ingest.py` stub + trigger-rule tests | Write `memory_consistency_check.py` + bootstrap test | — |
| D0 PM | `enqueue`/worker thread + integration test + splice cieu_writer | Wire STEP 11 into boot.sh + first drift test | Closure 1, 2 commits |
| D1 AM | (review Ryan's PR) | `continuation_writer.py` + atomic test + active_task splice | Closure 3 commit |
| D1 PM | (unblock closure 4 if whitelist ok) | `secretary_auto_memory_sync.py` + cron | Closure 4 commit (conditional) |
| D2 00:00–D3 00:00 | 24h smoke run on Bridge Labs | | Evidence report |

## 6. 24h smoke-test plan

Evidence must appear in `reports/cto/memory_loop_closure_evidence.md`:
1. **Closure 1**: Dump `.ystar_memory.db` — count rows where `source_cieu_ref IS NOT NULL AND created_at > T0`. Target ≥ 5 auto-ingested memories.
2. **Closure 2**: Run `scripts/memory_consistency_check.py --simulate-drift cwd=/tmp/fake` in a subshell → assert exit ≠ 0 and stdout contains `MEMORY_DRIFT_DETECTED: cwd=`.
3. **Closure 3**: During session mid-run, run 3 `active_task complete` calls for different tasks → snapshot `memory/continuation.json` mtime after each → assert all 3 distinct + `last_updated_ts` monotone.
4. **Closure 4** (if shipped): `ls ~/.claude/projects/.../memory/auto/` shows ≥ 1 file per role that has any feedback/decisions/lessons.

## 7. Commit & rollback strategy

- Each closure = 1 commit. 4 commits total. No squash.
- Ordering: closure 1 → 2 → 3 → 4. Each revertable independently via `git revert`.
- Ystar-gov commits pushed to its repo; ystar-company commits pushed to company repo. Tag linking: commit message trailer `Related: <other-repo-hash>`.
- No `--no-verify`, no `--amend`. Hook failure → fix forward with a new commit.

## 8. Known risks / Board decision points

1. **New memory_types are a schema-compatible addition**, no migration needed (SQLite `INSERT OR IGNORE` in `_seed_memory_types`). Safe.
2. **Violation severity field may not exist today** on `ystar.session.Violation`. Maya must verify; if absent, adding optional `severity: float = 0.0` is a non-breaking dataclass change — **does not need Board approval** (internal model).
3. **Closure 4 may require L3 `.ystar_session.json` amendment** to `secretary.write_paths`. **This does need Board approval**. File amendment draft alongside closure 4 PR; do not merge closure 4 until Board signs.
4. **Memory DB contention**: event bridge + boot check + sync script all writing to `.ystar_memory.db`. SQLite WAL is already on (see `store.py:93`). No extra lock needed, but if tests flake, Maya switches to `busy_timeout=5000`.
5. **No regression to Iron Rule 1** (no LLM on check path). The bridge is pure Python trigger rules; ingest.py has a unit test that asserts no LLM SDKs imported.

---

## 9. Assignments summary

| Closure | Lead | Repo | Est |
|---------|------|------|-----|
| 1 CIEU→memory bridge | Maya (eng-governance) | Y-star-gov | 0.75d |
| 2 boot consistency check | Ryan (eng-platform) | ystar-company | 0.5d |
| 3 continuation streaming | Ryan (eng-platform) | ystar-company | 0.5d |
| 4 secretary auto-sync | Ryan + Samantha | ystar-company | 0.5d (+Board wait) |

**Hand-off protocol**: each engineer sets `.ystar_active_agent` to their role, runs `governance_boot.sh <role>`, implements + tests, commits, then resets `.ystar_active_agent=cto` and writes a one-line completion note to `reports/cto/memory_loop_closure_evidence.md`.

---

## 10. Execution-environment blocker (reported to CEO)

This plan was drafted by CTO Ethan. **Per CLAUDE.md "单机运行原则" (AMENDMENT-004, 2026-04-12)**, actual code implementation is performed in-session by CTO/engineer sub-agents on the same Mac (`/Users/haotianliu/.openclaw/workspace/ystar-company`) — no cross-machine dispatch. The plan file remains the formal dispatch artifact; CEO hands it off via Agent tool to the relevant sub-agent.
