# CIEU Liveness Check — Execution Guide

**Source:** AGENTS.md CIEU Liveness Check章节（Constitutional Rule）  
**Moved to knowledge:** 2026-04-03（Constitutional cleanup）  
**Authority:** Board Directive #024

---

## Purpose

Verify that CIEU (Causal-Intent-Evidence-Upstream) governance engine is actively recording events. A dead CIEU = blind governance = P0 incident.

## When to Execute

**Trigger:** Every agent session start, within 60 seconds

**Constitutional requirement:** See AGENTS.md "CIEU Liveness Check"  
**Modern tool:** `ystar doctor --layer1` (preferred method, automated)

---

## Manual Execution Steps (Legacy)

If `ystar doctor --layer1` is not available:

### Step 1: Query baseline count
```bash
sqlite3 .ystar_cieu.db "SELECT COUNT(*) FROM cieu_events;"
```
Record the count (e.g., 1234).

### Step 2: Perform governed action
Execute any Y*gov-governed operation:
```bash
# Example: read a file (triggers CIEU event)
cat AGENTS.md > /dev/null
```

### Step 3: Query new count
```bash
sqlite3 .ystar_cieu.db "SELECT COUNT(*) FROM cieu_events;"
```
New count must be ≥ baseline + 1.

### Step 4: Verify or escalate
**If count increased:** ✅ CIEU is alive, proceed with session  
**If count did NOT increase:** ❌ CIEU is dead, P0 incident

---

## P0 Response Protocol

**If CIEU is dead:**

1. **STOP all operations immediately**
   - Do NOT proceed with any work
   - Report to CEO: "CIEU liveness check FAILED"

2. **Diagnostic steps**
   - Check if `.ystar_cieu.db` exists and is writable
   - Check if Y*gov hook is installed: `ystar doctor --layer1`
   - Check `settings.json` for hook configuration
   - Check recent CIEU events: `sqlite3 .ystar_cieu.db "SELECT * FROM cieu_events ORDER BY created_at DESC LIMIT 5;"`

3. **Attempted remediation** (only if authorized by Board)
   - Restart Claude Code session
   - Re-run `ystar hook-install`
   - Verify hook is active: check for `<user-prompt-submit-hook>` messages

4. **Escalation**
   - If remediation fails, escalate to Board
   - Include: diagnostic output, last known good CIEU event timestamp, error messages
   - Wait for Board authorization before proceeding

---

## Modern Automated Method (Preferred)

**Command:**
```bash
ystar doctor --layer1
```

**Expected output:**
```
[✓] CIEU Database — .ystar_cieu.db (3856 events)
```

**Failure indicators:**
- `[✗] CIEU Database — not found`
- `[✗] CIEU Database — no recent events (>1 hour stale)`
- Exit code 1

**On failure:** Follow P0 Response Protocol above.

---

## Success Criteria

- ✅ CIEU event count increases after governed action
- ✅ `.ystar_cieu.db` is accessible and writable
- ✅ Recent events visible in database (within last hour)
- ✅ `ystar doctor --layer1` passes CIEU check

---

## Why This Matters

CIEU is the audit trail for all governance decisions. Without CIEU:
- No proof of what Y*gov allowed/denied
- No causal chain for debugging violations
- No evidence for compliance audit
- Governance system is effectively offline

**A dead CIEU is equivalent to operating ungoverned.**

---

**Last updated:** 2026-04-03  
**Next review:** When `ystar doctor` architecture changes
