# E17 Feedback Runtime

Owner can import a response later with a small structured intake. The empty file claims no send and no customer response.

- action_id: c2_action_primary_001_cand_alicelabs_alicelabs
- ledger_id: ledger_c2_action_primary_001_cand_alicelabs_alicelabs
- feedback_event_id: feedback_c2_action_primary_001_cand_alicelabs_alicelabs
- empty_feedback_type: no_response_yet
- real_customer_response_claimed: false

## Supported Feedback Types
- no_response_yet
- no_response_after_wait_window
- positive_interest
- clarification_request
- pricing_question
- meeting_request
- referral
- objection
- unsubscribe_or_do_not_contact
- negative_response
- bounced_or_invalid_target
- manual_notes_only

## Classification Rule Families
- classify_no_response_yet: E17_manual_send_ready
- classify_positive_interest: E18_commercial_acceleration_candidate
- classify_pricing_question: E17_manual_follow_up_allowed_after_owner_review
- classify_meeting_request: E18_commercial_acceleration_candidate
- classify_clarification_request: E17_wait_for_owner_feedback_import
- classify_unsubscribe_or_do_not_contact: E17_suppress_target
- classify_bounced_or_invalid_target: E17_target_evidence_expansion_required
- classify_negative_response: E17_offer_revision_required
