# E80 CEO Online Cognition Loop Spec

This is an orchestration loop over discovered capabilities, not a new CEO brain.
- Stage count: 16

| stage | status | failure rule |
| --- | --- | --- |
| mission_and_owner_constraint_recall | context_bound_from_repository_evidence | fail_if_stage_uses_prompt_memory_without_repository_evidence |
| full_capability_inventory_recall | context_bound_from_repository_evidence | fail_if_stage_uses_prompt_memory_without_repository_evidence |
| relevant_historical_asset_retrieval | context_bound_from_repository_evidence | fail_if_stage_uses_prompt_memory_without_repository_evidence |
| current_problem_classification | runtime_active_or_adapter_active | fail_if_stage_uses_prompt_memory_without_repository_evidence |
| canonical_owner_selection | context_bound_from_repository_evidence | fail_if_stage_uses_prompt_memory_without_repository_evidence |
| existing_module_reuse_extend_wrap_create_new_decision | runtime_active_or_adapter_active | fail_if_stage_uses_prompt_memory_without_repository_evidence |
| long_memory_KG_brain_recall_if_evidence_supported | context_bound_from_repository_evidence | fail_if_stage_uses_prompt_memory_without_repository_evidence |
| field_dimensional_reasoning_if_evidence_supported | context_bound_from_repository_evidence | fail_if_stage_uses_prompt_memory_without_repository_evidence |
| thesis_generation | context_bound_from_repository_evidence | fail_if_buyer_pain_trigger_and_tradeoff_are_generic |
| counterfactual_action_comparison | runtime_active_or_adapter_active | fail_if_only_one_path_is_considered |
| pre_action_CIEU_residual_prediction | context_bound_from_repository_evidence | fail_if_action_selected_without_X_U_Y_star_Y_next_R_prediction |
| adversarial_critique | context_bound_from_repository_evidence | fail_if_stage_uses_prompt_memory_without_repository_evidence |
| commercial_sharpness_gate | context_bound_from_repository_evidence | fail_if_buyer_pain_trigger_and_tradeoff_are_generic |
| no_new_wheel_gate | context_bound_from_repository_evidence | fail_if_bridge_labs_reimplements_K9_Y_star_gov_or_gov_mcp_core |
| decision | context_bound_from_repository_evidence | fail_if_stage_uses_prompt_memory_without_repository_evidence |
| post_action_CIEU_residual_and_learning_update | context_bound_from_repository_evidence | fail_if_action_selected_without_X_U_Y_star_Y_next_R_prediction |
