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

`console_read_model/loader/` contains a static snapshot generator that compiles
these curated inputs into `console_read_model/generated/` for future UI/runtime
consumers. The generated files are derived artifacts, not live runtime state.

`console_read_model/cli/` contains a read-only command-line entry point that
prints summaries from generated snapshots only. It does not read raw runtime
state or call subprocesses.

`console_read_model/checks/` contains a local safety wrapper that runs the safe
manifest, snapshot, JSON, validator, and CLI smoke checks in one command. It is
not CI and does not inspect dirty runtime artifacts directly.

The console snapshot also includes a runtime artifact quarantine summary derived
from `runtime_artifact_quarantine/generated/runtime_artifact_manifest.json`.
That summary is path-level only: it exposes classes and counts, not artifact
contents, and it does not implement mining or ingestion.

The snapshot can also expose a safe-mining candidate summary derived from
`runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json`.
This is still a curated generated source: the console does not open raw reports,
and candidates remain review assets rather than brain memory or CIEU records.

The snapshot can expose a candidate review queue summary derived from
`runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json`.
This summarizes pending review state only. Queue entries are not approved,
ingested, or canonical.
