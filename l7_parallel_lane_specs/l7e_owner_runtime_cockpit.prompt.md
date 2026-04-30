# L7E Owner Runtime Cockpit Lane Prompt

Worktree path: `../ystar-company-l7-cockpit`
Branch: `l7/runtime-cockpit`

Objective: Build the owner-facing cockpit that explains what the system owns, which agents exist, what is blocked, what needs approval, and the next safest command.

Scoped files:
- `l7_owner_runtime_cockpit/**`
- `scripts/l7_lanes/build_l7e_owner_runtime_cockpit.py`

Forbidden actions:
- No external search by default, no external action, no core writeback, no secret handling, no manual URL request.

Validation command:
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/l7_lanes/build_l7e_owner_runtime_cockpit.py`

Completion report fields:
- Cockpit generated
- Agents displayed
- Revenue radar displayed
- Approval queues displayed
- Next safe command
