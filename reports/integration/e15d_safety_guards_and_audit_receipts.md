# E15D Safety Guards and Audit Receipts

- guard_count: 11
- audit_receipts: 3
- external_action_executed: false

## Guards
- global_kill_switch: deny_all
- batch_kill_switch: deny_batch
- target_suppression: suppress_target
- do_not_contact: suppress_target_and_stop
- max_actions_per_day: deny_rate_limit
- max_actions_per_target: deny_duplicate_target_send
- no_followup_without_positive_signal: deny_followup
- no_send_if_missing_target_identity: require_more_research
- no_send_if_message_unreviewed: draft_only
- no_send_if_envelope_not_active: send_gated_pending_authorization
- no_send_if_hard_gate_detected: owner_hard_gate
