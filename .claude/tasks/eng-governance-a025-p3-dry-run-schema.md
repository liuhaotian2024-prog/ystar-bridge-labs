## Task: A025-P3 — Dry-Run Schema for New Governance Rules

**Engineer:** eng-governance (Maya Patel)  
**Priority:** P3  
**Estimated Time:** 30 min  
**Amendment:** AMENDMENT-025 (CROBA Framework)

---

## Context

New governance rules immediately enforce hard denies, causing production incidents when rules have bugs (your `forget_guard_rules.yaml` edit blocked CEO's legitimate governance_boot.sh run).

**Required Behavior:** New rules must specify `dry_run_until: <ISO timestamp>`, enforcing warnings-only for 24h grace period before hardening to deny.

---

## Task

### Part A: Schema Update
Modify `/Users/haotianliu/.openclaw/workspace/ystar-company/governance/forget_guard_rules.yaml`:

1. **Add schema documentation header:**
   ```yaml
   # Forget Guard Rules Schema (A025-P3)
   # Required fields:
   #   - pattern: regex pattern to match command
   #   - action: deny | warn
   #   - message: human-readable explanation
   #   - dry_run_until: ISO8601 UTC timestamp (required for new rules)
   #
   # Dry-run behavior:
   #   - If current_time < dry_run_until: action forced to "warn"
   #   - If current_time >= dry_run_until: action enforced as specified
   #
   # Example:
   #   - pattern: "rm -rf governance/"
   #     action: deny
   #     message: "Cannot delete governance directory"
   #     dry_run_until: "2026-04-14T12:00:00Z"
   ```

2. **Add `dry_run_until` to all existing rules** (set to past timestamp like `"2026-01-01T00:00:00Z"` so they're already hardened)

### Part B: Enforcement Logic
Modify `/Users/haotianliu/.openclaw/workspace/ystar-company/governance/forget_guard.py`:

1. **Validate schema on load:**
   ```python
   from datetime import datetime
   
   def validate_rule(rule):
       required = ['pattern', 'action', 'message', 'dry_run_until']
       for field in required:
           if field not in rule:
               raise ValueError(f"Rule missing required field: {field}")
       
       # Validate ISO8601 format
       try:
           datetime.fromisoformat(rule['dry_run_until'].replace('Z', '+00:00'))
       except ValueError:
           raise ValueError(f"dry_run_until must be ISO8601 UTC: {rule['dry_run_until']}")
   ```

2. **Honor dry-run window during enforcement:**
   ```python
   def enforce_rule(rule, command):
       now = datetime.now(timezone.utc)
       dry_run_end = datetime.fromisoformat(rule['dry_run_until'].replace('Z', '+00:00'))
       
       if now < dry_run_end:
           # Still in dry-run window, force warn
           return {"action": "warn", "message": f"[DRY-RUN] {rule['message']}"}
       else:
           # Dry-run ended, enforce as specified
           return {"action": rule['action'], "message": rule['message']}
   ```

---

## Acceptance Criteria

- [ ] All rules in `forget_guard_rules.yaml` have valid `dry_run_until` field
- [ ] `forget_guard.py` validates schema on load, raises error if missing field
- [ ] New rule with `dry_run_until` in future → warns instead of denies
- [ ] New rule with `dry_run_until` in past → enforces deny immediately
- [ ] New rule without `dry_run_until` → schema validation fails (boot gate catches this)
- [ ] No files outside `/Users/haotianliu/.openclaw/workspace/ystar-company/governance/` modified

---

## Files in Scope

- `/Users/haotianliu/.openclaw/workspace/ystar-company/governance/forget_guard_rules.yaml`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/governance/forget_guard.py`

---

## Handoff

After completion:
1. Add a test rule with `dry_run_until` 1 hour in future, verify warns
2. Add a test rule without `dry_run_until`, verify schema error
3. Report to CTO: "A025-P3 complete, dry-run schema validated, {N} existing rules updated"
4. Do NOT commit — CTO handles unified commit
