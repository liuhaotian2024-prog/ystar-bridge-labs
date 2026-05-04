# E16X Router Consolidation Plan

- risk_tier_source: office/mission_command/e8_risk_controlled_action_model.py
- bridge_runtime_router: office/mission_command/action_authorization_router.py
- progressive_domain_source: office/mission_command/b2r_capability_domains.py
- outbound_policy_prototype: office/mission_command/e15d_ygov_outbound_policy.py

## Which router is canonical now?
action_authorization_router remains the bridge-labs action authorization entrypoint, but it is incomplete for B2R/E15D.

## Should action_authorization_router be upgraded?
yes; it should understand capability_domain, capability_level, canonical execution_mode, and E15D outbound policy reason codes.

## Should E15D policy call action_authorization_router?
yes; E15D policy should call action_authorization_router before E16C-0, so outbound policy cannot bypass the older Tier 2 safety discipline.

## Should B2R domains be source of truth?
yes for progressive capability domains inside bridge-labs until promoted to Y-star-gov policy.

## Should E8 risk model remain canonical?
yes for bridge-labs risk tiers; capability levels must not replace risk tiers.

## Tests Required Before E16C-0
- external_validation_message Level 5 maps to Tier 2 under low-volume transparent envelope
- E15D policy denies or owner-handoffs when router rejects
- mcp_execute_after_activation alias normalizes to gov_mcp_execute_after_activation
- owner approval state machine blocks send without activated envelope
- feedback fixture cannot become validation feedback or CIEU writeback
