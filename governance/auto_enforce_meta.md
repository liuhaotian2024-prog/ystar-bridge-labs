# Auto-Enforcement Meta-Observer Specification

**Authority**: Board 2026-04-16 P0 constitutional-meta directive — "把 enforcement landing 流程自动化常态化"
**Owner**: eng-governance (Maya Patel)
**L-Tag**: L4 SHIPPED (spec + helper + rule + test)
**Scope**: Automated detection of enforcement gaps requiring promotion from warn→deny or charter→runtime hardening

---

## 1. Problem Statement

Universal Enforcement Audit (2026-04-16) revealed:
- **18 constitutional rules**, only **2 fully hardened** (Rt+1=0)
- **System-wide residual gap**: Σ Rt+1 = 33
- **Manual bottleneck**: CEO must periodically audit + match candidates vs criteria + draft 5-tuple dispatch + spawn engineer

**Automation target**: Steps 1-3 (scan → match → candidate queue). Step 4 (spawn) remains CEO scope (requires Claude Code Agent tool).

---

## 2. Six Enforcement Criteria (from CEO Universal Audit Framework)

A rule/doctrine/obligation qualifies for **auto-enforcement hardening** when it meets **≥3 of 6 criteria**:

| # | Criterion | Detection Method | Weight |
|---|---|---|---|
| **C1** | **Recurrence ≥1** | CIEU `event_type=*_DRIFT` + `violations` array contains `rule_id` ≥1 times in last 30d | HIGH — proven failure mode |
| **C2** | **Constitutional weight** | Rule source contains keywords: `Iron Rule` / `Constitutional` / `Board [0-9]{4}-[0-9]{2}-[0-9]{2}` / `non-violable` | HIGH — Board/governance origin |
| **C3** | **Failure cost ≥P1** | CIEU drift record `severity` field ∈ {`critical`, `P0`, `P1`} OR manual annotation in charter `# severity: P0` | MEDIUM — blast radius |
| **C4** | **Detectability** | Rule has ≥1 ForgetGuard rule YAML entry (even if action=`warn`) | MEDIUM — scan infra exists |
| **C5** | **Self-comply gap** | Agent emitting drift = agent governed by rule (e.g., CEO violates CEO Dispatch Self-Check) | MEDIUM — role-level hypocrisy |
| **C6** | **Self-referential** | Rule governs enforcement/governance itself (e.g., Atomic Dispatch doctrine, L-tag taxonomy, CIEU 5-tuple) | MEDIUM — meta-governance stability |

---

## 3. Decision Tree (Auto-Dispatch Logic)

```
INPUT: rule candidate R with criteria scores [C1..C6]

IF count(criteria met) < 3:
    → SKIP (below threshold)

ELIF count(criteria met) == 3:
    → QUEUE as P1 (backlog)
    → emit CIEU ENFORCEMENT_GAP_DETECTED (severity=medium)

ELIF count(criteria met) >= 4:
    → QUEUE as P0 (priority)
    → emit CIEU ENFORCEMENT_GAP_DETECTED (severity=high)
    → IF C1=TRUE (recurrence proven):
        → auto-generate task card draft in `.claude/tasks/auto_enforce_{rule_id}.md`
        → emit CIEU AUTO_DISPATCH_CANDIDATE_READY (CEO must review+spawn)

ELIF C2=TRUE AND C5=TRUE (constitutional + self-comply gap):
    → ESCALATE to Board via `.claude/tasks/board_enforce_{rule_id}.md`
    → emit CIEU BOARD_ENFORCEMENT_ESCALATION
```

**Auto-spawn skeleton** (CEO inserts atomic dispatch from candidate's gap-fill template):
- Read rule charter source
- Identify missing layer: L1 (charter) / L2 (boot-load) / L3 (runtime ForgetGuard/hook)
- Draft 5-tuple per `governance/sub_agent_atomic_dispatch.md`:
  - **Y\***: `{rule_id} enforcement ≥ L{target_layer} with {specific_detector}`
  - **Xt**: current coverage (from Universal Audit Rt+1 score)
  - **U**: ≤15 tool_uses (add ForgetGuard rule / extend hook / write test)
  - **Yt+1**: L{target_layer} shipped + test PASS
  - **Rt+1**: gap-specific (e.g., `1 if rule missing` + `1 if test fails`)

---

## 4. Escalation Policy

- **P0 queue** (≥4 criteria): CEO review within 24h → spawn or defer with reason
- **P1 queue** (==3 criteria): CEO review within 72h
- **Board escalation** (C2+C5 combo): Board manual authorization required before enforcement (constitutional self-governance loop)

**ForgetGuard rule** `enforcement_gap_persistent`:
- **Trigger**: same `rule_id` appears in ≥2 consecutive observer scans (7d interval)
- **Action**: `warn` (not `deny` — meta-observer cannot block, only alert)
- **Message**: "Persistent enforcement gap detected: {rule_id} has Rt+1={score} across {N} scans. CEO: review `.claude/tasks/auto_enforce_{rule_id}.md` or mark WONTFIX with reason."

---

## 5. Helper API Contract

**Module**: `Y-star-gov/ystar/governance/enforcement_observer.py`

**Function**: `scan_pending_enforcement_candidates() -> list[dict]`

**Return schema**:
```python
[
    {
        "rule_id": str,              # e.g., "IRON_RULE_2_ATOMIC_DISPATCH"
        "source": str,               # file path (AGENTS.md / CLAUDE.md / governance/*.md)
        "criteria_met": list[str],   # e.g., ["C1_recurrence", "C2_constitutional", "C4_detectability"]
        "criteria_count": int,       # len(criteria_met)
        "priority": str,             # "P0" | "P1" | "SKIP"
        "rt_score": int,             # current Rt+1 from last audit (if available)
        "last_violation_ts": float,  # CIEU timestamp of most recent drift (or 0 if none)
        "recommended_engineer": str, # "Ryan" (hook) | "Maya" (ForgetGuard) | "Leo" (CIEU) based on gap type
        "gap_type": str,             # "L1_charter" | "L2_boot" | "L3_runtime" | "promotion_warn_to_deny"
    },
    ...
]
```

**Dependencies**:
- `ystar.governance.cieu_store.CIEUStore` — query drift events
- `pathlib.Path` + `re` — scan governance files for keywords
- `json` — parse `.ystar_session.json` ForgetGuard registry (if needed)

**Scan sources** (in priority order):
1. `governance/` directory — all `*.md` files
2. `AGENTS.md` — sections tagged `## Rules`, `## Iron Rule`, `### {Agent} Agent`
3. `CLAUDE.md` — `## IRON RULE` blocks
4. `.claude/agents/*.md` — agent charter `## Constitutional` sections

---

## 6. Test Requirements

**File**: `Y-star-gov/tests/governance/test_enforcement_observer.py`

**Minimum 6 assertions**:
1. **Criterion C1** (recurrence): mock CIEU with 2 drift events for `rule_A` → assert `rule_A` in candidates with `C1_recurrence` in `criteria_met`
2. **Criterion C2** (constitutional): mock governance file with "Iron Rule 99" text → assert candidate has `C2_constitutional`
3. **Criterion C4** (detectability): mock ForgetGuard YAML entry → assert `C4_detectability`
4. **Decision tree P0**: candidate with 4 criteria → assert `priority="P0"`
5. **Decision tree SKIP**: candidate with 2 criteria → assert not in returned list
6. **Empty scan**: no governance files, no CIEU events → assert `scan_pending_enforcement_candidates() == []`

**Test mode**: use `tmpdir` fixture + mock CIEUStore to avoid real DB dependency.

---

## 7. CLI Demo

```bash
# Scan current state and print candidates
python3 -c "
from ystar.governance.enforcement_observer import scan_pending_enforcement_candidates
import json
candidates = scan_pending_enforcement_candidates()
print(json.dumps(candidates, indent=2))
"
```

**Expected output** (example):
```json
[
  {
    "rule_id": "IRON_RULE_2_ATOMIC_DISPATCH",
    "source": "governance/sub_agent_atomic_dispatch.md",
    "criteria_met": ["C1_recurrence", "C2_constitutional", "C4_detectability"],
    "criteria_count": 3,
    "priority": "P1",
    "rt_score": 1,
    "last_violation_ts": 1713254400.0,
    "recommended_engineer": "Maya",
    "gap_type": "promotion_warn_to_deny"
  }
]
```

---

## 8. Integration with Existing Workflow

**CEO daily/weekly routine** (post-landing):
1. Run `python3 scripts/auto_enforce_scan.py` (thin wrapper around observer helper)
2. Review `.claude/tasks/auto_enforce_*.md` drafts
3. Spawn engineer sub-agent with 5-tuple from task card **OR** mark WONTFIX with reason
4. Observer persists scan results to `.ystar_cieu.db` as `ENFORCEMENT_GAP_DETECTED` events

**Convergence target**: Σ Rt+1 → 0 across all constitutional rules via automated detection + CEO atomic dispatch loop.

---

**Sign-off requirement**: Test ≥6 assertions PASS + pytest paste in receipt.
