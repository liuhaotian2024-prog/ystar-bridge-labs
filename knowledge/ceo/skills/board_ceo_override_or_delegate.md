# Board-CEO Override or Delegation Pattern

## When to Use This

**Trigger**: You (CEO) are about to write to a file outside your allowed paths, and governance hook is blocking you.

**Typical blocked paths**:
- Y*gov source code (`/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/`)
- Test files (`tests/`)
- Infrastructure scripts (`scripts/`)
- Agent definitions (`.claude/agents/`)

**Your allowed paths** (from AGENTS.md):
- `reports/`
- `DIRECTIVE_TRACKER.md`
- `BOARD_PENDING.md`
- `DISPATCH.md`
- `memory/`
- `knowledge/ceo/`

---

## Core Pattern

When governance blocks your write, you have **3 options**:

### Option 1: Delegate to Correct Agent (Recommended)
**If**: The work belongs to another role's domain.

**How**:
1. Write task card to `.claude/tasks/{agent}-{task-name}.md`
2. Update `DISPATCH.md` with assignment
3. Let agent pick up task in next session (or invoke via Agent tool if urgent)

**Example**:
```
Hook blocks: CEO writing to ystar/adapters/boundary_enforcer.py
Reason: This is CTO territory

CEO action:
1. Write .claude/tasks/cto-fix-boundary-enforcer-bug.md
2. Update DISPATCH.md: "CTO: fix boundary_enforcer.py line 234 (P0)"
3. Done — CTO will execute in next session
```

**Why this is correct**: CEO doesn't write code. That's what CTO is for.

---

### Option 2: Board-CEO Override (Break Glass)
**If**: Truly urgent AND Board is offline AND no other agent can do it AND delay causes material harm.

**How**:
```bash
bash /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/board_ceo_override.sh
```

**What it does**:
- Activates break_glass mode (CEO permissions elevated to match Board)
- Time-limited: 2 hours max, then auto-revokes
- CIEU logs every action taken (full audit trail)
- Must file incident report afterward

**When to use**:
- Production down, Board unreachable, only CEO can fix
- Security incident requiring immediate code patch
- Regulatory deadline (literal legal consequences if delayed)

**When NOT to use**:
- "I want to tweak this code quickly" → NO, delegate to CTO
- "Board will approve anyway" → NO, wait for Board or delegate
- "It's faster if I do it" → NO, that's not your role

**Aftermath**:
1. Hook auto-revokes after 2h (or CEO manually revokes with `ystar mode standard`)
2. CEO must write `reports/break_glass/{timestamp}_incident.md` explaining:
   - What emergency triggered override
   - What actions taken
   - Why delegation wasn't viable
   - Lessons learned / prevention actions
3. Board reviews next session

---

### Option 3: MCP Delegation Chain (Governance-Approved)
**If**: Task requires cross-agent coordination AND governance must stay enforced.

**How**:
```python
# Via MCP gov_delegate tool
mcp_call("gov_delegate", {
    "task": "Fix boundary_enforcer.py bug",
    "from_agent": "ceo",
    "to_agent": "cto",
    "authority_source": "Board directive DIRECTIVE-2026-04-10-001",
    "constraints": ["must pass all tests", "commit before EOD"]
})
```

**What it does**:
- Formal handoff with CIEU tracking
- CTO receives task with explicit authority trail
- CEO retains accountability (delegation ≠ abdication)
- Auto-generates task card + DISPATCH.md entry

**When to use**:
- Standard workflow (non-urgent)
- Task requires technical expertise CEO doesn't have
- Want full governance audit trail

---

## Decision Tree

```
CEO needs to write file X
  ↓
Is X in CEO allowed paths?
  YES → just do it
  NO  → continue
  ↓
Is Board online right now?
  YES → ask Board approval
  NO  → continue
  ↓
Is this truly urgent? (production down / legal deadline / security incident)
  NO  → Option 1: delegate to correct agent (task card + DISPATCH.md)
  YES → continue
  ↓
Can any other agent fix this? (CTO for code, Secretary for agent files, etc.)
  YES → Option 1: delegate (even if urgent, wake them up)
  NO  → Option 2: board_ceo_override.sh (break glass)
```

**95% of cases → Option 1 (delegate)**  
**4% of cases → Option 3 (MCP delegation)**  
**1% of cases → Option 2 (break glass)**

---

## Common Mistakes

1. **Reaching for break_glass too quickly**: "It's faster if I just fix it."
   - Fix: Delegation is ALWAYS faster long-term. Short-term speed creates long-term chaos.

2. **Forgetting task card**: Verbally telling agent "go fix X" without writing task card.
   - Fix: No task card = no accountability. Always write to `.claude/tasks/`.

3. **Vague delegation**: "CTO, make governance better."
   - Fix: Specific task, specific file, specific success criteria.

4. **No DISPATCH.md update**: Other agents don't know who's doing what.
   - Fix: DISPATCH.md is the single source of truth for active work.

5. **Using break_glass for convenience**: "I know Board would approve, so I'll just override."
   - Fix: Break glass is for emergencies, not convenience. Wait for Board or delegate.

---

## Example

**Scenario**: Test suite is failing, blocking PyPI release. Board is asleep (timezone difference).

### Wrong Approach (Break Glass Misuse)
```
CEO: "This is urgent, I'll use board_ceo_override.sh to fix tests myself."
→ Problem: CEO doesn't know testing internals, might break more things
→ Violation: Break glass should only be used when NO other agent can fix
```

### Correct Approach (Delegate to CTO)
```
CEO action sequence:
1. Write task card:
   .claude/tasks/cto-fix-failing-tests-p0.md
   ---
   ## Context
   PyPI release blocked by test failures:
   - test_behavior_rules.py::test_autonomous_mission (FAILED)
   - test_deny_as_teaching.py::test_remediation_payload (FAILED)

   ## Task
   1. Fix both test failures
   2. Run full test suite (`pytest --tb=short -q`)
   3. Commit with root cause analysis
   4. Report back to CEO

   ## Timeline
   P0 — block PyPI release
   Target: 4 hours

   ## Authority
   Board directive: "0.49.0 release by EOD" (DIRECTIVE-2026-04-12-003)

2. Update DISPATCH.md:
   ## [2026-04-13 01:00] CTO: Fix Test Failures (P0)
   **Blocker**: PyPI 0.49.0 release
   **Files**: test_behavior_rules.py, test_deny_as_teaching.py
   **ETA**: 4h
   **Reporter**: CEO

3. Notify CTO (if active):
   "Ethan, P0 task card in .claude/tasks/ — test failures blocking release."

4. CEO continues other work (doesn't wait for CTO)
```

**Outcome**: CTO fixes tests in 2 hours, commits, reports to CEO. CEO approves and proceeds with PyPI release. No governance violations, full audit trail.

---

## Special Case: Secretary Override for Agent Files

**Exception**: `.claude/agents/` files are immutable for all agents EXCEPT Secretary.

**If CEO needs to modify agent file**:
- Delegate to Secretary (Samantha)
- Secretary has explicit override permission for agent definitions
- Task card: `.claude/tasks/secretary-update-agent-X.md`

**Why**: Agent identity changes are sensitive. Secretary role exists specifically to curate these with Board oversight.

---

**Board Wisdom**: "Break glass exists so you're not helpless in emergencies. But if you use it for convenience, you've just made yourself a single point of failure — which defeats the entire purpose of having a team."

Most "urgent" tasks aren't urgent. They're just unfamiliar. Delegate and let the expert handle it.
