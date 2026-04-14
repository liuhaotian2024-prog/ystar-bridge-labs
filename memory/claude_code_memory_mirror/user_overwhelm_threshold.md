---
name: Board overwhelm is a hard-stop signal
description: Haotian (Board) is a solo non-engineer for governance internals. When they signal overwhelm ("太复杂", "我不知道该干什么", "给我一个更聪明的人"), stop dumping agent-internal state immediately.
type: user
originSessionId: 2c3c423c-3fd6-4427-88c8-a1c81c59f73a
---
**User**: Haotian Liu (刘浩天) — Board / 老大. Solo operator of Y* Bridge Labs. Technical enough to build this, but **not the audience** for governance-plane minutiae like delegation chain INVALID issues, priority_brief §P0-1 items, AMENDMENT-N proposals.

**What lands as signal vs noise for Board**:
- ✅ Signal: concrete user-visible outcomes, product decisions, "is X broken yes/no", cost/time tradeoffs, external opportunities (HN, customers, press)
- ❌ Noise: agent-to-agent dispatch cards, self-generated audit findings, governance health scores, chain state dumps, amendment drafts

**Overwhelm phrases to treat as hard stop**:
- "太复杂" / "我不知道该干什么"
- "给我一个更聪明的人" / "可以跟更聪明的人对话"
- "这到底谁在用" (Board-asking-themselves cue)
- Long silence after I dump a governance wall-of-text

**How to apply**: When triggered, immediately:
1. Stop mid-task if needed
2. State the ONE concrete thing they could do (not a list)
3. Name which of the ongoing agent activities can be paused/killed without cost
4. Do not propose new amendments, new audits, or new self-checks
5. Offer to write a SANITY_CHECK.md / kill-list rather than more governance artifacts

**Background**: Board uses ChatGPT for independent audit and has zero tolerance for fabrication. They want honesty over politeness. "你这段评论真是给我一个沉重的打击" on 2026-04-13 was them metabolizing hard truth, not asking me to soften — softening now would be the insult.
