# Brain 3-Loop Live Architecture — Implementation Spec

**Audience**: Ryan-Platform (hook wiring) · Leo-Kernel (semantic/Hebbian layer) · Maya-Governance (CIEU event types + dream scheduling) · Ethan-CTO (architectural review before ship) · Board (final green-light after Leo add_node fix tests pass).
**Research basis**: Board 2026-04-19 Q1 "are you working through the brain right now?" — **answer: no, brain is passive**; Q2 "how to make it rapidly smarter through work?" — 3-loop closed architecture. Empirical: `hook_ceo_pre_output_brain_query.py` exists as standalone module but zero references in `.claude/settings.json` hook chain. `aiden_brain.db` has 150 nodes + 1902 edges + 1.4M activation_log rows but WHO_I_AM access_count=0 due to `add_node()` INSERT OR REPLACE self-destruct (Ethan P0 bug). Consultant diagnosis: "hardware present, network not alive". Ethan's BRAIN-AUTO-INGEST ruling selected (c)+(d) boundary ingest and rejected (a) cron + (b) hot-path.
**Synthesis**: brain becomes a decision substrate (not archive) via 3 closed loops — **L1 pre-query** injects brain wisdom before decisions, **L2 write-back** records which nodes fired + strengthens Hebbian co-activation, **L3 dream consolidation** periodically distills activation_log into new nodes/edges. Each loop individually has marginal value; only the closed system produces flywheel effect. All 3 loops are currently broken (L1 unwired, L2 nonexistent, L3 manual-only). The L1+L2+L3 design here is additive to Ethan's (c)+(d) boundary ingest — boundary ingest feeds nodes INTO the brain; 3-loop makes the brain PARTICIPATE in work.
**Purpose**: give Ryan / Leo / Maya a ready-to-implement spec so that the moment Leo's CZL-BRAIN-ADD-NODE-PRESERVE fix lands + tests pass + CZL-BRAIN-AUTO-INGEST ships, 3-loop-live can be wired same-session. Prep during Leo's fix window (Board directive 2026-04-19: "趁这个时间把方案先做好").

**Author**: Aiden Liu (CEO)
**Date**: 2026-04-19
**Status**: [L1] SPEC — ready for Ethan architectural review
**Authority**: Board directive 2026-04-19 acknowledgement of Q1+Q2; Ethan's BRAIN-AUTO-INGEST ruling (already landed)
**Gating dependency**: CZL-BRAIN-ADD-NODE-PRESERVE (Leo) MUST land BEFORE any L2 write-back runs. Otherwise L2 writes trigger add_node which destroys state.

---

## 1. Architectural Overview

```
┌──────────────────────────────────────────────────────────────────┐
│  USER / BOARD PROMPT                                             │
│          │                                                       │
│          ▼                                                       │
│  L1: Pre-Query Hook (UserPromptSubmit)                           │
│   • Extract query signals (intent keywords, file scope refs)     │
│   • Project to 6D via cieu_brain_bridge.project_event_to_6d()    │
│   • Fetch top_k=3 nodes from aiden_brain.db                      │
│   • Inject wisdom summary (≤150 chars each) into CEO context     │
│          │                                                       │
│          ▼                                                       │
│  CEO REASONS + TAKES ACTION (tool calls, sub-agent spawns)       │
│          │                                                       │
│          ▼                                                       │
│  L2: Write-Back Hook (PostToolUse + Stop)                        │
│   • For each completed tool call / session-close:                │
│     – Determine which top_k nodes fired in the decision context  │
│     – Append activation_log row (node_ids, timestamp, session)   │
│     – For each pair of co-fired nodes: increment co_activations, │
│       bump Hebbian weight by learning_rate (capped at 1.0)       │
│     – Increment nodes.access_count for each fired node           │
│          │                                                       │
│          ▼                                                       │
│  L3: Dream Consolidation (periodic / idle)                       │
│   • Triggers: (a) session_close_yml.py end-of-session OR         │
│                (b) Board offline ≥4h autonomous mode transition  │
│   • Scans last N activation_log rows (N ~= 5000 default)         │
│   • Finds frequent co-activation patterns → proposes new edges   │
│   • Finds orphan/weak nodes → proposes pruning or archiving      │
│   • Finds recurring unknown-node hits → proposes new node adds   │
│   • Writes dream_proposals.jsonl for CEO-review-next-boot        │
└──────────────────────────────────────────────────────────────────┘
```

**Closed loop property**: L2 feeds L3 (activations fuel dream material) · L3 feeds L1 (better nodes/edges improve future queries) · L1 feeds L2 (injected wisdom guides decisions, which fire co-activations) → flywheel.

---

## 2. Loop 1 — Pre-Query (Read Path)

### 2.1 Trigger
`.claude/settings.json` → `hooks.UserPromptSubmit` — fires once per Board prompt. NOT PreToolUse (too fine, 200+ per session, latency risk) and NOT boot-only (too coarse).

Rationale: Board prompts are the natural decision-unit boundary. Each prompt starts a reasoning chain where pre-query wisdom has maximum leverage.

### 2.2 Hook wiring (Ryan-Platform deliverable)

Add to `.claude/settings.json`:
```json
"hooks": {
  "UserPromptSubmit": [
    {
      "hooks": [
        {"type": "command",
         "command": "python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_ceo_pre_output_brain_query.py"}
      ]
    }
  ]
}
```

Fallback: if query fails (brain DB locked / file missing) → emit CIEU event `BRAIN_QUERY_FAILED` and proceed without injection (NEVER block the prompt).

### 2.3 Query logic (module already exists — audit + finalize)
`hook_ceo_pre_output_brain_query.py` — read prior code, verify:
- Extracts signals from prompt text + any cited file paths
- Calls `project_event_to_6d()` to get 6D coordinates
- Calls `top_k_nodes(k=3)` against aiden_brain.db
- Returns top 3 nodes' names + first 150 chars of wisdom file + access_count

### 2.4 Injection format (into CEO context)
```
[BRAIN_WISDOM_K3]
  1. [0.74] Who I Am (hub, access_count=N) — <150char summary>
  2. [0.67] Entanglement: Maya claim-reality mismatch — <summary>
  3. [0.63] Iron Rule 0 (no choice questions) — <summary>
```

### 2.5 Latency budget
≤50ms total (brain query on 150 nodes with sqlite index is ~5-15ms; file read 3× 150-char slices is ~2ms; overhead 10ms). If measured > 50ms p95, Ryan investigates.

### 2.6 Selective query optimization
If prompt is simple acknowledgement ("ack", "ok", "continue"), SKIP query — no value in pre-query for trivial replies. Heuristic: prompt length < 30 chars → skip. Configurable threshold in `.ystar_session.json`.

---

## 3. Loop 2 — Write-Back (Learn Path)

### 3.1 Trigger
Two hooks:
- `PostToolUse` on Agent tool (sub-agent dispatch) — primary decision points
- `Stop` hook (end of CEO reply) — catches all other decisions that didn't spawn agents

### 3.2 New module: `scripts/hook_ceo_post_output_brain_writeback.py` (Ryan-Platform deliverable + Leo-Kernel semantic logic)

Responsibilities:
1. Read the most recent `BRAIN_WISDOM_K3` context injection from session cache (written by L1)
2. For each of the k=3 nodes that WERE fired, compute relevance score:
   - If CEO's reply explicitly cited the node's content → relevance=1.0
   - If CEO's action (tool call scope, agent prompt) matched node keyword → 0.6
   - Else → 0.3 (merely background context)
3. Write activation entry:
```json
{
  "query": "<original user prompt snippet>",
  "activated_nodes": [
    {"node_id": "WHO_I_AM", "relevance": 1.0},
    {"node_id": "feedback/atomic_dispatch", "relevance": 0.6},
    ...
  ],
  "session_id": "<current>",
  "timestamp": <unix>
}
```
4. Hebbian update for each pair in activated_nodes with relevance > 0.3:
   - `edges.co_activations += 1`
   - `edges.weight = min(1.0, weight + learning_rate * relevance_product)`
   - learning_rate = 0.1 initial (configurable)
5. Increment `nodes.access_count` for each fired node (gated on Leo's INSERT ON CONFLICT fix)

### 3.3 Async queue (latency-safe)
L2 writes are async: hook appends to `scripts/.brain_writeback_queue.jsonl`, a background cron/worker drains it every 30s. Stop hook never blocks user experience on DB writes.

### 3.4 Co-activation guard (Ethan's Q6 from CZL-BRAIN-BIPARTITE — self-referential training)
Write-back entries get `provenance='system:brain'` per Ethan's ruling. Bipartite learner (Leo's Phase 2) excludes these when computing contrastive drift, preventing brain-learning-from-brain-output feedback loop.

### 3.5 Failure handling
If writeback fails → CIEU event `BRAIN_WRITEBACK_FAILED` + queue preserved on disk for next session retry. NEVER drops data silently.

---

## 4. Loop 3 — Dream Consolidation (Grow Path)

### 4.1 Trigger (two conditions, either fires)
- **Session close**: `scripts/session_close_yml.py` → invokes `aiden_dream.py --mode consolidate --scope session-close` at end of every session
- **Board offline ≥4h**: detected via no UserPromptSubmit event in 4h → autonomous agent launches `aiden_dream.py --mode consolidate --scope idle` in a dedicated sub-session

### 4.2 Dream module (Maya-Governance deliverable — schedule integration; Leo-Kernel — semantic consolidation algorithm)

`aiden_dream.py` already exists. Audit current implementation, likely needs:
1. Scan last N=5000 activation_log rows (or since last consolidation timestamp)
2. **Pattern A**: find node pairs co-activated >3 times without an existing edge → propose new edge with low initial weight
3. **Pattern B**: find clusters of 3+ nodes always co-activating together → propose new `ecosystem_entanglement` node if cluster bridges 2+ module categories
4. **Pattern C**: find nodes with access_count ≤ 2 in past 30 days → propose archive/prune (write to archive proposals, NOT actioned automatically)
5. **Pattern D**: find recurring prompt contexts that activated NO high-relevance node → propose new node for blind spot
6. Write all proposals to `scripts/.dream_proposals.jsonl`

### 4.3 Review gate
Dream proposals are NOT applied automatically. On next boot, `governance_boot.sh` prints proposal count + CEO reviews + applies selectively via a new `aiden_dream.py --apply-proposal <id>` CLI.

### 4.4 CIEU event types (Maya-Governance deliverable)
- `BRAIN_DREAM_CYCLE_START` — when dream starts
- `BRAIN_DREAM_PROPOSAL_WRITTEN` — one per proposal
- `BRAIN_DREAM_CYCLE_COMPLETE` — with counts
- `BRAIN_NODE_PROPOSED` / `BRAIN_EDGE_PROPOSED` / `BRAIN_ARCHIVE_PROPOSED` — fine-grained

### 4.5 Idempotency guard
Dream writes a sentinel `.last_dream_timestamp` before starting. If another dream triggers within 30min, SKIP (prevents concurrent dream corruption).

---

## 5. Integration with Ethan's (c)+(d) Boundary Ingest

Ethan's CZL-BRAIN-AUTO-INGEST ruling ships boundary ingest in:
- **(c) governance_boot.sh** — boot-time ingest of new files since last boot
- **(d) session_close_yml.py** — close-time ingest

This 3-loop spec LAYERS ON TOP:
- Boundary ingest adds nodes/edges from reports/knowledge/memory (Ethan's domain)
- 3-loop makes those nodes PARTICIPATE in decisions (this spec's domain)

Order of ship:
1. **Leo**: CZL-BRAIN-ADD-NODE-PRESERVE (in flight now)
2. **Ethan/Leo/Ryan/Maya**: CZL-BRAIN-AUTO-INGEST implementation (boundary ingest + access_count preservation)
3. **Ryan**: L1 pre-query hook wiring (this spec Section 2)
4. **Ryan+Leo**: L2 write-back hook + module (this spec Section 3)
5. **Maya+Leo**: L3 dream scheduling + consolidation algorithm (this spec Section 4)

Each stage has its own regression tests. Stage N+1 ships only if Stage N passes.

---

## 6. Success Criteria

**L1 Live**: ≥80% of Board prompts in a session trigger successful pre-query injection within 50ms p95. CIEU events `BRAIN_QUERY_SUCCESS` > `BRAIN_QUERY_FAILED` 10:1.

**L2 Live**: WHO_I_AM `access_count` monotonically increases across a session. Hebbian edges with `co_activations > 0` grows by ≥10/session. No `INSERT OR REPLACE` regressions (Leo's fix preserves state).

**L3 Live**: Every session close OR 4h idle → dream proposals file exists with ≥1 proposal. Boot reports proposal count. Proposals actioned ≥1/day with CEO review.

**Flywheel proven (L5)**: 30-day window — cognitive gap rate (ForgetGuard violations + MATURITY_TAG_MISSING + choice_question_to_board) decreases month-over-month because brain increasingly pre-warns CEO. Measurable via CIEU event volume trend on these rule_ids.

---

## 7. Risks & Safeguards

| Risk | Safeguard |
|---|---|
| L1 latency exceeds 50ms → user experience degraded | p95 monitoring + feature flag to disable L1 if threshold breached |
| L2 async queue loses data on crash | Queue is JSONL-on-disk, not in-memory; survives crash; drained on next boot |
| L3 dream proposes bad edges → brain pollution | All proposals are GATED — CEO reviews before apply; never auto-applied |
| Self-referential feedback loop (brain learns from its own outputs) | provenance='system:brain' tag excludes these from bipartite training (Ethan Q6 ruling honored) |
| Concurrent L2 writes race on Hebbian update | Use sqlite transaction + optimistic concurrency (WHERE co_activations = :expected_old) |
| Pre-query before Leo's add_node fix | GATED — L1 wire MUST wait for Leo's P0 fix + regression tests green |
| Dream runs during heavy session | Idempotency guard + 30-min sentinel prevents concurrent dream corruption |

---

## 8. Owner Handoff Checklist

| Deliverable | Owner | Scope |
|---|---|---|
| L1 hook wire + latency check | Ryan-Platform | 1 config edit + 1 p95 test |
| L1 module audit (hook_ceo_pre_output_brain_query.py) | Leo-Kernel | read existing, verify project_event_to_6d + top_k_nodes contract |
| L2 new module + hook wire | Ryan (hook) + Leo (semantic) | new script + async queue + 2 hook configs |
| L2 regression tests | Ryan-Platform | concurrent writeback + crash-recovery tests |
| L3 dream algorithm enhance | Leo-Kernel | Pattern A/B/C/D in aiden_dream.py |
| L3 scheduling + CIEU events | Maya-Governance | 4 new CIEU event types + session_close_yml integration |
| Gating: add_node fix landed | Leo-Kernel | CZL-BRAIN-ADD-NODE-PRESERVE (in flight) |
| Architectural review of this spec | Ethan-CTO | single ruling .md in Y-star-gov/reports/cto/ |

---

## 9. Implementation Timeline (event-driven, not human cadence)

- **NOW → Leo#2 returns**: this spec reviewed by Ethan
- **Leo#2 returns green** + **CZL-BRAIN-AUTO-INGEST (c+d) boundary ship**: kickoff L1 + L2 in parallel
- **L1 L3 SHIPPED**: Ryan regression tests pass + 50ms p95 verified
- **L2 L3 SHIPPED**: end-to-end test — one full decision cycle writes ≥1 activation_log row + ≥1 Hebbian update
- **L3 L3 SHIPPED**: first dream cycle runs on session close, proposals file appears
- **Flywheel L5**: 30-day CIEU gap-rate trend shows decline

No human-cadence like "this week" or "in 3 days". Event-driven: N+1 waits on N's green.
