# Generator Policy

The Pre-U generator may read only curated role task envelopes, role-brain
profile JSON, and generated evidence hint routing files.

Allowed reads:

- `labs_governance_bridge/pre_u_generator/samples/*.json`
- `agent_brains/*/brain_profile.json`
- `runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json`

Allowed writes:

- generated Pre-U packet JSON
- generated hook envelope JSON
- generated governance decision snapshot JSON and Markdown
- generated manifests and summaries

Forbidden behavior:

- executing candidate actions
- calling daemon, hook, runtime, or agent scripts
- reading DB, WAL, SHM, raw logs, active-agent markers, or daemon state
- writing CIEU records
- mutating brain or memory
- approving candidates
- semantic truth scoring
