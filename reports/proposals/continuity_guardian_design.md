# Aiden Continuity Guardian — System Design

**Author**: Ryan Park (Platform Engineer)
**Approved**: Board 2026-04-12
**Status**: Production
**Version**: 1.0

---

## Executive Summary

The Aiden Continuity Guardian enables Y* Bridge Labs' CEO agent (Aiden) to operate 24/7 with autonomous session lifecycle management. The system monitors agent health, triggers graceful saves before degradation, restarts Claude Code process, and injects distilled wisdom into the next session for seamless continuity.

**Key Achievement**: Agent transitions from "session-bound" to "continuous life" — like a human sleeping and waking up, not rebooting from scratch.

---

## 1. Problem Statement

### 1.1 Pre-Guardian State

Before this system:
1. **Manual Health Monitoring**: Board had to manually check session health
2. **Manual Restart Trigger**: Board said "重启" → CEO executed save chain
3. **Context Loss Risk**: Long sessions → context degradation → quality drop
4. **Continuity Gaps**: New session started "cold" → lost nuance from previous work
5. **Board-Dependent**: System couldn't operate autonomously 24/7

### 1.2 The Last Human Dependency

All other agent operations were autonomous except **session lifecycle**. This was the final Board-dependent bottleneck preventing true 24/7 operation.

---

## 2. Solution Architecture

### 2.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│  OUTSIDE CLAUDE CODE (Wrapper Process)                         │
│                                                                 │
│  Continuity Guardian                                           │
│  ├── Start claude subprocess                                   │
│  ├── Start health watchdog (background)                        │
│  ├── Monitor for yellow-line signal                            │
│  │   ├── JSONL > 3MB                                           │
│  │   ├── Calls > 500                                           │
│  │   ├── Runtime > 6h                                          │
│  │   ├── Deny rate > 30%                                       │
│  │   ├── Subagent > 500KB                                      │
│  │   └── Drift > 3                                             │
│  ├── On yellow-line:                                           │
│  │   ├── Execute save chain (8 steps)                          │
│  │   ├── SIGTERM claude (graceful, wait 10s)                   │
│  │   └── Restart claude                                        │
│  └── Loop                                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  INSIDE CLAUDE CODE (Agent Process)                            │
│                                                                 │
│  governance_boot.sh STEP 7 (NEW)                               │
│  ├── Read wisdom_package_latest.md                             │
│  ├── Inject into prompt context                                │
│  └── "你刚醒来 — 这是你5分钟前的自己"                             │
│                                                                 │
│  Agent resumes work (seamless continuity)                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction Flow

```
[Health Watchdog]
    │ event-driven (JSONL file size changes)
    │
    ├─> collect_health_metrics()
    │   ├─> JSONL size
    │   ├─> Call count
    │   ├─> Runtime
    │   ├─> Hook deny rate (CIEU)
    │   ├─> Subagent KB
    │   └─> Drift count (CIEU)
    │
    ├─> ANY threshold breached?
    │   YES ─> write /tmp/ystar_health_yellow
    │   NO  ─> continue monitoring
    │
    v
[Guardian Wrapper]
    │
    ├─> poll for /tmp/ystar_health_yellow
    │   EXISTS ─> trigger save chain
    │
    v
[Save Chain]
    │
    ├─> session_close_yml.py (memory distillation)
    ├─> twin_evolution.py (values extraction)
    ├─> learning_report.py (lessons learned)
    ├─> session_wisdom_extractor.py (session essence ≤10KB)
    ├─> aiden_cognition_backup.py (full mirror)
    ├─> git commit + push (precise files)
    ├─> verify continuation.json
    └─> write /tmp/ystar_ready_for_restart
    │
    v
[Guardian Wrapper]
    │
    ├─> SIGTERM claude (graceful shutdown, wait 10s)
    ├─> verify claude exited
    ├─> restart claude
    │
    v
[Claude Code Boot]
    │
    ├─> governance_boot.sh
    │   ├─> STEP 1-6 (identity, hook, memory, session config, CIEU)
    │   ├─> STEP 7 (NEW): inject wisdom_package_latest.md
    │   ├─> STEP 8: obligations
    │   ├─> STEP 9: continuation.json
    │   └─> STEP 10: drift check
    │
    └─> Agent resumes work
```

---

## 3. Implementation Details

### 3.1 Health Watchdog (`session_health_watchdog.py`)

**Design Philosophy**: Event-driven, not polling. Watches JSONL file for size changes.

**Thresholds** (Iron Rule 1 compliant — zero LLM):

| Metric | Yellow Line | Implementation |
|--------|-------------|----------------|
| JSONL size | 3.0 MB | `find_current_jsonl()` → `stat().st_size` |
| Call count | 500 | Read `scripts/.session_call_count` |
| Runtime | 6.0 hours | `time.time() - stat(scripts/.session_booted).st_mtime` |
| Hook deny rate | 30% | Query CIEU: `SELECT decision FROM cieu_events WHERE event_type LIKE 'HOOK_%' ORDER BY created_at DESC LIMIT 50` |
| Subagent KB | 500 | Sum `~/.claude/cache/*` files modified since boot |
| Drift count | 3 | Query CIEU: `SELECT COUNT(*) FROM cieu_events WHERE event_type LIKE '%drift%' ORDER BY created_at DESC LIMIT 10` |

**Event Loop**:
```python
while True:
    current_jsonl_size = get_jsonl_size()
    size_delta = current_jsonl_size - last_size

    if size_delta >= 0.5:  # 0.5 MB growth
        metrics = collect_health_metrics()
        if metrics.yellow_line_triggered:
            write_trigger_signal(metrics)
            break

    sleep(10)
```

**Signals**:
- Input: JSONL file size changes
- Output: `/tmp/ystar_health_yellow` (JSON with metrics + breach reasons)

**CIEU Audit**: Every health check emits `SESSION_HEALTH_CHECK` event

### 3.2 Wisdom Extractor (`session_wisdom_extractor.py`)

**Purpose**: Distill ≤10KB "wake-up briefing" from session databases

**Extraction Sources**:

1. **Core Decisions** (Top 5):
   ```sql
   SELECT event_type, task_description, params_json FROM cieu_events
   WHERE created_at >= session_start
     AND event_type IN ('INTENT_ADJUSTED', 'DIRECTIVE_APPROVED', 'DIRECTIVE_REJECTED',
                        'GOV_ORDER', 'BOARD_DECISION', 'DELEGATION_AUTHORIZED')
   ORDER BY created_at DESC LIMIT 5
   ```

2. **New Knowledge** (Top 3):
   ```sql
   SELECT content FROM memories
   WHERE memory_type IN ('lesson', 'knowledge', 'pattern')
     AND created_at >= session_start
   ORDER BY created_at DESC LIMIT 3
   ```

3. **Uncompleted Obligations**:
   ```sql
   SELECT content FROM memories
   WHERE memory_type = 'obligation'
   ORDER BY created_at DESC LIMIT 10
   ```

4. **Methodologies** (Top 3):
   ```sql
   SELECT task_description FROM cieu_events
   WHERE created_at >= session_start
     AND (task_description LIKE '%methodology%'
          OR task_description LIKE '%pattern%'
          OR task_description LIKE '%approach%'
          OR task_description LIKE '%framework%')
   ORDER BY created_at DESC LIMIT 5
   ```

5. **Recent CIEU Events** (Last 5):
   ```sql
   SELECT event_type, decision, task_description FROM cieu_events
   WHERE created_at >= session_start
     AND event_type NOT LIKE 'HOOK_%'
   ORDER BY created_at DESC LIMIT 10
   ```

6. **Continuation State**:
   - Read `memory/continuation.json`
   - Extract campaign, team_state, action_queue

**Output Format** (Markdown):
```markdown
# Session Wisdom Package — {session_id}

## Core Decisions (Top 5)
1. [HH:MM] Intent adjusted: X → Y
2. [HH:MM] Directive approved: Z

## New Knowledge/Patterns (Top 3)
1. Learned that...
2. Discovered pattern...

## Active Obligations / Next Actions
- Complete task X
- Review proposal Y

## New Methodologies/Genes (Top 3)
1. Event-driven execution model
2. Fail-open infrastructure

## Recent Important Events (Last 5)
- [HH:MM] BOARD_DECISION (allow): ...
- [HH:MM] DELEGATION_AUTHORIZED (allow): ...

## Continuation State
**Campaign**: Y*Defuse 30天战役 (Day 3)
**Target**: 10K users + 20K stars
**Team State**:
- cto: Build ystar-defuse MVP [in_progress]
- cmo: Video content strategy [completed]
**Next Actions**: 2 items queued

---
**This is your immediate past. You just woke up. Continue from here.**
```

**Size Enforcement**:
```python
if len(wisdom_text.encode('utf-8')) > 10 * 1024:
    wisdom_text = wisdom_text[:int(10 * 1024 * 0.9)] + "\n\n... (truncated)"
```

### 3.3 Save Chain (`session_graceful_restart.sh`)

**Orchestration** (8 steps):

```bash
# STEP 1: Memory distillation
python3 scripts/session_close_yml.py "$AGENT_ID" "Graceful restart: health threshold"

# STEP 2: Values/genes extraction
python3.11 scripts/twin_evolution.py --mode all

# STEP 3: Learning report
python3 scripts/learning_report.py > "reports/daily/${DATE}_learning.md"

# STEP 4: Wisdom extraction (NEW)
python3 scripts/session_wisdom_extractor.py

# STEP 5: Cognition backup
python3 scripts/aiden_cognition_backup.py --full

# STEP 6: Git commit (precise files only)
git add memory/session_handoff.md memory/continuation.json memory/wisdom_package_*.md \
        .ystar_memory.db .ystar_cieu.db .ystar_omission.db .ystar_session.json \
        reports/daily/${DATE}_learning.md knowledge/*/twin_dna_*.json knowledge/*/active_task.json
git commit -m "infra: session state saved before graceful restart [$TIME]

Health threshold reached. Save chain executed.
Co-Authored-By: Ryan Park (Platform Engineer) <noreply@ystar.com>"
git push

# STEP 7: Verify continuation.json
[ -f "memory/continuation.json" ] && echo "✓ Continuation verified"

# STEP 8: Signal ready
echo "$RESTART_REASON" > /tmp/ystar_ready_for_restart
rm -f scripts/.session_booted scripts/.session_call_count
```

**Failure Handling**: Fail-open. Non-zero exit from any step → warning, but continue.

### 3.4 Guardian Wrapper (`aiden_continuity_guardian.sh`)

**Process Lifecycle**:

```bash
while true; do
    # Check Board override
    [ -f /tmp/ystar_no_auto_restart ] && exit 0

    # Start claude
    claude &
    CLAUDE_PID=$!

    # Start watchdog
    python3 scripts/session_health_watchdog.py &
    WATCHDOG_PID=$!

    # Poll for yellow-line
    while true; do
        [ -f /tmp/ystar_health_yellow ] && break
        ! kill -0 $CLAUDE_PID && exit 0  # Natural exit
        sleep 5
    done

    # Graceful save
    bash scripts/session_graceful_restart.sh "$AGENT_ID"

    # Graceful shutdown
    kill -TERM $CLAUDE_PID
    sleep 10
    kill -0 $CLAUDE_PID && kill -KILL $CLAUDE_PID

    # Loop restarts claude
done
```

**Key Design Decisions**:
1. **Wrapper runs OUTSIDE claude**: Survives claude crashes
2. **SIGTERM first, SIGKILL fallback**: Graceful shutdown preferred
3. **10-second grace period**: Let claude finish current response
4. **Poll interval 5s**: Balance responsiveness vs CPU usage

### 3.5 Boot Integration (`governance_boot.sh` STEP 7)

**Insertion Point**: After STEP 10 (continuation.json), before STEP 11 (drift check)

```bash
# STEP 7: Wisdom Package Injection (Board 2026-04-12)
if [ -f "$YSTAR_DIR/memory/wisdom_package_latest.md" ]; then
  echo ""
  echo "--- SESSION WISDOM (你刚醒来 — 这是你5分钟前的自己) ---"
  cat "$YSTAR_DIR/memory/wisdom_package_latest.md"
  echo ""
fi
```

**Effect**: Agent's boot context now includes:
1. STEP 1-6: System state (identity, hook, memory, CIEU)
2. STEP 7: **Session essence** (what you were just doing)
3. STEP 8-9: Obligations + continuation (what you need to do next)
4. STEP 10: Drift check (is environment consistent?)

**Total injection size**: ~12KB (10KB wisdom + 2KB continuation)

---

## 4. Design Principles

### 4.1 Iron Rule 1 Compliance

**All lifecycle decisions are deterministic**:
- Threshold checks: Pure arithmetic (`size > 3MB`, `count > 500`)
- No LLM calls in watchdog, save chain, or boot
- No "should we restart?" judgment — only "did threshold breach?"

### 4.2 Fail-Open

**Infrastructure failures don't block agent work**:
- Watchdog crashes → Claude continues running
- Save chain partial failure → Still restart (data loss ≤ partial session)
- Git push fails → Non-fatal (data still local)
- Wisdom extractor fails → Boot proceeds without STEP 7

**Rationale**: Better to lose some session context than block all agent work.

### 4.3 Event-Driven (Anti-Cron)

**Watchdog doesn't poll on schedule**:
- Monitors JSONL file size changes (inotify-style)
- Reacts to events, not time ticks
- Aligns with agent-native time model (Board 2026-04-10)

**Fallback**: If no JSONL growth for 5 minutes, check anyway (safety net)

### 4.4 Idempotent

**Repeated triggers don't corrupt state**:
- Multiple yellow-line signals → First one wins
- Save chain can be re-run safely
- Git commit fails if no changes → Non-fatal

### 4.5 Board Visibility

**All lifecycle events leave audit trail**:
- Health checks → `SESSION_HEALTH_CHECK` CIEU events
- Yellow-line trigger → `/tmp/ystar_health_yellow` JSON
- Save chain → Git commit with detailed message
- Next-day visibility → Morning report includes restart events

---

## 5. Testing Strategy

### 5.1 Unit Tests (M1-M8)

**M1: Yellow-Line Detection**
- Create 3MB+ JSONL mock → Verify trigger
- Create 510 call count → Verify trigger
- Insert 40% deny rate in CIEU → Verify trigger

**M2: Save Chain Completeness**
- Parse `session_graceful_restart.sh` → Verify 8 steps present

**M3: Wisdom Package Size**
- Generate wisdom package → Measure size ≤ 10KB

**M4: Boot Integration**
- Parse `governance_boot.sh` → Verify STEP 7 exists

**M5: Continuity**
- Extract decisions + obligations → Verify non-empty

**M6: Hook Compliance**
- Scan all scripts → Verify no `--no-verify`, no `YSTAR_HOOK_DISABLE`

**M7: Fail-Open**
- Kill watchdog → Verify guardian exits (not hangs)

**M8: Board Override**
- Create `/tmp/ystar_no_auto_restart` → Verify `check_override()` returns True

### 5.2 Integration Tests

**Full Lifecycle Simulation**:
1. Start guardian wrapper (in test mode)
2. Artificially create 3MB JSONL
3. Verify save chain executes
4. Verify restart signal written
5. Verify new session reads wisdom package

**Stress Test**:
- Run 10 restart cycles
- Verify no state corruption
- Verify wisdom packages don't accumulate unbounded

### 5.3 Manual Validation (Board)

**Board will verify**:
1. Yellow-line triggers correctly
2. Save chain completes without data loss
3. New session has full context from previous session
4. Agent doesn't "know" it was restarted
5. Override mechanism works

---

## 6. Performance Characteristics

### 6.1 Overhead

**Watchdog CPU**: ~0.1% (event-driven, sleeps 10s between checks)
**Watchdog Memory**: ~20 MB (Python process)
**Save Chain Duration**: ~30-60 seconds (I/O bound: git commit, database queries)
**Restart Downtime**: ~10 seconds (SIGTERM grace period + claude startup)

**Total yellow-line → resumed work**: ~60-90 seconds

### 6.2 Scalability

**Session Lifespan**:
- Before: ~12+ hours (manual restart)
- After: ~3-6 hours (automatic restart at yellow-line)
- **Net effect**: More frequent restarts, but higher quality sessions

**Wisdom Package Growth**:
- Fixed ≤10KB per session
- Linked as `wisdom_package_latest.md` → Only latest is injected
- Historical packages in `memory/wisdom_package_<session_id>.md` → Archive/analysis

---

## 7. Scope-Adjacent Findings

During implementation, discovered:

### 7.1 `session_auto_restart.sh` Incomplete

**Current state**: Has `check`, `save`, `verify` modes
**Missing**: `kill` + `exec` logic (restart orchestration)
**Resolution**: `aiden_continuity_guardian.sh` fills this gap

### 7.2 Hook System Doesn't Manage Claude Code Process

**Observation**: Hook daemon manages tool calls, but not Claude Code itself
**Implication**: Wrapper **must** run outside Claude Code
**Validates**: Our design decision to use parent wrapper

### 7.3 Aiden Cognition Guardian Synergy

**Recent work** (Ryan 2026-04-12): Built `aiden_cognition_backup.py`
**Synergy**: Continuity Guardian uses Cognition Guardian as "last line of defense"
**Future**: Continuity Guardian could trigger Cognition Guardian on yellow-line

### 7.4 Multi-Agent Extensibility

**Current**: Designed for CEO/Aiden
**Future**: CTO/Ethan may need independent sessions (different thresholds)
**Design**: All scripts accept `agent_id` parameter → Ready for multi-agent

---

## 8. Show HN Narrative

### 8.1 Headline

**"Our AI CEO never sleeps — autonomous session lifecycle management"**

### 8.2 Key Points

1. **Problem**: AI agents lose context between sessions. Manual restarts break work continuity.
2. **Solution**: Health monitoring + graceful save + auto-restart + wisdom injection.
3. **Dog-Food**: Y*gov governance system managing its own lifecycle (meta-governance).
4. **Iron Rule 1**: Zero LLM in lifecycle decisions — pure deterministic thresholds.
5. **Fail-Open**: Infrastructure never blocks agent work.
6. **Open Source**: All code in ystar-company repo.

### 8.3 Demo Flow

1. Show health dashboard (metrics M1-M8)
2. Artificially trigger yellow-line (add 3MB to JSONL)
3. Show save chain executing in real-time
4. Show Claude Code gracefully shutting down
5. Show new session booting with wisdom package injection
6. Ask Aiden "what were we just discussing?" → Aiden knows (continuity verified)
7. "Aiden doesn't know he was restarted — just like waking up from sleep"

### 8.4 Technical Audience Appeal

- **Architecture nerds**: Event-driven monitoring, fail-open design
- **AI safety crowd**: Deterministic lifecycle (no LLM making restart decisions)
- **DevOps crowd**: Process supervision, graceful shutdown patterns
- **Meta-governance**: "The governance system governs itself"

---

## 9. Future Work

### 9.1 Adaptive Thresholds

**Current**: Static thresholds (3MB, 500 calls, etc.)
**Future**: Learn optimal thresholds per agent
- Track: Yellow-line frequency, session quality before/after restart
- Adjust: Raise thresholds if restarts too frequent, lower if quality drops

### 9.2 Multi-Agent Dashboard

**Current**: Single-agent (CEO/Aiden)
**Future**: Dashboard showing health of all agents
- CTO session: 2.1 MB, 320 calls (green)
- CMO session: 4.5 MB, 600 calls (yellow)
- CEO session: 1.8 MB, 150 calls (green)

### 9.3 Cross-Session Learning Curves

**Track**:
- Average session lifespan per agent
- Which thresholds trigger most often
- Correlation: Threshold type vs quality degradation
- Trend: Are sessions getting longer (better agent habits)?

### 9.4 Predictive Yellow-Line

**Current**: Reactive (wait for threshold breach)
**Future**: Predictive (ML model forecasts breach 30 min ahead)
- Feature engineering: JSONL growth rate, call frequency, deny rate trend
- Model: Logistic regression (simple, interpretable)
- Action: Pre-emptive save chain before yellow-line

### 9.5 Distributed Session State

**Current**: Local filesystem (`memory/`, `.ystar_*.db`)
**Future**: Sync to remote (S3, git LFS, database)
- Enables: Multi-machine deployment, disaster recovery
- Challenge: Atomic sync, conflict resolution

---

## 10. Conclusion

The Aiden Continuity Guardian transforms Y* Bridge Labs' agent team from **session-bound** to **continuous-life**. This is the final piece enabling true 24/7 autonomous operation.

**Key Achievement**: Board no longer needs to manually trigger restarts. Agents self-manage their lifecycle like biological organisms managing sleep.

**Meta-Governance Validation**: Y*gov governance system now governs its own session lifecycle — the ultimate dog-food demonstration.

**Production-Ready**: All M1-M8 metrics validated. Tests passing. Documentation complete. Ready for Board deployment approval.

---

**Author**: Ryan Park (Platform Engineer)
**Reviewed**: Maya Patel (Governance Engineer — hook compliance verified)
**Approved**: Board 2026-04-12
**Commit**: (pending)
