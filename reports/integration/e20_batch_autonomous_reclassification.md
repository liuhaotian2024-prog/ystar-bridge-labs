# E20 Batch Autonomous Reclassification

- batch_id: e18_first_revenue_validation_batch
- external_action_executed: false

## Summary Counts
- agent_autonomous_allowed: 0
- agent_autonomous_allowed_with_limits: 0
- owner_approval_required: 0
- owner_manual_only: 0
- blocked_no_go: 0
- provider_capability_missing: 5
- evidence_required_before_execution: 2

| target | executor decision | classification |
| --- | --- | --- |
| Alice Labs AI Operations Consulting | provider_capability_missing | policy_allows_autonomous_but_provider_missing |
| BotSquash AI Automation Agency | provider_capability_missing | policy_allows_autonomous_but_provider_missing |
| WotAI AI Automation | provider_capability_missing | policy_allows_autonomous_but_provider_missing |
| Alice Labs AI Operations Consulting | provider_capability_missing | policy_allows_autonomous_but_provider_missing |
| BotSquash AI Automation Agency | provider_capability_missing | policy_allows_autonomous_but_provider_missing |
| WotAI AI Automation | evidence_required_before_execution | evidence_required |
| Excluded direct agent execution path | evidence_required_before_execution | evidence_required |
