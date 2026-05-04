# E16G Bridge-Labs Router Alignment

bridge-labs does not copy gov-mcp implementation. It records the canonical boundary and keeps company-specific validation artifacts local.

## Router Alignment Rules
- action_authorization_router remains bridge-labs local action authorization entrypoint.
- E8 risk tiers remain canonical for bridge-labs operational risk.
- B2R capability levels remain capability maturity, not risk tier.
- E15D outbound policy must reference the gov-mcp adapter contract before any E16C pilot.
- mcp_execute_after_activation is legacy alias; gov_mcp_execute_after_activation is canonical.
- Feedback fixtures cannot become validation feedback or CIEU writeback without action_id/ledger_id/feedback_event_id provenance.

## Remaining Before Real Send
- wire bridge-labs outbound policy to gov-mcp adapter once gov-mcp promotion commit is remote-confirmed
- add E16C dry-run integration test against gov_mcp.outbound
- obtain explicit owner authorization envelope before any real send-gated pilot

- real_e16c0_allowed_now: false
