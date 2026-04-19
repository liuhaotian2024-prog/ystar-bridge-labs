# claude-mem Research Scan — Relevance to Y*gov / ARCH-17 / ARCH-18

**Audience**: CEO (Aiden), CTO (Ethan) — for Board situational awareness
**Research basis**: WebSearch + WebFetch on thedotmack/claude-mem (GitHub, npm, docs.claude-mem.ai); cross-checked against our own memory stack (auto-memory MD corpus, CIEU DB 353k events, aiden_brain.db 146-node 6D graph).
**Synthesis**: 5-tuple receipt with ADOPT / ADAPT / IGNORE / REVISIT-LATER verdict per component.
**Purpose**: Decide whether to integrate, steal patterns, or ignore ahead of ARCH-17 (behavioral governance) + ARCH-18 (CIEU-as-brain-corpus) implementation.
**Date**: 2026-04-19
**Time budget**: 10 tool_uses / ≤12 cap.

---

## 1. What claude-mem IS

- **Author**: thedotmack (community project, not Anthropic).
- **Form factor**: Claude Code plugin, installed via `npx claude-mem install` or `/plugin`.
- **Runtime**: TypeScript/Node.js 18+, Bun process manager. Worker service = Express API on `localhost:37777`.
- **Storage**: SQLite at `~/.claude-mem/claude-mem.db` + ChromaDB vector sidecar (`ChromaSync.ts`).
- **License**: AGPL-3.0 (main) + PolyForm Noncommercial 1.0.0 on `ragtime/` subdir. **Maturity**: active, v10.3.1 as of this week, breaking changes still shipping (v5 → v7 → v10 in months).
- **Problem solved**: Claude Code forgets everything across sessions. claude-mem hooks into 5 lifecycle events (SessionStart / UserPromptSubmit / PostToolUse / Summary / SessionEnd), compresses raw tool I/O (1k–10k tokens) into ~500-token semantic observations via Claude Haiku, and re-injects filtered context on next SessionStart.

## 2. Technical architecture

### Data schema (SQLite)
- `sdk_sessions` — `sdk_session_id`, `claude_session_id`, `project`, `prompt_counter`, `status`, timestamps.
- `observations` — `session_id`, `project`, `prompt_number`, `tool_name`, `title`, `subtitle`, `narrative`, `text`, `facts`, `concepts`, `type`, file refs, timestamps.
- `session_summaries` — `request`, `investigated`, `learned`, `completed`, `next_steps`, `notes`.
- `user_prompts` — raw prompt text + counter.
- **Observation type enum**: `decision | bugfix | feature | refactor | discovery | change` — this is the key semantic axis.
- FTS5 virtual tables: `observations_fts`, `session_summaries_fts`, `user_prompts_fts` (trigger-synced).

### Retrieval / ranking
- **Hybrid** FTS5 BM25 `ORDER BY rank` + Chroma semantic similarity.
- No published scoring formula combining the two; appears to be rank-and-filter, not weighted fusion.
- **3-layer progressive disclosure** = index (50–100 tokens of IDs+titles) → timeline (chronological anchor) → full body fetch on filtered IDs only. Claimed ~10x / 50–75% token savings.
- **No temporal decay, no activation weighting, no N-dim coordinate embedding** documented. Chroma dim unspecified (likely default 1536 for OpenAI or model-native).

### Skills surface
- `mem-search` — HTTP query API
- `make-plan` — phased implementation planner
- `do` — subagent executor
- `<private>` tag stripping at hook edge for PII.

## 3. Relevance to Y*gov setup (dimension-by-dimension)

| Dimension | Our system | claude-mem | Match? |
|---|---|---|---|
| Event capture | CIEU (353k events, 5-tuple Y*/Xt/U/Yt+1/Rt+1, governance-grade causal) | PostToolUse hook, tool_name+input+output only | claude-mem is a SUBSET — captures tool I/O, no governance semantics, no Rt residual |
| Storage | CIEU SQLite DBs (.ystar_cieu.db) + aiden_brain.db 6D graph + markdown corpus | Single SQLite + Chroma sidecar | Architecturally similar at storage layer |
| Retrieval | aiden_brain.db has 6D coords but **0 activations** (shelved); MD corpus served by Claude Code's native auto-memory | FTS5 + Chroma hybrid, 3-layer disclosure | claude-mem has a WORKING activation path; we don't |
| Compression | None on CIEU; MD corpus hand-curated | Haiku compresses 1–10k → ~500 tokens with type+concepts+facts schema | **Gap they solve we haven't** |
| Ingest external logs | N/A (we ARE the log source) | No documented external ingest API | **Blocker for direct adoption** |
| Coordinate embedding | aiden_brain.db 6D manual | Chroma vector (opaque dim) | Different paradigm — theirs is learned, ours is structured |
| Activation semantics | Designed but not firing | SessionStart injection = crude "always load top-K by recency+relevance" | Neither has true activation physics |

## 4. What they got right that we haven't

1. **Observation type enum** (`decision | bugfix | feature | refactor | discovery | change`) is a useful **behavioral taxonomy** for CIEU events. Our CIEU has action types but no semantic intent class. ARCH-17 (behavioral governance) could borrow this axis verbatim and extend with governance-specific types (`violation | escalation | forgetguard_block | delegation`).
2. **Session summary schema** (`request / investigated / learned / completed / next_steps / notes`) is effectively a structured 5-tuple-adjacent receipt. Maps cleanly onto our Y*/Xt/U/Yt+1/Rt+1 but adds `investigated` and `learned` which are absent from our model — worth considering as optional fields for longer causal chains.
3. **3-layer progressive disclosure** is a clean retrieval pattern for 353k-scale CIEU — it solves the "load-everything-or-nothing" problem our aiden_brain.db hit. Algorithm: (a) FTS/metadata scan → compact index, (b) chronological window around anchor, (c) full fetch only for filtered IDs. This is **directly portable to CIEU-as-brain-corpus (ARCH-18)**.
4. **Per-session compression via sub-model** (Haiku) — a cheap background process generates summaries, freeing main-context tokens. We currently have no compression layer on CIEU; 353k events is getting unwieldy.
5. **Worker service pattern** (Express :37777) decouples capture from main Claude Code process. Same architectural shape as our gov-mcp (:7922).

## 5. What they DON'T have that we need

- No governance semantics (no allow/deny/redirect, no ForgetGuard equivalent, no 5-tuple residual).
- No cross-session causal chain (K9Audit territory).
- No policy enforcement — purely descriptive memory, not prescriptive governance.
- No external event ingest — cannot feed our CIEU into it without custom adapter.
- AGPL-3.0 license blocks us from pulling code into Y*gov (Y*gov is MIT). **Pattern-steal only, no code import.**
- Single-user/single-project assumption — no multi-agent identity layer, no CEO/CTO/CMO role separation.

## 6. Recommendation: **ADAPT (patterns only), IGNORE (product)**

### ADOPT directly (pattern)
- **Observation type enum** → extend CIEU with semantic-intent column (ARCH-17 scope).
- **3-layer progressive disclosure retrieval** → ARCH-18 CIEU-as-brain-corpus query API. This is the closest thing to "activation" for our 353k-event corpus and directly addresses aiden_brain.db's 0-activation problem.
- **Session summary schema** (`investigated / learned / next_steps`) → augment our 5-tuple with optional longitudinal fields for multi-session narratives.

### ADAPT (steal, don't copy)
- Worker service + SQLite + FTS5 triggers → already our shape, just not fully wired. Cross-reference their trigger DDL for our ARCH-18 implementation.
- Compression pipeline (Haiku background summarizer) → could run against CIEU DB to generate per-session "what happened" cards without burning main context.

### IGNORE (do not adopt product)
- AGPL license incompatible with Y*gov MIT.
- No governance primitives — it's a memory tool, not an enforcement layer.
- No 5-tuple / CIEU semantics.
- Would compete, not complement, once ARCH-18 ships.

### REVISIT-LATER
- Chroma embedding layer — if aiden_brain.db's 6D manual coords prove insufficient for ARCH-18 retrieval, revisit vector sidecar pattern (but with open-source model, not Anthropic API).

---

## 5-Tuple Receipt

- **Y\*** (goal): Decide whether claude-mem is useful or inspiring for Y*gov.
- **Xt** (state): Board heard of claude-mem; ARCH-17 + ARCH-18 in design; 353k CIEU + 146-node 6D graph under-activated.
- **U** (action): WebSearch + WebFetch on 4 URLs (github, docs root, db schema, search arch); cross-mapped to our stack.
- **Yt+1** (new state): Verdict issued — three patterns worth adopting (type enum / 3-layer retrieval / session summary schema); product itself not adoptable (license + scope mismatch).
- **Rt+1** (residual): 0. Research question answered. Next action owned by CTO: decide whether ARCH-17 schema extension includes observation type enum; ARCH-18 query API should borrow 3-layer disclosure.

**Tool uses**: 6 (2 WebSearch + 4 WebFetch) — under 12 cap.

---

## Sources

- https://github.com/thedotmack/claude-mem
- https://www.npmjs.com/package/claude-mem
- https://docs.claude-mem.ai/installation
- https://docs.claude-mem.ai/architecture/database
- https://docs.claude-mem.ai/architecture/search-architecture
- https://github.com/thedotmack/claude-mem/blob/main/CLAUDE.md
