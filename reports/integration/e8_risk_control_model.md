# E8 Risk-Controlled External Action Model

E8 asks what external action is allowed under which risk controls, not whether all external action is permanently forbidden.

## TIER_0_INTERNAL
- allowed_actions: internal_prepare
- prohibited_actions: none
- required_controls: none
- escalation_rule: No external side effect is allowed.
- audit_ledger_required: False
### Stop Conditions
- stop if action becomes external-facing

## TIER_1_PUBLIC_READ_ONLY
- allowed_actions: public_read
- prohibited_actions: send_validation_message, publish_post, collect_payment
- required_controls: stop_conditions_required, no_payment_required, no_account_creation_required
- escalation_rule: Escalate if login, form submission, contact, payment, or private data appears.
- audit_ledger_required: True
### Stop Conditions
- login required
- form/payment/contact flow
- private or sensitive page

## TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION
- allowed_actions: send_validation_message, request_feedback, collect_survey_response
- prohibited_actions: collect_payment, create_account, submit_form, core_writeback
- required_controls: ai_disclosure_required, owner_approval_required, target_seed_required, channel_required, draft_hash_required, max_count_required, stop_conditions_required, opt_out_required, action_ledger_required, feedback_ledger_required, no_deception_required, no_scraped_leads_required
- escalation_rule: Allow only with exact manifest, target, channel, draft hash, count, stop conditions, and disclosure.
- audit_ledger_required: True
### Stop Conditions
- opt-out
- recipient asks to stop
- budget exhausted
- draft hash changes
- unapproved channel

## TIER_3_PUBLIC_BROADCAST_OR_LANDING
- allowed_actions: publish_post, publish_landing_page
- prohibited_actions: collect_payment, create_account, execute_contract
- required_controls: ai_disclosure_required, owner_approval_required, draft_hash_required, stop_conditions_required, action_ledger_required, no_deception_required
- escalation_rule: Requires explicit Tier 3 publication approval.
- audit_ledger_required: True
### Stop Conditions
- publication content changes
- form/payment/account flow appears
- owner approval missing

## TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK
- allowed_actions: none
- prohibited_actions: collect_payment, create_account, submit_form, execute_contract, production_implementation, core_writeback
- required_controls: no_payment_required, no_account_creation_required, no_core_writeback_required
- escalation_rule: Always blocked in E8.
- audit_ledger_required: True
### Stop Conditions
- any Tier 4 action requested
