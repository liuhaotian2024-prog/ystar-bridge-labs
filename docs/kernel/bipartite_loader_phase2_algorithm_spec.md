# Bipartite Loader Phase 2 -- 6D Contrastive Drift Algorithm Spec

**Author**: Leo Chen (eng-kernel)
**Date**: 2026-04-19
**Status**: SPEC (no implementation)
**Audience**: CTO Ethan (architectural re-review before implementation); CEO Aiden (validation of 5-strategy coverage); Maya (integration with governance event types)
**Governing documents**:
  - CEO spec: `reports/ceo/governance/cieu_bipartite_learning_v1.md` (5 strategies)
  - CTO ruling: `Y-star-gov/reports/cto/CZL-BRAIN-BIPARTITE-ruling.md` (Q1-Q6)
  - 3-loop live spec: `reports/ceo/governance/brain_3loop_live_architecture_v1.md` (Section 5)
  - Phase 2 receipt: `reports/receipts/CZL-BRAIN-BIPARTITE-P2.md` (data baseline)

**Data baseline** (from P2 verified numbers, training_eligible=1 only):
  - Clean positives (allow + passed=1): 69,555
  - Clean negatives (deny + passed=0): 28,026
  - Escape pool (warn-as-escape + allow-fail, all passed=0): subset of 53,269
  - REWRITE candidates: 131 (Maya auditing quality)
  - Total training-eligible events: 381,026
  - Nodes in aiden_brain.db: 150, each with 6D coordinates (dim_y, dim_x, dim_z, dim_t, dim_phi, dim_c)

---

## A. Target Module Structure

### File path

`Y-star-gov/ystar/governance/cieu_bipartite_learner.py`

Per Ethan Q1: runs PARALLEL to existing Hebbian sub-system. Does NOT modify `aiden_brain.py` `hebbian_update()` or `apply_decay()`. The two systems share the `nodes` table but operate on different columns: Hebbian updates `edges`, bipartite updates `nodes.dim_*`.

### Public API

```python
def load_training_batch(
    cieu_db_path: str,
    brain_db_path: str,
    batch_size: int = 4096,
    escape_min_pct: float = 0.05,
    seed: int | None = None,
) -> TrainingBatch:
    """Load a stratified batch of CIEU events for contrastive drift.

    Returns a TrainingBatch containing event rows with 6D projections,
    weights, and partition labels. Enforces >=escape_min_pct escape
    samples per batch. Excludes system:* agent events at SQL level.
    Excludes training_eligible=0 events.
    """

def compute_drift(
    batch: TrainingBatch,
    brain_db_path: str,
    alpha: float = 0.15,
    lambda_contrastive: float = 0.5,
    max_drift_per_coord: float = 0.1,
) -> DriftResult:
    """Compute 6D coordinate drift vectors for each of 150 nodes.

    For each node, partitions relevant events into positive-weighted
    and negative-weighted sets, computes centroids, and derives the
    drift vector. Clips per-coordinate drift to max_drift_per_coord.
    """

def apply_drift_to_nodes(
    drift_result: DriftResult,
    brain_db_path: str,
    checkpoint: bool = True,
) -> ApplyResult:
    """Write drifted coordinates to aiden_brain.db nodes table.

    If checkpoint=True (default), saves current coordinates to
    a checkpoint table before applying. Returns count of nodes
    updated and total drift magnitude.
    """

def evaluate_held_out(
    cieu_db_path: str,
    brain_db_path: str,
    held_out_days: int = 7,
) -> EvalResult:
    """Evaluate brain quality on held-out recent events.

    Computes escape-sample recall and KL divergence vs baseline.
    Returns EvalResult with metrics + comparison table.
    """
```

### Data classes

```python
@dataclass
class WeightedEvent:
    event_id: str
    decision_canonical: str
    passed: int
    coords_6d: Coord6D          # from project_event_to_6d()
    weight: float               # signed: positive or negative
    partition: str              # 'positive' | 'negative' | 'escape_pre_hook' | 'escape_post_hook' | 'rewrite'

@dataclass
class TrainingBatch:
    events: list[WeightedEvent]
    stats: BatchStats           # counts per partition, total weight sums

@dataclass
class NodeDrift:
    node_id: str
    old_coords: Coord6D
    new_coords: Coord6D
    drift_vector: Coord6D       # new - old, per dimension
    drift_magnitude: float      # L2 norm of drift_vector
    n_positive_events: int
    n_negative_events: int

@dataclass
class DriftResult:
    node_drifts: list[NodeDrift]
    alpha_used: float
    lambda_used: float
    clipped_count: int          # how many nodes had drift clipped
    pass_id: int                # sequential pass number

@dataclass
class EvalResult:
    escape_recall: float        # proportion of held-out escape events
                                # whose nearest node shifted toward negative
    kl_divergence: float        # DKL(D_now || D_baseline)
    outcome_improvement: float  # delta in pass-rate prediction accuracy
    comparison_table: list[dict]  # per-bucket breakdown
```

### Dependencies

- `cieu_decision_normalizer.CANONICAL_VALUES`, `normalize()` -- canonical bucket lookup
- `cieu_brain_bridge.project_event_to_6d()`, `euclidean_6d()`, `top_k_nodes()` -- 6D projection and k-NN
- `aiden_brain.db` -- nodes table (150 nodes, 6D coords), activation_log
- `.ystar_cieu.db` -- cieu_events table (468K+ rows, columns: decision_canonical, passed, training_eligible, agent_id, event_type, drift_detected, violations)
- `sqlite3` -- direct DB access (no ORM)
- `math`, `statistics` -- centroid and divergence computation
- No external ML libraries. Pure numpy-free implementation. The 150-node 6D problem is small enough for stdlib.

---

## B. Sample Loading Logic (CIEU to Training Batches)

### B.1 Partition definitions

| Partition | SQL predicate (all rows also require `training_eligible = 1` AND `agent_id NOT LIKE 'system:%'`) | Weight |
|---|---|---|
| clean_positive | `decision_canonical = 'allow' AND passed = 1` | +1.0 |
| ambiguous_positive | `decision_canonical = 'allow' AND passed = 1 AND violations IS NOT NULL AND violations != '[]'` | +0.5 |
| good_deny | `decision_canonical = 'deny' AND passed = 0` | +0.8 |
| escape_pre_hook | `decision_canonical = 'escape' AND passed = 0 AND created_at < PRE_HOOK_CUTOFF` | **+0.6** |
| escape_post_hook | `decision_canonical = 'escape' AND passed = 0 AND created_at >= PRE_HOOK_CUTOFF` | **-0.3** |
| drift_flagged | `drift_detected = 1` (applies as weight modifier, not a separate partition) | additional -0.2 |
| rewrite | `decision_canonical = 'rewrite' AND passed = 1` | base weight x 3.0 multiplier |

**Constant**: `PRE_HOOK_CUTOFF = '2026-04-16T05:07:20'` -- timestamp of the first `HOOK_PRE_CALL` CIEU event. Events created before this timestamp occurred when governance hooks did not exist; these are blindspot coordinates where the brain was blind. The brain must learn TOWARD these patterns (+0.6 positive signal), not away from them. Events at or after this timestamp are genuine rule-edge-case failures that hooks caught but the agent escaped -- push brain away (-0.3 negative pull). Per CEO spec Section 3.2 lines 71-77, Ethan Ruling H.7.

**Weight composition rules** (applied in order):

1. Start with base weight from partition table above.
2. If `drift_detected = 1`, add -0.2 to the weight. A clean_positive with drift becomes +0.8. An escape_pre_hook with drift becomes +0.4. An escape_post_hook with drift becomes -0.5.
3. If partition is `rewrite`, multiply the cumulative weight by 3.0.

**Clarification on ambiguous_positive**: Events where `decision_canonical = 'allow' AND passed = 1` BUT the `violations` field is non-empty and not `'[]'` are "warned but passed" events. These get weight +0.5 instead of +1.0 because they carry ambiguity -- the system flagged something but the outcome was still positive. This is a sub-partition of clean_positive, identified at load time by inspecting the violations column.

### B.2 Self-referential exclusion (Ethan Q6)

All queries include:

```sql
WHERE training_eligible = 1
  AND (agent_id IS NULL OR agent_id NOT LIKE 'system:%')
```

Applied at SQL level, not Python post-filter. After loading each batch, an assertion verifies:

```python
assert all(
    not (e.get("agent_id") or "").startswith("system:")
    for e in batch.events
), "BRAIN_SELF_REFERENCE_VIOLATION"
```

If the assertion fails, abort the training pass and emit CIEU event `BRAIN_SELF_REFERENCE_VIOLATION`.

### B.3 Batch composition with rare-failure oversample (CEO spec 3.4)

Target batch size: 4096 events (configurable).

Composition algorithm:

```
1. escape_count = max(ceil(batch_size * escape_min_pct), 1)
                = max(ceil(4096 * 0.05), 1) = 205
   (combined: escape_pre_hook + escape_post_hook; 5% floor applies to total)

2. rewrite_count = min(available_rewrite, ceil(batch_size * 0.02))
                 = min(131, 82) = 82
   (REWRITE is so rare we take all available up to 2% cap)

3. remaining = batch_size - escape_count - rewrite_count
             = 4096 - 205 - 82 = 3809

4. Allocate remaining proportionally to clean_positive, good_deny,
   ambiguous_positive based on corpus ratio:
   - clean_positive ratio = 69555 / (69555 + 28026) = 0.713
   - good_deny ratio      = 28026 / (69555 + 28026) = 0.287
   - positive_count  = floor(3809 * 0.713) = 2716
   - deny_count      = 3809 - 2716 = 1093

5. Sample each partition randomly (with replacement if partition
   exhausted, which only applies to rewrite).

6. Verify: escape samples in batch >= 5% of batch_size.
```

### B.4 6D projection

For each loaded event row, call `project_event_to_6d(event_row)` from `cieu_brain_bridge.py` to obtain a `Coord6D` tuple. This is the event's position in 6D brain space.

The projection uses the existing heuristic rule table (11 rules, first-match). The same function is used by the L1 pre-query hook, ensuring consistency between the training signal and the inference path.

### B.5 OOD hold-back (CEO spec 3.5)

Before including events of a given `event_type` in the batch:

```sql
SELECT event_type, COUNT(*) as n
FROM cieu_events
WHERE training_eligible = 1
  AND agent_id NOT LIKE 'system:%'
GROUP BY event_type
HAVING n < 50
```

Any event_type with fewer than 50 training-eligible samples is excluded from the batch. These events are logged to a separate `ood_holdback_log` table (or CIEU event `BIPARTITE_OOD_HOLDBACK`) for CTO/Board review.

Rationale: a new event_type with insufficient samples could be a drift symptom; training on it prematurely bakes noise into coordinates.

---

## C. 6D Projection and Contrastive Drift Algorithm

### C.1 Activation relevance: which events map to which nodes

For each of the 150 nodes, determine which events from the batch are "relevant" -- i.e., which events' 6D projections fall within the node's receptive field.

```
For node N with coordinates C_N = (y, x, z, t, phi, c):
  relevant_events(N, batch) = {
      e in batch
      | euclidean_6d(e.coords_6d, C_N) < R_N
  }
```

Where `R_N` is the node's receptive radius, defined as:

```
R_N = median(distances from C_N to all 150 node coordinates) * 0.5
```

This adaptive radius ensures that nodes in dense regions of the 6D space have smaller receptive fields (more selective), while isolated nodes have larger ones.

If `|relevant_events(N, batch)| < 10`, skip this node for the current pass (insufficient signal to compute meaningful centroids).

### C.2 Partition relevant events into positive and negative sets

For each node N with sufficient relevant events:

```
positive_set(N) = { e in relevant_events(N) | e.weight > 0 }
negative_set(N) = { e in relevant_events(N) | e.weight < 0 }
```

Events with weight = 0 are excluded from centroid computation (they are neutral and carry no learning signal).

### C.3 Compute weighted centroids

For the positive set:

```
positive_centroid_6d[d] = SUM(e.weight * e.coords_6d[d] for e in positive_set)
                        / SUM(e.weight for e in positive_set)

for d in {dim_y, dim_x, dim_z, dim_t, dim_phi, dim_c}
```

For the negative set (note: weights are negative, so we use absolute values for centroid weighting):

```
negative_centroid_6d[d] = SUM(|e.weight| * e.coords_6d[d] for e in negative_set)
                        / SUM(|e.weight| for e in negative_set)
```

If `positive_set` is empty, skip this node (no positive signal to attract toward).
If `negative_set` is empty, use attraction-only update (see C.4 degenerate case).

### C.4 Update rule

**Full update** (both positive and negative sets non-empty):

```
drift_vector[d] = alpha * ((positive_centroid[d] - old_coord[d])
                           - lambda * (negative_centroid[d] - old_coord[d]))

new_coord[d] = old_coord[d] + drift_vector[d]
```

Expanding:
```
new_coord[d] = old_coord[d]
             + alpha * (positive_centroid[d] - old_coord[d])
             - alpha * lambda * (negative_centroid[d] - old_coord[d])
```

Interpretation:
- First term: attract toward positive centroid (move toward where successes cluster)
- Second term: repel from negative centroid (move away from where failures cluster)
- `alpha` controls overall step size (how far to move per pass)
- `lambda` controls contrastive strength (relative weight of repulsion vs attraction)

**Degenerate case** (negative_set empty):

```
drift_vector[d] = alpha * (positive_centroid[d] - old_coord[d])
```

Pure attraction, no repulsion. This is equivalent to the CEO spec's warning about Tesla-style averaging (alpha > 0 prevents full convergence to centroid, but without contrastive signal the update is purely attractive).

**Degenerate case** (positive_set empty):

Skip this node. We never apply pure repulsion without a positive anchor -- it would push the node into arbitrary regions of the space.

### C.5 Per-coordinate drift clipping

After computing `drift_vector[d]` for each dimension d:

```
drift_vector[d] = clip(drift_vector[d], -max_drift_per_coord, +max_drift_per_coord)

where max_drift_per_coord = 0.1
```

This ensures no node can move more than 10% of the coordinate range [0.0, 1.0] in a single pass, regardless of centroid geometry.

Additionally, clamp final coordinates to [0.0, 1.0]:

```
new_coord[d] = max(0.0, min(1.0, old_coord[d] + drift_vector[d]))
```

### C.6 Alpha adaptive schedule (Ethan Q3)

Constants (hard-coded, not CLI-configurable):

```python
ALPHA_INITIAL = 0.15
ALPHA_MIN = 0.10
ALPHA_MAX = 0.30
ALPHA_STEP = 0.05
COSINE_STABLE_THRESHOLD = 0.8
COSINE_UNSTABLE_THRESHOLD = 0.5
STABILITY_WINDOW = 3
```

After each full-corpus training pass, compute the cosine similarity between the aggregate contrastive direction vector of pass N and pass N-1:

```
contrastive_direction_N = mean(positive_centroid - negative_centroid)
                          across all nodes with both sets non-empty

cosine_sim = dot(cd_N, cd_{N-1}) / (||cd_N|| * ||cd_{N-1}||)
```

Schedule:
- If `cosine_sim > COSINE_STABLE_THRESHOLD` for `STABILITY_WINDOW` consecutive passes: increase alpha by `ALPHA_STEP`, capped at `ALPHA_MAX`.
- If `cosine_sim < COSINE_UNSTABLE_THRESHOLD`: decrease alpha by `ALPHA_STEP`, floored at `ALPHA_MIN`.
- Otherwise: alpha unchanged.

Every alpha change is logged as a CIEU event `BIPARTITE_ALPHA_ADJUSTED` with fields `{old_alpha, new_alpha, cosine_sim, pass_id}`.

### C.7 Pseudocode -- full drift pass

```python
def run_drift_pass(cieu_db_path, brain_db_path, pass_id):
    # 1. Load batch
    batch = load_training_batch(cieu_db_path, brain_db_path)

    # 2. Load all 150 nodes from brain
    nodes = load_all_nodes(brain_db_path)  # list of (id, coords_6d)

    # 3. Checkpoint current coordinates
    save_checkpoint(nodes, brain_db_path, pass_id)

    # 4. Compute receptive radii
    all_coords = [n.coords for n in nodes]
    for node in nodes:
        distances = [euclidean_6d(node.coords, other) for other in all_coords]
        node.radius = median(distances) * 0.5

    # 5. For each node, compute drift
    alpha = get_current_alpha(brain_db_path)  # from last pass or ALPHA_INITIAL
    lambda_c = 0.5  # contrastive strength

    drifts = []
    for node in nodes:
        # Find relevant events
        relevant = [e for e in batch.events
                    if euclidean_6d(e.coords_6d, node.coords) < node.radius]

        if len(relevant) < 10:
            continue  # insufficient signal

        pos = [e for e in relevant if e.weight > 0]
        neg = [e for e in relevant if e.weight < 0]

        if not pos:
            continue  # no positive anchor

        # Compute positive centroid (6D)
        pos_centroid = weighted_mean_6d(pos)

        if neg:
            # Compute negative centroid (6D, using |weight|)
            neg_centroid = weighted_mean_6d(neg, use_abs_weight=True)

            # Full contrastive update
            drift_vec = [
                alpha * ((pos_centroid[d] - node.coords[d])
                         - lambda_c * (neg_centroid[d] - node.coords[d]))
                for d in range(6)
            ]
        else:
            # Attraction-only (degenerate)
            drift_vec = [
                alpha * (pos_centroid[d] - node.coords[d])
                for d in range(6)
            ]

        # Clip per-coordinate
        drift_vec = [clip(v, -0.1, 0.1) for v in drift_vec]

        # Compute new coords, clamped to [0, 1]
        new_coords = tuple(
            max(0.0, min(1.0, node.coords[d] + drift_vec[d]))
            for d in range(6)
        )

        drifts.append(NodeDrift(
            node_id=node.id,
            old_coords=node.coords,
            new_coords=new_coords,
            drift_vector=tuple(drift_vec),
            drift_magnitude=l2_norm(drift_vec),
            n_positive_events=len(pos),
            n_negative_events=len(neg),
        ))

    # 6. Apply drifts to DB
    apply_drift_to_nodes(DriftResult(drifts, alpha, lambda_c, ...), brain_db_path)

    # 7. Update alpha schedule
    update_alpha_schedule(brain_db_path, pass_id, drifts)

    # 8. Evaluate on held-out
    eval_result = evaluate_held_out(cieu_db_path, brain_db_path)

    # 9. Check for feedback-loop divergence
    check_divergence(eval_result, brain_db_path, pass_id)

    return DriftResult(drifts, alpha, lambda_c, ...)
```

---

## D. Convergence and Safety

### D.1 Per-coordinate drift cap

Maximum absolute drift per coordinate per pass: 0.1

This is enforced in the `clip()` step of C.5. With coordinates in [0.0, 1.0], this means a node needs a minimum of 10 passes to traverse the full range of any single dimension, providing gradual convergence and opportunity for early detection of pathological drift.

### D.2 Stop condition

After each pass, compute:

```
pass_drift_vector = concatenation of all node drift vectors (150 * 6 = 900-dimensional)
cosine_sim = cosine(pass_drift_vector_N, pass_drift_vector_{N-1})
```

**Stop when**: `cosine_sim < 0.05` for 2 consecutive passes.

Interpretation: when the overall direction of coordinate change between successive passes is nearly orthogonal (cosine < 0.05), the system has effectively converged -- further passes would move nodes in random directions rather than systematically.

### D.3 Checkpoint and rollback

**Checkpoint storage**: a table `node_checkpoints` in `aiden_brain.db`:

```sql
CREATE TABLE IF NOT EXISTS node_checkpoints (
    checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pass_id       INTEGER NOT NULL,
    created_at    REAL NOT NULL,
    node_id       TEXT NOT NULL,
    dim_y         REAL NOT NULL,
    dim_x         REAL NOT NULL,
    dim_z         REAL NOT NULL,
    dim_t         REAL NOT NULL,
    dim_phi       REAL NOT NULL,
    dim_c         REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_checkpoint_pass ON node_checkpoints(pass_id);
```

Before every `apply_drift_to_nodes()`, the current coordinates of all 150 nodes are saved to this table with the current `pass_id`.

**Rollback trigger**: If the KL divergence check (Section D.4) detects an explosion:

```python
def rollback_to_checkpoint(brain_db_path, pass_id):
    """Restore node coordinates from the specified pass checkpoint."""
    conn = sqlite3.connect(brain_db_path)
    rows = conn.execute(
        "SELECT node_id, dim_y, dim_x, dim_z, dim_t, dim_phi, dim_c "
        "FROM node_checkpoints WHERE pass_id = ?", (pass_id,)
    ).fetchall()
    for r in rows:
        conn.execute(
            "UPDATE nodes SET dim_y=?, dim_x=?, dim_z=?, dim_t=?, dim_phi=?, dim_c=? "
            "WHERE id=?",
            (r[1], r[2], r[3], r[4], r[5], r[6], r[0])
        )
    conn.commit()
    conn.close()
    # Emit CIEU event
    emit_cieu("BIPARTITE_DRIFT_ROLLBACK", {"restored_pass_id": pass_id})
```

### D.4 KL divergence monitoring (Ethan Q4)

After each pass, run `evaluate_held_out()` to compute decision-prediction distribution on the held-out set.

**KL divergence computation**:

```python
def kl_divergence(p: dict[str, float], q: dict[str, float]) -> float:
    """DKL(P || Q) where P = current distribution, Q = baseline."""
    eps = 1e-10  # prevent log(0)
    kl = 0.0
    for bucket in CANONICAL_VALUES:
        p_val = p.get(bucket, eps)
        q_val = q.get(bucket, eps)
        if p_val > eps:
            kl += p_val * math.log(p_val / q_val)
    return kl
```

**Decision-prediction distribution**: For each held-out event, find its nearest node (k=1). The node's neighborhood (events in its receptive field from the training set) defines a distribution over `decision_canonical` values. The held-out event's "predicted" decision is the most frequent canonical value in that neighborhood. `D_now` is the aggregate distribution of predictions across all held-out events.

**Thresholds** (from Ethan Q4 ruling):

| Condition | Action |
|---|---|
| `DKL > 0.10` AND outcome flat/worsening | WARN: emit `BIPARTITE_DIVERGENCE_WARN` CIEU event |
| `DKL > 0.20` AND outcome flat/worsening | FREEZE: emit `FEEDBACK_LOOP_ALARM`, stop training, require CTO review |
| `DKL > 0.10` AND outcome improving | No alarm (healthy learning) |

**Outcome improvement** is measured as delta in escape-sample recall (Section E.1) compared to baseline.

### D.5 Cosine trajectory secondary alarm (Ethan Q4)

```
If cosine_sim(cd_N, cd_{N-1}) > 0.95 for 10+ consecutive passes
AND DKL is rising:
    emit FEEDBACK_LOOP_ALARM (strong evidence of monotonic feedback loop)
```

---

## E. Evaluation -- Held-Out Test

### E.1 Held-out split

Held-out set: most recent 7 days of CIEU events (by `created_at`), with `training_eligible = 1` and `agent_id NOT LIKE 'system:%'`.

The held-out set is NEVER used for training batch construction. The time-based split (most recent 7 days) ensures the held-out tests generalize to future data, not just interpolate within the training period.

Alternative (Ethan Q4): a fixed stratified sample of 1,000 events tagged `holdout=1` in a `cieu_holdout` table. For the initial implementation, use the time-based split (simpler, no schema change required). If CTO prefers the fixed holdout approach, switch in a follow-up.

### E.2 Metric 1: escape-sample recall

For each escape event in the held-out set:
1. Project to 6D via `project_event_to_6d()`.
2. Find nearest node (k=1) using `top_k_nodes()`.
3. Compute the node's "negative proximity" -- how much did this node drift toward the negative centroid during training?

```
negative_proximity(node) = 1 - cosine(node.drift_vector, mean_positive_direction)
```

If `negative_proximity > 0.5`, the node has drifted toward the negative region, meaning it would correctly flag this event as suspicious.

**Recall** = (escape events whose nearest node has negative_proximity > 0.5) / (total escape events in held-out)

Target: recall should be strictly greater than baseline (pre-training) recall. If not, the drift pass is harmful.

### E.3 Metric 2: KL divergence (see D.4)

Computed as part of every evaluation pass. Tracks whether the brain is diverging from its baseline decision distribution without corresponding outcome improvement.

### E.4 Pre/post comparison table template

```
| Metric                        | Baseline (pre-drift) | Post-drift | Delta  | Status   |
|-------------------------------|---------------------|------------|--------|----------|
| Escape recall (held-out)      | X.XX                | X.XX       | +X.XX  | PASS/FAIL|
| KL divergence vs baseline     | 0.000               | X.XXX      | +X.XXX | OK/WARN  |
| Mean node drift magnitude     | --                  | X.XXXX     | --     | INFO     |
| Nodes updated                 | --                  | N / 150    | --     | INFO     |
| Nodes skipped (< 10 events)   | --                  | N / 150    | --     | INFO     |
| Clipped drift count           | --                  | N          | --     | INFO     |
| Alpha used                    | --                  | X.XX       | --     | INFO     |
| Pass convergence cosine       | --                  | X.XXXX     | --     | INFO     |
```

Pass criteria: escape recall non-negative delta AND KL divergence not in FREEZE zone.

---

## F. Integration with 3-Loop Live (CEO Spec Section 5)

### F.1 When does the drift pass run

The drift pass runs as part of **L3 dream consolidation**, triggered by:
- `session_close_yml.py` at end-of-session
- Board offline >= 4h (autonomous mode transition)

Sequence within L3:
1. Dream consolidation runs (Pattern A/B/C/D proposals)
2. Bipartite drift pass runs (this spec)
3. Evaluation on held-out
4. Results logged to CIEU

The drift pass is computationally heavier than dream consolidation (loads 4096 events, computes centroids for 150 nodes). Running it during L3 (when the system is idle) avoids latency impact on L1 pre-query.

### F.2 Drift results feed L1 pre-query

After `apply_drift_to_nodes()` writes updated coordinates to `aiden_brain.db`, subsequent L1 pre-query calls to `top_k_nodes()` automatically use the new coordinates. No explicit hand-off is needed -- the bridge reads from the `nodes` table, which is the single source of truth.

### F.3 CIEU event types

| Event | Emitted when | Key fields |
|---|---|---|
| `BIPARTITE_DRIFT_START` | Drift pass begins | `{pass_id, batch_size, alpha, lambda}` |
| `BIPARTITE_DRIFT_COMPLETE` | Drift pass finishes successfully | `{pass_id, nodes_updated, mean_drift, eval_escape_recall, eval_kl}` |
| `BIPARTITE_DRIFT_ROLLBACK` | KL divergence triggers rollback | `{pass_id, restored_pass_id, kl_value}` |
| `BIPARTITE_ALPHA_ADJUSTED` | Alpha schedule changes alpha | `{old_alpha, new_alpha, cosine_sim, pass_id}` |
| `BIPARTITE_OOD_HOLDBACK` | Event type excluded for low sample count | `{event_type, sample_count, threshold}` |
| `BIPARTITE_DIVERGENCE_WARN` | DKL > 0.10 with flat outcome | `{kl_value, escape_recall_delta}` |
| `FEEDBACK_LOOP_ALARM` | DKL > 0.20 with flat outcome, or cosine > 0.95 for 10 passes | `{kl_value, cosine_streak}` |
| `BRAIN_SELF_REFERENCE_VIOLATION` | System event leaked into batch | `{count, agent_ids}` |

All events use `agent_id = 'system:brain_bipartite'` and `provenance = 'system:brain'` per Ethan Q6.

---

## G. Test Plan

### G.1 Unit tests (target: 20+ cases)

**load_training_batch tests**:
1. Batch respects `training_eligible = 1` filter (events with eligible=0 never appear)
2. Batch excludes `agent_id LIKE 'system:%'` events
3. Escape samples >= 5% of batch size
4. REWRITE samples capped at 2% of batch size
5. Batch size matches requested size (within 1% tolerance for rounding)
6. Weights are correct: clean positive = +1.0, good deny = +0.8, escape_pre_hook = +0.6, escape_post_hook = -0.3
7. Drift modifier: drift_detected=1 subtracts 0.2 from base weight
8. REWRITE multiplier: rewrite events have weight * 3.0
9. Empty corpus returns empty batch gracefully
10. OOD hold-back: event_type with < 50 samples excluded from batch

**compute_drift tests**:
11. Single node with only positive events: pure attraction, no repulsion term
12. Single node with both pos/neg: drift vector points away from negative centroid
13. Per-coordinate clip enforced: drift > 0.1 clipped to 0.1
14. Final coordinates clamped to [0.0, 1.0]
15. Node with < 10 relevant events: skipped (no drift computed)
16. Node with empty positive set: skipped
17. Drift magnitude is L2 norm of drift vector

**apply_drift_to_nodes tests**:
18. Checkpoint table populated before apply
19. Coordinates in DB match computed new_coords after apply
20. Rollback restores exact checkpoint coordinates

**evaluate_held_out tests**:
21. Held-out uses only last 7 days of events
22. KL divergence is 0.0 when distributions are identical
23. Escape recall computed correctly on known test data

### G.2 Integration test

Full pipeline integration:
- Seed a test `.ystar_cieu.db` with 500 synthetic events (300 positive, 100 negative, 50 escape, 50 rewrite)
- Seed a test `aiden_brain.db` with 10 nodes at known coordinates
- Run `load_training_batch` -> `compute_drift` -> `apply_drift_to_nodes` -> `evaluate_held_out`
- Assert: nodes moved toward positive centroid (verify with euclidean distance comparison)
- Assert: nodes moved away from negative centroid
- Assert: checkpoint table has exactly 10 rows
- Assert: evaluation returns non-zero metrics

### G.3 Regression test (feedback-loop detection)

Construct a pathological scenario:
- 1000 events all with `decision_canonical = 'allow'` and `passed = 1` (uniform positive)
- 0 negative events
- Run 5 drift passes
- Assert: KL divergence is monotonically increasing (no contrastive signal)
- Assert: alpha does NOT increase (cosine similarity should be unstable without contrastive pull)

This test catches the Tesla-style feedback loop: if the system trains only on positives, it should NOT claim improvement.

### G.4 Performance test

- Load full corpus from production `.ystar_cieu.db` (381K training-eligible events)
- Run single drift pass over 150 nodes with batch_size=4096
- Assert: total wall-clock time <= 120 seconds (2 minutes target)
- Profile: batch loading (expected dominant cost: SQL query + 6D projection)
- Profile: centroid computation (expected: fast, 4096 events * 150 nodes * 6 dims)
- Profile: DB writes (expected: 150 UPDATEs, trivial)

If the 2-minute target is exceeded, the bottleneck is almost certainly the 6D projection call for each event. Optimization path: precompute and cache 6D projections in a `coords_6d_cache` table during the normalizer migration. This is Phase 3 scope, not Phase 2.

---

## H. Open Questions for CTO Ethan Architectural Re-Review

### H.1 Lambda (contrastive strength) initial value

This spec proposes `lambda = 0.5` (repulsion is half the strength of attraction). Rationale: with the corpus imbalance (69K positive vs 28K negative for clean buckets, plus 53K escape which is negatively weighted), a full-strength lambda=1.0 might over-repel because the negative centroid has high variance (heterogeneous failure modes). Lambda=0.5 provides moderate repulsion.

**Question**: Does Ethan have a principled argument for a different initial value? Should lambda also be adaptive (similar to alpha)?

### H.2 Receptive radius multiplier

This spec uses `R_N = median(inter-node distances) * 0.5`. The 0.5 multiplier is heuristic. Too small -> many nodes get < 10 relevant events and are skipped. Too large -> nodes overlap heavily and centroids blur together.

**Question**: Should the multiplier be tuned empirically after the first pass (e.g., find the multiplier that gives each node 50-200 relevant events on average)? Or is 0.5 acceptable as initial value with a note to revisit?

### H.3 Checkpoint storage location

This spec places `node_checkpoints` in `aiden_brain.db`. Alternative: a separate `aiden_brain_checkpoints.db` file to keep the main brain DB lean.

**Question**: Ethan ruling on whether checkpoints belong in the same DB or a sibling file?

### H.4 Held-out strategy

This spec uses a time-based held-out (last 7 days). Ethan Q4 ruling suggests a fixed 1,000-event stratified holdout with `holdout=1` flag. These are different strategies with different tradeoffs:
- Time-based: tests generalization to future data; no schema change; but held-out set changes daily
- Fixed holdout: stable comparison baseline across passes; requires schema change or separate table; but may not represent evolving event distribution

**Question**: Which approach does Ethan prefer? Or both (time-based for regression detection, fixed for long-term trend comparison)?

### H.5 Interaction with CEO's formula vs this spec's formula

The CEO spec (Section 3.1) states:
```
new_coord = positive_centroid + alpha * (positive_centroid - negative_centroid)
```

Ethan's ruling (Q3) repeats this formula. This spec implements a slightly different formulation:
```
new_coord = old_coord + alpha * ((positive_centroid - old_coord) - lambda * (negative_centroid - old_coord))
```

The difference: the CEO/Ethan formula positions the new coordinate relative to the positive centroid (ignoring the old coordinate), while this spec's formula computes a delta from the old coordinate. The delta-from-old formulation provides:
- Gradual convergence (old coordinate anchors movement)
- Per-coordinate clipping works naturally (clip the delta)
- When alpha is small, the node moves a small step rather than jumping near the positive centroid

**Question**: Is this reformulation acceptable? Or should the implementation strictly follow the CEO/Ethan formula? The original formula could produce large jumps when positive_centroid is far from old_coord, which the per-coordinate clip would then truncate anyway.

### H.6 REWRITE pool quality gate

The 131 REWRITE candidates are being audited by Maya. The spec applies a 3x weight multiplier to REWRITE events. If Maya finds that a significant fraction (>30%) of REWRITE labels are noise, the multiplier should be reduced or REWRITE events should be excluded until audit completes.

**Question**: Should the implementation gate REWRITE inclusion on Maya's audit completion (i.e., only include REWRITE events that Maya has tagged as quality-verified)? Or proceed with all 131 and adjust multiplier post-audit?

---

## Appendix: Notation Reference

| Symbol | Meaning | Value/Range |
|---|---|---|
| alpha | Overall drift step size | [0.10, 0.30], initial 0.15 |
| lambda | Contrastive strength (repulsion/attraction ratio) | Initial 0.5 (pending Ethan ruling) |
| max_drift_per_coord | Per-dimension drift clip | 0.1 |
| R_N | Node receptive radius | median(inter-node distances) * 0.5 |
| k | Nearest neighbors for evaluation | 1 (held-out) or 3 (L1 pre-query) |
| Coord6D | 6-tuple | (dim_y, dim_x, dim_z, dim_t, dim_phi, dim_c) |
| D_now | Current decision-prediction distribution on held-out | 7-bucket probability vector |
| D_baseline | Baseline distribution (pre-training or 30-day-old) | 7-bucket probability vector |
| DKL | KL divergence DKL(D_now \|\| D_baseline) | nats; thresholds 0.10 (WARN), 0.20 (FREEZE) |

---

*This spec covers Sections A-H as required by the CZL-BIPARTITE-LOADER-P2-SPEC dispatch. NO CODE has been produced. Implementation begins after Ethan reviews Section H and rules on open questions.*
