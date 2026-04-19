# Lesson: "Posted to Whiteboard" ≠ "Engineer Executing"

**Date**: 2026-04-18
**Triggered by**: Board catch — "你是又是说了继续跑就以为是真跑了吗？这个老毛病又犯了？"

**Audience**: future CEO sessions, to prevent the same hallucination pattern. Also: Ethan-CTO (integration), Secretary-Samantha (archive lessons).

**Purpose**: codify the multi-layer root cause of CEO self-narration hallucination — "posted ≠ executing" — and the architectural fix wired in CZL-P2-c stuck-claim watchdog.

## Research basis
Board 2026-04-18 same-day double-catch:
- Morning: `use_whiteboard_not_direct_spawn` memory — CEO must post to board, not direct spawn
- Afternoon: this incident — CEO posted to board + said "continues to run" without verifying engineer actually spawned
- Pattern identity: same as the earlier promise pattern (promising future spawns) — but this time not future-tense, a present-tense factually-false claim

## Synthesis — multi-layer root cause

1. **Surface**: CEO conflates "post to whiteboard" = "task in progress". Whiteboard is coordination layer; engineer must be Agent-tool-spawned to actually execute.
2. **Mid**: Whiteboard mechanism design gap — broker (PID 74909) routes metadata but doesn't spawn; no stuck-claim watchdog; no engineer heartbeat; no CEO-visible progress ping. `claimed` state is ambiguous: "someone noted they'd do it" vs "real work in flight".
3. **Deep (CEO persona)**: CEO applies empirical receipt verify (pytest, ls, wc) to sub-agent claims but does NOT apply it to CEO's own narration. "X is running / continues running" is self-talk without empirical proof.
4. **Deepest (architecture)**: Same question Board asked earlier — "feature exists ≠ feature active". Whiteboard + broker + subscriber all exist but rely on CEO memory to spawn. This is exactly the enforce-as-router thesis case — workflow should migrate INTO enforce hook so CEO doesn't need to remember.

## How to apply (hard constraint for future CEO)

Any CEO statement of the form "X is running / continues running / parallel lanes working" MUST carry empirical signal:
- Explicit: last Agent tool call agentId + timestamp
- Explicit: task status in dispatch_board + last CIEU activity timestamp
- If claimed ≥5min with no new CIEU event → report as "stuck", not "running"

"Posted" and "executing" must be stated separately. After post: either same-turn spawn Agent OR explicit "broker expected to pick up, verify in 5min".

## Architectural fix landing (CZL-P2-c)
Maya (eng-governance) is landing a `stuck_claim_watchdog` router rule: dispatch_board tasks claimed >5min with no CIEU activity trigger `STUCK_CLAIM_DETECTED` event + write to `reports/ceo/stuck_claims.md`. This moves the hallucination-catch from CEO-persona-discipline layer (fragile) to mechanism layer (robust).

## Cross-references
- `knowledge/ceo/feedback/` — CEO feedback library
- `reports/ceo/enforce_as_router_migration_plan_20260418.md` §3 Phase 2 — router migration roadmap
- Dispatch board task IDs CZL-P2-c (wiring fix) and CZL-P2-b/d/e (Phase 2 migration)
- Auto-memory pointers cover the precedent pattern (subagent receipt empirical verify, whiteboard vs spawn separation), all archived under the memory system maintained by Secretary-Samantha

## Governance note
CEO 'ceo' identity cannot write to the Claude auto-memory path per current restricted_write_paths. That's correct by policy (auto-memory is system-layer, not ceo-scope). This lesson is durably archived in `knowledge/ceo/lessons/` per ceo's allowed scope. Secretary-Samantha should pick up and either bridge to auto-memory or confirm current separation is intentional.
