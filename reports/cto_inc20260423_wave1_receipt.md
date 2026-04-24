Audience: CEO (Aiden) for dispatch coordination + Board for incident audit trail
Research basis: INC-2026-04-23 incident report, hook_wrapper.py v1 marker chain (lines 167-253), identity_detector.py priority chain, boundary_enforcer.py session_start_protocol rule
Synthesis: v2 thin adapter lacked marker fallback chain causing agent="agent" -> session_start_protocol DENY-all -> 3h deadlock; structural fix adds _read_marker_fallback() to handle_hook_event() with 10 regression tests passing
Purpose: Enable CEO to proceed with Items #1 commit (needs Board shell or identity fix) and Items #3-#9 engineer dispatch

# CTO Technical Report — INC-2026-04-23 Wave-1 Audit

## 5-Tuple Receipt

```
Y*:  9-point audit Wave-1 kickoff
Xt:  Item #1 BLOCKED (identity), Item #2 SHIPPED (code+tests), Items #3-#9 task cards WRITTEN
U:   3 actions completed: v2 adapter fix, regression tests, task card document
Yt+1: CEO dispatches Items #3-#9 via sub-agents; Board or secretary fixes identity for Item #1 commit
Rt+1: >0 — Item #1 hook_wrapper.py inline comment+commit blocked by identity resolution bug (CTO resolves as "ceo")
```

## Item #1 — Board sed fix commit: BLOCKED

**Status**: Blocked by governance identity resolution

**Problem**: CTO sub-agent resolves as "ceo" in the governance hook. CEO write allowlist does not include `scripts/hook_wrapper.py`. The `.ystar_active_agent` marker file is secretary-only writable. This is a chicken-and-egg problem -- the identity resolution bug we are fixing prevents us from committing the fix.

**Board action needed**: Either:
1. Board shell: `sed -i '' '80i\    # DISABLED (Board 2026-04-23): v2 path caused fail-closed deadlock. See reports/incidents/2026-04-23-hook-fail-closed-deadlock.md' scripts/hook_wrapper.py` then `git add scripts/hook_wrapper.py && git commit -m "fix(hook): disable v2 adapter path + inline incident ref (INC-2026-04-23)"`
2. Or: spawn secretary to set `.ystar_active_agent` to "ystar-cto", then re-run CTO to commit

**Verification**: `scripts/hook_wrapper.py:80` currently reads `if False and os.environ.get("YSTAR_HOOK_V2") == "1":` -- Board sed confirmed working.

## Item #2 — v2 adapter structural fix: SHIPPED

**Status**: L3 code+tests shipped, not committed to Y-star-gov git

**Changes Made**:
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/hook.py`:
  - Added `_read_marker_fallback()` function (83 lines) at line 2006
  - Added marker injection block in `handle_hook_event()` (13 lines) at line 2049
  - Total: +102 lines, 0 lines removed

**Root cause addressed**: When Claude Code sends `agent_id=""` and `agent_type="agent"` (root process defaults), the v2 `handle_hook_event()` path previously passed the raw payload directly to router rules and `check_hook()`. The `_detect_agent_id()` function in identity_detector.py has marker file fallback at priority 7, but the `session_start_protocol_incomplete` rule in boundary_enforcer.py fires on the raw `who` value before identity resolution completes in the check_hook call chain. The fix pre-injects the marker identity into the payload at the top of `handle_hook_event()`, ensuring priority 1 (payload.agent_id) resolves correctly for all downstream processing.

**Marker fallback chain** (mirrors hook_wrapper.py v1 lines 167-253):
1. Per-session marker via `CLAUDE_SESSION_ID` env var
2. Per-session marker via `PPID` env var
3. Global marker — newest of repo-root vs scripts/ variants

**Test Results**:
- New tests: `tests/adapters/test_hook_v2_marker_fallback.py` — **10/10 passed**
- Existing v2 tests: `tests/adapters/test_hook_v2_arch6.py` — **10/11 passed** (1 pre-existing failure unrelated)
- Full adapter suite: **151/164 passed** (13 pre-existing failures, 0 new failures)

**Files created**:
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/adapters/test_hook_v2_marker_fallback.py` (181 lines)

## Items #3-#9 — Task Cards: WRITTEN

**Status**: Written to `reports/inc-20260423-task-cards.md` (governance blocked `.claude/tasks/` writes)

| Item | Bug/Task | Owner | Priority | Tool Budget |
|------|----------|-------|----------|-------------|
| #3 | FORGET_GUARD None.startswith | Maya | P0 | 8 |
| #4 | article_11 obligation fields | Leo/Maya | P1 | 10 |
| #5 | Transitive import audit | Leo | P0 | 20 |
| #6 | K9 Rescue Daemon v1 | Ryan | P0 | 40 |
| #7 | tmp/bak cleanup + chmod | Ryan | P1 | 5 |
| #8 | priority_brief refresh | Samantha | P1 | 15 |
| #9 | ForgetGuard CEO-bypass + import | Leo/Maya | P0 | 15 |

## Meta-observation: Identity Resolution is a Systemic Fragility

This session surfaced a recursive irony: the CTO cannot fix the identity resolution bug because the identity resolution bug prevents the CTO from writing to the fix location. Three governance boundaries conspired:

1. CTO sub-agent identity resolves as "ceo" (parent agent identity leaks)
2. CEO cannot write to `scripts/` (write boundary)
3. `.ystar_active_agent` is secretary-only (restricted write path)

This is the same class of lock-death the incident caused. The v2 fix I shipped addresses it for the v2 adapter path. But the v1 path's identity in sub-agent context (CTO spawned by CEO) still depends on the marker being correctly set by secretary before CTO runs. Item #9 (ForgetGuard CEO break-glass) addresses the emergency escape hatch.
