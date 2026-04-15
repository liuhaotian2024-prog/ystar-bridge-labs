# Gemma Shadow Archive

Raw A/B comparison records (Gemma vs Claude) for first 100 calls + forced shadow calls.

**Generation**: `scripts/gemma_client.generate()` auto-persists when `shadow_count < 100` or `force_shadow=True`

**Directory structure**:
```
gemma_shadow_archive/
├── 20260415/
│   ├── call_00001.json
│   ├── call_00002.json
│   └── ...
├── 20260416/
│   └── ...
└── README.md (this file)
```

## Record Schema

**Filename**: `call_NNNNN.json` (5-digit zero-padded counter)

**JSON structure**:
```json
{
  "call_id": "call_00001",
  "timestamp": 1776960000.0,
  "prompt_hash": "3f9a2b4c5d6e7f8a",
  "prompt_snippet": "First 200 chars of prompt...",
  "gemma": {
    "provider": "ystar-gemma:latest",
    "text": "Gemma output...",
    "tokens": 172,
    "latency_ms": 6360,
    "error": null
  },
  "claude": {
    "provider": "claude-sonnet-4.5",
    "text": "Claude output...",
    "tokens": 189,
    "latency_ms": 1820,
    "error": null
  },
  "metrics": {
    "similarity": 0.82,
    "key_info_retention": 0.95,
    "length_ratio": 1.10
  }
}
```

## Purpose

- **A/B baseline**: Establish quality baseline before trusting Gemma for production workloads
- **Failure forensics**: When quality_compare.py reports failures, Board/engineers review raw records
- **Threshold tuning**: Adjust quality thresholds based on observed metric distributions
- **CIEU audit**: Permanent record of LLM quality evolution (git-tracked)

## Retention Policy

- **First 100 calls**: Always shadowed (counter in `.ystar_gemma_shadow_count`)
- **Post-100**: Shadow only if `force_shadow=True` (manual Board inspection or anomaly investigation)
- **Git tracking**: All records committed to git for cross-session persistence

## Related

- **Daily reports**: `reports/gemma_quality_daily/YYYYMMDD.md` (aggregated metrics)
- **CIEU events**: `.ystar_cieu.db` (per-call quality audit events)
- **Counter file**: `.ystar_gemma_shadow_count` (persistent shadow counter)

---

_Bootstrap: 2026-04-15 Gemma Phase 1 Task 4_
