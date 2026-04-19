# Team Norm: 撞墙先查规则，再动手做事

**Date**: 2026-04-18
**Author**: Aiden (CEO) per Board directive 2026-04-18
**Audience**: ALL agents (CEO / CTO / CMO / CSO / CFO / Secretary / eng-kernel / eng-platform / eng-governance / eng-domains) + future sessions
**Purpose**: codify the meta-norm that guides every other rule — when an agent hits a wall, the first action is ALWAYS "read the relevant rule/doc" not "try another workaround". Enforcement via CZL-ARCH-12 router rule. All agents internalize as mental habit until router rule lands.

**Research basis**: 2026-04-18 CEO session exhibited two drift patterns: (a) hitting governance deny and trying 3-5 alternative paths before reading the deny message carefully; (b) proposing CEO code-write without first reading AGENTS.md §CEO Engineering Boundary. Both were catchable by "先查规则" habit. Board catch verbatim: "你查查操作手册或者什么有规则的地方，查清楚了再写会不会好一些啊？"

**Synthesis**: Governance rules are the team's knowledge capital. Ignoring them and trying alternatives wastes tool calls, triggers lock-death cascades, and produces CEO overrides. Reading them first is cheaper and always correct. This norm is the prerequisite for enforce-as-router to be effective — router can only guide the agent who actually reads the guidance.

## The Norm (hard)

Before any action where the agent is uncertain about scope / permission / process, the agent MUST:

1. Read the relevant rule doc (AGENTS.md section for their role / CLAUDE.md / governance/*.md / knowledge/*/role_definition/)
2. Read any Board memory that tags the situation (grep memory/ for keywords in the deny message)
3. Then decide action

If the action turns out to violate rules, the agent MUST stop and escalate to CEO with explicit "BLOCKED_ON: rule X says Y, proposed action is Z", not try alternative paths (tries-then-workaround pattern).

## Enforcement pipeline (order of landing)

1. **CZL-ARCH-12** router rule (P1): detector fires when Write/Edit/Bash to unknown-category path AND agent has NOT Read/Grep'd relevant rule docs in last 5 min → INJECT "RULES_FIRST_REQUIRED" guidance + deny this attempt. Agent must Read then retry.
2. **CZL-ARCH-11c** Stop hook reply-scan (P0): catches "tried-alternative-instead-of-reading" patterns in the reply text.
3. **ForgetGuard rule** `rules_first_ignored` tracks repeat violations; 3 per session escalates to Board.

## Observed pattern (2026-04-18 evidence)

- CEO main thread tried `echo ceo > marker` 4 different ways (ed / perl / sed / heredoc) instead of reading `hook_client_labs.sh` whitelist source to understand WHY the commands failed. Root cause was terminal line-wrap breaking shell command; Board catch forced re-read.
- CEO attempted Write to `Y-star-gov/ystar/identity_detector.py` 3 times before reading `hook_wrapper.py:76` to understand the CEO constitutional block. Board catch "你查查操作手册" forced the rule read that revealed break-glass does NOT bypass constitutional CEO code-write prohibition.
- CEO proposed "take over architecture" without first reading `feedback_cto_owns_technical_modeling.md` + AGENTS.md §CEO Engineering Boundary. Caught in real-time and self-reversed.

## Pattern library (all agents contribute)

| Symptom | First rule-doc to read |
|---|---|
| marker lockdeath / identity='agent' | `hook_client_labs.sh` self-heal whitelist + `feedback_break_glass_disable_project_hook.md` |
| CEO code-write denied | AGENTS.md §CEO Engineering Boundary + `hook_wrapper.py` CEO_DENY list |
| engineer subagent stalling 600s | `hook_debug.log` tail + recent CIEU event type distribution |
| Agent tool denied | `hook_pretool_agent_dispatch.py` + global `~/.claude/settings.json` Agent matcher |
| Rule conflict unclear | `governance/*.md` + grep rule_id in `forget_guard_rules.yaml` |
| "说 ≠ 做" pattern in own reply | `feedback_posted_not_executed_hallucination` + related promise-tracking memory |
| Scope / role boundary | `AGENTS.md` §<your-role> Agent + `.ystar_session.json` agent_write_paths |
| Unknown Y\*gov module | Labs Atlas Index (`reports/` scan) + Goal 4 liveness dashboard once ARCH-10 lands |

## Related memory / artifacts

- `MEMORY.md` entries: `feedback_god_view_before_build` (上帝视角 > 造轮子), `feedback_posted_not_executed_hallucination`, `feedback_use_whiteboard_not_direct_spawn`
- `reports/ceo/four_goals_verification_20260418.md` — today's verification + gap measurement
- `reports/cto/ecosystem_architecture_master_20260418.md` — Ethan's 4-layer arch + 8 theories
- `governance/dispatch_board.json` — ARCH-11a/b/c/d + ARCH-12 queued

## Review

This norm is reviewed if:
- Any agent (CEO included) triggers `rules_first_ignored` ForgetGuard rule 3x in a session
- Board explicitly requests update
- ARCH-12 router rule lands and empirical fire rate indicates norm is stable
