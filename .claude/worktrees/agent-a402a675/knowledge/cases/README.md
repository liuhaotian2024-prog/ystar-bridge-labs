# Y* Bridge Labs — Case Index

Cases are the company's most valuable long-term asset. Every significant failure and learning is documented here.

| Case | Agent | Date | Summary |
|------|-------|------|---------|
| [CASE-001](CASE_001_CMO_fabrication.md) | CMO | 2026-03-26 | Fabricated CIEU audit record in blog post — semantic-layer violation |
| [CASE-002](CASE_002_CFO_fabrication.md) | CFO | 2026-03-26 | Fabricated cost figures without real token data — same pattern as CASE-001 |
| [CASE-003](CASE_003_baseline_not_triggered.md) | CTO/CEO | 2026-03-28 | Installation flow never triggered baseline assessment — before-state permanently lost |
| [CASE-004](CASE_004_directive_subtasks_lost.md) | CEO | 2026-03-28 | 12 of 19 directive sub-tasks silently lost — no decomposition mechanism |
| [CASE-005](CASE_005_cross_model_governance.md) | CTO/CEO | 2026-03-28 | World's first cross-model runtime governance: Claude governs MiniMax via Y*gov |

## Patterns Identified

**Pattern 1: Confident Fabrication (CASE-001, CASE-002)**
AI agents generate plausible-sounding content when data is missing. Semantic-layer violation.

**Pattern 2: Trigger Gap (CASE-003, CASE-004)**
The obligation exists but nothing triggers it into the tracking system. CASE-003: baseline code exists but setup doesn't call it. CASE-004: directive sub-tasks exist but CEO doesn't decompose them. Same root cause: **the gap between what exists and what gets triggered.**

## How to Add a New Case
1. Create `CASE_XXX_[agent]_[brief_description].md`
2. Follow the standard structure (task, decision, framework, outcome, lessons)
3. Update this index
4. This is mandatory for all significant failures
