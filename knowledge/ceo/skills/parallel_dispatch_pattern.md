# Parallel Dispatch Pattern

## When to Use This

**Trigger**: You are about to delegate tasks to sub-agents, and you've dispatched 2+ times recently.

**Use parallel dispatch when**:
- Tasks are independent (no shared dependencies)
- Tasks can run simultaneously (no sequential order required)
- Waiting for Task A to finish before starting Task B wastes time

**Use serial dispatch when**:
- Task B depends on Task A output
- Tasks modify shared state (file conflicts, database race conditions)
- You need to verify Task A before committing to Task B

---

## Core Pattern

### Anti-Pattern: Serial Dispatch
```
CEO → dispatch CTO: "build feature X"
(wait for CTO to finish)
CEO → dispatch CMO: "write blog about X"
(wait for CMO to finish)
CEO → dispatch CSO: "demo X to customers"
```

**Problem**: Total time = CTO time + CMO time + CSO time (sequential bottleneck)

### Correct Pattern: Parallel Dispatch
```
CEO → batch write task cards to .claude/tasks/:
  - .claude/tasks/cto-build-feature-x.md
  - .claude/tasks/cmo-blog-feature-x.md
  - .claude/tasks/cso-pilot-customers.md

(each agent picks up their task card in next session)
```

**Benefit**: All agents can work simultaneously without blocking on each other.

---

## Implementation

### Y* Bridge Labs Dispatch Protocol (Recommended)

**Step 1: Batch Write Task Cards**
```bash
# Write all task cards in ONE assistant message (parallel Write calls)
Write .claude/tasks/cto-feature-x.md
Write .claude/tasks/cmo-blog-x.md  
Write .claude/tasks/cso-pilots-x.md
```

**Step 2: Update DISPATCH.md**
Add one entry for the batch dispatch:
```markdown
## [2026-04-13] Feature X Launch Coordination
**Dispatcher**: CEO (Aiden)
**Assigned**:
- CTO: build feature X with tests (.claude/tasks/cto-feature-x.md)
- CMO: draft blog post (.claude/tasks/cmo-blog-x.md)
- CSO: identify 5 pilot customers (.claude/tasks/cso-pilots-x.md)
**Timeline**: 48h
**Sync point**: CEO review when all 3 complete
```

**Step 3: Notify in Session (Optional)**
If agents are actively working, mention in session:
```
"Parallel dispatch: CTO/CMO/CSO each have task cards for Feature X launch. No dependencies — can all run now."
```

### Alternative: MCP gov_dispatch (Future)
```python
# When gov_dispatch enforcement is stable:
from ystar.governance import dispatch_parallel

dispatch_parallel(
    tasks=[
        ("cto", "build feature X"),
        ("cmo", "write blog about X"),
        ("cso", "find 5 pilot customers")
    ],
    coordinator="ceo",
    sync_point="all_complete"
)
```

---

## Common Mistakes

1. **False parallelism**: Tasks look independent but share hidden dependency.
   - Example: CMO needs CTO's feature screenshots → NOT parallel, serial dependency
   - Fix: CMO uses mockups/wireframes until CTO delivers, then updates blog

2. **Coordination overhead**: Creating 10 micro-tasks instead of 2 substantial ones.
   - Fix: Only parallelize if task >30min. Don't split 5-minute tasks.

3. **No sync point**: Dispatched 3 tasks, never checked if they finished.
   - Fix: Set explicit sync point ("CEO review when all 3 complete")

4. **Resource conflict**: Both CTO and CMO need to edit same file.
   - Fix: Assign file ownership, or use feature branches + merge

5. **Serial habit**: Defaulting to "wait and see" when tasks could run in parallel.
   - Fix: Before dispatching Task 2, ask "does this NEED Task 1 output, or just NICE to have?"

---

## Example

**Scenario**: Launch ystar-defuse product (Day 3 of 30-day campaign).

### Serial Approach (Slow)
```
Day 3: CEO → CTO "build defuse MVP"
Day 5: CTO done → CEO → CMO "write blog"
Day 7: CMO done → CEO → CSO "find pilot users"
Day 9: CSO done → CEO "now we can launch"
```
**Total**: 6 days (sequential bottleneck)

### Parallel Approach (Fast)
```
Day 3 morning: CEO writes 4 task cards simultaneously:
  - CTO: build defuse MVP (.claude/tasks/cto-defuse-mvp.md)
  - CMO: write launch blog (.claude/tasks/cmo-defuse-blog.md)
  - CSO: identify 10 pilot prospects (.claude/tasks/cso-defuse-pilots.md)
  - Secretary: prep Show HN post template (.claude/tasks/secretary-show-hn-template.md)

Day 3-5: All 4 agents work in parallel
  - CTO builds MVP
  - CMO writes blog (using wireframes, updates with real screenshots when CTO delivers)
  - CSO reaches out to prospects
  - Secretary drafts Show HN post

Day 5: CEO sync point
  - CTO: MVP ready
  - CMO: blog draft ready (inserts CTO screenshots)
  - CSO: 3 pilots agreed to test
  - Secretary: Show HN post ready

Day 6: Launch (blog + Show HN + pilot outreach)
```
**Total**: 3 days (parallel speedup: 2x faster)

**Key insight**: CMO didn't wait for CTO screenshots — used mockups first, then updated. CSO didn't wait for MVP — recruited based on pitch deck. Only CEO needed to wait for all 4 to sync.

---

## When NOT to Parallelize

**Don't parallelize if**:
1. Task B needs Task A output (true dependency)
2. Both tasks modify same files (merge conflict risk)
3. Task is <15 minutes (coordination overhead exceeds savings)
4. You need to validate Task A before committing to Task B (exploration phase)

**Example where serial is correct**:
```
CTO: "I need to prototype 3 approaches, pick the best one, THEN implement."
→ Don't parallelize implementation. Do serial: prototype → decide → implement.
```

---

**CEO Mandate**: Default to parallel unless proven dependency. Serial dispatch is optimization for coordination, not default mode.

If you're waiting for Agent X to finish before starting Agent Y, ask: "Does Y actually NEED X's output, or am I just being cautious?"
