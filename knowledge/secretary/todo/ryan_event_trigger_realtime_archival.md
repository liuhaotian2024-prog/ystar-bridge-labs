# TODO for Ryan (eng-platform) — Event Trigger for `realtime_artifact_archival_czl`

- **Owner**: Samantha Lin (Secretary) drafted, Ryan Park (eng-platform) implements
- **Charter**: `agents/Secretary.md` §长期自主任务 → `realtime_artifact_archival_czl`
- **Board directive**: 2026-04-16 (long-term autonomous CZL duty added to Secretary)
- **Need**: event-driven trigger layer so Secretary receives `NEW_ARTIFACT` signal instead of polling

## Required triggers

### 1. post-commit hook
(.git/hooks/post-commit): emit CIEU `NEW_COMMIT_ARTIFACT` with list of files touched under `reports/|knowledge/|products/|content/|governance/`

### 2. fs watcher
(launchd on macOS; prefer `fswatch` over inotify since macOS): watch those 5 dirs, debounce 10s, emit CIEU `NEW_FILE_ARTIFACT` with path + mtime

### 3. subagent return scan
In Stop hook or subagent post-exec, regex `\[L[3-5]\]` on return text → emit CIEU `SUBAGENT_L3PLUS_DELIVERABLE` with agent_id + quoted claim

## 4. Board coined-phrase detector

**Purpose**: Capture novel terminology, metaphors, and conceptual labels coined by Board (Haotian) in dialogue, ensuring high-value cognitive artifacts are indexed before dilution.

**Monitoring sources**:
- Chat transcripts during active session (via hook or session_close extraction)
- Incremental `memory/WORLD_STATE.md` updates (diff detection)
- `.ystar_last_board_msg` rotational log
- `knowledge/ceo/lessons/` Board-comment-heavy files (weekly diff scan)

**Detection heuristic**:
- Quoted terms in Board utterances: `"新术语"` or `「概念」` (Chinese/English)
- Repeated novel phrase ≥2 occurrences in 1 session
- Board uses metaphor + agent echoes back → signal conceptual weight
- Exclusion filter: known Y*gov terminology (grep against `governance/GLOSSARY.md` + `products/ystar-gov/TERMINOLOGY.md`)
- Minimum phrase length: 4 characters / 2 words (avoid trivial fragments)

**CIEU event schema**:
```json
{
  "event_type": "BOARD_COINED_PHRASE",
  "agent_id": "system:board_phrase_detector",
  "context": {
    "phrase": "<extracted term>",
    "first_occurrence_line": "<session log line or WORLD_STATE line>",
    "repetition_count": <int>,
    "session_date": "YYYY-MM-DD"
  }
}
```

**Archival route**:
- Samantha receives event → append to `knowledge/ceo/lessons/board_coined_phrases.md`
- Entry format: `## "新术语" (YYYY-MM-DD)` + first context + Board's original usage + Secretary annotation if semantically dense
- Index back-reference in `ARCHIVE_INDEX.md` under "Board Terminology"

**Rt+1 for detector**:
`1 if BOARD_COINED_PHRASE event emitted but phrase NOT in board_coined_phrases.md else 0`

## Non-goals (out of Ryan scope here)

- Do NOT implement the archival action itself (that's Secretary runtime behavior)
- Do NOT scan historical backlog (separate task)

## Acceptance

- Four CIEU event types emit correctly with canonical agent_id (`system:fswatch` etc)
- Secretary can `SELECT * FROM cieu_events WHERE event_type IN (...)` and react
- Rt+1 on Secretary's duty computable (count unindexed events vs indexed)
