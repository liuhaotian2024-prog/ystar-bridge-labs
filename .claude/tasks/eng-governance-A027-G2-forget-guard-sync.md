## Task: A027-G2 — forget_guard.py real-time rule sync

Engineer: eng-governance
Priority: P0 (AMENDMENT-027 blocking)
Context: Gap G2 — sub-agent sees stale forget_guard_rules.yaml (boot snapshot only)

**Acceptance Criteria:**
- [ ] Expand `ystar/governance/forget_guard.py` — every rule evaluate reads current rules from watcher memory (not boot snapshot)
- [ ] Sub-agent payload includes "rule_version_seen" field
- [ ] Version mismatch triggers STALE_CONTEXT event
- [ ] Existing forget_guard tests still pass
- [ ] New test: edit forget_guard_rules.yaml during sub-agent run → next tool call detects stale + refreshes

**Files in scope:**
- ystar/governance/forget_guard.py (expand)
- ystar/governance/governance_watcher.py (read-only — Ryan will expand broadcast in next step)
- tests/test_forget_guard.py (expand)

**Deliverable:**
- Working code + passing tests
- Commit hash
- One-line: "G2 PASS/FAIL + test count"

**Hard constraint:**
- No bash background spawn
- Return full response when done (CTO will wait)
