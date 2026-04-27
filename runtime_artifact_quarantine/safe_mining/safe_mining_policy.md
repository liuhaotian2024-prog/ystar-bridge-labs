# Safe Mining Policy

Safe mining v0 implements bounded Markdown candidate extraction only.

Allowed behavior:

- Read `runtime_artifact_quarantine/generated/runtime_artifact_manifest.json`.
- Select only approved Markdown report classes.
- Read at most five files per class.
- Read at most forty lines per file.
- Read at most four thousand characters per file.
- Extract headings, simple source metadata, and bounded snippets.
- Generate candidate-only indexes under `runtime_artifact_quarantine/safe_mining/generated/`.

Forbidden behavior:

- Reading SQLite DB, WAL, or SHM contents.
- Reading `scripts/.logs/*`.
- Reading active-agent marker contents.
- Reading daemon pid/state contents.
- Reading pycache or backup DB contents.
- Treating candidates as canonical memory.
- Writing CIEU records.
- Writing brain or memory state.
- Cleaning, moving, deleting, archiving, or staging raw runtime artifacts.

Candidate records are safe only as review inputs. The next allowed step is human review or a future curated queue. Direct brain writeback is explicitly forbidden.

The review queue consumes only generated candidate JSON. It does not reopen raw reports. Every queue entry starts as `pending_review` and `not_ingested`.
