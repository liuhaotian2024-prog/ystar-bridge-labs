# Console Read Model

`console_read_model/` is the future safe read layer for UI/runtime consumers.

It reads curated capsule, schema, and index files. It must not read DBs, logs,
active-agent markers, daemon output, or mutable runtime state directly.

This directory summarizes:

- Agents and their role-brain capsules.
- Team capabilities.
- Runtime readiness.
- Governance links.
- Safe and unsafe data sources.
- Known gaps.

This is not a frontend, not runtime execution, not a validator implementation,
and not DB ingestion. Future console work should consume these curated read-model
files first and only use raw stores through later reviewed safe adapters.
