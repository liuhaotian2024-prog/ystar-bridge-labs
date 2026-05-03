# E15A Feedback Capture and Signal Loop

E15A does not invent feedback. This fixture defines how later owner-entered replies will be normalized.

## no_response
- normalized_signal: no_response
- signal_strength: weak
- sales_implication: no buyer signal yet
- governance_implication: valid only after real action ledger and wait window
- next_action_route: rotate_to_fallback_or_wait

## positive_interest
- normalized_signal: positive_interest
- signal_strength: medium
- sales_implication: buyer interest exists but may not be paid signal
- governance_implication: requires next-step envelope before follow-up
- next_action_route: prepare_governed_followup_decision

## price_question
- normalized_signal: price_question
- signal_strength: strong
- sales_implication: paid-signal candidate may exist
- governance_implication: requires ledger-backed feedback and CIEU residual candidate
- next_action_route: E15D_gov_mcp_controlled_execution_pilot_after_owner_review

## unsubscribe_or_do_not_contact
- normalized_signal: unsubscribe_or_do_not_contact
- signal_strength: hard_stop
- sales_implication: target must be suppressed
- governance_implication: suppression and stop condition triggered
- next_action_route: E15E_suppression_and_batch_replacement

## Invalid no_response
- normalized_signal: invalid_no_response_without_action
- no_response is invalid unless owner has a real sent ledger and wait window.
