# Tool CIEU Event Policy

The wrapper emits a dry-run CIEU-compatible event envelope so the future learning loop has an event shape to validate.

The generated event is not persisted to a CIEU database or store. It is a local JSON fixture only.

Required disabled flags:

- `dry_run_only: true`
- `persistence_enabled: false`
- `learning_eligibility: false`
- `direct_brain_writeback_allowed: false`
- `direct_memory_ingestion_allowed: false`
- `raw_artifact_ingestion_allowed: false`

Future milestones may route a governed tool invocation through a Pre-U bridge, but that must still keep live execution and persistence disabled until explicit live gates exist.

