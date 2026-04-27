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

The snapshot can expose a backlog disposition summary derived from
`runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json`.
This covers the dirty artifact backlog as routing metadata only; it does not
perform truth scoring, adapter extraction, or ingestion.

The snapshot can expose an evidence review summary derived from
`runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json` and
related generated indexes. This summarizes structural readiness only. It is not
truth validation, approval, memory ingestion, CIEU writing, or brain writeback.

The snapshot can expose a Labs-Gov alignment bridge summary derived from
`labs_governance_bridge/generated/governance_decision_snapshot.json`. This
shows a Y-star-gov dry-run decision for a curated sample labs task. It is not
real hook integration, action execution, CIEU writing, memory ingestion, or
brain writeback.

The snapshot can expose a multi-role Pre-U governance summary derived from
`labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json`.
This covers Aiden, Ethan, and Samantha dry-run packets only. It is not runtime
packet execution or hook enforcement.

The snapshot can expose a labs runtime acceptance summary derived from
`labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json`. This
is dry-run acceptance only and does not execute actions, write CIEU, or mutate
brain/memory.

The snapshot can expose a cross-repo governance alignment summary derived from
`cross_repo_alignment/generated/cross_repo_status_manifest.json`. This shows
dry-run compatibility between ystar-company and Y-star-gov. It is not CI, push,
hook enforcement, or runtime execution.

The snapshot can expose a live-readiness summary derived from
`labs_live_readiness/generated/live_readiness_report.json`. This confirms
dry-run governance readiness while keeping live action execution, CIEU writes,
memory ingestion, and brain writeback disabled.

The snapshot can expose a live-boundary summary derived from
`labs_live_boundary/generated/live_boundary_summary.json`. This confirms the
operator approval, sandbox, rollback, CIEU writer, and no-writeback boundaries
are defined but disabled. It is not hook activation or live execution.
