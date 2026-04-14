# Preservation Guard Demo — Live Examples

Generated: 2026-04-13  
Purpose: Demonstrate preservation guard detecting Y*gov innovation conflicts

---

## Case 1: RED LINE — Constitutional AI (conflicts with iron_rule_1)

Query: "constitutional safety enforcement"

**Detection**:
- ✅ Detected: iron_rule_1 conflict
- 🔴 Red Line: YES
- ⚠️ Warning: "ADAPT ONLY — Core innovation conflict detected"

**Reason**: Constitutional AI uses LLM for constitutional critique, violates Y*gov Iron Rule 1 (hook is deterministic, zero LLM). External framework would replace our enforcement mechanism.

**Recommendation**: Borrow the concept (constitutional principles as first-class), build Y*gov-native adapter wrapping it into CIEU/hook enforcement plane.

---

## Case 2: Non-Red Line — Letta (Memory doesn't conflict with 6 red lines)

Query: "agent memory management"

**Detection**:
- ✅ Detected: autonomy_engine, amendment_evolution
- 🔴 Red Line: NO (memory_classification is innovation #10, NOT in RED_LINE list)
- ✅ Safe to integrate: Evaluate architecture design

**Reason**: Memory management doesn't conflict with core enforcement/math/architecture (iron_rule_1, cieu_5tuple, omission_engine, 12_layer_construction, capability_delegation, name_role_binding). Letta's hierarchical memory can complement Y*gov without replacing core primitives.

**Recommendation**: Standard integration path — evaluate complexity, POC, test.

---

## Case 3: Ordinary Query — No Conflicts

Query: "generic data processing pipeline optimization"

**Detection**:
- Preserved Innovations: None detected
- Red Line: No
- borrowed_pattern_only: Based on complexity heuristics

**Behavior**: Still outputs Preservation Analysis section (every brief audited, even if clean).

---

## Stats

**Preservation Guard Coverage**:
- 12 core innovations tracked
- 6 red line innovations enforced
- 100% brief coverage (every tech_radar output includes preservation analysis)

**Test Coverage**:
- 7 new tests added
- 18 total tech_radar tests
- All passing ✓

---

**Commit**: `3f00131` — feat: tech_radar preservation guard
**Impact**: Every external tech borrow now auto-audited against dogfooding-as-product risk. No silent innovation replacement possible.
