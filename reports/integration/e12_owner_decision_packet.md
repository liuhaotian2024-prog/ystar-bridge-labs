# E12 Owner Decision Packet

- e12_status: BLOCKED_BY_MISSING_E12_OWNER_APPROVAL
- external_validation_ran: false
- aiden_sent_anything: false
- customer_contact_occurred: false
- publication_occurred: false
- approval_valid: false
- execution_status: blocked_missing_or_invalid_approval
- feedback_captured: false
- validation_signal_classification: blocked_no_execution
- recommended_next_step: provide_valid_E12_approval_and_feedback

## Exact Owner Action
- If owner wants owner-operated validation: approve `operations/external_validation/e12_owner_approval.request.json`, materialize `operations/external_validation/e12_target_seeds.json`, manually execute the handoff, then record `operations/external_validation/e12_feedback_events.json`.
- If owner wants Aiden execution later: provide valid approval, approved targets, safe provider, and keep all E11 router checks passing.
- If owner has already collected feedback manually: record it in the E12 feedback events file using the generated template.

## Approval Does Not Cover
- payment collection
- account creation
- form submission
- publication
- core DB/brain/memory/CIEU writeback
