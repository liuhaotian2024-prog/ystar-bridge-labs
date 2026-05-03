# C3 E15 Next-Action Decision Packet

- recommended_route: E15A
- why_recommended: C3 replay is consistent and owner-handoff batch is ready; real execution still requires owner activation and later ledger/feedback.

## E15A: owner manually sends 3 validation messages and records result
- trigger_condition: C3 owner-handoff batch is ready and owner activates narrow envelope.
- owner_involvement_level: constitutional activation plus optional manual send while gov-mcp live adapter is inactive
- expected_next_repository_milestone: E15A_owner_handoff_validation_execution
- allowed_actions: owner manual send, action ledger entry, feedback event entry
- blocked_actions: Aiden autonomous send, payment, login, form submit, publication

## E15B: revise offer before sending because target/message fit is weak
- trigger_condition: feedback fixture or owner review flags weak fit.
- owner_involvement_level: review revised positioning only
- expected_next_repository_milestone: E15B_offer_revision_before_action
- allowed_actions: revise draft, rerun batch selection
- blocked_actions: send unrevised weak-fit message

## E15C: expand target discovery before outreach
- trigger_condition: insufficient primary/fallback target quality.
- owner_involvement_level: approve target-class boundary if changed
- expected_next_repository_milestone: E15C_target_expansion
- allowed_actions: public read-only target discovery
- blocked_actions: scrape personal contacts, contact targets

## E15D: activate narrower gov-mcp controlled execution pilot after owner approval
- trigger_condition: owner approves gov-mcp controlled execution envelope and adapter is available.
- owner_involvement_level: constitutional envelope only, not micro-operator
- expected_next_repository_milestone: E15D_gov_mcp_controlled_action_pilot
- allowed_actions: gov-mcp controlled low-volume execution
- blocked_actions: out-of-envelope execution, bulk outreach, payment

## E15E: suppress risky/incomplete targets and replace batch
- trigger_condition: risk, missing fields, opt-out, complaint, or decision replay inconsistency.
- owner_involvement_level: review only if target class changes
- expected_next_repository_milestone: E15E_batch_replacement
- allowed_actions: suppress target, replace target
- blocked_actions: continue suppressed target
