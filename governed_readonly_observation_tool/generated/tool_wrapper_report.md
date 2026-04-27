# Governed Read-Only Observation Tool Report

tool_contract_defined: True
allowed_source_registry_defined: True
sample_result_defined: True
unsafe_invocation_rejected: True
local_readonly_dry_run_callable: True
first_governed_tool_wrapper_created: True

## Source Registry

- source_count: 11
- mission-dashboard: governed_observation_loop/generated/mission_dashboard_snapshot.json
- company-state-digest: governed_observation_loop/generated/company_state_digest.json
- observation-loop-summary: governed_observation_loop/generated/governed_observation_loop_summary.json
- legacy-triage-summary: legacy_asset_triage/generated/legacy_asset_triage_summary.json
- top-absorption-candidates: legacy_asset_triage/generated/top_absorption_candidates.json
- autonomous-cycle-summary: company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json
- autonomy-inventory-summary: company_autonomy_inventory/generated/company_autonomy_readiness_summary.json
- live-readiness-report: labs_live_readiness/generated/live_readiness_report.json
- live-boundary-summary: labs_live_boundary/generated/live_boundary_summary.json
- cieu-boundary-summary: labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_summary.json
- team-console-snapshot: console_read_model/generated/team_console_snapshot.json

## Sample Result

- status: success
- read_sources: 8
- real_action_executed: False
- external_action_executed: False
- live_action_enabled: False
- cieu_persistence_enabled: False
- brain_writeback_enabled: False
- memory_ingestion_enabled: False

Next required milestone: L4.5 Governed Tool Invocation Through Pre-U Bridge v0

Warning: Read-only wrapper is callable locally, but live execution and persistence remain disabled.
