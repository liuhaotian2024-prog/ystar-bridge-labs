# Generated Console Snapshots

These files are derived artifacts from curated read-model inputs only.
They do not contain DB contents, raw logs, daemon state, active-agent state,
or live runtime observations.

`quarantine_summary.json` is derived from the runtime artifact quarantine
path-only manifest. It summarizes classes/counts only and does not include
artifact contents.

`safe_mining_summary.json` is derived from bounded Markdown report candidate
indexes. It summarizes candidate counts/classes only; candidates remain
review assets, not brain memory.

`review_queue_summary.json` is derived from generated review queue files.
It summarizes pending review state only; entries are not approved or ingested.

`artifact_disposition_summary.json` is derived from generated backlog
disposition indexes. It summarizes routing/disposition only; it is not ingestion.

`evidence_review_summary.json` is derived from generated evidence review
indexes. It summarizes structural readiness only; it is not approval.

`governance_bridge_summary.json` is derived from the generated Labs-Gov
dry-run decision snapshot. It is not hook execution or CIEU writeback.

`pre_u_governance_summary.json` is derived from generated multi-role
Pre-U dry-run decisions. It is not runtime packet execution.

`labs_acceptance_summary.json` is derived from the generated labs runtime
acceptance report. It is dry-run acceptance only, not runtime execution.

`cross_repo_alignment_summary.json` is derived from the generated cross-repo
alignment manifest. It is dry-run compatibility only, not CI or hook execution.

`live_readiness_summary.json` is derived from the generated live-readiness
report. It identifies blockers and keeps live execution disabled.

`console_read_model/cli/team_console.py` consumes these generated files as its
only data source.
