# Skill-Trust Spec #72 — Ecosystem Audit (5 New Engineers)

**Date**: 2026-04-16
**Auditor**: CTO Ethan Wright
**Authority**: Board 2026-04-16 design discipline directive — retroactive 联动 audit for #72 skill-trust spec

**Context**: governance/skill_trust_hybrid_v1.md spawned 5 new engineers without applying 8-cascade checklist. CEO batch-approved without ecosystem-view filter. This audit applies ecosystem_dependency_checklist_v1.md retroactively to enumerate missing cascades.

---

## Summary — Cascade Missing Inventory

| Engineer | Cascades Spec'd | Cascades Missing | Critical Gaps | Estimated Atomic Impl Effort |
|----------|-----------------|------------------|---------------|------------------------------|
| eng-data (Maya dual-hat) | 1/8 (charter file only) | 7/8 | canonical registry, boot script, dispatch routing | 6 atomics |
| eng-security (Alex Kim) | 1/8 (charter file only) | 7/8 | naming collision (NAMING CONFLICT detected), all other cascades | 8 atomics |
| eng-ml (Priya Sharma) | 1/8 (charter file only) | 7/8 | canonical registry, boot script, dispatch routing | 6 atomics |
| eng-perf (Carlos Mendez) | 1/8 (charter file only) | 7/8 | canonical registry, boot script, dispatch routing | 6 atomics |
| eng-compliance (Sofia Chen) | 1/8 (charter file only) | 7/8 | **NAMING COLLISION (Critical)**: Sofia Chen vs Sofia Zhang (CMO), all other cascades | 9 atomics |

**Total missing cascades**: 35/40 (87.5% cascade coverage gap)
**Total estimated atomic impl effort**: 35 atomics (7 atomics/engineer average)

**Critical finding**: 2 naming collisions detected (Alex Kim potential conflict with future Alex-CSO if hired; Sofia Chen **confirmed conflict** with existing Sofia Zhang-CMO per agents/CMO.md line 1)

---

## Per-Engineer Cascade Analysis

### eng-data (Maya Patel dual-hat)

**Spec'd in skill_trust_hybrid_v1.md**:
- (a) Charter file: `.claude/agents/maya-data.md` ✓

**Missing cascades** (7/8):

**(b) Canonical agent_id registry**:
- Status: ❌ NOT in `governance/agent_id_canonical.json`
- Required: Add `"maya-data": {"display_name": "Maya Patel (Data Analytics)", "scope": "CIEU analytics + governance metrics", "created": "2026-04-16", "note": "dual-hat with maya-governance"}`
- Atomic impl: 1 atomic (Edit canonical registry)

**(c) governance_boot.sh CHARTER_MAP**:
- Status: ❌ NOT in STEP 11.5 CHARTER_MAP
- Required: Add `elif [ "$AGENT_ID" = "maya-data" ]; then CHARTER_FILE=".claude/agents/maya-data.md"`
- Atomic impl: 1 atomic (Edit boot script)

**(d) Dispatch routing acceptance**:
- **Board dispatch**: ❌ CEO dispatch logic does not recognize "maya-data" (only "Maya" / "maya-governance")
- **Sync layer**: ❌ `scripts/sync_layer.py` does not recognize "maya-data" as claimable engineer_id
- **Engineer subscriber**: ❌ `scripts/engineer_subscriber.py` does not include "maya-data" in eng-* whitelist
- Atomic impl: 2 atomics (Update CEO dispatch pattern recognition + sync layer engineer_id validation)

**(e) Hook handler scope**:
- Status: ❌ Hook `engineer_file_scope_check` does not recognize "maya-data" (only maya-governance scope)
- Required: Extend hook to recognize maya-data + dual-hat file scope (union of governance + data analytics files)
- Atomic impl: 1 atomic (Update hook handler)

**(f) CIEU schema**:
- Status: ⚠️ No new event_type defined in spec, but likely needed (e.g., `ENG_DATA_ANOMALY_DETECTED`, `TRUST_SCORE_UPDATED`)
- Required: Define event schema in `governance/cieu_event_taxonomy.md`
- Atomic impl: 1 atomic (if event_type needed, add to taxonomy; if not, skip)

**(g) ForgetGuard rule scope**:
- Status: ❌ `engineer_file_scope_drift` rule does not include maya-data agent_filter
- Required: Update agent_filter to include "maya-data" + define allowed file patterns
- Atomic impl: 1 atomic (Edit ForgetGuard rules)

**(h) Pre-auth template**:
- Status: ❌ No pre-auth template defined in `governance/tiered_routing_protocol_v1.md` §3 for maya-data
- Required: Define template (likely inherit from maya-governance template + extend with data analytics patterns)
- Atomic impl: 1 atomic (Add to tier-routing spec)

**Total: 6 atomics missing for eng-data**

---

### eng-security (Alex Kim)

**Spec'd in skill_trust_hybrid_v1.md**:
- (a) Charter file: `.claude/agents/alex-security.md` ✓

**Missing cascades** (7/8):

**NAMING COLLISION CHECK**:
- ❌ **POTENTIAL CONFLICT**: "Alex" first name used. If future CSO hired with name "Alex" (e.g., Alex Rodriguez), collision occurs.
- **Recommendation**: Use disambiguating agent_id `alex-kim-security` or rename to different first name (e.g., "Adrian Kim")
- **Atomic impl**: 1 atomic (Naming disambiguation decision + charter rename if needed)

**(b) Canonical agent_id registry**:
- Status: ❌ NOT in `governance/agent_id_canonical.json`
- Required: Add `"alex-security": {"display_name": "Alex Kim", "scope": "security audit + threat modeling", "created": "2026-04-16"}`
- Atomic impl: 1 atomic

**(c) governance_boot.sh CHARTER_MAP**:
- Status: ❌ NOT in STEP 11.5
- Atomic impl: 1 atomic

**(d) Dispatch routing acceptance**:
- ❌ Board dispatch / sync layer / engineer subscriber all missing
- Atomic impl: 2 atomics

**(e) Hook handler scope**:
- ❌ Security engineer needs special hook permissions (e.g., read all files for audit, test bypass attempts for pen-testing)
- Required: Define security-engineer-specific hook exceptions
- Atomic impl: 1 atomic

**(f) CIEU schema**:
- ⚠️ Likely needs event_type: `SECURITY_AUDIT_COMPLETED`, `CVE_DETECTED`, `PENETRATION_TEST_RESULT`
- Atomic impl: 1 atomic (define 3 event schemas)

**(g) ForgetGuard rule scope**:
- ❌ Security engineer needs exemptions from some rules (e.g., can read secrets for audit, but must log access)
- Atomic impl: 1 atomic (define security-specific rule exceptions)

**(h) Pre-auth template**:
- ❌ Security engineer likely needs broader file read access than base engineer template
- Atomic impl: 1 atomic

**Total: 8 atomics missing for eng-security** (including naming disambiguation)

---

### eng-ml (Priya Sharma)

**Spec'd in skill_trust_hybrid_v1.md**:
- (a) Charter file: `.claude/agents/priya-ml.md` ✓

**Missing cascades** (7/8):

**(b) Canonical agent_id registry**: ❌ 1 atomic
**(c) governance_boot.sh CHARTER_MAP**: ❌ 1 atomic
**(d) Dispatch routing acceptance**: ❌ 2 atomics
**(e) Hook handler scope**: ❌ ML engineer needs access to `scripts/local_learn.py` + Gemma endpoint scripts → 1 atomic
**(f) CIEU schema**: ⚠️ Likely needs `MODEL_EVAL_COMPLETED`, `GEMMA_FINE_TUNE_STARTED` → 1 atomic
**(g) ForgetGuard rule scope**: ❌ 1 atomic
**(h) Pre-auth template**: ❌ 1 atomic

**Total: 6 atomics missing for eng-ml**

---

### eng-perf (Carlos Mendez)

**Spec'd in skill_trust_hybrid_v1.md**:
- (a) Charter file: `.claude/agents/carlos-perf.md` ✓

**Missing cascades** (7/8):

**(b) Canonical agent_id registry**: ❌ 1 atomic
**(c) governance_boot.sh CHARTER_MAP**: ❌ 1 atomic
**(d) Dispatch routing acceptance**: ❌ 2 atomics
**(e) Hook handler scope**: ❌ Performance engineer needs profiling tool access → 1 atomic
**(f) CIEU schema**: ⚠️ Likely needs `PERF_BASELINE_RECORDED`, `SLO_BREACH_DETECTED` → 1 atomic
**(g) ForgetGuard rule scope**: ❌ 1 atomic
**(h) Pre-auth template**: ❌ 1 atomic

**Total: 6 atomics missing for eng-perf**

---

### eng-compliance (Sofia Chen) — **CRITICAL NAMING COLLISION**

**Spec'd in skill_trust_hybrid_v1.md**:
- (a) Charter file: `.claude/agents/sofia-compliance.md` ✓

**NAMING COLLISION CHECK**:
- ❌ **CONFIRMED CONFLICT**: "Sofia Chen" (compliance engineer) vs "Sofia Zhang" (CMO, per `agents/CMO.md` line 1: `# 官方姓名：Sofia Zhang · 对外介绍必须使用此名`)
- **Impact**: Board/CEO dispatch ambiguity ("Sofia, 做 X" → which Sofia?), CIEU agent_id collision if both use "sofia", charter file collision if both use `.claude/agents/sofia.md`
- **Recommendation**: Rename compliance engineer to different first name (e.g., "Elena Chen", "Sophia Chen with 'ph'", or use full agent_id "sofia-chen-compliance")
- **Atomic impl**: 1 atomic (Naming disambiguation decision + spec update + charter rename)

**Missing cascades** (7/8):

**(b) Canonical agent_id registry**:
- Status: ❌ NOT in registry
- **Conflict risk**: If added as "sofia-compliance", must disambiguate from potential "sofia-cmo" (CMO currently uses "Sofia-CMO" per AGENTS.md, not "sofia")
- Required: Add with disambiguated agent_id (e.g., `"sofia-chen-compliance"` or rename to `"elena-compliance"`)
- Atomic impl: 1 atomic (includes collision resolution)

**(c) governance_boot.sh CHARTER_MAP**: ❌ 1 atomic
**(d) Dispatch routing acceptance**: ❌ 2 atomics (must resolve naming collision first)
**(e) Hook handler scope**: ❌ Compliance engineer needs read access to all CIEU logs for audit → 1 atomic
**(f) CIEU schema**: ⚠️ Likely needs `COMPLIANCE_AUDIT_COMPLETED`, `GDPR_VIOLATION_DETECTED` → 1 atomic
**(g) ForgetGuard rule scope**: ❌ Compliance engineer needs exemptions for audit trail read access → 1 atomic
**(h) Pre-auth template**: ❌ 1 atomic

**Total: 9 atomics missing for eng-compliance** (including naming collision resolution as P0)

---

## Cascade Impact Summary (Counterfactual Probe Applied)

**Per counterfactual probe template (ecosystem_dependency_checklist_v1.md Part 2)**:

### Affected Entities Across 5 Engineers

1. **Dispatch routing**: CEO dispatch logic, sync_layer.py, dispatch_board.py, engineer_subscriber.py (4 entities affected per engineer × 5 = 20 entity-impacts)
2. **Charter mount**: governance_boot.sh, agent_id_canonical.json, AGENTS.md (potential), governance/engineer_trust_scores.json (4 entities × 5 = 20 entity-impacts)
3. **CIEU events**: Secretary audit, drift observer, trust score updater, cieu_event_taxonomy.md (4 entities × 5 = 20 entity-impacts)
4. **Naming collision**: 2 collisions detected (Sofia Chen vs Sofia Zhang-CMO, Alex Kim vs potential future Alex-CSO)
5. **File scope**: Hook validator, CTO code review, pre-commit tests, tier-routing classifier (4 entities × 5 = 20 entity-impacts)
6. **Governance rules**: ForgetGuard rules (engineer_file_scope_drift, tier_routing_trust_violation, etc.), pre-auth templates (5+ rules × 5 = 25+ entity-impacts)

**Total affected entities**: 105+ entity-impacts (far exceeds threshold of ≥10 → should have escalated to CTO for architectural review before creation)

---

## Recommended Remediation Plan

### Phase 1: P0 Naming Collisions (MUST fix before any engineer activation)

**Atomic 1**: Resolve Sofia Chen naming collision
- **Decision**: Rename to "Elena Chen" (compliance engineer) to avoid conflict with Sofia Zhang (CMO)
- **Files**: Update `governance/skill_trust_hybrid_v1.md` lines 164-177, update all future references
- **Owner**: CTO (architectural decision) + Maya (spec update)

**Atomic 2**: Pre-check Alex Kim collision
- **Decision**: Use agent_id `alex-kim-security` (not just "alex") to avoid future CSO collision
- **Files**: Update `governance/skill_trust_hybrid_v1.md` lines 107-120
- **Owner**: CTO + Maya

### Phase 2: Canonical Registry + Boot Script (Blocks all engineer activation)

**Atomics 3-7**: Add 5 engineers to `governance/agent_id_canonical.json`
- **Owner**: Maya (governance engineer)

**Atomics 8-12**: Add 5 engineers to `governance_boot.sh` STEP 11.5 CHARTER_MAP
- **Owner**: Ryan (platform engineer, owns boot script)

### Phase 3: Dispatch Routing (Blocks CEO→engineer task assignment)

**Atomics 13-17**: Update CEO dispatch pattern recognition for 5 engineers
- **Owner**: CEO (self-update to `.claude/agents/ceo.md` dispatch logic)

**Atomics 18-22**: Update `scripts/sync_layer.py` + `dispatch_board.py` engineer_id validation
- **Owner**: Ryan (platform engineer)

### Phase 4: Hook Handler + ForgetGuard Rules

**Atomics 23-27**: Update hook handlers for 5 engineers (file scope, special permissions)
- **Owner**: Ryan (platform engineer, owns `ystar/adapters/hook.py`)

**Atomics 28-32**: Update ForgetGuard rules agent_filter for 5 engineers
- **Owner**: Maya (governance engineer)

### Phase 5: CIEU Schema + Pre-Auth Templates

**Atomics 33-37**: Define CIEU event schemas for new event_types (if needed)
- **Owner**: Maya (governance engineer, owns `governance/cieu_event_taxonomy.md`)

**Atomics 38-42**: Define pre-auth templates for 5 engineers
- **Owner**: Maya (governance engineer, owns `governance/tiered_routing_protocol_v1.md`)

### Phase 6: Charter Files (Last — blocks nothing but completes cascade)

**Atomics 43-47**: Write 5 charter files `.claude/agents/{engineer-id}.md`
- **Owner**: CTO (charter authorship) or delegate to each engineer's domain lead

---

## Meta-Learning (CEO Self-Probe)

**Pattern**: CEO missed 7/8 cascades per engineer (87.5% miss rate) → systemic design blind-spot, not one-off error

**Root cause**:
- CEO focused on functional charter (what engineer does) but not integration cascades (who/what needs to know engineer exists)
- No checklist template used before creation
- Batch approval without ecosystem-view filter (approved 5 engineers in single pass without counterfactual probe)

**Prevention**:
- Enforce ForgetGuard rule `ceo_design_ecosystem_blind` (mode=warn for 48h, then deny)
- CEO must use counterfactual probe template (ecosystem_dependency_checklist_v1.md Part 2) before any new entity creation
- CTO architectural review required if total affected entities ≥10 (this case: 105+ → should have triggered)

**Systemic fix**:
- Ecosystem Dependency Checklist v1 now canonical (governance/ecosystem_dependency_checklist_v1.md)
- ForgetGuard rule enforcement starting 2026-04-16 (warn mode)

**Retrospective written to**: `knowledge/ceo/lessons/ecosystem_cascade_retrospectives.md` (CEO responsibility per ecosystem_dependency_checklist_v1.md Part 3)

---

## Estimated Total Effort

**35 atomics** (7 atomics/engineer average, excluding charter authorship which was already spec'd)

**Breakdown by owner**:
- Maya (governance engineer): 15 atomics (canonical registry, ForgetGuard rules, CIEU schemas, pre-auth templates)
- Ryan (platform engineer): 10 atomics (boot script, sync layer, dispatch board, hook handlers)
- CTO (Ethan): 5 atomics (naming decisions, architectural review, charter review)
- CEO (Aiden): 5 atomics (dispatch pattern recognition self-update, retrospective)

**Critical path**: Phase 1 (naming collisions) → Phase 2 (registry + boot) → Phase 3 (dispatch routing) must complete before any engineer can claim first task. Phases 4-6 can run in parallel after Phase 3.

**AI re-grain note (2026-04-16)**: Timeline replaced with parallel atomic dispatch count per Board mandate — no hardcoded hour estimates.

**Atomic dispatch estimate** (if parallelized):
- Phase 1: 2 atomics (CTO decision + Maya spec update) — sequential dependency
- Phase 2-3: 7 atomics (Maya canonical registry + Ryan boot script + routing updates) — 5 parallel + 2 sequential
- Phase 4-6: 10 atomics (Maya + Ryan parallel work) — fully parallel
- **Total: 19 parallel atomic dispatches** (wall-clock depends on engineer availability + claim velocity, not time-grain prediction)

---

## Audit Conclusion

**Finding**: Skill-trust spec #72 created 5 new engineers with 87.5% cascade coverage gap (35/40 cascades missing). 2 naming collisions detected (1 confirmed P0 blocker). Total affected entities: 105+ (far exceeds CTO review threshold).

**Recommendation**: Do NOT activate any of the 5 engineers until Phase 1-3 remediation complete (naming collision resolution + canonical registry + boot script + dispatch routing). Phases 4-6 can ship incrementally after activation.

**Systemic improvement**: Ecosystem Dependency Checklist v1 + ForgetGuard rule `ceo_design_ecosystem_blind` now enforced to prevent recurrence.

**Responsible parties**:
- CTO (Ethan): Naming collision decisions (Phase 1)
- Maya (governance engineer): Registry + ForgetGuard + CIEU + pre-auth (Phases 2, 4, 5)
- Ryan (platform engineer): Boot script + dispatch routing + hooks (Phases 2, 3, 4)
- CEO (Aiden): Dispatch pattern self-update + retrospective (Phase 3, meta-learning)

---

**Audit completed**: 2026-04-16
**Next action**: CTO decision on Phase 1 naming collisions → dispatch Phase 2-3 remediation to Maya + Ryan
