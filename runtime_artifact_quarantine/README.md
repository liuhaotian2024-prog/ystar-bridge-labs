# Runtime Artifact Quarantine

Runtime artifacts are not canonical memory.

They may contain valuable evidence, CIEU signals, dream diffs, agent behavior
traces, failure evidence, and governance insights, but they require quarantine
and curation before they can nourish agent brains or inform architecture.

This framework classifies runtime artifacts without reading unsafe contents. It
supports future safe mining adapters while preserving the boundary between raw
runtime evidence and curated memory.

This milestone does not clean, ingest, migrate, archive, delete, or move
anything. It creates a path-level inventory framework only.

Relationship:

- `console_read_model/` consumes curated snapshots, not raw artifacts.
- `agent_brains/` are persistent role-brain read models.
- CIEU and future adapters should convert selected runtime evidence into
  reviewed, structured learning signals.
- Brain writeback should only happen after curation and governance-compatible
  review.
