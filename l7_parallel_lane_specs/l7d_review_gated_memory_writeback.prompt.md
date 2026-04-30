# L7D Review-Gated Memory / Brain Writeback Lane Prompt

Worktree path: `../ystar-company-l7-memory`
Branch: `l7/review-gated-memory-writeback`

Objective: Build dry-run-only memory, brain, capability, strategy, and CIEU DB writeback candidate structures behind human review gates.

Scoped files:
- `l7_review_gated_memory_writeback/**`
- `scripts/l7_lanes/build_l7d_review_gated_memory_writeback.py`

Forbidden actions:
- No actual CIEU DB write, brain/memory writeback, canonical strategy mutation, direct Y* mutation, or automatic approval.

Validation command:
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/l7_lanes/build_l7d_review_gated_memory_writeback.py`

Completion report fields:
- Candidate count
- Target layers covered
- Dry-run-only status
- Human approval gate
- Core writeback blocked
