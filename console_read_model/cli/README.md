# Team Console CLI

`team_console.py` is a read-only CLI for the generated team console snapshot.

It reads only:

- `console_read_model/generated/team_console_snapshot.json`
- `console_read_model/generated/agent_cards_compiled.json`
- `console_read_model/generated/readiness_summary.json`
- `console_read_model/generated/quarantine_summary.json`
- `console_read_model/generated/safe_mining_summary.json`
- `console_read_model/generated/review_queue_summary.json`
- `console_read_model/generated/artifact_disposition_summary.json`
- `console_read_model/generated/evidence_review_summary.json`
- `console_read_model/generated/governance_bridge_summary.json`
- `console_read_model/generated/pre_u_governance_summary.json`
- `console_read_model/generated/generation_manifest.json`

It does not read DBs, logs, active-agent markers, daemon state, raw runtime
reports, or live memory. It does not write files or run subprocesses.

Example commands:

```bash
python3 console_read_model/cli/team_console.py summary
python3 console_read_model/cli/team_console.py agents
python3 console_read_model/cli/team_console.py agent Ethan-CTO
python3 console_read_model/cli/team_console.py readiness
python3 console_read_model/cli/team_console.py quarantine
python3 console_read_model/cli/team_console.py mining-candidates
python3 console_read_model/cli/team_console.py review-queue
python3 console_read_model/cli/team_console.py artifact-disposition
python3 console_read_model/cli/team_console.py evidence-review
python3 console_read_model/cli/team_console.py governance-bridge
python3 console_read_model/cli/team_console.py pre-u-governance
python3 console_read_model/cli/team_console.py validate-local
```

This is the first user-facing operational entry point, but it remains strictly
snapshot-based and read-only.

The `quarantine` command displays only the generated path-level quarantine
summary. It does not read runtime artifacts, logs, DBs, active-agent markers, or
daemon state directly.

The `mining-candidates` command displays only the generated safe-mining summary.
It does not open raw reports. Candidate snippets remain review assets and are
not brain memory, CIEU records, or writeback approval.

The `review-queue` command displays only the generated candidate review queue
summary. Entries remain pending review and not ingested.

The `artifact-disposition` command displays only the generated backlog
disposition summary. Disposition is routing metadata, not ingestion.

The `evidence-review` command displays only the generated evidence review
summary. Evidence scoring is structural only and does not approve candidates.

The `governance-bridge` command displays only the generated Labs-Gov bridge
summary. The bridge calls Y-star-gov dry-run judgment upstream, but the console
itself remains read-only and does not execute actions.

The `pre-u-governance` command displays only the generated multi-role Pre-U
governance summary. Packets are dry-run artifacts and are not runtime actions.
