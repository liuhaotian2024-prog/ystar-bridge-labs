# CEO Operating Methodology v1.0

**Constitutional — Board 2026-04-16 META Layer — Single Atomic**

**Authority**: CTO Ethan Wright per CEO dispatch — "reactive patch 不可持续 → unified framework at methodology layer"

**Problem**: CEO wrote 6+ reactive ForgetGuard rules today (coord_reply_5tuple, coordinator_summary_rt_audit, subagent_unauthorized_git_op, charter_drift_mid_session, ceo_design_ecosystem_blind, ceo_deferred_dispatch_promise_orphan, subagent_no_choice_question, subagent_tool_uses_claim_mismatch). Pattern: every new violation dimension → manual MEMORY entry + rule spec + test + wire. At 30+ rules/week projection, this becomes unmaintainable cognitive load and architectural debt. Board catch: need methodology-level unified framework that auto-derives instance rules from primitives.

**Solution**: Five foundational methodology primitives + auto-derivation pipeline + meta-audit hook to catch genuinely new dimensions requiring new primitives.

---

## Part 1 — Five Foundational Methodology Primitives

Each primitive defines: concept, invariant principles, and how to recognize violations.

### 1. Communication Discipline

**Concept**: All inter-agent messaging (CEO↔Board, CEO↔sub-agent, sub-agent→receipt) must carry verifiable structure enabling empirical closure measurement.

**Invariant Principles**:
- **5-tuple completeness**: Every dispatch and receipt contains Y\* (ideal contract), Xt (measured pre-state), U (actions), Yt+1 (post-state), Rt+1 (gap).
- **Empirical predicate**: Y\* must be verifiable via tool_use (file exists, test passes, CIEU event count ≥N) — no "I feel it's done" impressions.
- **Rt+1=0 closure**: Task is NOT complete until Rt+1 gap reaches zero AND validator confirms artifacts exist.
- **Single recommendation**: Receipts propose ONE path forward, not choice menus. Board/CEO decides via override if needed.
- **Promise=action coupling**: If CEO says "I will X", U section must contain concrete action for X, not deferred placeholder.

**Pattern Library** (shared validators):
- `validate_5tuple_structure(text) -> list[str]`: returns missing sections
- `validate_xt_empirical(xt_section) -> bool`: rejects speculation markers ("印象", "should be", "估计")
- `validate_rt_closure(rt_value, artifacts) -> tuple[bool, float]`: empirical gap calculation
- `validate_single_recommendation(text) -> bool`: rejects "Option A / Option B" patterns
- `validate_promise_action_coupling(promises, u_actions) -> list[str]`: matches "I will X" to concrete U step

**Derived Rules** (auto-generated from primitive + instance context):
- `coord_reply_5tuple` ← Communication + "CEO reply to Board missing 5-tuple"
- `coordinator_summary_rt_audit` ← Communication + "CEO summary claims Rt+1=0 without artifact verification"
- `subagent_no_choice_question` ← Communication + "sub-agent receipt presents choice menu"
- `ceo_deferred_dispatch_promise_orphan` ← Communication + "CEO promise lacks matching U action"

**Canonical reference**: `governance/czl_unified_communication_protocol_v1.md` (423 lines, Board 2026-04-16)

---

### 2. Ecosystem Design

**Concept**: Before creating any new entity (agent/engineer/module/rule/event/template), enumerate its dependency cascade across all existing system layers to prevent orphan components and integration debt.

**Invariant Principles**:
- **8-cascade checklist**: Charter file, canonical registry, governance_boot.sh recognition, dispatch routing, hook handler scope, CIEU schema, ForgetGuard agent_filter, pre-auth template.
- **Counterfactual probe**: "If this entity claims a task, which 5+ other entities need to know?" — forces dependency enumeration before creation.
- **Naming collision pre-check**: Grep existing agent_id/alias/skill names before assigning new ID.
- **Meta-learning retrospective**: After every Board catch ("you forgot cascade X"), append to `knowledge/ceo/lessons/ecosystem_cascade_retrospectives.md` and update checklist if new cascade type discovered.
- **Threshold escalation**: If total affected entities ≥10 across all cascades → escalate to CTO for architectural review before creation.

**Pattern Library**:
- `run_ecosystem_dependency_map(entity_spec) -> dict`: runs 8-cascade checklist + counterfactual probe, returns impact graph
- `check_naming_collision(proposed_id) -> list[str]`: greps agent_id_canonical.json + charter files
- `estimate_cascade_impact(edm_output) -> int`: counts total affected entities

**Derived Rules**:
- `ceo_design_ecosystem_blind` ← Ecosystem + "CEO dispatch contains 'create new' / '新增' keyword but no EDM section"

**Canonical reference**: `governance/ecosystem_dependency_checklist_v1.md` (194 lines, Board 2026-04-16)

---

### 3. Empirical Verification

**Concept**: Never trust completion claims on prose; always verify via artifact existence, test pass output, CIEU event delta, or other tool-observable evidence.

**Invariant Principles**:
- **Artifact existence**: `Path(claimed_file).exists()` must be True before accepting "file written" claim.
- **Test pass evidence**: Receipt must paste `pytest -q` output showing X/X PASS.
- **CIEU event delta**: If task claimed to emit N events, query `.ystar_cieu.db` for actual count.
- **Bash verification paste**: Receipts include `ls -la`, `wc -l`, `git diff --stat` pasted output.
- **Metadata reconciliation**: Sub-agent prose claim ("I used 6 tool_uses") vs runtime metadata (actual=14) → trust metadata, reject prose.

**Pattern Library**:
- `validate_artifact_exists(claimed_paths) -> list[Path]`: returns missing paths
- `parse_test_output(receipt) -> dict`: extracts pytest pass/fail counts from pasted output
- `query_cieu_delta(event_type, time_window) -> int`: counts new CIEU events
- `extract_bash_verification(receipt) -> bool`: checks for `ls -la` / `wc -l` patterns
- `reconcile_claim_metadata(prose_claim, runtime_metadata) -> dict`: flags discrepancies

**Derived Rules**:
- `coordinator_summary_rt_audit` ← Empirical + "CEO claims Rt+1=0 but artifacts missing"
- `subagent_tool_uses_claim_mismatch` ← Empirical + "sub-agent prose tool_uses ≠ metadata"
- `charter_drift_mid_session` ← Empirical + "charter mtime changed but no CIEU CHARTER_UPDATED event" (NOTE: current I1 uses mtime; v2 will use content-hash per Task #27)

**Canonical reference**: `governance/czl_unified_communication_protocol_v1.md` §3-4 (Gate 2 empirical verification), `reports/autonomous/papers/self_strengthening_governance_loop_20260416.md` §5.2 (hallucination detection).

---

### 4. Tiered Authority

**Concept**: Route tasks to appropriate decision-maker tier (CEO direct dispatch / CTO routing / Board approval) based on architectural impact, not organizational hierarchy.

**Invariant Principles**:
- **T1 = atomic**: Single engineer, ≤15 tool_uses, ≤3 files, fits pre-authorized template → CEO direct dispatch allowed.
- **T2 = architectural**: ≥2 engineers OR new module OR API change → CTO must route/split/approve.
- **T3 = system**: git push, PyPI release, external comm, payment → Board must approve.
- **Pre-auth templates**: CTO maintains whitelist of T1-eligible task patterns per engineer (e.g., Maya: add ForgetGuard warn rule ≤50 lines).
- **Scope escalation**: If T1 dispatch actual post-completion scope exceeds claimed tier (e.g., modified 5 files when claimed ≤3) → emit TIER_MISCLASSIFIED event, CEO recalibrates classifier.
- **Trust score awareness**: Sub-agent with trust_score <0.7 → auto-escalate from T1 to T2 regardless of task shape.

**Pattern Library**:
- `classify_tier(task_desc, estimated_scope) -> int`: returns 1/2/3 + routing decision
- `match_pre_auth_template(task_desc, engineer_id) -> str | None`: returns template_id or None
- `audit_tier_scope(claimed_tier, actual_files, actual_tool_uses) -> bool`: post-completion verification

**Derived Rules**:
- `subagent_unauthorized_git_op` ← Tiered Authority + "sub-agent (not CTO/eng-*) ran git commit/push without T3 Board approval"
- `dispatch_tier_misclassified` (pending, Maya task) ← Tiered Authority + "T1 dispatch actual scope >T1 limits"

**Canonical reference**: `governance/tiered_routing_protocol_v1.md` (420 lines, Board 2026-04-16), `memory/feedback_dispatch_via_cto.md` (updated 2026-04-16).

---

### 5. Self-Strengthening Loop (TS3L)

**Concept**: Every detected violation must produce permanent capability gain (CIEU event + MEMORY entry + test case + ForgetGuard rule + hook), not just one-time correction. This converts failure from recurring tax to structural improvement.

**Invariant Principles**:
- **Failure → evidence**: Emit CIEU event capturing violation context (who, what, when, metadata).
- **Evidence → heuristic**: Write MEMORY entry (`feedback_*.md`) documenting pattern and correction.
- **Heuristic → test**: Add regression test case to catch recurrence (`tests/governance/test_*.py`).
- **Test → runtime gate**: Land ForgetGuard rule (warn→deny after 48h dry-run) OR hook injector.
- **Gate → meta-learning**: If new violation type has no primitive mapping → emit METHODOLOGY_UNMAPPED_VIOLATION, spawn CTO atomic to assess if new primitive needed.

**Pattern Library**:
- `log_violation_to_cieu(event_type, metadata) -> None`
- `draft_memory_entry(violation_context) -> str`: auto-generates MEMORY .md template
- `generate_regression_test(violation_example) -> str`: pytest template
- `auto_derive_forgetguard_rule(primitive_id, instance_context) -> dict`: rule YAML from template
- `check_primitive_coverage(violation_type) -> str | None`: returns primitive_id or None if unmapped

**Derived Rules**:
- `methodology_unmapped_violation` (meta-rule, Maya task inline below) ← TS3L + "K9 detected violation with no primitive mapping"

**Canonical reference**: `reports/autonomous/papers/self_strengthening_governance_loop_20260416.md` (216 lines, Board 2026-04-16), `knowledge/shared/unified_work_protocol_20260415.md` (CIEU loop definition).

---

## Part 2 — Auto-Derivation Pipeline

**Purpose**: Replace manual "CEO writes rule + test + wire" with automated rule generation from primitive templates.

**Architecture**:

```
K9 violation detected
  ↓
Classify violation → primitive lookup (Communication / Ecosystem / Empirical / Authority / TS3L)
  ↓
Auto-generate ForgetGuard rule from primitive template + instance context
  ↓
Write rule to forget_guard_rules.yaml with mode=warn, dry_run_hours=48
  ↓
Auto-generate test case from primitive test template
  ↓
Run pytest to verify rule fires on violation example
  ↓
Emit RULE_AUTO_DERIVED CIEU event
  ↓
After 48h: if no false positives logged, auto-promote mode=warn → deny
```

**Templates** (stored in `governance/auto_derivation_templates/`):

### Communication Primitive Templates

**Template: 5tuple_missing**
```yaml
id: {instance_id}_missing_5tuple
description: "{agent_role} {message_type} lacks CIEU 5-tuple structure"
trigger:
  tool: ["Agent", "Edit", "Write"]
  conditions:
    - type: active_agent_equals
      value: "{agent_role}"
    - type: content_contains
      keywords: {context_keywords}
    - type: content_missing
      pattern: "Y\\*.*Xt.*U.*Yt\\+1.*Rt\\+1"
action: warn
recipe: |
  Your {message_type} lacks required 5-tuple structure.
  Add: Y* (ideal), Xt (pre-state), U (actions), Yt+1 (post-state), Rt+1 (gap).
  Ref: governance/czl_unified_communication_protocol_v1.md
cieu_event: {instance_id}_5TUPLE_MISSING
```

**Template: rt_closure_unverified**
```yaml
id: {instance_id}_rt_not_zero
description: "{agent_role} claims Rt+1=0 without artifact verification"
trigger:
  tool: ["Edit", "Write"]
  conditions:
    - type: content_contains
      keywords: ["Rt+1=0", "Rt+1 = 0"]
validation:
  - type: python_validator
    module: "ystar.kernel.czl_protocol"
    function: "validate_receipt"
    args: ["text", "artifacts_expected"]
    expect_valid: true
action: deny
recipe: |
  Claimed Rt+1=0 but empirical verification failed.
  Missing artifacts: {missing_artifacts}
  Re-verify or correct Rt+1 calculation.
cieu_event: {instance_id}_RT_UNVERIFIED
```

**Template: choice_question**
```yaml
id: {instance_id}_choice_question
description: "{agent_role} presented choice menu instead of single recommendation"
trigger:
  tool: ["Edit", "Write"]
  conditions:
    - type: content_contains
      keywords: ["Option A", "Option B", "请选择", "方案一", "方案二", "1)", "2)", "3)"]
action: deny
recipe: |
  Choice questions prohibited (Iron Rule 0).
  Pick best option yourself, execute, report.
  Board overrides if needed.
cieu_event: {instance_id}_CHOICE_QUESTION
```

### Ecosystem Primitive Templates

**Template: edm_missing**
```yaml
id: {instance_id}_ecosystem_blind
description: "{agent_role} creating new entity without EDM section"
trigger:
  tool: ["Agent", "Edit", "Write"]
  conditions:
    - type: content_contains
      keywords: ["create new", "新增", "spawn", "ship new", "立"]
    - type: content_missing
      pattern: "Ecosystem Dependency Map|EDM|联动|cascade"
action: warn
recipe: |
  New entity creation detected without Ecosystem Dependency Map.
  Run 8-cascade checklist + counterfactual probe before creation.
  Ref: governance/ecosystem_dependency_checklist_v1.md
cieu_event: {instance_id}_EDM_MISSING
```

### Empirical Primitive Templates

**Template: artifact_unverified**
```yaml
id: {instance_id}_artifact_unverified
description: "{agent_role} claims artifact created but no bash verification"
trigger:
  tool: ["Edit", "Write"]
  conditions:
    - type: content_contains
      keywords: ["file written", "created", "shipped"]
    - type: content_missing
      pattern: "ls -la|wc -l|pytest|git diff"
action: deny
recipe: |
  Claimed artifact creation but no bash verification paste.
  Include: ls -la <path>, wc -l <path>, pytest output, git diff --stat
  Ref: governance/czl_unified_communication_protocol_v1.md §4
cieu_event: {instance_id}_ARTIFACT_UNVERIFIED
```

**Template: claim_metadata_mismatch**
```yaml
id: {instance_id}_claim_mismatch
description: "Sub-agent prose claim vs runtime metadata discrepancy"
trigger:
  tool: ["SendMessage"]
  conditions:
    - type: content_contains
      keywords: ["tool_uses", "files modified"]
validation:
  - type: python_validator
    module: "ystar.governance.claim_mismatch"
    function: "reconcile_claim_metadata"
    args: ["receipt_text", "runtime_metadata"]
    expect_match: true
action: warn
recipe: |
  Prose claim: {prose_claim}
  Runtime metadata: {actual_metadata}
  Discrepancy detected. Trust metadata, re-report honestly.
cieu_event: {instance_id}_CLAIM_MISMATCH
```

### Tiered Authority Templates

**Template: unauthorized_tier3_op**
```yaml
id: {instance_id}_unauthorized_git_op
description: "Non-authorized agent attempted T3 operation without Board approval"
trigger:
  tool: ["Bash"]
  conditions:
    - type: content_contains
      keywords: ["git push", "git commit", "pypi", "deploy"]
    - type: active_agent_not_in
      values: ["cto", "board"]
action: deny
recipe: |
  T3 operation (git push/commit, deploy, release) requires Board approval.
  Route through CTO → CEO → Board escalation.
  Ref: governance/tiered_routing_protocol_v1.md §1
cieu_event: {instance_id}_UNAUTHORIZED_T3
```

### TS3L Primitive Template

**Template: violation_no_test_case**
```yaml
id: {instance_id}_no_regression_test
description: "Violation detected but no regression test added to prevent recurrence"
trigger:
  event_source: cieu
  conditions:
    - type: event_type_pattern
      value: "{violation_event_type}"
validation:
  - type: test_file_exists
    pattern: "tests/governance/test_{instance_id}.py"
    expect: true
action: warn
recipe: |
  Violation {violation_event_type} detected but no regression test added.
  TS3L loop incomplete: failure → evidence → test → rule → meta-learning.
  Add test case to tests/governance/test_{instance_id}.py
cieu_event: {instance_id}_NO_REGRESSION_TEST
```

**Auto-Derivation Script** (Ryan task card inline below):
```python
# scripts/auto_derive_forgetguard_rule.py
# Input: K9 violation event (from CIEU DB) + primitive_id
# Output: ForgetGuard rule YAML + test case .py + dry_run schedule

def auto_derive_rule(violation_event: dict, primitive_id: str) -> dict:
    """
    Generate ForgetGuard rule from primitive template + violation context.
    
    Args:
        violation_event: CIEU event dict with metadata
        primitive_id: "communication" | "ecosystem" | "empirical" | "authority" | "ts3l"
    
    Returns:
        {
            "rule_yaml": str,  # Generated rule for forget_guard_rules.yaml
            "test_case": str,  # Generated pytest test
            "instance_id": str,  # e.g., "coord_reply_5tuple"
            "dry_run_until": datetime  # 48h from now
        }
    """
    template = load_template(primitive_id, violation_event["subtype"])
    instance_id = generate_instance_id(violation_event)
    
    rule = template["rule"].format(
        instance_id=instance_id,
        agent_role=violation_event["agent_id"],
        message_type=violation_event["context"],
        context_keywords=violation_event["trigger_keywords"]
    )
    
    test = template["test"].format(
        instance_id=instance_id,
        violation_example=violation_event["example_text"]
    )
    
    return {
        "rule_yaml": rule,
        "test_case": test,
        "instance_id": instance_id,
        "dry_run_until": datetime.now() + timedelta(hours=48)
    }
```

**Integration with K9**:
- K9 event trigger (`scripts/k9_event_trigger.py`) detects new violation type
- Calls `classify_primitive(violation_context) -> str`
- If primitive found, calls `auto_derive_rule(event, primitive_id)`
- Writes rule to `forget_guard_rules.yaml` with `mode: warn, dry_run_hours: 48`
- Writes test to `tests/governance/test_auto_{instance_id}.py`
- Emits `RULE_AUTO_DERIVED` CIEU event
- Schedules dry-run review in 48h (cron job checks for false positives, auto-promotes to deny if clean)

---

## Part 3 — Retrospective Mapping (Today's 8 Reactive Rules → Primitive)

| Reactive Rule (Manual Today) | Primitive | Auto-Derive Template | Would Have Caught? |
|---|---|---|---|
| `coord_reply_5tuple` | Communication | 5tuple_missing | ✅ Yes — CEO reply to Board without 5-tuple structure |
| `coordinator_summary_rt_audit` | Communication + Empirical | rt_closure_unverified | ✅ Yes — CEO claims Rt+1=0, Gate 2 finds missing artifacts |
| `subagent_unauthorized_git_op` | Tiered Authority | unauthorized_tier3_op | ✅ Yes — sub-agent git push without Board approval |
| `charter_drift_mid_session` | Empirical | artifact_unverified (mtime variant) | ⚠️ Partial — I1 uses mtime, should use content-hash (Task #27 pending) |
| `ceo_design_ecosystem_blind` | Ecosystem | edm_missing | ✅ Yes — CEO "create new" without EDM section |
| `ceo_deferred_dispatch_promise_orphan` | Communication | promise_action_coupling (needs template) | ✅ Yes — CEO "I will X" with no matching U action |
| `subagent_no_choice_question` | Communication | choice_question | ✅ Yes — sub-agent receipt "Option A/B" pattern |
| `subagent_tool_uses_claim_mismatch` | Empirical | claim_metadata_mismatch | ✅ Yes — prose "6 tool_uses" vs metadata actual=14 |

**Coverage**: 7/8 rules auto-derivable from 4 primitives (Communication, Ecosystem, Empirical, Authority). 1 rule (`charter_drift_mid_session`) needs architectural fix (mtime→content-hash) but detector pattern still fits Empirical primitive.

**Conclusion**: If auto-derivation pipeline had been live, CEO would have written ZERO manual rules today — K9 would have detected violations, classified to primitives, auto-generated rules from templates.

---

## Part 4 — Methodology Self-Audit Hook (Meta-Rule)

**Purpose**: Catch violations that do NOT map to any existing primitive → trigger CTO atomic to assess if genuinely new dimension requiring new primitive.

**ForgetGuard Meta-Rule** (Maya task card inline below):

```yaml
id: methodology_unmapped_violation
enabled: true
description: "K9 detected violation with no primitive mapping — potential new methodology gap"
last_reviewed: "2026-04-16"
reviewer: "CTO Ethan Wright + Maya Patel (eng-governance)"

trigger:
  event_source: cieu
  conditions:
    - type: event_type_pattern
      value: "K9_VIOLATION_DETECTED"

validation:
  - type: python_validator
    module: "ystar.governance.primitive_mapper"
    function: "check_primitive_coverage"
    args: ["violation_type"]
    expect_non_null: true  # Expect a primitive_id to be returned

action: warn
recipe: |
  K9 detected violation type: {violation_type}
  No primitive mapping found in: Communication, Ecosystem, Empirical, Authority, TS3L.
  
  This is either:
  (1) New dimension requiring new primitive (escalate to CTO)
  (2) Existing primitive needs extended template coverage (Maya adds template)
  
  CTO atomic dispatch:
  - Review violation context in .ystar_cieu.db
  - Assess if genuinely new dimension (e.g., "Time-bounded SLA enforcement" not covered by existing 5)
  - If new primitive needed: update this spec, add template library, notify CEO
  - If existing primitive: Maya extends template library, no spec change
  
  Ref: governance/ceo_operating_methodology_v1.md Part 4

cieu_event: METHODOLOGY_UNMAPPED_VIOLATION
severity: high
escalate: true
notify: [cto]
```

**Workflow**:
1. K9 detects violation, emits `K9_VIOLATION_DETECTED` with `violation_type` metadata
2. `methodology_unmapped_violation` rule fires
3. Calls `check_primitive_coverage(violation_type) -> str | None`
4. If `None` returned (no primitive mapping), emits `METHODOLOGY_UNMAPPED_VIOLATION` CIEU event
5. CTO receives notification (via cron observer or real-time SSE stream once W9 ships)
6. CTO spawns atomic to review violation context:
   - If genuinely new dimension → update this spec with 6th primitive + template library
   - If existing primitive with insufficient template coverage → Maya extends template library
7. After CTO decision, emit `PRIMITIVE_COVERAGE_UPDATED` or `METHODOLOGY_EXTENDED` CIEU event

**This replaces**: CEO reactive "I noticed a new pattern, let me write a rule" workflow with systematic "K9 detected gap → auto-assess if methodology hole or template gap → CTO decides → system self-extends".

---

## Part 5 — Migration Plan

**Phase 1: Spec + Inline Task Cards** (this document)
- CTO writes this spec with 5 primitives + auto-derivation architecture + meta-audit hook
- Inline 2 task cards: Ryan (auto-derivation generator script) + Maya (meta-audit rule)
- **Deliverable**: This file + 2 task cards in `.claude/tasks/`

**Phase 2: Auto-Derivation Generator** (Ryan T1 atomic, post-spec)
- Implement `scripts/auto_derive_forgetguard_rule.py` with template engine
- Write primitive template library in `governance/auto_derivation_templates/`
- Wire K9 event trigger to call auto-derive on new violations
- Test: simulate violation → verify rule auto-generated + test case created + dry-run scheduled
- **Deliverable**: Script + templates + K9 integration + pytest passing

**Phase 3: Meta-Audit Hook** (Maya T1 atomic, post-spec)
- Implement `methodology_unmapped_violation` ForgetGuard rule in `forget_guard_rules.yaml`
- Implement `ystar.governance.primitive_mapper.check_primitive_coverage(violation_type)`
- Wire to CTO notification channel (CIEU event + optional SSE stream if W9 shipped)
- Test: inject unmapped violation type → verify CTO gets notified
- **Deliverable**: Rule + mapper + notification wiring + pytest passing

**Phase 4: Retrospective Cleanup** (CEO, post-Phase 2/3)
- For each of today's 8 manual rules, verify auto-derivation pipeline would have caught it
- Archive manual rule specs to `knowledge/ceo/lessons/pre_methodology_reactive_rules_archive.md`
- Update MEMORY entries to reference methodology primitives instead of individual rules
- **Deliverable**: Verification report + archive file + MEMORY cleanup

**Phase 5: Dry-Run Observation** (48h after Phase 2/3 ship)
- Monitor `.logs/tier_misclassified.log` and similar dry-run logs for false positives
- If false positive rate <5%, auto-promote rules from warn→deny
- If ≥5%, Maya reviews triggers and refines patterns
- **Deliverable**: Promotion decision + refined rules if needed

**Phase 6: Deprecate Reactive Rule Writing** (after Phase 5 clean)
- Update `knowledge/ceo/working_style/` to reference methodology primitives as canonical
- CEO MEMORY entry: "New violation → check primitive coverage first, do NOT write manual rule"
- ForgetGuard rule: `ceo_wrote_manual_rule_without_primitive_check` (action: warn)
- **Deliverable**: MEMORY update + meta-rule for CEO self-enforcement

---

## Part 6 — Inline Task Cards

### Task Card A: Ryan Park (eng-platform) — Auto-Derivation Generator Script

**Task ID**: `ryan-m6-auto-derive-generator`  
**Priority**: P1  
**Tier**: T1 (≤15 tool_uses, single engineer, additive script)

**CIEU 5-tuple**:

**Y\***: File `scripts/auto_derive_forgetguard_rule.py` exists with function:
```python
def auto_derive_rule(violation_event: dict, primitive_id: str) -> dict:
    # Returns {"rule_yaml": str, "test_case": str, "instance_id": str, "dry_run_until": datetime}
```

Template library `governance/auto_derivation_templates/*.yaml` contains ≥5 templates (5tuple_missing, rt_closure_unverified, choice_question, edm_missing, artifact_unverified).

K9 event trigger (`scripts/k9_event_trigger.py`) wired to call auto_derive on `K9_VIOLATION_DETECTED`.

Tests pass: `pytest tests/platform/test_auto_derive_forgetguard.py -q` (≥3 tests: derive_from_communication_primitive, derive_from_ecosystem_primitive, dry_run_schedule).

**Xt**: No auto-derivation script exists. `scripts/k9_event_trigger.py` currently hard-codes 8 violation types (from today's manual rules). No template library in `governance/auto_derivation_templates/`.

**U**:
1. Read `governance/ceo_operating_methodology_v1.md` Part 2 (auto-derivation architecture)
2. Create `governance/auto_derivation_templates/` directory
3. Write 5 YAML template files (communication_5tuple_missing.yaml, communication_rt_closure.yaml, communication_choice_question.yaml, ecosystem_edm_missing.yaml, empirical_artifact_unverified.yaml) per Part 2 template specs
4. Write `scripts/auto_derive_forgetguard_rule.py` with `auto_derive_rule()` function + template loader
5. Update `scripts/k9_event_trigger.py` to call auto_derive on new violation instead of hard-coded rule lookup
6. Write `tests/platform/test_auto_derive_forgetguard.py` with 3 test cases
7. Run `pytest tests/platform/test_auto_derive_forgetguard.py -q`, paste output
8. Run `ls -la governance/auto_derivation_templates/`, paste output
9. Run `wc -l scripts/auto_derive_forgetguard_rule.py`, paste output
10. Commit: `git commit -m "feat(platform): ForgetGuard auto-derivation generator — methodology v1 [ryan-m6]"`

**Yt+1**: Script exists, 5 templates exist, K9 wired, 3/3 tests pass, receipt contains bash verification.

**Rt+1 target**: 0.0

**Role tags**: `{"producer": "cto", "executor": "eng-platform", "governed": "eng-platform"}`

---

### Task Card B: Maya Patel (eng-governance) — Methodology Unmapped Violation Meta-Rule

**Task ID**: `maya-m7-methodology-meta-audit`  
**Priority**: P1  
**Tier**: T1 (≤15 tool_uses, single engineer, additive rule)

**CIEU 5-tuple**:

**Y\***: File `governance/forget_guard_rules.yaml` contains rule `methodology_unmapped_violation` per Part 4 spec.

File `ystar/governance/primitive_mapper.py` exists with function:
```python
def check_primitive_coverage(violation_type: str) -> str | None:
    # Returns primitive_id ("communication" | "ecosystem" | ...) or None if unmapped
```

Tests pass: `pytest tests/governance/test_methodology_meta_audit.py -q` (≥2 tests: unmapped_violation_triggers_cto_notify, mapped_violation_bypasses).

CTO notification channel wired (CIEU event `METHODOLOGY_UNMAPPED_VIOLATION` emitted, CTO receives via existing K9 observer).

**Xt**: No `methodology_unmapped_violation` rule in `forget_guard_rules.yaml`. No `primitive_mapper.py` module exists. Current K9 observer (`scripts/k9_event_trigger.py`) does not classify violations to primitives.

**U**:
1. Read `governance/ceo_operating_methodology_v1.md` Part 4 (meta-audit hook spec)
2. Write `ystar/governance/primitive_mapper.py` with `check_primitive_coverage(violation_type)` function
3. Implement mapping logic: load Part 1 primitive pattern libraries, match `violation_type` to primitive via keyword/pattern match
4. Add `methodology_unmapped_violation` rule to `governance/forget_guard_rules.yaml` per Part 4 YAML spec
5. Write `tests/governance/test_methodology_meta_audit.py` with 2 test cases
6. Run `pytest tests/governance/test_methodology_meta_audit.py -q`, paste output
7. Verify CTO notification: inject unmapped violation via test, check CIEU DB for `METHODOLOGY_UNMAPPED_VIOLATION` event
8. Run `wc -l ystar/governance/primitive_mapper.py`, paste output
9. Commit: `git commit -m "feat(governance): Methodology unmapped violation meta-rule — CTO escalation [maya-m7]"`

**Yt+1**: Rule exists, mapper exists, 2/2 tests pass, CTO notification verified, receipt contains pytest + CIEU query output.

**Rt+1 target**: 0.0

**Role tags**: `{"producer": "cto", "executor": "eng-governance", "governed": "eng-governance"}`

---

## Part 7 — Success Metrics

**Week 1** (post-Phase 2/3 ship):
- 0 manual ForgetGuard rules written by CEO (baseline: 8 rules written 2026-04-16)
- ≥3 rules auto-derived from violations via K9 trigger
- 0 false positives in dry-run logs (action=warn only, no deny yet)

**Week 2** (post-Phase 5 promotion):
- ≥5 rules auto-promoted from warn→deny after clean 48h dry-run
- CEO cognitive load: ≤5min to review auto-derived rule vs ≥30min to write manual rule (6x efficiency gain)
- 0 `METHODOLOGY_UNMAPPED_VIOLATION` events (i.e., all violations map to existing 5 primitives)

**Week 4** (post-Phase 6 deprecation):
- CEO MEMORY entries reference primitives, not individual rules
- New engineer onboarding doc: "Read 5 primitives + auto-derivation pipeline" instead of "Read 30+ individual rules"
- Methodology spec becomes canonical reference for all governance rule design

**Failure criteria** (triggers CTO review):
- False positive rate >5% in dry-run (indicates primitive pattern too broad)
- ≥3 `METHODOLOGY_UNMAPPED_VIOLATION` events in single week (indicates 5 primitives insufficient, need 6th)
- Auto-derivation script crashes on new violation type (indicates template engine fragile)

---

## Part 8 — Empirical Verification (Receipt Template for CTO)

After completing this spec, Ethan (CTO) receipt MUST contain:

**Bash verification**:
```bash
# Verify spec file exists
ls -la governance/ceo_operating_methodology_v1.md
wc -l governance/ceo_operating_methodology_v1.md

# Verify 5 primitives documented
grep -c "^### [1-5]\." governance/ceo_operating_methodology_v1.md  # Expect 5

# Verify 2 inline task cards exist
grep -c "^### Task Card [AB]:" governance/ceo_operating_methodology_v1.md  # Expect 2

# Verify retrospective mapping table complete
grep -c "coord_reply\|coord_summary\|unauthorized_git\|charter_drift\|ecosystem_blind\|deferred_dispatch\|no_choice\|tool_uses_claim" governance/ceo_operating_methodology_v1.md  # Expect ≥8

# Verify auto-derivation templates specified
grep -c "Template:" governance/ceo_operating_methodology_v1.md  # Expect ≥5
```

**CIEU 5-tuple receipt**:
- **Y\***: governance/ceo_operating_methodology_v1.md with 5 primitives + auto-derivation pipeline + 8-rule retrospective mapping + meta-audit hook + 2 inline task cards
- **Xt**: (paste grep counts from above bash verification)
- **U**: (paste actual tool_use count from metadata, NOT prose estimate)
- **Yt+1**: Spec shipped, primitives enumerated, templates specified, task cards inlined
- **Rt+1**: (calculate: 1 if spec <5 primitives, +1 if <8 rule mappings, +1 if <2 task cards, +1 if no meta-audit hook, +1 if no auto-derivation pipeline spec, +1 if receipt missing bash paste; target 0)

**Tool_uses claim reconciliation**: Prose claim MUST match `metadata.tool_uses` exactly (enforced by `subagent_tool_uses_claim_mismatch` rule, E1 live).

---

## References

**Authoritative Sources**:
- `governance/czl_unified_communication_protocol_v1.md` — Communication primitive (423 lines, Board 2026-04-16)
- `governance/ecosystem_dependency_checklist_v1.md` — Ecosystem primitive (194 lines, Board 2026-04-16)
- `governance/tiered_routing_protocol_v1.md` — Tiered Authority primitive (420 lines, Board 2026-04-16)
- `reports/autonomous/papers/self_strengthening_governance_loop_20260416.md` — TS3L primitive (216 lines, Board 2026-04-16)
- `governance/sub_agent_atomic_dispatch.md` — Atomic dispatch constraint (32 lines, Board 2026-04-15)
- `knowledge/shared/unified_work_protocol_20260415.md` — CIEU 5-tuple canonical definition

**Implementation Evidence**:
- `scripts/k9_event_trigger.py` — K9 violation detection (current 8 hard-coded rules)
- `governance/forget_guard_rules.yaml` — 12 existing rules (790 lines, last updated 2026-04-16)
- `Y-star-gov/ystar/kernel/czl_protocol.py` — CZL validators (353 lines, Leo-Kernel)
- `Y-star-gov/ystar/governance/claim_mismatch.py` — E1 claim/metadata reconciler (Maya-Governance)

**Related Lessons**:
- `knowledge/ceo/lessons/atomic_task_per_dispatch_2026_04_13.md` — 11-failure lesson leading to atomic dispatch doctrine
- `knowledge/ceo/lessons/autonomy_degradation_root_cause_2026_04_13.md` — 7-cause diagnosis of CEO self-drive degradation
- `.claude/projects/.../memory/feedback_subagent_receipt_empirical_verify.md` — Ethan#CZL-1 hallucination catch

**Version History**:
- v1.0 (2026-04-16): Initial specification, CTO Ethan Wright per CEO dispatch

---

**END OF SPECIFICATION**

Co-Authored-By: Ethan Wright (CTO, Y* Bridge Labs)
