# CHARTER AMENDMENT 016: Rule Mirror Sync — Single Source of Truth for All Governance Rules

**Submitted by:** CTO (Ethan Wright)  
**Date:** 2026-04-13  
**Status:** DRAFT  
**Implementation Deadline:** 2026-04-15 (48h)  
**Dependency:** AMENDMENT-015 Layer 1 (active_agent SSoT watcher pattern, commit `4eb531a`)

---

## 1. The Meta-Root Cause

### 1.1 Current Fragmentation Audit

We have **6 separate sources of truth** for governance rules, each caching their own version with no propagation mechanism:

| Source | Format | Sample Rule | Who Writes | Who Reads | Sync Mechanism |
|--------|--------|-------------|------------|-----------|----------------|
| `AGENTS.md` | Natural language | "CTO can only access `./src/`, `./tests/`" | Board + Secretary | All agents (at boot) | **None** |
| `.ystar_session.json` | JSON paths | `"immutable_paths": [".claude/agents/"]` | Secretary | Hook daemon | **None** |
| `.claude/agents/{role}.md` | Markdown | "Permission Boundaries: You can only access..." | Secretary | Agent at spawn | **None** |
| `gov-mcp` contract registry | Y*gov contract JSON | `{deny: ["/etc", "/root"]}` | `ystar init` + manual edits | GOV MCP server | **None** |
| Hook daemon memory | Runtime state | Loaded from `.ystar_session.json` at startup | N/A | Hook client | **File mtime check** |
| Agent prompt context | LLM context window | Full AGENTS.md text | N/A | LLM | **Session restart** |

**Inconsistency example (just encountered):**
- `.ystar_session.json` line 21: `.claude/agents/` is immutable
- Hook interpretation: CTO cannot read `.claude/agents/cto.md`
- Actual intent: Agents cannot *modify* their own role definitions, but CTO reviewing engineer role cards should be allowed
- **No compliance_recipe**: Hook says "denied", doesn't say "ask Secretary to modify" or "use Agent tool to delegate read to Secretary"

### 1.2 How This Causes the 5 Lock Cycles

From `reports/lock_cycles_taxonomy_20260413.md`:

1. **Circular dependency lock**: Agent needs info from file X to complete task, but rule says can't read X, and the rule's compliance path points to another restricted file
2. **Authority query lock**: Hook denies action → agent queries GOV MCP for exemption → GOV MCP checks contract → contract is stale (last updated 3 sessions ago) → agent stuck
3. **Delegation loop lock**: Agent A delegates to Agent B → B needs permission → checks `.ystar_session.json` → rule says "escalate to CEO" → CEO delegates to A → cycle
4. **State desync lock**: Hook allows action (using session.json v1) → Agent attempts → GOV MCP denies (using contract v2) → agent doesn't know which authority is canonical
5. **Compliance recipe missing lock**: Hook denies with "not allowed", agent tries 3 different workarounds, all fail, doesn't know the *correct* path exists in a different rule source

**Root cause**: All 5 locks stem from **rule fragmentation + no sync + incomplete rule schema (deny info only, no compliance path)**.

---

## 2. Target Architecture

### 2.1 Single Source of Truth: GOV MCP Contract Registry

**Rationale**: GOV MCP already has:
- Structured contract format (JSON schema)
- Runtime query interface (MCP tools)
- Session persistence (survives agent restarts)
- CIEU audit integration (every rule check is logged)

**New requirement**: Make it the *authoritative* source. All other sources become **read-only projections**.

### 2.2 Rule Schema v2: Four-Field Design

Every rule must have 4 fields, not just `deny`:

```json
{
  "rule_id": "immutable_agents_dir",
  "condition": {
    "path_pattern": ".claude/agents/**",
    "action": "write",
    "exempt_roles": ["secretary"]
  },
  "block_msg": "Role definitions are immutable to prevent self-modification",
  "compliance_recipe": {
    "primary": "Ask Secretary to review and apply changes via curate workflow",
    "fallback": "If Secretary unavailable, write proposed changes to .claude/tasks/secretary_*.md"
  },
  "exemption_path": "Board directive overrides this rule (see AGENTS.md Article 4)"
}
```

**Key change**: `compliance_recipe` is mandatory. Every "no" must come with "here's how to do it correctly."

### 2.3 Propagation Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  GOV MCP Contract Registry (Single Source of Truth)        │
│  - Rules in 4-field schema                                  │
│  - Exposes SSE stream on rule changes                       │
│  - Exposes MCP tool: gov_rule_query(rule_id) → full schema  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├──> AGENTS.md (generated projection)
                 │    - Natural language version
                 │    - Regenerated on rule change
                 │    - Human-readable, not hand-edited
                 │
                 ├──> .ystar_session.json (generated projection)
                 │    - JSON paths for hook daemon
                 │    - Regenerated on rule change
                 │    - Hook daemon watches file mtime, reloads
                 │
                 ├──> .claude/agents/{role}.md (generated projection)
                 │    - Per-role filtered view
                 │    - Only includes rules relevant to this role
                 │    - Regenerated on rule change
                 │
                 └──> Hook daemon (SSE subscriber)
                      - Listens to GOV MCP SSE stream
                      - Reloads rules in <5 seconds on change
                      - Returns compliance_recipe in deny messages
```

**Critical property**: Only GOV MCP contract is hand-edited. All others are code-generated.

### 2.4 Migration from Current State

**Phase 1: Audit and consolidate (Day 1, 2026-04-14)**
- Script: `scripts/rule_source_audit.py`
- Output: `reports/rule_fragmentation_audit_20260413.md`
- For each rule found in any of the 6 sources:
  - Extract intent
  - Identify conflicts (same rule, different interpretation across sources)
  - Write to `data/rule_consolidation.jsonl` (one rule per line, 4-field schema)

**Phase 2: Isolated experiment (Day 2, 2026-04-15)**
- Engineer: Maya (eng-governance)
- Workspace: `/Users/haotianliu/.openclaw/workspace/ystar-company-test/`
- Goal: Prove the sync loop works
- Test: Hand-edit one rule in GOV MCP contract → verify AGENTS.md regenerates + hook behavior changes within 5 seconds + sub-agent can see change immediately
- Deliverable: Experiment report + screen recording

**Phase 3: Production migration (Day 3-5, 2026-04-16 to 2026-04-18)**
- CTO approval required before touching production
- Backup current AGENTS.md, .ystar_session.json, all agent role cards
- Run `ystar rule-migrate --from-audit data/rule_consolidation.jsonl --dry-run`
- Review generated projections
- If Board approves, run `ystar rule-migrate --apply`
- Monitor for 24h, ready to rollback

---

## 3. Relationship to AMENDMENT-015

AMENDMENT-015 Layer 1 (commit `4eb531a`) already implemented the **SSoT + watcher** pattern for `active_agent`:

- GOV MCP holds canonical value in session state
- `.ystar_active_agent` file is a projection
- File watcher reloads on change
- Sub-agents see updates within seconds

**This amendment = generalize that pattern to ALL rules.**

Key reuse opportunities:
- File watcher infrastructure (already exists in `scripts/governance_boot.sh` and hook daemon)
- SSE stream from GOV MCP (already implemented for session events)
- Projection generation pattern (already proven for `active_agent` file)

**Difference**: `active_agent` is a single scalar value. Rules are a structured schema. We need:
- Schema validation on rule write (JSON Schema or Pydantic)
- Multi-target projection (AGENTS.md ≠ .ystar_session.json ≠ agent role cards)
- Conflict detection (what if Board hand-edits AGENTS.md while script is regenerating it?)

---

## 4. Rollback Plan

### 4.1 Pre-Migration Backup

Before `ystar rule-migrate --apply`:
```bash
tar -czf backups/pre_am016_$(date +%s).tar.gz \
  AGENTS.md \
  .ystar_session.json \
  .claude/agents/ \
  memory/boot_packages/
```

### 4.2 Rollback Trigger Conditions

Rollback immediately if:
1. Any of the 86 tests fail after migration
2. Hook daemon crashes or enters infinite reload loop
3. Any agent cannot boot (blocked by malformed rule projection)
4. Board cannot complete basic workflow (read priority_brief, delegate task, review report)

### 4.3 Rollback Procedure

```bash
# Stop GOV MCP server
pkill -f gov-mcp

# Restore backup
tar -xzf backups/pre_am016_<timestamp>.tar.gz

# Restart with old config
bash scripts/governance_boot.sh ceo

# Verify ALL SYSTEMS GO
```

**Time to rollback**: <5 minutes  
**Data loss risk**: Zero (all changes are in git, CIEU logs preserved)

---

## 5. Open Questions (Require Board Input)

### 5.1 Conflict Resolution: Human Edit vs. Code Generation

**Scenario**: Board hand-edits AGENTS.md to add a new rule. Meanwhile, `rule_watcher.py` regenerates AGENTS.md from GOV MCP contract.

**Options**:
1. **Human edits always win**: Watcher detects human edit (git diff), extracts new rule, writes to GOV MCP, then regenerates
2. **Code generation always wins**: Watcher overwrites human edits, forces all changes through `ystar rule-add` command
3. **Hybrid**: AGENTS.md has a "hand-edited rules" section that watcher never touches

**CTO recommendation**: Option 1 (human edits win, but get canonicalized). Matches Board's workflow (direct AGENTS.md editing is faster than learning `ystar` CLI).

### 5.2 Rule Schema Versioning

Current contract format is unversioned. If we make `compliance_recipe` mandatory, how do we handle:
- Old contracts without `compliance_recipe` field?
- Future schema changes (e.g., adding `audit_level` or `auto_fix_script`)?

**CTO recommendation**: Add `schema_version` field to contract, default old contracts to v1 (no compliance_recipe required), new rules must be v2.

### 5.3 Performance: Rule Query Latency

If every hook call queries GOV MCP for full rule schema (not just deny list), we add:
- MCP tool call latency (~50-200ms)
- Contract parsing overhead

**Current**: Hook reads `.ystar_session.json` from memory (no network call, <1ms)  
**After migration**: Hook must either:
  - Cache rules in memory + subscribe to SSE updates (complex, but fast)
  - Query GOV MCP on every check (simple, but adds latency)

**CTO recommendation**: Hybrid — hook caches rules, GOV MCP pushes updates via SSE, hook reloads cache.

---

## 6. Success Metrics

### 6.1 Technical Metrics

- [ ] All 6 rule sources consolidated into single GOV MCP contract (audit report shows 100% coverage)
- [ ] Rule change propagates to all projections in <5 seconds (experiment proves this)
- [ ] Hook denial messages include `compliance_recipe` (test with deliberate violation)
- [ ] Zero rule conflicts after migration (audit script finds no inconsistencies)
- [ ] All 86 tests pass after migration
- [ ] Sub-agent can see rule change without session restart (experiment proves this)

### 6.2 Operational Metrics (Measure over 7 days post-migration)

- [ ] Lock cycle incidents: <1 per week (baseline: 5 in last 48h)
- [ ] Hook denials with compliance_recipe: 100% (baseline: 0%)
- [ ] Agent escalations to Board for "how do I do X": <2 per week (baseline: ~10)
- [ ] Rule edit roundtrip time (Board intent → agent sees new behavior): <10 minutes (baseline: 1-2 hours, requires session restart)

---

## 7. Next Steps (48h Timeline)

### Day 1 (2026-04-14, EOD)
- [x] CTO writes this 6-pager
- [ ] CTO writes `scripts/rule_source_audit.py`
- [ ] CTO runs audit, produces `reports/rule_fragmentation_audit_20260413.md`
- [ ] CTO reviews audit with Board, gets approval to proceed to Day 2

### Day 2 (2026-04-15, EOD)
- [ ] CTO dispatches Maya to isolated experiment workspace
- [ ] Maya sets up `/Users/haotianliu/.openclaw/workspace/ystar-company-test/`
- [ ] Maya implements minimal SSoT sync for 1 rule
- [ ] Maya proves <5 second propagation + sub-agent visibility
- [ ] Maya writes experiment report with screen recording
- [ ] CTO reviews experiment, gets Board approval for production migration

### Day 3-5 (2026-04-16 to 2026-04-18, if Board approves)
- [ ] CTO writes `ystar rule-migrate` command
- [ ] CTO runs dry-run, reviews generated projections
- [ ] Board approves production migration
- [ ] CTO runs migration
- [ ] CTO monitors for 24h, ready to rollback

---

## 8. Architectural Debt This Amendment Pays Down

From `reports/tech_debt.md`:
- **DEBT-003**: Rule fragmentation (6 sources, no sync) → PAID (single SSoT + watcher)
- **DEBT-007**: Hook denial messages missing compliance path → PAID (4-field schema mandatory)
- **DEBT-011**: Agent delegation loops due to authority confusion → PAID (canonical authority = GOV MCP)
- **DEBT-015**: AGENTS.md manual edits don't propagate to runtime → PAID (projection generation)

**Net tech debt reduction**: 4 items, estimated 120 engineering hours saved over next 6 months.

---

## 9. Relationship to Long-Term Vision (Vogels Principle)

Werner Vogels: "Everything fails. Design for failure."

**Current state violates this**: Rule fragmentation means there's no single failure mode. An agent can be simultaneously:
- Allowed by AGENTS.md
- Denied by .ystar_session.json
- Allowed by GOV MCP contract
- Denied by hook daemon (stale cache)

**After this amendment**: Single failure mode. If GOV MCP contract is wrong, everything is wrong consistently. We can detect and fix.

**Operational runbook addition**: When agent reports "permission denied" → query GOV MCP contract directly → if contract is wrong, fix in one place → change propagates everywhere in <5 seconds.

**Chaos test addition** (post-migration):
```python
# tests/test_rule_sync_chaos.py
def test_rule_change_mid_delegation():
    """Verify rule change doesn't break in-flight delegation."""
    # Start CEO delegating to CTO
    # Mid-delegation, change a rule that affects CTO's scope
    # Verify delegation completes (uses rule version at delegation start)
    # Verify next action uses new rule
```

---

**Submitted for Board review.**  
**Awaiting approval to proceed to Day 1 audit script.**
