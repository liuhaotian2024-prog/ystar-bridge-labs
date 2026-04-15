# Gemma Quality Daily Reports

Auto-generated daily quality reports comparing Gemma 4 vs Claude baseline.

**Generation**: `scripts/quality_compare.py` runs nightly @ 06:10 (via `scripts/k9_daily_patrol.sh` Step 3)

**Filename**: `YYYYMMDD.md` (e.g., `20260415.md`)

## Report Schema

**Front-matter** (YAML):
```yaml
date: YYYY-MM-DD
total_calls: N
shadow_calls: N
pass: N
fail: N
pass_rate: 0.XXX
similarity_avg: 0.XX
retention_avg: 0.XX
alerts_pushed: N
```

**Body sections**:
1. Summary — one-line stats
2. Failures — table of failed calls (if any) with metrics and reasons
3. Action items — recommended follow-ups

## Quality Metrics

| Metric | Threshold | Description |
|--------|-----------|-------------|
| `similarity` | >= 0.70 | SequenceMatcher ratio (textual similarity) |
| `key_info_retention` | >= 0.80 | Jaccard token overlap (how much Claude info survives in Gemma) |
| `length_ratio` | 0.5 - 2.0 | Gemma output length / Claude output length |

**Pass criteria**: All 3 metrics within thresholds.

## Alerts

Telegram push triggered when:
- `pass_rate < 70%` (daily)
- `similarity < 0.50` or `retention < 0.60` (single call, severe)
- `gemma_error_rate > 5%` (daily)

## Related Artifacts

- **Shadow records**: `reports/gemma_shadow_archive/YYYYMMDD/call_NNNNN.json` (raw prompt/output pairs)
- **CIEU events**: `.ystar_cieu.db` (event_type: `llm_quality_audit`, `llm_quality_audit_summary`)
- **Thresholds**: `scripts/quality_compare.py` top-level constants (Board-tunable)

## Design Provenance

- **Leo 510ee408**: `reports/gemma4_api_bridge_exploration_20260415.md` (Gemma client architecture)
- **Samantha 871b1b9e**: `reports/gemma_quality_monitor_design_20260415.md` (quality monitor spec)

---

_Bootstrap: 2026-04-15 Gemma Phase 1 Task 4_
