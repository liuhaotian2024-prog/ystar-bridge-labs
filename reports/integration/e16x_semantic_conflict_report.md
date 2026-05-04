# E16X Semantic Conflict Report

## risk_tier_vs_capability_level
- severity: high
- conflict: E8 uses TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION for validation messages, action_authorization_router only allows Tier 2, while B2R/E15D language can look like capability level 5 / Tier 5.
- canonical_resolution: Risk tier and capability level are separate. B2R Level 5 external_validation_message maps to risk_tier TIER_2 when it is low-volume, AI-transparent, non-binding validation messaging.
- blocking_for_real_send: true

## execution_mode_enum
- severity: medium
- conflict: C2 modes prepare_only/owner_handoff/dry_run_local/pending_owner_approval/mcp_execute_after_activation overlap E15D modes draft_only/owner_handoff/send_gated_pending_authorization/send_gated_dry_run/gov_mcp_execute_after_activation.
- canonical_resolution: Use one enum: deny, prepare_only, draft_only, owner_handoff, dry_run_local, send_gated_pending_authorization, send_gated_dry_run, gov_mcp_execute_after_activation. Treat mcp_execute_after_activation as deprecated alias.
- blocking_for_real_send: true

## owner_approval_state_machine
- severity: medium
- conflict: owner_handoff, owner_review_required, activated envelope, authorization envelope, owner approval present, and constitutional hard gate are used as overlapping states.
- canonical_resolution: Adopt state machine: proposed -> owner_review_required -> activated | rejected | revoked | expired, with constitutional_hard_gate_escalated as separate terminal escalation.
- blocking_for_real_send: true

## feedback_semantics
- severity: high
- conflict: Public evidence, owner-reported feedback, customer response, signal fixtures, and CIEU writeback candidates risk being mixed.
- canonical_resolution: Public evidence is not validation feedback. Fixtures are not actual feedback events. Only owner-confirmed external action plus valid customer/owner-recorded response can become validation feedback; CIEU writeback remains candidate until Y-star-gov eligibility passes.
- blocking_for_real_send: false

## gov_mcp_boundary
- severity: high
- conflict: bridge-labs defines gov-mcp outbound adapter contract, but gov-mcp currently exposes governance/check/enforce surfaces and deterministic execution rather than a real outbound provider adapter.
- canonical_resolution: E15D adapter stays prototype in bridge-labs until a gov-mcp promotion PR implements outbound dry-run/preflight/receipt schemas and tests. No real send-gated pilot should depend on bridge-labs-only adapter logic.
- blocking_for_real_send: true
