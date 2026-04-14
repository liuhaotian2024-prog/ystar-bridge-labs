## Task: A025-P1 — Flip invariant Default to Fail-Open

**Engineer:** eng-kernel (Leo Chen)  
**Priority:** P1  
**Estimated Time:** 30 min  
**Amendment:** AMENDMENT-025 (CROBA Framework)

---

## Context

Current `nl_to_contract.py` defaults `invariant` field to **fail-closed** (strict enforcement even when not explicitly requested). This caused Maya's governance rule to hard-deny before dry-run period, blocking legitimate self-heal operations.

**Root Cause:** Implicit `strict: true` when agent writes invariant without explicit relaxation flag.

---

## Task

Modify `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/nl_to_contract.py`:

1. **Locate invariant parsing logic** (search for `invariant` field handling)
2. **Change default behavior:**
   - Old: `invariant` implies `strict: true` (fail-closed)
   - New: `invariant` implies `strict: false` (fail-open) unless explicitly `strict: true` in rule text
3. **Add schema validation:** Reject contracts with `invariant` but ambiguous strictness (require explicit `strict: true/false`)

---

## Acceptance Criteria

- [ ] `invariant` rules default to `strict: false` (warnings only)
- [ ] Explicit `strict: true` in rule text → hard enforcement
- [ ] Schema validation rejects ambiguous invariants (neither strict=true nor strict=false)
- [ ] All 86+ Y*gov tests pass (run `python -m pytest` in Y-star-gov/)
- [ ] No files outside `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/` modified

---

## Files in Scope

- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/nl_to_contract.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/` (read-only, for validation)

---

## Handoff

After completion:
1. Run `python -m pytest --tb=short -q` in Y-star-gov workspace
2. Report to CTO: "A025-P1 complete, {N} tests pass, invariant default flipped to fail-open"
3. Do NOT commit — CTO handles unified commit for all 4 tasks
