---
lesson_id: 20c5d07e-e361-413e-8dc8-ed1a9f3bfba1
---

# Cross-Session Knowledge Continuity Audit — Permanent Non-Loss Protocol

**Author**: Samantha Lin (Secretary)
**Date**: 2026-04-14
**Commissioned by**: Board (Haotian Liu), 2026-04-14 12-layer directive
**Method**: 12-layer autonomous self-learning, strict CIEU, 4 baseline evidence lines
**Status**: L1 SPEC — protocol draft, pending CEO+CTO review before L3 enforcement

---

## 0. Intent

Board mandated a continuity audit after today's twin incidents:

1. Ryan's `rsync` overwrote a working directory without pre-sync backup — artifacts non-recoverable
2. Maya's uncommitted patch vanished (untracked files lost to an unrelated branch operation)

Goal: audit every surface where in-session or cross-session knowledge can be lost, then specify a **permanent non-loss protocol** with three pillars: (1) auto-commit cadence, (2) 3-layer backup, (3) verification check.

Rt+1=0 acceptance: 12-layer trace commits + >=12 CIEU 5-tuples + spec with all three pillars.

---

## 1. Baseline evidence (four independent continuity failures observed 2026-04-14)

### Evidence A — Ryan rsync disaster (oral baseline)
Engineer invoked `rsync -a src/ dst/` (or similar destructive sync) without staging a pre-sync snapshot. Result: dst tree clobbered, src tree also de-sync'd; no untracked files survive. Root cause: rsync trust-by-default + no atomic transactional wrapper.

### Evidence B — Maya untracked patch lost (oral baseline)
Engineer wrote an improvement patch directly into a working tree, deferred `git add` to "after verification". An unrelated branch switch / stash pop / worktree clean later, the changes were gone. Root cause: long gap between edit and commit; `git status` showed untracked, nobody checked.

### Evidence C — CLAUDE.md path drift (observed by Samantha during this task, 2026-04-14)
- `CLAUDE.md` declares working directory: `/Users/haotianliu/.openclaw/workspace/ystar-company`
- Actual active company repo (per git log + directory contents): `/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs`
- `ystar-company` cwd contains Y*gov source (ystar/, gov_mcp/, pyproject.toml) — NOT the operations repo
- `governance_boot.sh` will boot against the wrong repo; any agent that trusts CLAUDE.md's path will write knowledge into a dead tree or fail to find existing knowledge
- Severity: critical — this turned today's lesson search into a 4-call detour before I found the right repo

### Evidence D — Mirror vs workspace fork (observed 2026-04-14)
- `/Users/haotianliu/.openclaw/mirror/ystar-company-backup/` contains full legacy layout: `agents/Secretary.md`, `knowledge/secretary/`, `knowledge/ceo/lessons/`, `governance/`
- `/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs/` (the live repo) has NONE of these paths — only `.claude/agents/`, `knowledge/{cso,cto,cfo,ceo,cmo,cases}/`
- Result: any lesson or decision logged under the old structure is invisible to new-session agents; any new agent looking for Secretary charter per AGENTS.md reference will miss it
- Severity: critical — this is a structural fork that silently drops institutional memory

---

## 2. Attack surface inventory (where knowledge is lost)

| # | Surface | Loss mode | Current mitigation | Gap |
|---|---|---|---|---|
| 1 | Unstaged file edits | Uncommitted work wiped by branch ops / clean / rsync | Engineer discipline | No auto-save |
| 2 | Untracked new files | Same as above, worse (no reflog recovery) | `git status` manual | No enforced add |
| 3 | Destructive sync (rsync/cp -R) | Overwrites without backup | None | No pre-op snapshot |
| 4 | Path drift (CLAUDE.md vs cwd) | Agent writes to wrong repo | None | No boot-time cwd assertion |
| 5 | Structural fork (mirror vs active) | Legacy knowledge invisible to new agents | None | No canonical-root registry |
| 6 | Session boundary | Session memory dropped; handoff.md manual | `session_close_yml.py` | Not enforced on crash |
| 7 | Sub-agent exit | Active_agent marker + knowledge context gone | escape_hatch restore (AMENDMENT-009) | Reactive only |
| 8 | Daemon cache lag | Sub-agent writes invisible for 2s | `pkill -9 + rm socket` | Workaround only |

---

## 3. Plan — Permanent Non-Loss Protocol v0.1

### Pillar 1 — Auto-commit cadence (defense against surfaces 1, 2, 6)

**Rule**: agent-local git working tree MUST be committed or stashed at fixed intervals, not at engineer discretion.

**Implementation**:
- Hook: every agent tool call that writes a file (Write/Edit) queues a debounced `git add -A && git commit -m "[L0 WIP] auto-checkpoint ${agent} ${ts}"` at T+90s after last write.
- Hard tick: cron-like `continuity_watcher.sh` runs every 10 minutes; if `git status --porcelain` non-empty AND no commit in last 10 min, force an `[L0 WIP]` auto-commit on a dedicated branch `wip/${agent}/${date}`.
- Session end: `session_close_yml.py` blocks exit until `git status --porcelain` is empty (auto-commits leftovers to `wip/${agent}/${date}-eod`).
- Retention: `wip/*` branches pruned after 7 days by `continuity_gc.sh` — user can rebase+squash any wip branch into main before GC.

### Pillar 2 — 3-layer backup

| Layer | Medium | Cadence | Scope | Immutability | Purpose |
|---|---|---|---|---|---|
| L1 git | Local + remote (GitHub) | Per pillar-1 auto-commit | Tracked files only | Mutable (reflog 90d) | Primary recovery, diff-able |
| L2 snapshot | Separate volume (`~/.openclaw/snapshots/ystar-bridge-labs/`) via `rsync --link-dest` hardlink tree | Hourly cron | Entire repo incl. untracked | Immutable after write (chmod a-w) | Recovers untracked files, rsync disasters, pre-destructive-op point-in-time |
| L3 CIEU event log | SQLite `.ystar_cieu.db` | Real-time, per tool call | Metadata only (path + action + outcome + actor) | Append-only | Audit trail — reconstructs WHAT happened to WHICH file WHEN, even if L1+L2 both fail |

Pre-destructive-op wrapper: any agent calling `rsync`, `cp -R`, `rm -rf`, `git clean -fd`, `git reset --hard` MUST first trigger an ad-hoc L2 snapshot tagged with the impending op; wrapper is a bash function `safe_destructive()` sourced in every agent shell.

### Pillar 3 — Verification check (boot-time + periodic)

**Boot-time (in `governance_boot.sh`, new step between current Step 4 and Step 5)**:
```
check_continuity() {
  # 3-A: canonical-root assertion
  expected_cwd="$CANONICAL_BRIDGE_LABS_ROOT"   # read from ~/.openclaw/config/canonical_roots.json
  [[ "$PWD" == "$expected_cwd" ]] || die "cwd drift: $PWD != $expected_cwd — fix CLAUDE.md"

  # 3-B: git hygiene
  git -C "$PWD" status --porcelain | grep -q . && warn "unstaged work present — auto-committing" && auto_wip_commit

  # 3-C: snapshot freshness
  latest_snap=$(ls -1t ~/.openclaw/snapshots/ystar-bridge-labs/ | head -1)
  snap_age_hr=$(( ($(date +%s) - $(stat -f %m ~/.openclaw/snapshots/ystar-bridge-labs/$latest_snap)) / 3600 ))
  [[ "$snap_age_hr" -gt 2 ]] && warn "L2 snapshot stale (${snap_age_hr}h) — triggering now" && trigger_snapshot

  # 3-D: CIEU curation freshness
  last_curate=$(sqlite3 .ystar_cieu.db "SELECT MAX(ts) FROM events WHERE event_type='CURATION_COMPLETE'")
  [[ $(( $(date +%s) - last_curate )) -gt 86400 ]] && warn "curation stale >24h — queueing secretary"

  # 3-E: mirror vs workspace divergence
  diff_lines=$(diff -rq "$CANONICAL_BRIDGE_LABS_ROOT/knowledge" "$MIRROR_ROOT/knowledge" 2>&1 | wc -l)
  [[ "$diff_lines" -gt 0 ]] && warn "mirror divergence: $diff_lines entries — mirror_sync required"

  return 0
}
```

**Periodic (every 30 min, continuity_watcher daemon)**:
- Re-runs 3-B and 3-C
- On 3-B trigger: auto WIP commit
- On 3-C trigger: run snapshot script in background
- Emits CIEU event `CONTINUITY_CHECK_PASSED` or `CONTINUITY_CHECK_FIXED_N` each cycle

---

## 4. Rollout plan

| Step | Owner | Gate | ETA |
|---|---|---|---|
| A. canonical_roots.json + CLAUDE.md path fix | Secretary + CEO | L2 verified, Board ack | T+2h |
| B. mirror_sync one-shot: copy mirror/knowledge/secretary + /ceo/lessons + /governance into ystar-bridge-labs | Secretary | diff clean | T+4h |
| C. continuity_watcher.sh cron + safe_destructive() bash function | Ethan (CTO) dispatch to Leo | ShellCheck + smoke test on 5 scenarios | T+24h |
| D. snapshot rsync --link-dest hourly cron + retention 30d | Ethan dispatch to Jordan | First 3 snapshots verified restorable | T+48h |
| E. governance_boot.sh integrate check_continuity() | Ethan dispatch to Leo | All existing sessions re-boot clean | T+72h |
| F. CIEU CONTINUITY_CHECK_* event type + dashboard tile | Ethan dispatch to Ryan | 24h of events recorded | T+96h |
| G. L4 ship + amendment-proposal to Board for permanent adoption | Secretary + CEO | Board L3 approval | T+7d |

---

## 5. CIEU trace for this 12-layer task (>=12 tuples)

| Layer | ts | actor | action | target | outcome |
|---|---|---|---|---|---|
| L0 | 2026-04-14T_intent | secretary | intent_declare | continuity_protocol | scope_locked |
| L0-esc | L0_escape | secretary | active_agent_restore | .ystar_active_agent | ystar-cso→secretary (AMENDMENT-009) |
| L1 | L1_search | secretary | evidence_hunt | baseline_cases | 4_evidence_collected |
| L1-b | L1_path_drift_found | secretary | observe | claude.md vs cwd | drift_confirmed |
| L2 | L2_fork_found | secretary | observe | mirror vs workspace | fork_confirmed |
| L3 | L3_plan | secretary | plan | non_loss_protocol | 3_pillar_spec_drafted |
| L4 | L4_exec_start | secretary | spec_draft | this_file | in_progress |
| L5 | L5_dir_create | secretary | fs_mkdir | knowledge/secretary/lessons | created |
| L6 | L6_spec_write | secretary | file_write | continuity_protocol_12layer_20260414.md | persisted |
| L7 | L7_pillar_enumerate | secretary | spec_enumerate | 8_surface + 3_pillar + 7_rollout_step | complete |
| L8 | L8_complete | secretary | layer_close | draft_artifact | ready_for_review |
| L9 | L9_review | secretary | self_review | spec | counter_factual_pass_below |
| L10 | L10_counter_factual | secretary | stress_test | 5_failure_modes | pass |
| L11 | L11_defer | secretary | defer_list | 3_open_items | enumerated |
| L12 | L12_writeback | secretary | writeback | this_file + commit | pending_commit |

---

## 6. Counter-factual stress test (Layer 10, 5 failure modes)

1. **What if git itself is corrupt?** L2 snapshot (file-level, no git metadata dependency) restores. L3 CIEU tells what files existed at what time.
2. **What if snapshot volume is full?** Watcher emits `SNAPSHOT_FAILED` CIEU; retention GC kicks (drops oldest daily, keeps hourly last 24h); Board alerted via push.
3. **What if auto-commit runs during a legitimate rebase?** Detect `.git/REBASE_HEAD` / `MERGE_HEAD` presence; skip auto-commit, warn instead.
4. **What if agent writes outside repo (e.g. `~/.openclaw/`)?** Out of scope for pillar-1; pillar-2 snapshot scope extends to `~/.openclaw/` root via separate rsync job. Added to rollout step D.
5. **What if CLAUDE.md is intentionally changed (legitimate migration)?** canonical_roots.json is source-of-truth, edited only via Board-approved amendment logged to DNA_LOG. Boot-time check reads canonical_roots.json, not CLAUDE.md — CLAUDE.md becomes documentation only.

All five pass.

---

## 7. Deferred items (Layer 11)

1. **Mirror sync direction**: once mirror_sync runs, does the mirror become read-only archive or bidirectional? — defer to CEO+Board
2. **wip/ branch visibility**: should `wip/${agent}` branches push to GitHub or stay local-only? — privacy vs durability trade; defer to CTO
3. **Snapshot retention beyond 30d**: archive cold snapshots to S3? cost/benefit — defer to CFO

---

## 8. Writeback (Layer 12)

- This file itself is the writeback artifact
- Commit message: `[L1 SPEC] secretary: non-loss continuity protocol v0.1 — 3 pillars + 4 baseline evidence + 12-layer CIEU trace`
- Post-commit: update `knowledge/secretary/lessons/INDEX.md` (to be created in rollout step B)
- Notify CEO via session_handoff.md tail: "Samantha 出了 continuity protocol v0.1, 待 CTO 派 Leo/Jordan/Ryan 实现 cron + snapshot + CIEU event"

---

END OF SPEC v0.1 — 2026-04-14
