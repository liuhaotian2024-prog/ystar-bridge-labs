## Mission 1: L5 ForgetGuard Rule Activation
Engineer: eng-governance (Maya Patel)
Priority: P0
L-label: L5 (Leadership Loop - meta-governance self-improvement)

Gap: `must_dispatch_via_cto` rule NOT_ENFORCING — CEO can still direct-dispatch engineers bypassing CTO.

Acceptance Criteria:
- [ ] Add `ceo_direct_engineer_dispatch` deny rule to `ystar/governance/forget_guard_rules.yaml`
- [ ] Rule trigger: Edit/Write to .claude/tasks/eng-* by agent_id=ceo
- [ ] deny_mode with clear violation message referencing AMENDMENT-025 L5 constraint
- [ ] governance_boot.sh STEP 8.5 self-test: mock CEO write to .claude/tasks/eng-kernel-test.md, verify DENY
- [ ] Test passes, commit, report commit hash + L5 label

Files in scope: ystar/governance/forget_guard_rules.yaml, scripts/governance_boot.sh
