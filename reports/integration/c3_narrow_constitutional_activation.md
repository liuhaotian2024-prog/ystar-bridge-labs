# C3 Narrow Constitutional Activation

## 人话摘要

C3 没有伪造 owner approval。当前 envelope 是 `locally_activated_for_owner_handoff_only`，只允许 owner-handoff 和 local dry-run。它不允许 agent 直接发送消息，也不允许 login / form submission / publication / account creation / payment / contract / core writeback。

## Scope

- allowed_scope: low_risk_validation_messaging, owner_handoff_execution, local_dry_run_receipt, feedback_intake, signal_evaluation, next_action_recommendation
- allowed_execution_modes: owner_handoff, dry_run_local
- agent_direct_execution_allowed: false
- external_action_executed: false
