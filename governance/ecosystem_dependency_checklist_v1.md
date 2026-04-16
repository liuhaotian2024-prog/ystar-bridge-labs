# Ecosystem Dependency Checklist v1.0

**Constitutional — Board 2026-04-16 Design Discipline**

**Context**: Board catch — CEO design blind-spot: 创新 engineers (#72 skill-trust 5 new engineers) 没列联动，cascade backlog 拖死 risk。Single atomic spec含 standard 8-cascade checklist + counterfactual probe + meta-learning self-probe + naming-collision pre-check.

**Authority**: CTO discipline enforcement. Per Board 2026-04-16 directive: "创新 engineers 没列联动 → cascade backlog 拖死 risk. Single atomic 含 spec + ForgetGuard rule + retroactive audit."

---

## Part 1 — Standard 8-Cascade Checklist for New Entity Creation

**Applies to**: Any new (a) agent (b) engineer (c) entity with identity/scope/responsibility (d) system component requiring dispatch/enforcement/coordination.

**When to apply**: Before creating charter file, before naming new entity, before assigning first task.

### 8 Cascades (ALL must be enumerated before creation)

**Cascade (a): Charter file `.claude/agents/{id}.md`**
- Where does charter live? (`.claude/agents/` for sub-agents, `agents/` for C-suite)
- Template: use existing engineer charter as model (e.g., `eng-platform.md`)
- MUST include: Session boot protocol, scope boundaries, prohibited files, thinking discipline, recognition patterns

**Cascade (b): Canonical agent_id registry update**
- Add entry to `governance/agent_id_canonical.json` "roles" or "system_components"
- Format: `"eng-{id}": {"display_name": "Full Name", "scope": "brief", "created": "2026-04-16"}`
- MUST NOT conflict with existing agent_id or aliases

**Cascade (c): governance_boot.sh CHARTER_MAP / STEP entry**
- Add `elif [ "$AGENT_ID" = "eng-{id}" ]; then CHARTER_FILE=".claude/agents/eng-{id}.md"` to STEP 11.5 CHARTER_MAP
- Verify boot script recognizes new agent_id and mounts charter

**Cascade (d): Dispatch routing acceptance**
- **Board dispatch**: Can Board directly name this engineer in chat? (requires CEO recognition pattern update in `knowledge/ceo/` or `.claude/agents/ceo.md` dispatch logic)
- **Sync layer**: Does `scripts/sync_layer.py` or `dispatch_board.py` need to recognize new engineer_id for claim/complete?
- **Engineer-task subscriber**: If eng-* role, does `scripts/engineer_subscriber.py` need new engineer_id in whitelist?

**Cascade (e): Hook handler scope**
- Which Y*gov hooks need to know this entity exists? (e.g., `must_dispatch_via_cto`, `engineer_file_scope_check`, `claim_metadata_validator`)
- Does this entity need pre-authorization templates? (if eng-*, see `governance/tiered_routing_protocol_v1.md` §3)
- Does this entity emit CIEU events? (requires hook whitelist update if new event_type)

**Cascade (f): CIEU schema if new event_type emit**
- If entity emits new event_type (e.g., `ENG_DATA_ANOMALY_DETECTED`), define schema in `governance/cieu_event_taxonomy.md`
- Add event_type to `scripts/_cieu_helpers.py` emit_cieu() docstring examples

**Cascade (g): ForgetGuard rule scope (agent_filter field update)**
- Which existing ForgetGuard rules need agent_filter updated to include/exclude new entity?
- Example: `ceo_dispatch_tier1_block` rule agent_filter = "ceo" — if new entity should also be blocked from direct T1 dispatch, add to filter
- Example: `engineer_file_scope_drift` rule — if new engineer has unique file scope, add exception or extend pattern

**Cascade (h): Pre-auth template per engineer**
- If eng-* role, create pre-authorization template in `governance/tiered_routing_protocol_v1.md` §3 (or inherit from base engineer template)
- Define: allowed file patterns, allowed edit patterns, forbidden patterns, auto-escalation triggers

---

## Part 2 — Counterfactual Probe Template

**Before creating entity X, answer**:

1. **Dispatch routing**: If this entity claims a task, which 5+ other entities need to know about it? (CEO / CTO / sync layer / dispatch board / engineer subscriber / hook validator / ...)
2. **Charter mount**: If this entity starts a session, which 3+ other files need to reference its charter path? (governance_boot.sh / agent_id_canonical.json / AGENTS.md / ...)
3. **CIEU events**: If this entity emits events, which 3+ other entities consume those events? (Secretary audit / drift observer / trust score updater / ...)
4. **Naming collision**: Does this entity's ID conflict with any existing agent_id / alias / skill name / file path stem? (e.g., "Sofia" engineer conflicts with "Sofia-CMO", "alex" engineer conflicts with "Alex-CSO" if later added)
5. **File scope**: If this entity writes files, which 3+ other entities need to validate/review those files? (CTO code review / hook scope validator / pre-commit tests / ...)
6. **Governance rules**: Which 5+ existing ForgetGuard rules need agent_filter updates to account for this entity? (dispatch block / file scope / pre-auth templates / ...)

**Threshold**: If ANY question produces ≥3 affected entities → MUST enumerate all cascades before creation. If total affected entities across all 6 questions ≥10 → escalate to CTO for architectural review before creation.

---

## Part 3 — Meta-Learning Self-Probe (Retrospective for CEO)

**After every new entity creation (or after Board catch), CEO MUST answer**:

1. **Pattern**: 过去 3 CEO design 缺哪类联动? (e.g., "charter mount cascade", "dispatch routing cascade", "naming collision")
2. **Root cause**: Why did I miss this cascade? (e.g., "只想到 charter 创建，没想到 boot script recognition", "只想到功能实现，没想到审计 observer 需要消费 CIEU events")
3. **Prevention**: How do I catch this earlier next time? (e.g., "use counterfactual probe template before any creation", "read existing entity charters to extract cascade pattern")
4. **Systemic fix**: Should we add a new item to 8-cascade checklist? (if yes, update this spec + ForgetGuard rule)

**Write to**: `knowledge/ceo/lessons/ecosystem_cascade_retrospectives.md` (append each retrospective with timestamp)

---

## Part 4 — Naming-Collision Pre-Check

**Before assigning any new agent_id, run**:

```bash
# Check existing agent_id in canonical registry
grep -i "new_id" /Users/haotianliu/.openclaw/workspace/ystar-company/governance/agent_id_canonical.json

# Check existing charter files
ls /Users/haotianliu/.openclaw/workspace/ystar-company/.claude/agents/ | grep -i "new_id"
ls /Users/haotianliu/.openclaw/workspace/ystar-company/agents/ | grep -i "new_id"

# Check full-name collision (e.g., "Sofia Chen" engineer vs "Sofia Zhang" CMO)
grep -ri "new_full_name" /Users/haotianliu/.openclaw/workspace/ystar-company/.claude/agents/
grep -ri "new_full_name" /Users/haotianliu/.openclaw/workspace/ystar-company/agents/
```

**Collision resolution**:
- **agent_id collision**: Use disambiguating suffix (e.g., `sofia-compliance` vs `sofia-cmo`)
- **Full-name collision**: Use different first name or add middle initial (e.g., "Sofia C. Chen" vs "Sofia Zhang")
- **Alias collision**: Document in `governance/agent_id_canonical.json` "aliases" field + add disambiguation note in charter

---

## Part 5 — Enforcement via ForgetGuard (see governance/forget_guard_rules.yaml)

**Rule**: `ceo_design_ecosystem_blind`

**Mode**: warn (dry-run for 48h until 2026-04-18, then switch to deny)

**Trigger**: CEO dispatch (Agent tool prompt) ≥200 chars contains "create new" / "新增" / "spawn engineer" / "ship new module" / "立 rule" keyword AND missing **Ecosystem Dependency Map / EDM / 联动** section

**Pattern**:
- Positive match: `(?i)(create|新增|ship|立|spawn).+?(engineer|module|rule|event|template|charter)`
- Negative match (bypass): `(?i)(ecosystem|联动|cascade|EDM|dependency.?map)`

**Helper**: `scripts/coordinator_audit.py::check_ecosystem_view_present(prompt) -> dict | None`

**Inline test card for Maya (governance engineer)**:

```markdown
## Task: Implement ForgetGuard rule ceo_design_ecosystem_blind
Engineer: maya-governance
Priority: P1
Tier: T1 (≤10 tool_uses)

**Acceptance Criteria**:
- [ ] Add rule to `governance/forget_guard_rules.yaml` with pattern above
- [ ] Implement `scripts/coordinator_audit.py::check_ecosystem_view_present(prompt)`
- [ ] Helper returns `{"missing": True, "keywords_matched": [...]}` if positive match + no negative match
- [ ] Helper returns `None` if bypass (contains "ecosystem" / "联动" / ...)
- [ ] Rule mode=warn, emit CIEU event `CEO_DESIGN_ECOSYSTEM_BLIND_DRIFT`
- [ ] Inline test: `pytest tests/governance/test_ecosystem_blind_rule.py -q` (≥2 tests: rule_triggers_on_missing_edm, rule_bypasses_on_edm_present)
- [ ] 48h dry-run window: switch to mode=deny on 2026-04-18 00:00 ET

**Files in scope**: `governance/forget_guard_rules.yaml`, `scripts/coordinator_audit.py`, `tests/governance/test_ecosystem_blind_rule.py`
```

---

## Part 6 — Usage Protocol

**When CEO receives task involving**:
- Creating new agent/engineer/entity
- Spawning new module/feature with identity
- Establishing new governance rule affecting dispatch

**MUST**:
1. Run naming-collision pre-check (Part 4)
2. Run counterfactual probe template (Part 2)
3. Enumerate all 8 cascades (Part 1) in dispatch prompt or task card
4. If total affected entities ≥10 → escalate to CTO for architectural review
5. After creation → run meta-learning self-probe (Part 3)

**Output format in dispatch**:

```
## Ecosystem Dependency Map (EDM)

### Counterfactual Probe
- Dispatch routing: [list 5+ entities]
- Charter mount: [list 3+ entities]
- CIEU events: [list 3+ entities]
- Naming collision: [collision check result]
- File scope: [list 3+ entities]
- Governance rules: [list 5+ entities]

### 8-Cascade Checklist
(a) Charter file: [path]
(b) Canonical registry: [entry added]
(c) governance_boot.sh: [STEP 11.5 updated]
(d) Dispatch routing: [board/sync/subscriber updates]
(e) Hook handler scope: [which hooks updated]
(f) CIEU schema: [new event_type if any]
(g) ForgetGuard rules: [which rules need agent_filter update]
(h) Pre-auth template: [template path or "inherit base"]

### Total Cascade Impact
Affected entities: [count] (threshold: ≥10 → escalate to CTO)
```

**Failure to include EDM section → ForgetGuard rule `ceo_design_ecosystem_blind` triggers warn/deny.**

---

## Change Log

- 2026-04-16: Initial spec (CTO Ethan per Board design discipline directive)
