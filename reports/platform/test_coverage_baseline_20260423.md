# Y*gov Test Coverage Baseline — 2026-04-23

**Measured by**: eng-platform (Ryan Park)
**Method**: `pytest --cov=ystar --cov-report=term-missing` on commit 92b113e
**Result**: 1775 passed, 99 failed, 16 skipped (178s runtime)

## Overall Coverage

| Metric | Value |
|--------|-------|
| Total statements | 29,954 |
| Covered statements | 15,916 |
| Missed statements | 14,038 |
| **Overall line coverage** | **53%** |
| Target | 80% |
| Gap | 27 percentage points (~8,000 lines to cover) |

## Top 3 Coverage Gaps (Biggest Bang for Buck)

Ranked by `missed_lines * (1 - coverage%)` — prioritizing large files with low coverage.

| Rank | File | Stmts | Miss | Cover | Impact |
|------|------|-------|------|-------|--------|
| 1 | `ystar/governance/metalearning.py` | 1,011 | 741 | 27% | Largest single file, 741 uncovered lines. Tests for ML metalearning loop would add ~2.5% to overall coverage alone. |
| 2 | `ystar/kernel/prefill.py` | 662 | 460 | 31% | Second largest gap. Prefill logic has 460 uncovered lines. High LOC, low coverage. |
| 3 | `ystar/kernel/dimensions.py` | 1,018 | 432 | 58% | Biggest file in kernel. Despite 58% coverage, 432 missed lines is the third highest absolute count. |

**Honorable mentions** (0% coverage, moderate LOC):
- `ystar/governance/k9_adapter/compliance_audit.py` — 200 lines, 0%
- `ystar/governance/ml/objectives.py` — 497 lines, 0%
- `ystar/adapters/connector.py` — 291 lines, 3%
- `ystar/check_service.py` — 233 lines, 0%
- `ystar/capabilities.py` — 151 lines, 0%

## Coverage by Module

| Module | Stmts | Miss | Approx Cover |
|--------|-------|------|-------------|
| ystar/adapters/ | 3,783 | 1,433 | 62% |
| ystar/governance/ | 10,638 | 5,080 | 52% |
| ystar/kernel/ | 3,135 | 1,324 | 58% |
| ystar/domains/ | 1,992 | 1,172 | 41% |
| ystar/cli/ | 1,696 | 1,188 | 30% |
| ystar/memory/ | 332 | 63 | 81% |
| ystar/rules/ | 338 | 33 | 90% |
| ystar/products/ | 647 | 472 | 27% |
| ystar/path_a+b/ | 1,152 | 259 | 78% |
| ystar/ (root files) | 1,241 | 1,014 | 18% |

## Estimated Effort to Reach 80%

To go from 53% to 80%, we need to cover ~8,000 additional lines.
At ~0.5 test lines per source line covered (conservative), that is ~4,000 lines of test code.
At ~20 lines per tool_use (empirical average for test writing), that is **~200 tool_uses** across multiple sessions.

**Recommended attack order** (maximize coverage delta per session):
1. **metalearning.py** (741 lines, +2.5% overall) — mostly ML loop, testable with mocks
2. **prefill.py** (460 lines, +1.5%) — kernel prefill, needs kernel fixtures
3. **connector.py + check_service.py + capabilities.py** (674 lines combined, +2.2%) — adapter/CLI scope, directly in eng-platform territory
4. **cli/*.py** (1,188 uncovered, +4.0%) — CLI commands, high testability
5. **governance/ml/** (778 lines at 0%, +2.6%) — ML subsystem entirely untested

## Blockers

- **99 test failures**: Existing test suite has 99 failures (5.3% failure rate). Many are in governance/ and adapters/ — likely due to recent refactors breaking assertions. These should be fixed before writing new coverage tests, otherwise new tests may mask regressions.
- **dev_cli.py parse error**: `ystar/dev_cli.py` has a syntax error (f-string unmatched paren at line 500) — coverage tool cannot parse it. This file is excluded from the report.
- **No pytest-cov in default env**: Had to install pytest-cov manually. CI should pin it.

## CIEU Event

Event: `WAVE_Y001_2_COVERAGE_BASELINE`
Decision: `auto_approve`
Params: `{"overall_coverage_pct": 53, "top_gaps": ["governance/metalearning.py:27%", "kernel/prefill.py:31%", "kernel/dimensions.py:58%"], "blocked": false, "test_failures": 99, "total_stmts": 29954, "missed_stmts": 14038}`
