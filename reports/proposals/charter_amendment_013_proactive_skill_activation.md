# AMENDMENT-013: Proactive Skill Activation
**Date**: 2026-04-13  
**Author**: Jordan Lee (eng-domains)  
**Status**: Implementation In Progress  
**Parent**: AMENDMENT-012 (Deny as Teaching / Remediation)  

---

## Executive Summary

Upgrade hook return values from binary `{allow, deny}` to ternary `{allow, deny, activate}`. Instead of waiting for rule violations to teach, **proactively inject relevant skills, role DNA, and 11-layer templates into agent context before they execute actions**.

Board insight (2026-04-13 session): **"Symbolic alignment deny is already a primitive teaching mechanism"** — when autonomous mission triggers without Article 11, deny + show template simultaneously. AMENDMENT-013 formalizes this into a general-purpose activation system.

---

## Problem Statement

Current governance is **reactive**: we wait for agents to hit boundaries, then provide remediation. But many patterns are predictable:
- Agent declares autonomous mission → will need Article 11 7-layer construction template
- CEO uses "decide"/"战略" keywords → should see counterfactual template first
- Any agent edits code → should be reminded of root_cause_fix_required pattern
- CEO tries to write outside allowed paths → needs skill showing `board_ceo_override.sh` or delegation chain

**Current State**: agent violates → DENY + remediation message  
**Target State**: agent about to act → ACTIVATE skill + ALLOW with context  

This reduces governance friction while increasing teaching bandwidth.

---

## Design

### 1. Three-Value Policy Decision

```python
# ystar/adapters/boundary_enforcer.py

class Decision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ACTIVATE = "activate"   # Allow execution but inject skill first

@dataclass
class SkillActivation:
    skill_id: str             # e.g., "knowledge/ceo/skills/article_11_seven_layers.md"
    skill_content: str        # parsed markdown payload (not just path)
    trigger_rule: str         # which rule triggered this activation
    priority: int             # when multiple skills activate, order matters (1=highest)
    role_filter: List[str]    # only activate for these roles (empty = all roles)
```

### 2. Activation Trigger Registry

Each trigger = `(detection_pattern, skill_id, rule_name, priority, role_filter)` tuple.

**Phase 1 (MVP — 5 triggers):**

| Detection Pattern | Inject Skill | Trigger Rule | Priority | Roles |
|---|---|---|---|---|
| Action contains `autonomous_mission` (symbol alignment) + "自主任务"/"autonomous" keywords | `knowledge/{role}/skills/article_11_seven_layers.md` | `autonomous_mission_requires_article_11` | 1 | all |
| CEO uses "决策"/"decide"/"战略"/"strategic" keywords | `knowledge/ceo/skills/counterfactual_before_major_decision.md` | `counterfactual_before_major_decision` | 1 | ceo |
| Edit/Write to code file (`.py`) | `knowledge/{role}/skills/root_cause_fix_pattern.md` | `root_cause_fix_required` | 2 | cto, eng-* |
| Agent delegates to sub-agent 2+ times in 5 actions | `knowledge/{role}/skills/parallel_dispatch_pattern.md` | `parallel_dispatch_required` | 3 | ceo, cto |
| CEO Write to path outside allowed boundaries | `knowledge/ceo/skills/board_ceo_override_or_delegate.md` | `write_boundary_violation` | 1 | ceo |

**Phase 2 (future — pattern-based):**
- Analyze recent N CIEU events for recurring patterns (e.g., "about to do X")
- Proactively activate skills before pattern completes
- Use LLM intent detection (not just keyword match)

### 3. Hook Integration

**Hook daemon (`_hook_daemon.py`) + wrapper (`hook_wrapper.py`):**

When `Decision.ACTIVATE` returned:
1. Hook returns `allow` to Claude Code (action proceeds)
2. But prepends activation payload to response message:
   ```
   [Y*] 📖 SKILL ACTIVATED: {skill_id}
   
   {skill_content}
   
   ---
   ```
3. Emit CIEU event: `SKILL_ACTIVATION` with metadata (agent, skill_id, trigger_rule, timestamp)
4. Track activation frequency → high-frequency skills = high-value content for future skill generation

**Graceful degradation:**
- If `skill_id` points to nonexistent file → log warning, return ALLOW without activation
- If `skill_content` fails to parse → log warning, show skill path only
- If role_filter mismatch (e.g., CMO triggering CEO-only skill) → skip activation, log INFO

### 4. CIEU Event Schema

```python
{
    "event_type": "SKILL_ACTIVATION",
    "agent_id": "ceo",
    "skill_id": "knowledge/ceo/skills/counterfactual_before_major_decision.md",
    "trigger_rule": "counterfactual_before_major_decision",
    "action_type": "Write",  # original action that triggered activation
    "timestamp": "2026-04-13T00:50:00Z",
    "priority": 1
}
```

### 5. Relationship to AMENDMENT-012 (Remediation)

**No conflict — complementary mechanisms:**

| Amendment | When | Return | Payload |
|---|---|---|---|
| 012 (Remediation) | Action **DENIED** | `deny` | Structured remediation (why denied + how to fix + example) |
| 013 (Activation) | Action **ALLOWED** | `activate` | Skill content (template/pattern injected before execution) |

**Can combine**: same `PolicyResult` can have both `remediation` (for DENY) and `activation` (for future ALLOW):
- Example: DENY autonomous mission without Article 11 → remediation = "you must complete Article 11 first" + activation = Article 11 template (primed for next attempt)

---

## Implementation Plan

### Milestone 1: Data Structures + 2 Triggers (+3h)

1. **Charter**: this document  
2. **PolicyResult extension**: add `Decision.ACTIVATE` + `SkillActivation` dataclass  
3. **Trigger registry**: `ystar/adapters/activation_triggers.py` with 2 initial triggers:
   - `autonomous_mission_requires_article_11`
   - `counterfactual_before_major_decision`
4. **Skill drafts**: write Hermes-4-section drafts for 2 skills (if files don't exist)

### Milestone 2: Hook Integration + All 5 Triggers (+6h)

5. **Hook daemon**: integrate ACTIVATE decision handling in `_hook_daemon.py`  
6. **Hook wrapper**: prepend skill content to response message  
7. **CIEU emit**: emit `SKILL_ACTIVATION` event  
8. **Trigger registry complete**: add remaining 3 triggers:
   - `root_cause_fix_required`
   - `parallel_dispatch_required`
   - `write_boundary_violation`
9. **All skill drafts**: write 5 skill files (Hermes 4-section format)

### Milestone 3: Tests + Report (+8h)

10. **Test suite**: `tests/test_proactive_activation.py` with 10+ test cases:
    - Autonomous mission declaration → ACTIVATE + CIEU emit
    - CEO "决策" keyword → counterfactual skill primed
    - skill_id nonexistent → graceful degradation (warning + ALLOW)
    - CIEU SKILL_ACTIVATION schema validation
    - Role filter mismatch → skip activation
    - Multiple skills activate simultaneously → priority ordering
    - Integration with AMENDMENT-012 remediation (same PolicyResult has both)
11. **Integration validation**: verify no conflict with AMENDMENT-012  
12. **Local commit**: Y-star-gov + ystar-company  
13. **Report**: `reports/amendment_013_impl_20260413.md`  
14. **Ping CEO**: ready for review

---

## Skill Content Format (Hermes 4-Section)

Each skill file follows Hermes standard:

```markdown
# {Skill Title}

## When to Use This
{Triggering conditions}

## Core Pattern
{Step-by-step template or checklist}

## Common Mistakes
{What agents get wrong + how to avoid}

## Example
{Concrete example from Y* Bridge Labs history}
```

---

## Success Criteria

- [ ] `Decision.ACTIVATE` + `SkillActivation` dataclass implemented
- [ ] 5 activation triggers registered and active
- [ ] 5 skill files written (or gracefully degraded if missing)
- [ ] Hook daemon integrates ACTIVATE decision
- [ ] CIEU emits `SKILL_ACTIVATION` events
- [ ] 10+ tests pass (all green)
- [ ] No conflict with AMENDMENT-012 remediation system
- [ ] Report documents all changes
- [ ] No remote push (local commit only)

---

## Phase 2: Pattern-Based Activation (Future)

After MVP stabilizes:
- Analyze CIEU event sequences for recurring patterns
- Use LLM intent detection (not just keyword match)
- Auto-generate new skills from high-frequency activation patterns
- Build skill recommendation system (suggest new skills based on CIEU gaps)

---

## References

- **AMENDMENT-012**: Deny as Teaching / Structured Remediation (commit c510127)  
- **Maya's Obligation Fulfiller Contract**: proactive obligation injection (sister mechanism)  
- **Article 11 (AGENTS.md)**: 7-layer cognitive construction for autonomous missions  
- **Board insight (2026-04-13)**: "Symbolic alignment deny is already primitive teaching"

---

**Status**: Implementation starting 2026-04-13 00:50  
**Target Completion**: 2026-04-13 08:50 (+8h)  
**Blocker**: None  
