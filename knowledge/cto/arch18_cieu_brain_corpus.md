# ARCH-18: CIEU-as-Brain-Corpus Architecture Spec

**Author**: Ethan Wright (CTO)
**Date**: 2026-04-19
**Status**: DESIGN — Phase 0 executable-on-read
**Board directive**: "把 CIEU log 放进 Aiden 和 Ethan 的大脑里面"

---

## Formal Definitions

Let `E` denote the CIEU event corpus, `E = {e_1, e_2, ..., e_N}` where `N = 353,334`.

Each event `e_i` is a tuple:
```
e_i = (id, t_i, type_i, agent_i, session_i, decision_i, payload_i)
```
where:
- `t_i in R+` — Unix timestamp (created_at)
- `type_i in T` — event type, `|T| = 209`
- `agent_i in A` — agent identifier, `|A| = 426` (includes ephemeral session IDs)
- `session_i in S` — session identifier, `|S| = 15,104`
- `decision_i in {allow, deny, info, warn, escalate, unknown, ...}`
- `payload_i` — structured JSON (params_json, result_json, violations, drift_details)

**Brain function** `B: Context x Query -> Decision`:
```
B(ctx, q) = argmax_d P(d | ctx, q, M(E))
```
where `M(E)` is the memory representation of corpus `E` — the design target of this spec.

**Objective**: Design `M(E)` such that:
1. `P(correct_decision | M(E))` > `P(correct_decision | no_M)` (measurable via shelf-ratio)
2. Latency(M(E) lookup) < 2s per query
3. Coverage(causal_graph(E)) > 80% of event types

## Mathematical Model

### Information-Theoretic Framing

The CIEU corpus has entropy:
```
H(E) = -SUM_over_types P(type) * log2(P(type))
```

Empirical type distribution (top 10 of 209 types cover 54% of events):
```
K9_ROUTING_DISPATCHED:  47,026 (13.3%)  — system routing noise
HOOK_HEALTH_K9_ESCALATE: 24,175 (6.8%)  — health monitoring
AGENT_REGISTRY_K9_WARN:  22,359 (6.3%)  — registry warnings
external_observation:    20,870 (5.9%)   — actual governance decisions
SESSION_JSON_SCHEMA_VIOLATION: 16,012 (4.5%) — schema drift
HOOK_BOOT:               15,163 (4.3%)  — boot telemetry
orchestration:*:         44,548 (12.6%) — orchestration heartbeats
omission_setup_complete: 14,648 (4.1%)  — setup confirmations
handoff:                 14,633 (4.1%)   — session handoffs
circuit_breaker_armed:   14,573 (4.1%)  — circuit breaker events
```

**Signal-to-noise ratio**: ~35% of events are actionable governance decisions (external_observation, cmd_exec, file_write, file_read, BEHAVIOR_RULE_VIOLATION, intervention_gate:deny). ~65% are system telemetry/heartbeat noise.

### Bayesian Decision Support

For a new decision query `q` at time `t`:
```
P(deny | q, E) = P(q | deny_events) * P(deny) / P(q)
```

Prior from corpus:
```
P(deny)     = 44,618 / 353,334 = 0.126
P(allow)    = 64,929 / 353,334 = 0.184
P(info)     = 137,817 / 353,334 = 0.390
P(warn)     = 47,946 / 353,334 = 0.136
P(escalate) = 28,225 / 353,334 = 0.080
```

These priors alone tell us: **12.6% of all governance events result in denial**. Any agent action has a ~1-in-8 chance of hitting a governance wall. This is the base rate for engineering reliability targets.

---

## 1. Corpus Characterization (Empirical)

### 1.1 Schema

Two tables coexist in `.ystar_cieu.db`:

| Table | Rows | Purpose |
|-------|------|---------|
| `cieu_events` | 353,334 | Primary governance audit trail (28 columns) |
| `events` | 16 | Legacy lightweight event log (5 columns) |

**Primary table `cieu_events`** (28 columns): identity (event_id UUID, rowid, seq_global us-order), temporal (created_at), context (session_id, agent_id, event_type), decision (allow/deny/escalate/info/warn + passed bool), drift (drift_detected/details/category + violations JSON), target (file_path, command, url, skill_name, task_description), lineage (contract_hash, chain_depth, human_initiator, lineage_path), payload (params_json: 87,944 populated, avg 251B, max 8,204B; result_json), audit (sealed, evidence_grade).

**Indexes**: 5 B-tree (session_id, agent_id, decision, created_at, event_type). **FTS**: FTS5 on 11 text columns. **Sealed sessions**: Merkle-root hash chain.

### 1.2 Size

| Metric | Value |
|--------|-------|
| Total events | 353,334 |
| DB file size | 224 MB |
| Total payload bytes (JSON fields) | 62.6 MB |
| Distinct event types | 209 |
| Distinct agents | 426 (including ~300 ephemeral session-hash agents) |
| Named agents | ~30 (CEO, CTO, 4 engineers, Secretary, CMO, CFO, CSO, system:*) |
| Distinct sessions | 15,104 |

### 1.3 Temporal Coverage

| Date | Events | Notes |
|------|--------|-------|
| 2026-04-09 | 21 | Genesis |
| 2026-04-10 | 90 | Early testing |
| 2026-04-11 | 3,739 | First real sessions |
| 2026-04-12 | 6,043 | AMENDMENT-004 migration |
| 2026-04-13 | 19,367 | Autonomy push begins |
| 2026-04-14 | 14,285 | Sub-agent dispatch era |
| 2026-04-15 | 23,834 | Unified Work Protocol |
| 2026-04-16 | 117,169 | Peak — massive dispatch + K9 routing |
| 2026-04-17 | 46,292 | Stabilization |
| 2026-04-18 | 81,828 | Hook enforcement live |
| 2026-04-19 | 41,430 | Current (partial day) |

**Growth rate**: ~40,000-80,000 events/day (current steady state).

### 1.4 Agent Coverage

| Agent Category | Events | Denials | Denial Rate |
|----------------|--------|---------|-------------|
| system:k9_subscriber | 47,245 | 0 | 0.0% |
| unidentified | 40,172 | 9,506 | 23.7% |
| agent (generic) | 34,741 | 18,150 | 52.3% |
| orchestrator | 31,168 | 0 | 0.0% |
| Ethan-CTO | 27,213 | 0 | 0.0% |
| ceo | 17,735 | 891 | 5.0% |
| intervention_engine | 10,390 | 10,390 | 100.0% |
| Leo-Kernel | 9,112 | 0 | 0.0% |
| Maya-Governance | 8,187 | 0 | 0.0% |
| Ryan-Platform | 7,573 | 0 | 0.0% |
| eng-platform | 6,221 | 123 | 2.0% |
| cto | 5,087 | 208 | 4.1% |

**Key insight**: `unidentified` agents have 23.7% denial rate; `agent` (generic) has 52.3%. Agents that fail to identify themselves get denied far more often. This is empirical proof that identity enforcement works.

### 1.5 Decision Distribution

| Decision | Count | Percentage |
|----------|-------|------------|
| info | 137,817 | 39.0% |
| allow | 64,929 | 18.4% |
| warn | 47,946 | 13.6% |
| deny | 44,618 | 12.6% |
| unknown | 29,672 | 8.4% |
| escalate | 28,225 | 8.0% |

### 1.6 Drift Categories (38,028 drift events)

| Category | Count |
|----------|-------|
| (uncategorized) | 15,673 |
| identity_violation | 12,014 |
| institutional_memory | 6,602 |
| omission_failure | 3,322 |
| intervention_pulse | 417 |

### 1.7 Top Deny Event Types (Failure Library Source)

| Event Type | Deny Count |
|------------|------------|
| circuit_breaker_armed | 14,639 |
| intervention_gate:deny | 12,014 |
| external_observation | 7,336 |
| cmd_exec | 5,362 |
| file_write | 2,462 |
| BEHAVIOR_RULE_VIOLATION | 990 |
| Bash | 507 |
| Write | 389 |
| Read | 282 |
| web_fetch | 179 |
| Edit | 173 |
| handoff_failed | 34 |

---

## 2. Brain-Ingestion Architecture

### 2.1 Route Analysis

**Route A: Pre-output RAG** — Embed CIEU in vector DB, retrieve top-K at decision time. (+) Real-time, scales. (-) Misses causal structure; ~$15 embedding cost; cold-start per session.

**Route B: Nightly Pattern-Synthesis** — LLM batch summarizes CIEU into "lessons learned". (+) Human-readable, compresses to ~50 pages. (-) Stale by design; lossy; hallucination-prone on structured data.

**Route C: K9Audit CausalChainAnalyzer** — Feed CIEU through `build_causal_dag()`. (+) Preserves causation; root cause analysis native. (-) JSONL adapter needed; ~350MB RAM; session-scoped only.

**Route D: Hybrid — Signal-Routed Architecture (SELECTED)** — Different event categories serve different cognitive functions. Route each to its optimal pipeline.

```
CIEU Events (353K)
    |
    +--[DENY events: 44,618]------> Failure Library (structured extraction)
    |                                 -> ForgetGuard rules
    |                                 -> Regression tests
    |                                 -> Behavioral taxonomy
    |
    +--[DRIFT events: 38,028]------> K9 CausalChainAnalyzer
    |                                 -> Causal DAG per session
    |                                 -> Root cause catalog
    |                                 -> Intervention effectiveness scores
    |
    +--[ALLOW+INFO: 202,746]-------> Statistical Priors (batch aggregation)
    |                                 -> Agent performance baselines
    |                                 -> Normal behavior fingerprints
    |                                 -> Decision latency distributions
    |
    +--[HEARTBEAT/NOISE: ~65%]-----> Filtered out (retained in DB, not ingested)
    |
    +--[ESCALATE: 28,225]----------> Escalation Pattern Library
                                      -> Board intervention triggers
                                      -> Resolution time analysis
```

### 2.2 Route D Rationale (with Industry Precedent)

I select Route D because the CIEU corpus is not a homogeneous text corpus — it is a multi-modal structured log with distinct signal types. Treating it as a single embedding target (Route A) discards structure. Summarizing it (Route B) discards specifics. Analyzing it purely causally (Route C) misses statistical patterns. Hybrid routing matches each signal type to its best-fit analytical method.

**Industry precedents (5+ references)**:

1. **Replay Buffers in Reinforcement Learning** (Mnih et al., 2015, "Human-level control through deep RL", Nature). Experience replay stores (s, a, r, s') tuples and samples them for training. CIEU events are governance-domain (state, action, reward, next-state) tuples. Our "replay" is structured extraction, not gradient descent, but the principle is identical: past experience improves future decisions.

2. **OPA Decision Log Mining** (Open Policy Agent, Styra). OPA's decision log records every policy evaluation with input/output/decision. Styra DAS mines these logs to: (a) detect policy drift, (b) generate coverage reports, (c) suggest policy improvements. CIEU is architecturally equivalent to OPA decision logs. Our failure library extraction mirrors Styra's policy suggestion pipeline.

3. **LangSmith Trace Replay** (LangChain, 2024). LangSmith records full LLM traces (input/output/latency/token counts) and provides replay + analysis. Key insight: they do NOT embed all traces into a vector DB. They provide structured querying (filter by run type, status, latency) plus human-readable dashboards. Our hybrid approach follows this pattern.

4. **Post-Mortem Automation** (Google SRE Book, Ch. 15 "Postmortem Culture"). Google automates post-mortem generation from monitoring logs, correlating alert triggers with timeline events. Their system routes different signal types (alerts, changes, traffic) through different analysis pipelines before merging into a unified postmortem document. Our DENY -> Failure Library pipeline mirrors this.

5. **Retrieval-Augmented Agent Memory** (Park et al., 2023, "Generative Agents: Interactive Simulacra of Human Behavior", Stanford). Generative agents store observations in a memory stream, retrieve by recency + importance + relevance, and reflect on retrieved memories. Our hybrid routes high-importance events (DENY, DRIFT) through deep analysis while letting low-importance events (heartbeats) decay.

6. **Incident.io Learning from Incidents** (incident.io engineering blog, 2024). They extract structured "learnings" from incident timelines, tag them with failure modes, and surface relevant learnings when similar incidents occur. Our failure library extraction is this pattern applied to governance events.

---

## 3. Per-Brain Integration

### 3.1 CEO Brain (Aiden)

**Hook point**: Session boot (`governance_boot.sh` Phase 2). Inject `CIEU_BRAIN_CONTEXT` block (2,000 tokens max) containing: active failure patterns (deny events, last 48h, with frequency + mitigation), agent performance dashboard (last 7 days, denial rates + trends), unresolved escalations (count + age), causal insights from K9 (top root cause + intervention effectiveness).

**Use cases**: Pre-dispatch (check agent denial rates), pre-escalation (check similar resolutions), post-mortem (full causal chain), strategic planning (trend analysis).

### 3.2 CTO Brain (Ethan)

**Hook point**: Task acceptance (when CTO receives a task card from `.claude/tasks/`). Inject `CIEU_CTO_CONTEXT` block containing: code-path failure map (file_write + cmd_exec denials by path pattern), architecture decision support (modules with highest drift, cross-module causal chains, test coverage gaps), build/deploy failure patterns (most-denied commands), engineer performance table (task completion, denial rate, scope violations).

**Use cases**: Architecture decisions (module fragility), task assignment (engineer-scope denial rates), code review (common violation patterns per file path), post-mortem writing (full causal chains).

### 3.3 Engineers

**Access level**: Read-only, filtered to own scope.

Engineers do NOT get the full CIEU brain context. They receive:
- Their own denial history (last 7 days) at task start
- Relevant failure patterns for files in their task scope
- No access to other engineers' performance data
- No access to escalation patterns or strategic data

**Rationale**: Engineers need tactical context ("this file path has been denied 12 times for scope violations"), not strategic overview. Limiting their view prevents information overload and maintains focus.

**Injection mechanism**: Task card includes a `## Prior Failures` section auto-populated by querying CIEU for denials matching the task's file scope.

---

## 4. Failure Library Extraction

### 4.1 Architecture

```
CIEU DB (deny events: 44,618)
    |
    v
[Failure Extractor Script]  --- runs at session boot + on-demand
    |
    +---> ForgetGuard YAML candidates
    |       knowledge/shared/forgetguard_candidates.yml
    |
    +---> Regression test cases
    |       tests/regression/cieu_extracted/
    |
    +---> Behavioral rule taxonomy entries
            knowledge/shared/behavioral_rules_from_cieu.yml
```

### 4.2 ForgetGuard-YAML Candidate Extraction

**Algorithm**:
1. Query: `SELECT violations, drift_details, event_type, agent_id, COUNT(*) FROM cieu_events WHERE decision='deny' GROUP BY violations, event_type HAVING COUNT(*) >= 3 ORDER BY COUNT(*) DESC`
2. For each cluster of 3+ identical violations:
   - Extract the violation predicate (from `violations` JSON)
   - Map to ForgetGuard rule format:
     ```yaml
     - rule_id: "FG_CIEU_{hash}"
       trigger: "{extracted predicate}"
       action: deny
       source: "CIEU corpus, {count} occurrences, first seen {date}"
       confidence: {count / total_denials}
     ```
3. Deduplicate against existing ForgetGuard rules in `.ystar_session.json`
4. Output to `knowledge/shared/forgetguard_candidates.yml` for CTO review

**Threshold**: Only promote to ForgetGuard if:
- >= 5 occurrences (statistical significance)
- Occurred across >= 2 distinct sessions (not session-specific noise)
- Not already covered by existing ForgetGuard rule (dedup check)

### 4.3 Regression Test Case Generation

For each deny event with populated `params_json` and `command`/`file_path`: extract action + violation rule, generate `test_cieu_regression_{hash}()` that simulates the action and asserts governance engine denies it. Group by violation type (1 test per unique `(event_type, violation_pattern)` pair) to avoid redundancy. Output to `tests/regression/cieu_extracted/`.

### 4.4 Behavioral Rule Taxonomy Entries (ARCH-17 Feed)

Each deny cluster maps to a behavioral rule:
```yaml
- rule: "CIEU_BR_{hash}"
  description: "Agents must not {action} because {reason}"
  evidence: "{count} denials across {sessions} sessions"
  first_observed: "{date}"
  last_observed: "{date}"
  agents_affected: ["{agent_list}"]
  severity: "{count_normalized}"
```

**Top candidates from current corpus** (empirically derived):

| Pattern | Deny Count | Rule Candidate |
|---------|------------|----------------|
| circuit_breaker_armed | 14,639 | "Do not proceed when circuit breaker is armed" |
| intervention_gate:deny | 12,014 | "Identity must be established before any action" |
| external_observation denied | 7,336 | "External observations require valid agent context" |
| cmd_exec denied | 5,362 | "Commands outside agent scope are blocked" |
| file_write denied | 2,462 | "File writes outside permitted paths are blocked" |
| BEHAVIOR_RULE_VIOLATION | 990 | "Known behavioral anti-patterns auto-deny" |

---

## 5. Causal Chain Analysis (K9Audit Integration)

### 5.1 Adapter Design

K9Audit's `CausalChainAnalyzer` reads JSONL files. CIEU is in SQLite. `CIEUtoK9Adapter` bridges them:

- `export_session_jsonl(session_id)`: Query `cieu_events WHERE session_id=? ORDER BY seq_global`, transform each row to K9 record format (`event_type`, `X_t: {agent_id, session_id}`, `U_t: {skill, params}`, `Y_t+1: {result}`, `R_t+1: {passed, violations}`), write to `/tmp/cieu_k9/{session_id}.jsonl`.
- `export_deny_sessions()`: Find `SELECT DISTINCT session_id FROM cieu_events WHERE decision='deny'`, export each via `export_session_jsonl`.

### 5.2 Causal Analysis Pipeline

**Execution**: Batch job, triggered at session boot if last run > 6 hours ago.

1. Export deny-containing sessions via adapter (~2,000 sessions with denials)
2. For each session: `CausalChainAnalyzer(path).build_causal_dag()`, then `find_root_causes()` for each deny node; store in catalog
3. Aggregate root causes: group by type, count frequency, compute `IE(intervention) = P(no_repeat | intervention) - P(no_repeat | no_intervention)`
4. Output to `cieu_causal_catalog.json`, `cieu_intervention_scores.json`, `cieu_attack_surface.json`

### 5.3 Attack Surface Map

Derived from causal DAG edges:
```json
{
  "attack_surfaces": [
    {
      "entry_point": "cmd_exec",
      "deny_rate": 0.594,
      "common_violations": ["scope_violation", "identity_missing"],
      "downstream_impact": ["file_write", "file_read"],
      "causal_depth": 3.2
    }
  ]
}
```

### 5.4 Intervention Effectiveness Scores

For each intervention type (circuit_breaker, identity_check, scope_guard):
```
Effectiveness(I) = 1 - (repeat_violations_after_I / violations_before_I)
```

Output enables CTO to prioritize which governance mechanisms to strengthen.

---

## 6. Dream-Mode Input

### 6.1 Design

Dream mode synthesizes CIEU patterns during idle periods (trigger: session idle > 30min OR explicit Board command).

**Pipeline**: CIEU Dream Reader queries last 48h events grouped by (event_type, decision, agent_id) + all drift events + escalation events with resolution. Pattern Synthesizer runs: (1) anomaly detection (event types with >2 sigma frequency change), (2) correlation mining (co-occurring event types within 60s windows), (3) counterfactual generation ("If agent X had been identified, would deny Y have been avoided?").

**Output**: `knowledge/{ceo,cto}/dreams/dream_{date}.md` containing: anomalies detected, counterfactuals, emerging patterns, ForgetGuard rule recommendations.

---

## 7. Privacy / Secret Hygiene

### 7.1 Threat Model

CIEU `params_json` and `result_json` may contain:
- File contents (from Read/Write tool calls)
- Command outputs (from Bash tool calls)
- API keys, tokens, passwords (if agent accidentally processed .env files)
- Personal data (email addresses, names in content files)

### 7.2 Sanitization Layer

**Position in pipeline**: Between CIEU DB read and any brain ingestion route.

`CIEUSanitizer` class redacts `params_json`, `result_json`, `command`, `task_description` fields using regex patterns for: API keys (OpenAI sk-*, GitHub ghp_*, AWS AKIA*), generic secret assignments, base64 blobs >40 chars, email addresses.

**Validation**: Run on full corpus, count redactions, spot-check 100 random redacted events for false positives/negatives.

### 7.3 Access Control

- Sanitized corpus: CEO + CTO access
- Raw corpus (`.ystar_cieu.db`): System-level only (hooks, governance engine)
- Engineer view: Pre-filtered to own agent_id + own file_path scope, always sanitized
- Dream output: Sanitized before writing to knowledge/

---

## 8. Measurable Outcomes

### 8.1 Shelf-Ratio Reduction

**Definition**: Shelf-ratio = (knowledge available but not used) / (total knowledge available).

**Current state**: CIEU has 353K events. CEO and CTO use exactly 0 of them for decisions. Shelf-ratio = 1.00.

**Target** (Phase 1, first 30 sessions after deployment):
- CEO brain context includes CIEU data: shelf-ratio < 0.95 (top 5% of events surfaced)
- Failure library extracted: shelf-ratio < 0.85 (deny events fully mined)

**Target** (Phase 2, after K9 integration):
- Causal graph covers 80%+ of event types: shelf-ratio < 0.50
- Dream mode synthesizes weekly: shelf-ratio < 0.30

**Measurement**: `shelf_ratio = 1 - (events_referenced_in_decisions / total_events)`
Track via CIEU meta-events: emit `CIEU_BRAIN_QUERY` event each time brain context is loaded.

### 8.2 Decision-Support Latency

| Operation | Target Latency |
|-----------|---------------|
| Boot context generation | < 3s |
| Failure library query | < 500ms |
| Causal chain trace (single session) | < 2s |
| Full causal catalog rebuild | < 5min |
| Dream synthesis (48h window) | < 30s |

**Measurement**: Instrument each query with timing. Store in CIEU as `BRAIN_QUERY_LATENCY` events.

### 8.3 Causal-Graph Coverage

**Definition**: Coverage = (event types with at least one causal edge) / (total event types).

**Current**: 0% (no causal graph exists).
**Target Phase 1**: 60% (deny-containing event types fully graphed).
**Target Phase 2**: 80%+ (all actionable event types graphed).

**Measurement**: After each K9 CausalChainAnalyzer run, compute coverage from DAG metadata.

### 8.4 Decision Quality Improvement

**Proxy metric**: Denial rate trend.

If CIEU brain context helps agents avoid known failure patterns, the denial rate should decrease over time (agents learn from past denials).

**Baseline**: 12.6% overall denial rate (current).
**Target**: < 8% denial rate after 60 sessions with CIEU brain active.

**Counterfactual validation**: For each new denial, check if the failure pattern existed in the brain context that session. If yes, the brain failed to prevent a known failure — flag for investigation.

---

## 9. Implementation Phases

### Phase 0: Corpus Characterization (THIS DOCUMENT)
- Empirical data collected and documented above
- Schema, size, distribution, temporal coverage verified via sqlite3
- No implementation required — this spec is the deliverable

### Phase 1: Failure Library Extraction
- Build `cieu_failure_extractor.py`
- Extract ForgetGuard candidates from deny clusters
- Generate behavioral rule taxonomy entries
- Inject into session boot context
- **Estimated effort**: 1 engineer, 1 session

### Phase 2: Brain Context Generation
- Build `cieu_brain_context.py`
- CEO boot hook integration (governance_boot.sh Phase 2)
- CTO task acceptance hook integration
- Engineer task card auto-population
- **Estimated effort**: 1 engineer, 2 sessions

### Phase 3: K9Audit CausalChainAnalyzer Integration
- Build `cieu_k9_adapter.py`
- Batch causal analysis pipeline
- Attack surface map generation
- Intervention effectiveness scoring
- **Estimated effort**: 1 engineer, 2 sessions

### Phase 4: Dream Mode
- Build `cieu_dream_reader.py`
- Anomaly detection on event frequency
- Counterfactual generation
- Dream output to knowledge/ directories
- **Estimated effort**: 1 engineer, 1 session

### Phase 5: Sanitization + Access Control
- Build `cieu_sanitizer.py`
- Validate against full corpus
- Engineer-scoped view filtering
- **Estimated effort**: 1 engineer, 1 session

---

## 10. File Manifest

| File | Purpose | Phase |
|------|---------|-------|
| `tools/cieu/cieu_failure_extractor.py` | Extract failure library from denials | 1 |
| `tools/cieu/cieu_brain_context.py` | Generate per-brain context blocks | 2 |
| `tools/cieu/cieu_k9_adapter.py` | CIEU SQLite -> K9 JSONL adapter | 3 |
| `tools/cieu/cieu_dream_reader.py` | Dream mode synthesis | 4 |
| `tools/cieu/cieu_sanitizer.py` | Secret/PII redaction | 5 |
| `knowledge/shared/forgetguard_candidates.yml` | Auto-extracted FG rules | 1 |
| `knowledge/shared/behavioral_rules_from_cieu.yml` | ARCH-17 feed | 1 |
| `knowledge/cto/cieu_causal_catalog.json` | Root cause catalog | 3 |
| `knowledge/cto/cieu_intervention_scores.json` | Intervention effectiveness | 3 |
| `knowledge/shared/cieu_attack_surface.json` | Attack surface map | 3 |
| `knowledge/ceo/dreams/dream_{date}.md` | CEO dream output | 4 |
| `knowledge/cto/dreams/dream_{date}.md` | CTO dream output | 4 |

---

## 11. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Sanitizer false negatives (secrets leak to brain) | Medium | High | Conservative regex + manual spot-check of first 1000 events |
| Brain context too large (crowds out task context) | Medium | Medium | Hard 2000-token budget, priority-ranked content |
| K9 CausalChainAnalyzer OOM on large sessions | Low | Medium | Session chunking (max 500 events per analysis run) |
| Stale brain context misleads decisions | Medium | Medium | Timestamp all context, decay factor for old patterns |
| Dream mode generates hallucinated patterns | Medium | Low | All dream outputs flagged as hypotheses, require CTO validation |

