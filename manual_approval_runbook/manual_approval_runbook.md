# Manual Approval Runbook

## Approver Review
- Review package id, scope, denied scope, evidence dossier, Y* non-mutation check, MCP non-bypass check, rollback plan, snapshot policy, and preflight validation plan.
- Do not approve direct Y* mutation, brain writeback, memory ingestion, strategy mutation, live/MCP/network execution, or bundled L6 revenue execution.

## Evidence Review
- Confirm sandbox validation, rollback validation, and original-vs-sandbox comparison are present.
- Confirm residual never rewrites mission-level or behavior-level Y* directly.

## Handoff
- Future approval record creation must precede release operator handoff.
- Rollback operator handoff must be complete before application.
- Emergency stop is triggered on validation failure, approval integrity mismatch, rollback unavailability, live/MCP execution, external action, network call, or writeback attempt.
