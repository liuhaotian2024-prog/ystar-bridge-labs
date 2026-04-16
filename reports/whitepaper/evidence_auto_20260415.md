# CZL Enforcement Evidence Report
Generated: 2026-04-15 20:48:49

## Summary

Total CZL enforcement events: 71
Unique sessions: 3
Date range: 2026-04-14 00:31:19 to 2026-04-16 00:47:24

This report aggregates governance enforcement events from Y*gov's CIEU database,
demonstrating real-world runtime governance in action.

## Event Counts by Type

| Event Type | Count | Description |
|------------|-------|-------------|
| `DEFER_LANGUAGE_DRIFT` | 29 | Defer language drift |
| `BOARD_CHOICE_QUESTION_DRIFT` | 27 | Choice question to Board |
| `CEO_CODE_WRITE_DRIFT` | 10 | CEO writing code |
| `DEFER_IN_REPLY_DRIFT` | 2 | Defer language in reply |
| `BACKLOG_DISGUISE_DRIFT` | 1 | Backlog as defer disguise |
| `CANONICAL_HASH_DRIFT` | 1 | Canonical hash mismatch |
| `IMMUTABLE_FORGOT_BREAK_GLASS` | 1 | Immutable file edit without break-glass |

## Timeline (Latest 20 Events)

| Timestamp | Event Type | Agent | Session ID (last 8) |
|-----------|------------|-------|---------------------|
| 2026-04-16 00:47:24 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-16 00:47:24 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-16 00:47:24 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-16 00:40:57 | `BACKLOG_DISGUISE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-16 00:15:24 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-16 00:15:24 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:53 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:53 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:52 | `BOARD_CHOICE_QUESTION_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:52 | `BOARD_CHOICE_QUESTION_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:52 | `BOARD_CHOICE_QUESTION_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:52 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:52 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:03 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:03 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:03 | `BOARD_CHOICE_QUESTION_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:03 | `BOARD_CHOICE_QUESTION_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:03 | `BOARD_CHOICE_QUESTION_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:03 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |
| 2026-04-15 23:27:03 | `DEFER_LANGUAGE_DRIFT` | forget_guard | 0a84f3c6 |

## Representative Samples

### Sample 1: ForgetGuard Deny

**Event ID**: `fg_1776314844385_1776300443939684`
**Timestamp**: 2026-04-16 00:47:24
**Agent**: forget_guard
**Event Type**: `DEFER_LANGUAGE_DRIFT`
**Decision**: warn
**Drift Detected**: True

**Drift Details**:
```json
{
  "rule_id": "defer_language",
  "severity": "low",
  "tool": "Write",
  "file_path": "reports/test.md",
  "command": null
}
```

**File Path**: `reports/test.md`

## Reproducibility

To re-run this query:

```bash
python3 scripts/evidence_aggregator.py > reports/whitepaper/evidence_auto_$(date +%Y%m%d).md
```

Direct SQL query:

```sql
SELECT event_id, created_at, agent_id, event_type, decision
FROM cieu_events
WHERE event_type IN (
  'FORGETGUARD_DENY',
  'CANONICAL_HASH_DRIFT',
  'DEFER_IN_REPLY_DRIFT',
  'BACKLOG_DISGUISE_DRIFT',
  'PROMPT_SUBGOAL_CHECK',
  'SUBGOAL_COMPRESSED',
  'CAMPAIGN_STUB_REJECTED',
  'DEFER_LANGUAGE_DRIFT',
  'BOARD_CHOICE_QUESTION_DRIFT',
  'IMMUTABLE_FORGOT_BREAK_GLASS',
  'CEO_CODE_WRITE_DRIFT'
)
ORDER BY created_at DESC;
```


