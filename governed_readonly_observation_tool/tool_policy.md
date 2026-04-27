# Governed Read-Only Observation Tool Policy

The wrapper is local-only and contract-first.

Allowed behavior:

- Read generated/read-model JSON summaries listed in `generated/allowed_source_registry.json`.
- Reject any requested source that is not in the allowed registry.
- Reject unsafe paths, path traversal, absolute paths, non-JSON sources, and oversized generated summaries.
- Return normalized observation data only.
- Emit a dry-run CIEU-compatible event envelope with persistence disabled.

Forbidden behavior:

- No live execution.
- No external actions.
- No network access.
- No GitHub issue or PR creation.
- No git push.
- No daemon control.
- No DB, WAL, SHM, SQLite, log, active-agent marker, raw report, brain, memory, or raw runtime artifact reads.
- No CIEU DB/store writes.
- No brain/memory writeback.
- No candidate approvals.
- No semantic truth scoring.

The wrapper is callable for local read-only dry-run use, but remains disabled for live execution.

