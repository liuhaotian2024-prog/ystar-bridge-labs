# L7.0Q2 Summary

```json
{
  "schema_version": "v0",
  "milestone_id": "L7.0Q2",
  "milestone_name": "Full-Repository Conservatism Debt Scan & Policy Migration Map",
  "total_tracked_files_scanned": 42041,
  "total_text_files_scanned": 41053,
  "total_findings": 129682,
  "findings_by_severity": {
    "P0": 82,
    "P1": 2014,
    "P2": 44768,
    "P3": 82818
  },
  "findings_by_classification": {
    "console_read_model_overconservative": 7371,
    "core_writeback_overblocked": 255,
    "disabled_as_final_state": 813,
    "documentation_overconservative": 14990,
    "external_action_overblocked": 863,
    "fixture_only_regression": 104,
    "generated_artifact_overconservative": 4676,
    "hardcoded_blacklist": 263,
    "hardcoded_forbidden_action_list": 7508,
    "legitimate_hard_boundary": 56285,
    "no_action_receipt_overuse": 689,
    "owner_manual_burden": 165,
    "policy_registry_needed": 1,
    "policy_registry_present": 2261,
    "readiness_or_preflight_overuse": 3393,
    "runtime_visibility_overblocked": 25439,
    "test_expectation_overconservative": 4606
  },
  "findings_by_artifact_epoch": {
    "console_read_model": 9401,
    "docs": 52500,
    "generated": 5535,
    "l5": 35,
    "l6_early": 2701,
    "l6_observation": 9764,
    "l6_review_strategy": 1801,
    "l7_commercial": 1450,
    "policy": 228,
    "scripts": 3503,
    "tests": 5400,
    "unknown": 37364
  },
  "harmful_overconservatism_count": 71136,
  "legitimate_hard_boundary_count": 56285,
  "policy_registry_coverage_percentage": 1.78,
  "files_needing_policy_ref_migration": 38369,
  "p0_migration_targets": [
    {
      "file_path": "scripts/aiden_dream.py",
      "migration_priority": "P0",
      "current_pattern": "disabled",
      "target_policy_ref": "policy/action_capability_registry.json",
      "recommended_patch_type": "convert_disabled_to_auto_detect",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "activation path"
    },
    {
      "file_path": "scripts/hook_wrapper.py",
      "migration_priority": "P0",
      "current_pattern": "disabled",
      "target_policy_ref": "policy/action_capability_registry.json",
      "recommended_patch_type": "convert_disabled_to_auto_detect",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "activation path"
    },
    {
      "file_path": "scripts/session_health_watchdog.py",
      "migration_priority": "P0",
      "current_pattern": "disabled",
      "target_policy_ref": "policy/action_capability_registry.json",
      "recommended_patch_type": "convert_disabled_to_auto_detect",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "activation path"
    },
    {
      "file_path": "scripts/tests/test_behavior_gov_engine.py",
      "migration_priority": "P0",
      "current_pattern": "disabled",
      "target_policy_ref": "policy/action_capability_registry.json",
      "recommended_patch_type": "convert_disabled_to_auto_detect",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "activation path"
    },
    {
      "file_path": "l6_real_controlled_external_observation_mission_sprint/l6_13_generation_manifest.json",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    },
    {
      "file_path": "controlled_no_action_receipts/no_side_effect_receipt.json",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    },
    {
      "file_path": "controlled_no_action_receipts/no_action_receipt_index.json",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    },
    {
      "file_path": "scripts/governance_boot.sh",
      "migration_priority": "P0",
      "current_pattern": "disabled",
      "target_policy_ref": "policy/action_capability_registry.json",
      "recommended_patch_type": "convert_disabled_to_auto_detect",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "activation path"
    },
    {
      "file_path": "scripts/memory_consistency_check.py",
      "migration_priority": "P0",
      "current_pattern": "not_configured",
      "target_policy_ref": "policy/action_capability_registry.json",
      "recommended_patch_type": "convert_disabled_to_auto_detect",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "activation path"
    },
    {
      "file_path": "scripts/linkedin_auth.py",
      "migration_priority": "P0",
      "current_pattern": "disabled",
      "target_policy_ref": "policy/action_capability_registry.json",
      "recommended_patch_type": "convert_disabled_to_auto_detect",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "activation path"
    },
    {
      "file_path": "ceo_command_brief/l6_16_ceo_command_brief.json",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    },
    {
      "file_path": "real_no_action_receipts/no_side_effect_receipt.json",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    },
    {
      "file_path": "l6_15_no_action_receipts/no_side_effect_receipt.json",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    },
    {
      "file_path": "scripts/platform_wave1_livefire_20260424.md",
      "migration_priority": "P0",
      "current_pattern": "disabled",
      "target_policy_ref": "policy/action_capability_registry.json",
      "recommended_patch_type": "convert_disabled_to_auto_detect",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "activation path"
    },
    {
      "file_path": "internal_strategy_memo/l6_16_internal_strategy_memo.json",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    },
    {
      "file_path": "decision_boundary_packet/decision_boundary_packet.json",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    },
    {
      "file_path": "l6_human_review_decision_boundary_sprint/l6_15_scope.json",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    },
    {
      "file_path": "l6_16_no_action_receipts/no_action_receipt_report.md",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    },
    {
      "file_path": "internal_strategy_memo/l6_16_internal_strategy_memo.md",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    },
    {
      "file_path": "l6_14_no_action_receipts/no_side_effect_receipt.json",
      "migration_priority": "P0",
      "current_pattern": "ask_user_url",
      "target_policy_ref": "policy/owner_burden_reduction_policy.json",
      "recommended_patch_type": "replace_user_manual_step_with_launcher",
      "risk_of_patch": "medium",
      "suggested_milestone": "L7.0Q2-p0-migration",
      "expected_capability_gain": "owner automation"
    }
  ],
  "first_patch_applied": true,
  "first_patch_description": "L7.0P status output now references the staged policy registry; L7.0P artifacts already carry L7.0Q policy refs.",
  "ask_user_for_url_occurred": false,
  "external_side_effects_occurred": false,
  "core_writeback_occurred": false,
  "secret_values_serialized": false,
  "y_star_gov_modified": false,
  "gov_mcp_modified": false,
  "db_log_wal_shm_active_agent_marker_content_read": false
}
```
