# Directive Liveness Evaluator v1 — 3-Component Model

**Author**: Aiden Liu (CEO)
**Date**: 2026-04-19
**Status**: [L1] SPEC — ready for implementation handoff to eng-governance (via CTO)
**Authority**: Board directive 2026-04-19 — "以后如何可以被持续的智能的执行"
**Maturity target**: L3 LIVE = agent auto-detects stale directives without human prompt

---

## 0. Why This Exists

Governance directives (pauses, blocks, bans, obligations) are written with **implicit conditions** — "pause X pending Y". Over time:

- The condition resolves, but no one updates the status field.
- The environment shifts, making the original concern moot.
- A newer directive supersedes but does not cite the earlier one.
- The label outlives the reason.

Current pattern: agents ask Board "is this still in effect?" every session. Board has to re-evaluate. This is **evaluation waste** — the answer is usually derivable.

Goal: every directive carries machine-checkable release conditions so agents can self-evaluate liveness without Board in the loop.

---

## 1. The 3-Component Model

Every directive decomposes into:

| Component | Question | Example (P2 pause 2026-04-18) |
|---|---|---|
| **Trigger** | What present concern motivated this? | "ARCH unclear, P2 migration risks wrong foundation" |
| **Release** | What event lifts this? | "CTO architecture review complete (task a00cd8a6596785e9b)" |
| **Scope** | What actions does this cover? | "all P2 migration work (P2-b/c/d/e)" |

A directive is **LIVE** iff:
- (Trigger still present) **AND**
- (Release condition not yet met) **AND**
- (Action falls in scope)

If any component fails → directive no longer auto-applies → action may proceed.

If 2+ components are ambiguous → escalate to originating authority (usually Board or role owner).

---

## 2. Schema (machine-readable directive annotation)

Every blocking/pausing directive on the whiteboard, in obligations, or in governance/*.md MUST carry this JSON block:

```json
{
  "directive_id": "CZL-P2-PAUSE-20260418",
  "issued_at": "2026-04-18T22:00:00Z",
  "issued_by": "Board",
  "trigger": {
    "statement": "ARCH enforce-as-router design unclear",
    "check": {
      "type": "doc_exists",
      "path": "Y-star-gov/docs/arch/arch17_behavioral_governance_spec.md",
      "min_status": "L1"
    },
    "current_state": "present|resolved|ambiguous"
  },
  "release": {
    "statement": "CTO architecture review complete",
    "check": {
      "type": "task_completed",
      "source": "whiteboard",
      "atomic_id": "a00cd8a6596785e9b"
    },
    "current_state": "met|unmet|partial"
  },
  "scope": {
    "statement": "all P2 migration work",
    "covers": ["CZL-P2-b", "CZL-P2-c", "CZL-P2-d", "CZL-P2-e"],
    "pattern": "atomic_id matches ^CZL-P2-"
  },
  "evaluator": {
    "last_run": "2026-04-19T14:52:00Z",
    "verdict": "RELEASED|LIVE|AMBIGUOUS",
    "evidence": ["arch17 consolidated by Ethan 2026-04-19", "3 router commits landed"],
    "requires_human_ack": true
  }
}
```

---

## 3. Check Primitives

The evaluator needs a small library of deterministic checks. All must be side-effect-free reads:

| Type | Input | Output | Example |
|---|---|---|---|
| `doc_exists` | path, min_status | bool | ARCH-17 canonical doc at L1+ |
| `task_completed` | atomic_id | bool | whiteboard task marked complete |
| `file_mtime_after` | path, iso_timestamp | bool | file touched since directive issued |
| `git_commit_matches` | repo, pattern, since | bool | commit with message match exists |
| `obligation_closed` | obligation_id | bool | OmissionEngine obligation not pending |
| `cieu_event_absent` | event_type, hours | bool | no recent violation event |
| `manual_ack` | acker, note | bool | Board/role-owner explicit ack captured |

No LLM judgment inside primitives — deterministic only. LLM may compose primitives into a verdict, but individual checks resolve to true/false from concrete filesystem/database state.

---

## 4. Integration Points (where this fires)

Four surfaces — ordered by implementation complexity:

1. **Whiteboard scan (simplest, implement first)** — `dispatch_board.py` extended with `evaluate_blocks` subcommand. For every task with `status=blocked`, read `blocked_on_directive_id`, load directive annotation, run primitives, emit verdict. Auto-unblock + post ack receipt if all conditions clear. Human confirmation required if `requires_human_ack=true`.

2. **Obligation close-check (OmissionEngine)** — same primitives run on pending obligations; if release condition met, obligation auto-closes with CIEU receipt.

3. **Enforce-router rule (ties into ARCH P2-a router_registry)** — detector: action matches a directive's scope pattern. executor: run primitives, if LIVE then DENY with directive_id citation, if RELEASED then ALLOW with audit trail, if AMBIGUOUS then ESCALATE to originator.

4. **Boot-time staleness report (lightweight)** — `governance_boot.sh` prints count of directives with verdict != last_run_verdict (i.e., state changed since last eval). No action, just visibility.

---

## 5. Failure Modes & Safeguards

| Failure | Safeguard |
|---|---|
| Evaluator wrongly auto-releases a still-live directive | `requires_human_ack=true` default for Board-issued directives; 15-min grace window before auto-apply |
| Release-check primitive returns false-positive (e.g., doc exists but empty) | `min_status` + content signature check; primitive must verify `L1+` tag present |
| Scope pattern too broad | Every directive carries explicit `covers: [ids]` + `pattern`; pattern is advisory, `covers` is authoritative |
| Agent games evaluator (writes doc to fake release) | Primitives check git-signed commits + CIEU audit trail, not just file existence; writes trigger CIEU event which evaluator cross-references |
| Directive missing annotation | Retro-fill campaign on first boot after ship; unchecked directives are treated as LIVE until annotated (fail-safe toward caution) |

---

## 6. Phased Rollout

**Phase 1 (this week)** — [L1→L3 target]
- Schema + primitives library
- Whiteboard `evaluate_blocks` subcommand
- Retro-annotate existing 4 blocked tasks on whiteboard (P2-b/c/d/e + any obligations)
- Manual evaluator run on boot, output in governance_boot.sh

**Phase 2 (next week)** — [L3→L4 target]
- OmissionEngine integration
- Enforce-router rule (detector + executor pattern for directive-scoped actions)
- CIEU event emission on evaluator verdicts

**Phase 3 (validation)** — [L4→L5 target]
- Live-fire: deliberately stale a directive → evaluator catches → CIEU confirms
- 30-day run with zero Board-initiated "is X still in effect?" questions = L5

---

## 7. Open Questions (for Ethan/CTO architectural review)

1. Does this belong in Y*gov product core (`Y-star-gov/ystar/governance/`) or company layer (`ystar-company/scripts/`)? Lean product-core for reusability across customer deployments.
2. Should directive annotation schema live in JSON (extensible, current) or a SQLite table (queryable, better for cross-directive correlations)? Lean SQLite for Phase 2+.
3. Interaction with ForgetGuard: FG rules are one form of directive. Should FG ingest this schema directly or stay parallel? Lean ingest — reduces redundancy.
4. LLM-judge role: primitives are deterministic, but verdicts on AMBIGUOUS cases might use LLM. Acceptable only if (a) audit-trailed (b) conservative default (LIVE unless confident RELEASED).

---

## 8. Owner Handoff

- **Implementation owner**: eng-governance (Maya Patel) primary; eng-platform (Ryan) for whiteboard CLI integration; eng-kernel (Leo) for router-rule detector if Phase 2.
- **Architectural review**: CTO (Ethan) — addresses Q1-Q4 above before Phase 1 ship.
- **CEO role (Aiden)**: cross-role coordination; report Phase 1 completion to Board; draft Phase 2 scope when Phase 1 L3.
- **Board role (Haotian)**: approve schema + rollout shape; final acceptance at Phase 3 L5.

---

## 9. This Directive's Own Annotation (dogfood)

```json
{
  "directive_id": "CEO-DIR-LIVE-EVAL-20260419",
  "issued_at": "2026-04-19T14:55:00Z",
  "issued_by": "Board via CEO",
  "trigger": {"statement": "recurring Board evaluation of stale directives is waste"},
  "release": {"statement": "Phase 3 L5 accepted — 30-day zero-question run", "check": {"type": "manual_ack", "acker": "Board"}},
  "scope": {"statement": "design + implement directive liveness evaluator", "covers": ["CZL-GOV-LIVE-EVAL"]},
  "evaluator": {"verdict": "LIVE", "last_run": "2026-04-19T14:55:00Z"}
}
```

When this spec ships to L5, the evaluator evaluates itself as RELEASED. That is the receipt.
