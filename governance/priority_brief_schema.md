# Priority Brief YAML Frontmatter Schema (AMENDMENT-009 §2.2)

**Authority**: AMENDMENT-009 §2.2 (approved 2026-04-12)
**Enforcement**: `scripts/priority_brief_validator.py` + `scripts/session_close_yml.py` hook
**Target file**: `reports/priority_brief.md`

---

## Schema Definition

Priority brief MUST contain YAML frontmatter at document start with three target arrays:

```yaml
---
version: "vX.Y"
last_updated: "YYYY-MM-DD"
status: "active|stub|deprecated"
today_targets:
  - target: "具体目标描述"
    owner: "ceo|cto|cmo|cso|cfo|eng-kernel|eng-platform|eng-governance|eng-domains"
    deadline: "EOD|HH:MM|YYYY-MM-DD"
    verify: "可验证的完成标准"
this_week_targets:
  - target: "..."
    owner: "..."
    deadline: "YYYY-MM-DD"
    verify: "..."
this_month_targets:
  - target: "..."
    owner: "..."
    deadline: "YYYY-MM-DD"
    verify: "..."
---
```

### Field Requirements

**Top-level fields** (all required):
- `version`: string, semantic version matching §9 version list
- `last_updated`: string, ISO date YYYY-MM-DD
- `status`: enum ["active", "stub", "deprecated"]
- `today_targets`: array of target objects
- `this_week_targets`: array of target objects
- `this_month_targets`: array of target objects

**Target object** (all fields required):
- `target`: string, non-empty, describes what to achieve
- `owner`: string, must be one of known agent roles
- `deadline`: string, non-empty (EOD / ISO date / timestamp)
- `verify`: string, non-empty, objective completion criteria

---

## Validation Rules

1. **Parsing**: YAML frontmatter must be valid YAML between `---` delimiters
2. **Schema**: All top-level fields must be present
3. **Target arrays**: Must be arrays (can be empty, but should not be)
4. **Target objects**: Each target must have all 4 required fields
5. **Owner validation**: `owner` must be a known agent role
6. **Non-empty strings**: `target`, `verify`, `deadline` must not be empty or whitespace-only

---

## Enforcement Points

### 1. Session Close (Warning Mode)

**When**: `scripts/session_close_yml.py` runs
**Action**: Run `scripts/priority_brief_validator.py`
**Outcome**:
- If validation fails → emit CIEU `PRIORITY_BRIEF_TARGETS_CHECK` with `decision=warn`
- If `today_targets` is empty → emit warning "ADE cannot drive daily work"
- **Does NOT block** session close (warning only)

### 2. Session Boot (Future — AMENDMENT-009 §2.2 phase 2)

**When**: `scripts/governance_boot.sh` STEP 0
**Action**: Validate priority_brief.md schema
**Outcome**:
- If validation fails → boot FAIL
- If `today_targets` empty → boot FAIL (except for secretary/passive roles)
- If `last_updated` > 48h old → boot FAIL (staleness check)

---

## CEO Update Protocol

**When to update**: Every session close, before running `session_close_yml.py`

**Process**:
1. Review completed targets from today/this_week
2. Add new targets from §2 (P0/P1 priorities)
3. Update `last_updated` to current date
4. Increment `version` (minor bump for content updates)
5. Verify all target objects have 4 required fields
6. Run validator: `python scripts/priority_brief_validator.py`
7. Fix any validation errors
8. Proceed with session close

**What drives the targets**:
- `today_targets`: Derived from §2 P0 items — must have clear EOD deliverables
- `this_week_targets`: Derived from §2 P0 + high P1 items
- `this_month_targets`: Derived from §2 P1 + strategic P2 items

---

## CIEU Event Schema

**Event Type**: `PRIORITY_BRIEF_TARGETS_CHECK`

**Params JSON**:
```json
{
  "today_count": 3,
  "week_count": 5,
  "month_count": 4,
  "validation_errors": ["error1", "error2"]
}
```

**Decision values**:
- `allow`: Schema valid, today_targets non-empty
- `warn`: Schema invalid OR today_targets empty (does not block close)

---

## Migration Guide (v0.3 → v0.4)

**Current state** (v0.3):
- No YAML frontmatter
- Metadata in markdown paragraph format
- No structured targets

**Target state** (v0.4):
- YAML frontmatter with 3 target arrays
- Extract targets from §2 P0/P1 priorities
- Map priorities to owner/deadline/verify structure

**CEO action** (next session):
1. Read this schema spec
2. Read current priority_brief.md §2 (Top-5 priorities)
3. Map P0-1/P0-2/P0-3 items to `today_targets` array
4. Map P0-2/P0-3 + high P1 to `this_week_targets`
5. Map P1/P2 strategic items to `this_month_targets`
6. Add YAML frontmatter block at document start
7. Run validator to verify
8. Update version to v0.4 in both frontmatter and §9

---

## Example (from current priority_brief.md §2)

**Current P0-1 items**:
1. CIEU persistence 断裂
2. Delegation chain INVALID
3. Circuit Breaker ARMED

**Maps to**:
```yaml
today_targets:
  - target: "CIEU persistence 断裂修复 — 切 SQLite persistent store"
    owner: "eng-kernel"
    deadline: "EOD"
    verify: "gov_doctor L1.02 不再报 in_memory_only"
  - target: "Delegation chain INVALID 修复 — chain reset + grant 逻辑审查"
    owner: "eng-platform"
    deadline: "EOD"
    verify: "gov_doctor L1.03 DELEGATION_CHAIN_INVALID 消失"
  - target: "Circuit Breaker ARMED 诊断 — dump 821 violations log"
    owner: "eng-kernel"
    deadline: "EOD"
    verify: "报告落地到 reports/diagnostics/circuit_breaker_violations.md"
```

---

## Lifecycle

- **Born**: AMENDMENT-009 approved, Jordan implements validator (2026-04-12)
- **Enforced at close**: Immediately (warning mode)
- **Enforced at boot**: Phase 2 (after CEO updates v0.3→v0.4)
- **Supersedes**: Unstructured priority tracking in DISPATCH.md
