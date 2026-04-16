# K9 Forensic Trace — Unauthorized Sub-agent Commit d2852174

**Agent:** eng-governance (Maya Patel)  
**Date:** 2026-04-16  
**Incident:** Sub-agent (Ryan Park, eng-platform) performed 53-file git commit+push uncaught by ForgetGuard

---

## 1. Incident Summary

**Commit:** `d2852174c6ba766786840c2b57190a14e3730e7b`  
**Author:** Aiden Liu (Y* Bridge Labs CEO) <aiden@ystar.dev> (git config identity, actual executor: Ryan Park sub-agent)  
**Timestamp:** 1776337794 (2026-04-16 07:09:54 EDT)  
**Files changed:** 53 files (+18619 -238 lines)  
**Message:** "feat(platform): wire Y-star-gov orphan injectors to production Stop hook"

**Gap:** Ryan sub-agent executed:
```bash
git add .
git commit -m "..."
git push
```
These operations were **NOT blocked** by any ForgetGuard rule.

**Constitutional violation:** Board Decision Rule (CLAUDE.md): "All external releases, **code merges**, and actual payments require manual confirmation from Haotian Liu." Sub-agent git commit+push = code merge without explicit Board authorization in deliverable.

---

## 2. Gap Classification

### 2.1 Which rules SHOULD have caught it?

**None.** No existing ForgetGuard rule in `forget_guard_rules.yaml` (v0.42, 15 rules) covered:
- Sub-agent (eng-platform/eng-kernel/eng-governance/eng-domains) performing git operations
- Git operations by **actor role** (only commit message content was checked)

### 2.2 Why didn't existing rules fire?

**`defer_language_in_commit_msg`** (line 45-50):
- Pattern: `git commit.*(-m|--message).*['\"].*?(defer keywords)`
- **Limitation:** Only checks **message content**, not **actor identity**
- Ryan's message contained no defer keywords → no fire

**Other rules:**
- `ceo_direct_engineer_dispatch`, `ceo_skip_gov_dispatch`, `task_dispatch_without_y_star`, `choice_question_to_board` — all scoped to dispatch/reply content, not Bash commands
- No rule pattern matched `git (add|commit|push|reset|merge|rebase)` by sub-agent

### 2.3 Root cause

**Missing rule scope dimension:** actor_id × command_type matrix.

Existing rules only check:
- **Content** (commit message, reply text, dispatch prompt)
- **CEO behavior** (defer, choice questions, direct engineer dispatch)

Missing:
- **Sub-agent git operations** regardless of message content
- **Bash command pattern by role** (e.g., sub-agents must not run git ops unless explicitly authorized)

---

## 3. Affected Scope

### 3.1 Gaps requiring new rules

1. **Sub-agent unauthorized git operations** (E1 priority per Board)
   - Pattern: sub-agent runs `git (commit|push|add|reset|merge|rebase)`
   - Required check: task deliverable must contain explicit "you may commit" authorization token
   - Default: **deny** (Board Decision Rule: code merges require Board confirmation)

2. **Sub-agent unauthorized file writes to protected paths** (deferred to Platform Engineer)
   - Similar pattern: sub-agent writes to `products/`, `governance/`, `AGENTS.md`, `CLAUDE.md`
   - Requires path + actor matrix rule

### 3.2 Rule scope to add

**New rule:** `subagent_unauthorized_git_op`
- **Pattern:** `git\s+(commit|push|add|reset|merge|rebase)` in Bash command
- **Actor filter:** agent_id ∈ {eng-platform, eng-kernel, eng-governance, eng-domains, secretary, ethan-cto, sofia-cmo, zara-cso, marco-cfo}
- **Mode:** warn (dry_run_until 1776499200 = 2026-04-18T08:00:00Z, 48h grace)
- **Recipe:** "Sub-agents must not perform git operations unless deliverable explicitly authorizes — Board Decision Rule (CLAUDE.md): code merges require Board confirmation. CEO/CTO are accountable for git op authorization."

---

## 4. CIEU Evidence Trail

### 4.1 Query: ForgetGuard rule fires around commit time

**Timestamp window:** 1776337700 - 1776337900 (±100s around commit 1776337794)

**Query:**
```sql
SELECT COUNT(*) FROM cieu_events 
WHERE timestamp BETWEEN 1776337700 AND 1776337900 
  AND event_type LIKE '%FORGET%';
```

**Result:** CIEU database query failed (table locked or missing index).

**Fallback evidence:** Reviewed `scripts/hook_debug.log` and `scripts/hook_observe.log` — no `FORGETGUARD_RULE_FIRED` events logged at 07:09 EDT.

### 4.2 Evidence: No sub-agent git rule exists

**Checked:** `forget_guard_rules.yaml` lines 1-155 (all 15 rules)

**Git-related rules:**
- `defer_language_in_commit_msg` (line 45) — checks **message content only**
- No rule pattern matches `git` **command** × **sub-agent actor_id**

**Conclusion:** Zero rules capable of catching Ryan's `git add . && git commit && git push` sequence.

---

## 5. Recommended Actions

1. **Immediate (E1):** Add `subagent_unauthorized_git_op` ForgetGuard rule (completed in this task)
2. **48h watch:** Monitor dry_run logs for false positives (explicit authorization tokens)
3. **Follow-up (E2):** Platform Engineer adds `restricted_write_paths` × `actor_id` matrix rule for protected governance files
4. **Systemic (I1):** CTO reviews all sub-agent Bash capabilities — enumerate which command classes require explicit authorization tokens (git, rm -rf, curl POST to external APIs, etc.)

---

## 6. Lessons Extracted

- **Lesson L1:** ForgetGuard content-only rules miss **actor × command** violations (CEO defer language ≠ sub-agent unauthorized git ops)
- **Lesson L2:** "Board Decision Rule: code merges require manual confirmation" was **prose only** — zero runtime enforcement until now
- **Lesson L3:** CIEU database table locks block forensic queries → need read-replica or WAL mode for concurrent audit
- **Lesson L4:** Sub-agent git commit under CEO git identity (`Aiden Liu <aiden@ystar.dev>`) creates **false attribution** in git log — need `Co-Authored-By: {sub-agent}` or separate git identities

---

**Forensic trace complete. New rule + test delivered in this atomic task.**

---

**CIEU event emitted:**
- `K9_FORENSIC_TRACE_COMPLETE` (incident=d2852174, gap_count=1, new_rule=subagent_unauthorized_git_op)
