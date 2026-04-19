---
Audience: Ethan CTO CIEU-corpus design + Board wakeup brief + future dream mode.
Research basis: live DB probes 2026-04-19 pre-dawn during Board autonomous-run window.
Synthesis: CIEU corpus and 6D brain are physically disconnected today; fusion is GWT implementation with 353k-event empirical base.
Purpose: give Ethan enough data to bake fusion pipeline into ARCH-18 spec without re-discovery.
---

# CIEU × 6D Brain Fusion — Empirical Findings

## Database inventory (live probe)

**.ystar_cieu.db** (216 MB)
- Table `cieu_events`: 353,747 rows (real corpus)
- Table `events`: 16 rows (legacy, ignore)
- FTS index `cieu_fts`: 353,747 docs indexed
- Table `sealed_sessions`: 0 rows (session-sealing not yet used)

**aiden_brain.db** (1.0 MB)
- Table `nodes`: 146 rows (6D coords per node)
- Table `edges`: 1,638 rows
- Table `activation_log`: 0 rows (NEVER FIRED — shelved)

## Node type breakdown

| node_type | count | role |
|---|---|---|
| meta | 68 | architectural concepts (building_aiden / 6d_cognitive_architecture / global_workspace) |
| ecosystem_team | 15 | team units (CEO/CTO/engineers/C-suite) |
| ceo_learning | 12 | CEO learning records |
| ecosystem_module | 12 | Y*gov/Labs/K9 submodules |
| ecosystem_product | 10 | product entities |
| self_knowledge | 9 | identity/honesty rules |
| paradigm | 7 | failure-mode lessons |
| strategic | 7 | CEO strategic thinking |
| ecosystem_entanglement | 5 | cross-module coupling (THIS is causal surface) |
| hub | 1 | central broadcast node (GWT theater) |

## Fusion pipeline required (ARCH-18 mandate)

Every CIEU event row must flow through:

1. **Feature extraction** — (agent_id, event_type, tool_name, decision, reason, payload_signature, timestamp) → feature vector
2. **6D projection** — map feature vector to (dim_y, dim_x, dim_z, dim_t, dim_phi, dim_c) coordinates using learned projection matrix (initial: hand-rules, later: embedding model)
3. **Top-K node activation** — K-nearest nodes in 6D space receive activation with weight inversely proportional to distance
4. **activation_log INSERT** — rows: (event_id, node_id, activation_weight, timestamp)
5. **Hebbian edge update** — co-fired nodes → strengthen existing edge OR create new edge if absent
6. **Dim centroid drift** — node's own 6D coords slowly move toward accumulated firing context (learning)

## Usage paths

- **CEO pre-output**: project current-context to 6D → query top-N recently-active nodes → inject node content as wisdom context
- **CEO pre-dispatch**: project proposed task to 6D → which ecosystem_entanglement nodes fire? → surface coupling risks before spawn
- **Dream mode (nightly)**: scan activation_log over window → find unusual co-firing clusters → propose new nodes/edges → write to dreams/
- **Root-cause analysis**: given failure event, read backward through activation_log to identify node chain → feed K9Audit CausalChainAnalyzer

## GWT mapping (Global Workspace Theory)

| GWT concept | Y*gov implementation |
|---|---|
| Conscious workspace (theater) | `hub` node + top-K high-activation nodes |
| Specialized modules | other 145 nodes |
| Broadcast | activation_log INSERT fanout |
| Attention/selection | 6D projection + K-NN query |
| Long-term memory | nodes + edges tables |
| Episodic memory | cieu_events table |
| Global availability | CEO/CTO pre-output hooks query activated set |

## Why this matters for Board's directive

Board 2026-04-19: "融合起来，意味着什么？" — fusion is not incremental, it is **brain going from hardware to living network**. Every 2-hour Experiment 3 accumulates activation_log rows. Dream mode has real substrate to synthesize from. Ethan's CTO brain gets identical architecture, specialized with technical-depth nodes.

Shelf ratio S(t) target (per ARCH-17): today 100% shelved (activation_log=0). Post-fusion Phase 1 ship: target S(t) ≤ 20% within 100 tool-calls.
