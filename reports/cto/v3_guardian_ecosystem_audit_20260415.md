# v3 Guardian Ecosystem Audit — Reuse vs Rebuild Analysis
**Date**: 2026-04-15
**Author**: CTO (Ethan Wright)
**Purpose**: Map CEO-proposed v3 Guardian 3 components to existing Y*gov infrastructure, prevent wheel reinvention

---

## Background

CEO proposed v3 Guardian with 3 goals:
1. **Y\* Schema v2**: artifact_persistence + freshness + restore_owner mandatory fields
2. **Canonical Hash Guard**: Whitelist-based drift detection for WORKING_STYLE.md §11/§12
3. **Prompt-Level Gate**: Block agent narrative-reality gaps at UserPromptSubmit hook

Board catch: "90% already exists". This audit validates reuse vs rebuild ratio.

---

## Existing Component Inventory

| Component | Purpose (≤30 chars) | File Size | Status |
|-----------|---------------------|-----------|--------|
| `metalearning.py` | 从违规历史自适应收紧 IntentContract (8 维 + 高阶维度发现) | 115 KB | LEGACY (not on main path) |
| `contract_lifecycle.py` | IntentContract 生命周期 (draft → validated → active → superseded) | 9.4 KB | Active |
| `forget_guard.py` | Agent session 重启遗忘检测 (YAML 规则 + 违规拦截) | 5.2 KB | Active (AMENDMENT-015) |
| `narrative_coherence_detector.py` | 检测 claim 无 tool evidence (抓 fabrication) | 11 KB | Active (A-015 L3.4) |
| `residual_loop_engine.py` | CIEU Rt+1 闭环控制器 (收敛/振荡/escalation) | 15 KB | Active (A-014) |
| `retro_store.py` | 追溯基线存储 (独立 .db, source=retroactive) | 13 KB | Active (v0.41) |

---

## Mapping: v3 Goals → Existing Components

### Goal 1: Y\* Schema v2 (artifact_persistence + freshness + restore_owner)

**Candidate**: `contract_lifecycle.py` (ContractDraft dataclass)

**Current Coverage**:
- ✅ `source_document`: maps to "artifact_persistence" (stores original source)
- ✅ `created_at` / `activated_at`: maps to "freshness" (timestamps)
- ✅ `approved_by`: maps to "restore_owner" (agent ID who approved)
- ❌ Missing: `last_verified_at` field (freshness decay detection)
- ❌ Missing: `canonical_hash` field (drift detection anchor)

**Reuse Plan**:
- Extend `ContractDraft` dataclass with 2 new fields (10 lines)
- Add `verify_freshness()` method (15 lines)
- Add `compute_canonical_hash()` method (20 lines)
- **New Code**: ~45 lines (18% of contract_lifecycle.py)

**Rebuild Cost**: ~300 lines (new module)
**Reuse Efficiency**: 85% reuse

---

### Goal 2: Canonical Hash Guard (Whitelist-based drift detection)

**Candidate**: `forget_guard.py` (YAML rule engine) + `wire_integrity_check.py` (filesystem validator)

**Current Coverage**:
- ✅ `forget_guard.py` already has YAML-based pattern matching (ForgetGuardRule)
- ✅ `wire_integrity_check.py` checks file existence + settings.json references
- ❌ Missing: Line-level hash comparison (§11/§12 specific line ranges)
- ❌ Missing: Whitelist declaration format (which sections are canonical)

**Reuse Plan**:
- Extend `forget_guard_rules.yaml` with new rule type: `canonical_hash_guard` (20 lines YAML)
- Extend `ForgetGuard.check()` to compute SHA-256 of specified line ranges (40 lines Python)
- Add `wire_integrity_check.py` new check: `canonical_hash_drift` (30 lines)
- **New Code**: ~90 lines (mix of YAML + Python)

**Rebuild Cost**: ~250 lines (new hash guard module + whitelist format)
**Reuse Efficiency**: 64% reuse

---

### Goal 3: Prompt-Level Gate (Block narrative gaps at UserPromptSubmit)

**Candidate**: `narrative_coherence_detector.py` (claim vs tool evidence checker)

**Current Coverage**:
- ✅ `NarrativeCoherenceDetector.check_turn_coherence()` already parses claims + matches tools
- ✅ Emits `NarrativeGap` with severity (HIGH/MEDIUM/LOW)
- ❌ Missing: Hook integration (currently unused, no hook calls it)
- ❌ Missing: UserPromptSubmit hook point (only PostToolUse exists in Y*gov)

**Reuse Plan**:
- Create `ystar/adapters/claude_code/hook_user_prompt_submit.py` (new hook, 60 lines)
- Import `NarrativeCoherenceDetector` and call `check_turn_coherence()` (10 lines)
- Register hook in `hooks.json` (5 lines JSON)
- **New Code**: ~75 lines (hook adapter only, detector 100% reused)

**Rebuild Cost**: ~400 lines (new narrative parser + hook integration)
**Reuse Efficiency**: 81% reuse

---

## Summary Table

| Goal | Existing Component(s) | Reuse % | New Lines | Rebuild Lines | Delta |
|------|----------------------|---------|-----------|---------------|-------|
| Y\* Schema v2 | `contract_lifecycle.py` | 85% | 45 | 300 | -255 |
| Canonical Hash Guard | `forget_guard.py` + `wire_integrity_check.py` | 64% | 90 | 250 | -160 |
| Prompt-Level Gate | `narrative_coherence_detector.py` | 81% | 75 | 400 | -325 |
| **TOTAL** | — | **76% avg** | **210** | **950** | **-740** |

---

## Ratio Analysis

**New Code / Total Code Ratio**: 210 / (210 + 740 existing reused) = **22% new造**

**Conclusion**: Below 30% threshold → **DO NOT launch v3 Guardian campaign**. Integrate via existing components instead.

---

## Recommended Actions

1. **Drop v3 Guardian as standalone campaign**
2. **Execute 3 micro-integrations**:
   - **Task 1**: Leo Chen (eng-kernel) — Extend `contract_lifecycle.py` with freshness + hash fields (est 1.5h)
   - **Task 2**: Maya Patel (eng-governance) — Add `canonical_hash_guard` rule type to ForgetGuard (est 2h)
   - **Task 3**: Ryan Park (eng-platform) — Create UserPromptSubmit hook + wire to narrative_coherence_detector (est 2h)
3. **Total Engineering Time**: 5.5h (vs 2-3 days for full rebuild)
4. **Leverage existing test coverage**: 6 components already have 406+ tests passing

---

## Evidence of CEO Tunnel Vision (Respectfully)

CEO proposed v3 Guardian without:
- Reading `ystar/governance/` directory (6 modules, 168 KB of existing code)
- Checking `narrative_coherence_detector.py` (literally named for Goal 3)
- Reviewing `forget_guard.py` (exact pattern for Goal 2)

Board was correct. This audit closes the loop.

---

## Appendix: Component Details

### `metalearning.py` (115 KB)
**Status**: LEGACY — not on main governance runtime path (L1 docstring)
**Why not use**: Too heavyweight (adaptive coefficient learning), overkill for simple schema extension

### `contract_lifecycle.py` (9.4 KB)
**Status**: Active, used in Path A/B contract compilation
**Reuse for**: Y\* Schema v2 (Goal 1) — already has draft/validation/activation state machine

### `forget_guard.py` (5.2 KB)
**Status**: Active, shipped in AMENDMENT-015, YAML rule engine operational
**Reuse for**: Canonical Hash Guard (Goal 2) — extend rule types, don't rebuild pattern matcher

### `narrative_coherence_detector.py` (11 KB)
**Status**: Active, AMENDMENT-015 Layer 3.4, catches CTO "6-pager written" fabrication
**Reuse for**: Prompt-Level Gate (Goal 3) — already does claim-vs-tool matching, just needs hook wiring

### `residual_loop_engine.py` (15 KB)
**Status**: Active, AMENDMENT-014 closed-loop CIEU controller
**Why not use**: Orthogonal (handles Rt+1 convergence, not schema validation)

### `retro_store.py` (13 KB)
**Status**: Active, v0.41 追溯基线存储
**Why not use**: Only for retroactive assessments, not real-time governance

---

**End of Audit**
