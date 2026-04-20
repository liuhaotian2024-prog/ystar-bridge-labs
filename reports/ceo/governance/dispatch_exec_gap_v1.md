# CZL-DISPATCH-EXEC — Subscriber Claim-No-Spawn Gap Fix

**Audience**: CTO Ethan for architectural ruling; eng-platform (Ryan) for implementation; future sessions debugging dispatch pipeline.
**Research basis**: `scripts/engineer_task_subscriber.py:44-45` inline comment ("In production, would spawn execution here. For now, daemon only auto-claims (engineer must manually complete)"); 5 cards posted 2026-04-19T15:23-15:25 all claimed by subscribers within 90s but 0 sub-agent sessions actually executing; 3 subscriber PIDs running (1606 eng-platform / 1607 eng-governance / 1608 eng-domains) all stuck in claim-only loop since 2026-04-17 18:19.
**Synthesis**: The "whiteboard + broker auto-execute" mental model is a false premise — subscriber is a Python daemon that cannot spawn Agent tool calls because only the main Claude Code session can. The "in production, would spawn" branch was never implemented. All whiteboard posts are dead-in-water unless CEO main thread direct-spawns Agent tool after claim.
**Purpose**: ship a hybrid pattern — whiteboard holds ledger + claim reservation, CEO main thread is the executor. Subscriber's role narrows to "reserve + emit spawn-intent event", and CEO picks up spawn-intents same-turn.

**Author**: Aiden Liu (CEO)
**Date**: 2026-04-19
**Status**: [L1] SPEC — ready for CTO architectural review then Ryan implementation
**Authority**: Board directive 2026-04-19 authorized execution after diagnosis

---

## 1. The Gap

```python
# engineer_task_subscriber.py:41-45
if result.returncode == 0:
    print(f"Claimed task: {result.stdout.strip()}", file=sys.stderr)
    # In production, would spawn execution here
    # For now, daemon only auto-claims (engineer must manually complete)
time.sleep(poll_interval)
```

Subscriber is a **subprocess** launched from CEO's Claude Code session. It cannot originate Agent tool calls — those only emanate from the Claude session's own tool-use loop. The claim is a **reservation**, not an execution.

Why this stayed invisible: CEO saw "claimed" on whiteboard and mentally-substituted "executing". Board caught the 5-cards-claimed-but-no-activity pattern today and forced the check.

## 2. Four Candidate Patterns

| Pattern | Mechanism | Verdict |
|---|---|---|
| A. Subprocess spawns `claude` CLI per claim | Each claim fork+exec a new Claude Code process | REJECT — cross-process context loss, no shared memory, expensive |
| B. Subscriber writes `spawn_intent` event → CEO polls + spawns | Daemon writes `scripts/.pending_spawns.jsonl`, CEO main loop inspects at each tool-use tick | VIABLE — but CEO main loop has no built-in poller |
| C. Hybrid: whiteboard is ledger, CEO main thread spawns synchronously after post | Each `dispatch_board.py post` emits card + immediately CEO Agent-spawns matching subagent | **CHOSEN** — simplest, lowest change, no daemon rewrite |
| D. MCP server as shared executor | Build MCP tool that both subscriber and CEO can invoke for spawn | OVERKILL for now — revisit at 100+ agents scale |

**Choice**: C. Retrofit current flow — when CEO posts a card, same turn CEO Agent-spawns the responsible engineer with a prompt pointing to the card. Subscriber claims stay as audit trail + collision prevention only.

## 3. Minimum Implementation

### 3.1 Scope-to-Role Map (`scripts/dispatch_role_routing.py`)

Given a card's `scope` string, return the canonical subagent_type:

```python
ROUTE = [
    (r"Y-star-gov/ystar/adapters/|identity_detector|hook\.py", "Leo-Kernel"),
    (r"scripts/hook_|scripts/dispatch_|scripts/.*_wrapper", "Ryan-Platform"),
    (r"governance/|OmissionEngine|ForgetGuard|router_registry", "Maya-Governance"),
    (r"domains/|policy|template", "Jordan-Domains"),
    (r"reports/cto/|arch/|SPEC|review", "Ethan-CTO"),
]
```

Fallback: if no pattern matches, route to `Ethan-CTO` for triage.

### 3.2 CEO Post-and-Spawn Helper (`scripts/dispatch_post_and_spawn.py`)

Wraps `dispatch_board.py post` — after successful post, emits a structured `spawn_intent` to a JSONL tail that CEO's main session reads opportunistically. CEO still does the actual Agent tool call; the helper just assembles the prompt.

Prompt template per `governance/sub_agent_boot_prompt_template.md` — includes BOOT CONTEXT (card id, scope, description, related files to read) + scope guard (no git commit/push) + atomic-scope reminder + 5-tuple receipt requirement.

### 3.3 Subscriber Change (`scripts/engineer_task_subscriber.py`)

Narrow the subscriber's job: claim + emit CIEU event `SUBSCRIBER_CLAIM_PENDING_SPAWN` + write to `scripts/.pending_spawns.jsonl`. Remove the misleading "would spawn" comment; replace with explicit "spawn-is-CEO-responsibility" doc block.

## 4. Integration with Directive Liveness Evaluator (CZL-GOV-LIVE-EVAL)

The evaluator's `task_completed` check primitive (Section 3 of that spec) must verify both whiteboard `completed_at` AND CIEU event `SUBAGENT_COMPLETE` for the card. Claim-only (no completion) = evaluator verdict stays LIVE.

## 5. Safeguards

| Risk | Mitigation |
|---|---|
| CEO forgets to spawn after post | pending_spawns.jsonl tail becomes a CEO nag — every boot checks for un-spawned claims older than 1h |
| Subscriber claims but CEO crashes before spawn | claim TTL 1h — subscriber un-claims expired cards |
| Race: two subscribers claim same card | existing atomic-claim in dispatch_board.py already handles this |
| Role mis-routing | fallback is Ethan-CTO triage, never silent drop |

## 6. Rollout

- **Phase 1 (this round)**: ship `dispatch_role_routing.py` + Ryan retrofit subscriber comment; CEO starts using Agent-spawn-same-turn pattern manually.
- **Phase 2**: `dispatch_post_and_spawn.py` helper; CEO uses it instead of raw post.
- **Phase 3**: pending_spawns.jsonl + boot check + claim TTL.

## 7. Owner

- Architecture: CTO Ethan (ruling on Pattern C vs B, scope-to-role regex taxonomy).
- Implementation: Ryan Park (eng-platform).
- Tests: Leo Chen (adapter-layer unit tests for role routing).
- CEO role: compose Agent-spawn prompts using the new helper; feedback on friction.

## 8. Success Criteria

- Next 5 cards posted → 5 sub-agents actually running within same CEO turn → receipts back within their estimated_tool_uses budgets.
- Zero "claimed but not executing" dead-water cards after Phase 2 ship.
- CIEU event stream shows matched pairs: `SUBSCRIBER_CLAIM_PENDING_SPAWN` → `SUBAGENT_START` within 60s.
