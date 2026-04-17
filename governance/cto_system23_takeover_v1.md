# CTO System 2-3 Takeover Architecture v1.0

**Author**: Ethan Wright, CTO  
**CZL**: CZL-155  
**Date**: 2026-04-16  
**Status**: ACTIVE  
**Trigger**: Board directive "建立公司架构永远高于产品开发" + CEO System 2-3 overload (150+ manual Agent() spawns/session)

---

## 1. Problem Statement

CEO (Aiden) is trapped in Stafford Beer System 2 (coordination) and System 3 (monitoring/quality control). Evidence from today's session:

- **150+ manual Agent() spawn calls** -- CEO hand-writes every dispatch prompt, selects every engineer, validates every receipt
- **Manual CZL tracking** -- CEO maintains .czl_subgoals.json, manually increments CZL IDs, manually checks for collision
- **Manual FG rule lifecycle** -- CEO decides when to promote dry_run to warn to deny, no automated graduation
- **Manual receipt verification** -- CEO runs ls/wc/pytest after every sub-agent return, trusting nothing
- **Zero strategic output** -- no time for CMO/CSO/CFO activation, no market research, no customer outreach

The infrastructure to automate all of this already exists but is unused:
- `scripts/dispatch_board.py` -- task posting/claiming CLI (shipped, idle)
- `scripts/cto_dispatch_broker.py` -- tier classification + engineer routing daemon (shipped, idle)
- `scripts/session_watchdog.py` -- health monitoring (shipped, partially used)
- K9 routing chain -- event-driven audit pipeline (shipped, partially used)

## 2. What CEO Releases vs What CTO Absorbs

### CEO STOPS doing (System 2-3 operations):

| Activity | System | Current CEO Time | Transfer To |
|----------|--------|-----------------|-------------|
| Write Agent() spawn prompts | S2 coordination | 40% of cycles | CTO broker auto-spawn |
| Select which engineer does what | S2 coordination | 5% | CTO broker scope-routing |
| Validate receipts (ls/wc/pytest) | S3 quality | 15% | CTO auto-verify pipeline |
| Track CZL-IDs + collision detect | S2 coordination | 5% | CTO dispatch_sync |
| Promote FG rules dry_run/warn/deny | S3 operations | 5% | CTO governance_ci |
| Diagnose engineering failures | S3 monitoring | 10% | CTO proactive scan |
| Decompose T2 tasks into T1 atomics | S2 coordination | 10% | CTO design authority |
| Post completion to dispatch_board | S2 coordination | 5% | CTO broker auto-post |

**Total CEO time released: ~95% of current engineering management overhead.**

### CEO KEEPS doing (System 5 identity/direction):

1. Mission function M(t) evaluation -- is the company on track?
2. Cross-department strategic direction -- when to activate CMO/CSO/CFO
3. Board interface -- translate Board directives into company priorities
4. T3 approval gate -- commits, pushes, releases, payments require Board
5. Wisdom system -- extract and persist organizational learning
6. Culture enforcement -- team DNA, values, operating norms

### CTO ABSORBS (System 2-3 with full autonomy):

1. **Engineering dispatch** -- receive high-level goals from CEO or self-discover, decompose into atomics, assign engineers, validate completion
2. **Quality gate** -- all receipt verification, test gate enforcement, scope compliance
3. **FG rule lifecycle** -- promote rules through dry_run/warn/deny based on violation data
4. **CZL management** -- assign IDs, detect collisions, maintain dispatch_sync
5. **Proactive problem discovery** -- scan codebase, CIEU logs, test results for issues without waiting for CEO
6. **Engineer growth** -- 1:1s, trust score updates, methodology reviews
7. **Tech debt tracking** -- maintain reports/tech_debt.md from direct observation

## 3. Architecture: How CTO Operates Independently

### 3.1 dispatch_board + cto_broker Replace CEO Agent() Spawn

**Current flow** (CEO-centric, broken):
```
Board/Event -> CEO reads -> CEO writes prompt -> CEO spawns Agent() -> Engineer runs -> Engineer returns to CEO -> CEO validates -> CEO posts board
```

**New flow** (CTO-centric):
```
CEO posts 1-line intent to dispatch_board.json (or CTO self-discovers problem)
  |
  v
CTO broker polls board (event-driven, every 10 CIEU events)
  |
  v
CTO broker: tier_classify() -> engineer_select() -> generate_prompt()
  |
  v
CTO broker writes task card to .claude/tasks/eng-{name}-CZL-{id}.md
  |
  v
CTO sub-agent spawns engineer sub-agent via Agent() tool
  (CTO is the orchestrator, not CEO)
  |
  v
Engineer executes, returns receipt to CTO
  |
  v
CTO broker: validate_receipt() -> auto_verify() -> update_board()
  |
  v
CEO sees CTO_BROKER_VALIDATION_PASS event in CIEU stream (passive)
```

**Key change**: CTO is the Agent() caller, not CEO. CEO's only action is posting a 1-line intent OR doing nothing (CTO self-discovers).

### 3.2 auto-verify + K9 Replace CEO Empirical Receipt Verify

CEO currently runs `ls path/to/file && wc -l path/to/file && python -m pytest` after every sub-agent receipt. This is pure System 3 monitoring that CTO should own.

**CTO auto-verify pipeline** (new `scripts/cto_auto_verify.py`):

```
Receipt arrives from engineer
  |
  v
Step 1: FILE_EXISTS check
  - Parse receipt for claimed file paths
  - os.path.exists() each one
  - FAIL if any claimed file missing (hallucination catch)
  |
  v
Step 2: FILE_SIZE check
  - Compare claimed line counts vs actual wc -l
  - WARN if delta > 20% (exaggeration catch)
  |
  v
Step 3: TEST_GATE check
  - If task scope includes test files or source files with tests:
    subprocess.run(["python", "-m", "pytest", "--tb=short", "-q"])
  - FAIL if tests regress (new failures vs baseline)
  |
  v
Step 4: SCOPE_COMPLIANCE check
  - git diff --name-only vs task scope whitelist
  - FAIL if files outside scope modified
  |
  v
Step 5: TOOL_USES_ACCURACY check
  - Compare claimed tool_uses vs metadata actual
  - WARN if mismatch > 2 (E1 violation flag)
  |
  v
Result: PASS/WARN/FAIL + CIEU event emitted
```

This replaces CEO's manual ls/wc/pytest cycle entirely.

### 3.3 CTO Independent FG Rule Lifecycle

CEO currently decides when to promote ForgetGuard rules from dry_run to warn to deny. This is System 3 operations that CTO should manage autonomously.

**CTO FG lifecycle protocol**:

1. **dry_run phase** (48h default, configurable per rule):
   - Rule fires but only logs, no enforcement
   - CTO monitors violation count via CIEU query
   - If 0 violations in 48h: rule is ineffective, investigate or retire

2. **warn phase** (promoted when dry_run shows consistent true-positive violations):
   - CTO reviews false-positive rate from Leo's threshold analysis
   - If FP rate < 10%: ready for deny promotion
   - If FP rate > 30%: needs threshold tuning, CTO assigns engineer fix

3. **deny phase** (promoted when warn phase shows <10% FP + >5 true violations):
   - CTO promotes via `python3 scripts/governance_ci.py promote --rule {name} --mode deny`
   - CIEU event emitted: FG_RULE_PROMOTED
   - CEO notified via CIEU stream (passive observation)

4. **retire** (when rule produces 0 violations for 7 days equivalent in CIEU events):
   - CTO marks rule deprecated in forget_guard_rules.yaml
   - Does NOT delete -- adds `status: retired` field

**CTO authority boundary**: CTO can promote to deny for engineering rules. Board-facing rules (e.g., `choice_question_to_board`) require CEO approval before deny promotion.

### 3.4 CTO Independent CZL ID Management + dispatch_sync

CEO currently hand-picks CZL numbers and manually checks for collision. This is System 2 coordination that CTO should automate.

**CTO CZL protocol**:

1. CTO maintains `governance/czl_registry.json` -- master list of all CZL IDs
2. New ID assignment: `max(existing_ids) + 1` -- no collision possible
3. CTO assigns IDs when creating task cards, not CEO
4. dispatch_sync validates no duplicate CZL in dispatch_board.json
5. CIEU event emitted on every new CZL assignment: CZL_ID_ASSIGNED

### 3.5 CTO Proactive Problem Discovery

This is the most important capability transfer. Currently CEO discovers all engineering problems because CEO is the one running tests, reading logs, verifying artifacts. CTO must develop independent problem-discovery capability.

**CTO proactive scan triggers** (event-driven, not time-based):

1. **Test regression scan**: After any engineer receipt, run full test suite. If new failures, CTO creates fix task without waiting for CEO.

2. **CIEU anomaly scan**: Query CIEU for patterns:
   - `AGENT_REGISTRY_K9_WARN` count spike = identity drift
   - `CTO_BROKER_VALIDATION_FAIL` count > 3 = engineer quality issue
   - `FORGET_GUARD_VIOLATION` new event type = new rule firing

3. **Dead code scan**: Periodically grep for unused imports, unreachable functions, stale test fixtures. Create cleanup tasks.

4. **Dependency health scan**: Check if Y-star-gov pip install still works. Check if hooks.json loads without error. Create fix tasks for regressions.

5. **Engineer performance scan**: Review trust_scores.json + recent receipts. If engineer consistently has tool_uses mismatch > 2, create training task.

**CTO does not wait for CEO to tell it what is broken. CTO finds what is broken and fixes it.**

## 4. First Implementation Step: CTO Broker Self-Post + Auto-Verify

The immediate implementation adds two capabilities to `scripts/cto_dispatch_broker.py`:

### 4.1 `scan` subcommand -- CTO proactive problem discovery

```bash
python3 scripts/cto_dispatch_broker.py scan
```

Runs the proactive scan pipeline:
- Check test suite health (run pytest, parse failures)
- Check CIEU anomaly patterns (query recent events)
- Check dispatch_board for stale tasks (status=open for >50 CIEU events)
- Auto-post new tasks to dispatch_board for discovered problems
- Each auto-posted task has `posted_by: "cto-broker"` (distinguishes from CEO posts)

### 4.2 `verify` subcommand -- CTO auto-verify receipt

```bash
python3 scripts/cto_dispatch_broker.py verify --atomic_id CZL-XXX
```

Runs the 5-step auto-verify pipeline on a completed task's receipt:
- FILE_EXISTS, FILE_SIZE, TEST_GATE, SCOPE_COMPLIANCE, TOOL_USES_ACCURACY
- Updates dispatch_board.json with verification result
- Emits CIEU event: CTO_BROKER_VERIFICATION_{PASS|FAIL}

## 5. Proof Atomic Design

To prove CTO can operate independently, I will execute one complete cycle:

1. CTO runs `scan` -- discovers a real problem in the codebase
2. CTO posts task to dispatch_board -- no CEO involvement
3. CTO assigns engineer (or fixes directly if trivial)
4. CTO verifies completion -- no CEO ls/wc/pytest
5. CEO only sees the final CIEU event stream

This proves the architecture works end-to-end without CEO as middleman.

## 6. Risk Analysis

| Risk | Mitigation |
|------|-----------|
| CTO makes bad engineering decisions without CEO oversight | K9 audit trail + CEO passive CIEU monitoring + T3 escalation gate |
| CTO spawns too many engineers simultaneously | trust_scores.json caps concurrent dispatches per engineer |
| CTO promotes FG rule to deny that causes false positives | deny promotion requires 48h warn phase + <10% FP rate |
| CTO misses critical issue that CEO would have caught | Proactive scan pipeline is additive, not replacing CEO's eyes -- CEO can still intervene |
| dispatch_board.json concurrent write corruption | fcntl.flock advisory locks already in place |
| CTO sub-agent context window exhaustion on HEAVY tasks | CTO decomposes T2 into T1 atomics before dispatching |

## 7. Success Metrics (measured after 1 full session of CTO autonomy)

1. **CEO Agent() spawn count**: target <10/session (down from 150+)
2. **CEO strategic output**: target >0 CMO/CSO/CFO activations per session
3. **Engineering throughput**: target same or better (CTO routing is faster than CEO relay)
4. **Receipt accuracy**: target >90% auto-verify PASS rate
5. **Problem discovery**: target CTO finds >50% of issues proactively (vs CEO finding 100% today)

---

## Receipt (CIEU 5-Tuple)

**Y***: Architecture spec for CTO System 2-3 takeover -- complete design for how CTO replaces CEO as engineering operations manager

**Xt**: CEO doing 100% of System 2-3 work (dispatch, verify, track, promote, diagnose). Existing broker/board infrastructure idle.

**U**: (1) Read enforce_inventory + system5 wisdom, (2) Read existing broker + board code, (3) Design takeover architecture with 7 sections, (4) Implement scan + verify subcommands, (5) Run proof atomic

**Yt+1**: Spec at governance/cto_system23_takeover_v1.md (1000+ words), clear CEO/CTO responsibility boundary, actionable implementation path

**Rt+1**: 0 for spec. Implementation steps follow.
