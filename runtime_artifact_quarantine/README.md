# Runtime Artifact Quarantine

Runtime artifacts are not canonical memory.

They may contain valuable evidence, CIEU signals, dream diffs, agent behavior
traces, failure evidence, and governance insights, but they require quarantine
and curation before they can nourish agent brains or inform architecture.

This framework classifies runtime artifacts without reading unsafe contents. It
supports future safe mining adapters while preserving the boundary between raw
runtime evidence and curated memory.

This framework does not clean, ingest, migrate, archive, delete, or move
anything. The base quarantine inventory is path-level only.

`safe_mining/` adds the first bounded adapter layer. It reads the path-level
manifest, opens only approved Markdown report classes with strict caps, and
generates candidate-only review assets. Those candidates are not canonical
memory and are not approved for direct brain, memory, or CIEU use.

`backlog_disposition/` classifies every artifact in the quarantine manifest into
a routing disposition. It identifies safe-mined/reviewed items, deferred adapter
needs, generated cache, unknown classes, and forbidden direct-read groups without
opening raw artifact contents.

Relationship:

- `console_read_model/` consumes curated snapshots, not raw artifacts.
- `agent_brains/` are persistent role-brain read models.
- CIEU and future adapters should convert selected runtime evidence into
  reviewed, structured learning signals.
- Brain writeback should only happen after curation and governance-compatible
  review.
