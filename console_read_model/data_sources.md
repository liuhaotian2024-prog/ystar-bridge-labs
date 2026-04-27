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
- `cross_repo_alignment/generated/cross_repo_status_manifest.json`
- `cross_repo_alignment/generated/cross_repo_alignment_summary.json`
- `labs_live_readiness/generated/live_readiness_report.json`
- `labs_live_readiness/generated/transition_backlog.json`
- `labs_live_readiness/generated/live_readiness_manifest.json`
- `labs_live_boundary/generated/live_boundary_manifest.json`
- `labs_live_boundary/generated/live_boundary_summary.json`
- `labs_live_boundary/generated/live_transition_checklist.json`
- `labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_manifest.json`
- `labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_summary.json`
- `labs_cieu_runtime_boundary/generated/sample_cieu_runtime_event.json`
- `labs_cieu_runtime_boundary/generated/sample_prediction_delta_fixture.json`
- `company_autonomy_inventory/generated/repo_discovery_manifest.json`
- `company_autonomy_inventory/generated/existing_asset_inventory.json`
- `company_autonomy_inventory/generated/observation_capability_map.json`
- `company_autonomy_inventory/generated/resource_sensing_map.json`
- `company_autonomy_inventory/generated/action_capability_map.json`
- `company_autonomy_inventory/generated/governed_tool_registry_candidates.json`
- `company_autonomy_inventory/generated/agent_role_capability_matrix.json`
- `company_autonomy_inventory/generated/company_autonomy_readiness_summary.json`
- `company_autonomy_inventory/generated/inventory_size_guard.json`
- `company_autonomous_work_cycle/generated/mission_profile.json`
- `company_autonomous_work_cycle/generated/company_observation_snapshot.json`
- `company_autonomous_work_cycle/generated/autonomous_work_backlog.json`
- `company_autonomous_work_cycle/generated/selected_work_item.json`
- `company_autonomous_work_cycle/generated/role_delegation_plan.json`
- `company_autonomous_work_cycle/generated/governed_tool_selection.json`
- `company_autonomous_work_cycle/generated/pre_u_packet_simulation.json`
- `company_autonomous_work_cycle/generated/governance_decision_simulation.json`
- `company_autonomous_work_cycle/generated/simulated_action_plan.json`
- `company_autonomous_work_cycle/generated/simulated_cieu_event.json`
- `company_autonomous_work_cycle/generated/residual_delta_simulation.json`
- `company_autonomous_work_cycle/generated/next_task_recommendations.json`
- `company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json`
- `console_read_model/generated/quarantine_summary.json`
- `console_read_model/generated/safe_mining_summary.json`
- `console_read_model/generated/review_queue_summary.json`
- `console_read_model/generated/artifact_disposition_summary.json`
- `console_read_model/generated/evidence_review_summary.json`
- `console_read_model/generated/governance_bridge_summary.json`
- `console_read_model/generated/pre_u_governance_summary.json`
- `console_read_model/generated/labs_acceptance_summary.json`
- `console_read_model/generated/cross_repo_alignment_summary.json`
- `console_read_model/generated/live_readiness_summary.json`
- `console_read_model/generated/live_boundary_summary.json`
- `console_read_model/generated/cieu_boundary_summary.json`
- `console_read_model/generated/autonomy_inventory_summary.json`
- `console_read_model/generated/autonomous_cycle_summary.json`

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
- Cross-repo alignment data may be displayed only from generated alignment
  manifests; alignment is dry-run compatibility only and not CI or hook execution.
- Live-readiness data may be displayed only from generated gate reports; live
  action execution, CIEU writes, memory ingestion, and brain writeback remain
  forbidden.
- Live-boundary data may be displayed only from generated boundary summaries;
  boundary contracts are defined but disabled and require manual enablement.
- CIEU runtime boundary data may be displayed only from generated boundary
  summaries and fixtures; persistence and writeback remain disabled.
- Company autonomy inventory data may be displayed only from generated inventory
  maps and summaries; governed tool candidates remain disabled and require
  future wrappers, approval, Y-star-gov checks, rollback policy, and CIEU events
  before any live action.
- Autonomous work cycle data may be displayed only from generated simulator
  outputs; it is not live execution, tool invocation, CIEU persistence, memory
  ingestion, or brain writeback.
