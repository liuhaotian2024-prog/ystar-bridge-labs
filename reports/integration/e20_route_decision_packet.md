# E20 Route Decision Packet

- recommended_route: prepare_E21_autonomous_provider_adapter_plan
- reason: Low-risk autonomous execution is policy-eligible for several candidates, but live provider capability is missing.
- real_external_action_executed: false

## Summary Counts
- agent_autonomous_allowed: 0
- agent_autonomous_allowed_with_limits: 0
- owner_approval_required: 0
- owner_manual_only: 0
- blocked_no_go: 0
- provider_capability_missing: 5
- evidence_required_before_execution: 2

## Route Options
- build_real_provider_adapter_for_low_risk_autonomous_send: Future gov-mcp milestone if owner wants live autonomous sends.
- run_autonomous_dry_run_batch_first: Allowed locally with no provider call.
- revise_messages_before_autonomous_send: Use if message variants are weak.
- expand_target_evidence_before_autonomous_send: Use for evidence_required candidates.
- owner_approval_required_for_high_risk_only: Owner gates exceptional risk, not normal low-risk send.
- keep_high_risk_actions_blocked: T4/T5 remain gated or blocked.
- resolve_gov_mcp_provider_gap: Implement live provider adapter and tests in gov-mcp.
- prepare_E21_autonomous_provider_adapter_plan: Recommended next step.
