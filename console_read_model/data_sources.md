# Data Sources

## Safe Curated Sources

- `actual_team_registry/*.json`
- `actual_team_registry/*.md`
- `agent_brains/**/*.json`
- `agent_brains/**/*.md`
- `agent_brain_capsule/*.md`
- `agent_brain_capsule/*.json`
- `brain_index/db_manifest.json`
- `memory_index/memory_manifest.json`
- `governance_refs/boundaries.md`
- `runtime_mechanism_inventory/mechanisms.json`
- `company_state/current_world_state_ref.md`
- `runtime_artifact_quarantine/quarantine_index.json`
- `runtime_artifact_quarantine/generated/runtime_artifact_manifest.json`
- `runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json`
- `runtime_artifact_quarantine/safe_mining/generated/mining_manifest.json`
- `runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json`
- `runtime_artifact_quarantine/safe_mining/review_queue/generated/review_queue_manifest.json`
- `runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json`
- `runtime_artifact_quarantine/backlog_disposition/generated/disposition_manifest.json`
- `runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json`
- `runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json`
- `runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json`
- `runtime_artifact_quarantine/evidence_review/generated/evidence_review_manifest.json`
- `labs_governance_bridge/generated/sample_hook_envelope.json`
- `labs_governance_bridge/generated/governance_decision_snapshot.json`
- `labs_governance_bridge/generated/bridge_run_manifest.json`
- `labs_governance_bridge/pre_u_generator/generated/pre_u_packet_manifest.json`
- `labs_governance_bridge/pre_u_generator/generated/hook_envelope_manifest.json`
- `labs_governance_bridge/pre_u_generator/generated/governance_decision_snapshots.json`
- `labs_governance_bridge/pre_u_generator/generated/pre_u_governance_run_manifest.json`
- `labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json`
- `labs_runtime_acceptance/generated/labs_runtime_acceptance_manifest.json`
- `console_read_model/generated/quarantine_summary.json`
- `console_read_model/generated/safe_mining_summary.json`
- `console_read_model/generated/review_queue_summary.json`
- `console_read_model/generated/artifact_disposition_summary.json`
- `console_read_model/generated/evidence_review_summary.json`
- `console_read_model/generated/governance_bridge_summary.json`
- `console_read_model/generated/pre_u_governance_summary.json`
- `console_read_model/generated/labs_acceptance_summary.json`

## Unsafe Direct Sources

- `*.db`
- `*.db-wal`
- `*.db-shm`
- `scripts/.logs/*`
- Active-agent markers.
- Daemon pid/state files.
- `__pycache__`.
- Raw runtime reports unless curated/indexed.

## Rules

- DBs may be referenced by manifest only.
- Logs may be summarized only through future safe adapters.
- Console must not mutate anything.
- Console should never treat raw runtime state as canonical memory.
- Console should prefer curated read models over direct operational stores.
- Runtime artifact quarantine data may be displayed only as path-level
  summaries/classes/counts until future safe adapters exist.
- Safe-mining candidate data may be displayed only from generated candidate
  indexes; candidates are not canonical memory and require review.
- Review queue data may be displayed only from generated queue indexes; entries
  are pending decisions, not approvals or ingestion.
- Backlog disposition data may be displayed only from generated disposition
  indexes; disposition is routing metadata, not evidence scoring or ingestion.
- Evidence review data may be displayed only from generated evidence indexes;
  scoring is structural only and decisions remain undecided.
- Labs-Gov bridge data may be displayed only from generated bridge snapshots;
  bridge decisions are dry-run only and must not execute actions or write CIEU.
- Pre-U governance data may be displayed only from generated dry-run packet
  decision snapshots; generated packets are not runtime actions.
- Labs runtime acceptance data may be displayed only from generated acceptance
  reports; acceptance is dry-run only and not runtime execution.
