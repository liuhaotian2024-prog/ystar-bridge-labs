Audience: CEO (Aiden) for spawn dispatch; Samantha (Secretary) for execution
Research basis: Mission 1 patch commit 1b554c1b verified ForgetGuard import chain restored; Leo kernel_import_audit_20260423.md Item #5
Synthesis: Shadow import blocker is fixed; Samantha can now retry the methodology lesson import that failed during INC-2026-04-23
Purpose: Enable CEO to spawn Samantha sub-agent to complete the blocked MEMORY.md import

# Task -- Samantha retry methodology lesson import to MEMORY.md

Status: ready for CEO spawn (Leo Item #5 patch applied, identity import chain fixed)

Source: reports/lessons/feedback_post_incident_methodology_regression_20260423.md

Targets (Samantha immutable_paths scope):
  - ~/.claude/projects/-Users-haotianliu--openclaw-workspace-ystar-company/memory/feedback_post_incident_methodology_regression.md (new file)
  - ~/.claude/projects/-Users-haotianliu--openclaw-workspace-ystar-company/memory/MEMORY.md (insert entry above Rt+1=0 line)

Expected: new feedback file + MEMORY.md index +1 entry

Prereq verified: Mission 1 smoke import pass (commit 1b554c1b, `python3 -c "import sys; sys.path.insert(0, '.../Y-star-gov'); from ystar.governance.forget_guard import ForgetGuard; print('OK')"` returns OK)
