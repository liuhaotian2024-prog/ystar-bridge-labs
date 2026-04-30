# L7C Human-Approved External Action Gate Lane Prompt

Worktree path: `../ystar-company-l7-action`
Branch: `l7/human-approved-action-gate`

Objective: Build draft-only external action packet schemas and approval state machines so no external action can execute before explicit human approval.

Scoped files:
- `l7_human_approved_external_action_gate/**`
- `scripts/l7_lanes/build_l7c_human_approved_external_action_gate.py`

Forbidden actions:
- No sending, submitting, publishing, payment, account creation, signatures, social posting, MCP/live behavior, or external side effects.

Validation command:
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/l7_lanes/build_l7c_human_approved_external_action_gate.py`

Completion report fields:
- Action types modeled
- Default status
- Approval state machine
- Post-action receipt requirement
- Execution remains blocked
