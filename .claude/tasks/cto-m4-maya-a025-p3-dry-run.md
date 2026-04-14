## Mission 4: A025 P3 — dry_run_until Field
Engineer: eng-governance (Maya Patel)
Priority: P1
L-label: L3 (Governance Specification - safe rule rollout)

Gap: No dry_run_until field for ForgetGuard rules — new rules can't be tested in production without risk.

Acceptance Criteria:
- [ ] Extend `ystar/governance/forget_guard_rules.yaml` schema: add `dry_run_until: "YYYY-MM-DD"` field
- [ ] Edit `ystar/governance/forget_guard.py`: honor dry_run_until — log violation but ALLOW action
- [ ] Add example rule with dry_run_until set to 2026-04-20
- [ ] Test: trigger rule, verify ALLOW + log entry
- [ ] Commit, report hash + L3 label

Files in scope: ystar/governance/forget_guard_rules.yaml, ystar/governance/forget_guard.py
