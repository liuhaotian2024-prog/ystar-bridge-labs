# C5 Working Memory Snapshot - Integration Guide

**Component**: C5 of AMENDMENT-015 v2 LRS (Lifecycle Resurrection System)  
**Author**: Maya Patel (eng-governance)  
**Status**: ✅ Shipped (MVP)  
**Coverage**: Dimension 4 (Working Memory)

---

## What It Does

Captures structured snapshot of agent's working memory at session boundaries:

1. **Recent CIEU events** (last 20) - immediate context from governance logs
2. **Active sub-agents** - parsed from `/private/tmp/.../tasks/*.output`
3. **Today's targets progress** - from `goal_progress.py` output
4. **Recent commits** - last hour from ystar-company + Y-star-gov repos
5. **Unfinished tool calls** - placeholder (requires LLM context access)
6. **Last Board directive** - placeholder (requires conversation history access)

---

## Files

### Core Implementation
- `scripts/working_memory_snapshot.py` - Snapshot capture/save/load engine
- `tests/test_working_memory_snapshot.py` - 7 unit tests (all passing)

### Integration Points
- `scripts/hook_session_start.py` - SessionStart hook reads latest snapshot
- `memory/working_memory_snapshot_*.json` - Persisted snapshots

---

## Usage

### Command Line

```bash
# Save current snapshot
python3 scripts/working_memory_snapshot.py save

# Save with explicit session/agent ID
python3 scripts/working_memory_snapshot.py save --session-id abc123 --agent-id maya

# Load latest snapshot (outputs JSON to stdout)
python3 scripts/working_memory_snapshot.py load-latest
```

### Programmatic

```python
from working_memory_snapshot import WorkingMemorySnapshot

engine = WorkingMemorySnapshot()

# Capture snapshot
snapshot = engine.capture(session_id='test', agent_id='maya')

# Save to file
path = engine.save(snapshot)

# Load latest
latest = engine.load_latest()
```

---

## Integration Status

### ✅ SessionStart Hook (hook_session_start.py)

**Where**: After C7 replay (Ryan's impl), before wisdom package  
**Priority**: 3 (C7=1, C3=2, C5=3, C1=4)

The hook calls `working_memory_snapshot.py load-latest` and injects summary:

```
## Working Memory Snapshot (C5 LRS)
- Session: 20260413_112345
- Captured: 2026-04-13T11:23:45Z
- Recent CIEU events: 20
- Active subagents: 3
- Recent commits: 5

<details>
<summary>Full snapshot (click to expand)</summary>
...
</details>
```

### ⏳ SessionClose Hook (Pending)

**Recommended integration** - Add to session close workflow:

```bash
# In session_close_yml.py or equivalent
python3 scripts/working_memory_snapshot.py save
```

**Alternative** - Manual/cron trigger:

```bash
# Add to nightly cron or pre-restart checklist
python3 scripts/working_memory_snapshot.py save
```

---

## Data Schema

```json
{
  "session_id": "20260413_112345",
  "agent_id": "maya",
  "captured_at": "2026-04-13T11:23:45.678901Z",
  
  "recent_cieu_events": [
    {
      "event_type": "file_write",
      "decision": "allow",
      "file_path": "scripts/working_memory_snapshot.py",
      "agent_id": "eng-governance",
      "created_at": 1776093976.265054
    }
  ],
  
  "active_subagents": [
    {
      "task_file": "bafq0oh08.output",
      "age_minutes": 2.3,
      "size_bytes": 4521,
      "preview": "Running task: implement C5..."
    }
  ],
  
  "today_targets_progress": {
    "status": "ok",
    "progress_lines": ["▓▓▓▓░░░░░░ 40% - C5 snapshot MVP"],
    "full_output_length": 2341
  },
  
  "recent_commits": [
    {
      "repo": "ystar-company",
      "commits": [
        "abc1234 feat: C5 working memory snapshot",
        "def5678 test: add 7 unit tests for C5"
      ]
    }
  ],
  
  "unfinished_tool_calls": [],
  "last_board_directive": ""
}
```

---

## Tests

All 7 unit tests passing (pytest-8.4.2):

1. ✅ `test_capture_returns_correct_schema` - Validates all required fields
2. ✅ `test_save_load_roundtrip` - Persistence integrity
3. ✅ `test_recent_cieu_only_takes_20` - Enforces 20-event limit
4. ✅ `test_subagent_status_parsing` - Subagent field validation
5. ✅ `test_load_latest_returns_none_when_empty` - Empty dir handling
6. ✅ `test_load_latest_picks_most_recent` - mtime-based selection
7. ✅ `test_goal_progress_integration` - goal_progress.py bridge

Run: `python3 -m pytest tests/test_working_memory_snapshot.py -v`

---

## Performance

- Snapshot capture: ~200-500ms (depends on CIEU DB size, git log)
- File size: 5-20 KB per snapshot (JSON, human-readable)
- SessionStart overhead: +300ms for load-latest + formatting

---

## Future Enhancements (Post-MVP)

1. **unfinished_tool_calls** - Extract from Claude Code conversation JSONL
2. **last_board_directive** - Parse last user message from JSONL
3. **Compression** - Archive snapshots older than 7 days
4. **Diff view** - Compare current vs previous snapshot
5. **Selective fields** - Allow caller to skip expensive fields (e.g., `--skip-commits`)

---

## Compatibility

- **Iron Rule 1**: ✅ No LLM calls during boot (all offline data processing)
- **C7 Conversation Replay**: ✅ Compatible - C5 loads after C7 prepending
- **12 Y\*gov Innovations**: ✅ No conflicts - uses CIEU as input source

---

## Rollback Plan

If C5 causes session start delays or errors:

1. Comment out `_append_working_memory_snapshot()` call in `hook_session_start.py`
2. Snapshots will stop being loaded at boot (but can still be saved/queried manually)
3. No data loss - existing snapshots remain in `memory/`

---

**Ship date**: 2026-04-13  
**Tool count**: 25/25 (atomic single activity)  
**Next**: Ryan's C7 Conversation Replay Engine (parallel track)
