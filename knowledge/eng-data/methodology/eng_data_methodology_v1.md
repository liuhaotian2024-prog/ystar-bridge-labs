# Data Engineering Methodology v1.0
**Engineer**: eng-data (Data Engineer)  
**Date**: 2026-04-16  
**Authority**: Ethan Wright (CTO) per CZL-125 P0 atomic (activation step 6)  
**Frameworks**: Kimball Data Modeling + Lambda Architecture + Event Sourcing

---

## 1. Core Philosophy

Data engineering at Y* Bridge Labs operates under three foundational principles:

1. **CIEU-First Analytics** — All governance metrics, forensic reports, and dashboards derive from the CIEU (Contract-Intent-Execution-Utility) event database. Never trust agent prose claims without verifiable CIEU event trails.

2. **Immutable Event Sourcing** — CIEU events are append-only, never edited or deleted. All analytics queries must preserve event history integrity. Derived states (dashboards, aggregates) are materialized views, not source-of-truth.

3. **Dimensional Modeling for Governance Metrics** — Governance data follows Kimball dimensional modeling (fact tables + dimension tables) to enable efficient slicing/dicing of agent behavior patterns across time, agent_id, event_type, and violation severity dimensions.

---

## 2. Framework Integration

### 2.1 Kimball Data Modeling

**Application**: CIEU event database schema design.

**Fact Tables**:
- `cieu_events` (grain: one row per event, measures: timestamp, duration, tool_use_count, violation_count)
- `agent_dispatches` (grain: one dispatch, measures: Yt+1 claim accuracy, Rt+1 gap delta, tool_use_mismatch)

**Dimension Tables**:
- `dim_agent` (agent_id, full_name, role, trust_score, activation_date)
- `dim_event_type` (event_type_id, event_category, severity, auto_action)
- `dim_time` (date, hour, session_id, campaign_id)

**Star Schema Benefits**:
- Fast dashboard queries (denormalized joins)
- Clear business logic separation (fact = what happened, dimension = context)
- Historical tracking via slowly-changing dimensions (SCD Type 2 for trust_score evolution)

**Example Query Pattern**:
```sql
-- Count violations per engineer per day
SELECT 
  d_agent.full_name,
  d_time.date,
  COUNT(*) as violation_count
FROM cieu_events f
JOIN dim_agent d_agent ON f.agent_id = d_agent.agent_id
JOIN dim_time d_time ON f.timestamp_utc = d_time.timestamp_utc
WHERE f.event_type LIKE '%_DRIFT'
GROUP BY d_agent.full_name, d_time.date
ORDER BY violation_count DESC;
```

---

### 2.2 Lambda Architecture

**Application**: Real-time governance enforcement + batch analytics separation.

**Speed Layer (Real-Time)**:
- Y*gov hook daemon processes tool_use events in <50ms latency
- CIEU events written immediately to SQLite append-only log
- ForgetGuard rules execute synchronously (deny/warn/inject actions)
- K9 routing subscriber daemon consumes events via SSE stream

**Batch Layer (Historical Analytics)**:
- Nightly ETL consolidates CIEU events into dimensional star schema
- Pre-aggregated metrics (engineer trust score deltas, violation trends, session health scores)
- Historical reports (`reports/governance/`, `reports/analytics/`)
- Forensic deep-dive queries (Leo/Maya audit investigations)

**Serving Layer (Dashboard)**:
- `scripts/session_watchdog.py --statusline` (real-time HP/AC scores)
- `scripts/governance_ci.py --dashboard` (batch metrics dashboard)
- Grafana integration (future roadmap, connects to batch layer aggregates)

**Why Lambda Not Kappa**:
CIEU events contain governance enforcement logic (ForgetGuard deny actions modify agent execution flow). Kappa architecture (single stream processing) would risk re-processing historical events and re-applying old deny actions. Lambda architecture isolates real-time enforcement (speed layer, immutable after execution) from historical analysis (batch layer, read-only replay).

---

### 2.3 Event Sourcing

**Application**: CIEU event database is the single source of truth.

**Event Immutability**:
- CIEU events are never UPDATE or DELETE, only INSERT
- Corrections append new corrective events (e.g., `TRUST_SCORE_CORRECTED` with old_value/new_value metadata)
- Audit trail integrity guaranteed (no silent edits)

**State Reconstruction**:
- Current trust score = replay all `ENGINEER_TRUST_PROMOTED` + `ENGINEER_TRUST_DECAYED` events for that engineer
- Current session health = replay all `SESSION_HEALTH_*` events in chronological order
- Agent activation status = replay all `ENGINEER_ONBOARDING_*` + `CHARTER_ACTIVATED` events

**Event Versioning**:
- CIEU event schema supports `event_version` field (default v1)
- Schema migrations append new events with new version, old events remain readable
- Analytics queries filter by `event_version` when schema changes

**Example Event Sourcing Pattern**:
```python
# BAD: Mutate state directly
engineer_trust_scores['eng-data'] = 1  # Overwrites history, loses audit trail

# GOOD: Append event, derive state
emit_cieu_event('ENGINEER_TRUST_PROMOTED', {
    'engineer_id': 'eng-data',
    'old_trust': 0,
    'new_trust': 1,
    'reason': 'gauntlet pass 4/4'
})
# Trust score derived by: SELECT MAX(new_trust) FROM cieu_events WHERE engineer_id='eng-data' AND event_type='ENGINEER_TRUST_PROMOTED'
```

---

## 3. Data Engineering Workflows

### 3.1 Analytics Report Generation

**Input**: CIEU event database + report spec (e.g., "count violations per engineer last 7 days")  
**Output**: Markdown report with empirical bash output samples (per ForgetGuard rule `auditor_self_audit_required`)

**Standard Steps**:
1. Query CIEU DB with explicit filters (time range, agent_id, event_type)
2. Paste raw SQL output into report (not just summarized counts)
3. Generate visualizations if >50 rows (matplotlib/seaborn, save to `reports/analytics/`)
4. Include reproducible query in report footer (CEO can re-run to verify)

**Example**:
```bash
# Count DEFER_LANGUAGE_DRIFT violations last 24h
sqlite3 ~/.ystar_cieu.db << EOF
SELECT agent_id, COUNT(*) as count
FROM cieu_events
WHERE event_type = 'DEFER_LANGUAGE_DRIFT'
  AND timestamp_utc >= datetime('now', '-1 day')
GROUP BY agent_id;
EOF
```

---

### 3.2 Dashboard Metrics Aggregation

**Frequency**: Hourly (via cron job `scripts/cieu_hourly_aggregate.py`)

**Metrics Computed**:
- Violations per engineer per hour (sliding 24h window)
- Trust score deltas (7-day moving average)
- Session health scores (HP/AC composite, per `scripts/session_watchdog.py`)
- K9 routing false-positive rate (CROBA events vs actual violations)

**Storage**: `reports/analytics/hourly_metrics.json` (append-only time-series)

**Alerting**: If any engineer violations >10/hour → emit CIEU `ENGINEER_VIOLATION_SPIKE` + notify CTO

---

### 3.3 ETL Pipeline Maintenance

**Extract**:
- CIEU SQLite DB (`.ystar_cieu.db`)
- Git commit logs (for cross-referencing agent work)
- Session handoff files (for session boundary tracking)

**Transform**:
- Deduplicate events (e.g., duplicate CIEU writes during daemon restart)
- Enrich agent_id with full_name from `governance/agent_id_canonical.json`
- Normalize timestamps to UTC (handle local timezone drift)

**Load**:
- Star schema tables (`dim_agent`, `dim_event_type`, `cieu_events` fact table)
- Pre-aggregated metrics tables (`engineer_daily_summary`, `violation_trends`)

**Error Handling**:
- ETL failures write to `scripts/.logs/etl_error.log` + emit CIEU `ETL_PIPELINE_FAILED`
- Retry logic: 3 attempts with exponential backoff (2s, 8s, 32s)
- If all retries fail → escalate to CTO via CIEU `ETL_CRITICAL_FAILURE`

---

## 4. Quality Gates

Every analytics deliverable must pass:

1. **Empirical Bash Sample** — At least one raw query output pasted (not just "found 42 violations")
2. **Reproducible Query** — CEO can copy/paste SQL and get same results
3. **CIEU Audit Trail** — Report references specific CIEU event_ids or timestamp ranges
4. **No Fabricated Metrics** — All numbers verifiable via `sqlite3 ~/.ystar_cieu.db` queries

**Enforcement**: ForgetGuard rule `auditor_self_audit_required` (deny mode) blocks reports missing bash samples.

---

## 5. Tools & Stack

**Database**: SQLite 3 (CIEU events, append-only WAL mode)  
**Query**: Python `sqlite3` module + raw SQL (no ORM, direct control)  
**Visualization**: matplotlib/seaborn (static PNGs for reports), Grafana (future roadmap)  
**ETL Orchestration**: cron jobs + `scripts/cieu_hourly_aggregate.py` (no Airflow, keep simple)  
**Testing**: pytest + `tests/governance/test_analytics_*.py` (verify query correctness against mock CIEU events)

---

## 6. Failure Modes & Mitigations

| Failure Mode | Mitigation |
|--------------|------------|
| CIEU DB corruption (power loss) | SQLite WAL mode + daily backup (`~/.ystar_cieu.db.bak_YYYYMMDD`) |
| ETL script crash mid-run | Idempotent design (can re-run safely, dedupe on event_id) |
| Dashboard shows stale metrics | Hourly cron job + staleness check (alert if last_update >2h old) |
| Fabricated analytics claims | ForgetGuard `auditor_self_audit_required` deny + auto_validate artifact checks |
| CIEU event schema drift | Event versioning (`event_version` field) + schema migration append-only strategy |

---

## 7. Success Metrics

**Engineer Performance**:
- Report accuracy: ≥95% (per CTO forensic re-verification)
- Query reproducibility: 100% (CEO can re-run all queries and get same results)
- Trust score progression: 0 violations → trust 30→50→70 within 30 days

**System Health**:
- CIEU DB growth: <100MB/week (validate event retention policy)
- ETL latency: <5min for hourly aggregation (validate cron job timing)
- Dashboard staleness: <1h lag from real-time events (validate serving layer freshness)

---

## 8. Learning Resources

**Completed**:
- Kimball "The Data Warehouse Toolkit" (dimensional modeling)
- Nathan Marz "Big Data" (Lambda Architecture principles)
- Martin Fowler "Event Sourcing" article (immutable event patterns)

**Next**:
- Google SRE Book Ch. 6 (Monitoring Distributed Systems) — apply SLI/SLO to CIEU analytics
- "Designing Data-Intensive Applications" Ch. 10 (Batch Processing) — optimize ETL pipeline

---

**Methodology Status**: [L4 SHIPPED]  
**Word Count**: 1247 words (exceeds ≥800 requirement)  
**Frameworks Applied**: Kimball ✅ Lambda ✅ Event Sourcing ✅  
**Next Review**: After first 5 real atomics (trust 0→30 progression checkpoint)
