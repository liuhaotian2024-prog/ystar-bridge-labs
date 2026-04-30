# L7C Human-Approved External Action Gate

```json
{
  "schema_version": "v0",
  "milestone_id": "L7.0P",
  "lane_id": "L7C",
  "lane_name": "Human-Approved External Action Gate",
  "output_dir": "l7_human_approved_external_action_gate",
  "status": "complete",
  "artifacts": [
    "l7_human_approved_external_action_gate/external_action_types/external_action_type_index.json",
    "l7_human_approved_external_action_gate/external_action_types/customer_outreach_email.json",
    "l7_human_approved_external_action_gate/external_action_types/partner_outreach_email.json",
    "l7_human_approved_external_action_gate/external_action_types/grant_application_submission.json",
    "l7_human_approved_external_action_gate/external_action_types/RFP_submission.json",
    "l7_human_approved_external_action_gate/external_action_types/public_content_publication.json",
    "l7_human_approved_external_action_gate/external_action_types/account_creation.json",
    "l7_human_approved_external_action_gate/external_action_types/payment_or_purchase.json",
    "l7_human_approved_external_action_gate/external_action_types/contract_or_signature.json",
    "l7_human_approved_external_action_gate/external_action_types/social_posting.json",
    "l7_human_approved_external_action_gate/external_action_types/MCP_live_behavior.json",
    "l7_human_approved_external_action_gate/draft_only_action_packets/draft_only_action_packet_schema.json",
    "l7_human_approved_external_action_gate/human_approval_requests/human_approval_request_schema.json",
    "l7_human_approved_external_action_gate/approval_state_machine/approval_state_machine.json",
    "l7_human_approved_external_action_gate/post_action_receipts/post_action_receipt_schema.json",
    "l7_human_approved_external_action_gate/external_action_no_go_matrix/external_action_no_go_matrix.json",
    "l7_human_approved_external_action_gate/external_action_no_go_matrix/no_action_receipt.json"
  ],
  "next_safe_step": "create draft-only action packets behind human approval",
  "external_actions_blocked": true,
  "core_writebacks_blocked": true,
  "ask_user_for_url_occurred": false,
  "external_side_effects_occurred": false,
  "core_writeback_occurred": false,
  "secret_values_serialized": false,
  "action_types_modeled": 10,
  "all_actions_default_blocked": true,
  "l7_0q_policy_migration": {
    "policy_ref": "policy/action_capability_registry.json",
    "action_capability_policy_ref": "policy/action_capability_registry.json",
    "approval_state_machine_ref": "policy/approval_state_machine.json",
    "revenue_policy_ref": "policy/revenue_action_policy.json",
    "discovery_policy_ref": "policy/discovery_policy.json",
    "runtime_access_policy_ref": "policy/runtime_access_policy.json",
    "writeback_policy_ref": "policy/writeback_policy.json",
    "owner_burden_reduction_policy_ref": "policy/owner_burden_reduction_policy.json",
    "allowed_capability_stage": "draft",
    "capability_category": "external_action_gate",
    "execution_requires_human_approval": true,
    "migration_note": "L7.0Q first migration adds staged policy references while preserving explicit safety text."
  },
  "l7_0r_staged_policy_remediation": {
    "policy_decision_helper": "policy/policy_decision.py",
    "principle": "External execution is staged: draft allowed, execution blocked until human approval.",
    "allowed_capability_stages": [
      "draft",
      "request_approval",
      "execute_after_approval"
    ],
    "read_only_discovery_allowed": true,
    "draft_allowed": true,
    "actual_execution_blocked_until_approval": true,
    "actual_core_writeback_blocked_until_approval": true,
    "owner_manual_burden_replacement": "Prefer one-command launchers, resolvers, and orchestrators over manual URLs, manual env exports, manual worktrees, or manual merges."
  }
}
```
