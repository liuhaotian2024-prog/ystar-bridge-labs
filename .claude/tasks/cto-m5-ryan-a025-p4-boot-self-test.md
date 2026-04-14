## Mission 5: A025 P4 — Boot Self-Test for ForgetGuard
Engineer: eng-platform (Ryan Park)
Priority: P1
L-label: L4 (Infrastructure - boot reliability gate)

Gap: governance_boot.sh doesn't test self-heal enforcement — can boot with broken rules.

Acceptance Criteria:
- [ ] Add STEP 8.5 to `scripts/governance_boot.sh`
- [ ] Run mock self-heal command set: e.g., `echo "test" > /tmp/restricted_path_test.txt`
- [ ] Verify any DENY from ForgetGuard → boot FAIL with clear message
- [ ] If pass, continue boot
- [ ] Test with intentional violation, verify boot stops
- [ ] Commit, report hash + L4 label

Files in scope: scripts/governance_boot.sh
