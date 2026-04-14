## Task: A025-P2 — Self-Heal Whitelist Bypass in Hook

**Engineer:** eng-platform (Ryan Park)  
**Priority:** P2  
**Estimated Time:** 30 min  
**Amendment:** AMENDMENT-025 (CROBA Framework)

---

## Context

Hook currently blocks `pkill -9 -f hook_daemon` and `rm /tmp/ystar_hook.sock`, preventing agents from self-healing stuck governance daemons. CEO had to manually intervene 3 times in last session.

**Required Behavior:** Self-heal commands must **always allow**, bypassing all hook layers.

---

## Task

Modify `/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_client_labs.sh`:

1. **Add whitelist logic at top of script** (before any other checks):
   ```bash
   # Self-heal whitelist bypass (A025-P2)
   case "$PAYLOAD" in
     *"pkill"*"hook_daemon"*|\
     *"rm "*"/tmp/ystar_hook.sock"*|\
     *"governance_boot.sh"*|\
     *".ystar_active_agent"*)
       echo '{"action":"allow","message":"self-heal bypass"}'; exit 0;;
   esac
   ```

2. **Test patterns:**
   - `pkill -9 -f hook_daemon` → allow
   - `pkill -9 python3` → block (not hook-related)
   - `rm /tmp/ystar_hook.sock` → allow
   - `rm /tmp/other.sock` → normal hook evaluation
   - `bash scripts/governance_boot.sh cto` → allow
   - `echo "ceo" > .ystar_active_agent` → allow

---

## Acceptance Criteria

- [ ] Self-heal commands match whitelist → instant allow (no further hook evaluation)
- [ ] Non-self-heal commands → normal hook flow
- [ ] Whitelist uses exact pattern matching (no wildcards that could create bypass holes)
- [ ] Hook script syntax valid (run `bash -n scripts/hook_client_labs.sh`)
- [ ] No files outside `/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/` modified

---

## Files in Scope

- `/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_client_labs.sh`

---

## Handoff

After completion:
1. Test whitelist manually: `echo 'pkill -9 -f hook_daemon' | bash scripts/hook_client_labs.sh`
2. Verify output: `{"action":"allow","message":"self-heal bypass"}`
3. Report to CTO: "A025-P2 complete, self-heal whitelist active, tested {N} patterns"
4. Do NOT commit — CTO handles unified commit
