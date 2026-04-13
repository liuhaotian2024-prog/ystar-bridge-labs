# E1 FIX: governance_boot.sh Auto-Inject agent_id

**Priority:** P0 (3h session lock root cause)
**Assigned:** CTO (Ethan Wright)
**Requested by:** CEO (Aiden) on behalf of Board
**Due:** Immediate

## Root Cause
Y*gov identity_detector reads `.ystar_session.json` field `agent_id` to determine identity. When field is missing → fallback to generic "agent" → hook DENY all operations → session deadlock (proven today, 3h loss).

## Fix Required
In `/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/governance_boot.sh` at STEP 4 (session markers), after creating `.session_booted`, add Python code to inject agent_id into .ystar_session.json:

```python
import json
session_json = '.ystar_session.json'
with open(session_json, 'r') as f:
    d = json.load(f)
d['agent_id'] = '$AGENT_ID'  # shell variable from script arg
d['agent_stack'] = ['$AGENT_ID']
with open(session_json, 'w') as f:
    json.dump(d, f, indent=2)
```

Only run when `VERIFY_ONLY=false` (same condition as `touch .session_booted`).

## Acceptance Criteria
1. Edit governance_boot.sh to add injection logic at STEP 4
2. Run `bash scripts/governance_boot.sh ceo` to verify:
   - No errors during execution
   - .ystar_session.json contains `"agent_id": "ceo"` and `"agent_stack": ["ceo"]`
3. Commit to ystar-company repo with message: `fix(infra): E1 boot script auto-inject agent_id to session.json (3h session lock root cause)`
4. Report back with commit hash + verify session.json content

## Exact Edit Location
Replace lines 136-147 in governance_boot.sh (the "# 4. 创建session标记" block).

New version should:
- Keep existing touch/echo for .session_booted and .session_call_count
- Add python3 inline script to update .ystar_session.json
- Print "[4/7] Session markers + agent_id injection: done" on success
- Exit with error if JSON update fails

## Why CEO Can't Do This
CEO has write boundary restriction - cannot modify scripts/. This is infrastructure work under CTO scope.
