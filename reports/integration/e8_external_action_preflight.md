# E8 External Action Preflight

- action_id: e8_action_001
- action_type: send_validation_message
- risk_tier: TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION
- allowed: False
- review_gated: False
- blocked: True
- manifest_status: invalid_or_missing
- target_status: invalid_or_missing
- draft_status: valid
- transparency_status: valid
- autonomy_budget_status: invalid_or_missing
- governance_status: blocked_or_review_gated
- blocked_reason: manifest_invalid_or_missing, target_invalid_or_missing

## Exact Unblock Action
- Provide a valid manifest, target seed, frozen draft hash, AI disclosure, and stop conditions before any E8 external action.
