# Governance Coverage Audit — CEO Side (joint with Secretary)

**Audience**: Board (Haotian Liu); Secretary (Samantha) for her complementary half; future sessions inheriting the audit methodology.
**Research basis**: empirical evidence from 2026-04-19 session (CEO dispatch errors caught post-hoc by hook, 6-day silent `must_dispatch_via_cto` disablement found by Ryan, subscriber claim-no-spawn stub, CEO routing AGENTS.md edit to wrong role); governance/*.md count 40 files; AGENTS.md 1145 lines; BOARD_CHARTER_AMENDMENTS.md 375 lines; .ystar_session.json 1K+ lines; CLAUDE.md 207 lines; 26 AMENDMENTS filed to date.
**Synthesis**: governance content is currently **document-heavy, enforce-light**. What an agent reads at boot ≠ what an agent is actually prevented from violating. Today's 3 concrete failures (modifying AGENTS.md routed to wrong role / stale `board_ceo_override` sat 6 days silently / 5 whiteboard cards dead-water) are all **symptoms of the same class**: protocols live in prose, not in executable rules. Restructure is warranted but must be preceded by coverage audit so we know *what to keep, formalize, and delete*.
**Purpose**: propose feasibility approach for (1) governance coverage audit methodology, (2) restructure shape, (3) joint CEO+Secretary execution plan. This document is the CEO half; Samantha's complementary half covers documentation archive state + duplicates + staleness from her custodial perspective.

**Author**: Aiden Liu (CEO)
**Date**: 2026-04-19
**Status**: [L1] PROPOSAL — Board review before execution
**Authority**: Board directive 2026-04-19 ("让秘书和你一起来检查一次我们现在的需要被执行治理的内容是否够全,还有是否应该进行一次文档的重新的新建和重构")

---

## 1. Coverage Matrix (CEO view — 12 governance domains)

Classification columns:
- **Documented**: where the protocol is currently written (file + section)
- **Machine-enforced**: Y/N + how (hook/router/ForgetGuard/ObligationEngine)
- **Gap evidence 2026-04-19**: concrete miss from today's session
- **Proposed target state**: after restructure

| Domain | Documented | Machine-enforced? | Gap today | Target |
|---|---|---|---|---|
| **Charter amendment flow** | BOARD_CHARTER_AMENDMENTS.md header + AGENTS.md:941 | Partial (hook blocks non-secretary writes, but no REDIRECT to Samantha) | CEO routed AGENTS.md edit to Ethan (wrong role); only caught post-hoc | Router rule: detect intent → REDIRECT to Samantha |
| **Must-dispatch-via-CTO** | AGENTS.md + feedback memory | LIVE now (fixed by Ryan today), but 6 days silent; aliases still missing | display-name spawns (`Leo-Kernel`) not mapped to canonical (`eng-kernel`) → detector misses | aliases land + CIEU live-fire smoke |
| **Whiteboard dispatch pipe** | governance/cto_role_v2_and_dispatch_board_20260416.md | NO — subscriber is stub | 5 cards claimed, 0 executing | CZL-DISPATCH-EXEC Pattern C ship |
| **Directive liveness** | no prior protocol | NO | P2 pause sat 2 days after release cond met | CZL-GOV-LIVE-EVAL Phase 1 (Maya in flight) |
| **CIEU receipt discipline** | AGENTS.md + feedback memory | Partial (CIEU event required, content not validated) | sub-agent receipts occasionally prose-only (memory warns but no hook) | receipt schema validator + hook check |
| **Agent role write scope** | AGENTS.md agent block + .ystar_session.json restricted_write_paths | LIVE (hook enforces) | eng-* roles not individually registered (AMENDMENT-020 fixes today) | AMENDMENT-020 lands |
| **Iron Rule 0 (no choice Q)** | CLAUDE.md + ForgetGuard | LIVE | — (hook catches) | — |
| **Atomic dispatch (Iron Rule 0.5)** | AGENTS.md ceo_dispatch_self_check.md | Partial (self-check not machine-verified) | CEO self-check claim ≠ actual compliance | detector on Agent call payload |
| **Commit-push integrity (Directive #022)** | AGENTS.md:1027 | Partial (30-min SLA not auto-escalated) | many unpushed commits in .git state (not today's issue but structural) | cron + CIEU age-check |
| **Idle learning loop (AMENDMENT-003)** | AGENTS.md | LIVE (GOV-009 obligation) | — | — |
| **Cross-review (Directive #023)** | AGENTS.md:967 | Partial (SLA auto-escalate absent) | self-approval possible in fast-spawn workflow | cross-review obligation on Agent returns |
| **Shadow-path lock-death** | 10-path memory note + CEO lessons | Partial (path #8 symlink fixed today; others untested) | 10 paths enumerated, only 1-2 tested live | live-fire for each path |

**Reading**: 6 of 12 domains are Partial or NO enforce. The Partial cases are precisely where today's failures occurred.

---

## 2. Restructure Shape (proposal)

Currently `governance/` is a flat directory of 40 .md files with overlapping content (many reference each other, some supersede without deleting, some are drafts beside finals).

Proposed 4-tier hierarchy:

```
governance/
├── charter/           ← Constitutional (Board-authority only)
│   ├── AGENTS.md                           (symlink/ref)
│   ├── BOARD_CHARTER_AMENDMENTS.md
│   └── CLAUDE.md                           (symlink/ref)
├── enforced/          ← Machine-readable, ingested by enforce-router
│   ├── charter_amendment_flow.rule.yaml    ← today's pilot
│   ├── must_dispatch_via_cto.rule.yaml
│   ├── dispatch_post_and_spawn.rule.yaml
│   ├── ...
│   └── README.md   (how to write a rule)
├── protocols/         ← Human-readable, referenced from .rule.yaml
│   ├── cross_review.md
│   ├── cieu_receipt_schema.md
│   ├── atomic_dispatch.md
│   └── ...
└── archive/           ← Deprecated, kept for history only
    ├── daemon_retirement_2026-04-xx.md
    └── ...
```

**Migration rule**: every `.rule.yaml` in `enforced/` MUST reference a `protocols/*.md` for human context. Every `protocols/*.md` MUST be referenced by at least one `.rule.yaml` — else it moves to `archive/` or gets deleted.

**Enforced-as-source-of-truth**: in case of conflict between prose in `protocols/` and executable rule in `enforced/`, the rule wins. Prose is updated to match. This eliminates "docs say X, hook does Y" drift.

---

## 3. Execution Plan (joint CEO + Secretary)

### Phase 1 — Audit (this week, L3 target)

**CEO (me)** responsibilities:
- Coverage matrix above ✓ (this doc)
- Cross-check each `Partial` / `NO` row against existing work-in-flight (CZL-DISPATCH-EXEC, CZL-GOV-LIVE-EVAL, CZL-BRAIN-BIPARTITE, CZL-P2-d)
- Propose new atomic cards for uncovered gaps
- Draft the final joint audit with Samantha

**Samantha (Secretary)** responsibilities (dispatched separately):
- Inventory all 40 governance/*.md files: created-when / last-modified / referenced-by-whom / supersedes-what
- Duplicate detection (same concept in multiple files)
- Broken reference detection (file A says "see file B" but B doesn't exist)
- Staleness audit (files >30 days stale with no incoming references)
- Her judgment on which files go to charter/ / enforced-source / protocols/ / archive/

**Joint deliverable**: single report `reports/joint/governance_audit_and_restructure_proposal.md` — combining both halves.

### Phase 2 — Pilot (after audit)

Execute CZL-CHARTER-FLOW-RULE-PILOT (proposed below). Proof-of-concept for one rule migration end-to-end: protocol → enforced rule → live-fire smoke → receipt. This validates the methodology before batch migration.

### Phase 3 — Batch migration (CZL-P2-d expanded scope)

With pilot done, run the 40-file migration through the methodology. Not starting here.

---

## 4. Risks & Safeguards

| Risk | Safeguard |
|---|---|
| Restructure breaks existing references | every file move logs a forwarding symlink for 30 days, then delete |
| Over-formalization — trivial protocols become rigid rules | "protocol stays prose unless 2+ enforcement gaps observed" threshold |
| Audit finds too many gaps, scope creep | cap Phase 1 audit at 2 rounds per agent, Board-review scope before Phase 3 |
| Samantha + CEO diverge on categorization | conflicts default to CEO rules until Board adjudicates |
| Enforce rule bugs cause governance lock-death | every new rule ships with live-fire smoke + 15-min rollback plan |

---

## 5. Ask of Board

1. Approve joint audit methodology (Samantha-Secretary to produce complementary half).
2. Approve pilot — CZL-CHARTER-FLOW-RULE-PILOT as the first migration, proves methodology.
3. After pilot + audit, Board reviews combined proposal → approves/adjusts restructure shape → then Phase 3.

Board's "没纳入治理层" diagnosis is correct and actionable. This is the scaffolding to move from document-heavy to enforce-first without breaking what works.
