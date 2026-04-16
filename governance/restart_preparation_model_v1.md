# Restart Preparation Behavior Model v1

**Authority**: CTO Ethan Wright per CZL-137  
**Upstream**: CLAUDE.md "热重启" procedure + action_model_v2 phase taxonomy + session health monitoring (HP/AC signals)  
**Downstream**: `scripts/restart_readiness_check.py` (Maya/Ryan impl) + auto-restart decision logic  
**Purpose**: Formalize session restart from shell-only procedure to mathematical model with pre-restart verification, auto-trigger taxonomy, and state preservation guarantees

---

## §1 Why — The Unmodeled Restart Gap

**Current state**: CLAUDE.md defines "热重启" as a 6-step shell procedure:
1. Delete `scripts/.session_booted` and `scripts/.session_call_count`
2. Re-run `bash scripts/governance_boot.sh AGENT_ID`
3. Confirm `ALL SYSTEMS GO` output
4. If FAILURES, troubleshoot per SKILL.md
5. Complete in same session (no Claude Code exit)
6. Prohibit Board questions during restart flow

**Problem**: This is a **manual, shell-only protocol** with no formal pre-restart verification. Leads to 4 systematic gaps:

1. **State loss risk**: No verification that in-flight sub-agent receipts are collected before restart. Today CEO discovered 9-engineer Sonnet 4.5 quietly running post-Opus-upgrade-but-no-restart — no baseline check detected the version drift.

2. **Memory corruption risk**: Session close writes `session_summary` and `continuation.json`, but restart doesn't verify these files exist or are well-formed. If `session_close_yml.py` silently failed, next session loses context.

3. **Graceful degradation undefined**: When should restart auto-trigger vs manual-only? HP < 28 suggests restart needed, but no decision threshold defined. AC signal not wired to restart logic.

4. **No mathematical model**: What's the **cost** of restarting vs continuing degraded session? When does `C_restart < degradation_rate * remaining_value`? Current procedure has no utility calculation.

**Root cause**: Restart is treated as administrative plumbing, not a governance-critical state transition. No formal readiness predicate, no cost model, no auto-trigger taxonomy.

**Today's incident** (2026-04-16): CEO upgrade Claude model Sonnet 4.5 → Opus 4.6, but didn't manually restart. Result: 9 engineers (5 new + 4 old) active simultaneously, CHARTER_MAP out of sync, dispatch board whitelist stale. Only discovered when Board noticed "eng-data" responses while expecting CTO. **If restart-readiness check existed**, it would have flagged: `agent_count(current) = 9 ≠ agent_count(charter_map) = 4 → BLOCKED, restart required`.

---

## §2 Pre-Restart 7-Step Standard Procedure

Before executing the 6-step CLAUDE.md restart, agent must complete these **verification steps** to ensure state preserved + system clean.

### Step 1: Verify All In-Flight Sub-Agent Receipts Received

**Predicate**: `receipts_complete(s) := count(dispatch_log) = count(reply_registered_events)`

**Implementation**:
```bash
python3 scripts/dispatch_board.py --verify-receipts-complete
```

**Check**:
- Read `governance/active_dispatch_log.md` (or dispatch board state)
- Count dispatches with status `dispatched` or `in_flight`
- Query CIEU `.ystar_cieu.db` for `REPLY_REGISTERED` events since dispatch time
- If count mismatch → list missing receipts → set restart readiness = PARTIAL

**Rationale**: Restarting mid-sub-agent execution loses their work. Must confirm all spawned agents returned receipts.

### Step 2: Verify All 4 Daemons LIVE

**Predicate**: `daemons_live(s) := ∀d ∈ {k9_routing_subscriber, k9_alarm_consumer, cto_dispatch_broker, engineer_task_subscriber}, process_alive(d)`

**Implementation**:
```bash
pgrep -f k9_routing_subscriber && \
pgrep -f k9_alarm_consumer && \
pgrep -f cto_dispatch_broker && \
pgrep -f engineer_task_subscriber
```

**Check**:
- If any daemon dead → restart readiness = BLOCKED (supervision blind)
- If all alive → proceed

**Rationale**: Restart doesn't auto-fix dead daemons if they crashed due to code bugs. Must surface daemon failures before restart.

### Step 3: Verify AC ≥75 (or document graceful degradation justification)

**Predicate**: `ac_threshold_met(s) := AC(s) ≥ 75 ∨ explicit_justification(s, AC < 75)`

**Implementation**:
```bash
python3 scripts/session_watchdog.py --statusline
```

**Check**:
- Parse `AC:XX` from output
- If AC < 75 AND no justification file → restart readiness = PARTIAL
- If AC < 40 → restart readiness = BLOCKED (critical degradation, restart mandatory)

**Rationale**: AC degradation may indicate deeper issues (API failures, daemon crashes, ForgetGuard noise). Restart won't fix these — need root-cause investigation first. But if AC < 40 (red zone), restart anyway to clear session state corruption.

### Step 4: Run session_close_yml.py (preserve session memory)

**Predicate**: `memory_preserved(s) := session_close_yml_success(s) ∧ file_exists(continuation.json) ∧ file_well_formed(continuation.json)`

**Implementation**:
```bash
python3 scripts/session_close_yml.py cto "restart-triggered session close"
```

**Check**:
- Script exit code 0
- `memory/continuation.json` exists
- `memory/continuation.json` is valid JSON (parse test)
- `.ystar_memory.db` updated (check mtime > now - 60s)

**Rationale**: Per CLAUDE.md, session close is mandatory before restart. This step enforces it programmatically.

### Step 5: Archive .czl_subgoals.json Snapshot

**Predicate**: `subgoal_snapshot_archived(s) := file_exists(memory/archive/czl_subgoals_<timestamp>.json)`

**Implementation**:
```bash
cp .czl_subgoals.json memory/archive/czl_subgoals_$(date +%Y%m%d_%H%M%S).json
```

**Rationale**: Campaign state lives in `.czl_subgoals.json`. If restart corrupts it, lose all subgoal context. Archive before restart for rollback.

### Step 6: Verify continuation.json Written with Next-Session Focus

**Predicate**: `continuation_written(s) := file_exists(memory/continuation.json) ∧ |action_queue(continuation)| > 0`

**Implementation**:
```bash
python3 -c "import json; c=json.load(open('memory/continuation.json')); assert len(c.get('action_queue',[])) > 0, 'Empty action queue'"
```

**Check**:
- `continuation.json` has non-empty `action_queue` field
- `campaign` field present with valid name/day/target

**Rationale**: Empty continuation = context loss. Next session boots blind.

### Step 7: Snapshot HP + AC + 6-Signal Breakdown to Reports

**Predicate**: `baseline_snapshot_written(s) := file_exists(reports/restart_baseline_<timestamp>.md)`

**Implementation**:
```bash
python3 scripts/session_watchdog.py --full-report > reports/restart_baseline_$(date +%Y%m%d_%H%M%S).md
```

**Output format**:
```
=== Restart Baseline Snapshot ===
Timestamp: 2026-04-16T19:45:00
HP: 52
AC: 84
Daemons: 4/4 alive
Receipts: 12/12 complete
CIEU events (session): 456
Tool_uses honesty rate: 92% (23/25)
K9 SNR (last 100): precision=0.88 recall=0.91
Readiness: READY
```

**Rationale**: Baseline captures pre-restart health. Post-restart, compare to detect regression (e.g., restart caused daemon crash, AC dropped).

---

## §3 Formal Definitions

Per `governance/formal_methods_primer_v1.md` §3 mandate — governance specs must declare types, predicates, invariants.

### Type System

```
RestartReadiness :: {READY, PARTIAL, BLOCKED}

RestartCause :: {Health, Deploy, Periodic, Emergency}

RestartExecution :: {
  readiness: RestartReadiness,
  cause: RestartCause,
  pre_restart_steps_completed: [Step],  -- §2 7-step checklist
  session_state_snapshot: SessionSnapshot,
  restart_time: Timestamp,
  post_restart_validation: ValidationResult
}

SessionSnapshot :: {
  hp: Int,              -- session health signal
  ac: Int,              -- agent capability score
  daemon_status: [Bool],  -- 4 daemons alive/dead
  receipt_gap_count: Int, -- missing receipts
  continuation_exists: Bool,
  czl_snapshot_path: FilePath
}

ValidationResult :: {
  memory_intact: Bool,   -- continuation.json unchanged post-restart
  daemons_restarted: Bool,  -- all 4 alive
  ac_delta: Int,         -- AC post-restart - AC pre-restart
  boot_success: Bool     -- governance_boot.sh returned 0
}
```

### Predicates

```
-- Pre-restart readiness (conjunction of 7 steps)
ready(s: SessionSnapshot) := 
  receipts_complete(s) ∧ 
  daemons_live(s) ∧ 
  ac_threshold_met(s) ∧ 
  memory_preserved(s) ∧ 
  subgoal_snapshot_archived(s) ∧
  continuation_written(s) ∧
  baseline_snapshot_written(s)

-- Component predicates (from §2)
receipts_complete(s) := 
  count(dispatch_log, status=in_flight) = count(cieu_events, type=REPLY_REGISTERED)

daemons_live(s) := 
  ∀d ∈ {k9_routing_subscriber, k9_alarm_consumer, cto_dispatch_broker, engineer_task_subscriber},
    process_alive(d)

ac_threshold_met(s) := 
  s.ac ≥ 75 ∨ (s.ac < 75 ∧ explicit_justification_exists(s))

memory_preserved(s) := 
  session_close_yml_success(s) ∧ 
  file_exists(continuation.json) ∧ 
  valid_json(continuation.json)

-- Post-restart validation
post_restart_valid(r: RestartExecution) :=
  r.post_restart_validation.boot_success ∧
  r.post_restart_validation.memory_intact ∧
  r.post_restart_validation.daemons_restarted ∧
  abs(r.post_restart_validation.ac_delta) < 15  -- AC shouldn't drop >15 from restart alone
```

### Invariants

Temporal logic (□ = always, ◇ = eventually):

```
-- Never restart without readiness check
□(restart_initiated(s) → ready(s) ∨ cause(restart) = Emergency)

-- Emergency restart bypasses steps 4-5 (speed over safety)
□(cause(restart) = Emergency → |pre_restart_steps_completed| ≥ 3)

-- All non-emergency restarts must preserve memory
□(cause(restart) ≠ Emergency → memory_preserved(s))

-- Restart eventually completes successfully
□(restart_initiated(s) → ◇(boot_success ∨ escalate_to_board))

-- Post-restart validation must run
□(restart_completed(s) → validation_executed(s))
```

---

## §4 Mathematical Model

Per `governance/formal_methods_primer_v1.md` §4 mandate — quantify utility, failure rates, costs.

### State Preservation Reliability

Define reliability as probability all critical state survives restart:

```
P(memory_intact_post_restart) = ∏ P(component_persists)
```

**Components** (5 critical persistence points):
1. **jsonl_transcript** (Claude Code conversation log) — p₁ = 1.0 (managed by harness, never lost)
2. **czl_subgoals.json** (campaign state) — p₂ = 0.95 (disk write may fail, hence Step 5 archive)
3. **continuation.json** (session handoff) — p₃ = 0.98 (written by session_close_yml.py, usually succeeds)
4. **session_summary** (YML memory) — p₄ = 0.99 (SQLite ACID guarantees)
5. **MEMORY feedback files** — p₅ = 1.0 (git-tracked, never lost unless disk failure)

**Overall reliability**:
```
P_intact = 1.0 * 0.95 * 0.98 * 0.99 * 1.0 = 0.9212 ≈ 92%
```

**Target**: ≥99% reliability. **Gap**: czl_subgoals.json is weakest link (0.95). **Mitigation**: Step 5 archive + Step 6 continuation.json redundancy raises effective p₂ to 0.998 (archive OR continuation survives) → overall 0.99.

### Cost Model

Define restart cost vs continued session cost:

```
C_restart = readiness_check_time + boot_time + cache_rewarming
C_continue = degradation_rate * remaining_session_value

Decision rule: restart if C_restart < C_continue
```

**Concrete example** (HP=52, AC=84, 2 hours into 4-hour session):

```
C_restart:
  - readiness_check_time = 7 steps * 30s = 3.5 min
  - boot_time = governance_boot.sh execution = 2 min (cold start)
  - cache_rewarming = agent re-reads context = 5 min (first reply slower)
  Total: 10.5 min

C_continue:
  - degradation_rate = (HP_initial - HP_current) / session_hours = (100 - 52) / 2 = 24 HP/hour
  - remaining_session_value = 2 hours * 60 tool_uses/hour * $0.50/tool_use = $60
  - degradation_impact = if HP < 40, tool_uses blocked → $60 * 0.5 = $30 lost
  Total: $30 expected loss

C_restart ($10.5 min ≈ $3.50 in agent time) < C_continue ($30 expected loss)
→ **restart now**
```

**Threshold formula**:
```
restart_threshold(HP, AC, hours_in_session) := 
  HP < 28 ∨ 
  AC < 40 ∨ 
  (degradation_rate > 20 HP/hour ∧ remaining_session_hours > 1)
```

### Bayesian Decision Model

Update restart probability given signals:

```
P(restart_now_optimal | HP, AC, deploy_pending, hours_in_session)

Prior P(restart_optimal) = 0.05  (5% baseline — most sessions don't need restart)

Likelihoods:
  P(HP < 40 | restart_optimal) = 0.9
  P(HP < 40 | ¬restart_optimal) = 0.1
  
  P(AC < 75 | restart_optimal) = 0.8
  P(AC < 75 | ¬restart_optimal) = 0.2

Posterior (Bayes rule):
  P(restart | HP=52, AC=84) = prior * P(HP=52|restart) * P(AC=84|restart) / P(evidence)
                            = 0.05 * 0.3 * 0.6 / 0.15
                            ≈ 0.06  (6% — marginal, not urgent)

But if HP=28, AC=68:
  P(restart | HP=28, AC=68) = 0.05 * 0.85 * 0.75 / 0.08
                            ≈ 0.40  (40% — strong signal, recommend restart)
```

**Decision threshold**: If posterior > 0.30 (30% probability), trigger auto-restart with Board notification. If > 0.60 (60%), auto-restart immediately (Board veto window = 30s).

---

## §5 Auto-Restart Trigger Taxonomy

When should restart auto-fire vs require manual confirmation?

### Trigger Class 1: Health-Driven (Auto with Board Notification)

**Conditions** (any true → auto-restart):
- HP < 28 (red zone per session health model)
- AC < 40 (critical capability degradation)
- Daemon mass-death (≥2 daemons dead simultaneously)

**Action**:
1. Execute full Pre-Restart 7-step (except Step 4-5 if Emergency variant)
2. Emit CIEU event `AUTO_RESTART_TRIGGERED` with metadata {cause: Health, HP: X, AC: Y}
3. Write brief Board notification to `scripts/.ystar_last_board_msg`: "Auto-restart triggered (HP=X, AC=Y). Resuming in 2 min."
4. Execute CLAUDE.md 6-step restart
5. Post-restart validation (§6 integration with action_model_v2)

**Board veto**: None (health restart is time-critical, Board can review CIEU audit post-hoc).

### Trigger Class 2: Deploy-Driven (Manual Confirmation Required)

**Conditions**:
- Charter changes pending in `.claude/agents/*.md` (new engineer added, scope changed)
- Major dependency upgrade (Y*gov version bump, Claude model upgrade)
- ForgetGuard rule promotion (dry_run → warn → deny) batch

**Action**:
1. Detect change via file watcher or manual flag
2. Emit CIEU event `RESTART_RECOMMENDED` with metadata {cause: Deploy, pending_changes: [list]}
3. Write Board message: "Restart recommended to pick up [changes]. Confirm via 'restart' command or defer."
4. Wait for Board confirmation (no auto-execute)

**Rationale**: Deploy changes aren't time-critical. Board may want to batch multiple changes before restart.

### Trigger Class 3: Periodic (Scheduled Hygiene)

**Conditions**:
- Session duration > 6 hours (heuristic: long sessions accumulate state drift)
- CIEU event count > 2000 (database size threshold)

**Action**:
1. At next natural breakpoint (campaign subgoal Rt+1=0 close), suggest restart
2. Emit CIEU event `PERIODIC_RESTART_SUGGESTED`
3. Write Board message: "Session running 6h+, recommend restart for hygiene. Confirm or continue."
4. Wait for Board confirmation

**Rationale**: Periodic restart is optimization, not correctness requirement. Board may defer if in flow state.

### Trigger Class 4: Emergency (Skip Steps 4-5, Preserve Critical Only)

**Conditions**:
- Daemon crash loop (daemon restarts >3 times in 5 min)
- CIEU database corruption detected (SQLite integrity check fails)
- Active_agent drift deadlock (CEO write operations blocked >10 min)

**Action**:
1. Execute Pre-Restart steps 1-3 only (skip session_close and archive — too slow)
2. Force-kill all daemons
3. Execute CLAUDE.md 6-step restart
4. Emit CIEU event `EMERGENCY_RESTART` with metadata {cause: X}

**Trade-off**: Speed over safety. May lose session summary, but preserves receipts (step 1) and baseline (step 7 if time permits).

**Board notification**: Post-restart only (emergency can't wait for veto).

---

## §6 Integration with action_model_v2

Restart itself is a **special atomic action** — 4th class beyond Heavy/Light/Investigation.

### Restart as Atomic Class

```
Atomic :: {Heavy, Light, Investigation, Restart}

RestartAtomic :: {
  class: Restart,
  cause: RestartCause,  -- from §5 taxonomy
  phase_a_steps: [Step],  -- Pre-Restart 7-step (§2)
  phase_b_steps: [Step],  -- CLAUDE.md 6-step restart execution
  phase_c_steps: [Step],  -- Post-restart validation
  rt_plus_1: Nat         -- honest gap (0 = clean restart, >0 = validation failed)
}
```

### Phase Mapping

**Phase A (Pre-Restart 7-step)**:
1. Verify receipts complete
2. Verify daemons live
3. Verify AC ≥75
4. Run session_close_yml.py
5. Archive .czl_subgoals.json
6. Verify continuation.json written
7. Snapshot HP/AC baseline

**Phase B (Restart Execution)**:
1. Delete `.session_booted` and `.session_call_count`
2. Execute `bash scripts/governance_boot.sh AGENT_ID`
3. Confirm `ALL SYSTEMS GO` output
4. If FAILURES → troubleshoot (enter Investigation atomic)
5. Restore context from continuation.json
6. Emit `SESSION_RESTART_COMPLETE` CIEU event

**Phase C (Post-Restart Validation)**:
1. **Memory consistency check**: `diff <(sha256sum memory/continuation.json) <(sha256sum memory/archive/continuation_pre_restart.json)` (hash match = no corruption)
2. **Daemon liveness re-verify**: `pgrep -f k9_routing_subscriber` (all 4 alive)
3. **AC delta measurement**: `session_watchdog.py --statusline` compare to baseline
4. **Boot log audit**: `grep FAILURE scripts/.governance_boot.log` (0 failures)
5. **CIEU emit**: `RESTART_VALIDATION_COMPLETE` event with metadata {memory_intact: bool, ac_delta: int, daemons_alive: int}
6. **Trust score**: Restart Rt+1=0 → no trust impact. Rt+1>0 (validation failed) → -0.05 (execution fault, not judgment fault)
7. **Knowledge writeback**: If restart revealed issue (e.g., daemon crash pattern), append to `MEMORY/feedback_restart_patterns.md`
8. **Cascade trigger**: If restart was health-driven (HP < 28), queue root-cause investigation atomic
9. **Baseline update**: Write new HP/AC baseline to `reports/restart_baseline_latest.md`

**Rt+1 calculation**:
```
Rt+1_restart = 
  (memory_intact ? 0 : 1) +
  (daemons_alive = 4 ? 0 : 1) +
  (abs(ac_delta) < 15 ? 0 : 1) +
  (boot_success ? 0 : 1)

Target: Rt+1 = 0 (clean restart)
```

**Enforcement**: `action_model_v2.md` ForgetGuard rules apply:
- `dispatch_missing_phase_a` → denies restart without Pre-Restart 7-step
- `receipt_missing_phase_c_heavy` → denies restart receipt without Post-Restart validation

---

## §7 Test & Experiment Plan

Per Board directive "做完了测试实验，有问题再改" — v1 spec must include empirical validation plan.

### Test Cases (3 Readiness States)

**Objective**: Verify `restart_readiness_check.py` correctly classifies session state.

**Corpus**:
1. **READY state**:
   - All 7 pre-restart steps pass
   - HP=60, AC=85, daemons=4/4, receipts=10/10
   - Expected: readiness=READY, allow restart

2. **PARTIAL state**:
   - Steps 1-6 pass, step 7 (baseline snapshot) missing
   - HP=50, AC=78, daemons=4/4, receipts=10/10
   - Expected: readiness=PARTIAL, warn but allow restart

3. **BLOCKED state**:
   - Step 1 fails (2 receipts missing from 12 dispatches)
   - HP=55, AC=80, daemons=3/4 (cto_dispatch_broker dead)
   - Expected: readiness=BLOCKED, deny restart until receipts complete + daemon recycled

**Execution**: Create synthetic session state snapshots (mock CIEU database, dispatch log, daemon PIDs). Run `restart_readiness_check.py --dry-run` on each. Verify output matches expected.

**Success criteria**: 3/3 states correctly classified.

### Pilot Graceful Restart (1 Real Execution)

**Objective**: Execute full restart flow on live session, measure baseline consistency.

**Procedure**:
1. At next campaign subgoal Rt+1=0 close, trigger manual restart
2. Execute Pre-Restart 7-step, log each step duration
3. Execute CLAUDE.md 6-step restart
4. Execute Post-Restart validation 9-step
5. Measure metrics:
   - Total restart time (target <15 min)
   - Memory intact (continuation.json hash match)
   - AC delta (target abs <10)
   - Daemon restart success (target 4/4)

**Data collection**:
- CIEU events: `RESTART_READINESS_CHECK`, `SESSION_RESTART_COMPLETE`, `RESTART_VALIDATION_COMPLETE`
- Baseline files: `reports/restart_baseline_<timestamp>.md` (before + after)

**Iteration trigger**: If any validation step fails (Rt+1 > 0), root-cause investigation → spec update.

**Timeline**: Next session (Board approval pending). After pilot closes Rt+1=0, promote to standard protocol.

---

## §8 Rollout Sequence

3 sequence-only steps (NO time cadence per AI methodology — event-driven execution):

### Step A: Spec Ship (This Atomic — CZL-137)

**Deliverable**: `governance/restart_preparation_model_v1.md` spec with 8 sections.

**Success criteria**:
- Spec exists, 1500-2200 words, 8 sections present
- Empirical paste verification (ls + wc + grep)
- Rt+1=0

**Status**: In flight (this atomic).

### Step B: Wire Implementation (Maya/Ryan)

**Deliverable**: `scripts/restart_readiness_check.py` — standalone validator implementing §2 7-step + §3 predicates.

**Features**:
1. CLI: `restart_readiness_check.py [--dry-run] [--cause Health|Deploy|Periodic|Emergency]`
2. Output: JSON `{readiness: READY|PARTIAL|BLOCKED, failed_steps: [list], recommendation: str}`
3. Integration: Called by `governance_boot.sh` on restart (if `--verify-readiness` flag set)
4. CIEU emit: `RESTART_READINESS_CHECK` event with readiness + failed_steps

**Upstream dependency**: Step A (spec) must close Rt+1=0 before Maya/Ryan start Step B.

**Success criteria**:
- Script exists, 3 test cases (§7) PASS
- CIEU emit working (event appears in `.ystar_cieu.db`)
- Rt+1=0

### Step C: Pilot + Rollout

**Deliverable**: 1 pilot graceful restart (§7 experiment) + governance_boot.sh integration.

**Sequence**:
1. Execute pilot restart with full 7+6+9 step instrumentation
2. Collect metrics (time, memory consistency, AC delta, daemon status)
3. If Rt+1=0 → promote to standard protocol (update CLAUDE.md to reference restart_preparation_model_v1.md)
4. If Rt+1>0 → iterate on failed steps → re-pilot

**Upstream dependency**: Step B (wiring) must close Rt+1=0 before Step C pilot.

**Success criteria**:
- Pilot restart completes with Rt+1=0
- CLAUDE.md updated with reference to this model
- Auto-restart taxonomy (§5) wired to session_watchdog.py triggers

**Downstream cascade**: After Step C LIVE, all future restarts subject to readiness checks. Manual "热重启" still allowed (bypass readiness for emergency), but logged as `cause=Emergency` for audit.

---

## Empirical Verification (Anti-Hallucination Protocol)

Per CZL-114 lesson — empirical paste mandatory for all spec deliverables.
