# Governance Audit & Restructure — Joint CEO + Secretary Proposal

**Audience**: Board (Haotian Liu) for feasibility decision; all agents for reference after approval; consultants reviewing Y* Bridge Labs' internal governance maturity.
**Research basis**: CEO-side 12-domain coverage matrix (`reports/ceo/governance/governance_coverage_audit_v1_ceo_side.md`); Secretary-side 40-file inventory + duplicate + dead-ref + staleness audit (`reports/secretary/governance_audit_and_restructure_v1_secretary_side.md`); empirical 2026-04-19 session evidence (3 concrete governance-gap failures: wrong-role AGENTS.md dispatch / 6-day silent `must_dispatch_via_cto` disablement / whiteboard 37→0 wipe incident this session).
**Synthesis**: governance at Y* Bridge Labs is **document-heavy, enforce-light, and archive-absent**. The CEO-view shows 6/12 governance domains are Partial or No-enforce; the Secretary-view shows 40 files with 8 orphans + 3 dead refs + 8 duplicate clusters + no ARCHIVE_INDEX. Both halves independently diagnose the same condition. Today's 3 live failures are the concrete consequence. A restructure from flat docs → 4-tier (charter / enforced / protocols / archive) with ARCHIVE_INDEX as the top-level navigation fixes the architecture; a Top-5 prioritized fix list gets immediate wins in one workday.
**Purpose**: give Board a single consolidated feasibility plan to approve — method + scope + phased execution + risks + success criteria — so Phase 1 (pilot + fixes) can start same-session.

**Authors**: Aiden Liu (CEO, methodology + coverage matrix) + Samantha Lin (Secretary, archive inventory + staleness + categorization)
**Date**: 2026-04-19
**Status**: [L2] FEASIBILITY PROPOSAL — Board review → approve/adjust before Phase 1 starts
**Authority**: Board directive 2026-04-19 ("让秘书和你一起来检查一次我们现在的需要被执行治理的内容是否够全...应该进行一次文档的重新的新建和重构")

---

## 1. Executive Summary (30 seconds)

- **Diagnosis**: governance is 6/12 under-enforced (CEO view) AND 40 files are un-indexed with 8 orphans + 8 duplicates + 3 dead refs (Samantha view). Both views converge.
- **Today's evidence**: wrong-role dispatch (charter amendment) · 6-day silent rule-off (must_dispatch_via_cto) · 37→0 whiteboard wipe (this session).
- **Fix**: 4-tier restructure (`charter/` · `enforced/` · `protocols/` · `archive/`) + ARCHIVE_INDEX.md + 5-item priority list.
- **Pilot live**: CZL-CHARTER-FLOW-RULE-PILOT (Maya running now) validates the methodology on one rule before batch migration.
- **Cost**: ~6 engineer-sub-agent spawns to finish Phase 1 (pilot + Top-5 fixes). Phase 2-3 scoped separately.
- **Ask Board**: approve the plan shape + Top-5 priority order.

---

## 2. Merged Coverage + Documentation Gaps

### 2A. Coverage Gaps (CEO view — 12 governance domains)

| Domain | Documented | Machine-enforced? | Fix card |
|---|---|---|---|
| Charter amendment flow | BOARD_CHARTER_AMENDMENTS.md header | **Partial** | CZL-CHARTER-FLOW-RULE-PILOT (in flight) |
| must_dispatch_via_cto | AGENTS.md + feedback memory | **LIVE** (today) | CZL-HOOK-DISPATCH-RESIDUAL posted |
| Whiteboard dispatch pipe | governance/cto_role_v2_and_dispatch_board_20260416.md | **LIVE** (today) | CZL-DISPATCH-EXEC complete |
| Directive liveness | (none before today) | **LIVE** (today) | CZL-GOV-LIVE-EVAL complete |
| CIEU receipt discipline | AGENTS.md + feedback | Partial | (new card needed) |
| Agent role write scope | AGENTS.md + restricted_write_paths | Partial → LIVE (AMENDMENT-020 landing) | CZL-AGENTS-ENGREG-GAP / AMENDMENT-020 |
| Iron Rule 0 (no choice Q) | CLAUDE.md + ForgetGuard | LIVE | — |
| Atomic dispatch (Iron Rule 0.5) | ceo_dispatch_self_check.md | Partial | (new card) |
| Commit-push integrity | AGENTS.md:1027 | Partial | (new card) |
| Idle learning loop | AMENDMENT-003 | LIVE | — |
| Cross-review (Directive #023) | AGENTS.md:967 | Partial | (new card) |
| Shadow-path lock-death | 10-path memory | Partial (1 of 10 fixed today) | 9 remaining cards |

**After today**: 4 domains moved from Partial/NO → LIVE in one session. 5 Partials + 1 No-enforce remain.

### 2B. Documentation State (Secretary view — 40 files)

| Symptom | Count | Sample |
|---|---|---|
| No ARCHIVE_INDEX.md | 1 missing | (top-level navigation absent — root cause of "messy" feel) |
| Orphan files (0 inbound refs) | 8 | CALENDAR.md, CSO_INTEL_PROTOCOL.md, INNER_DRIVE_PROTOCOL.md, 5 more |
| Real dead references | 3 | active_dispatch_log.md → croba_false_positive...; skill_trust_hybrid_v1.md → 2 missing |
| Placeholder dead refs (code examples) | 5 | — (ignorable) |
| Duplicate-concept clusters | 8 | 3 require merge, 4 require supersession markers, 1 fine |
| Staleness candidates | 13 | 7 reminders/*.md + CIEU_VIDEO_METHODOLOGY.md + cto_system23_takeover_v1.md + 4 more |

**After Phase 1 Top-5 fixes**: ARCHIVE_INDEX exists + 4 merges done + 13 files moved to archive/ + 4 supersession headers + 3 dead refs fixed = **40 → ~27 active files + proper indexing**.

---

## 3. Proposed 4-Tier Hierarchy (final — Samantha's variant applied)

```
governance/
├── charter/           ← Board-authority; Secretary-write-only
│   ├── AGENTS.md              (symlink/stub)
│   ├── BOARD_CHARTER_AMENDMENTS.md
│   ├── CLAUDE.md              (symlink/stub)
│   └── ARCHIVE_INDEX.md       ← NEW: top-level navigator, Secretary-owned
├── enforced/          ← Machine-readable, ingested by enforce-router + ForgetGuard + whitelist
│   ├── rules/                 ← *.rule.yaml — detector + executor pairs
│   │   └── charter_amendment_flow.rule.yaml   (CZL-CHARTER-FLOW-RULE-PILOT target)
│   ├── whitelist/             ← moved from governance/whitelist/
│   │   ├── agent_caller_whitelist.yaml
│   │   ├── restricted_writers.yaml
│   │   └── ...
│   ├── logs/                  ← auto-written, NOT human-authored
│   │   ├── active_dispatch_log.md
│   │   ├── dashboard/
│   │   └── escalations.json
│   └── README.md       ← how to write a .rule.yaml
├── protocols/         ← Human-readable, each MUST be referenced by ≥1 .rule.yaml
│   ├── cross_review.md
│   ├── cieu_receipt_schema.md
│   ├── atomic_dispatch.md
│   ├── (others kept after dedup)
│   └── README.md
└── archive/           ← Deprecated, kept for history; Secretary-write-only
    ├── daemon_retirement_2026-04-xx.md
    ├── 13 files from staleness audit
    └── ...
```

### Invariants (governance-rule-of-governance-docs)

- Every `protocols/*.md` MUST be referenced by at least one `enforced/rules/*.rule.yaml`. Orphans are moved to `archive/` in quarterly audit.
- Every `enforced/rules/*.rule.yaml` MUST cite a `protocols/*.md` for human context.
- **Enforce-as-source-of-truth**: in case of conflict between prose and rule, the rule wins. Prose is updated to match.
- `charter/ARCHIVE_INDEX.md` is the required entry point — every agent boot validates its existence via a check primitive (reuses CZL-GOV-LIVE-EVAL's `doc_exists` primitive).

---

## 4. Top-5 Priority Fixes (Phase 1 — same workday target)

Order reflects dependency + ROI (Samantha-proposed, CEO-validated):

| # | Fix | Owner | Effort | Why this order |
|---|---|---|---|---|
| 1 | Create `governance/ARCHIVE_INDEX.md` (Secretary catalogs all 40 files with status/category) | Samantha | 6 tool_uses | Unblocks all other audits; removes the "messy" feeling in one stroke |
| 2 | Merge 4 small CEO-dispatch protocol docs into one canonical `atomic_dispatch.md` | Samantha | 8 tool_uses | Dup cluster with highest noise; enables router rule authoring |
| 3 | Move 13 staleness candidates to `archive/` with supersession headers | Samantha | 6 tool_uses | Surface-area reduction without info loss |
| 4 | Add supersession headers to 4 cluster pairs (non-moved dups) | Samantha | 4 tool_uses | Preserves content, fixes navigation |
| 5 | Fix 3 real dead references | Samantha or Ryan | 3 tool_uses | Removes broken-link friction |

**All Phase 1 items are Secretary-scope** except #5 (Ryan optional). Samantha can ship in one atomic multi-deliverable run after Board ack.

---

## 5. Phased Execution

- **Phase 0 (done today)**: CEO audit + Secretary audit + this joint proposal. Board review next.
- **Phase 1 (1 workday after Board ack)**: Top-5 fixes + pilot CZL-CHARTER-FLOW-RULE-PILOT ship. Validates methodology.
- **Phase 2 (next week)**: Extract next 5 protocols → rule.yaml migrations (subset of CZL-P2-d scope). Each migration requires pilot's success criteria met.
- **Phase 3 (ongoing)**: Full CZL-P2-d — batch-migrate remaining protocols. Quarterly archive audit cadence established.

---

## 6. Risks & Safeguards

| Risk | Safeguard |
|---|---|
| Restructure breaks existing file-path refs in code | 30-day forwarding symlinks for every moved file; then delete after audit |
| Over-formalization (trivial protocol becomes rigid rule) | Threshold: protocol stays prose unless 2+ enforce gaps observed (today we have evidence for 6) |
| Samantha + CEO diverge on categorization | Conflicts default to CEO judgment until Board adjudicates |
| Archive loses relevant history | Every archive move has a supersession header pointing to the replacement |
| Router rule bugs cause governance lock-death | Every new rule ships with live-fire smoke + 15-min rollback plan (pilot validates this) |
| Concurrent-write corruption (today's whiteboard wipe) | CZL-WHITEBOARD-WIPE-RCA posted P0 — atomic-write pattern + sanity check will be mandatory for all governance state files |

---

## 7. Board Asks (3 yes/no decisions)

1. **Approve the 4-tier hierarchy shape** (charter / enforced / protocols / archive, with Samantha's variant on machine-readable files going to `enforced/`)? 
2. **Approve Top-5 priority order** (ARCHIVE_INDEX first, Samantha as main owner)?
3. **Approve Phase 1 start after Board ack** (1 workday), with pilot completion as gate to Phase 2?

No choice questions — each is a yes/no with a clear default. Board silence > 12h = default ack per autonomous-operation rules; CEO proceeds to Phase 1.

---

## 8. Success Criteria

- **Phase 1 L4**: Top-5 fixes shipped + pilot .rule.yaml live + CIEU events prove `CHARTER_FLOW_REDIRECT` fires on wrong-role AGENTS.md attempts.
- **Phase 2 L4**: 5 more rule.yaml migrations + quarterly archive cadence documented in charter/ARCHIVE_INDEX.md.
- **Phase 3 L5**: 30 days run with 0 Board-initiated "is X still enforced?" questions + 0 document-reality drift alarms from the enforcement observer.
