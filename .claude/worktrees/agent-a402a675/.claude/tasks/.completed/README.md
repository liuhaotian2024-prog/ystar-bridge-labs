# Completed Tasks Archive

This directory contains tasks that have been completed and should not be reassigned.

## Protocol

When an agent completes a task:
1. Move the task file from `.claude/tasks/` to `.claude/tasks/.completed/`
2. Add completion metadata to the task file
3. Commit the move with the work report

When assigning tasks:
1. Check `.claude/tasks/.completed/` first
2. Do not reassign completed tasks
3. If unsure, check git log for completion commits

## Format

Completed task files should have:
```markdown
Status: COMPLETE
Completed by: [agent role]
Completed on: [YYYY-MM-DD]
Commit: [git hash]
```

This prevents duplicate work across agent sessions.
