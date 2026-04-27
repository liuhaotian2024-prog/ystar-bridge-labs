# Candidate Review Queue

The review queue turns safe-mined Markdown report candidates into explicit review entries.

Queue entries are not memory, CIEU records, capsule updates, or brain writeback. They are pending decisions about whether a candidate may later become a reviewed hint for continuity, governance gaps, role-brain capsules, Pre-U packets, or CIEU prediction-delta work.

The queue builder reads only:

- `runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json`

It does not reopen source reports, DBs, logs, active-agent markers, daemon state, or runtime files. Every generated entry starts as `pending_review` with `ingestion_status: not_ingested`.

The backlog disposition layer consumes the generated queue as one of its curated inputs and keeps every linked entry `not_ingested`.

The evidence review layer consumes the generated queue to create structural
scores, undecided decision stubs, and not-approved hint routes. Queue entries
remain pending and not ingested.
