# E81 Cognitive OS Enforcement Fixture Results

- Valid packet allowed: True
- Invalid packets denied: True

| fixture | decision | failed_stage | reason |
| --- | --- | --- | --- |
| valid_full_packet | ALLOW |  | pre-action packet satisfies bridge-labs pre-sync cognitive OS validator |
| invalid_recent_memory_only | DENY | full_capability_inventory_recall | recent-memory-only reasoning is blocked |
| invalid_no_counterfactual | DENY | counterfactual_action_comparison | counterfactual comparison requires at least two candidate actions |
| invalid_no_pre_action_cieu_prediction | DENY | pre_action_CIEU_residual_prediction | missing pre-action CIEU prediction |
| invalid_no_adversarial_critique | DENY | adversarial_critique | missing adversarial critique |
| invalid_construction_without_no_new_wheel | DENY | no_new_wheel_gate | construction recommendation missing no-new-wheel proof |
| invalid_L4_without_owner_approval | DENY | owner_approval_gate | L4/external execution requires explicit owner approval |
| invalid_unverified_runtime_active_capability | DENY | repository_evidence | unverified runtime-active capability claim: cap_fake_runtime_brain |
| invalid_forbidden_customer_paid_compliance_claim | DENY | overclaim_boundary | forbidden claim present: customer_validation_claim |
