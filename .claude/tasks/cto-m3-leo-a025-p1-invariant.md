## Mission 3: A025 P1 — Invariant Default Fail-Open
Engineer: eng-kernel (Leo Chen)
Priority: P1
L-label: L3 (Governance Specification - safer contract defaults)

Gap: `invariant` constraints default to strict, causing unnecessary friction.

Acceptance Criteria:
- [ ] Edit `Y-star-gov/ystar/kernel/nl_to_contract.py`
- [ ] Change `invariant` parsing: default `optional`, only enforce when `strict: true` explicitly set
- [ ] Add unit test in `Y-star-gov/tests/` verifying default behavior
- [ ] Run full test suite (158 tests must pass)
- [ ] Commit to Y*gov repo, report hash + L3 label

Files in scope: /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/nl_to_contract.py
