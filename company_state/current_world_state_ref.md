# Current World State References

This file is a pointer document only. It does not rewrite runtime state.

Primary references:
- `/Users/haotianliu/.openclaw/workspace/ystar-company/memory/WORLD_STATE.md`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/memory/session_handoff.md`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/.czl_subgoals.json`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_ceo_mode.json`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json`

Treatment:
- These are runtime-state references.
- Do not mutate them casually.
- Future console/read-model work should read curated index files first and only touch raw state through explicit, reviewed runtime mechanisms.
- DB/WAL/SHM files are intentionally excluded from direct read-model consumption.
