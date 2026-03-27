# Y* Bridge Labs — Case Index

Cases are the company's most valuable long-term asset. Every significant failure and learning is documented here.

| Case | Agent | Date | Summary |
|------|-------|------|---------|
| [CASE-001](CASE_001_CMO_fabrication.md) | CMO | 2026-03-26 | Fabricated CIEU audit record in blog post — semantic-layer violation |
| [CASE-002](CASE_002_CFO_fabrication.md) | CFO | 2026-03-26 | Fabricated cost figures without real token data — same pattern as CASE-001 |

## Pattern: Confident Fabrication
Both cases share the same root cause: AI agents generate plausible-sounding content when data is missing, because fabrication is the most "helpful-seeming" response. This is a systematic risk, not an edge case.

## How to Add a New Case
1. Create `CASE_XXX_[agent]_[brief_description].md`
2. Follow the standard structure (task, decision, framework, outcome, lessons)
3. Update this index
4. This is mandatory for all significant failures
