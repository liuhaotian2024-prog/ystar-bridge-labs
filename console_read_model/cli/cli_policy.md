# CLI Policy

## Allowed Sources

The CLI may read only generated snapshot files:

- `console_read_model/generated/team_console_snapshot.json`
- `console_read_model/generated/agent_cards_compiled.json`
- `console_read_model/generated/readiness_summary.json`
- `console_read_model/generated/quarantine_summary.json`
- `console_read_model/generated/generation_manifest.json`

## Forbidden Sources

The CLI must not read:

- `.db`, `.db-wal`, `.db-shm`
- `scripts/.logs`
- `__pycache__`
- active-agent markers
- `.pid`
- daemon state
- raw runtime report directories

## Execution Rules

- No writes.
- No subprocesses.
- No runtime truth claims.
- No direct DB/log/runtime access.

Generated snapshots are curated static state, not live team state.
The quarantine summary is also curated static state. It may show path-level
counts/classes from the quarantine manifest, but the CLI must never follow those
paths or read artifact contents.
