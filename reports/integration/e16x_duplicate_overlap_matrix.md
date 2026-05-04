# E16X Duplicate / Overlap Matrix

## e8_risk_model_vs_b2r_capability_domains
- duplicate_type: intentional_evolution
- risk_level: medium
- conflict_summary: E8 defines risk tiers; B2R defines progressive capability levels. Treating B2R level 5 as risk tier 5 would incorrectly over-risk low-volume transparent validation messages.
- recommended_resolution: Keep E8 risk tiers canonical for action risk. Keep B2R as capability maturity taxonomy and map low-risk validation messaging to E8 Tier 2.
- files:
- office/mission_command/e8_risk_controlled_action_model.py
- office/mission_command/b2r_capability_domains.py

## e8_preflight_vs_action_authorization_router
- duplicate_type: old_router_needs_upgrade
- risk_level: medium
- conflict_summary: Preflight and router both gate external actions but router does not fully understand later capability domains.
- recommended_resolution: Upgrade action_authorization_router to call canonical risk tier mapping and capability-domain checks.
- files:
- office/mission_command/e8_external_action_preflight.py
- office/mission_command/action_authorization_router.py

## action_authorization_router_vs_c2_decision_control
- duplicate_type: harmful_parallel_logic
- risk_level: high
- conflict_summary: C2 introduced deterministic decision/control envelopes parallel to the older router.
- recommended_resolution: Make C2/E15D policy call the router or promote router vocabulary so one allow/deny source exists before real E16C.
- files:
- office/mission_command/action_authorization_router.py
- office/mission_command/c2_ygov_action_decision.py
- office/mission_command/c2_gov_mcp_execution_control.py

## b2r_gov_mcp_contract_vs_c2_execution_control
- duplicate_type: intentional_evolution
- risk_level: medium
- conflict_summary: B2R declares gateway contract; C2 turns it into execution modes.
- recommended_resolution: Fold both into a canonical gov-mcp execution contract proposal and promote to gov-mcp.
- files:
- office/mission_command/b2r_gov_mcp_execution_contract.py
- office/mission_command/c2_gov_mcp_execution_control.py

## c2_c3_e15a_feedback_vs_e12_e14_feedback
- duplicate_type: harmful_parallel_logic
- risk_level: high
- conflict_summary: Readiness fixtures, owner-reported feedback, and actual customer responses can be confused if schemas remain parallel.
- recommended_resolution: Use E12/E14 feedback event schema as canonical validation feedback and mark C2/C3/E15A fixtures as pre-feedback templates until owner/customer evidence exists.
- files:
- office/mission_command/e12_feedback_capture.py
- office/mission_command/e12_signal_evaluator.py
- office/mission_command/e14_feedback_events.py
- office/mission_command/c2_feedback_loop.py
- office/mission_command/c3_feedback_intake_runtime.py
- office/mission_command/e15a_feedback_signal_evaluator.py

## e15d_outbound_policy_vs_b2r_external_validation_message_domain
- duplicate_type: canonical_candidate
- risk_level: medium
- conflict_summary: B2R defines domain; E15D defines policy and queues for the same outbound validation space.
- recommended_resolution: Keep B2R domain as capability definition and E15D as pilot policy implementation after router alignment.
- files:
- office/mission_command/b2r_external_validation_messaging.py
- office/mission_command/e15d_ygov_outbound_policy.py

## e15d_adapter_contract_vs_real_gov_mcp_surface
- duplicate_type: harmful_parallel_logic
- risk_level: high
- conflict_summary: bridge-labs defines a future gov-mcp outbound adapter, but gov-mcp currently exposes governance tools and deterministic execution, not a real outbound provider adapter.
- recommended_resolution: Do not proceed to real send-gated pilot until gov-mcp owns and tests the outbound adapter interface.
- files:
- office/mission_command/e15d_gov_mcp_outbound_adapter.py
- gov_mcp/server.py
- gov_mcp/router.py
- gov_mcp/README.md

## e15d_safety_guards_vs_e9_suppression_e8_stop_conditions
- duplicate_type: old_router_needs_upgrade
- risk_level: medium
- conflict_summary: Kill-switch/rate-limit/suppression logic overlaps with earlier suppression and execution gates.
- recommended_resolution: Make suppression registry and E8 stop conditions canonical guard inputs for E15D outbound safety.
- files:
- office/mission_command/e15d_outbound_safety_guards.py
- office/mission_command/e9_suppression_registry.py
- office/mission_command/e8_execution_gate.py

## e15d_send_gated_queue_vs_e15a_owner_console
- duplicate_type: intentional_evolution
- risk_level: low
- conflict_summary: E15D queue derives from E15A owner console to reduce owner manual burden.
- recommended_resolution: Keep derivation explicit; do not let queue execute until gov-mcp adapter and owner authorization exist.
- files:
- office/mission_command/e15a_owner_execution_console.py
- office/mission_command/e15d_send_gated_pilot_queue.py
