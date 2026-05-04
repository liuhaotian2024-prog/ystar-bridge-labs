# E17 Route Decision Packet

- recommended_route: E17_manual_send_ready
- reason: The selected action is commercially prepared, owner-facing, and still no-send; the shortest cash path is owner manual send followed by feedback import.
- e16c1_real_send_blocked: true

## Route Options
### E17_manual_send_ready
- status: recommended_if_no_response_yet
- allowed: owner reviews one page
- allowed: owner manually sends if approved
- allowed: owner later imports feedback
- blocked: agent send
- blocked: provider API call
- blocked: real send receipt

### E17_wait_for_owner_feedback_import
- status: after_owner_manual_send
- allowed: owner imports response summary
- allowed: deterministic classification
- blocked: claim paid signal without evidence

### E17_offer_revision_required
- status: if weak/no-response/objection evidence appears
- allowed: revise pain framing
- allowed: revise CTA
- allowed: revise packaging
- blocked: keep repeating weak message

### E17_target_evidence_expansion_required
- status: if target/channel evidence is weak
- allowed: public read-only evidence expansion
- allowed: replace from existing queue
- blocked: scrape private contact data

### E17_provider_adapter_preparation_allowed
- status: allowed_as_no_send_engineering_only
- allowed: provider-safe tests
- allowed: no-send adapter preparation
- blocked: real send before explicit activation

### E16C1_real_send_still_blocked
- status: blocked
- blocked: real email/message send
- required_before_unblock: explicit owner activation
- required_before_unblock: real provider adapter implementation
- required_before_unblock: provider tests
- required_before_unblock: safety tests
- required_before_unblock: bridge delivery closure

### E18_commercial_acceleration_candidate
- status: only_if_imported_response_is_positive_or_budget_signal
- allowed: owner-reviewed paid diagnostic follow-up
- allowed: meeting scheduling if requested
- blocked: automated follow-up without owner review
