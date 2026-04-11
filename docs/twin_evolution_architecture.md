# Digital Twin Evolution Architecture

## Overview

Board's digital twin evolution system automatically captures Board's decision principles and compensates for Board's self-identified limitations, mirroring the idle_learning architecture.

## Design Philosophy

**"Board的数字分身需要和空闲学习一样的自动化保障"**

The system ensures CEO (Aiden) gradually evolves toward Board's decision-making quality while compensating for Board's known weaknesses.

## Three Evolution Modes

### Mode 1: extract-values

**Purpose**: Extract Board's decision principles from CIEU audit trail

**Process**:
1. Scan `.ystar_cieu.db` for `agent_id="board"` events
2. Target event types:
   - `INTENT_CONFIRMED` - Board confirmed a CEO decision (approval rationale)
   - `INTENT_ADJUSTED` - Board adjusted CEO's intent (correction principle)
   - `DIRECTIVE_REJECTED` - Board rejected a directive (critical lesson)
   - `GOV_ORDER` - High/Critical severity governance orders
3. Extract decision rationale from `params_json`, `result_json`, `task_description`
4. Check existing YML memories to avoid duplicates
5. Write new principles to YML:
   - `memory_type: "lesson"`
   - `half_life_days: 365` (Board values decay very slowly)
   - `context_tags: ["board_value", "digital_twin"]`
   - `agent_id: "ceo"` (CEO is responsible for learning Board's principles)

**Example Extracted Value**:
```
Board adjusted: "Direct code commit" → "CTO authorization required first"
Reason: Chain of command violation - CEO must not bypass CTO for engineering tasks
```

### Mode 2: capability-gap

**Purpose**: Analyze CEO's capability coverage vs world-class standard

**Metrics**:
- `world_class_standard.md` existence
- Theory entries count: `knowledge/ceo/theory/*.md`
- Expected theories: Count from `task_type_map.md`
- Coverage percentage: `theory_count / expected_theories * 100`

**Output**:
```
CEO能力覆盖率: 5/12 theory files (42%)
Gap: Missing theories for strategic_planning, crisis_management, ...
```

### Mode 3: compensation-check

**Purpose**: Detect Board's 3 known limitations in CEO's recent behavior

**Board's Self-Identified Limitations**:

1. **Emotional Volatility** (情绪波动大)
   - **Detector**: Count `INTENT_ADJUSTED` events per session
   - **Threshold**: >3 adjustments in one session = volatile
   - **Compensation**: Cooling-off period recommendation

2. **Systemic Management Gap** (管理系统性不足)
   - **Detector**: CEO dispatching to `eng-*` agents without CTO in session
   - **Threshold**: Any unauthorized dispatch = violation
   - **Compensation**: Enforce chain of command governance rule

3. **Intuition Over Analysis** (直觉优于分析)
   - **Detector**: `INTENT_DECLARED` without prior `gov_check`/`gov_precheck`
   - **Threshold**: >2 unchecked decisions in 7 days
   - **Compensation**: Mandatory pre-commit governance checks

**Auto-Remediation**:
- If limitations detected, write `memory_type="gap"` to YML
- `half_life_days=30` (faster decay - CEO must demonstrate improvement)
- `context_tags: ["limitation_compensation", "board_weakness"]`

## Automated Execution

### Daily Cron Schedule

```bash
# Add to crontab:
37 22 * * * /path/to/ystar_wakeup.sh twin
```

**Why 22:37?**
- Evening execution after day's work
- CIEU events accumulated from full workday
- Fresh insights for next morning

### Manual Execution

```bash
# Full evolution cycle
python3 scripts/twin_evolution.py --mode all

# Individual modes
python3 scripts/twin_evolution.py --mode extract-values
python3 scripts/twin_evolution.py --mode capability-gap
python3 scripts/twin_evolution.py --mode compensation-check

# View evolution status
python3 scripts/twin_report.py
```

## Integration with Session Protocol

**CLAUDE.md Session Close Protocol**:

```
Session结束时必须：
1. 删除 scripts/.session_booted 和 .session_call_count
2. 运行 python3 scripts/session_close_yml.py ceo "session summary"
3. 如果本session有Board参与，运行 python3 scripts/twin_evolution.py --mode extract-values
```

**Trigger Logic**:
- Check if `CIEU_DB` contains `agent_id="board"` events in current session
- If yes → extract Board values immediately while context is fresh
- Write to YML before session state is cleared

## Audit Trail (CIEU + Gemma Log)

### CIEU Event Recording

Every twin evolution execution writes:
```sql
event_type: TWIN_EVOLUTION
agent_id: ceo
task_description: "{mode}: {action}"
params_json: {
  "mode": "extract-values",
  "action": "board_value_extraction",
  "outcome": "5 new lessons extracted",
  "details": {...}
}
```

### Gemma Session Log

Every execution appends to `knowledge/ceo/gaps/gemma_sessions.log`:
```json
{
  "timestamp": 1775876107.29,
  "actor": "ceo",
  "mode": "twin_evolution",
  "submode": "extract-values",
  "action": "board_value_extraction",
  "result": {
    "total_events": 15,
    "lessons_extracted": 5,
    "duplicates_skipped": 10
  }
}
```

## Reporting

### Daily Twin Evolution Report

Location: `reports/daily/YYYY-MM-DD_twin_evolution.md`

Content:
```
=== Digital Twin Evolution Report ===

Board价值观已提取: 23条 (YML中tag=board_value的lesson)
CEO能力覆盖率: 7/12 theory files (58%)

局限补偿状态 (最近7天):
  情绪波动检测: 2次异常 / 阈值 3
  越权指挥检测: 0次 / 阈值 0
  无预检决策: 1次 / 阈值 2

总体评估:
  ⚠ 检测到 3 项局限表现 - 建议加强补偿机制

最后进化日期: 2026-04-10
```

## Key Design Decisions

### 1. Why 365-day half-life for Board values?

Board's core principles should persist long-term. Unlike tactical knowledge (7-day half-life for session context), governance principles are constitutional and should decay slowly.

### 2. Why deduplicate against existing lessons?

Board often reinforces the same principles across multiple sessions. Duplicate lessons create noise and waste YML storage. Normalization (lowercase + strip) prevents semantic duplicates.

### 3. Why CEO (not Board) is agent_id for lessons?

- Board is the **teacher**, CEO is the **student**
- YML memories belong to the agent who needs to learn
- CEO's recall engine uses `agent_id="ceo"` for decision support

### 4. Why 30-day half-life for limitation gap memories?

Gap memories should expire faster to incentivize improvement. If CEO demonstrates sustained good behavior, limitation warnings decay naturally.

## Future Enhancements

### Phase 2: Active Intervention

Currently, the system is **observational** (detect and log). Phase 2 will add:
- Pre-commit hooks that block unauthorized engineer dispatches
- Cooling-off enforcer (force 1-hour delay after volatile session)
- Mandatory gov_precheck before INTENT_DECLARED

### Phase 3: Counterfactual Twin Simulation

Similar to idle_learning Priority 3:
- Generate fictional Board-CEO conflict scenarios
- CEO drafts resolution plan
- Compare plan against extracted Board values
- Identify gaps in CEO's internalization of Board principles

### Phase 4: Gemma-Powered Value Synthesis

Use local Gemma to:
- Cluster similar Board values (find common themes)
- Generate high-level governance principles from specific decisions
- Auto-update `world_class_standard.md` with distilled wisdom

## Files

### Core Scripts
- `scripts/twin_evolution.py` - Three-mode evolution executor
- `scripts/twin_report.py` - Evolution progress dashboard
- `scripts/ystar_wakeup.sh` - Cron integration wrapper

### Configuration
- `CLAUDE.md` - Session close protocol (auto-extract if Board present)

### Data Sources
- `.ystar_cieu.db` - CIEU audit trail (source of Board decisions)
- `.ystar_memory.db` - YML memory store (target for lessons/gaps)
- `knowledge/ceo/gaps/gemma_sessions.log` - Execution audit log

### Outputs
- `reports/daily/*_twin_evolution.md` - Daily evolution reports
- YML memories with `tag:board_value` - Extracted principles
- YML memories with `tag:limitation_compensation` - Detected gaps

## Verification

```bash
# Check Board values in YML
sqlite3 .ystar_memory.db "
  SELECT content, created_at
  FROM memories
  WHERE agent_id='ceo'
  AND memory_type='lesson'
  AND context_tags LIKE '%board_value%'
  ORDER BY created_at DESC
  LIMIT 10
"

# Check twin evolution execution history
tail -20 knowledge/ceo/gaps/gemma_sessions.log | grep twin_evolution

# View latest report
cat reports/daily/$(date +%Y-%m-%d)_twin_evolution.md
```

## Success Metrics

**Short-term (1 month)**:
- Board values extracted: >20 lessons
- CEO capability coverage: >60%
- Limitation detections: <5 per week

**Medium-term (3 months)**:
- Board intervention rate decreases (fewer INTENT_ADJUSTED events)
- CEO theory library complete (100% coverage)
- Zero unauthorized dispatches

**Long-term (6 months)**:
- Board can delegate full authority to CEO for routine decisions
- CEO demonstrates consistent governance-first mindset
- Digital twin quality approaches Board's decision-making standard

---

**Implementation Date**: 2026-04-10
**Owner**: CTO (Ethan Wright)
**Stakeholders**: Board, CEO (Aiden Liu)
