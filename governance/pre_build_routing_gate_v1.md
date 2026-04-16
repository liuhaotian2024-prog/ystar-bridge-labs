# Pre-Build Routing Gate v1.0 — Anti-Duplication Discipline

**Author**: Maya Patel (Governance Engineer)  
**Date**: 2026-04-16  
**Status**: Draft → Review → Canonical (post-CTO approval)  
**Upstream**: MEMORY rule `feedback_god_view_before_build` (2026-04-15)  
**Downstream**: Every future sub-agent dispatch involving NEW component creation  

---

## Problem Statement

**Empirical failure pattern observed 2026-04-16 session**: CEO dispatched 5+ sub-agent atomics to write "new" specs/detectors/methodologies that all duplicated existing Y*gov modules:

1. **CZL-113** "reply scan detector" → **DUPLICATE** of `coordinator_audit.py` existing reply quality detector
2. **CZL-114-115** formal methods primer → **DUPLICATE** of `intervention_engine.py` + `causal_engine.py` existing proof integration
3. **CZL-117** observable_action_detector → **DUPLICATE** of `enforcement_observer.py` existing action tracing
4. **CZL-XXX** omission scanner v2 → **DUPLICATE** of `omission_engine.py` (canonical omission detection)
5. **CZL-XXX** narrative coherence detector → **DUPLICATE** of `metalearning.py` narrative_coherence_score function

**Root cause**: MEMORY rule `feedback_god_view_before_build` (2026-04-15) established manual discipline ("Glob+Grep scan 4 repos before proposing new components"), but discipline relies on CEO self-control, which failed under load. Board caught it: "我们又在重复造轮子，Y*gov 输入管线本身就是这一套东西."

**Solution**: Automate god-view precheck via **Pre-Build Routing Gate** — mandatory precheck script invocation before any NEW file creation in governance namespaces. Convert discipline from human-discipline to machine-enforced routing decision tree.

---

## Routing Decision Tree

```
NEW component request arrives
  ↓
Run `python3 scripts/precheck_existing.py <component_name>`
  ↓
Scan 4 repos (ystar-company / Y-star-gov / K9Audit / OpenClaw)
  ↓
Matches found? (name + synonym glob+grep)
  ↓
YES → ROUTE_TO_EXTEND atomic
  │   - Sub-agent reframes atomic as "extend existing <file>"
  │   - Explicit justification in receipt why extend vs rebuild
  │   - Receipt cites precheck JSON output
  │
NO → BUILD_NEW atomic (allowed, but requires justification)
  │   - Sub-agent writes new file
  │   - Receipt MUST cite precheck JSON {"matches": [], "routing_recommendation": "build_new"}
  │   - Justification required: why no existing component fits
```

---

## 4-Repo Coverage Map

| Repo              | Purpose                              | Example Paths                                              |
|-------------------|--------------------------------------|------------------------------------------------------------|
| **ystar-company** | Operations, scripts, knowledge       | `scripts/`, `governance/`, `knowledge/`, `reports/`        |
| **Y-star-gov**    | Governance product source            | `ystar/governance/`, `ystar/adapters/`, `ystar/domains/`   |
| **K9Audit**       | Causal audit tooling (read-only)     | `k9log/`, `k9_repo_audit.py`, `tests/k9/`                  |
| **OpenClaw**      | Workspace adapter (external, rarely) | `adapters/`, `harness/`                                    |

**Precheck scan order**:
1. Y-star-gov (primary product source, highest overlap risk)
2. ystar-company (operations scripts, governance specs)
3. K9Audit (causal audit patterns, read-only)
4. OpenClaw (workspace adapter, low overlap but check anyway)

---

## Component Category → Repo Routing Rules

| Component Type                  | Primary Repo        | Routing Logic                                                                 |
|---------------------------------|---------------------|-------------------------------------------------------------------------------|
| **Detector / Scanner**          | Y-star-gov          | Match against `ystar/governance/*_engine.py`, `*_detector.py`, `*_scanner.py` |
| **Audit / CIEU log**            | Y-star-gov          | Match against `cieu_store.py`, `causal_chain_analyzer.py`, `k9_routing_subscriber.py` |
| **Operations script**           | ystar-company       | Match against `scripts/*.py`, `scripts/governance_*.py`                       |
| **Domain pack**                 | Y-star-gov          | Match against `ystar/domains/*.py`                                            |
| **Adapter / integration**       | Y-star-gov          | Match against `ystar/adapters/*.py`                                           |
| **Knowledge / spec / template** | ystar-company       | Match against `governance/*.md`, `knowledge/**/*.md`                          |
| **Test**                        | Y-star-gov (source) | Match against `tests/**/*.py`                                                 |
| **ForgetGuard rule**            | Y-star-gov          | Match against `forget_guard_rules.yaml`                                       |

**Synonym expansion**:
- "detector" → "scanner", "analyzer", "observer", "monitor"
- "audit" → "CIEU", "causal", "chain", "log"
- "script" → "automation", "tool", "workflow"
- "engine" → "loop", "policy", "enforcer"

Precheck script MUST expand synonyms to reduce false negatives.

---

## Anti-Pattern Catalog (Today's Violations)

| CZL # | Requested Component         | Duplicate Of                     | Miss Type          | Precheck Would Catch? |
|-------|-----------------------------|----------------------------------|--------------------|------------------------|
| 113   | reply scan detector         | coordinator_audit.py             | Name synonym miss  | YES (scan→audit)       |
| 114   | formal methods primer       | intervention_engine.py           | Category miss      | YES (proof→intervention)|
| 115   | formal methods spec         | causal_engine.py                 | Category miss      | YES (proof→causal)     |
| 117   | observable_action_detector  | enforcement_observer.py          | Name exact miss    | YES (action→observe)   |
| ?     | omission scanner v2         | omission_engine.py               | Version duplication| YES (name exact match) |
| ?     | narrative coherence detector| metalearning.py (narrative_coherence_score) | Function-level dup | PARTIAL (need deep scan) |

**Success criteria**: Precheck script catches ≥80% of duplicates via name+synonym glob. Remaining 20% (function-level deep duplicates) require human judgment, but forcing precheck invocation raises awareness baseline.

---

## Implementation Plan

### 1. Precheck Script (`scripts/precheck_existing.py`)

**Input**: `component_name` (string, e.g., "reply_scan_detector")

**Action**:
1. Expand synonyms (detector→scanner/analyzer/observer/monitor)
2. Glob+grep across 4 repos:
   - Y-star-gov: `ystar/governance/*.py`, `ystar/adapters/*.py`, `ystar/domains/*.py`
   - ystar-company: `scripts/*.py`, `governance/*.md`, `knowledge/**/*.md`
   - K9Audit: `k9log/*.py`, `tests/k9/*.py`
   - OpenClaw: `adapters/*.py` (if local clone exists)
3. Match patterns:
   - Exact name match (case-insensitive)
   - Synonym expansion match
   - Camelized/snake_cased variants
4. Collect matches (repo, file, line, snippet ±3 lines context)

**Output**: JSON
```json
{
  "component_name": "reply_scan_detector",
  "matches": [
    {
      "repo": "Y-star-gov",
      "file": "ystar/governance/coordinator_audit.py",
      "line": 142,
      "snippet": "def scan_reply_quality(receipt: str) -> dict:\n    # Detect hallucinations, choice questions, missing evidence\n    ...",
      "match_type": "synonym_exact"
    }
  ],
  "routing_recommendation": "extend",
  "justification_required": true
}
```

If `matches == []`:
```json
{
  "component_name": "new_unique_detector",
  "matches": [],
  "routing_recommendation": "build_new",
  "justification_required": true
}
```

### 2. Updated Boot Prompt Template

**Insert new step 3 into `governance/sub_agent_boot_prompt_template.md`**:

```
3. **Pre-build routing gate**: If atomic involves writing NEW file in `governance/` or `Y-star-gov/ystar/governance/`, run `python3 scripts/precheck_existing.py <component_name>` BEFORE Write tool. If `matches.count > 0`, atomic MUST be reframed to EXTEND existing file OR justify BUILD_NEW with explicit reason in receipt citing precheck JSON.
```

### 3. ForgetGuard Rule (`new_artifact_without_precheck`)

**Trigger**: Write tool used to create NEW file in `governance/` or `Y-star-gov/ystar/governance/` without prior `precheck_existing.py` Bash call in same atomic.

**Mode**: `dry_run` (48h auto-promote `warn`)

**Detector logic** (≤40 lines):
```python
def detect_new_artifact_without_precheck(transcript: list[dict]) -> bool:
    """
    Scan sub-agent transcript for:
    - Write tool call creating NEW file in governance namespace
    - No prior Bash call to `precheck_existing.py` in same atomic
    """
    governance_paths = [
        "governance/",
        "Y-star-gov/ystar/governance/",
        "/ystar/governance/"
    ]
    
    write_calls = []
    precheck_calls = []
    
    for event in transcript:
        if event.get("tool") == "Write":
            file_path = event.get("parameters", {}).get("file_path", "")
            if any(p in file_path for p in governance_paths):
                write_calls.append(file_path)
        
        if event.get("tool") == "Bash":
            command = event.get("parameters", {}).get("command", "")
            if "precheck_existing.py" in command:
                precheck_calls.append(command)
    
    # Violation: governance Write without prior precheck
    if write_calls and not precheck_calls:
        return True
    
    return False
```

**Test coverage** (≥3 assertions):
1. Write to `governance/new_spec.md` without precheck → violation detected
2. Bash `precheck_existing.py foo` + Write `governance/foo.md` → no violation
3. Write to `scripts/util.py` (non-governance) → no violation

---

## Ecosystem Dependency Map

**Upstream**:
- MEMORY rule `feedback_god_view_before_build` (manual discipline, now automated)
- Campaign v6 W11 sub-goal (anti-duplicate routing requirement)

**Downstream**:
- Every future CEO/CTO sub-agent dispatch involving NEW governance component
- ForgetGuard enforcement layer (prevents precheck bypass)
- Sub-agent boot prompt template (mandatory BOOT step 3)

**Cross-cutting**:
- Y-star-gov governance module inventory (canonical entity list)
- K9Audit causal audit patterns (read-only reference)
- OpenClaw workspace adapter (low overlap but completeness)

**Naming collision risks**: None (precheck script name is unambiguous; FG rule name follows convention).

---

## Success Metrics

**L3 VALIDATED criteria**:
- Precheck script callable, returns valid JSON for test inputs
- Boot template updated with step 3
- FG rule spec complete (detector + test ≥3 assertions)

**L4 SHIPPED criteria** (deferred to next atomic):
- FG rule live in `forget_guard_rules.yaml`
- 48h dry_run window passed
- Auto-promote to `warn` mode
- 1+ real violation caught in wild

**L5 LIVE criteria** (future):
- ≥80% duplication catch rate over 30-day window
- 0 false positives (legitimate new components blocked)
- Sub-agents cite precheck JSON in 100% of NEW component receipts

---

## Edge Cases

1. **Function-level duplication** (e.g., narrative_coherence_score inside metalearning.py): Precheck catches file match, sub-agent must read file to confirm function-level dup. Not automatic, but forces awareness.

2. **Cross-repo refactor** (e.g., move detector from ystar-company to Y-star-gov): Precheck shows both locations, sub-agent must justify consolidation plan.

3. **Legitimate parallel builds** (e.g., two sub-agents writing different new components simultaneously): Precheck won't catch (different names). Acceptable — BOOT step 2 (git log) catches file-level race.

4. **K9Audit read-only** (AGPL-3.0 license): Precheck matches K9Audit patterns but sub-agent MUST NOT copy code. Extract concept only. Receipt must cite license boundary.

---

## Amendment Cascade (Per feedback_ceo_ecosystem_view_required)

| Layer                  | Entity Created               | Status   |
|------------------------|------------------------------|----------|
| Charter                | (No new agent/role)          | N/A      |
| Registry               | (No new canonical entity)    | N/A      |
| Boot                   | Template step 3 added        | CZL-118  |
| Dispatch               | Precheck script callable     | CZL-118  |
| Hook                   | FG rule `new_artifact_*`     | CZL-118  |
| CIEU                   | (No new event type)          | N/A      |
| ForgetGuard Scope      | Rule added to FG rules.yaml  | Next atomic |
| Pre-authorization      | (No Board approval required) | N/A      |

**Minimal cascade** — this is a process gate, not a new entity. Only touches Boot (template) + Dispatch (script) + Hook (FG rule).

---

## Appendix: Y*gov Governance Module Inventory (2026-04-16 Snapshot)

Canonical modules in `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/`:

- `adaptive.py` — adaptive policy tuning
- `amendment.py` — governance contract amendment lifecycle
- `auto_configure.py` — auto-configuration of Y*gov settings
- `autonomy_engine.py` — autonomous agent decision loop
- `backdoor_adjuster.py` — emergency backdoor management
- `boundary_enforcer.py` — scope boundary enforcement
- `causal_chain_analyzer.py` — causal chain tracing (K9Audit heritage)
- `causal_discovery.py` — causal graph discovery
- `causal_engine.py` — causal inference engine
- `causal_feedback.py` — causal feedback loop
- `causal_graph.py` — causal graph data structure
- `charter_drift.py` — charter drift detection
- `cieu_store.py` — CIEU event persistence
- `claim_mismatch.py` — claim vs evidence mismatch detector
- `constraints.py` — governance constraint solver
- `contract_lifecycle.py` — contract lifecycle management
- `coordinator_audit.py` — coordinator/CEO receipt quality audit
- `counterfactual_engine.py` — counterfactual reasoning engine
- `delegation_policy.py` — delegation policy enforcement
- `domain_context.py` — domain context injection
- `enforcement_observer.py` — enforcement action observer
- `experience_bridge.py` — experience bridge (session persistence)
- `forget_guard.py` — ForgetGuard core engine
- `governance_loop.py` — main governance loop orchestrator
- `intervention_engine.py` — intervention policy engine
- `intervention_models.py` — intervention models (proof integration)
- `k9_routing_subscriber.py` — K9 event routing subscriber
- `k9_rt_sentinel.py` — K9 real-time sentinel monitor
- `metalearning.py` — metalearning + narrative coherence scoring
- `narrative_coherence.py` — narrative coherence analyzer
- `observable_action.py` — observable action detector
- `omission_engine.py` — omission detection engine
- `omission_scanner.py` — omission scanner
- `path_a/` — Path A meta-agent orchestration
- `path_b/` — Path B runtime governance
- `policy_swap.py` — policy hot-swap mechanism
- `reporting.py` — governance reporting
- `retro_store.py` — retrospective analysis store
- `rule_advisor.py` — rule suggestion advisor

**Total**: 35+ modules, 40+ concepts. High duplication risk without routing gate.

---

**END OF SPEC**
