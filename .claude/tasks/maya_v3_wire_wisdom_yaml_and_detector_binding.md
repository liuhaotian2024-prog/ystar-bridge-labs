---
title: "V3 Maya: Wire Wisdom→YAML + Detector 7-Philosophy/M-Triangle Binding"
engineer: eng-governance (Maya Patel)
priority: P0
atomic_id: CZL-CEO-RULES-REGISTRY-V3-MAYA
parent: CZL-CEO-RULES-REGISTRY-V3-EXISTING-ASSETS-FIRST
date: 2026-04-22
estimated_tu: 55
m_triangle: M-2a commission + M-2b omission (closing G3+G4 gaps)
---

## BOOT 4-step (MANDATORY — run before any business tool)

```bash
cat /Users/haotianliu/.openclaw/workspace/ystar-company/.czl_subgoals.json
cd /Users/haotianliu/.openclaw/workspace/ystar-company && git log -10 --oneline
python3 scripts/precheck_existing.py "CZL-CEO-RULES-REGISTRY-V3-MAYA" 2>&1 | tail -10
sqlite3 .ystar_cieu.db "SELECT count(*) FROM cieu_events WHERE created_at >= strftime('%s','now','-1 hour')"
```

## Context (self-contained — no session history required)

CEO spec: `reports/ceo/governance/CEO_RULES_REGISTRY_AUDIT.md` Section 10.3 (G3) + Section 10.4 (G4).

Board 2026-04-22 directive: close 4 governance gaps. This card covers G3 (memory→yaml automation) + G4 (philosophy/M-Triangle specific detector binding).

### Existing Assets (DO NOT rebuild — wire and extend)

1. **`scripts/session_wisdom_extractor_v2.py`** (25KB, Maya EXP-6 red-team revised): 11-source scan, time/board/role weighted, outputs `memory/wisdom_package_*.md`. Already covers NL→structured extraction.
2. **`Y-star-gov/ystar/governance/narrative_coherence_detector.py`** (19KB, AMENDMENT-015 Layer 3.4): Catches "file written" without Write tool, "tests pass" without pytest. Claim vs tool evidence gap detection.
3. **`Y-star-gov/ystar/governance/observable_action_detector.py`** (7KB, AMENDMENT-015 Layer 3.1): Replaces ritual phrase compliance with observable evidence (git commit/file write/test pass). Eliminated 72.3% false positives.
4. **`governance/forget_guard_rules.yaml`**: Current 22 yaml commission rules (46 unique at runtime with built-ins).

### What Does NOT Exist Yet (your delta)

- `governance/proposed_rules/` directory (create it)
- Wiring from wisdom_extractor output → yaml candidate entries
- 7-philosophy (P-1 through P-7) specific binding in narrative_coherence_detector
- M-Triangle three-question (pushes which face / weakens which face / balanced?) specific binding in observable_action_detector

## Task 1: Wire wisdom_extractor → proposed yaml entries (G3, ~30 tu)

### Goal
When `session_wisdom_extractor_v2.py` runs, its output (`memory/wisdom_package_*.md`) should additionally produce candidate yaml entries in `governance/proposed_rules/` directory, formatted to match `forget_guard_rules.yaml` schema.

### Steps

1. Read `scripts/session_wisdom_extractor_v2.py` fully — understand its output format
2. Read `governance/forget_guard_rules.yaml` fully — understand the yaml schema (each rule has: name, trigger_patterns, action, severity, description, etc.)
3. Create `governance/proposed_rules/` directory
4. Write `scripts/wisdom_to_yaml_proposer.py`:
   - Input: path to a wisdom_package_*.md or memory/feedback_*.md file
   - Output: writes a candidate yaml file to `governance/proposed_rules/{source_name}_proposed.yaml`
   - Each candidate entry must include:
     - `name`: derived from feedback filename
     - `trigger_patterns`: extracted behavioral patterns from the feedback text
     - `action`: `deny` for commission, `warn` for advisory
     - `severity`: P0/P1/P2 based on content analysis
     - `description`: one-line summary
     - `source`: original feedback filename
     - `status`: `proposed` (not `active` — CTO must review before activation)
   - Use Claude-style NL parsing (regex + heuristic, not LLM call) to extract actionable patterns
   - Handle edge cases: feedback files that are diagnostic memos (not behavioral rules) should produce `action: info` entries
5. Test: run proposer on 3 existing feedback files that have ENFORCED status (e.g., `feedback_address_laoda.md`, `feedback_ai_disclosure_mandatory.md`, `feedback_board_shell_marker.md`) and verify proposed yaml matches existing rules in forget_guard_rules.yaml
6. Test: run proposer on 3 GAP feedback files and verify proposed yaml is reasonable

### Acceptance Criteria
- [ ] `governance/proposed_rules/` directory exists
- [ ] `scripts/wisdom_to_yaml_proposer.py` exists and runs without error
- [ ] Running proposer on `feedback_address_laoda.md` produces yaml with trigger patterns matching "Board" without "老大"
- [ ] Running proposer on a diagnostic memo (e.g., `feedback_team_enforce_asymmetry.md`) produces `action: info` not `deny`

## Task 2: Detector 7-philosophy + M-Triangle binding (G4, ~25 tu)

### Goal
Add specific bindings to `narrative_coherence_detector.py` and `observable_action_detector.py` so they can detect claims about philosophy/methodology compliance without evidence.

### Context on 7-Philosophy + M-Triangle

The 7 philosophies (P-1 through P-7) are from `knowledge/ceo/wisdom/WORK_METHODOLOGY.md`:
- P-1: Align to M Triangle
- P-2: Three-question check (pushes which M face / weakens which / balanced?)
- P-3: Counterfactual reasoning
- P-4: Real testing > hand-wave
- P-5: Implicit PASS/FAIL counts as data
- P-6: Independent reproduction + cross-validation (double-blind)
- P-7: Goal transmission chain complete (M → mid → U → action → result)

The M-Triangle three questions:
1. Which M face does this push? (M-1 Survivability / M-2 Governability / M-3 Value Production)
2. Which M face does this weaken?
3. Is the triangle balanced?

### Steps

1. Read `Y-star-gov/ystar/governance/narrative_coherence_detector.py` fully
2. Read `Y-star-gov/ystar/governance/observable_action_detector.py` fully
3. In `narrative_coherence_detector.py`, add a new detection category `PHILOSOPHY_CLAIM_WITHOUT_EVIDENCE`:
   - Trigger: reply contains phrases like "I checked P-3" / "passed counterfactual" / "M-Triangle balanced" / "三问通过" WITHOUT corresponding tool evidence (e.g., a search/grep tool call, a test run, a file read that demonstrates the check)
   - Emit: CIEU event type `NARRATIVE_GAP` subtype `PHILOSOPHY_UNVERIFIED_CLAIM`
   - Key patterns to detect:
     - "P-1" through "P-7" mentioned as "done/checked/passed" without tool_use evidence in same reply
     - "三问" / "three questions" / "M-Triangle" claimed as checked without specific face identification
     - "反事实" / "counterfactual" claimed without actual alternative scenario text
4. In `observable_action_detector.py`, add observable evidence mappings for philosophy checks:
   - P-3 counterfactual: must contain "if we had NOT..." or "如果不做..." alternative text
   - P-4 real testing: must contain pytest/bash test execution tool call
   - P-6 cross-validation: must contain at least 2 independent verification tool calls
   - M-Triangle: must explicitly name which M-face(s) affected
5. Test: craft a mock reply that says "I passed P-3 counterfactual check" with zero tool evidence → narrative_coherence_detector must flag it
6. Test: craft a mock reply with actual counterfactual text → narrative_coherence_detector must NOT flag it

### Acceptance Criteria
- [ ] `narrative_coherence_detector.py` has `PHILOSOPHY_CLAIM_WITHOUT_EVIDENCE` detection category
- [ ] `observable_action_detector.py` has P-1~P-7 + M-Triangle observable evidence mappings
- [ ] Livefire test: a reply claiming "I passed P-3 counterfactual" with no tool evidence triggers CIEU `NARRATIVE_GAP` event (delta 0→1)
- [ ] Livefire test: a reply with actual counterfactual reasoning text does NOT trigger false positive

## Livefire Verification (MANDATORY — task is NOT done without this)

Run this exact scenario after both tasks are complete:

```
Scenario: Fabricate a reply "我已通过 P-3 反事实推导" with zero tool evidence.
Expected: narrative_coherence_detector fires NARRATIVE_GAP with subtype PHILOSOPHY_UNVERIFIED_CLAIM.
Verify: sqlite3 .ystar_cieu.db "SELECT count(*) FROM cieu_events WHERE event_type='NARRATIVE_GAP'" shows delta +1 from baseline.
```

If CIEU delta is 0, the binding is NOT live — debug and fix before reporting done.

## 5-Tuple Receipt Template (fill and return to CEO)

```
- Y*: wisdom→yaml proposer LIVE + detector 7-philosophy binding LIVE
- Xt: [describe what you found when you started]
- U: [list exact tool_uses with count]
- Yt+1: [describe actual end state with file paths]
- Rt+1: [honest gap — 0 means truly done, >0 means what remains]
```

## Hard Constraints

- **NO git commit / push / add / reset** — only Write/Edit files, CEO handles git
- **NO choice questions** — pick the best approach, execute, report "I chose X because Y"
- **NO defer language** — no "later/tomorrow/next session/wait"
- **NO self-claims without tool evidence** — narrative_coherence_detector is LIVE and will catch you (this task literally strengthens it, so eat your own dogfood)
- **Files in scope**: `scripts/wisdom_to_yaml_proposer.py` (new), `governance/proposed_rules/` (new dir), `Y-star-gov/ystar/governance/narrative_coherence_detector.py` (extend), `Y-star-gov/ystar/governance/observable_action_detector.py` (extend)
- **Files NOT in scope**: anything outside the above list
