# Continuity Protocol — Cross-Session Life Continuity

**Board-approved**: 2026-04-12
**Scope**: All agents (starting with CEO/Aiden)
**Owner**: Platform Engineering (Ryan Park)
**Status**: Production

---

## 1. Purpose

Agent teams at Y* Bridge Labs operate autonomously 24/7. Sessions must be **continuous life cycles**, not isolated episodes.

This protocol defines how agents:
1. Monitor their own health degradation
2. Trigger autonomous save + restart before catastrophic failure
3. Inject accumulated wisdom into next session
4. Resume work seamlessly as if "waking up from sleep"

**Metaphor**: Like a human going to sleep and waking up — you don't lose your memory, your goals, or your ongoing work. You just resume.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Continuity Guardian (Wrapper, runs OUTSIDE Claude Code)       │
│                                                                 │
│  ┌────────────────┐      ┌──────────────────┐                 │
│  │ Health Watchdog│─────>│ Yellow Line?     │                 │
│  │ (event-driven) │      │ Any threshold:   │                 │
│  │                │      │ - JSONL > 3MB    │                 │
│  │ Monitors:      │      │ - Calls > 500    │                 │
│  │ - JSONL size   │      │ - Runtime > 6h   │                 │
│  │ - Call count   │      │ - Deny rate >30% │                 │
│  │ - Runtime      │      │ - Subagent >500KB│                 │
│  │ - Hook denies  │      │ - Drift > 3      │                 │
│  │ - Subagent KB  │      └────────┬─────────┘                 │
│  │ - CIEU drift   │               │                           │
│  └────────────────┘               │ YES                       │
│                                   ▼                           │
│                       ┌───────────────────────┐               │
│                       │ Graceful Save Chain   │               │
│                       │ 1. session_close_yml  │               │
│                       │ 2. twin_evolution     │               │
│                       │ 3. learning_report    │               │
│                       │ 4. wisdom_extractor   │ <─── NEW      │
│                       │ 5. cognition_backup   │               │
│                       │ 6. git commit + push  │               │
│                       │ 7. continuation.json  │               │
│                       └───────────┬───────────┘               │
│                                   │                           │
│                                   ▼                           │
│                       ┌───────────────────────┐               │
│                       │ Graceful Shutdown     │               │
│                       │ (SIGTERM → wait 10s)  │               │
│                       └───────────┬───────────┘               │
│                                   │                           │
│                                   ▼                           │
│                       ┌───────────────────────┐               │
│                       │ Restart Claude Code   │               │
│                       │ (exec claude)         │               │
│                       └───────────┬───────────┘               │
└───────────────────────────────────┼─────────────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────────┐
                        │ New Session Boot          │
                        │ (governance_boot.sh)      │
                        │                           │
                        │ STEP 7 (NEW):             │
                        │ Read wisdom_package       │
                        │ "你刚醒来 — 这是你5分钟前的自己"│
                        │                           │
                        │ Inject:                   │
                        │ - Core decisions (Top 5)  │
                        │ - New knowledge (Top 3)   │
                        │ - Active obligations      │
                        │ - New methodologies       │
                        │ - Recent CIEU events      │
                        │ - Continuation state      │
                        └───────────┬───────────────┘
                                    │
                                    ▼
                        ┌───────────────────────────┐
                        │ Agent resumes work        │
                        │ (seamless continuity)     │
                        └───────────────────────────┘
```

---

## 3. Components

### 3.1 Health Watchdog (`session_health_watchdog.py`)

**Mode**: Event-driven (monitors JSONL file size changes)

**Thresholds** (Board-approved 2026-04-12):

| Metric | Yellow Line | Rationale |
|--------|-------------|-----------|
| JSONL size | 3.0 MB | ~50% context estimate (conservative) |
| Call count | 500 | High-density sessions |
| Runtime | 6.0 hours | Hard constraint (quality degradation) |
| Hook deny rate | 30% | Recent 50 calls (governance friction) |
| Subagent output | 500 KB | Cumulative this session |
| CIEU drift | 3 events | Out of recent 10 |

**Trigger**: ANY threshold reached → Write `/tmp/ystar_health_yellow`

**Iron Rule 1 Compliance**: Zero LLM. Pure arithmetic thresholds.

### 3.2 Graceful Save Chain (`session_graceful_restart.sh`)

**Orchestration**:
1. `session_close_yml.py` — YML memory distillation
2. `twin_evolution.py --mode all` — Board values/genes extraction
3. `learning_report.py` — Lessons learned
4. **`session_wisdom_extractor.py`** ← NEW — Session essence (≤10KB)
5. `aiden_cognition_backup.py --full` — Full cognitive mirror
6. `git commit + push` — Precise file add (no `-A`)
7. Verify `continuation.json` snapshot
8. Write `/tmp/ystar_ready_for_restart`

**Failure Mode**: Fail-open. Partial save still triggers restart.

### 3.3 Session Wisdom Extractor (`session_wisdom_extractor.py`)

**Purpose**: Distill session into ≤10KB "wake-up briefing"

**Extracts**:
- Top 5 core decisions (from CIEU events)
- Top 3 new knowledge/patterns (from memory.db)
- Active obligations / next actions
- Top 3 new methodologies/genes (from CIEU patterns)
- Recent 5 important CIEU events
- Continuation state summary

**Output**: `memory/wisdom_package_<session_id>.md`
**Latest Link**: `memory/wisdom_package_latest.md`

**Zero Fabrication**: All extracted from databases. No LLM summaries.

### 3.4 Boot Integration (`governance_boot.sh` STEP 7)

**Injection Point**: After STEP 10 (continuation.json), before STEP 11 (drift check)

**Display**:
```bash
if [ -f "memory/wisdom_package_latest.md" ]; then
  echo "--- SESSION WISDOM (你刚醒来 — 这是你5分钟前的自己) ---"
  cat memory/wisdom_package_latest.md
fi
```

**Experience**: Agent reads wisdom package as first context → knows exactly what was happening 5 minutes ago.

### 3.5 Continuity Guardian Wrapper (`aiden_continuity_guardian.sh`)

**Runs**: Outside Claude Code (parent process)

**Loop**:
1. Start `claude` subprocess
2. Start `session_health_watchdog.py` in background
3. Poll for `/tmp/ystar_health_yellow`
4. On yellow line → Execute save chain
5. Send SIGTERM to claude (graceful shutdown, wait 10s)
6. Restart claude
7. Repeat

**Board Override**: `touch /tmp/ystar_no_auto_restart` → Disable loop, exit

**Fail-Open**: If guardian crashes, claude continues running (no harm)

---

## 4. Yellow-Line Philosophy

**Not Red-Line**: We don't wait for catastrophic failure (context explosion, OOM).

**Yellow-Line = Preventive**: Trigger restart when quality *starts* degrading, not when it's *already degraded*.

**Conservative Thresholds**: Better to restart too early (no cost) than too late (data loss).

**Example**: JSONL at 3MB might be fine, but 6MB is risky. We restart at 3MB.

---

## 5. Wisdom Package Design

**≤10KB Constraint**: Next session boot must be fast. No multi-megabyte context injection.

**Content Selection**:
- **Decisions**: Only Board-level or high-impact (INTENT_ADJUSTED, DIRECTIVE_*, GOV_ORDER)
- **Knowledge**: Only `lesson`, `knowledge`, `pattern` memory types
- **Obligations**: Active only (not completed)
- **Methodologies**: Only from CIEU events mentioning "methodology", "pattern", "framework"
- **CIEU Events**: Only non-HOOK events (HOOK_* are noisy)

**No LLM Summarization**: All extraction is database queries + truncation. Zero hallucination risk.

**Metaphor**: Like a colleague leaving you a sticky note: "We were discussing X, decided Y, next step is Z."

---

## 6. Graceful Shutdown Protocol

**Signal**: SIGTERM (not SIGKILL)

**Wait**: Up to 10 seconds for claude to finish current response

**Fallback**: If still running after 10s → SIGKILL (forced)

**Why**: Claude Code may be mid-tool-call or mid-write. Give it time to complete gracefully.

---

## 7. Git Commit Strategy

**No `git add -A`**: Current repo has 213 uncommitted files (many temporary).

**Precise Add**:
```bash
FILES_TO_ADD=(
  "memory/session_handoff.md"
  "memory/continuation.json"
  "memory/wisdom_package_*.md"
  ".ystar_memory.db"
  ".ystar_cieu.db"
  ".ystar_omission.db"
  ".ystar_session.json"
  "reports/daily/*.md"
  "knowledge/*/twin_dna_*.json"
  "knowledge/*/active_task.json"
)
```

**Commit Message Template** (pre-whitelisted in hook):
```
infra: session state saved before graceful restart [HH:MM]

Health threshold reached. Save chain executed:
- Memory distillation
- Values extraction
- Learning report
- Wisdom package
- Cognition backup
- Continuation snapshot

Next session will inject wisdom package for seamless continuity.

Co-Authored-By: Ryan Park (Platform Engineer) <noreply@ystar.com>
```

---

## 8. Board Override Mechanisms

**Disable Auto-Restart**:
```bash
touch /tmp/ystar_no_auto_restart
```

**Re-Enable**:
```bash
rm /tmp/ystar_no_auto_restart
```

**Check Status**:
```bash
[ -f /tmp/ystar_no_auto_restart ] && echo "DISABLED" || echo "ENABLED"
```

**When to Use**:
- Board wants to manually control restart timing
- Debugging session issues
- Running special one-off sessions

---

## 9. Failure Modes & Recovery

| Failure | Impact | Recovery |
|---------|--------|----------|
| Watchdog crashes | No auto-restart | Guardian exits (fail-open), claude continues |
| Save chain partial failure | Some data not saved | Continue anyway (fail-open), emit warning |
| Git push fails | State not synced to remote | Non-fatal, data still local |
| Wisdom extractor fails | No wisdom package | Boot proceeds without STEP 7 |
| Claude won't gracefully exit | Restart delayed | Force SIGKILL after 10s |
| Guardian crashes | No monitoring | Claude continues until manual restart |

**Design Philosophy**: Fail-open. Never block agent work due to infrastructure issues.

---

## 10. Metrics & Success Criteria

| # | Metric | Target | Validation |
|---|--------|--------|------------|
| M1 | Guardian detects yellow-line | 100% | Synthetic test: 3MB JSONL |
| M2 | Save chain completes | 100% | All 7 steps execute |
| M3 | Wisdom package size | ≤10 KB | Measure output file |
| M4 | Boot time | ≤1 CIEU event depth | New session first response |
| M5 | Continuity | Agent knows recent context | Ask "what were we doing?" |
| M6 | Hook compliance | Zero violations | CIEU audit log |
| M7 | Fail-open | Agent continues if guardian dies | Kill guardian, verify claude runs |
| M8 | Board override | Auto-restart disabled | Touch override file, verify exit |

**All metrics tested in `tests/test_continuity_guardian.py`**

---

## 11. Future Extensions

### Multi-Agent Support
Currently designed for CEO/Aiden. Future:
- CTO/Ethan may have independent sessions
- CMO/Sofia may have marketing-focused sessions
- Each agent has own watchdog + wisdom package

**Design**: Agent-agnostic. Pass `agent_id` to all scripts.

### Adaptive Thresholds
Current thresholds are static. Future:
- Learn optimal thresholds per agent
- Adjust based on task complexity
- Dynamic threshold tuning

### Cross-Session Learning Curves
Track:
- How often sessions hit yellow-line
- Which thresholds trigger most often
- Average session lifespan
- Quality metrics before/after restart

---

## 12. Show HN Narrative Angle

**Headline**: "Our CEO never sleeps — autonomous session lifecycle for AI agents"

**Key Points**:
1. **Problem**: AI agents lose context between sessions. Manual restarts break continuity.
2. **Solution**: Health monitoring + graceful save + automatic restart + wisdom injection.
3. **Dog-Food**: Y*gov governance system managing itself (meta-governance).
4. **Iron Rule 1**: Zero LLM in lifecycle management (deterministic thresholds only).
5. **Fail-Open**: Infrastructure failures don't block agent work.
6. **Open Source**: All code in ystar-company repo.

**Demo**:
- Show health dashboard (M1-M8 metrics)
- Trigger yellow-line artificially
- Show save chain executing
- Show new session resuming seamlessly
- "Aiden doesn't know he was restarted"

---

## 13. Appendix: File Locations

| Component | Path |
|-----------|------|
| Guardian wrapper | `scripts/aiden_continuity_guardian.sh` |
| Health watchdog | `scripts/session_health_watchdog.py` |
| Wisdom extractor | `scripts/session_wisdom_extractor.py` |
| Save chain | `scripts/session_graceful_restart.sh` |
| Boot integration | `scripts/governance_boot.sh` (STEP 7) |
| Protocol doc | `governance/CONTINUITY_PROTOCOL.md` (this file) |
| Tests | `tests/test_continuity_guardian.py` |
| Design doc | `reports/proposals/continuity_guardian_design.md` |

---

**This protocol enables true 24/7 autonomous agent operation. Aiden can work indefinitely, self-managing his own lifecycle like a biological organism managing sleep cycles.**
