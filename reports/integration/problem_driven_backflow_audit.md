# Problem-Driven Backflow Audit

Audience: Board, Aiden CEO, Ethan CTO, Samantha Secretary, Y-star-gov maintainers, gov-mcp maintainers.
Research basis: local read-only inspection of `ystar-bridge-labs`, `Y-star-gov`, `gov-mcp`, and recent `ystar-company` incubator artifacts. No DB/WAL/SHM/log/secret/env/active-agent marker contents were read.
Synthesis: `ystar-company` should not become the final company brain. Its useful patterns are backflow candidates only where they repair concrete gaps in the original repos.
Purpose: select the minimum high-value backflow targets for this sprint.

## 1. Problems in ystar-bridge-labs

### Aiden CEO interaction

The original company repo has strong Aiden identity in `README.md`, `AGENTS.md`, and `OPERATIONS.md`, but it lacks a small owner-facing Aiden meeting runtime. Aiden's role is described as CEO, directive decomposer, Board-facing synthesizer, and Level-2 coordinator, yet there is no direct CLI or meeting room where the owner can ask Aiden strategy questions and receive repo-grounded answers.

### Owner-agent meeting workflow

The repo contains rich operating doctrine, daily schedules, Board directive protocols, and historical daily/autonomous reports, but the workflow is mostly document-mediated. There is no simple "owner asks Aiden -> Aiden answers from current company context -> memory/summary captured" loop.

### Directive tracker usability

`DIRECTIVE_TRACKER.md` is canonical and detailed, but it is long and archival. It proves that directives were tracked, but it is not an approachable meeting interface for a live owner conversation. The tracker is useful evidence, not a usable discussion room.

### Autonomous work becoming report-only

`reports/autonomous/` and `OPERATIONS.md` show autonomous cycles that produce substantial reports. The failure mode is that internal work can look complete because a report exists, while M-3 value production remains weak. This matches the Board's repeated "plan does not equal done" concern in `WORK_METHODOLOGY.md`.

### M-3 value production not becoming runtime

`AGENTS.md` and `M_TRIANGLE.md` define M-3 as real product, real customer, real revenue, and real industry impact. The repo has sales/content/operations files, but no small runtime that forces Aiden to keep first-cash reasoning tied to M Triangle and M-3 rather than drifting into more governance prose.

### Sales/meta-development workflow fragmentation

Sales assets live under `sales/`, operational strategy lives in `OPERATIONS.md`, company identity in `README.md`/`AGENTS.md`, and methodology in `knowledge/ceo/wisdom/`. The ideas are present, but not assembled into a conversational CEO interface that can explain "what are we selling next and why?"

### Lack of usable Office entry point

There are office images and frontend artifacts, but no minimal local "Aiden meeting room" focused on the owner asking real questions. A heavy cockpit would repeat the ystar-company mistake; the correct repair is a small CLI/runtime first.

### Lack of repo-grounded Aiden response engine

The repo has enough source context for a useful deterministic Aiden: M Triangle, WORK_METHODOLOGY, Operations, governance, team identity, gov_order pipeline. What is missing is the loader/classifier/response layer that turns those artifacts into direct CEO answers.

## 2. Problems in Y-star-gov

### Missing company_runtime domain pack

Y-star-gov has strong deterministic governance and existing domain packs such as OpenClaw, but no first-class domain pack for AI company runtime missions: internal work, read-only research, preparation-only actions, owner-approved external execution, and high-risk review-gated actions.

### No first-class delegated mission contract

Delegation and omission are well represented, but "delegated company mission" is not a domain object with explicit owner goal, permission tier, budget, forbidden action classes, and required review points.

### No permission tier abstraction

The kernel has contracts, domains, and checks, but company operation needs a named risk-tier vocabulary: Tier 0 internal autonomous work through Tier 4 high-risk blocked/review-gated action.

### No escalation/action preflight abstraction

The enforcement layer can allow/deny low-level actions, but company operations need a deterministic preflight saying "ALLOW_INTERNAL", "NEEDS_OWNER_APPROVAL", "BLOCKED", or "REVIEW_GATED" for commercial, mission, memory, repo, and external side-effect actions.

### Mission/commercial/residual objects not governed as domain concepts

Recent ystar-company work proved that mission, commercial action, manual-send, feedback, residual, and learning candidate objects are useful, but in Y-star-gov they should appear only as deterministic governance concepts, not as an app or packet UI.

## 3. Problems in gov-mcp

### Missing company operation MCP tools

gov-mcp exposes many governance tools, but none speak the company-runtime language the owner now needs: mission check, action preflight, escalation check, owner decision envelope.

### gov_check/gov_enforce are low-level but not mission-aware

`gov_check` and `gov_enforce` are correct low-level tools, but they require callers to express company work as generic tool/action params. They do not know permission tiers, manual-send-only boundaries, or owner approval semantics.

### No MCP tools for owner decision, mission preflight, escalation preflight, residual building

The gateway lacks normalized company runtime tools that can classify an action, verify a mission budget/tier, validate escalation completeness, and record an owner decision envelope without executing the action.

### No clean company runtime bridge

gov-mcp should bridge clients into Y-star-gov's deterministic company_runtime pack. It should not depend on `ystar-bridge-labs` paths and should not become an office UI.

## 4. Useful ideas in ystar-company

### L7 office / whiteboard / team work

Useful classification: `useful_but_needs_redesign`.

Useful idea: owner-facing meeting/work surface and Aiden routing. Do not backflow the giant UI, packet directories, or fake team rooms. Backflow only the idea that Aiden needs a direct meeting interface grounded in company context.

### L7.6 scheduler

Useful classification: `useful_but_needs_redesign`.

Useful idea: bounded autonomous internal work and approval interrupts. Do not migrate scheduler implementation now. Backflow its permission-boundary logic into Y-star-gov domain concepts.

### L8 first cash path loop

Useful classification: `useful_to_backflow_now`.

Useful idea: first cash path as a seed, manual-send only action, owner approval, feedback, residual, review-gated learning. In this sprint, backflow only into Aiden's reasoning and Y-star-gov/gov-mcp approval/preflight vocabulary.

### L9 opportunity runtime

Useful classification: `useful_to_backflow_now`.

Useful idea: first cash path is a seed, not a prison; company should compare multiple money paths and align them to internal assets. Backflow into Aiden's CEO response engine, not as a packet tree.

### L10 delegated mission runtime

Useful classification: `useful_to_backflow_now`.

Useful idea: permission tiers, bounded research budget, escalation packets, delegated mission contract. Backflow as deterministic Y-star-gov domain pack and gov-mcp tools.

### Aiden chat / UX attempts

Useful classification: `useful_to_backflow_now`.

Useful idea: small Aiden conversation engine with context loader, intent classifier, meeting memory, and direct Chinese answers. Backflow into `ystar-bridge-labs/office/aiden_meeting_room/`, but ground it in original repo context instead of ystar-company summaries.

### Approval/manual-send/feedback/residual/learning candidate patterns

Useful classification: `useful_but_needs_redesign`.

Useful idea: action execution must stop at owner approval, manual-send packet, feedback, residual, review-gated learning. For now, represent these as governance classifications and Aiden reasoning. Do not migrate all packet directories.

## 5. What to backflow now

1. `ystar-bridge-labs`: add a small repo-grounded Aiden CEO Meeting Room CLI/runtime.
2. `Y-star-gov`: add a deterministic `company_runtime` domain pack for permission tiers, delegated mission contracts, escalation contracts, and company action classification.
3. `gov-mcp`: expose company runtime governance tools backed by Y-star-gov, with no external action execution.

## 6. What not to migrate

- Raw L7/L8/L9/L10 directory names.
- Giant cockpit UI.
- Packet-only demo scaffolds.
- Runtime packet history and fixture outputs.
- Fake Aiden fallback templates.
- Duplicated team definitions.
- ystar-company hardcoded localhost ports or paths.
- Any invented COO role.

## 7. No-action statement

This audit performed local file inspection only. It did not send email, contact customers, publish, pay, submit forms, execute MCP/live external behavior, write core brain/memory/canonical/CIEU DB, read secrets/env files, or read DB/WAL/SHM/log/active-agent marker contents.
