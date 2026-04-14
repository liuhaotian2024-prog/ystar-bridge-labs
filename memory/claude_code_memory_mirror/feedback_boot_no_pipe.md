---
name: Run governance_boot.sh directly — no pipes
description: Execute `bash scripts/governance_boot.sh AGENT_ID` as a plain Bash call. Do NOT pipe through tail/head, do NOT wrap in `run_in_background=true`.
type: feedback
originSessionId: 2c3c423c-3fd6-4427-88c8-a1c81c59f73a
---
**Rule**: On restart, use exactly:
```
bash /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/governance_boot.sh <AGENT_ID>
```

No `| tail -80`, no `| head -N`, no `run_in_background: true`, no redirect to a background log file that gets polled.

**Why**: 2026-04-13 restart, I piped output through `tail -80` inside a background Bash task. The pipe buffered, task output file stayed 0 bytes, I thought boot was hung, killed the wrapper process, re-ran. Turned a 30-second restart into a 5-minute debug session that made Board think the whole restart protocol was broken. The pipe was the bug, the protocol was fine.

**How to apply**:
- Boot script prints ~60 lines (obligations, lessons, continuation). That's fine — let it print.
- If output is too noisy to summarize, read the final file `/tmp/boot.log` after-the-fact; don't filter at the pipe level
- Timeout: give the Bash call at least 60000ms (script does 5 E2E hard constraint tests, genuinely takes ~20-30s)
- Completion signal: grep for exact string `ALL SYSTEMS GO` or `FAILURES`. Anything else = still running
