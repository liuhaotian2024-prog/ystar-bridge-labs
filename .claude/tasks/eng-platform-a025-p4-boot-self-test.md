## Task: A025-P4 — Boot Self-Test for Governance Rules

**Engineer:** eng-platform (Ryan Park)  
**Priority:** P4  
**Estimated Time:** 30 min  
**Amendment:** AMENDMENT-025 (CROBA Framework)

---

## Context

`governance_boot.sh` loads all governance rules but never tests if they actually work. This allowed broken rules (missing `dry_run_until`, invalid regex) to pass boot and cause runtime denies.

**Required Behavior:** After loading rules, boot script must run a self-test suite simulating self-heal commands. Any deny on whitelisted commands → boot FAIL.

---

## Task

Modify `/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/governance_boot.sh`:

1. **Add STEP 8.5 between "Load rules" and "Final health check":**
   ```bash
   echo "━━━ STEP 8.5: Self-Test Governance Rules ━━━"
   
   # Test 1: Self-heal commands must always allow
   test_commands=(
       "pkill -9 -f hook_daemon"
       "rm /tmp/ystar_hook.sock"
       "bash scripts/governance_boot.sh cto"
       "echo ceo > .ystar_active_agent"
   )
   
   for cmd in "${test_commands[@]}"; do
       result=$(echo "$cmd" | bash scripts/hook_client_labs.sh)
       action=$(echo "$result" | jq -r '.action')
       if [[ "$action" != "allow" ]]; then
           echo "❌ BOOT FAILURE: Self-heal command blocked: $cmd"
           echo "   Hook response: $result"
           exit 1
       fi
   done
   
   # Test 2: Governance rule schema validation
   python3 - <<EOF
   import yaml
   from datetime import datetime
   
   with open('governance/forget_guard_rules.yaml') as f:
       rules = yaml.safe_load(f)['rules']
   
   for rule in rules:
       # Validate required fields
       required = ['pattern', 'action', 'message', 'dry_run_until']
       for field in required:
           if field not in rule:
               print(f"❌ BOOT FAILURE: Rule missing field '{field}': {rule}")
               exit(1)
       
       # Validate ISO8601 format
       try:
           datetime.fromisoformat(rule['dry_run_until'].replace('Z', '+00:00'))
       except ValueError:
           print(f"❌ BOOT FAILURE: Invalid dry_run_until format: {rule['dry_run_until']}")
           exit(1)
   
   print("✅ All governance rules valid")
   EOF
   
   echo "✅ Self-test passed: {N} commands allowed, schema valid"
   ```

2. **Update final "ALL SYSTEMS GO" condition:**
   - Only print "ALL SYSTEMS GO" if all steps 1-8.5 pass
   - If STEP 8.5 fails, print "BOOT FAILED: governance self-test" and exit 1

---

## Acceptance Criteria

- [ ] Boot runs self-test suite after loading rules
- [ ] Self-heal commands tested → all allow
- [ ] Governance rules schema validated → all valid
- [ ] Any failure in self-test → boot exits with code 1 (not "ALL SYSTEMS GO")
- [ ] Self-test output shows number of commands tested
- [ ] No files outside `/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/` modified

---

## Files in Scope

- `/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/governance_boot.sh`

---

## Handoff

After completion:
1. Run `bash scripts/governance_boot.sh cto` and verify STEP 8.5 output
2. Temporarily break a rule (remove `dry_run_until`), verify boot fails
3. Restore rule, verify boot succeeds
4. Report to CTO: "A025-P4 complete, boot self-test added, tested {N} scenarios"
5. Do NOT commit — CTO handles unified commit
