# E9 Progressive Autonomy Ladder

## L0_internal_only
- allowed_in_E9: True
- required_controls: no_external_side_effect
- description: Prepare, analyze, draft.

## L1_read_only
- allowed_in_E9: True
- required_controls: public_read_only_budget
- description: Read public no-login sources.

## L2_owner_operated_handoff
- allowed_in_E9: True
- required_controls: manifest, targets, draft_hash
- description: Owner sends manually from handoff packet.

## L3_aiden_sends_with_exact_approval_provider
- allowed_in_E9: True
- required_controls: valid_manifest, approved_targets, safe_provider, action_ledger
- description: Aiden may send only within exact approved scope.

## L4_public_broadcast_with_explicit_approval
- allowed_in_E9: True
- required_controls: tier3_publication_approval, draft_hash, ledger
- description: Publish only with explicit Tier 3 approval.

## L5_commercial_production_blocked_in_E9
- allowed_in_E9: False
- required_controls: separate_future_approval
- description: Payment, contracts, account creation, production changes are blocked in E9.
