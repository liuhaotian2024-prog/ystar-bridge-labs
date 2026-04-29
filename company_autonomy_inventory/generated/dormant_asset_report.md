# Dormant Asset Report

## Strongest existing assets

- repo_or_code_observation: 3789 mapped assets
- cieu_helpers_or_audit: 3241 mapped assets
- action_execution: 3146 mapped assets
- reporting_or_status: 3001 mapped assets
- hook_or_gate: 2922 mapped assets
- mcp_or_external_interface: 2828 mapped assets
- agent_identity: 2676 mapped assets
- testing_or_validation: 2565 mapped assets

## Action-capable assets that remain disabled

- shell, git, hook, daemon, CIEU, brain/memory, and external interface surfaces require governed wrappers

## Should be wrapped into governed tools

- Console read model tools (candidate)
- Governance dry-run tools (needs_wrapper)
- Live readiness and boundary tools (needs_tests)
- CIEU boundary tools (needs_schema)
- Safe repository scan tools (candidate)
- Local validation and test tools (candidate)
- Docs and report generation tools (candidate)
- GitHub PR and issue tools (blocked)
- MCP interface tools (needs_wrapper)

## Should not be reused yet

- direct push, external communication, CIEU persistence, daemon control, brain writeback, memory ingestion
