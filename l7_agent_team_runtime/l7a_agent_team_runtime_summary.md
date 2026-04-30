# L7A Agent Team Runtime

```json
{
  "schema_version": "v0",
  "milestone_id": "L7.0P",
  "lane_id": "L7A",
  "lane_name": "Agent Team Runtime",
  "output_dir": "l7_agent_team_runtime",
  "status": "complete",
  "artifacts": [
    "l7_agent_team_runtime/agent_role_profiles/ceo.json",
    "l7_agent_team_runtime/agent_role_profiles/researcher.json",
    "l7_agent_team_runtime/agent_role_profiles/operator_coo.json",
    "l7_agent_team_runtime/agent_role_profiles/engineer_cto.json",
    "l7_agent_team_runtime/agent_role_profiles/secretary.json",
    "l7_agent_team_runtime/agent_role_profiles/auditor.json",
    "l7_agent_team_runtime/agent_role_profiles/revenue_scout.json",
    "l7_agent_team_runtime/agent_responsibility_boundaries/boundary_matrix.json",
    "l7_agent_team_runtime/agent_work_order_inboxes/inbox_index.json",
    "l7_agent_team_runtime/agent_handoff_packets/handoff_packet_schema.json",
    "l7_agent_team_runtime/agent_reporting_lines/team_orchestration_manifest.json",
    "l7_agent_team_runtime/agent_status_snapshots/l7a_agent_team_status.json",
    "l7_agent_team_runtime/agent_team_no_action_receipts/no_action_receipt.json"
  ],
  "next_safe_step": "assign read-only commercial work orders to role-specific inboxes",
  "external_actions_blocked": true,
  "core_writebacks_blocked": true,
  "ask_user_for_url_occurred": false,
  "external_side_effects_occurred": false,
  "core_writeback_occurred": false,
  "secret_values_serialized": false,
  "required_agents": [
    "CEO",
    "Researcher",
    "Operator/COO",
    "Engineer/CTO",
    "Secretary",
    "Auditor",
    "Revenue Scout"
  ],
  "agent_count": 7,
  "l7_0q_policy_migration": {
    "policy_ref": "policy/action_capability_registry.json",
    "action_capability_policy_ref": "policy/action_capability_registry.json",
    "approval_state_machine_ref": "policy/approval_state_machine.json",
    "revenue_policy_ref": "policy/revenue_action_policy.json",
    "discovery_policy_ref": "policy/discovery_policy.json",
    "runtime_access_policy_ref": "policy/runtime_access_policy.json",
    "writeback_policy_ref": "policy/writeback_policy.json",
    "owner_burden_reduction_policy_ref": "policy/owner_burden_reduction_policy.json",
    "allowed_capability_stage": "plan",
    "capability_category": "agent_team_runtime",
    "execution_requires_human_approval": false,
    "migration_note": "L7.0Q first migration adds staged policy references while preserving explicit safety text."
  },
  "l7_0r_staged_policy_remediation": {
    "policy_decision_helper": "policy/policy_decision.py",
    "principle": "Use staged capability policy instead of blanket blocking.",
    "allowed_capability_stages": [
      "observe",
      "analyze",
      "draft",
      "plan",
      "request_approval"
    ],
    "read_only_discovery_allowed": true,
    "draft_allowed": true,
    "actual_execution_blocked_until_approval": true,
    "actual_core_writeback_blocked_until_approval": true,
    "owner_manual_burden_replacement": "Prefer one-command launchers, resolvers, and orchestrators over manual URLs, manual env exports, manual worktrees, or manual merges."
  }
}
```
