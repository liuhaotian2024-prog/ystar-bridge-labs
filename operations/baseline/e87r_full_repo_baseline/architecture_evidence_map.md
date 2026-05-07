# E87R Architecture Evidence Map

## bridge_labs_ceo_company_runtime
- Owner: `bridge-labs`
- Status: `active_runtime_and_generated_artifact_mixture`
- Purpose: Owns company/CEO behavior center, mission command, business context, owner decision artifacts, external validation plans, and delivery reports.
- Files: `office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py`, `office/mission_command/e46b_ceo_brain_adapter.py`, `office/aiden_meeting_room/aiden_response_engine.py`, `office/aiden_meeting_room/company_context_loader.py`, `operations/external_validation/`, `scripts/repository_delivery_bridge_submit.py`
- Tests: `tests/office/test_e85_ceo_cognitive_os_runtime_bridge.py`, `tests/office/test_e86_cieu_log_insertion_point_report.py`
- Gaps: CEO intelligence remains split across generated artifacts, meeting-room code, mission_command, and reports.; A single end-to-end CEO runtime session that invokes Y-star-gov and gov-mcp from normal CEO work still needs a major closure milestone.

## Y_star_gov_governance_runtime
- Owner: `Y-star-gov`
- Status: `active_runtime`
- Purpose: Owns deterministic governance reflexes: CEO Cognitive OS contract, runtime hook, check/enforce patterns, CIEUStore persistence, pre-U validation, omission/delegation/governance loop.
- Files: `ystar/governance/ceo_cognitive_os_contract.py`, `ystar/governance/ceo_cognitive_os_runtime_hook.py`, `ystar/governance/ceo_cognitive_os_cieu_log.py`, `ystar/governance/cieu_store.py`, `ystar/governance/pre_u_packet_validator.py`, `ystar/governance/cieu_prediction_delta.py`, `ystar/governance/contract_dry_run.py`, `ystar/adapters/cieu_writer.py`
- Tests: `tests/governance/test_ceo_cognitive_os_contract.py`, `tests/governance/test_ceo_cognitive_os_runtime_hook.py`, `tests/governance/test_ceo_cognitive_os_cieu_log.py`, `tests/test_cieu_store.py`
- Gaps: Formal CIEUStore writes are explicit opt-in; no hidden runtime write by default.; Hook/check/enforce integration beyond CEO runtime wrapper still needs normal runtime-session wiring.

## gov_mcp_execution_boundary
- Owner: `gov-mcp`
- Status: `active_dry_run`
- Purpose: Owns MCP/provider/tool execution boundary, gov_check/gov_enforce tools, dry-run outbound adapter, guard stack, and no-send receipts.
- Files: `gov_mcp/server.py`, `gov_mcp/company_runtime_tools.py`, `gov_mcp/outbound/policy.py`, `gov_mcp/outbound/dry_run_adapter.py`, `gov_mcp/outbound/provider_guard_stack.py`, `gov_mcp/models.py`
- Tests: `tests/test_company_runtime_tools.py`, `tests/test_outbound_dry_run_adapter.py`, `tests/test_provider_guard_stack.py`
- Gaps: No live provider execution should be claimed from current evidence.; Owner-activated live-ready preflight and provider promotion remain future work.

## cross_repo_runtime_chain
- Owner: `shared_with_clear_owners`
- Status: `partial_runtime_chain`
- Purpose: Bridge-labs produces CEO packets; Y-star-gov validates and writes CIEUStore records; gov-mcp provides dry-run provider envelope after allow; K9Audit remains separate stronger evidence-chain boundary unless owner-approved integration is added.
- Files: `bridge-labs:office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py`, `Y-star-gov:ystar/governance/ceo_cognitive_os_runtime_hook.py`, `Y-star-gov:ystar/governance/ceo_cognitive_os_cieu_log.py`, `gov-mcp:gov_mcp/outbound/dry_run_adapter.py`, `bridge-labs:scripts/repository_delivery_bridge_submit.py`
- Tests: `bridge-labs:tests/office/test_e85_ceo_cognitive_os_runtime_bridge.py`, `Y-star-gov:tests/governance/test_ceo_cognitive_os_cieu_log.py`
- Gaps: End-to-end normal CEO session binding across all three repos is not yet one canonical runtime command.; K9Audit ledger/hash-chain is read-only reference, not integrated write path.

