# E96 Controlled Capability Catalog

- controlled_capability_count: `11`
- quarantined_entrypoint_count: `30`

## Controlled Capabilities
- `owner_facing_aiden_governed_gateway`: active_runtime via `office/aiden_meeting_room/governed_gateway.py::answer_owner_governed`
- `raw_answer_owner_kernel`: internal_kernel_only via `office/aiden_meeting_room/aiden_response_engine.py::answer_owner`
- `brain_grounding_and_provenance`: active_runtime_partial_writeback via `office/mission_command/e93_brain_grounded_live_runtime.py::query_brain_for_stage`
- `ceo_behavior_center_runtime_contract`: active_runtime via `ystar/governance/ceo_behavior_center_runtime_contract.py::validate_and_write_ceo_behavior_center_runtime_packet`
- `ceo_major_action_runtime_hook`: active_runtime via `ystar/governance/ceo_cognitive_os_runtime_hook.py::validate_ceo_runtime_envelope`
- `gov_mcp_dry_run_boundary`: active_dry_run_only via `gov_mcp/outbound/dry_run_adapter.py::dry_run_outbound_action`
- `ceo_intelligence_loop_compiler`: active_structured_fixture_runtime via `office/mission_command/e89_ceo_intelligence_loop_runtime_compiler.py::run_ceo_intelligence_runtime_session`
- `ceo_market_strategy_benchmark`: active_benchmark_limited_external_grounding via `office/mission_command/e90_market_grounded_strategy_run.py::run_e90_market_grounded_strategy_session`
- `ceo_doctrine_registry`: active_but_needs_integrity_cleanup via `office/mission_command/e91_ceo_operating_doctrine_registry.py::build_ceo_operating_doctrine_registry`
- `codex_executor_boundary`: active_runtime via `office/mission_command/e92_ceo_principal_codex_executor_boundary.py::run_ceo_codex_executor_boundary_session`
- `sleep_dream_learning_candidate`: partial_isolated_write_proof via `office/mission_command/e95_behavior_center_caller_migration_and_sleep_dream_loop.py::apply_sleep_dream_learning_candidate`

## Quarantined Entrypoints
- `office/mission_command/e40_no_send_message_and_walkthrough.py`: review_required_external_surface_with_some_local_controls (auto_discovered_external_surface)
- `office/mission_command/e96_ceo_controlled_capability_control_plane.py`: review_required_external_surface_with_some_local_controls (auto_discovered_external_surface)
- `scripts/auto_commit_push.py`: review_required_external_surface_with_some_local_controls (auto_discovered_external_surface)
- `scripts/create_channel.py`: quarantined_high_risk_live_external_action (live_channel_creation_and_publication)
- `scripts/deploy_mac_cto.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/deploy_mac_cto_ssh.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/gemma_client.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/gov_order.py`: review_required_external_surface_with_some_local_controls (auto_discovered_external_surface)
- `scripts/k9.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/k9_baseline_verify.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/k9_inbox.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/k9_login.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/k9_phase1.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/k9_phase2.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/k9_phase4_baseline.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/k9_reinstall.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/k9_watch.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/linkedin_auth.py`: quarantined_high_risk_live_external_action (live_social_posting_and_login)
- `scripts/mac_command.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/mac_deploy_agents.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/meeting_room/server.py`: quarantined_until_governed_gateway_adapter (meeting_room_canned_dialogue_and_tts)
- `scripts/post_ep01.py`: quarantined_high_risk_live_external_action (live_publication)
- `scripts/post_episodes.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/publish_telegram.py`: quarantined_high_risk_live_external_action (live_publication)
- `scripts/publish_x.py`: quarantined_high_risk_live_external_action (live_publication)
- `scripts/publish_x_v2.py`: quarantined_high_risk_live_external_action (live_publication)
- `scripts/quality_compare.py`: quarantined_external_surface_no_canonical_gateway (auto_discovered_external_surface)
- `scripts/telegram_bridge.py`: quarantined_high_risk_remote_control (remote_command_bridge)
- `scripts/telegram_notify.py`: review_required_external_surface_with_some_local_controls (auto_discovered_external_surface)
- `worker.js`: quarantined_until_governed_gateway_adapter (cloud_llm_persona_responder)

## Registry Integrity
- issue_count: `1`
- `ystar_governance_runtime_reflex`: callable_path_not_found_in_bridge_labs_tree
