# Dormant Asset Report

## Strongest existing assets

- repo_or_code_observation: 2988 mapped assets
- cieu_helpers_or_audit: 2745 mapped assets
- reporting_or_status: 2474 mapped assets
- agent_identity: 2438 mapped assets
- action_execution: 2340 mapped assets
- testing_or_validation: 2314 mapped assets
- governance_bridge: 2296 mapped assets
- hook_or_gate: 2251 mapped assets

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
