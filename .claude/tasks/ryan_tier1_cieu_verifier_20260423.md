## Task: Build `scripts/cieu_receipt_verifier.py` — Tier 1 CIEU Hard Gate CLI

Engineer: eng-platform (Ryan Park)
Priority: P0
Date: 2026-04-23
Assigned by: CTO (Ethan Wright)

## BOOT CONTEXT (read before coding)

Board approved a 3-tier CIEU QA gate. You are building Tier 1: a CLI that verifies a CIEU event_id exists and matches expected values. This is the hard gate — if this script says "no match", the CEO rejects the sub-agent receipt.

Read the CTO opinion memo for full context: `reports/cto/opinion_k9_cieu_always_20260423.md`

## Deliverable

Create `scripts/cieu_receipt_verifier.py` with the following spec:

### CLI Interface

```bash
python3 scripts/cieu_receipt_verifier.py --event-id <uuid> --expected-decision <allow|auto_approve|warn|deny|escalate|ALLOW> [--expected-file-path <path>]
```

### Behavior

1. Open `.ystar_cieu.db` (read-only, same directory as script's parent `../.ystar_cieu.db`, or accept `--db-path` override)
2. Query: `SELECT event_id, decision, created_at, file_path, agent_id, event_type, substr(params_json, 1, 500) as params_preview, substr(result_json, 1, 500) as result_preview FROM cieu_events WHERE event_id = ?`
3. If event not found: exit 1, stderr "EVENT_NOT_FOUND: {event_id}"
4. If event found but decision does not match `--expected-decision` (case-insensitive compare): exit 2, stderr "DECISION_MISMATCH: expected={expected} actual={actual}"
5. If `--expected-file-path` given and event's `file_path` does not match: exit 3, stderr "FILE_PATH_MISMATCH: expected={expected} actual={actual}"
6. If all checks pass: exit 0

### Stdout Output (always, even on failure)

JSON object on stdout:
```json
{
  "event_id": "...",
  "decision": "...",
  "created_at": 1234567890.123,
  "created_at_iso": "2026-04-23T12:34:56Z",
  "file_path": "...",
  "agent_id": "...",
  "event_type": "...",
  "params_preview": "...",
  "result_preview": "...",
  "match": true,
  "errors": []
}
```

On not-found, output `{"event_id": "<queried>", "match": false, "errors": ["EVENT_NOT_FOUND"]}`.

### Additional Requirements

- `--help` must work and be informative
- `--db-path` optional override (default: resolve relative to script location)
- Target latency: <5ms for the query. Single indexed lookup on `event_id` (UNIQUE index exists).
- **READ-ONLY**: Do NOT write to `.ystar_cieu.db`. No INSERT, no UPDATE, no CREATE. Open with `uri=file:...?mode=ro` or equivalent.
- Use `datetime.datetime.utcfromtimestamp()` for ISO conversion of `created_at`.
- No external dependencies beyond Python stdlib (sqlite3, json, argparse, datetime, sys, os).
- Script must be executable: include `#!/usr/bin/env python3` and `if __name__ == "__main__"` guard.

### CIEU Event for Your Ship

After building the script, you MUST emit a CIEU event recording that you shipped it. Use the existing CIEU infrastructure (import from ystar if available, or direct sqlite3 INSERT as last resort — but into a NEW event, not modifying existing ones). The event must have:
- `agent_id`: "eng-platform"
- `event_type`: "TIER1_CIEU_VERIFIER_SHIPPED"
- `decision`: "allow"
- `task_description`: "Built scripts/cieu_receipt_verifier.py — Tier 1 CIEU hard gate CLI"
- Return the `event_id` in your receipt so CTO can verify.

## Acceptance Criteria

- [ ] `python3 scripts/cieu_receipt_verifier.py --help` exits 0 with usage info
- [ ] Live query on known event `906d71b8-fad5-4c06-90ce-77994fd06b9d` with `--expected-decision ALLOW` exits 0 and outputs valid JSON
- [ ] Query on non-existent event exits 1
- [ ] Decision mismatch exits 2
- [ ] No writes to `.ystar_cieu.db` (K9 write count stays 0)
- [ ] CIEU event emitted for your ship, event_id returned in receipt

## Scope (positive allowlist)

- WRITE: `scripts/cieu_receipt_verifier.py` ONLY
- READ: `.ystar_cieu.db`, this task card, `reports/cto/opinion_k9_cieu_always_20260423.md`
- **NO git commit / push / add / reset**
- **NO modifications to any other file**

## Receipt Format

Return to CTO with:
```yaml
task: Tier 1 CIEU Receipt Verifier
status: COMPLETE / BLOCKED
event_id: <your-ship-cieu-event-id>
verify_sql: "SELECT event_id, decision FROM cieu_events WHERE event_id = '<your-event-id>'"
tool_uses: <count>
files_written: [scripts/cieu_receipt_verifier.py]
test_evidence:
  help_exit_code: 0
  known_event_exit_code: 0
  missing_event_exit_code: 1
  mismatch_exit_code: 2
```
