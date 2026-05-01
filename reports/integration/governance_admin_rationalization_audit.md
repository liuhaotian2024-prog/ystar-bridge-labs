# Governance/Admin Rationalization Audit

**Date:** 2026-04-30
**Scope:** `ystar-bridge-labs`, `Y-star-gov`, `gov-mcp`
**Purpose:** identify governance and administrative rules that still protect the M Triangle, and separate them from historical ceremony that now slows value production.

## Executive Finding

Y* Bridge Labs does not suffer from lack of governance. It suffers from mixed active state: core constitutional rules, historical launch calendars, stale directives, daily/weekly rituals, sales experiments, and agent learning obligations are all presented as if they are equally active. This creates a governance self-loop: agents maintain paperwork, old cadences, and historic obligations instead of producing M-3 value.

The current standard should be the M Triangle:

- **M-1 Survivability**
- **M-2 Governability**
- **M-3 Value Production**

Any active rule must defend at least one side of that triangle without crushing the others.

## KEEP_CORE_CONSTITUTIONAL

These rules directly protect the company and remain active:

- M Triangle as the top alignment test.
- Deterministic enforcement with no LLM in the ALLOW/DENY path.
- CIEU evidence preservation and auditability.
- Approval-gated external side effects: customer contact, email/message sending, publication, payment, form submission, account creation.
- Review-gated core writeback: brain, memory, canonical strategy, CIEU DB, or protected repo mutation.
- No secret/env/private DB/WAL/SHM/log/active-agent marker content reading.
- Role identity preservation and no invented COO.
- Counterfactual reasoning for Level 2/3 or permission-tier equivalent decisions.
- Maturity honesty: distinguish plan, draft, tested, shipped, and adopted.

## SIMPLIFY_ACTIVE_RUNTIME_RULE

Still useful, but currently too verbose or ceremonial:

- Iron Rule 0 should mean "no unanalyzed choice dumping"; it must not block approval controls. Owner approval requires explicit approve/reject/request_revision/hold.
- Directive decomposition remains useful, but old 10-minute universal decomposition should be mission-bound, not automatic paperwork for every historical item.
- Reporting should be evidence-backed and decision-useful, not daily prose by default.
- Work methodology should remain a checklist for important work, not a ritual that makes small reversible work impossible.
- Aiden should synthesize and recommend defaults instead of acting as a clerk who mirrors every old task.

## REPLACE_WITH_PERMISSION_TIER

These should move from hard-coded "always/never" language into the company runtime permission model:

- Read-only external research: allowed as Tier 1 when budgeted.
- Drafting outreach/content/proposals: Tier 2 preparation-only, owner-approved execution.
- Constrained external execution: future Tier 3 only with explicit pre-approval and exact scope.
- High-risk actions: Tier 4 blocked or review-gated.
- Reporting obligations: active only when mission-bound, owner-approved cadence, or evidence-critical.
- Stale legacy directives: should be re-triaged before they become active work.

## ARCHIVE_LEGACY_ADMIN

Historical but not active by default:

- OPERATIONS daily schedule tables with fixed Monday-Friday cadences.
- Old nightly/daily/weekly report requirements.
- HN/LinkedIn content calendar and article cadence.
- Old community monitoring requirements.
- Historical enterprise sales Phase 1 target list and warm-intro campaign.
- NotebookLM/books purchase task.
- Old recurring K9 daily intelligence tasks unless mission-bound.
- "All agents must report" style obligations that create paperwork without a current mission.

## MARK_SUPERSEDED

Superseded by Aiden Meeting Room, delegated mission model, permission tiers, or company runtime preflight:

- Board-facing choice prohibition that accidentally suppresses approval controls.
- Old directive tracker entries treated as active only because they remain incomplete.
- Static content calendars replaced by mission-based M-3 value production work.
- Enterprise sales plan replaced by evidence-backed money path experiments and owner approval gates.
- Report-heavy autonomous cycles replaced by delegated missions with deliverables, evidence, escalation, and residuals.

## DELETE_IF_DUPLICATE_OR_HARMFUL

Do not delete blindly in this sprint, but these should no longer be active:

- Duplicate Iron Rule 0 sections in `AGENTS.md`.
- Multiple overlapping daily/weekly schedules in `OPERATIONS.md`.
- Repeated "constitutional/non-violable" labels for administrative rituals.
- Any text implying old HN/LinkedIn/enterprise sales cadences are still mandatory.
- Any rule that makes Board/owner perform operations instead of strategic authorization.
- Any rule that makes Aiden maintain bureaucracy instead of advancing M-3.

## OWNER_DECISION_REQUIRED

Ambiguous items needing owner review before deletion:

- Patent prosecution tasks.
- Public content strategy assets with possible future commercial use.
- Academic collaboration timeline.
- Historical case-study content that may become sales evidence.
- Old K9 long-term data collection requirements.

## Old Problems Found In ystar-bridge-labs

- Aiden and the team have strong identity, but the active interface has been documents and trackers rather than a usable meeting/mission runtime.
- M Triangle exists, but M-3 Value Production is often buried under M-2 administrative rituals.
- DIRECTIVE_TRACKER mixes current work, old launch tasks, historical tasks, and owner-decision items without a re-triage layer.
- OPERATIONS still presents old daily/weekly schedules, HN/LinkedIn cadence, and enterprise sales phase as current-looking mandates.
- Reporting obligations are over-broad and can force agents into clerk mode.
- Aiden can inherit stale obligations and act like an administrator instead of CEO.
- Old "no choice questions" wording conflicts with modern approval/escalation controls.

## Old Problems Found In Y-star-gov

- Strong check/enforce/CIEU/obligation core exists.
- The new company runtime domain pack has permission tiers, but does not yet classify administrative ceremony or stale legacy directives.
- No first-class rule for "mission-bound obligation" versus "historical reporting ritual."
- No deterministic helper to archive/simplify admin burden when it lacks M Triangle alignment.

## Old Problems Found In gov-mcp

- Strong low-level governed execution exists.
- Company runtime tools classify actions, missions, escalations, and owner decisions, but do not yet flag administrative/reporting burden.
- Escalation validation allows blind option lists without requiring a recommended default.
- Mission check does not yet warn when a mission carries unnecessary reporting/admin load.

## Useful ystar-company Ideas Applied

- Aiden meeting room as a usable owner-to-CEO interface.
- Delegated mission structure instead of static document obligations.
- Permission tiers for risk-tiered autonomy.
- Escalation packet pattern for approval-needed actions.
- Manual-send, feedback, residual, and learning-candidate loops as M-3-oriented operations.
- "First cash path is seed, not prison" as a way to keep M-3 active without locking the company.

## What To Backflow Now

- Concise active operating charter in `ystar-bridge-labs`.
- Re-triage layer for `DIRECTIVE_TRACKER.md`.
- Aiden Meeting Room awareness of active charter and legacy burden.
- Admin-rule classification helpers in `Y-star-gov` company runtime domain.
- gov-mcp company runtime tool alignment for admin/reporting actions and escalation recommendations.

## What Not To Migrate

- Raw L7/L8/L9/L10 directory names.
- Giant cockpit UI.
- Demo-only packet directories.
- Packet-only scaffolding.
- Duplicate legacy team definitions.
- Invented COO.
- ystar-company hardcoded paths.
- Tests that only prove files exist.

## Rationalization Decision

This sprint should not reduce governance. It should reduce governance drag. The active rule set should become smaller, clearer, and more executable, while high-risk actions remain strictly approval-gated or review-gated.
