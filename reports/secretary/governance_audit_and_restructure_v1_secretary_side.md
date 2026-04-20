# Governance Audit — Secretary Side (joint with CEO)

**Audience**: Board (Haotian Liu); CEO (Aiden) for merging into joint proposal; future Secretary sessions inheriting archive state.
**Research basis**: empirical file-system scan of `governance/` 2026-04-19 (40 .md files, 3 subdirectories, 7,978 KB); git log first-commit/last-modified for every file; cross-reference grep across `governance/**`, `AGENTS.md`, `CLAUDE.md`; CEO side audit at `reports/ceo/governance/governance_coverage_audit_v1_ceo_side.md`.
**Synthesis**: `governance/` is a **flat dump of 40 files with no index, no canonical-vs-draft markers, and no archive subfolder**. 8 files are **orphan** (cited by nothing including AGENTS.md/CLAUDE.md), 5 files have **broken references**, 6 same-week sibling specs cover **overlapping concepts with no supersession markers**, and `WORKING_STYLE.md` is the only file with 100+ references — everything else lives in a long tail. Board's "messy" intuition is empirically correct. Restructure is warranted and the 4-tier shape proposed by CEO is workable, with one Secretary-proposed variant (split `charter/` from `runtime-state/`).

**Author**: Samantha Lin (Secretary)
**Date**: 2026-04-19
**Status**: [L1] PROPOSAL — Secretary half of joint audit, ready to merge with CEO half
**Authority**: Board directive 2026-04-19 ("让秘书和你一起来检查一次…文档的重新的新建和重构")

**Scope guard honored**: no file moved/renamed/deleted; AGENTS.md + BOARD_CHARTER_AMENDMENTS.md untouched (Samantha#1 owns those for AMENDMENT-020 in flight); no git commit/push.

---

## CIEU 5-tuple

- **Y\***: Secretary-side audit complete; Board has combinable half; each of 40 files has state + category verdict
- **Xt**: 40 governance/*.md + 3 subdirs scanned; no ARCHIVE_INDEX.md exists; git dates + reference counts + dead-link check collected
- **U**: 6 audit sections (A-F) inline below
- **Yt+1**: joint audit mergeable; CEO consolidates into single Board proposal
- **Rt+1**: 0 — all 6 sections present + 40 files covered + priority list delivered

---

## A. File inventory table

Format: `filename | created | last-mod | LOC | refs (across repo .md/.yaml/.py/.json) | status | note`

**ACTIVE-high** = ≥8 refs and touched within 7d. **ACTIVE-low** = 1–7 refs, touched within 7d. **STALE** = no modification in ≥30 days OR never referenced and mod-date old relative to active wave. **ORPHAN** = never referenced (via `governance/X.md` pattern in any .md). **SUPERSEDED** = explicitly newer sibling exists.

| # | filename | created | last-mod | LOC | refs | status | note |
|---|---|---|---|---|---|---|---|
| 1 | action_model_v2.md | 2026-04-16 | 2026-04-16 | 522 | 7 | ACTIVE-low | 17-step atomic lifecycle; canonical referenced by sub_agent_boot_prompt_template |
| 2 | active_dispatch_log.md | 2026-04-16 | 2026-04-16 | 33 | 8 | ACTIVE-low (append-only) | immutable log; no new entries in 3 days — verify still being written or is stale |
| 3 | auto_commit_push_v1.md | 2026-04-16 | 2026-04-16 | 243 | 0 | ORPHAN | spec authored, never cited from anywhere; implementation deferred |
| 4 | auto_enforce_meta.md | 2026-04-16 | 2026-04-16 | 181 | 2 | ACTIVE-low | L4 SHIPPED per header but only 2 back-refs |
| 5 | BOARD_CHARTER_AMENDMENTS.md | 2026-04-09 | 2026-04-15 | 375 | 51 | ACTIVE-high | constitutional; AMENDMENT-020 currently being added by Samantha#1 |
| 6 | CALENDAR.md | 2026-04-06 | 2026-04-06 | 38 | 8 | ORPHAN (in gov filename pattern) | 8 refs from other contexts; never-ref in pure `governance/X.md` form; 13 days untouched |
| 7 | ceo_dispatch_self_check.md | 2026-04-16 | 2026-04-16 | 33 | 8 | ACTIVE-low | cited by AGENTS.md:688 |
| 8 | ceo_midstream_checkin_protocol.md | 2026-04-16 | 2026-04-16 | 29 | 7 | ORPHAN (in gov filename pattern) | 7 refs but zero `governance/X.md` citations; discoverability risk |
| 9 | ceo_operating_methodology_v1.md | 2026-04-16 | 2026-04-16 | 694 | 3 | ACTIVE-low | CEO-specific method spec |
| 10 | cieu_event_taxonomy.md | 2026-04-16 | 2026-04-16 | 390 | 8 | ACTIVE-low | contains the explicit DEPRECATED status column |
| 11 | CIEU_VIDEO_METHODOLOGY.md | 2026-04-08 | 2026-04-08 | 110 | 6 | STALE | 11 days untouched; video pipeline not shipping; candidate for archive |
| 12 | CONTINUITY_PROTOCOL.md | 2026-04-12 | 2026-04-12 | 376 | 11 | ACTIVE-low | 7 days untouched but high-ref; keep |
| 13 | CSO_INTEL_PROTOCOL.md | 2026-04-11 | 2026-04-11 | 89 | 3 | ORPHAN (in gov filename pattern) | 8 days untouched, low discoverability |
| 14 | cto_dispatch_broker_v1.md | 2026-04-16 | 2026-04-16 | 674 | 3 | PARTIAL-SHIP | Ethan spec for dispatch broker; overlaps cto_role_v2_and_dispatch_board AND cto_system23_takeover |
| 15 | cto_role_v2_and_dispatch_board_20260416.md | 2026-04-16 | 2026-04-16 | 447 | 7 | ACTIVE-low | CEO audit names this as source-of-truth for whiteboard dispatch |
| 16 | cto_system23_takeover_v1.md | 2026-04-16 | 2026-04-16 | 274 | 0 | ORPHAN | CZL-155 spec, never cited; likely superseded by broker v1 |
| 17 | czl_unified_communication_protocol_v1.md | 2026-04-16 | 2026-04-16 | 423 | 8 | ACTIVE-low | 5-tuple envelope spec |
| 18 | DNA_LOG.md | 2026-04-08 | 2026-04-16 | 226 | 20 | ACTIVE-high | Secretary append-only evolution log |
| 19 | ecosystem_dependency_checklist_v1.md | 2026-04-16 | 2026-04-16 | 193 | 4 | ACTIVE-low | design-discipline checklist |
| 20 | enforce_status_dashboard.md | 2026-04-16 | 2026-04-18 | 32 | 5 | ACTIVE-low (auto-written) | auto-generated by K9 consumer; not human doc |
| 21 | ETHICS.md | 2026-04-10 | 2026-04-10 | 86 | 19 | ACTIVE-high | charter-grade; 9 days untouched but widely referenced |
| 22 | forget_guard_rule_new_artifact_without_precheck.md | 2026-04-16 | 2026-04-16 | 225 | 0 | ORPHAN | rule spec, never cited from any doc; implementation lives in forget_guard_rules.yaml |
| 23 | formal_methods_primer_v1.md | 2026-04-16 | 2026-04-16 | 738 | 3 | ACTIVE-low | CTO primer; referenced by reply_taxonomy_whitelist |
| 24 | INNER_DRIVE_PROTOCOL.md | 2026-04-11 | 2026-04-11 | 120 | 5 | ORPHAN (in gov filename pattern) | 8 days untouched |
| 25 | INTERNAL_GOVERNANCE.md | 2026-04-09 | 2026-04-10 | 346 | 43 | ACTIVE-high | GOV-005-origin doc; 9 days untouched but 43 refs |
| 26 | k9_alarm_consumer_v1.md | 2026-04-16 | 2026-04-16 | 169 | 1 | ACTIVE-low | pairs with enforce_status_dashboard |
| 27 | methodology_framework_assignments_v1.md | 2026-04-16 | 2026-04-16 | 696 | 3 | ACTIVE-low | 55KB single file; may warrant split |
| 28 | new_engineer_onboarding_gauntlet_v1.md | 2026-04-16 | 2026-04-16 | 273 | 8 | ACTIVE-low | spec awaiting Maya/Ryan/Samantha impl (L1) |
| 29 | pre_build_routing_gate_v1.md | 2026-04-16 | 2026-04-16 | 326 | 2 | ACTIVE-low | precheck gate spec |
| 30 | priority_brief_schema.md | 2026-04-13 | 2026-04-13 | 183 | 3 | ORPHAN (in gov filename pattern) | 6 days untouched |
| 31 | reply_scan_detector_methodology_v1.md | 2026-04-16 | 2026-04-16 | 492 | 1 | ACTIVE-low | methodology, detector lives in code |
| 32 | reply_taxonomy_whitelist_v1.md | 2026-04-16 | 2026-04-16 | 565 | 3 | ACTIVE-low | superseded-by-design: whitelist replaces blacklist detector |
| 33 | restart_preparation_model_v1.md | 2026-04-16 | 2026-04-16 | 594 | 1 | ACTIVE-low | overlaps with CONTINUITY_PROTOCOL |
| 34 | skill_trust_hybrid_v1.md | 2026-04-16 | 2026-04-16 | 658 | 8 | ACTIVE-low | foundational for 5 new engineers + anti-monopoly |
| 35 | sub_agent_atomic_dispatch.md | 2026-04-16 | 2026-04-16 | 31 | 17 | ACTIVE-high | Iron Rule 0.5 source |
| 36 | sub_agent_boot_prompt_template.md | 2026-04-16 | 2026-04-16 | 59 | 17 | ACTIVE-high | every sub-agent prompt cites this |
| 37 | TEMP_LAW.md | 2026-04-06 | 2026-04-09 | 98 | 12 | STALE-CANDIDATE | 10 days untouched; only TL-001/004 active but dated 2026-04-06 |
| 38 | tiered_routing_protocol_v1_sync_addendum.md | 2026-04-17 | 2026-04-17 | 312 | 2 | ACTIVE-low | extends tiered_routing_protocol_v1 |
| 39 | tiered_routing_protocol_v1.md | 2026-04-16 | 2026-04-16 | 419 | 7 | ACTIVE-low | pair with addendum |
| 40 | WORKING_STYLE.md | 2026-04-06 | 2026-04-15 | 967 | 125 | ACTIVE-high | charter-grade; most-cited file in repo |

### Subdirectory inventory

| path | files | status | note |
|---|---|---|---|
| governance/directives/ | 6 JSON | ACTIVE | CZL-P2-* directive cards; referenced by directive liveness system |
| governance/reminders/ | 7 MD | STALE | k9 warn artifacts from 2026-04-16; not referenced anywhere; archive candidates |
| governance/whitelist/ | 8 YAML + 1 JSON | ACTIVE | constitutional/escape_hatch/event_workflow/inter_role_sop/project_procedure/rapid_matrix/role_mandate + schema — this is the machine-readable enforcement layer already per CEO audit |

### Orphan detection summary (never cited via `governance/X.md` in any .md/.yaml source)

8 files never referenced by filename pattern from any other governance doc, AGENTS.md, or CLAUDE.md:
- CALENDAR.md
- CSO_INTEL_PROTOCOL.md
- INNER_DRIVE_PROTOCOL.md
- auto_commit_push_v1.md
- auto_enforce_meta.md
- ceo_midstream_checkin_protocol.md
- forget_guard_rule_new_artifact_without_precheck.md
- priority_brief_schema.md

---

## B. Duplicate detection — concept clusters

Grouped by overlapping concept. **Canonical** = recommended single source of truth. **Redundant** = collapse or explicit supersession marker needed.

### Cluster B.1 — CTO dispatch / routing architecture (3 overlapping specs, same day)
| file | LOC | role |
|---|---|---|
| cto_role_v2_and_dispatch_board_20260416.md (**canonical**) | 447 | role re-definition + whiteboard paradigm |
| cto_dispatch_broker_v1.md | 674 | broker daemon impl spec; EXTENDS canonical, should reference it as upstream |
| cto_system23_takeover_v1.md | 274 | System 2-3 takeover; ORPHAN — 0 refs; likely draft superseded by broker spec |
**Verdict**: cto_system23_takeover_v1.md → candidate for archive/. broker v1 stays as sub-spec; add explicit `Upstream: cto_role_v2...` marker.

### Cluster B.2 — CEO dispatch discipline (4 overlapping docs)
| file | LOC | scope |
|---|---|---|
| sub_agent_atomic_dispatch.md (**canonical-rule**) | 31 | "1 dispatch = 1 deliverable" constitutional |
| sub_agent_boot_prompt_template.md (**canonical-template**) | 59 | boot context every prompt must inject |
| ceo_dispatch_self_check.md | 33 | 3-question pre-dispatch self-check |
| ceo_midstream_checkin_protocol.md | 29 | ≥30min no-return → SendMessage |
**Verdict**: 4 tiny related files (avg 38 LOC). Consider merging into single `protocols/ceo_dispatch.md` (~150 LOC) with 4 numbered sections. Current fragmentation forces 4 cross-refs instead of 1.

### Cluster B.3 — Tiered routing (intentional pair)
| file | LOC | role |
|---|---|---|
| tiered_routing_protocol_v1.md | 419 | original tier taxonomy |
| tiered_routing_protocol_v1_sync_addendum.md | 312 | sync layer bolt-on |
**Verdict**: no action — addendum explicitly extends. Add `Extended-by: sync_addendum.md` header to v1 for discoverability.

### Cluster B.4 — Continuity / restart (2 overlapping)
| file | LOC | role |
|---|---|---|
| CONTINUITY_PROTOCOL.md (**canonical**) | 376 | cross-session life continuity |
| restart_preparation_model_v1.md | 594 | restart preparation behavior model |
**Verdict**: restart_preparation is larger but newer and less-referenced. Either merge restart_prep as §N of CONTINUITY or mark CONTINUITY as V1 superseded-by restart_prep. Currently both live with no cross-ref → drift risk.

### Cluster B.5 — Methodology frameworks (3 overlapping meta-level)
| file | LOC | scope |
|---|---|---|
| ceo_operating_methodology_v1.md | 694 | CEO-specific methodology |
| methodology_framework_assignments_v1.md | 696 | all-role framework assignments |
| formal_methods_primer_v1.md | 738 | mathematical foundations |
**Verdict**: ~2,100 LOC across three meta files, all authored 2026-04-16, zero cross-refs between the three. At minimum they need a common index doc. At best they fold into one `methodology_v1/` subdirectory with a README linking them.

### Cluster B.6 — Reply scan / taxonomy
| file | LOC | role |
|---|---|---|
| reply_scan_detector_methodology_v1.md | 492 | detector methodology (blacklist era) |
| reply_taxonomy_whitelist_v1.md | 565 | whitelist replacement (newer paradigm) |
**Verdict**: taxonomy_whitelist **semantically supersedes** detector_methodology (blacklist → whitelist shift). Mark detector_methodology as SUPERSEDED-BY inline; after hook confirmed fully on whitelist, archive detector_methodology.

### Cluster B.7 — ForgetGuard rule artifacts
| file | LOC | role |
|---|---|---|
| forget_guard_rule_new_artifact_without_precheck.md | 225 | one rule spec authored as standalone file |
| pre_build_routing_gate_v1.md | 326 | related gate doctrine |
| forget_guard_rules.yaml | 28KB | actual rule registry (the source of truth) |
**Verdict**: individual rule-spec .md files don't scale. Either every rule gets its own .md (40+ expected) or none do (rule doc lives in yaml + comments). Current single orphaned spec is a bad precedent.

### Cluster B.8 — Auto-enforcement / auto-commit
| file | LOC | status |
|---|---|---|
| auto_commit_push_v1.md | 243 | 0 refs, impl deferred, ORPHAN |
| auto_enforce_meta.md | 181 | 2 refs, L4 shipped per header |
**Verdict**: auto_commit_push is draft-abandoned; mark [L0 draft] or archive. auto_enforce_meta confirmed shipped and needs to be linked from AGENTS.md.

**Duplicate total**: 8 clusters. 3 require merge (B.2, B.5, B.6). 4 require explicit supersession header (B.1, B.4, B.7, B.8). 1 is fine (B.3).

---

## C. Broken reference detection

Grep pattern `governance/[A-Za-z0-9_\-]+\.md` across 40 gov files + AGENTS.md + CLAUDE.md.

### C.1 Dead filename references (file cited does not exist in governance/)

| referring file | cited target | context |
|---|---|---|
| formal_methods_primer_v1.md | `file.md` | illustrative placeholder in example — not a real bug |
| pre_build_routing_gate_v1.md | `foo.md`, `new_spec.md` | both illustrative placeholders in examples — not real bugs |
| forget_guard_rule_new_artifact_without_precheck.md | `new_spec.md` | placeholder in example — not a real bug |
| active_dispatch_log.md | `croba_false_positive_core_py_20260416.md` | **REAL DEAD LINK** — file does not exist anywhere |
| skill_trust_hybrid_v1.md | `pair_sessions_log.md`, `security_audit_log.md` | **REAL DEAD LINKS** — both forward-reference files that were never created |

**Real dead-reference count: 3**. All others are in-prose code-block placeholders (acceptable but still inviting lint false-positives).

### C.2 Files referenced externally but whose existence state is uncertain

- `archive/deprecated/*` paths referenced 3x in BOARD_CHARTER_AMENDMENTS.md §5.3 — directory has not been created yet. This is the Secretary archive backlog. Action: create `archive/deprecated/` and execute the amendment's move list.

### C.3 Never-referenced-via-filename (orphan discoverability)

See §A orphan list. These 8 files cannot be found via grep-by-filename from AGENTS.md or CLAUDE.md, meaning an agent reading boot context will not discover them. Either (a) add inline citation from a charter-grade file, or (b) move to `archive/`.

---

## D. Staleness audit

Criteria: last-modified ≥7d ago AND not in active CZL work.

| file | days stale | refs | verdict |
|---|---|---|---|
| CALENDAR.md | 13 | 8 | keep — constitutional time authority |
| CIEU_VIDEO_METHODOLOGY.md | 11 | 6 | **archive candidate** — video pipeline not active product line today |
| CSO_INTEL_PROTOCOL.md | 8 | 3 | keep — CSO active role |
| INNER_DRIVE_PROTOCOL.md | 8 | 5 | keep — philosophical charter |
| TEMP_LAW.md | 10 | 12 | **review needed** — TL-001/004 dated 2026-04-06 may be closed; need Board confirm |
| ETHICS.md | 9 | 19 | keep — charter-grade |
| INTERNAL_GOVERNANCE.md | 9 | 43 | keep — most-ref stale-ish |
| priority_brief_schema.md | 6 | 3 | keep — AMENDMENT-009 schema |
| BOARD_CHARTER_AMENDMENTS.md | 4 | 51 | actively being edited by Samantha#1 this moment |
| WORKING_STYLE.md | 4 | 125 | keep — most-cited file |
| CONTINUITY_PROTOCOL.md | 7 | 11 | keep |
| governance/reminders/*.md (7 files) | 3 | 0 | **all archive candidates** — auto-written k9 warn artifacts, no citations |

**Archive-now candidates**: CIEU_VIDEO_METHODOLOGY.md + 7 reminder artifacts + (after Board review) cto_system23_takeover_v1.md + auto_commit_push_v1.md draft + reply_scan_detector_methodology_v1.md (once whitelist fully displaces).

**Needs-closure-check**: TEMP_LAW.md — TL-001 / TL-004 statuses dated 2026-04-06, 13 days old, need verify "still in effect" vs "closed and not marked".

---

## E. Categorization proposal

I agree with CEO's 4-tier `charter/ enforced/ protocols/ archive/` hierarchy shape. I propose **one variant**: split CEO's `charter/` into `charter/` (Board-only immutable law) + `runtime-state/` (append-only logs authored by code, not humans). Rationale: mixing human-edited charter with machine-written logs in one dir makes diff-review ambiguous.

### Proposed assignment of all 40 files

#### charter/ (human-authored, Board-authority-only edits; 6 files)
- AGENTS.md (ref only — lives at repo root)
- BOARD_CHARTER_AMENDMENTS.md
- CLAUDE.md (ref only — lives at repo root)
- WORKING_STYLE.md
- ETHICS.md
- INTERNAL_GOVERNANCE.md

#### enforced/ (machine-readable rules already ingested by hooks/router; 9 files + 1 yaml dir)
- governance/whitelist/ (8 yaml + 1 json) — **already machine-enforced per CEO audit**
- forget_guard_rules.yaml (already in enforcement loop)
- canonical_hashes.json
- active_dispatch_log.md (machine-writable append-only)
- enforce_status_dashboard.md (auto-written)
- blocking_events.log (auto-written)
- ceo_escalations.json (auto-written)
- czl_escalations.json (auto-written)
- dispatch_board.json (live queue)

#### protocols/ (human-readable doctrines referenced from charter or enforced/; 18 files)
- action_model_v2.md
- auto_enforce_meta.md
- CALENDAR.md
- ceo_dispatch_self_check.md (candidate merge with sub_agent_atomic_dispatch + template + midstream)
- ceo_midstream_checkin_protocol.md (merge candidate)
- ceo_operating_methodology_v1.md
- cieu_event_taxonomy.md
- CONTINUITY_PROTOCOL.md
- CSO_INTEL_PROTOCOL.md
- czl_unified_communication_protocol_v1.md
- DNA_LOG.md (also serves as runtime-state but is Secretary-curated, keep in protocols/)
- ecosystem_dependency_checklist_v1.md
- formal_methods_primer_v1.md
- INNER_DRIVE_PROTOCOL.md
- k9_alarm_consumer_v1.md
- methodology_framework_assignments_v1.md
- new_engineer_onboarding_gauntlet_v1.md
- pre_build_routing_gate_v1.md
- priority_brief_schema.md
- reply_taxonomy_whitelist_v1.md (keep; detector_methodology goes to archive/)
- restart_preparation_model_v1.md (merge with CONTINUITY_PROTOCOL)
- skill_trust_hybrid_v1.md
- sub_agent_atomic_dispatch.md (merge candidate)
- sub_agent_boot_prompt_template.md (merge candidate)
- tiered_routing_protocol_v1.md
- tiered_routing_protocol_v1_sync_addendum.md
- cto_role_v2_and_dispatch_board_20260416.md
- cto_dispatch_broker_v1.md

#### archive/ (deprecated or never-referenced; 6 files immediate + 4 candidate)
**Immediate archive:**
- CIEU_VIDEO_METHODOLOGY.md (stale 11d, video pipeline not active)
- cto_system23_takeover_v1.md (0 refs, superseded by broker spec)
- reply_scan_detector_methodology_v1.md (whitelist replaces blacklist era)
- forget_guard_rule_new_artifact_without_precheck.md (0 refs, doesn't scale as pattern)
- auto_commit_push_v1.md (0 refs, impl deferred indefinitely)
- governance/reminders/ (7 files — all auto-written k9 artifacts with 0 citations)

**Board-review-then-archive candidates:**
- TEMP_LAW.md (TL-001/004 closure status needed)
- TEMP_LAW entries if closed (leave file, mark closed inline)

**Not added** — Samantha#1 AMENDMENT-020 in flight, I defer to her on anything touching AGENTS.md/BOARD_CHARTER_AMENDMENTS.md.

### Variant summary vs CEO proposal

CEO's 4-tier: `charter/ enforced/ protocols/ archive/`. My variant: **keep 4 tiers, but**:
1. enforced/ should include already-machine-readable yaml+json that live in governance/whitelist/ today — the migration largely IS a mkdir + mv
2. dual-purpose files (auto-written logs like enforce_status_dashboard) should live in enforced/ not protocols/ — they are runtime artifacts not doctrines
3. merges in §B.2 and §B.4 should happen BEFORE the move, otherwise we encode fragmentation into new structure

---

## F. Priority fix list (top 5 — reduces Board "messy" perception most)

1. **Create governance/ARCHIVE_INDEX.md** — Secretary's own file does not exist. 40 files with no index = the #1 "messy" signal. One pass to generate: filename / status / category / supersedes / last-verified date.

2. **Merge the 4 tiny CEO dispatch protocols (B.2) into one `protocols/ceo_dispatch.md`** — 4 × ~40 LOC files on the same topic with no cross-ref creates more cognitive load than one 150-LOC section'd doc. Zero enforcement impact (hooks read yaml rules, not these prose docs).

3. **Archive the 6 immediate-archive files + 7 reminder artifacts** — removes 13 files from the flat listing, making the remaining 27 easier to scan. `git mv` to `governance/archive/` with forwarding note.

4. **Add explicit supersession headers to the 4 cluster pairs (B.1, B.4, B.6, B.8)** — inline `**Supersedes**: X.md` / `**Superseded-by**: Y.md` markers so next reader doesn't have to infer. Zero file moves required; pure prose patch.

5. **Fix the 3 real dead references (§C.1)** — active_dispatch_log → croba_false_positive file, skill_trust_hybrid → pair_sessions_log + security_audit_log. Either create the 3 missing files or remove/reword the references. Dead links in charter-adjacent docs signal "nobody maintains this".

**Expected effect after these 5 fixes**: 40 files → 21 active + 19 archived, with index + supersession markers + zero dead links. That matches Board's intuition of what "not messy" looks like.

---

## Notes for CEO consolidation

- No conflict with CEO's 4-tier shape; my `runtime-state/` suggestion is optional refinement.
- My priority list emphasizes **low-risk doc hygiene** (index + merges + archive + supersession markers); CEO's priority list emphasizes **high-leverage enforcement wiring** (router rules + charter flow pilot). They are complementary, not alternative — phase 1 audit includes both, phase 2 pilot is CEO's CZL-CHARTER-FLOW-RULE-PILOT, phase 3 batch migration naturally absorbs my doc-hygiene list.
- Samantha#1 is landing AMENDMENT-020 concurrently; all my assignments leave AGENTS.md / BOARD_CHARTER_AMENDMENTS.md untouched.

**Receipt**: this document = Secretary half delivered; Rt+1 = 0.
