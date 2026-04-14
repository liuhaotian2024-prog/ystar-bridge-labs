# Y*gov Architecture Roadmap — Board Session 2026-04-11

## Board Directive Origin
Board governance recovery session 2026-04-11. Session restart exposed fundamental gaps in enforcement infrastructure. Board directive: "所有硬约束必须集中在一个地方，永久有效，重启不失效。"

---

## Core Architecture (Platform-Agnostic)

```
Y*gov Core (one codebase, works everywhere)
  ├── boundary_enforcer.py   <- Rule engine (who, tool_name, params) -> ALLOW/DENY
  ├── session config         <- Rule data (.ystar_session.json)
  ├── CIEU                   <- Immutable audit chain
  ├── OmissionEngine         <- Obligation tracking (timeout/violation/intervention)
  └── Symbol Sync System     <- task_type_symbols (checkpoint attestation)
```

## Three-Layer Enforcement Model

| Layer | Role | Can agent bypass? |
|-------|------|-------------------|
| Hook (PreToolUse) | Mandatory enforcement — all hard constraints | NO |
| Skill (ystar-govern) | Guardian — ensures Hook is alive and configured | Not relevant — it guards, not enforces |
| Gov-mcp (49 tools) | Operations — audits, reports, manual checks | YES — but it's toolbox, not enforcement |

## Symbol Synchronization System

Converts cognitive rules into mechanically checkable symbols.

```json
"task_type_symbols": {
  "autonomous_mission": {
    "required": ["L0-MEANING", "L1-GOALS", "L2-HYPOTHESES", "L3-THEORY",
                  "L4-BENCHMARK", "L5-RELEVANCE", "L6-CASES", "L7-CAPABILITY"],
    "enforce": "DENY_EXECUTION_WITHOUT_ALL"
  },
  "bug_fix": {
    "required": ["ROOT-CAUSE-IDENTIFIED", "TEST-WRITTEN", "FIX-VERIFIED"],
    "enforce": "DENY_COMMIT_WITHOUT_ALL"
  },
  "content_publish": {
    "required": ["FACT-CHECKED", "ETHICS-REVIEWED", "BOARD-APPROVED"],
    "enforce": "DENY_PUBLISH_WITHOUT_ALL"
  },
  "learning_session": {
    "required": ["THEORY-SELECTED", "THEORY-STUDIED", "PRACTICE-APPLIED",
                  "REFLECTION-DONE", "KNOWLEDGE-WRITTEN", "GAP-IDENTIFIED"],
    "enforce": "DENY_CLAIM_LEARNING_WITHOUT_ALL"
  }
}
```

## Platform Adapter Strategy

```
Adapters (thin, platform-specific)
  ├── Claude Code adapter    <- PreToolUse hook (IMPLEMENTED)
  ├── OpenClaw adapter       <- Legal contract format (EXISTS)
  ├── LangChain adapter      <- CallbackHandler (PLANNED)
  ├── Codex adapter          <- Function calling middleware (PLANNED)
  ├── Gateway adapter        <- HTTP proxy mode (PLANNED)
  └── Container adapter      <- Sandbox I/O control (PLANNED)
```

## Labs = Clean Governed Organization

```
Labs (ystar-company)
  ├── Agent definitions (11 people: names, roles, org chart)
  ├── Product work (ystar-defuse, content, sales, finance)
  ├── Operational data (reports, CIEU, memory)
  └── knowledge/ (agent learning accumulation)
```

No governance rules in Labs. All rules in Y*gov core + session config.

## Rule Change Process

```
Board decides change
  -> tells Secretary (Samantha Lin)
  -> Secretary modifies .ystar_session.json
  -> Hook reads fresh config on next tool call
  -> Done. No restart. No code change.
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Platform changes hook mechanism | Adapter pattern allows migration |
| Hook daemon crashes | Fail-closed + slow path + crontab 30min verify |
| No defense in depth | CIEU post-hoc audit as second line |

## Constraint Count: 193 items

- 20 enforcement functions in boundary_enforcer.py
- 89 agent behavior rules (10 agents x 7-12 rules)
- 15 system-level constraints (paths, commands, immutable, restricted)
- 4 Labs-specific checks (hook_wrapper.py)
- 4 task types with symbol requirements
- Full index: docs/HARD_CONSTRAINTS.md

---

*Archived by CEO (Aiden Liu). Secretary (Samantha Lin) is custodian.*
*Source: 2026-04-11 Board governance recovery session.*
