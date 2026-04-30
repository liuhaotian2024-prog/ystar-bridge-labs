# L7E Owner Runtime Cockpit

```json
{
  "schema_version": "v0",
  "milestone_id": "L7.0P",
  "lane_id": "L7E",
  "lane_name": "Owner Runtime Cockpit",
  "output_dir": "l7_owner_runtime_cockpit",
  "status": "complete",
  "artifacts": [
    "l7_owner_runtime_cockpit/system_status_cards/system_status_card.json",
    "l7_owner_runtime_cockpit/agent_team_cards/agent_team_card_index.json",
    "l7_owner_runtime_cockpit/work_order_queue_cards/work_order_queue_cards.json",
    "l7_owner_runtime_cockpit/revenue_opportunity_cards/revenue_opportunity_cards.json",
    "l7_owner_runtime_cockpit/approval_queue_cards/approval_queue_cards.json",
    "l7_owner_runtime_cockpit/blocked_action_cards/blocked_action_cards.json",
    "l7_owner_runtime_cockpit/next_command_recommendations/next_command_recommendations.json",
    "l7_owner_runtime_cockpit/owner_cockpit_no_action_receipts/no_action_receipt.json",
    "l7_owner_runtime_cockpit/owner_cockpit.json",
    "l7_owner_runtime_cockpit/owner_cockpit.md"
  ],
  "next_safe_step": "bash scripts/run_l7_parallel_lanes.sh --mode local-parallel",
  "external_actions_blocked": true,
  "core_writebacks_blocked": true,
  "ask_user_for_url_occurred": false,
  "external_side_effects_occurred": false,
  "core_writeback_occurred": false,
  "secret_values_serialized": false,
  "owner_cockpit_created": true,
  "blocked_actions": 11,
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
    "capability_category": "owner_cockpit",
    "execution_requires_human_approval": false,
    "migration_note": "L7.0Q first migration adds staged policy references while preserving explicit safety text."
  }
}
```
