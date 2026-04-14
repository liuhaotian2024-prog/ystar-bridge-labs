---
name: Default agent on restart is Aiden (CEO), not engineer
description: When Board says "重启" or starts a new session, the default identity should be ceo (Aiden / 承远). Engineers (Ryan/Leo/Maya/Jordan) and C-suite (Ethan/Sofia/Marco/Zara) only when explicitly named.
type: feedback
originSessionId: 2c3c423c-3fd6-4427-88c8-a1c81c59f73a
---
**Rule**: On `重启` or a fresh session open, run:
```
bash /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/governance_boot.sh ceo
```

If `.ystar_active_agent` marker says something other than `ceo`, the boot script's HOME-RESET block (governance_boot.sh:85-103) will auto-correct it when AGENT_ID=ceo — do not try to overwrite the marker directly (hook blocks non-secretary roles).

**Why**: Board is the single user of this system. They want to talk to the CEO persona (Aiden), not land inside a specific engineer sub-agent session. Today (2026-04-13) the SessionStart hook defaulted to eng-platform because a prior session left the marker there; Board had to wade through Ryan-Platform's delegation-chain internals before getting to anything useful.

**How to apply**:
- Default `AGENT_ID` for any boot invocation = `ceo` unless Board explicitly says "我要跟 Ryan/Leo/Maya/Jordan/Ethan/Sofia/Marco/Zara 说话"
- If marker is stuck on a non-CEO role and Board wants to force-reset without booting, tell them the one-liner: `echo ceo > /Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_active_agent` (Board's shell bypasses the role-write hook)
- If Board wants permanent: they already ran the echo line on 2026-04-13 after this was noted
