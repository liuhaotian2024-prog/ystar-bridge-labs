# E16X Route Reconciliation Packet

- recommended_route: E16G_cross_repo_gov_mcp_adapter_promotion_first
- secondary_route: E16B_owner_manual_send_first
- e16c0_should_proceed: false
- e16c0_reconciliation: Delay and revise E16C-0 to dry-run only until taxonomy/router conflicts are fixed and gov-mcp owns the outbound adapter boundary.

## Decision Basis
- Risk tier/capability-level semantics need canonicalization.
- Execution mode enum needs normalization.
- Owner activation state machine needs one source of truth.
- gov-mcp does not yet own a confirmed outbound provider adapter.
- bridge-labs E15D adapter remains a prototype contract, not execution authority.

## E16B_owner_manual_send_first
- status: available_lowest_operational_risk
- trigger: owner wants first validation with no adapter dependency

## E16C0_one_action_send_gated_pilot_dry_run
- status: delay_or_revise_to_dry_run_only
- trigger: router taxonomy conflicts resolved and gov-mcp promotion plan accepted

## E16C1_owner_activated_one_action_send_gated_pilot
- status: blocked_now
- trigger: requires activated owner envelope and gov-mcp adapter implementation

## E16D_expand_evidence_before_any_send
- status: available_if_target_message_fit_weakens
- trigger: target/message evidence is insufficient or owner wants more market evidence

## E16G_cross_repo_gov_mcp_adapter_promotion_first
- status: recommended
- trigger: semantic conflicts unresolved or gov-mcp lacks outbound adapter implementation
