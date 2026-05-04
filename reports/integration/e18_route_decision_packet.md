# E18 Route Decision Packet

- recommended_route: manual_send_batch_ready
- reason: Ready candidates exist, but no manual send or feedback has been imported.
- real_provider_send_blocked: true
- external_action_executed: false

## Route Options
- manual_send_batch_ready: Owner may approve selected manual-send candidates.
- revise_some_messages_before_send: Use if owner dislikes angle or risk language.
- reject_weak_targets: Use for weak/suppressed/invalid candidates.
- expand_target_evidence: Use if evidence is insufficient.
- wait_for_feedback_import: Use after owner manually sends.
- prepare_followup_only_after_feedback: Use only after positive/clarifying feedback.
- revise_offer: Use after objections or no-response learning.
- commercial_acceleration_candidate: Use after meeting/pricing/positive signal.
- keep_real_provider_send_blocked: Always true until owner explicitly authorizes and provider implementation/tests exist.
