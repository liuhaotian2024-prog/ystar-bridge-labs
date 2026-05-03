# E15D E16 Controlled Pilot Decision Packet

- recommended_route: E16B_owner_manual_send_first
- recommendation_reason: E15A/C3 targets and messages are ready; safest next proof is owner manual send before activating gov-mcp send.

## E16A_owner_approves_draft_only_pilot
- trigger: owner wants gov-mcp to prepare drafts only
- owner_involvement: approve draft-only envelope
- allowed_actions: draft_only_generation, draft_receipts, no_send
- blocked_actions: real_send, publication, payment

## E16B_owner_manual_send_first
- trigger: target/message fit ready but owner wants lowest-risk validation first
- owner_involvement: manual send and feedback capture
- allowed_actions: owner manually sends E15A primary actions, owner records ledger and feedback
- blocked_actions: agent autonomous send, gov-mcp live send without activated envelope

## E16C_one_action_send_gated_pilot_after_authorization
- trigger: owner explicitly activates narrow one-action send-gated envelope
- owner_involvement: constitutional envelope approval only
- allowed_actions: one gov-mcp controlled send, receipt, feedback wait state
- blocked_actions: more than one send, follow-up without positive signal, out-of-envelope send

## E16D_expand_evidence_before_send
- trigger: target/message fit weak or required evidence missing
- owner_involvement: review improved batch
- allowed_actions: public read-only target/evidence improvement, message revision
- blocked_actions: send before evidence improves

## E16E_suppress_current_batch_and_rebuild
- trigger: suppression/risk/do-not-contact emerges
- owner_involvement: review suppression if ambiguous
- allowed_actions: suppress targets, replace batch, record audit receipt
- blocked_actions: contact suppressed target
