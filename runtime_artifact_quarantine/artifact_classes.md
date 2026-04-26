# Artifact Classes

| Class | Pattern | Likely value | Risk | Direct read policy | Future adapter recommendation | Console direct read |
| --- | --- | --- | --- | --- | --- | --- |
| DB_CORE | `*.db`, `*.sqlite`, `*.sqlite3` | Brain state, CIEU events, memory graph, omission state. | Very high: structured stores may be live or sensitive. | Forbidden. Metadata/path only. | Readonly DB adapter with explicit schema and CIEU review. | false |
| DB_SIDECARE | `*.db-wal`, `*.db-shm`, `*.sqlite-wal`, `*.sqlite-shm` | Evidence of live/recent DB activity. | Extreme: sidecar files are runtime-coupled. | Forbidden. Metadata/path only. | Usually no content adapter; treat as live-state signal only. | false |
| LOG_RUNTIME | `scripts/.logs/*`, `*.log` | Daemon health, drift signals, dialogue contracts, dream cycles. | High: large/noisy/private/runtime. | Forbidden for direct bulk read. | Bounded log summarizer with size/time limits. | false |
| ACTIVE_AGENT_MARKER | `.ystar_active_agent.*`, `scripts/.ystar_active_agent.*` | Role activity and execution context hints. | High: live/ephemeral state. | Avoid content reads; path-only now. | Marker summarizer with explicit bounds. | false |
| DAEMON_STATE | `*.pid`, daemon/subscriber/alarm consumer state files. | Process ownership and runtime health hints. | High: live control-plane state. | Forbidden. | State metadata adapter only. | false |
| CACHE_SENTINEL | cache, sentinel, session call count, last message markers. | Runtime coordination and recent activity clues. | Medium/high: ephemeral and easy to misinterpret. | Path-only now. | Cache/sentinel classifier, not memory ingestion. | false |
| PYCACHE | `__pycache__`, `*.pyc` | Almost no semantic value. | Low/medium clutter risk. | No content read. | Ignore or cleanup policy later. | false |
| DREAM_REPORT | `reports/ceo/brain_dream_diffs/*` | Consolidation insights and dream deltas. | Medium: may be valuable but uncurated. | No bulk read now. | Bounded dream report parser. | false |
| ESCALATION_REPORT | `reports/escalation/*` | Governance failures, incidents, escalation context. | Medium/high: sensitive evidence. | No bulk read now. | Escalation parser with CIEU mapping. | false |
| DAILY_REPORT | `reports/daily/*` | Curated operational summaries. | Medium: may still need curation. | No bulk read now. | Bounded report parser. | false |
| DRIFT_REPORT | `reports/drift_hourly/*` | Drift signals and trajectory data. | Medium. | No bulk read now. | Drift report parser. | false |
| WHITELIST_REPORT | `reports/whitelist_daily/*` | Whitelist/allowance context. | Medium. | No bulk read now. | Policy report parser. | false |
| BACKUP_DB | `backups/*.db` | Historical brain snapshots. | Very high. | Forbidden. Metadata/path only. | Backup DB inventory adapter; readonly extraction later. | false |
| UNKNOWN_RUNTIME_ARTIFACT | Unclassified dirty runtime-like path. | Unknown. | Unknown. | Path-only until classified. | Manual triage. | false |
| UNKNOWN_OR_NON_RUNTIME | Modified docs/source/generated files not classified as runtime artifacts. | May be normal worktree changes. | Depends on path. | Normal repo review rules. | Not a mining target by default. | false |
