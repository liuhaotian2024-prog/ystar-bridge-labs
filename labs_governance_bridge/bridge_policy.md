# Bridge Policy

The labs-governance bridge may read only curated labs files and generated
review artifacts. It may call only the Y-star-gov hook contract dry-run CLI.

Allowed inputs:

- `labs_governance_bridge/samples/sample_labs_task.json`
- `agent_brains/Aiden-CEO/brain_profile.json`
- `runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json`
- generated bridge envelope files

Allowed outputs:

- generated hook-like envelope JSON
- generated bridge manifest JSON
- generated governance decision snapshot JSON and Markdown

Forbidden behavior:

- executing `selected_U`
- running daemon, hook, runtime, or agent scripts
- reading DB, WAL, SHM, raw logs, active-agent markers, or daemon state
- writing CIEU records
- mutating brain or memory
- approving evidence review candidates
- performing semantic truth scoring
