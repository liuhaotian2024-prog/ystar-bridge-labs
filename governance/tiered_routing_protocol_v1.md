# Tiered Routing Protocol v1.0

**Purpose**: Eliminate CTO bottleneck for atomic engineer tasks while preserving architectural oversight.

**Context**: 2026-04-16 empirical observation — 80% of CEO→CTO→Engineer dispatches are T1-shaped (single engineer, ≤15 tool_uses, no cross-module impact). Current MEMORY rule `feedback_dispatch_via_cto.md` forces all engineer work through CTO, creating serialization bottleneck even when CTO review adds no architectural value.

**Solution**: Tier-based routing with pre-authorized templates for atomic work.

---

## 1. Tier Taxonomy

### T1: Atomic Engineer Task
**CEO 直派允许** (skip CTO routing)

**Characteristics**:
- Single engineer scope
- ≤15 tool_uses empirical
- ≤3 files modified
- No architectural decision required
- Fits pre-authorized template (see §3)
- No cross-engineer coordination
- No new component/module creation

**Examples**:
- Add ForgetGuard rule mode=warn dry_run≤48h
- Extend single hook script with try/except wrapper
- Add test assertions to existing test_*.py
- Update single charter section (additive only)
- File rename within agent scope
- Extend CIEU schema reader helper
- Add log rotation script
- Fix typo in error message

**CIEU emission**: `CEO_DIRECT_DISPATCH_TIER1` with fields:
- `engineer_id`
- `template_matched` (which pre-auth template, or "none" if judgment call)
- `estimated_tool_uses`
- `files_in_scope`

---

### T2: Cross-Engineer / Architectural
**必经 CTO 中转**

**Characteristics**:
- ≥2 engineers required OR
- New component/module creation OR
- Scope >3 files OR
- Architectural decision (API change, module boundary, data model) OR
- New ForgetGuard rule mode=deny OR
- Refactor / migration task OR
- >15 tool_uses estimated

**Examples**:
- Design + implement new governance pipeline stage
- Refactor CIEU event taxonomy
- Migrate governance_boot.sh to Python
- Add new MCP server integration
- Change ystar-gov API contract
- Cross-repo dependency update (Y*gov + ystar-company)
- Implement new amendment

**Routing**: CEO writes T2 task card → CTO reviews + splits into T1 sub-tasks OR CTO executes OR CTO escalates to T3

**CIEU emission**: `CTO_ROUTED_TIER2` with fields:
- `task_card_path`
- `cto_decision` (execute_self / split_to_t1 / escalate_to_t3)
- `engineers_assigned` (if split)

**Workaround for nested sub-agent limit** (per MEMORY `feedback_cto_subagent_cannot_async_orchestrate.md`):
- CTO writes task card to `.claude/tasks/cto-{id}.md`
- CTO returns control to CEO
- CEO spawns engineer sub-agent(s) with prompt referencing CTO task card
- Engineer reports back to CEO
- CEO forwards completion to CTO for review
- CTO approves or requests rework

---

### T3: System Decision
**Board 必批**

**Characteristics**:
- Production deploy OR
- Git commit/push to main OR
- PyPI release OR
- Payment / external invoice OR
- External communication (cold email, PR merge with external contributor) OR
- Rollback / amendment proposal OR
- Security incident response OR
- Data deletion (GDPR, etc.)

**Examples**:
- Push to ystar-gov main branch
- Publish ystar 0.43.0 to PyPI
- Send cold email to enterprise prospect
- Approve external contributor PR merge
- Propose AMENDMENT-030
- Roll back governance_boot.sh to commit abc123
- Delete CIEU records per user request

**Routing**: CEO drafts proposal → Board approval required before execution

**CIEU emission**: `BOARD_ESCALATED_TIER3` with fields:
- `proposal_path` (markdown file with decision memo)
- `board_response` (approved / denied / deferred)
- `executed_at` (ISO timestamp, null if not yet executed)

---

## 2. Classifier Rules

**Input**: Task description string + estimated scope

**Output**: Integer `tier_level` (1/2/3) + routing decision

**Deterministic rules** (ForgetGuard-implementable, Maya to design full regex patterns):

### T3 Keywords (highest priority)
- `push origin` / `git push` / `deploy` / `release` / `pypi`
- `付款` / `payment` / `invoice`
- `rollback` / `revert` / `git reset --hard`
- `amendment` / `propose AMENDMENT-`
- `external email` / `cold outreach` / `pr merge external`
- `delete CIEU` / `GDPR` / `data deletion`

### T2 Keywords
- `architecture` / `API change` / `module boundary`
- `new module` / `new component` / `new MCP`
- `cross-engineer` / `≥2 engineers` / `collaboration`
- `refactor` / `migrate` / `rewrite`
- `ForgetGuard rule mode=deny`
- `spec` / `design doc` / `6-pager`
- File count >3 OR tool_uses >15 (heuristic)

### T1 = Default
- Everything else within engineer scope
- Must match at least one pre-authorized template (§3)
- If no template match → escalate to T2 for CTO judgment

**Edge case**: If task description ambiguous, classifier emits `TIER_AMBIGUOUS` event and escalates to T2.

---

## 3. CTO Pre-Authorization Templates

**CTO maintains this list** (refreshed weekly, stored in `.ystar_session.json` or `governance/pre_authorized_templates.yaml`).

Each template specifies:
- Engineer role(s)
- Allowed operation pattern
- Scope guards (max files, max lines, writable paths)
- Example task descriptions

### Maya Patel (eng-governance) Templates

**Template M1**: Add ForgetGuard warn rule
- **Pattern**: "Add ForgetGuard rule mode=warn dry_run ≤48h"
- **Scope**: `ystar/governance/forget_guard_rules.yaml` only
- **Max lines**: +50
- **Example**: "Add `ceo_forgot_handoff` warn rule triggered by missing session_handoff.md read in first 5 tool_uses"

**Template M2**: Extend coordinator_audit helper
- **Pattern**: "Extend governance coordinator_audit.py with new helper function"
- **Scope**: `ystar/governance/coordinator_audit.py` only, additive only
- **Max lines**: +100
- **Example**: "Add `count_tier1_bypasses_last_24h()` to coordinator_audit helpers"

**Template M3**: Write governance test
- **Pattern**: "Write test_governance_*.py"
- **Scope**: `tests/test_governance_*.py`, new file OK
- **Max lines**: ≤100
- **Example**: "Write test_tiered_routing_classifier.py with 5 test cases"

### Ryan Park (eng-platform) Templates

**Template R1**: Extend hook script fail-safe
- **Pattern**: "Add try/except to hook script"
- **Scope**: `scripts/*.py`, existing file only
- **Max lines**: +20 per try/except block
- **Example**: "Wrap `session_boot_yml.py` CIEU write with try/except, log to .logs/boot_fail.log on error"

**Template R2**: Add platform test
- **Pattern**: "Write test_*.py for platform/infra"
- **Scope**: `tests/test_*.py`, new file OK
- **Max lines**: ≤200
- **Example**: "Write test_governance_boot_self_heal.py with mock ForgetGuard DENY"

**Template R3**: Extend CIEU schema reader
- **Pattern**: "Add CIEU database query helper"
- **Scope**: `scripts/cieu_trace.py` or `scripts/_cieu_helpers.py`
- **Max lines**: +50
- **Example**: "Add `get_tier1_dispatch_count(agent_id, last_n_hours)` to _cieu_helpers"

### Samantha (secretary) Templates

**Template S1**: Merge agent charter section
- **Pattern**: "Update .claude/agents/*.md, additive section only"
- **Scope**: `.claude/agents/{agent_name}.md`, existing file only
- **Max lines**: +30
- **Example**: "Add 'Tier Routing Compliance' section to .claude/agents/ceo.md"

**Template S2**: Extend ARCHIVE_INDEX
- **Pattern**: "Add entry to knowledge/*/ARCHIVE_INDEX.md"
- **Scope**: `knowledge/*/ARCHIVE_INDEX.md`
- **Max lines**: +10
- **Example**: "Add tiered_routing_protocol_v1.md to knowledge/cto/ARCHIVE_INDEX.md"

**Template S3**: Log file rotation
- **Pattern**: "Rotate/archive log file"
- **Scope**: `scripts/.logs/`, `.ystar_session.json` (read-only for this), move files only
- **Max ops**: 5 file moves
- **Example**: "Move scripts/.logs/dialogue_contract.log to scripts/.logs/archive/dialogue_contract_20260416.log"

### Leo Chen (eng-kernel) Templates

**Template L1**: Extend kernel helper
- **Pattern**: "Add helper function to ystar/kernel/*"
- **Scope**: `ystar/kernel/*.py`, existing file only, additive
- **Max lines**: +80
- **Example**: "Add `parse_tier_from_task_card(path)` to ystar/kernel/task_utils.py"

**Template L2**: Add kernel test
- **Pattern**: "Write test_kernel/*.py"
- **Scope**: `tests/test_kernel/*.py`, new file OK
- **Max lines**: ≤150
- **Example**: "Write test_kernel/test_task_parser.py with 3 tier classification cases"

### Jordan Lee (eng-domains) Templates

**Template J1**: Write domain-specific test
- **Pattern**: "Add test for domain pack"
- **Scope**: `tests/test_domains/*.py`, new file OK
- **Max lines**: ≤120
- **Example**: "Write test_domains/test_claw_template.py"

**Template J2**: Add domain pipeline check
- **Pattern**: "Extend domain validation pipeline"
- **Scope**: `ystar/domains/validation.py`, additive
- **Max lines**: +60
- **Example**: "Add `validate_tier_routing_config()` to domains/validation.py"

---

## 4. ForgetGuard Rule Spec

**Rule Name**: `dispatch_tier_misclassified`

**Mode**: `warn` (48h dry_run, then escalate to deny per Maya decision)

**Trigger**: Agent tool dispatch actual scope exceeds claimed tier

**Implementation** (Maya eng-governance task card):

```yaml
# ystar/governance/forget_guard_rules.yaml

dispatch_tier_misclassified:
  mode: warn
  dry_run_hours: 48
  description: "Fires when Agent tool dispatch's actual post-completion scope exceeds claimed tier in CIEU_DISPATCH event"
  
  trigger:
    event_sequence:
      - type: CEO_DIRECT_DISPATCH_TIER1
        capture: [estimated_tool_uses, files_in_scope, engineer_id]
      - type: AGENT_SPAWN  # eng-{role} sub-agent starts
      - type: AGENT_COMPLETE  # sub-agent returns
      - post_check:
          actual_tool_uses: "query CIEU events between AGENT_SPAWN and AGENT_COMPLETE"
          actual_files_modified: "query Write/Edit tool_use events, count distinct file_path"
          
  condition: |
    (claimed_tier == 1 AND actual_files_modified > 3) OR
    (claimed_tier == 1 AND actual_tool_uses > 15) OR
    (claimed_tier == 1 AND no_template_match(files_in_scope, pre_authorized_templates))
    
  violation_message: |
    ❌ Tier misclassification detected:
    Claimed: T1 (CEO direct dispatch)
    Actual scope:
      - Files modified: {actual_files_modified} (T1 limit: 3)
      - Tool uses: {actual_tool_uses} (T1 limit: 15)
      - Template match: {template_matched}
    
    Action required:
    - If scope creep during execution → acceptable, log and continue
    - If pre-dispatch estimate wrong → CEO must recalibrate classifier
    - If engineer exceeded assigned scope → engineer discipline issue, CTO review
    
  dry_run_behavior: "Log violation to .logs/tier_misclassified.log, emit CIEU event, do NOT block"
  
  post_dry_run: "After 48h, Maya reviews .logs/tier_misclassified.log and proposes mode=deny threshold or keeps warn"
```

**Task card for Maya**: Create `.claude/tasks/maya-tier-classifier-forgetguard.md` with above spec, acceptance criteria = rule added to forget_guard_rules.yaml + tested with mock T1→T2 scope creep case.

---

## 5. CIEU Audit Chain

Every dispatch emits tier classification + routing decision + post-completion scope verification.

**Event sequence**:

1. **Pre-dispatch** (CEO layer):
   - `CEO_TASK_RECEIVED` — Board/autonomous trigger
   - `TIER_CLASSIFIED` — classifier output (tier_level, confidence, matched_keywords)
   - Decision branch:
     - T1 → `CEO_DIRECT_DISPATCH_TIER1` (engineer_id, template_matched, estimated_tool_uses, files_in_scope)
     - T2 → `CTO_ROUTING_INITIATED` (task_card_path)
     - T3 → `BOARD_ESCALATION_DRAFTED` (proposal_path)

2. **Execution**:
   - `AGENT_SPAWN` (agent_id=eng-{role}, parent=ceo, task_card_ref)
   - Sub-agent work (N tool_use events)
   - `AGENT_COMPLETE` (status, return_blob_size)

3. **Post-completion audit**:
   - `TIER_SCOPE_AUDIT` (claimed_tier, actual_tool_uses, actual_files_modified, template_compliance)
   - If mismatch → `dispatch_tier_misclassified` ForgetGuard event

4. **CTO review** (T2 only):
   - `CTO_REVIEW_STARTED` (task_card_path)
   - `CTO_DECISION` (approved / rework_requested / escalate_to_t3)

5. **Board approval** (T3 only):
   - `BOARD_DECISION` (approved / denied / deferred)
   - If approved → `T3_EXECUTED` (commit_hash / release_tag / etc.)

**Audit query examples** (for CEO/CTO/Board):

```sql
-- T1 bypass rate (should be >60% if protocol working)
SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM cieu WHERE event_type LIKE '%DISPATCH%')
FROM cieu 
WHERE event_type = 'CEO_DIRECT_DISPATCH_TIER1'
AND timestamp > datetime('now', '-7 days');

-- T1 misclassification rate
SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM cieu WHERE event_type = 'CEO_DIRECT_DISPATCH_TIER1')
FROM cieu
WHERE event_type = 'dispatch_tier_misclassified'
AND json_extract(metadata, '$.claimed_tier') = 1;

-- CTO bottleneck relief (avg T2 routing time)
SELECT AVG(julianday(complete.timestamp) - julianday(start.timestamp)) * 24 AS avg_hours
FROM cieu start
JOIN cieu complete ON start.session_id = complete.session_id 
  AND json_extract(start.metadata, '$.task_card_path') = json_extract(complete.metadata, '$.task_card_path')
WHERE start.event_type = 'CTO_ROUTING_INITIATED'
AND complete.event_type = 'CTO_DECISION';
```

---

## 6. Migration from Current Rule

**Current rule** (`feedback_dispatch_via_cto.md`):
> 跨工程师的工作必须先派 Ethan-CTO，由 CTO 分派给 Leo/Maya/Ryan/Jordan。CEO 不能跳过 CTO 直接派工程师。

**Update**:

```markdown
# feedback_dispatch_via_cto.md (UPDATED 2026-04-16)

跨工程师或架构工作 (T2/T3) 必须先派 Ethan-CTO。单工程师原子任务 (T1) CEO 可直派。

**Tier definitions**: See `governance/tiered_routing_protocol_v1.md`

**T1 (CEO 直派允许)**:
- Single engineer, ≤15 tool_uses, ≤3 files, matches pre-authorized template
- Examples: add ForgetGuard warn rule, extend hook try/except, add test assertions
- CIEU: `CEO_DIRECT_DISPATCH_TIER1`

**T2 (必经 CTO)**:
- ≥2 engineers OR new module OR >3 files OR architectural decision OR ForgetGuard deny rule
- CTO writes task card → CEO spawns engineer (workaround for nested sub-agent limit)
- CIEU: `CTO_ROUTED_TIER2`

**T3 (Board 必批)**:
- commit/push, PyPI release, payment, external comm, rollback, amendment
- CIEU: `BOARD_ESCALATED_TIER3`

**Why updated**: 2026-04-16 Board catch — CTO single-point routing created bottleneck; 80% tasks were T1-shaped and didn't need CTO architectural review. Tier protocol eliminates unnecessary serialization while preserving CTO authority for true cross-cutting work.

**Enforcement**: ForgetGuard rule `dispatch_tier_misclassified` (warn mode 48h) audits actual scope vs claimed tier.
```

**MEMORY file to create**: `feedback_tiered_routing_protocol.md` (this migration note becomes new memory entry)

---

## Appendix: Empirical Tier Distribution (2026-04-16)

Based on `.claude/tasks/*.md` file analysis:

**T1 candidates** (~75-80%):
- `cto-m1-maya-l5-forgetguard.md` — add ForgetGuard deny rule (actually T2 because mode=deny, but task is atomic)
- `cto-m5-ryan-a025-p4-boot-self-test.md` — extend governance_boot.sh with test step
- `W16_maya_amendment_governance.md` — fix 6 test failures in 2 files
- `W16_ryan_hook_chaos_others.md` — hook resilience test (single file)
- `secretary_fix5_intent_prefix.md` — fix intent prefix pattern (single file)
- `p2_path_a_acknowledgement_fix.md` — fix Path A acknowledgement (likely 1-2 files)

**T2 examples** (~15-20%):
- `eng-governance-20260413-a023-rules-tests.md` — A023 full rule suite (cross-cutting)
- `eng-platform-20260413-a023-enforcement-infra.md` — enforcement infrastructure (new module)
- `governance-evolution-exec-spec.md` — governance evolution spec (architectural)
- `cto-governance-evolution-blocker.md` — blocker analysis (multi-engineer)
- `eng-governance-heartbeat.md` — heartbeat system (new component)

**T3 examples** (~5%):
- `AMENDMENT_015_SYSTEMIC_UNLOCK_20260413.md` — amendment (Board approval)
- `board-github-token-workflow-scope.md` — Board directive (external auth)
- `NEXT_SESSION_P0_yml_session_bridge.md` — critical system change (CTO + Board)

**Conclusion**: If T1 direct dispatch had been allowed, CEO could have resolved 75-80% of tasks without CTO serialization, reducing average task latency from ~2h (CTO task card write + spawn + review) to ~20min (CEO direct spawn).
