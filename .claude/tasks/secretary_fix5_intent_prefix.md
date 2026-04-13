# FIX-5: Add Intent Declaration to Sub-Agent Prompt Prefix

**Assignee**: Secretary (Samantha Lin)  
**Priority**: P0  
**Requested by**: Platform Engineer (Ryan Park) per Board directive  
**Date**: 2026-04-13

## Context

Maya's breach report (`reports/breaker_violations_20260413.md`) shows Circuit Breaker ARMED with 1757 violations, top rule = `omission_violation:intent_declaration` (10x/window).

Root cause: Worker agents (CTO, engineers, C-suite) don't declare intent before actions, causing Y*gov OmissionEngine to flag every tool call.

## Task

Add intent declaration requirement to **all** agent prompt templates in `.claude/agents/`:
- cto.md
- eng-kernel.md (Leo)
- eng-governance.md (Maya)
- eng-platform.md (Ryan)
- eng-domains.md (Jordan)
- cmo.md (Sofia)
- cso.md (Zara)
- cfo.md (Marco)

## Implementation

Insert this block **immediately after the role header, before any other instructions**:

```markdown
## Y*gov Intent Declaration (Constitutional)

Before EVERY action (tool call, decision, file operation), you MUST emit one line to CIEU:

**INTENT: [goal in <10 words]**

Example:
- `INTENT: Read hook.py to understand current violation detection`
- `INTENT: Edit orchestrator.py to add retry logic`
- `INTENT: Run pytest to verify fix`

This is a Y*gov `intent_declaration` requirement. Omissions trigger Circuit Breaker.
```

## Acceptance Criteria

1. All 8 agent files updated with intent declaration block
2. Block appears **before** role-specific instructions
3. Formatting consistent across all files
4. No other changes to agent files

## Follow-up

After completion, Platform Engineer will:
1. Reset Circuit Breaker (`gov_reset_breaker`)
2. Monitor 10min for new `intent_declaration` violations
3. Report result to Board: "prefix shipped + breaker reset, new violations in 10min = X"

## Notes

- Secretary has `immutable_path` override for `.claude/agents/`
- This is constitutional change — affects all future sessions
- Intent declaration is lightweight (one line per action), not verbose logging
