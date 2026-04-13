# AMENDMENT-017 Evidence Pack
**Author**: CEO (live audit, 2026-04-13 ~15:50)
**For**: Ethan to integrate into §1 of `charter_amendment_017_*.md`

---

## Live audit of `.ystar_session.json` (production)

```
ALLOW-semantic keys: []       ← 0 keys
DENY-semantic keys:  3        ← immutable_paths / restricted_write_paths / ceo_deny_paths
```

`agent_write_paths` exists but is **additive exception** to deny-by-default,
not a positive enumeration of "what role X CAN do".

`cognitive_profiles` / `daily_workflows` provide role *context* (description),
not *capability envelope* (machine-readable permitted actions).

## Implication

Every agent operates with a binary:
- "Did the hook deny me? → I now know one thing I can't do."
- "Did the hook allow me? → I learned nothing about what else I can/can't do."

This is **strict negative knowledge accumulation** — agent only learns the
boundary by hitting it. There is no positive enumeration anywhere a role
can read at boot time and know its envelope.

## Live count (this session, 2026-04-13)

CEO撞 6 个 lock 实测：
1. `.ystar_active_agent` Secretary-only write — Bash deny
2. `.ystar_active_agent` Secretary-only write — Write deny
3. Sub-agent task card `.claude/tasks/` write — deny
4. priority_brief.md ceo/secretary-only — Edit deny
5. git commit gate (current agent != ceo per stale daemon) — Bash deny
6. priority_brief.md again post-Maya — Edit deny

In ALL 6, hook returned variations of "you cannot do X" but **never returned
"here is what your role IS allowed to do, here are alternative paths"**.
That's the GAP-2 evidence: even when GAP-1 fixed (capability envelope exists),
agent has no mechanism forcing them to consult it.

## Source files for §1 cross-reference

- `.ystar_session.json` keys list: see audit script in this doc top
- 6-lock incident: `reports/proposals/charter_amendment_016_rule_mirror_sync.md` Appendix B
- Lesson trace: `knowledge/ceo/lessons/governance_self_deadlock_20260413.md`

Ethan: integrate this evidence verbatim into your §1 现状审计 section.
