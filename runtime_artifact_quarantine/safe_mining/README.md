# Runtime Artifact Safe Mining

This directory contains the first safe mining adapter layer for quarantined runtime artifacts.

Safe mining v0 reads the existing path-level quarantine manifest, selects only low-risk Markdown report classes, and extracts bounded candidate snippets for later human review. The generated candidates are not canonical memory, not CIEU records, and not brain writeback.

Allowed source classes for this adapter:

- `DREAM_REPORT`
- `DAILY_REPORT`
- `DRIFT_REPORT`
- `ESCALATION_REPORT`
- `WHITELIST_REPORT`

The adapter refuses DB/WAL/SHM files, logs, active-agent markers, daemon state, pycache, backups, unknown runtime artifacts, and any non-Markdown source. It caps files, lines, and characters so report inspection remains bounded.

Generated files under `generated/` are candidate assets only. They may be shown by the console read model, but they still require review before any memory, CIEU, or brain pathway can use them.

`review_queue/` adds the next boundary: generated candidate records become pending review entries with explicit intended-use hints and forbidden direct-ingestion actions. Review queue entries are not approvals and are not canonical memory.
