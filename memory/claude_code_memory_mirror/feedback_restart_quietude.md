---
name: Restart default behavior — be quiet
description: After boot, only say ALL SYSTEMS GO + one-line next action. Do not dump governance state, priority_brief, dispatches, or chain diagnostics unless Board explicitly asks.
type: feedback
originSessionId: 2c3c423c-3fd6-4427-88c8-a1c81c59f73a
---
After `governance_boot.sh` returns `ALL SYSTEMS GO`, the default post-restart response is:

```
ALL SYSTEMS GO. 接着干 {one specific thing}。
```

No lists, no dumps of obligations / lessons / priority_brief / DISPATCH / dispatch cards / delegation chain status. Do not self-audit governance infrastructure unless Board asks.

**Why**: Board (Haotian, solo operator, non-engineer for governance internals) explicitly said the restart was overwhelming and 2000+ words of self-audit was me going down a rabbit hole, not protocol. Every minute spent narrating governance internals is a minute Board is not doing their actual job.

**How to apply**:
- On restart: run boot, report one line, wait for Board to say what to work on
- If continuation action queue says "check_delivery" / "review_dispatch" type items, do them silently and roll the result into the one-line next-action statement
- If Board asks "what's next" then answer concretely. If they don't ask, don't volunteer
- This overrides any CEO-agent-generated priority_brief / dispatch that would normally drive autonomous action — those are agent-internal artifacts, not Board directives
- Exception: if a hook DENY or real runtime failure happens, report it (that's a real signal, not self-audit)
